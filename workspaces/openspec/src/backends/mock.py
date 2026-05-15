from __future__ import annotations
"""
Mock ASR backend for local development and testing.
Returns a deterministic transcript — no GPU or network required.
Replace this backend with a real implementation (Whisper, NeMo, etc.)
by implementing ASRBackend and registering it in registry.py.
"""
import time

import numpy as np

from .base import ASRBackend, TranscriptResult


class MockASRBackend(ASRBackend):
    """
    Deterministic mock ASR backend.

    Returns the configured transcript regardless of audio content.
    Simulates a configurable inference delay to model realistic latency.
    Suitable for local development, CI, and unit/integration tests.
    """

    _BACKEND_ID = "mock"
    _MODEL_NAME = "mock-asr"
    _MODEL_VERSION = "0.1.0"

    def __init__(
        self,
        transcript: str = "안녕하세요 반갑습니다",
        confidence: float = 0.95,
        inference_delay_ms: float = 10.0,
    ) -> None:
        """
        Args:
            transcript: Fixed transcript to return.
            confidence: Fixed confidence score to return.
            inference_delay_ms: Simulated inference latency in milliseconds.
        """
        self._transcript = transcript
        self._confidence = float(confidence)
        self._inference_delay_ms = float(inference_delay_ms)

    def transcribe(self, audio: np.ndarray, sample_rate: int) -> TranscriptResult:
        """
        Return a deterministic mock transcript.

        The audio array is accepted but not used — this ensures the interface
        contract is satisfied and allows future backends to drop in.
        """
        start = time.perf_counter()

        # Simulate inference time
        if self._inference_delay_ms > 0:
            time.sleep(self._inference_delay_ms / 1000.0)

        elapsed_ms = (time.perf_counter() - start) * 1000.0

        return TranscriptResult(
            transcript=self._transcript,
            confidence=self._confidence,
            inference_ms=elapsed_ms,
            backend_name=self._BACKEND_ID,
            model_name=self._MODEL_NAME,
            model_version=self._MODEL_VERSION,
        )

    def health_check(self) -> bool:
        """Mock backend is always healthy."""
        return True

    @property
    def backend_id(self) -> str:
        return self._BACKEND_ID
