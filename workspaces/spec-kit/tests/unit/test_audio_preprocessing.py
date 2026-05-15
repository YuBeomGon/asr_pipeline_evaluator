"""
Unit tests for audio preprocessing.

Spec ref: .specify/asr-pipeline-spec.md § FR-007
  - Resample to 16 kHz mono
  - Return numpy array and duration
"""

import io
import struct
import numpy as np
import pytest
import soundfile as sf

from src.audio.preprocessing import preprocess_audio, AudioChunk
from src.config.settings import settings


def make_wav_bytes(
    samples: np.ndarray,
    sample_rate: int = 16000,
    num_channels: int = 1,
) -> bytes:
    """Create a WAV file in memory from a numpy float32 array."""
    buf = io.BytesIO()
    sf.write(buf, samples, sample_rate, format="WAV", subtype="PCM_16")
    return buf.getvalue()


class TestPreprocessAudio:
    def test_mono_passthrough(self):
        samples = np.zeros(16000, dtype=np.float32)
        wav = make_wav_bytes(samples, sample_rate=16000, num_channels=1)
        chunk = preprocess_audio(wav)
        assert chunk.sample_rate == settings.target_sample_rate
        assert abs(chunk.duration_seconds - 1.0) < 0.01

    def test_stereo_to_mono(self):
        stereo = np.zeros((8000, 2), dtype=np.float32)
        buf = io.BytesIO()
        sf.write(buf, stereo, 16000, format="WAV", subtype="PCM_16")
        wav = buf.getvalue()
        chunk = preprocess_audio(wav)
        assert chunk.samples.ndim == 1

    def test_empty_bytes_raises(self):
        with pytest.raises(ValueError, match="[Ee]mpty"):
            preprocess_audio(b"")

    def test_invalid_bytes_raises(self):
        with pytest.raises(ValueError):
            preprocess_audio(b"not_audio_data_at_all")

    def test_duration_correct(self):
        duration = 2.5
        n_samples = int(16000 * duration)
        samples = np.zeros(n_samples, dtype=np.float32)
        wav = make_wav_bytes(samples, sample_rate=16000)
        chunk = preprocess_audio(wav)
        assert abs(chunk.duration_seconds - duration) < 0.01

    def test_returns_audio_chunk(self):
        samples = np.zeros(1600, dtype=np.float32)
        wav = make_wav_bytes(samples, sample_rate=16000)
        chunk = preprocess_audio(wav)
        assert isinstance(chunk, AudioChunk)
        assert chunk.samples.dtype == np.float32
