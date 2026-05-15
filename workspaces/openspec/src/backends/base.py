from __future__ import annotations
"""
Abstract base class for ASR backends.
All backends must implement the ASRBackend interface.
Swapping backends (mock -> Whisper, NeMo, etc.) requires no changes
to the API layer — only the backend implementation changes.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

import numpy as np


@dataclass
class TranscriptResult:
    """Result returned by an ASR backend."""

    transcript: str
    """Raw transcript string (before postprocessing)."""

    confidence: float
    """Confidence score in [0, 1]. Backend-specific semantics."""

    inference_ms: float
    """Time spent in backend inference (milliseconds)."""

    backend_name: str
    """Human-readable backend identifier (e.g. 'mock', 'whisper')."""

    model_name: str
    """Model name/path used for inference."""

    model_version: str
    """Model version string."""

    extras: dict = field(default_factory=dict)
    """Optional backend-specific metadata."""


class ASRBackend(ABC):
    """
    Abstract base class for ASR inference backends.

    Implementations must be stateless with respect to request data;
    any shared state (models, caches) should be initialized in __init__
    and treated as read-only during transcription.
    """

    @abstractmethod
    def transcribe(self, audio: np.ndarray, sample_rate: int) -> TranscriptResult:
        """
        Transcribe a mono float32 audio array.

        Args:
            audio: 1-D float32 numpy array, already resampled to sample_rate.
            sample_rate: Sample rate of the audio array (Hz).

        Returns:
            TranscriptResult with raw transcript and metadata.

        Raises:
            ASRBackendError: If inference fails.
        """

    @abstractmethod
    def health_check(self) -> bool:
        """Return True if the backend is ready to serve requests."""

    @property
    @abstractmethod
    def backend_id(self) -> str:
        """Short identifier for this backend (e.g. 'mock', 'whisper')."""


class ASRBackendError(Exception):
    """Raised when an ASR backend encounters an error during inference."""
