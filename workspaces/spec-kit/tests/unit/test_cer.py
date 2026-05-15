"""
Unit tests for CER evaluation logic.

Spec ref: .specify/asr-pipeline-spec.md § FR-010, FR-011, SC-004
  - CER = (S + D + I) / N
  - NFKC normalization, lowercase, whitespace collapsing, space removal
"""

import pytest
from src.eval.cer import normalize_for_cer, compute_cer_sample, compute_cer_batch


# ── normalize_for_cer ────────────────────────────────────────────────────────

class TestNormalizeForCER:
    def test_lowercase(self):
        assert normalize_for_cer("Hello World") == "helloworld"

    def test_strip_whitespace(self):
        assert normalize_for_cer("  hello  ") == "hello"

    def test_collapse_internal_whitespace(self):
        assert normalize_for_cer("hello   world") == "helloworld"

    def test_remove_spaces(self):
        # Spaces are removed for character-level alignment
        assert normalize_for_cer("a b c") == "abc"

    def test_nfkc_normalization(self):
        # Full-width ASCII → ASCII
        assert normalize_for_cer("Ａ") == "a"

    def test_korean_nfc(self):
        # Korean text passes through unchanged (already in NFC/NFKC)
        text = "안녕하세요"
        result = normalize_for_cer(text)
        assert result == "안녕하세요"

    def test_empty_string(self):
        assert normalize_for_cer("") == ""

    def test_whitespace_only(self):
        assert normalize_for_cer("   ") == ""

    def test_mixed_korean_ascii(self):
        result = normalize_for_cer("한국어 ABC 123")
        # spaces removed, lowercase
        assert result == "한국어abc123"


# ── compute_cer_sample ───────────────────────────────────────────────────────

class TestComputeCERSample:
    def test_perfect_match_ascii(self):
        result = compute_cer_sample("s1", "hello", "hello")
        assert result.cer == pytest.approx(0.0)
        assert result.edits == 0
        assert result.reference_chars == 5

    def test_perfect_match_korean(self):
        result = compute_cer_sample("s1", "안녕하세요", "안녕하세요")
        assert result.cer == pytest.approx(0.0)

    def test_completely_wrong(self):
        result = compute_cer_sample("s1", "abc", "xyz")
        assert result.edits == 3
        assert result.cer == pytest.approx(1.0)

    def test_empty_hypothesis(self):
        # All deletions → CER = 1.0 (reference_chars / reference_chars)
        result = compute_cer_sample("s1", "hello", "")
        assert result.cer == pytest.approx(1.0)
        assert result.edits == 5

    def test_empty_reference(self):
        # Undefined → cer is None
        result = compute_cer_sample("s1", "", "hello")
        assert result.cer is None
        assert result.reference_chars == 0

    def test_empty_both(self):
        result = compute_cer_sample("s1", "", "")
        assert result.cer is None

    def test_cer_can_exceed_one(self):
        # Many insertions relative to a very short reference
        result = compute_cer_sample("s1", "a", "abcde")
        assert result.cer == pytest.approx(4.0)

    def test_whitespace_in_reference(self):
        # Spaces are removed before comparison
        result = compute_cer_sample("s1", "a b c", "abc")
        assert result.cer == pytest.approx(0.0)

    def test_case_insensitive(self):
        result = compute_cer_sample("s1", "Hello", "hello")
        assert result.cer == pytest.approx(0.0)

    def test_partial_match_korean(self):
        # "안녕하세요" vs "안녕" → 3 deletions out of 5 chars
        result = compute_cer_sample("s1", "안녕하세요", "안녕")
        assert result.edits == 3
        assert result.cer == pytest.approx(3 / 5)


# ── compute_cer_batch ────────────────────────────────────────────────────────

class TestComputeCERBatch:
    def test_single_perfect(self):
        pairs = [{"id": "s1", "reference": "hello", "hypothesis": "hello"}]
        result = compute_cer_batch(pairs)
        assert result.overall_cer == pytest.approx(0.0)
        assert result.total_reference_chars == 5
        assert result.total_edits == 0

    def test_aggregate_excludes_empty_refs(self):
        pairs = [
            {"id": "s1", "reference": "hello", "hypothesis": "hello"},
            {"id": "s2", "reference": "",      "hypothesis": "hi"},   # excluded
        ]
        result = compute_cer_batch(pairs)
        assert result.overall_cer == pytest.approx(0.0)
        assert result.total_reference_chars == 5

    def test_aggregate_cer(self):
        # s1: ref="abc" (3 chars), hyp="abc" → 0 edits
        # s2: ref="xyz" (3 chars), hyp=""   → 3 edits
        # overall = 3 / 6 = 0.5
        pairs = [
            {"id": "s1", "reference": "abc", "hypothesis": "abc"},
            {"id": "s2", "reference": "xyz", "hypothesis": ""},
        ]
        result = compute_cer_batch(pairs)
        assert result.total_reference_chars == 6
        assert result.total_edits == 3
        assert result.overall_cer == pytest.approx(0.5)

    def test_empty_batch(self):
        result = compute_cer_batch([{"id": "s1", "reference": "", "hypothesis": ""}])
        assert result.overall_cer == 0.0
        assert result.total_reference_chars == 0
