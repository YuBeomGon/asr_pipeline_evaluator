from __future__ import annotations
"""
Audio preprocessing module.
Handles loading audio from bytes, resampling to target_sample_rate (16 kHz),
converting to mono, and returning a float32 numpy array with duration.
"""
import io
from dataclasses import dataclass

import numpy as np
import soundfile as sf


@dataclass
class PreprocessResult:
    """Result of audio preprocessing."""

    audio: np.ndarray
    """float32 mono audio array, shape (num_samples,)"""

    sample_rate: int
    """Sample rate of the returned audio array (always target_sample_rate)"""

    duration_seconds: float
    """Audio duration in seconds"""


class AudioPreprocessingError(Exception):
    """Raised when audio preprocessing fails."""


class AudioPreprocessor:
    """
    Loads raw audio bytes, converts to mono float32, and resamples.
    Uses soundfile for decoding (supports WAV, FLAC, OGG, AIFF).
    Uses simple linear resampling when the sample rate differs.
    """

    def __init__(self, target_sample_rate: int = 16000) -> None:
        self.target_sample_rate = target_sample_rate

    def preprocess(self, audio_bytes: bytes) -> PreprocessResult:
        """
        Preprocess raw audio bytes.

        Args:
            audio_bytes: Raw audio file bytes (WAV, FLAC, OGG, etc.)

        Returns:
            PreprocessResult with mono float32 array at target_sample_rate.

        Raises:
            AudioPreprocessingError: If the audio cannot be decoded or processed.
        """
        if not audio_bytes:
            raise AudioPreprocessingError("Empty audio bytes received")

        try:
            buf = io.BytesIO(audio_bytes)
            audio, src_sample_rate = sf.read(buf, dtype="float32", always_2d=False)
        except Exception as exc:
            raise AudioPreprocessingError(
                f"Failed to decode audio: {exc}"
            ) from exc

        # Convert to mono if multi-channel
        if audio.ndim == 2:
            audio = audio.mean(axis=1)

        # Resample if needed
        if src_sample_rate != self.target_sample_rate:
            audio = self._resample(audio, src_sample_rate, self.target_sample_rate)

        duration = len(audio) / self.target_sample_rate

        return PreprocessResult(
            audio=audio.astype(np.float32),
            sample_rate=self.target_sample_rate,
            duration_seconds=duration,
        )

    @staticmethod
    def _resample(
        audio: np.ndarray, src_rate: int, dst_rate: int
    ) -> np.ndarray:
        """
        Linear interpolation resampling (lightweight, no extra deps).
        For production use, replace with scipy.signal.resample or librosa.resample.
        """
        if src_rate == dst_rate:
            return audio

        num_samples_dst = int(len(audio) * dst_rate / src_rate)
        if num_samples_dst == 0:
            return np.array([], dtype=np.float32)

        # Build index arrays for linear interpolation
        src_indices = np.linspace(0, len(audio) - 1, num_samples_dst)
        left_indices = np.floor(src_indices).astype(int)
        right_indices = np.minimum(left_indices + 1, len(audio) - 1)
        fractions = src_indices - left_indices

        resampled = (
            audio[left_indices] * (1 - fractions) + audio[right_indices] * fractions
        )
        return resampled.astype(np.float32)
