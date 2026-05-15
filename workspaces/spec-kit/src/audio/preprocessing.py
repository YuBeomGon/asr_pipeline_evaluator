"""
Audio preprocessing for the ASR serving pipeline.

Spec ref: .specify/asr-pipeline-spec.md § FR-007
  - Resample audio to 16 kHz mono
  - Return numpy array and audio duration in seconds

Spec ref: .specify/asr-pipeline-spec.md § Assumptions
  - Input may be any format readable by soundfile
  - Non-readable formats return 422 at the API layer
"""

import io
from dataclasses import dataclass

import numpy as np
import soundfile as sf

from src.config.settings import settings


@dataclass
class AudioChunk:
    """Preprocessed audio data ready for ASR inference."""
    samples: np.ndarray      # float32, shape (N,), 16 kHz mono
    sample_rate: int         # always settings.target_sample_rate after preprocessing
    duration_seconds: float  # len(samples) / sample_rate


def _resample(samples: np.ndarray, orig_sr: int, target_sr: int) -> np.ndarray:
    """
    Simple linear-interpolation resampling.

    We use scipy.signal.resample_poly when available for quality, with a
    fallback to numpy interpolation so the service starts even without scipy.
    """
    if orig_sr == target_sr:
        return samples

    try:
        from scipy.signal import resample_poly
        from math import gcd
        g = gcd(target_sr, orig_sr)
        up, down = target_sr // g, orig_sr // g
        return resample_poly(samples, up, down).astype(np.float32)
    except ImportError:
        # Fallback: numpy linear interpolation
        n_target = int(len(samples) * target_sr / orig_sr)
        orig_indices = np.linspace(0, len(samples) - 1, n_target)
        return np.interp(orig_indices, np.arange(len(samples)), samples).astype(np.float32)


def preprocess_audio(audio_bytes: bytes) -> AudioChunk:
    """
    Decode, convert to mono, and resample audio bytes.

    Args:
        audio_bytes: Raw audio file bytes (WAV, FLAC, OGG, etc.)

    Returns:
        AudioChunk with 16 kHz mono float32 samples and duration.

    Raises:
        ValueError: If the audio cannot be decoded or is empty.
    """
    if not audio_bytes:
        raise ValueError("Empty audio file provided")

    try:
        buf = io.BytesIO(audio_bytes)
        samples, orig_sr = sf.read(buf, dtype="float32", always_2d=True)
    except Exception as exc:
        raise ValueError(f"Cannot decode audio: {exc}") from exc

    # Convert to mono by averaging channels (FR-007)
    if samples.shape[1] > 1:
        samples = samples.mean(axis=1)
    else:
        samples = samples[:, 0]

    # Resample to target sample rate (FR-007)
    target_sr = settings.target_sample_rate
    samples = _resample(samples, orig_sr, target_sr)

    if len(samples) == 0:
        raise ValueError("Audio contains no samples after preprocessing")

    duration = len(samples) / target_sr
    return AudioChunk(
        samples=samples,
        sample_rate=target_sr,
        duration_seconds=duration,
    )
