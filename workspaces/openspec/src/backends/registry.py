from __future__ import annotations
"""
Backend registry: maps backend names to factory functions.
Add new backends here to make them available via the ASR_BACKEND env var.
"""
from functools import lru_cache
from typing import TYPE_CHECKING

from .base import ASRBackend
from .mock import MockASRBackend

if TYPE_CHECKING:
    from src.config.settings import Settings


def _make_mock(settings: "Settings") -> MockASRBackend:
    return MockASRBackend(
        transcript=settings.mock_transcript,
        confidence=settings.mock_confidence,
        inference_delay_ms=settings.mock_inference_delay_ms,
    )


_REGISTRY = {
    "mock": _make_mock,
}


@lru_cache(maxsize=1)
def get_backend() -> ASRBackend:
    """
    Return the configured ASR backend singleton.
    The backend is instantiated once and reused across requests.
    """
    from src.config.settings import get_settings

    settings = get_settings()
    factory = _REGISTRY.get(settings.backend)
    if factory is None:
        raise ValueError(
            f"Unknown ASR backend: '{settings.backend}'. "
            f"Available: {list(_REGISTRY.keys())}"
        )
    return factory(settings)
