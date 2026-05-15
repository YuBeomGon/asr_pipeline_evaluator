"""Shared pytest fixtures for the ASR pipeline test suite.

BMAD QA: All fixtures are defined here to avoid duplication across test modules.
Tests use `httpx.AsyncClient` with the app directly — no server process needed.
"""
from __future__ import annotations

import io

import numpy as np
import pytest
import pytest_asyncio
import soundfile as sf
from httpx import AsyncClient, ASGITransport

from src.api.main import app as _app


# ─────────────────────────────── App fixture ───────────────────────────────

@pytest.fixture(scope="session")
def app():
    """Return the module-level FastAPI app instance (created once at import)."""
    return _app


@pytest_asyncio.fixture
async def client(app):
    """Async HTTP client connected to the FastAPI app (no server startup)."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


# ─────────────────────────────── Audio fixtures ────────────────────────────

def make_wav_bytes(
    duration_seconds: float = 1.0,
    sample_rate: int = 16000,
    frequency: float = 440.0,
) -> bytes:
    """Generate a synthetic sine-wave WAV file as bytes."""
    n_samples = int(duration_seconds * sample_rate)
    t = np.linspace(0, duration_seconds, n_samples, endpoint=False)
    audio = (np.sin(2 * np.pi * frequency * t) * 0.5).astype(np.float32)

    buf = io.BytesIO()
    sf.write(buf, audio, sample_rate, format="WAV", subtype="FLOAT")
    buf.seek(0)
    return buf.read()


@pytest.fixture
def wav_bytes_1s():
    """1-second 16 kHz mono WAV file."""
    return make_wav_bytes(duration_seconds=1.0)


@pytest.fixture
def wav_bytes_short():
    """0.1-second silent WAV file."""
    n = int(0.1 * 16000)
    silence = np.zeros(n, dtype=np.float32)
    buf = io.BytesIO()
    sf.write(buf, silence, 16000, format="WAV", subtype="FLOAT")
    buf.seek(0)
    return buf.read()


@pytest.fixture
def wav_bytes_stereo():
    """1-second stereo WAV file (2 channels)."""
    n_samples = 16000
    audio = np.zeros((n_samples, 2), dtype=np.float32)
    buf = io.BytesIO()
    sf.write(buf, audio, 16000, format="WAV", subtype="FLOAT")
    buf.seek(0)
    return buf.read()
