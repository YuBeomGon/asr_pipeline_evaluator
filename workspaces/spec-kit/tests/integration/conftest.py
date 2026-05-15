"""
Shared fixtures for integration tests.

Spec ref: .specify/asr-pipeline-spec.md § FR-015
"""

import io
import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient

from src.api.main import app


@pytest.fixture(scope="module")
def client():
    """Return a synchronous TestClient for the FastAPI app."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def wav_bytes_16k():
    """Return 1-second of silence as WAV bytes at 16 kHz mono."""
    samples = np.zeros(16000, dtype=np.float32)
    buf = io.BytesIO()
    sf.write(buf, samples, 16000, format="WAV", subtype="PCM_16")
    return buf.getvalue()


@pytest.fixture
def wav_bytes_44k():
    """Return 1-second of silence as WAV bytes at 44.1 kHz stereo (needs resampling)."""
    samples = np.zeros((44100, 2), dtype=np.float32)
    buf = io.BytesIO()
    sf.write(buf, samples, 44100, format="WAV", subtype="PCM_16")
    return buf.getvalue()
