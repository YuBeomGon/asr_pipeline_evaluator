# Spec ref: .specify/asr-pipeline-spec.md § FR-005, FR-006
from src.backends.base import ASRBackend, TranscriptResult, TimingInfo, ModelInfo
from src.backends.mock import MockASRBackend

__all__ = ["ASRBackend", "TranscriptResult", "TimingInfo", "ModelInfo", "MockASRBackend"]
