"""POST /transcribe route.

BMAD Developer: This route orchestrates preprocessing → inference → postprocessing.
Timing is measured at each step. Metrics are incremented via context manager.
"""
from __future__ import annotations

import time
import unicodedata
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.api.models import ModelInfo, TimingInfo, TranscribeResponse
from src.audio import AudioPreprocessor
from src.backends import get_backend
from src.observability import get_logger
from src.observability.metrics import ASR_ERRORS_TOTAL, ASR_REQUEST_DURATION, ASR_REQUESTS_TOTAL

router = APIRouter()
_preprocessor = AudioPreprocessor()


@router.post("/transcribe", response_model=TranscribeResponse, tags=["asr"])
async def transcribe(file: UploadFile = File(...)) -> TranscribeResponse:
    """Transcribe an uploaded audio file.

    - Accepts multipart/form-data with 'file' field.
    - Returns transcript, confidence, timing, and model metadata.
    - request_id is prefixed with 'req_'.
    """
    request_id = f"req_{uuid.uuid4()}"
    log = get_logger(__name__, request_id=request_id)
    log.info("Transcribe request received", extra={"audio_filename": file.filename})

    total_start = time.perf_counter()

    try:
        # ── Preprocess ──────────────────────────────────────────────────────
        t0 = time.perf_counter()
        audio_bytes = await file.read()
        if not audio_bytes:
            raise HTTPException(status_code=422, detail="Empty audio file")

        try:
            preprocess_result = _preprocessor.preprocess(audio_bytes)
        except ValueError as e:
            log.warning(f"Audio preprocessing failed: {e}")
            ASR_ERRORS_TOTAL.inc()
            ASR_REQUESTS_TOTAL.labels(status="error").inc()
            raise HTTPException(status_code=422, detail=str(e))

        preprocess_ms = (time.perf_counter() - t0) * 1000
        log.info(
            "Audio preprocessed",
            extra={
                "duration_s": round(preprocess_result.duration_seconds, 3),
                "orig_sr": preprocess_result.original_sample_rate,
            },
        )

        # ── Inference ───────────────────────────────────────────────────────
        t1 = time.perf_counter()
        backend = get_backend()
        result = backend.transcribe(preprocess_result.audio, preprocess_result.sample_rate)
        inference_ms = (time.perf_counter() - t1) * 1000

        # ── Postprocess ─────────────────────────────────────────────────────
        t2 = time.perf_counter()
        transcript = unicodedata.normalize("NFC", result.text)
        postprocess_ms = (time.perf_counter() - t2) * 1000

        total_ms = (time.perf_counter() - total_start) * 1000

        log.info(
            "Transcription complete",
            extra={
                "transcript_len": len(transcript),
                "confidence": result.confidence,
                "total_ms": round(total_ms, 2),
            },
        )

        # ── Metrics ─────────────────────────────────────────────────────────
        ASR_REQUESTS_TOTAL.labels(status="success").inc()
        ASR_REQUEST_DURATION.observe(total_ms / 1000)

        return TranscribeResponse(
            request_id=request_id,
            transcript=transcript,
            confidence=result.confidence,
            audio_duration_seconds=round(preprocess_result.duration_seconds, 6),
            timing=TimingInfo(
                preprocess_ms=round(preprocess_ms, 3),
                inference_ms=round(inference_ms, 3),
                postprocess_ms=round(postprocess_ms, 3),
                total_ms=round(total_ms, 3),
            ),
            model=ModelInfo(
                backend=result.backend,
                name=result.name,
                version=result.version,
            ),
        )

    except HTTPException:
        raise
    except Exception as e:
        log.exception(f"Unexpected error during transcription: {e}")
        ASR_ERRORS_TOTAL.inc()
        ASR_REQUESTS_TOTAL.labels(status="error").inc()
        raise HTTPException(status_code=500, detail="Internal server error")
