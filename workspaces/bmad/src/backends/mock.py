from __future__ import annotations
"""Mock ASR Backend.

BMAD Developer note: This backend is deterministic and requires no GPU,
network, or model weights. It is the default backend for local dev and tests.

The returned transcript is either:
1. The value of settings.mock_transcript (configurable via env var MOCK_TRANSCRIPT)
2. A deterministic text derived from audio length (for variety in tests)
"""
import unicodedata

import numpy as np

from src.config import get_settings
from .base import ASRBackend, TranscriptResult

_DEFAULT_TRANSCRIPTS = [
    "안녕하세요 이것은 모의 음성 인식 결과입니다",
    "테스트 음성 파일을 처리했습니다",
    "음성 인식 시스템이 정상 작동 중입니다",
    "모의 백엔드에서 처리된 결과입니다",
]


class MockASRBackend(ASRBackend):
    """Deterministic mock ASR backend for local development and testing.

    No GPU, no network, no model files required.
    """

    BACKEND_NAME = "mock"
    MODEL_NAME = "mock-asr"
    MODEL_VERSION = "0.1.0"

    def transcribe(self, audio: np.ndarray, sample_rate: int) -> TranscriptResult:
        settings = get_settings()

        if settings.mock_transcript:
            # Use configured transcript (NFC normalized)
            text = unicodedata.normalize("NFC", settings.mock_transcript)
        else:
            # Derive a deterministic transcript from audio duration
            duration_ms = int((len(audio) / max(sample_rate, 1)) * 1000)
            idx = duration_ms % len(_DEFAULT_TRANSCRIPTS)
            text = unicodedata.normalize("NFC", _DEFAULT_TRANSCRIPTS[idx])

        return TranscriptResult(
            text=text,
            confidence=settings.mock_confidence,
            backend=self.BACKEND_NAME,
            name=self.MODEL_NAME,
            version=self.MODEL_VERSION,
        )

    def health(self) -> bool:
        return True
