from __future__ import annotations
"""ASR Backend abstract base class.

BMAD Architect decision: ASRBackend is the only interface the API layer
depends on. Any real ASR engine (Whisper, Azure, Google) must implement
this interface. Swapping backends requires changing only the registry
selection, not any route code.
"""
from abc import ABC, abstractmethod

import numpy as np
from pydantic import BaseModel


class TranscriptResult(BaseModel):
    """The result returned by any ASR backend."""
    text: str
    confidence: float
    backend: str
    name: str
    version: str


class ASRBackend(ABC):
    """Abstract base class for all ASR backends.

    Implementations must be stateless with respect to individual requests
    (or manage state thread-safely). The API layer calls `transcribe` once
    per request and `health` during health checks.
    """

    @abstractmethod
    def transcribe(self, audio: np.ndarray, sample_rate: int) -> TranscriptResult:
        """Transcribe audio samples to text.

        Args:
            audio: Float32 numpy array, shape (N,) or (N, channels), mono preferred.
            sample_rate: Sample rate of the audio array (should be 16000 Hz after preprocessing).

        Returns:
            TranscriptResult with text, confidence, and model metadata.
        """
        ...

    @abstractmethod
    def health(self) -> bool:
        """Return True if the backend is ready to serve requests."""
        ...
