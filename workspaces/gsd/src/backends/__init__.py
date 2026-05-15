"""Backend registry."""
from __future__ import annotations

from .base import ASRBackend, TranscriptResult
from .mock import MockASRBackend


def get_backend(name: str) -> ASRBackend:
    backends = {
        "mock": MockASRBackend,
    }
    cls = backends.get(name.lower())
    if cls is None:
        raise ValueError(f"Unknown ASR backend: {name!r}. Available: {list(backends)}")
    return cls()


__all__ = ["ASRBackend", "TranscriptResult", "MockASRBackend", "get_backend"]
