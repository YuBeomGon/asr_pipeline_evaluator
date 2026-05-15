from __future__ import annotations
"""Integration tests for POST /eval/cer."""
import pytest


class TestEvalCEREndpoint:
    def test_eval_cer_returns_200(self, client):
        payload = {
            "pairs": [
                {"id": "s1", "reference": "hello", "hypothesis": "hello"},
            ]
        }
        response = client.post("/eval/cer", json=payload)
        assert response.status_code == 200

    def test_perfect_match_cer_zero(self, client):
        payload = {
            "pairs": [
                {"id": "s1", "reference": "hello", "hypothesis": "hello"},
            ]
        }
        response = client.post("/eval/cer", json=payload)
        data = response.json()
        assert data["results"][0]["cer"] == pytest.approx(0.0)

    def test_response_schema(self, client):
        payload = {
            "pairs": [
                {"id": "s1", "reference": "hello", "hypothesis": "helo"},
            ]
        }
        response = client.post("/eval/cer", json=payload)
        data = response.json()
        assert "results" in data
        assert "aggregate" in data

        result = data["results"][0]
        for key in ["id", "reference", "hypothesis", "cer", "substitutions", "deletions", "insertions", "reference_length"]:
            assert key in result

        agg = data["aggregate"]
        for key in ["mean_cer", "total_substitutions", "total_deletions", "total_insertions", "total_reference_length", "total_samples"]:
            assert key in agg

    def test_korean_eval(self, client):
        payload = {
            "pairs": [
                {
                    "id": "kr_1",
                    "reference": "안녕하세요 반갑습니다",
                    "hypothesis": "안녕하세요 반갑습니다",
                },
            ]
        }
        response = client.post("/eval/cer", json=payload)
        data = response.json()
        assert data["results"][0]["cer"] == pytest.approx(0.0)

    def test_multiple_pairs_aggregate(self, client):
        payload = {
            "pairs": [
                {"id": "s1", "reference": "abc", "hypothesis": "abc"},
                {"id": "s2", "reference": "abc", "hypothesis": "axc"},
            ]
        }
        response = client.post("/eval/cer", json=payload)
        data = response.json()
        assert data["aggregate"]["total_samples"] == 2
        assert data["aggregate"]["mean_cer"] == pytest.approx(1 / 6)

    def test_empty_pairs_returns_422(self, client):
        response = client.post("/eval/cer", json={"pairs": []})
        assert response.status_code == 422

    def test_missing_pairs_field_returns_422(self, client):
        response = client.post("/eval/cer", json={})
        assert response.status_code == 422

    def test_normalization_case_insensitive(self, client):
        payload = {
            "pairs": [
                {"id": "s1", "reference": "Hello", "hypothesis": "hello"},
            ]
        }
        response = client.post("/eval/cer", json=payload)
        data = response.json()
        assert data["results"][0]["cer"] == pytest.approx(0.0)
