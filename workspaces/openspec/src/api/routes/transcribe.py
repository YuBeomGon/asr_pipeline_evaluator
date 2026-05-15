from __future__ import annotations
"""POST /transcribe — audio file upload and transcription."""
import time
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File, status

from src.api.postprocessing import postprocess_transcript
from src.api.schemas import ModelInfo, TimingInfo, TranscribeResponse
from src.audio.preprocessing import AudioPreprocessor, AudioPreprocessingError
from src.backends.base import ASRBackendError
from src.backends.registry import get_backend
from src.config.settings import get_settings
from src.observability.logging import get_logger, request_id_var
from src.observability.metrics import get_metrics

router = APIRouter()
logger = get_logger(__name__)


def _make_request_id() -> str:
    return f"req_{uuid.uuid4()}"


@router.post(
    "/transcribe",
    response_model=TranscribeResponse,
    status_code=status.HTTP_200_OK,
    tags=["transcription"],
)
async def transcribe_audio(
    file: UploadFile = File(..., description="Audio file to transcribe"),
) -> TranscribeResponse:
    """
    Transcribe an uploaded audio file.

    Processing pipeline:
      1. Generate unique request_id (req_<UUID4>)
      2. Read and validate audio bytes
      3. Preprocess: resample to 16kHz mono
      4. ASR backend inference
      5. Postprocess: NFC normalization, punctuation cleanup
      6. Return structured response with timing breakdown
    """
    request_id = _make_request_id()
    # Inject request_id into logging context
    token = request_id_var.set(request_id)

    settings = get_settings()
    metrics = get_metrics()
    total_start = time.perf_counter()

    logger.info(
        "Transcription request received",
        extra={
            "audio_filename": file.filename,
            "content_type": file.content_type,
        },
    )

    try:
        # ── Step 1: Read audio bytes ─────────────────────────────────────────
        audio_bytes = await file.read()
        if len(audio_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty audio file",
            )
        if len(audio_bytes) > settings.max_audio_bytes:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Audio file exceeds maximum size of {settings.max_audio_bytes} bytes",
            )

        # ── Step 2: Preprocess audio ─────────────────────────────────────────
        preprocess_start = time.perf_counter()
        preprocessor = AudioPreprocessor(
            target_sample_rate=settings.target_sample_rate
        )
        try:
            prep_result = preprocessor.preprocess(audio_bytes)
        except AudioPreprocessingError as exc:
            logger.warning("Audio preprocessing failed", extra={"error": str(exc)})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Audio preprocessing failed: {exc}",
            )
        preprocess_ms = (time.perf_counter() - preprocess_start) * 1000.0

        logger.info(
            "Audio preprocessed",
            extra={
                "duration_seconds": prep_result.duration_seconds,
                "sample_rate": prep_result.sample_rate,
                "num_samples": len(prep_result.audio),
            },
        )

        # Record audio duration metric
        metrics.audio_duration_seconds.observe(prep_result.duration_seconds)

        # ── Step 3: ASR inference ─────────────────────────────────────────────
        backend = get_backend()
        try:
            transcript_result = backend.transcribe(
                audio=prep_result.audio,
                sample_rate=prep_result.sample_rate,
            )
        except ASRBackendError as exc:
            logger.error("ASR backend error", extra={"error": str(exc)})
            metrics.errors_total.inc()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"ASR inference failed: {exc}",
            )

        inference_ms = transcript_result.inference_ms
        metrics.inference_duration_seconds.observe(inference_ms / 1000.0)

        # ── Step 4: Postprocess transcript ───────────────────────────────────
        postprocess_start = time.perf_counter()
        clean_transcript = postprocess_transcript(transcript_result.transcript)
        postprocess_ms = (time.perf_counter() - postprocess_start) * 1000.0

        total_ms = (time.perf_counter() - total_start) * 1000.0

        logger.info(
            "Transcription complete",
            extra={
                "transcript_length": len(clean_transcript),
                "confidence": transcript_result.confidence,
                "total_ms": total_ms,
            },
        )

        # ── Step 5: Record metrics ───────────────────────────────────────────
        metrics.requests_total.labels(status="success").inc()
        metrics.request_duration_seconds.observe(total_ms / 1000.0)

        return TranscribeResponse(
            request_id=request_id,
            transcript=clean_transcript,
            confidence=transcript_result.confidence,
            audio_duration_seconds=prep_result.duration_seconds,
            timing=TimingInfo(
                preprocess_ms=preprocess_ms,
                inference_ms=inference_ms,
                postprocess_ms=postprocess_ms,
                total_ms=total_ms,
            ),
            model=ModelInfo(
                backend=transcript_result.backend_name,
                name=transcript_result.model_name,
                version=transcript_result.model_version,
            ),
        )

    except HTTPException:
        metrics.requests_total.labels(status="error").inc()
        metrics.errors_total.inc()
        raise
    except Exception as exc:
        logger.exception("Unexpected error during transcription")
        metrics.requests_total.labels(status="error").inc()
        metrics.errors_total.inc()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {exc}",
        )
    finally:
        request_id_var.reset(token)
