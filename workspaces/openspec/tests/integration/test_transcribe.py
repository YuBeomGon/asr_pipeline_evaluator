from __future__ import annotations
"""Integration tests for POST /transcribe."""
import pytest


class TestTranscribeEndpoint:
    def test_transcribe_returns_200(self, client, sample_wav):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", sample_wav, "audio/wav")},
        )
        assert response.status_code == 200

    def test_transcribe_response_schema(self, client, sample_wav):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", sample_wav, "audio/wav")},
        )
        data = response.json()

        assert "request_id" in data
        assert "transcript" in data
        assert "confidence" in data
        assert "audio_duration_seconds" in data
        assert "timing" in data
        assert "model" in data

    def test_request_id_format(self, client, sample_wav):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", sample_wav, "audio/wav")},
        )
        data = response.json()
        assert data["request_id"].startswith("req_")

    def test_request_id_unique(self, client, sample_wav):
        r1 = client.post("/transcribe", files={"file": ("test.wav", sample_wav, "audio/wav")})
        r2 = client.post("/transcribe", files={"file": ("test.wav", sample_wav, "audio/wav")})
        assert r1.json()["request_id"] != r2.json()["request_id"]

    def test_confidence_in_range(self, client, sample_wav):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", sample_wav, "audio/wav")},
        )
        data = response.json()
        assert 0.0 <= data["confidence"] <= 1.0

    def test_audio_duration_positive(self, client, sample_wav):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", sample_wav, "audio/wav")},
        )
        data = response.json()
        assert data["audio_duration_seconds"] > 0.0

    def test_timing_fields(self, client, sample_wav):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", sample_wav, "audio/wav")},
        )
        timing = response.json()["timing"]
        for field in ["preprocess_ms", "inference_ms", "postprocess_ms", "total_ms"]:
            assert field in timing
            assert timing[field] >= 0.0

    def test_model_fields(self, client, sample_wav):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", sample_wav, "audio/wav")},
        )
        model = response.json()["model"]
        assert model["backend"] == "mock"
        assert model["name"] == "mock-asr"
        assert "version" in model

    def test_transcript_is_string(self, client, sample_wav):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", sample_wav, "audio/wav")},
        )
        assert isinstance(response.json()["transcript"], str)

    def test_empty_file_returns_400(self, client):
        response = client.post(
            "/transcribe",
            files={"file": ("empty.wav", b"", "audio/wav")},
        )
        assert response.status_code == 400

    def test_invalid_audio_returns_400(self, client):
        response = client.post(
            "/transcribe",
            files={"file": ("bad.wav", b"this is not audio", "audio/wav")},
        )
        assert response.status_code == 400

    def test_missing_file_returns_422(self, client):
        response = client.post("/transcribe")
        assert response.status_code == 422
