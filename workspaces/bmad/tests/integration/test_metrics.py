from __future__ import annotations
"""Integration tests for GET /metrics and POST /eval/cer."""
import pytest


@pytest.mark.asyncio
async def test_metrics_returns_200(client):
    response = await client.get("/metrics")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_metrics_content_type(client):
    response = await client.get("/metrics")
    content_type = response.headers.get("content-type", "")
    assert "text/plain" in content_type


@pytest.mark.asyncio
async def test_metrics_contains_required_metrics(client):
    response = await client.get("/metrics")
    body = response.text

    assert "asr_requests_total" in body
    assert "asr_request_duration_seconds" in body
    assert "asr_errors_total" in body


@pytest.mark.asyncio
async def test_eval_cer_perfect_match(client):
    response = await client.post(
        "/eval/cer",
        json={
            "pairs": [
                {
                    "id": "s1",
                    "reference": "안녕하세요",
                    "hypothesis": "안녕하세요",
                }
            ]
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["results"][0]["cer"] == pytest.approx(0.0)
    assert body["aggregate"]["mean_cer"] == pytest.approx(0.0)


@pytest.mark.asyncio
async def test_eval_cer_empty_hypothesis(client):
    response = await client.post(
        "/eval/cer",
        json={
            "pairs": [
                {
                    "id": "s1",
                    "reference": "테스트",
                    "hypothesis": "",
                }
            ]
        },
    )
    assert response.status_code == 200
    body = response.json()
    # All chars deleted → CER = 1.0
    assert body["results"][0]["cer"] == pytest.approx(1.0)


@pytest.mark.asyncio
async def test_eval_cer_response_schema(client):
    response = await client.post(
        "/eval/cer",
        json={
            "pairs": [
                {"id": "s1", "reference": "한국어", "hypothesis": "한국어"},
                {"id": "s2", "reference": "테스트", "hypothesis": "텍스트"},
            ]
        },
    )
    assert response.status_code == 200
    body = response.json()

    assert "results" in body
    assert "aggregate" in body
    assert len(body["results"]) == 2

    for result in body["results"]:
        assert "id" in result
        assert "reference" in result
        assert "hypothesis" in result
        assert "cer" in result
        assert "substitutions" in result
        assert "deletions" in result
        assert "insertions" in result
        assert "reference_length" in result

    agg = body["aggregate"]
    assert "mean_cer" in agg
    assert "total_samples" in agg
    assert "total_reference_chars" in agg
    assert "total_errors" in agg
    assert agg["total_samples"] == 2


@pytest.mark.asyncio
async def test_eval_cer_batch_aggregate(client):
    response = await client.post(
        "/eval/cer",
        json={
            "pairs": [
                {"id": "s1", "reference": "안녕", "hypothesis": "안녕"},   # CER=0
                {"id": "s2", "reference": "테스트", "hypothesis": "텍스트"}, # CER≈0.333
            ]
        },
    )
    body = response.json()
    expected_mean = (0.0 + 1 / 3) / 2
    assert body["aggregate"]["mean_cer"] == pytest.approx(expected_mean, abs=1e-4)


@pytest.mark.asyncio
async def test_eval_cer_empty_pairs_returns_422(client):
    response = await client.post(
        "/eval/cer",
        json={"pairs": []},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_eval_cer_reference_length_excludes_spaces(client):
    """reference_length should count chars after normalization (no spaces)."""
    response = await client.post(
        "/eval/cer",
        json={
            "pairs": [
                {
                    "id": "s1",
                    "reference": "안녕 하세요",  # 5 chars after space removal
                    "hypothesis": "안녕하세요",
                }
            ]
        },
    )
    body = response.json()
    assert body["results"][0]["reference_length"] == 5
    assert body["results"][0]["cer"] == pytest.approx(0.0)
