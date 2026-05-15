"""Eval smoke test: load a JSONL manifest and compute CER end-to-end."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from src.eval.cer import compute_cer, aggregate_cer
from src.eval.cer_runner import load_manifest, run


SAMPLE_MANIFEST = [
    {"id": "ko_001", "reference": "안녕하세요 반갑습니다", "hypothesis": "안녕하세요 반갑습니다"},
    {"id": "ko_002", "reference": "이것은 테스트입니다", "hypothesis": "이것은 테스트"},
    {"id": "ko_003", "reference": "한국어 음성인식", "hypothesis": ""},
    {"id": "en_001", "reference": "hello world", "hypothesis": "hello world"},
    {"id": "en_002", "reference": "the quick brown fox", "hypothesis": "the quick brown fox"},
]


@pytest.fixture
def manifest_path(tmp_path: Path) -> Path:
    p = tmp_path / "manifest.jsonl"
    with open(p, "w", encoding="utf-8") as f:
        for rec in SAMPLE_MANIFEST:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return p


def test_load_manifest(manifest_path: Path):
    records = load_manifest(manifest_path)
    assert len(records) == len(SAMPLE_MANIFEST)
    assert records[0]["id"] == "ko_001"


def test_run_produces_valid_report(manifest_path: Path):
    report = run(manifest_path)
    agg = report["aggregate"]
    assert agg["num_samples"] == len(SAMPLE_MANIFEST)
    assert "micro_cer" in agg
    assert "macro_cer" in agg
    assert isinstance(agg["micro_cer"], float)
    assert 0.0 <= agg["micro_cer"] <= 2.0  # sanity: not absurdly large


def test_perfect_samples_have_zero_cer(manifest_path: Path):
    report = run(manifest_path)
    perfect_ids = {"ko_001", "en_001", "en_002"}
    for s in report["samples"]:
        if s["id"] in perfect_ids:
            assert s["cer"] == 0.0, f"Expected 0 CER for {s['id']}, got {s['cer']}"


def test_empty_hypothesis_gives_max_cer():
    r = compute_cer("한국어 음성인식", "", "ko_003")
    assert r.cer == 1.0


def test_partial_error_in_range():
    r = compute_cer("이것은 테스트입니다", "이것은 테스트", "ko_002")
    assert 0.0 < r.cer < 1.0


def test_output_file_written(manifest_path: Path, tmp_path: Path):
    out = tmp_path / "report.json"
    run(manifest_path, output_path=out)
    assert out.exists()
    data = json.loads(out.read_text("utf-8"))
    assert "aggregate" in data
    assert "samples" in data


def test_manifest_with_blank_lines(tmp_path: Path):
    p = tmp_path / "sparse.jsonl"
    with open(p, "w", encoding="utf-8") as f:
        f.write('{"id": "x", "reference": "a", "hypothesis": "a"}\n')
        f.write("\n")
        f.write('{"id": "y", "reference": "b", "hypothesis": "b"}\n')
    records = load_manifest(p)
    assert len(records) == 2
