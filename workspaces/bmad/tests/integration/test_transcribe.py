from __future__ import annotations
"""Integration tests for POST /transcribe."""
import pytest


@pytest.mark.asyncio
async def test_transcribe_returns_200(client, wav_bytes_1s):
    response = await client.post(
        "/transcribe",
        files={"file": ("test.wav", wav_bytes_1s, "audio/wav")},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_transcribe_response_schema(client, wav_bytes_1s):
    response = await client.post(
        "/transcribe",
        files={"file": ("test.wav", wav_bytes_1s, "audio/wav")},
    )
    body = response.json()

    # Required top-level fields
    assert "request_id" in body
    assert "transcript" in body
    assert "confidence" in body
    assert "audio_duration_seconds" in body
    assert "timing" in body
    assert "model" in body


@pytest.mark.asyncio
async def test_transcribe_request_id_prefix(client, wav_bytes_1s):
    response = await client.post(
        "/transcribe",
        files={"file": ("test.wav", wav_bytes_1s, "audio/wav")},
    )
    body = response.json()
    assert body["request_id"].startswith("req_")


@pytest.mark.asyncio
async def test_transcribe_request_id_unique(client, wav_bytes_1s):
    r1 = await client.post(
        "/transcribe",
        files={"file": ("test.wav", wav_bytes_1s, "audio/wav")},
    )
    r2 = await client.post(
        "/transcribe",
        files={"file": ("test.wav", wav_bytes_1s, "audio/wav")},
    )
    assert r1.json()["request_id"] != r2.json()["request_id"]


@pytest.mark.asyncio
async def test_transcribe_timing_fields(client, wav_bytes_1s):
    response = await client.post(
        "/transcribe",
        files={"file": ("test.wav", wav_bytes_1s, "audio/wav")},
    )
    timing = response.json()["timing"]
    assert "preprocess_ms" in timing
    assert "inference_ms" in timing
    assert "postprocess_ms" in timing
    assert "total_ms" in timing
    for k, v in timing.items():
        assert isinstance(v, (int, float)), f"{k} should be numeric"
        assert v >= 0


@pytest.mark.asyncio
async def test_transcribe_model_fields(client, wav_bytes_1s):
    response = await client.post(
        "/transcribe",
        files={"file": ("test.wav", wav_bytes_1s, "audio/wav")},
    )
    model = response.json()["model"]
    assert "backend" in model
    assert "name" in model
    assert "version" in model
    assert model["backend"] == "mock"


@pytest.mark.asyncio
async def test_transcribe_confidence_range(client, wav_bytes_1s):
    response = await client.post(
        "/transcribe",
        files={"file": ("test.wav", wav_bytes_1s, "audio/wav")},
    )
    confidence = response.json()["confidence"]
    assert 0.0 <= confidence <= 1.0


@pytest.mark.asyncio
async def test_transcribe_audio_duration_positive(client, wav_bytes_1s):
    response = await client.post(
        "/transcribe",
        files={"file": ("test.wav", wav_bytes_1s, "audio/wav")},
    )
    duration = response.json()["audio_duration_seconds"]
    assert duration > 0


@pytest.mark.asyncio
async def test_transcribe_stereo_audio(client, wav_bytes_stereo):
    """Stereo audio should be downmixed and processed successfully."""
    response = await client.post(
        "/transcribe",
        files={"file": ("stereo.wav", wav_bytes_stereo, "audio/wav")},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_transcribe_invalid_audio_returns_422(client):
    response = await client.post(
        "/transcribe",
        files={"file": ("bad.wav", b"this is not audio", "audio/wav")},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_transcribe_no_file_returns_422(client):
    response = await client.post("/transcribe")
    assert response.status_code == 422
