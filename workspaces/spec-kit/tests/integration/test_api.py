"""
Integration tests for all API endpoints.

Spec ref: .specify/asr-pipeline-spec.md § FR-015, SC-001 through SC-007
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthz:
    """Spec ref: .specify/asr-pipeline-spec.md § FR-001, SC-001"""

    def test_returns_200(self, client: TestClient):
        response = client.get("/healthz")
        assert response.status_code == 200

    def test_returns_status_ok(self, client: TestClient):
        response = client.get("/healthz")
        assert response.json() == {"status": "ok"}


class TestMetrics:
    """Spec ref: .specify/asr-pipeline-spec.md § FR-002, SC-002"""

    def test_returns_200(self, client: TestClient):
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_content_type_prometheus(self, client: TestClient):
        response = client.get("/metrics")
        ct = response.headers.get("content-type", "")
        assert "text/plain" in ct

    def test_contains_required_metrics(self, client: TestClient):
        # Trigger a transcription first so counters are non-zero
        response = client.get("/metrics")
        text = response.text
        assert "asr_requests_total" in text
        assert "asr_request_duration_seconds" in text
        assert "asr_errors_total" in text


class TestTranscribe:
    """Spec ref: .specify/asr-pipeline-spec.md § FR-003, SC-003"""

    def test_valid_wav_returns_200(self, client: TestClient, wav_bytes_16k: bytes):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", wav_bytes_16k, "audio/wav")},
        )
        assert response.status_code == 200

    def test_response_schema_fields(self, client: TestClient, wav_bytes_16k: bytes):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", wav_bytes_16k, "audio/wav")},
        )
        data = response.json()
        required_keys = {
            "request_id", "transcript", "confidence",
            "audio_duration_seconds", "timing", "model",
        }
        assert required_keys.issubset(data.keys())

    def test_request_id_prefix(self, client: TestClient, wav_bytes_16k: bytes):
        """Spec ref: FR-008 — request_id MUST start with 'req_'"""
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", wav_bytes_16k, "audio/wav")},
        )
        data = response.json()
        assert data["request_id"].startswith("req_")

    def test_request_ids_are_unique(self, client: TestClient, wav_bytes_16k: bytes):
        ids = set()
        for _ in range(5):
            response = client.post(
                "/transcribe",
                files={"file": ("test.wav", wav_bytes_16k, "audio/wav")},
            )
            ids.add(response.json()["request_id"])
        assert len(ids) == 5

    def test_timing_fields_present(self, client: TestClient, wav_bytes_16k: bytes):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", wav_bytes_16k, "audio/wav")},
        )
        timing = response.json()["timing"]
        assert all(k in timing for k in ["preprocess_ms", "inference_ms", "postprocess_ms", "total_ms"])

    def test_model_fields_present(self, client: TestClient, wav_bytes_16k: bytes):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", wav_bytes_16k, "audio/wav")},
        )
        model = response.json()["model"]
        assert all(k in model for k in ["backend", "name", "version"])

    def test_model_backend_is_mock(self, client: TestClient, wav_bytes_16k: bytes):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", wav_bytes_16k, "audio/wav")},
        )
        assert response.json()["model"]["backend"] == "mock"

    def test_confidence_in_range(self, client: TestClient, wav_bytes_16k: bytes):
        response = client.post(
            "/transcribe",
            files={"file": ("test.wav", wav_bytes_16k, "audio/wav")},
        )
        confidence = response.json()["confidence"]
        assert 0.0 <= confidence <= 1.0

    def test_empty_file_returns_422(self, client: TestClient):
        response = client.post(
            "/transcribe",
            files={"file": ("empty.wav", b"", "audio/wav")},
        )
        assert response.status_code == 422

    def test_invalid_audio_returns_422(self, client: TestClient):
        response = client.post(
            "/transcribe",
            files={"file": ("bad.wav", b"not_audio_at_all", "audio/wav")},
        )
        assert response.status_code == 422

    def test_resampling_44k_stereo(self, client: TestClient, wav_bytes_44k: bytes):
        """44.1 kHz stereo input should be resampled and still return 200."""
        response = client.post(
            "/transcribe",
            files={"file": ("stereo.wav", wav_bytes_44k, "audio/wav")},
        )
        assert response.status_code == 200

    def test_metrics_incremented_after_request(self, client: TestClient, wav_bytes_16k: bytes):
        """Spec ref: FR-002 — asr_requests_total should increment after transcription."""
        client.post(
            "/transcribe",
            files={"file": ("test.wav", wav_bytes_16k, "audio/wav")},
        )
        metrics_resp = client.get("/metrics")
        assert 'asr_requests_total{status="success"}' in metrics_resp.text


class TestEvalCER:
    """Spec ref: .specify/asr-pipeline-spec.md § FR-004, SC-004"""

    def test_perfect_match_returns_zero_cer(self, client: TestClient):
        response = client.post(
            "/eval/cer",
            json={"pairs": [{"id": "s1", "reference": "안녕하세요", "hypothesis": "안녕하세요"}]},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["overall_cer"] == pytest.approx(0.0)

    def test_response_schema(self, client: TestClient):
        response = client.post(
            "/eval/cer",
            json={"pairs": [{"id": "s1", "reference": "hello", "hypothesis": "hello"}]},
        )
        data = response.json()
        assert "pairs" in data
        assert "overall_cer" in data
        assert "total_reference_chars" in data
        assert "total_edits" in data

    def test_per_sample_cer_fields(self, client: TestClient):
        response = client.post(
            "/eval/cer",
            json={"pairs": [{"id": "s1", "reference": "hello", "hypothesis": "hello"}]},
        )
        pair = response.json()["pairs"][0]
        assert all(k in pair for k in ["id", "cer", "reference_chars", "edits"])

    def test_empty_hypothesis_cer_is_one(self, client: TestClient):
        response = client.post(
            "/eval/cer",
            json={"pairs": [{"id": "s1", "reference": "hello", "hypothesis": ""}]},
        )
        data = response.json()
        assert data["overall_cer"] == pytest.approx(1.0)

    def test_empty_reference_cer_is_null(self, client: TestClient):
        response = client.post(
            "/eval/cer",
            json={"pairs": [{"id": "s1", "reference": "", "hypothesis": "hello"}]},
        )
        pair = response.json()["pairs"][0]
        assert pair["cer"] is None

    def test_multiple_pairs(self, client: TestClient):
        response = client.post(
            "/eval/cer",
            json={
                "pairs": [
                    {"id": "s1", "reference": "hello", "hypothesis": "hello"},
                    {"id": "s2", "reference": "world", "hypothesis": "word"},
                ]
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["pairs"]) == 2

    def test_empty_pairs_rejected(self, client: TestClient):
        response = client.post("/eval/cer", json={"pairs": []})
        assert response.status_code == 422
