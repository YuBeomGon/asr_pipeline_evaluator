from __future__ import annotations
"""Unit tests for text normalization and audio preprocessing.

BMAD QA: Verifies edge cases in normalization pipeline and audio conversion.
"""
import io

import numpy as np
import pytest
import soundfile as sf

from src.audio.preprocessor import AudioPreprocessor
from src.eval.cer import normalize_text, normalize_transcript
from src.backends.mock import MockASRBackend


# ─────────────────────────────── normalize_transcript ───────────────────────

class TestNormalizeTranscript:
    """NFC normalization used for /transcribe output."""

    def test_nfc_preserves_korean(self):
        text = "안녕하세요"
        result = normalize_transcript(text)
        assert result == "안녕하세요"

    def test_nfc_normalized(self):
        import unicodedata
        text = "안녕하세요"
        result = normalize_transcript(text)
        assert unicodedata.is_normalized("NFC", result)


# ─────────────────────────────── AudioPreprocessor ──────────────────────────

class TestAudioPreprocessor:
    def setup_method(self):
        self.preprocessor = AudioPreprocessor(target_sample_rate=16000)

    def _make_wav(
        self,
        duration_s: float = 1.0,
        sample_rate: int = 16000,
        channels: int = 1,
    ) -> bytes:
        n = int(duration_s * sample_rate)
        if channels == 1:
            audio = np.zeros(n, dtype=np.float32)
        else:
            audio = np.zeros((n, channels), dtype=np.float32)
        buf = io.BytesIO()
        sf.write(buf, audio, sample_rate, format="WAV", subtype="FLOAT")
        buf.seek(0)
        return buf.read()

    def test_mono_16k_passthrough(self):
        wav = self._make_wav(duration_s=1.0, sample_rate=16000, channels=1)
        result = self.preprocessor.preprocess(wav)
        assert result.sample_rate == 16000
        assert result.audio.ndim == 1
        assert abs(result.duration_seconds - 1.0) < 0.01

    def test_stereo_downmixed_to_mono(self):
        wav = self._make_wav(duration_s=0.5, sample_rate=16000, channels=2)
        result = self.preprocessor.preprocess(wav)
        assert result.audio.ndim == 1

    def test_resampling_8k_to_16k(self):
        wav = self._make_wav(duration_s=1.0, sample_rate=8000, channels=1)
        result = self.preprocessor.preprocess(wav)
        assert result.sample_rate == 16000
        assert result.original_sample_rate == 8000
        # Resampled length should be ~16000 samples
        assert abs(len(result.audio) - 16000) < 100

    def test_duration_accuracy(self):
        wav = self._make_wav(duration_s=2.0, sample_rate=16000, channels=1)
        result = self.preprocessor.preprocess(wav)
        assert abs(result.duration_seconds - 2.0) < 0.01

    def test_invalid_bytes_raises(self):
        with pytest.raises(ValueError, match="Cannot decode audio"):
            self.preprocessor.preprocess(b"not audio data")

    def test_output_dtype_float32(self):
        wav = self._make_wav()
        result = self.preprocessor.preprocess(wav)
        assert result.audio.dtype == np.float32


# ─────────────────────────────── MockASRBackend ─────────────────────────────

class TestMockASRBackend:
    def setup_method(self):
        self.backend = MockASRBackend()

    def _dummy_audio(self, n_samples: int = 16000) -> np.ndarray:
        return np.zeros(n_samples, dtype=np.float32)

    def test_returns_transcript_result(self):
        from src.backends.base import TranscriptResult
        result = self.backend.transcribe(self._dummy_audio(), sample_rate=16000)
        assert isinstance(result, TranscriptResult)
        assert isinstance(result.text, str)
        assert len(result.text) > 0

    def test_confidence_in_range(self):
        result = self.backend.transcribe(self._dummy_audio(), sample_rate=16000)
        assert 0.0 <= result.confidence <= 1.0

    def test_backend_name(self):
        result = self.backend.transcribe(self._dummy_audio(), sample_rate=16000)
        assert result.backend == "mock"

    def test_health_is_true(self):
        assert self.backend.health() is True

    def test_deterministic_for_same_input(self):
        audio = self._dummy_audio(16000)
        r1 = self.backend.transcribe(audio, 16000)
        r2 = self.backend.transcribe(audio, 16000)
        assert r1.text == r2.text
        assert r1.confidence == r2.confidence
