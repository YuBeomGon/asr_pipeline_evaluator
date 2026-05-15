"""
ASRBackend abstract base class and shared data models.

Spec ref: .specify/asr-pipeline-spec.md § FR-005
  ASRBackend ABC with method: transcribe(audio_bytes, sample_rate) -> TranscriptResult

Spec ref: .specify/asr-pipeline-spec.md § Key Entities
  TranscriptResult, TimingInfo, ModelInfo
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field


@dataclass
class TimingInfo:
    """Timing breakdown for a single transcription request (milliseconds)."""
    preprocess_ms: float = 0.0
    inference_ms: float = 0.0
    postprocess_ms: float = 0.0
    total_ms: float = 0.0


@dataclass
class ModelInfo:
    """Metadata about the ASR model/backend that produced a result."""
    backend: str = "mock"
    name: str = "mock-asr"
    version: str = "0.1.0"


@dataclass
class TranscriptResult:
    """
    Full result from a single ASR transcription call.

    Spec ref: .specify/asr-pipeline-spec.md § Key Entities → TranscriptResult
    """
    transcript: str
    confidence: float
    audio_duration_seconds: float
    timing: TimingInfo = field(default_factory=TimingInfo)
    model: ModelInfo = field(default_factory=ModelInfo)


class ASRBackend(ABC):
    """
    Abstract base class for all ASR backends.

    Spec ref: .specify/asr-pipeline-spec.md § FR-005
      All ASR calls go through this interface (NFR-005).
      Concrete backends MUST NOT leak implementation details into the API layer.

    Implementation contract:
      transcribe(audio_bytes, sample_rate) -> TranscriptResult
        audio_bytes  : raw audio samples as bytes (float32 array serialised to bytes)
                       OR the original encoded audio bytes — concrete backends decide.
        sample_rate  : sample rate of the audio in Hz (always 16000 after preprocessing)
    """

    @abstractmethod
    def transcribe(self, audio_bytes: bytes, sample_rate: int) -> TranscriptResult:
        """
        Transcribe audio and return a TranscriptResult.

        Args:
            audio_bytes: Audio data bytes (preprocessed to 16 kHz mono float32).
            sample_rate: Sample rate, always 16000 after preprocessing.

        Returns:
            TranscriptResult with transcript, confidence, timing, and model info.
        """
        ...

    @property
    @abstractmethod
    def backend_name(self) -> str:
        """Human-readable identifier for this backend."""
        ...
