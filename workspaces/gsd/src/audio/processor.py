"""Audio preprocessing: load, resample to 16 kHz mono, return numpy + duration."""
from __future__ import annotations

import io
from dataclasses import dataclass

import numpy as np
import soundfile as sf
import librosa


TARGET_SR = 16_000  # Hz


@dataclass
class AudioChunk:
    samples: np.ndarray  # float32, mono, 16 kHz
    sample_rate: int
    duration_seconds: float
    original_sample_rate: int
    num_channels: int


def load_audio(raw_bytes: bytes) -> AudioChunk:
    """Load audio bytes (any format soundfile supports) and resample to 16 kHz mono.

    Returns an AudioChunk ready for ASR inference.
    """
    buf = io.BytesIO(raw_bytes)

    # Read with soundfile (supports WAV, FLAC, OGG, etc.)
    try:
        data, sr = sf.read(buf, dtype="float32", always_2d=True)
    except Exception as exc:
        raise ValueError(f"Could not decode audio: {exc}") from exc

    original_sr = sr
    num_channels = data.shape[1]

    # Convert to mono by averaging channels
    if num_channels > 1:
        data = data.mean(axis=1)
    else:
        data = data[:, 0]

    # Resample if needed
    if sr != TARGET_SR:
        data = librosa.resample(data, orig_sr=sr, target_sr=TARGET_SR)
        sr = TARGET_SR

    # Ensure float32
    data = data.astype(np.float32)

    duration = len(data) / sr

    return AudioChunk(
        samples=data,
        sample_rate=sr,
        duration_seconds=duration,
        original_sample_rate=original_sr,
        num_channels=num_channels,
    )
