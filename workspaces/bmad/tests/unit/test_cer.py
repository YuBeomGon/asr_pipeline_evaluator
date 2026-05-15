from __future__ import annotations
"""Unit tests for CER calculation.

BMAD QA: Tests verify formula correctness, edge cases, and Korean text handling.
No network or GPU required.
"""
import pytest

from src.eval.cer import (
    CERCalculator,
    levenshtein_distance,
    normalize_text,
)


# ─────────────────────────────── normalize_text ─────────────────────────────

class TestNormalizeText:
    def test_identical_strings_after_normalization(self):
        assert normalize_text("안녕하세요") == normalize_text("안녕하세요")

    def test_removes_spaces(self):
        result = normalize_text("안녕 하세요")
        assert " " not in result

    def test_lowercases(self):
        assert normalize_text("HELLO") == "hello"

    def test_nfkc_full_width_to_ascii(self):
        # Full-width A (U+FF21) → ASCII A → lowercase a
        assert normalize_text("Ａ") == "a"

    def test_collapses_multiple_spaces(self):
        # Multiple spaces collapse before removal
        result = normalize_text("hello   world")
        assert result == "helloworld"

    def test_empty_string(self):
        assert normalize_text("") == ""

    def test_korean_nfkc_preserved(self):
        # Korean characters survive NFKC intact
        text = "테스트"
        result = normalize_text(text)
        assert result == "테스트"

    def test_strips_leading_trailing_whitespace(self):
        assert normalize_text("  hello  ") == "hello"

    def test_mixed_korean_latin(self):
        result = normalize_text("Hello 안녕")
        assert result == "hello안녕"


# ─────────────────────────────── levenshtein_distance ───────────────────────

class TestLevenshteinDistance:
    def test_identical_strings(self):
        s, d, i = levenshtein_distance("안녕", "안녕")
        assert s == 0 and d == 0 and i == 0

    def test_empty_ref_empty_hyp(self):
        s, d, i = levenshtein_distance("", "")
        assert s == 0 and d == 0 and i == 0

    def test_empty_ref_nonempty_hyp(self):
        # All insertions
        s, d, i = levenshtein_distance("", "abc")
        assert s == 0 and d == 0 and i == 3

    def test_nonempty_ref_empty_hyp(self):
        # All deletions
        s, d, i = levenshtein_distance("abc", "")
        assert s == 0 and d == 3 and i == 0

    def test_one_substitution(self):
        s, d, i = levenshtein_distance("테스트", "텍스트")
        assert s == 1 and d == 0 and i == 0

    def test_total_edit_distance(self):
        s, d, i = levenshtein_distance("한국어", "한글어")
        assert (s + d + i) == 1


# ─────────────────────────────── CERCalculator ─────────────────────────────

class TestCERCalculator:
    def setup_method(self):
        self.calc = CERCalculator()

    def test_perfect_match_cer_zero(self):
        result = self.calc.compute_pair("s1", "안녕하세요", "안녕하세요")
        assert result.cer == pytest.approx(0.0)
        assert result.substitutions == 0
        assert result.deletions == 0
        assert result.insertions == 0

    def test_empty_hypothesis_cer_one(self):
        result = self.calc.compute_pair("s1", "테스트", "")
        # 3 deletions / 3 chars = 1.0
        assert result.cer == pytest.approx(1.0)
        assert result.deletions == 3

    def test_one_substitution(self):
        # 테스트 (3 chars) → 텍스트 (3 chars): 1 substitution
        result = self.calc.compute_pair("s1", "테스트", "텍스트")
        assert result.cer == pytest.approx(1 / 3)
        assert result.substitutions == 1

    def test_empty_reference_returns_zero(self):
        result = self.calc.compute_pair("s1", "", "텍스트")
        assert result.cer == 0.0
        assert result.reference_length == 0

    def test_space_ignored_in_reference(self):
        # "안녕 하세요" → normalized → "안녕하세요" (5 chars)
        result = self.calc.compute_pair("s1", "안녕 하세요", "안녕하세요")
        assert result.cer == pytest.approx(0.0)
        assert result.reference_length == 5

    def test_batch_aggregate_mean(self):
        pairs = [
            {"id": "s1", "reference": "안녕", "hypothesis": "안녕"},        # CER=0
            {"id": "s2", "reference": "테스트", "hypothesis": "텍스트"},   # CER=1/3
        ]
        results, agg = self.calc.compute_batch(pairs)
        assert len(results) == 2
        assert agg.total_samples == 2
        expected_mean = (0.0 + 1 / 3) / 2
        assert agg.mean_cer == pytest.approx(expected_mean)
        assert agg.total_reference_chars == 2 + 3  # 2 + 3 chars

    def test_batch_empty(self):
        results, agg = self.calc.compute_batch([])
        assert len(results) == 0
        assert agg.mean_cer == 0.0
        assert agg.total_samples == 0

    def test_korean_with_spaces(self):
        # Reference with spaces; hypothesis without — should match after norm
        result = self.calc.compute_pair("s1", "한 국 어", "한국어")
        assert result.cer == pytest.approx(0.0)

    def test_full_width_normalization(self):
        # Full-width characters normalize to ASCII via NFKC
        result = self.calc.compute_pair("s1", "ＡＢＣ", "abc")
        assert result.cer == pytest.approx(0.0)
