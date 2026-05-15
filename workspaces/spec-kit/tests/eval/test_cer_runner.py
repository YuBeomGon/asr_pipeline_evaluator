"""
Eval smoke tests: CER CLI runner with JSONL manifest.

Spec ref: .specify/asr-pipeline-spec.md § FR-012, FR-013, SC-005
  - python -m src.eval.cer_runner --manifest <path> exits 0
  - prints overall_cer to stdout
"""

import json
import sys
from pathlib import Path

import pytest

from src.eval.cer_runner import main, load_manifest


SAMPLE_MANIFEST_CONTENT = """\
{"id":"s001","audio":"audio/s001.wav","reference":"안녕하세요","hypothesis":"안녕하세요"}
{"id":"s002","audio":"audio/s002.wav","reference":"반갑습니다","hypothesis":"반갑습니다"}
{"id":"s003","audio":"audio/s003.wav","reference":"hello world","hypothesis":"hello world"}
"""

PARTIAL_MATCH_MANIFEST = """\
{"id":"s001","reference":"안녕하세요","hypothesis":"안녕하세요"}
{"id":"s002","reference":"abcdef","hypothesis":"abc"}
"""

EMPTY_REF_MANIFEST = """\
{"id":"s001","reference":"","hypothesis":"hello"}
{"id":"s002","reference":"hello","hypothesis":"hello"}
"""


@pytest.fixture
def sample_manifest(tmp_path: Path) -> Path:
    manifest = tmp_path / "manifest.jsonl"
    manifest.write_text(SAMPLE_MANIFEST_CONTENT, encoding="utf-8")
    return manifest


@pytest.fixture
def partial_manifest(tmp_path: Path) -> Path:
    manifest = tmp_path / "partial.jsonl"
    manifest.write_text(PARTIAL_MATCH_MANIFEST, encoding="utf-8")
    return manifest


@pytest.fixture
def empty_ref_manifest(tmp_path: Path) -> Path:
    manifest = tmp_path / "empty_ref.jsonl"
    manifest.write_text(EMPTY_REF_MANIFEST, encoding="utf-8")
    return manifest


class TestCERRunnerCLI:
    def test_exits_zero_on_perfect_manifest(self, sample_manifest: Path, capsys):
        """Spec ref: SC-005"""
        exit_code = main(["--manifest", str(sample_manifest)])
        assert exit_code == 0

    def test_prints_overall_cer(self, sample_manifest: Path, capsys):
        """Spec ref: SC-005 — must print overall_cer"""
        main(["--manifest", str(sample_manifest)])
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        assert "overall_cer" in output
        assert output["overall_cer"] == pytest.approx(0.0)

    def test_missing_manifest_exits_nonzero(self, tmp_path: Path, capsys):
        missing = tmp_path / "does_not_exist.jsonl"
        with pytest.raises(SystemExit) as exc_info:
            main(["--manifest", str(missing)])
        assert exc_info.value.code != 0

    def test_partial_match_cer(self, partial_manifest: Path, capsys):
        main(["--manifest", str(partial_manifest)])
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        # s001: 0 edits, 5 chars; s002: 3 edits, 6 chars → overall = 3/11
        assert output["overall_cer"] == pytest.approx(3 / 11)

    def test_empty_reference_excluded_from_aggregate(self, empty_ref_manifest: Path, capsys):
        """Spec ref: FR-010 — empty ref excluded from aggregate"""
        main(["--manifest", str(empty_ref_manifest)])
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        # Only s002 counts: 5 chars, 0 edits
        assert output["overall_cer"] == pytest.approx(0.0)
        assert output["total_reference_chars"] == 5

    def test_output_json_structure(self, sample_manifest: Path, capsys):
        main(["--manifest", str(sample_manifest)])
        captured = capsys.readouterr()
        output = json.loads(captured.out)
        required_keys = {
            "overall_cer", "total_reference_chars", "total_edits",
            "num_samples", "num_scored", "pairs",
        }
        assert required_keys.issubset(output.keys())

    def test_output_file(self, sample_manifest: Path, tmp_path: Path, capsys):
        out_file = tmp_path / "results.json"
        exit_code = main(["--manifest", str(sample_manifest), "--output", str(out_file)])
        assert exit_code == 0
        assert out_file.exists()
        output = json.loads(out_file.read_text(encoding="utf-8"))
        assert "overall_cer" in output


class TestLoadManifest:
    def test_loads_valid_jsonl(self, sample_manifest: Path):
        pairs = load_manifest(sample_manifest)
        assert len(pairs) == 3
        assert pairs[0]["id"] == "s001"

    def test_skips_empty_lines(self, tmp_path: Path):
        manifest = tmp_path / "m.jsonl"
        manifest.write_text(
            '{"id":"s1","reference":"hi","hypothesis":"hi"}\n\n{"id":"s2","reference":"bye","hypothesis":"bye"}\n',
            encoding="utf-8",
        )
        pairs = load_manifest(manifest)
        assert len(pairs) == 2

    def test_missing_hypothesis_defaults_to_empty(self, tmp_path: Path):
        manifest = tmp_path / "m.jsonl"
        manifest.write_text('{"id":"s1","reference":"hello"}\n', encoding="utf-8")
        pairs = load_manifest(manifest)
        assert pairs[0]["hypothesis"] == ""
