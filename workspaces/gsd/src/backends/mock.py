"""Mock ASR backend — deterministic, no GPU or network required."""
from __future__ import annotations

import time

import numpy as np

from .base import ASRBackend, TranscriptResult

# Deterministic mock transcript returned for any input.
# Contains Korean text so CER evaluation is exercised end-to-end.
_MOCK_TRANSCRIPT = "안녕하세요 이것은 모의 전사입니다"
_MOCK_CONFIDENCE = 0.95
_MOCK_BACKEND_NAME = "mock"
_MOCK_MODEL_NAME = "mock-asr"
_MOCK_MODEL_VERSION = "0.1.0"


class MockASRBackend(ASRBackend):
    """Returns a fixed transcript regardless of audio content.

    Suitable for unit/integration tests and local development.
    Inference is ~1 ms (no actual computation).
    """

    @property
    def name(self) -> str:
        return _MOCK_BACKEND_NAME

    def transcribe(self, audio: np.ndarray, sample_rate: int) -> TranscriptResult:
        t0 = time.perf_counter()
        # Simulate minimal processing delay
        _ = audio.shape  # access to avoid unused-variable lint
        inference_ms = (time.perf_counter() - t0) * 1000.0

        return TranscriptResult(
            transcript=_MOCK_TRANSCRIPT,
            confidence=_MOCK_CONFIDENCE,
            backend_name=_MOCK_BACKEND_NAME,
            model_name=_MOCK_MODEL_NAME,
            model_version=_MOCK_MODEL_VERSION,
            inference_ms=inference_ms,
        )
