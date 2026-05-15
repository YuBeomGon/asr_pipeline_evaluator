"""POST /transcribe — multipart audio upload."""
from __future__ import annotations

import time
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.api.schemas import ModelInfo, TimingInfo, TranscribeResponse
from src.audio.processor import load_audio
from src.backends.base import ASRBackend
from src.eval.normalizer import normalize_transcript
from src.observability import logging as obs_logging
from src.observability.metrics import inc_error, inc_request, observe_duration

router = APIRouter()
_logger = obs_logging.get_logger(__name__)

# Backend injected at app startup via app.state.backend
_BACKEND: ASRBackend | None = None


def set_backend(backend: ASRBackend) -> None:
    global _BACKEND
    _BACKEND = backend


def _get_backend() -> ASRBackend:
    global _BACKEND
    if _BACKEND is None:
        from src.backends.mock import MockASRBackend
        _BACKEND = MockASRBackend()
    return _BACKEND


@router.post("/transcribe", response_model=TranscribeResponse)
async def transcribe(file: UploadFile = File(...)) -> TranscribeResponse:
    request_id = f"req_{uuid.uuid4()}"
    log = obs_logging.RequestLogAdapter(_logger, request_id)

    wall_start = time.perf_counter()

    try:
        # --- Preprocess ---
        t0 = time.perf_counter()
        raw_bytes = await file.read()
        if not raw_bytes:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        try:
            chunk = load_audio(raw_bytes)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

        preprocess_ms = (time.perf_counter() - t0) * 1000.0
        log.info("audio loaded", extra={"duration_s": chunk.duration_seconds, "sr": chunk.sample_rate})

        # --- Inference ---
        t1 = time.perf_counter()
        backend = _get_backend()
        result = backend.transcribe(chunk.samples, chunk.sample_rate)
        inference_ms = (time.perf_counter() - t1) * 1000.0

        # --- Postprocess ---
        t2 = time.perf_counter()
        transcript = normalize_transcript(result.transcript)
        postprocess_ms = (time.perf_counter() - t2) * 1000.0

        total_ms = (time.perf_counter() - wall_start) * 1000.0

        log.info(
            "transcription complete",
            extra={
                "backend": result.backend_name,
                "inference_ms": round(inference_ms, 2),
                "total_ms": round(total_ms, 2),
            },
        )

        inc_request(status="success")
        observe_duration((time.perf_counter() - wall_start))

        return TranscribeResponse(
            request_id=request_id,
            transcript=transcript,
            confidence=result.confidence,
            audio_duration_seconds=chunk.duration_seconds,
            timing=TimingInfo(
                preprocess_ms=round(preprocess_ms, 3),
                inference_ms=round(inference_ms, 3),
                postprocess_ms=round(postprocess_ms, 3),
                total_ms=round(total_ms, 3),
            ),
            model=ModelInfo(
                backend=result.backend_name,
                name=result.model_name,
                version=result.model_version,
            ),
        )

    except HTTPException:
        inc_request(status="error")
        inc_error()
        raise
    except Exception as exc:
        inc_request(status="error")
        inc_error()
        log.exception("unexpected error during transcription")
        raise HTTPException(status_code=500, detail="Internal server error") from exc
