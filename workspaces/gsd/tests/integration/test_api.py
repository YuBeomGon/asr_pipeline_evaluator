"""Integration tests for the FastAPI application.

Uses httpx.AsyncClient with the real app (mock backend, in-process).
"""
from __future__ import annotations

import io
import wave

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.api.main import create_app


def make_wav_bytes(duration_s: float = 0.5, sample_rate: int = 16000) -> bytes:
    """Generate a minimal silent WAV file as bytes."""
    num_samples = int(duration_s * sample_rate)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)  # 16-bit
        w.setframerate(sample_rate)
        w.writeframes(b"\x00\x00" * num_samples)
    return buf.getvalue()


@pytest.fixture
def app():
    return create_app()


@pytest_asyncio.fixture
async def client(app):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_healthz_returns_ok(client):
    resp = await client.get("/healthz")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_metrics_endpoint(client):
    resp = await client.get("/metrics")
    assert resp.status_code == 200
    ct = resp.headers["content-type"]
    assert "text/plain" in ct
    body = resp.text
    # Prometheus required metrics
    assert "asr_requests_total" in body
    assert "asr_request_duration_seconds" in body
    assert "asr_errors_total" in body


@pytest.mark.asyncio
async def test_transcribe_success(client):
    wav_bytes = make_wav_bytes(duration_s=1.0)
    resp = await client.post(
        "/transcribe",
        files={"file": ("test.wav", wav_bytes, "audio/wav")},
    )
    assert resp.status_code == 200
    data = resp.json()

    # Required fields
    assert data["request_id"].startswith("req_")
    assert isinstance(data["transcript"], str)
    assert 0.0 <= data["confidence"] <= 1.0
    assert data["audio_duration_seconds"] > 0.0

    timing = data["timing"]
    assert "preprocess_ms" in timing
    assert "inference_ms" in timing
    assert "postprocess_ms" in timing
    assert "total_ms" in timing

    model = data["model"]
    assert model["backend"] == "mock"
    assert model["name"] == "mock-asr"
    assert model["version"] == "0.1.0"


@pytest.mark.asyncio
async def test_transcribe_empty_file(client):
    resp = await client.post(
        "/transcribe",
        files={"file": ("empty.wav", b"", "audio/wav")},
    )
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_transcribe_invalid_audio(client):
    resp = await client.post(
        "/transcribe",
        files={"file": ("garbage.wav", b"not-audio-data-at-all", "audio/wav")},
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_eval_cer_perfect(client):
    payload = {
        "pairs": [
            {"id": "s1", "reference": "안녕하세요", "hypothesis": "안녕하세요"}
        ]
    }
    resp = await client.post("/eval/cer", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["aggregate"]["num_samples"] == 1
    assert data["aggregate"]["micro_cer"] == 0.0
    assert data["samples"][0]["cer"] == 0.0


@pytest.mark.asyncio
async def test_eval_cer_multiple_pairs(client):
    payload = {
        "pairs": [
            {"id": "a", "reference": "hello", "hypothesis": "hello"},
            {"id": "b", "reference": "world", "hypothesis": "word"},
        ]
    }
    resp = await client.post("/eval/cer", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["aggregate"]["num_samples"] == 2
    assert data["samples"][0]["cer"] == 0.0
    assert data["samples"][1]["cer"] > 0.0


@pytest.mark.asyncio
async def test_eval_cer_empty_pairs(client):
    payload = {"pairs": []}
    resp = await client.post("/eval/cer", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["aggregate"]["num_samples"] == 0


@pytest.mark.asyncio
async def test_metrics_incremented_after_transcribe(client):
    wav_bytes = make_wav_bytes(0.5)
    await client.post("/transcribe", files={"file": ("t.wav", wav_bytes, "audio/wav")})
    resp = await client.get("/metrics")
    body = resp.text
    assert 'asr_requests_total{status="success"}' in body
