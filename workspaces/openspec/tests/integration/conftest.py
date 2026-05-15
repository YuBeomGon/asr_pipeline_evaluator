from __future__ import annotations
"""Pytest fixtures for integration tests."""
import io
import wave

import numpy as np
import pytest
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """FastAPI TestClient with session scope to avoid repeated app init."""
    with TestClient(app) as c:
        yield c


def make_wav_bytes(
    num_samples: int = 16000,
    sample_rate: int = 16000,
    num_channels: int = 1,
) -> bytes:
    """Generate a valid WAV file in memory."""
    buf = io.BytesIO()
    freq = 440.0
    t = np.linspace(0, num_samples / sample_rate, num_samples, endpoint=False)
    audio = (np.sin(2 * np.pi * freq * t) * 32767).astype(np.int16)
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(num_channels)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())
    buf.seek(0)
    return buf.read()


@pytest.fixture(scope="session")
def sample_wav() -> bytes:
    """A 1-second 16kHz mono WAV file for testing."""
    return make_wav_bytes()
