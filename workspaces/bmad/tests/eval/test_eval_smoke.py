"""Eval smoke tests.

BMAD QA: Verifies the CLI runner works end-to-end with the fixture manifest.
Tests run without GPU or network.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

MANIFEST_PATH = Path(__file__).parent.parent / "fixtures" / "manifest.jsonl"
PROJECT_ROOT = Path(__file__).parent.parent.parent


class TestCERRunnerCLI:
    """Test `python -m src.eval.cer_runner` CLI."""

    def test_cli_runs_without_error(self):
        result = subprocess.run(
            [sys.executable, "-m", "src.eval.cer_runner", "--manifest", str(MANIFEST_PATH)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"CLI exited with {result.returncode}:\n{result.stderr}"

    def test_cli_outputs_jsonl(self):
        result = subprocess.run(
            [sys.executable, "-m", "src.eval.cer_runner", "--manifest", str(MANIFEST_PATH)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
        assert len(lines) > 0, "CLI produced no output"
        for line in lines:
            obj = json.loads(line)  # Each line must be valid JSON
            assert isinstance(obj, dict)

    def test_cli_outputs_aggregate(self):
        result = subprocess.run(
            [sys.executable, "-m", "src.eval.cer_runner", "--manifest", str(MANIFEST_PATH)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
        # Last line should be the aggregate
        last = json.loads(lines[-1])
        assert "aggregate" in last
        agg = last["aggregate"]
        assert "mean_cer" in agg
        assert "total_samples" in agg
        assert agg["total_samples"] == 5  # manifest has 5 entries

    def test_cli_per_sample_has_cer_field(self):
        result = subprocess.run(
            [sys.executable, "-m", "src.eval.cer_runner", "--manifest", str(MANIFEST_PATH)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
        # All lines except last should be sample results
        for line in lines[:-1]:
            obj = json.loads(line)
            assert "id" in obj
            assert "cer" in obj
            assert isinstance(obj["cer"], (int, float))

    def test_cli_perfect_match_cer_zero(self):
        """sample_001 has identical ref/hyp → CER should be 0."""
        result = subprocess.run(
            [sys.executable, "-m", "src.eval.cer_runner", "--manifest", str(MANIFEST_PATH)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
        sample_results = [json.loads(l) for l in lines[:-1]]
        s1 = next((r for r in sample_results if r.get("id") == "sample_001"), None)
        assert s1 is not None
        assert s1["cer"] == pytest.approx(0.0)

    def test_cli_empty_hypothesis_high_cer(self):
        """sample_004 has empty hypothesis → CER should be ~1.0."""
        result = subprocess.run(
            [sys.executable, "-m", "src.eval.cer_runner", "--manifest", str(MANIFEST_PATH)],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        lines = [l.strip() for l in result.stdout.strip().splitlines() if l.strip()]
        sample_results = [json.loads(l) for l in lines[:-1]]
        s4 = next((r for r in sample_results if r.get("id") == "sample_004"), None)
        assert s4 is not None
        assert s4["cer"] == pytest.approx(1.0)

    def test_cli_output_file(self, tmp_path):
        """--output flag writes JSONL file."""
        output_file = tmp_path / "results.jsonl"
        result = subprocess.run(
            [
                sys.executable, "-m", "src.eval.cer_runner",
                "--manifest", str(MANIFEST_PATH),
                "--output", str(output_file),
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0
        assert output_file.exists()
        lines = output_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) > 0
        for line in lines:
            json.loads(line)  # Must be valid JSON


class TestCERRunnerModule:
    """Test the run() function directly."""

    def test_run_returns_dict(self):
        from src.eval.cer_runner import run
        output = run(str(MANIFEST_PATH))
        assert "results" in output
        assert "aggregate" in output

    def test_run_total_samples(self):
        from src.eval.cer_runner import run
        output = run(str(MANIFEST_PATH))
        assert output["aggregate"]["total_samples"] == 5

    def test_run_mean_cer_range(self):
        from src.eval.cer_runner import run
        output = run(str(MANIFEST_PATH))
        assert 0.0 <= output["aggregate"]["mean_cer"] <= 1.0
