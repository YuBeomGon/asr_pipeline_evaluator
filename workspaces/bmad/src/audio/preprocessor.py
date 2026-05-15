"""Audio preprocessing pipeline.

BMAD Developer: Handles byte -> numpy conversion, mono downmix, and
resampling to the target sample rate (16 kHz). No external ML deps required.
"""
from __future__ import annotations

import io
from dataclasses import dataclass

import numpy as np
import soundfile as sf
from scipy.signal import resample_poly
from math import gcd

from src.config import get_settings


@dataclass
class PreprocessResult:
    audio: np.ndarray        # float32, shape (N,), mono, target_sample_rate
    sample_rate: int         # always == settings.target_sample_rate
    duration_seconds: float  # original audio duration
    original_sample_rate: int


class AudioPreprocessor:
    """Convert raw audio bytes to a normalized numpy array."""

    def __init__(self, target_sample_rate: int | None = None) -> None:
        settings = get_settings()
        self.target_sample_rate = target_sample_rate or settings.target_sample_rate

    def preprocess(self, audio_bytes: bytes) -> PreprocessResult:
        """Process raw audio bytes into a normalized float32 array.

        Steps:
        1. Decode via soundfile (supports WAV, FLAC, OGG, etc.)
        2. Convert to float32
        3. Downmix to mono (average channels)
        4. Resample to target_sample_rate if needed

        Args:
            audio_bytes: Raw audio file bytes.

        Returns:
            PreprocessResult with audio array and metadata.

        Raises:
            ValueError: If audio_bytes cannot be decoded.
        """
        try:
            audio, orig_sr = sf.read(io.BytesIO(audio_bytes), dtype="float32", always_2d=True)
        except Exception as e:
            raise ValueError(f"Cannot decode audio: {e}") from e

        # Ensure float32
        audio = audio.astype(np.float32)

        # Compute duration from original data
        n_frames, n_channels = audio.shape
        duration_seconds = n_frames / orig_sr

        # Mono downmix
        if n_channels > 1:
            audio = audio.mean(axis=1)
        else:
            audio = audio[:, 0]

        # Resample if needed
        if orig_sr != self.target_sample_rate:
            audio = self._resample(audio, orig_sr, self.target_sample_rate)

        return PreprocessResult(
            audio=audio,
            sample_rate=self.target_sample_rate,
            duration_seconds=duration_seconds,
            original_sample_rate=orig_sr,
        )

    @staticmethod
    def _resample(audio: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
        """Resample audio using rational resampling (polyphase filter)."""
        divisor = gcd(target_sr, orig_sr)
        up = target_sr // divisor
        down = orig_sr // divisor
        resampled = resample_poly(audio, up, down)
        return resampled.astype(np.float32)

    @staticmethod
    def generate_silence(duration_seconds: float, sample_rate: int = 16000) -> bytes:
        """Generate silent WAV bytes for testing."""
        import io as _io
        n_samples = int(duration_seconds * sample_rate)
        silence = np.zeros(n_samples, dtype=np.float32)
        buf = _io.BytesIO()
        sf.write(buf, silence, sample_rate, format="WAV", subtype="FLOAT")
        buf.seek(0)
        return buf.read()
