from __future__ import annotations
"""Integration tests for GET /healthz."""
import pytest


@pytest.mark.asyncio
async def test_healthz_returns_200(client):
    response = await client.get("/healthz")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_healthz_returns_ok_status(client):
    response = await client.get("/healthz")
    body = response.json()
    assert body == {"status": "ok"}


@pytest.mark.asyncio
async def test_healthz_content_type_json(client):
    response = await client.get("/healthz")
    assert "application/json" in response.headers["content-type"]
