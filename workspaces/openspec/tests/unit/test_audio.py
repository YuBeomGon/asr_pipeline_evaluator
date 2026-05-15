from __future__ import annotations
"""
Unit tests for audio preprocessing module.
"""
import io
import struct
import wave

import numpy as np
import pytest

from src.audio.preprocessing import AudioPreprocessor, AudioPreprocessingError, PreprocessResult


def make_wav_bytes(
    num_samples: int = 16000,
    sample_rate: int = 16000,
    num_channels: int = 1,
    sample_width: int = 2,
) -> bytes:
    """Generate minimal valid WAV bytes with a sine wave."""
    buf = io.BytesIO()
    freq = 440.0  # Hz
    t = np.linspace(0, num_samples / sample_rate, num_samples, endpoint=False)
    audio = (np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)

    with wave.open(buf, "wb") as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    buf.seek(0)
    return buf.read()


class TestAudioPreprocessor:
    def setup_method(self):
        self.preprocessor = AudioPreprocessor(target_sample_rate=16000)

    def test_mono_16khz_passthrough(self):
        wav = make_wav_bytes(num_samples=16000, sample_rate=16000, num_channels=1)
        result = self.preprocessor.preprocess(wav)
        assert isinstance(result, PreprocessResult)
        assert result.sample_rate == 16000
        assert result.audio.dtype == np.float32
        assert abs(result.duration_seconds - 1.0) < 0.01

    def test_stereo_to_mono(self):
        wav = make_wav_bytes(num_samples=16000, sample_rate=16000, num_channels=2)
        result = self.preprocessor.preprocess(wav)
        assert result.audio.ndim == 1, "Should be 1D mono array"

    def test_resample_8khz_to_16khz(self):
        wav = make_wav_bytes(num_samples=8000, sample_rate=8000)
        result = self.preprocessor.preprocess(wav)
        assert result.sample_rate == 16000
        # Should have approximately 16000 samples (1 second)
        assert abs(len(result.audio) - 16000) < 100

    def test_duration_calculation(self):
        # 2-second audio at 16kHz
        wav = make_wav_bytes(num_samples=32000, sample_rate=16000)
        result = self.preprocessor.preprocess(wav)
        assert abs(result.duration_seconds - 2.0) < 0.01

    def test_empty_bytes_raises(self):
        with pytest.raises(AudioPreprocessingError, match="Empty audio bytes"):
            self.preprocessor.preprocess(b"")

    def test_invalid_bytes_raises(self):
        with pytest.raises(AudioPreprocessingError):
            self.preprocessor.preprocess(b"not audio data at all")

    def test_output_is_float32(self):
        wav = make_wav_bytes()
        result = self.preprocessor.preprocess(wav)
        assert result.audio.dtype == np.float32
