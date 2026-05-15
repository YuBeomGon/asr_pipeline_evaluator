from __future__ import annotations
"""Integration tests for GET /healthz."""
import pytest


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/healthz")
        assert response.status_code == 200

    def test_health_returns_json(self, client):
        response = client.get("/healthz")
        data = response.json()
        assert "status" in data

    def test_health_status_ok(self, client):
        response = client.get("/healthz")
        data = response.json()
        assert data["status"] == "ok"

    def test_health_content_type(self, client):
        response = client.get("/healthz")
        assert "application/json" in response.headers["content-type"]
