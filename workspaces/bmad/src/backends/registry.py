"""Backend registry.

BMAD Architect decision: backends are registered by string name.
Adding a new backend means adding one entry here — no other code changes.

Usage:
    backend = get_backend()          # uses settings.asr_backend
    backend = get_backend("mock")    # explicit name
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from src.config import get_settings

if TYPE_CHECKING:
    from .base import ASRBackend


_REGISTRY: dict[str, type] = {}


def register(name: str):
    """Decorator to register a backend class."""
    def decorator(cls):
        _REGISTRY[name] = cls
        return cls
    return decorator


# Lazy imports to avoid circular deps and heavy library loading
def _load_registry() -> None:
    if _REGISTRY:
        return
    # Always register mock
    from .mock import MockASRBackend
    _REGISTRY["mock"] = MockASRBackend


def get_backend(name: str | None = None) -> "ASRBackend":
    """Return an instantiated ASR backend.

    Args:
        name: Backend name. If None, reads from settings.asr_backend.

    Raises:
        ValueError: If the backend name is not registered.
    """
    _load_registry()

    if name is None:
        name = get_settings().asr_backend

    cls = _REGISTRY.get(name)
    if cls is None:
        available = sorted(_REGISTRY.keys())
        raise ValueError(
            f"Unknown ASR backend '{name}'. Available backends: {available}"
        )

    return cls()
