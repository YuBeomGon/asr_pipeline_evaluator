from __future__ import annotations
"""
Eval smoke tests: CER runner with a JSONL manifest.
Tests that the CLI entry point processes manifests correctly.
"""
import json
import tempfile
from pathlib import Path

import pytest

from src.eval.cer_runner import load_manifest, run


def write_manifest(records: list[dict], tmp_path: Path) -> Path:
    manifest = tmp_path / "manifest.jsonl"
    with open(manifest, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    return manifest


class TestCERRunner:
    def test_load_manifest_basic(self, tmp_path):
        records = [
            {"id": "s1", "reference": "hello", "hypothesis": "hello"},
        ]
        manifest = write_manifest(records, tmp_path)
        loaded = load_manifest(manifest)
        assert len(loaded) == 1
        assert loaded[0]["id"] == "s1"

    def test_load_manifest_missing_hypothesis_defaults_empty(self, tmp_path):
        records = [
            {"id": "s1", "reference": "hello"},  # no hypothesis
        ]
        manifest = write_manifest(records, tmp_path)
        loaded = load_manifest(manifest)
        assert loaded[0]["hypothesis"] == ""

    def test_run_perfect_match(self, tmp_path):
        records = [
            {"id": "s1", "reference": "hello", "hypothesis": "hello"},
        ]
        manifest = write_manifest(records, tmp_path)
        results = run(manifest)
        assert results["aggregate"]["mean_cer"] == pytest.approx(0.0)
        assert results["aggregate"]["total_samples"] == 1

    def test_run_korean_manifest(self, tmp_path):
        records = [
            {
                "id": "kr_1",
                "reference": "안녕하세요",
                "hypothesis": "안녕하세요",
            },
            {
                "id": "kr_2",
                "reference": "오늘 날씨가 좋네요",
                "hypothesis": "오늘 날씨가 좋아요",
            },
        ]
        manifest = write_manifest(records, tmp_path)
        results = run(manifest)
        assert results["aggregate"]["total_samples"] == 2
        # kr_1: CER=0.0, kr_2: CER=1/8
        assert results["results"][0]["cer"] == pytest.approx(0.0)
        assert results["results"][1]["cer"] == pytest.approx(1 / 8)

    def test_run_writes_output_file(self, tmp_path):
        records = [
            {"id": "s1", "reference": "abc", "hypothesis": "axc"},
        ]
        manifest = write_manifest(records, tmp_path)
        output = tmp_path / "out.json"
        run(manifest, output_path=output)
        assert output.exists()
        data = json.loads(output.read_text(encoding="utf-8"))
        assert "results" in data
        assert "aggregate" in data

    def test_run_empty_hypothesis(self, tmp_path):
        records = [
            {"id": "s1", "reference": "hello", "hypothesis": ""},
        ]
        manifest = write_manifest(records, tmp_path)
        results = run(manifest)
        assert results["results"][0]["cer"] == pytest.approx(1.0)

    def test_run_audio_field_is_optional(self, tmp_path):
        # The 'audio' field is listed in the spec but should be optional
        records = [
            {
                "id": "s1",
                "audio": "audio/sample_001.wav",
                "reference": "hello",
                "hypothesis": "hello",
            },
        ]
        manifest = write_manifest(records, tmp_path)
        results = run(manifest)
        assert results["aggregate"]["total_samples"] == 1
