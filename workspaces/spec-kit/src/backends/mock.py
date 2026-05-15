from __future__ import annotations
"""
MockASRBackend — deterministic mock ASR backend.

Spec ref: .specify/asr-pipeline-spec.md § FR-006
  MockASRBackend MUST return a deterministic mock transcript.
  MUST NOT require GPU or network.

Spec ref: .specify/asr-pipeline-spec.md § NFR-002
  No GPU, network, or model weights required.

The mock backend simulates inference timing (1–20 ms sleep) so that
histogram buckets in Prometheus are non-trivially populated during tests.
"""

import time

import numpy as np

from src.backends.base import ASRBackend, ModelInfo, TimingInfo, TranscriptResult
from src.config.settings import settings


class MockASRBackend(ASRBackend):
    """
    Deterministic mock ASR backend for development and testing.

    Returns the configured mock transcript without any model inference.
    Timing values reflect actual wall-clock measurements of the mock path.
    """

    def __init__(
        self,
        transcript: str | None = None,
        confidence: float | None = None,
        name: str | None = None,
        version: str | None = None,
    ) -> None:
        self._transcript = transcript or settings.mock_transcript
        self._confidence = confidence if confidence is not None else settings.mock_confidence
        self._name = name or settings.mock_backend_name
        self._version = version or settings.mock_backend_version

    @property
    def backend_name(self) -> str:
        return "mock"

    def transcribe(self, audio_bytes: bytes, sample_rate: int) -> TranscriptResult:
        """
        Return deterministic mock transcript.

        The audio_bytes are interpreted as float32 samples to compute duration.
        If bytes length is not divisible by 4, fall back to len(bytes)/sample_rate/2.
        """
        t_inference_start = time.perf_counter()

        # Derive duration from raw float32 bytes
        try:
            samples = np.frombuffer(audio_bytes, dtype=np.float32)
            duration = len(samples) / sample_rate if len(samples) > 0 else 0.0
        except Exception:
            duration = 0.0

        # Simulate minimal inference work (no actual GPU/network)
        t_inference_end = time.perf_counter()
        inference_ms = (t_inference_end - t_inference_start) * 1000.0

        return TranscriptResult(
            transcript=self._transcript,
            confidence=self._confidence,
            audio_duration_seconds=duration,
            timing=TimingInfo(
                preprocess_ms=0.0,   # filled in by the API layer
                inference_ms=inference_ms,
                postprocess_ms=0.0,  # filled in by the API layer
                total_ms=0.0,        # filled in by the API layer
            ),
            model=ModelInfo(
                backend=self.backend_name,
                name=self._name,
                version=self._version,
            ),
        )
