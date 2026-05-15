"""
API route definitions for the ASR serving pipeline.

Spec ref: .specify/asr-pipeline-spec.md § API Contract
  - GET  /healthz
  - GET  /metrics
  - POST /transcribe
  - POST /eval/cer
"""

import time
import uuid

from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from fastapi.responses import PlainTextResponse, Response

from src.api.schemas import (
    CERRequest,
    CERResponse,
    CERSampleResponse,
    HealthResponse,
    ModelInfoSchema,
    TimingInfoSchema,
    TranscribeResponse,
)
from src.audio.postprocessing import postprocess_transcript
from src.audio.preprocessing import preprocess_audio
from src.backends.base import ASRBackend
from src.eval.cer import compute_cer_batch
from src.observability.logging import RequestLogger, get_logger
from src.observability.metrics import (
    asr_errors_total,
    asr_request_duration_seconds,
    asr_requests_total,
    get_metrics_output,
)
from src.config.settings import settings

logger = get_logger(__name__)

router = APIRouter()


# ── /healthz ─────────────────────────────────────────────────────────────────

@router.get(
    "/healthz",
    response_model=HealthResponse,
    summary="Health check",
    tags=["observability"],
)
async def healthz() -> HealthResponse:
    """
    Liveness / readiness probe.

    Spec ref: .specify/asr-pipeline-spec.md § FR-001, SC-001
    """
    return HealthResponse(status="ok")


# ── /metrics ─────────────────────────────────────────────────────────────────

@router.get(
    "/metrics",
    summary="Prometheus metrics",
    tags=["observability"],
    response_class=PlainTextResponse,
)
async def metrics() -> Response:
    """
    Expose Prometheus text-format metrics.

    Spec ref: .specify/asr-pipeline-spec.md § FR-002, Endpoint: GET /metrics
    Content-Type: text/plain; version=0.0.4
    """
    body, content_type = get_metrics_output()
    return Response(content=body, media_type=content_type)


# ── /transcribe ───────────────────────────────────────────────────────────────

def _make_request_id() -> str:
    """Generate a unique request ID. Spec ref: FR-008."""
    return f"{settings.request_id_prefix}{uuid.uuid4().hex}"


@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    summary="Transcribe an audio file",
    tags=["asr"],
)
async def transcribe(
    request: Request,
    file: UploadFile = File(..., description="Audio file (WAV, FLAC, OGG, etc.)"),
) -> TranscribeResponse:
    """
    Accept an audio file and return the ASR transcript.

    Spec ref: .specify/asr-pipeline-spec.md § FR-003, FR-007, FR-008, FR-009
    Spec ref: .specify/asr-pipeline-spec.md § Endpoint: POST /transcribe
    """
    request_id = _make_request_id()
    req_logger = RequestLogger(logger, request_id)
    t_total_start = time.perf_counter()

    req_logger.info("transcribe request received", extra={"audio_filename": file.filename})

    # Read uploaded bytes
    audio_bytes = await file.read()
    if not audio_bytes:
        asr_errors_total.inc()
        asr_requests_total.labels(status="error").inc()
        req_logger.warning("empty audio file uploaded")
        raise HTTPException(status_code=422, detail="Empty audio file")

    # Preprocessing (FR-007)
    t_pre_start = time.perf_counter()
    try:
        chunk = preprocess_audio(audio_bytes)
    except ValueError as exc:
        asr_errors_total.inc()
        asr_requests_total.labels(status="error").inc()
        req_logger.error("audio preprocessing failed", extra={"error": str(exc)})
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    t_pre_end = time.perf_counter()
    preprocess_ms = (t_pre_end - t_pre_start) * 1000.0

    # Inference (FR-005, FR-006)
    backend: ASRBackend = request.app.state.backend
    t_inf_start = time.perf_counter()
    result = backend.transcribe(chunk.samples.tobytes(), chunk.sample_rate)
    t_inf_end = time.perf_counter()
    inference_ms = (t_inf_end - t_inf_start) * 1000.0

    # Postprocessing (FR-004)
    t_post_start = time.perf_counter()
    transcript = postprocess_transcript(result.transcript)
    t_post_end = time.perf_counter()
    postprocess_ms = (t_post_end - t_post_start) * 1000.0

    t_total_end = time.perf_counter()
    total_ms = (t_total_end - t_total_start) * 1000.0

    # Prometheus metrics (FR-002)
    asr_requests_total.labels(status="success").inc()
    asr_request_duration_seconds.observe((t_total_end - t_total_start))

    req_logger.info(
        "transcription complete",
        extra={
            "audio_duration_seconds": chunk.duration_seconds,
            "total_ms": total_ms,
            "confidence": result.confidence,
        },
    )

    return TranscribeResponse(
        request_id=request_id,
        transcript=transcript,
        confidence=result.confidence,
        audio_duration_seconds=chunk.duration_seconds,
        timing=TimingInfoSchema(
            preprocess_ms=preprocess_ms,
            inference_ms=inference_ms,
            postprocess_ms=postprocess_ms,
            total_ms=total_ms,
        ),
        model=ModelInfoSchema(
            backend=result.model.backend,
            name=result.model.name,
            version=result.model.version,
        ),
    )


# ── /eval/cer ─────────────────────────────────────────────────────────────────

@router.post(
    "/eval/cer",
    response_model=CERResponse,
    summary="Compute Character Error Rate",
    tags=["evaluation"],
)
async def eval_cer(body: CERRequest) -> CERResponse:
    """
    Compute CER for a batch of reference/hypothesis text pairs.

    Spec ref: .specify/asr-pipeline-spec.md § FR-004, FR-010, FR-011
    Spec ref: .specify/asr-pipeline-spec.md § Endpoint: POST /eval/cer
    """
    pairs_dicts = [
        {"id": p.id, "reference": p.reference, "hypothesis": p.hypothesis}
        for p in body.pairs
    ]

    batch = compute_cer_batch(pairs_dicts)

    return CERResponse(
        pairs=[
            CERSampleResponse(
                id=s.id,
                cer=s.cer,
                reference_chars=s.reference_chars,
                edits=s.edits,
            )
            for s in batch.pairs
        ],
        overall_cer=batch.overall_cer,
        total_reference_chars=batch.total_reference_chars,
        total_edits=batch.total_edits,
    )
