from __future__ import annotations
"""Unit tests for ASR backends."""
import numpy as np
import pytest

from src.backends.base import ASRBackend, TranscriptResult
from src.backends.mock import MockASRBackend


class TestMockASRBackend:
    def setup_method(self):
        self.backend = MockASRBackend(
            transcript="안녕하세요",
            confidence=0.95,
            inference_delay_ms=0.0,  # no delay in tests
        )

    def test_implements_asr_backend(self):
        assert isinstance(self.backend, ASRBackend)

    def test_returns_transcript_result(self):
        audio = np.zeros(16000, dtype=np.float32)
        result = self.backend.transcribe(audio, sample_rate=16000)
        assert isinstance(result, TranscriptResult)

    def test_deterministic_transcript(self):
        audio = np.zeros(16000, dtype=np.float32)
        r1 = self.backend.transcribe(audio, 16000)
        r2 = self.backend.transcribe(audio, 16000)
        assert r1.transcript == r2.transcript == "안녕하세요"

    def test_confidence_value(self):
        audio = np.zeros(1600, dtype=np.float32)
        result = self.backend.transcribe(audio, 16000)
        assert result.confidence == pytest.approx(0.95)

    def test_backend_metadata(self):
        audio = np.zeros(1600, dtype=np.float32)
        result = self.backend.transcribe(audio, 16000)
        assert result.backend_name == "mock"
        assert result.model_name == "mock-asr"
        assert result.model_version == "0.1.0"

    def test_health_check(self):
        assert self.backend.health_check() is True

    def test_backend_id(self):
        assert self.backend.backend_id == "mock"

    def test_custom_transcript(self):
        custom_backend = MockASRBackend(transcript="custom text", inference_delay_ms=0.0)
        audio = np.zeros(1600, dtype=np.float32)
        result = custom_backend.transcribe(audio, 16000)
        assert result.transcript == "custom text"

    def test_inference_ms_positive(self):
        audio = np.zeros(1600, dtype=np.float32)
        result = self.backend.transcribe(audio, 16000)
        assert result.inference_ms >= 0.0
