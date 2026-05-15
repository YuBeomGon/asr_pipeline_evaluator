from __future__ import annotations
"""Integration tests for GET /metrics."""


class TestMetricsEndpoint:
    def test_metrics_returns_200(self, client):
        response = client.get("/metrics")
        assert response.status_code == 200

    def test_metrics_content_type(self, client):
        response = client.get("/metrics")
        ct = response.headers["content-type"]
        assert "text/plain" in ct

    def test_metrics_contains_asr_requests_total(self, client):
        # Make a transcription request first so the metric has a value
        response = client.get("/metrics")
        text = response.text
        assert "asr_requests_total" in text

    def test_metrics_contains_duration_histogram(self, client):
        response = client.get("/metrics")
        text = response.text
        assert "asr_request_duration_seconds" in text

    def test_metrics_contains_errors_total(self, client):
        response = client.get("/metrics")
        text = response.text
        assert "asr_errors_total" in text

    def test_metrics_prometheus_format(self, client):
        response = client.get("/metrics")
        text = response.text
        # Prometheus format starts with # HELP or # TYPE lines
        assert "# HELP" in text or "# TYPE" in text
