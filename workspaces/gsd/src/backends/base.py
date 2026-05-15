"""ASR backend abstract base class and result type."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

import numpy as np


@dataclass
class TranscriptResult:
    """Normalized output from any ASR backend."""

    transcript: str
    confidence: float  # 0.0 – 1.0
    backend_name: str
    model_name: str
    model_version: str
    inference_ms: float  # wall-clock time inside the backend call


class ASRBackend(ABC):
    """Abstract base for all ASR backends.

    Implementations must be stateless and thread-safe with respect to
    the `transcribe` method (shared model state is fine, but no per-call
    mutable state on self).
    """

    @abstractmethod
    def transcribe(self, audio: np.ndarray, sample_rate: int) -> TranscriptResult:
        """Transcribe a mono 16 kHz audio array.

        Args:
            audio: 1-D float32 numpy array, already resampled to ``sample_rate``.
            sample_rate: Must be 16000 for all production backends.

        Returns:
            TranscriptResult with transcript and metadata.
        """

    @property
    @abstractmethod
    def name(self) -> str:
        """Short backend identifier, e.g. 'mock' or 'whisper'."""
