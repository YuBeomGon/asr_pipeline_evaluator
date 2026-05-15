"""Unit tests for CER computation."""
from __future__ import annotations

import pytest

from src.eval.cer import compute_cer, aggregate_cer, CERResult


class TestComputeCER:
    def test_perfect_match(self):
        r = compute_cer("안녕하세요", "안녕하세요", "s1")
        assert r.cer == 0.0
        assert r.edit_distance == 0

    def test_complete_miss(self):
        r = compute_cer("abc", "xyz", "s2")
        assert r.cer == 1.0
        assert r.edit_distance == 3

    def test_empty_reference_empty_hypothesis(self):
        r = compute_cer("", "", "s3")
        assert r.cer == 0.0

    def test_empty_reference_nonempty_hypothesis(self):
        r = compute_cer("", "hello", "s4")
        assert r.cer == 1.0

    def test_nonempty_reference_empty_hypothesis(self):
        r = compute_cer("hello", "", "s5")
        assert r.cer == 1.0

    def test_single_substitution(self):
        # "abc" vs "aXc" → 1 substitution / 3 ref chars
        r = compute_cer("abc", "aXc", "s6")
        assert r.edit_distance == 1
        assert abs(r.cer - 1 / 3) < 1e-9

    def test_normalization_applied(self):
        # Extra spaces should be collapsed; case-folded
        r = compute_cer("Hello World", "hello world", "s7")
        assert r.cer == 0.0

    def test_korean_perfect(self):
        ref = "이것은 테스트입니다"
        hyp = "이것은 테스트입니다"
        r = compute_cer(ref, hyp, "s8")
        assert r.cer == 0.0

    def test_korean_partial_error(self):
        ref = "안녕하세요"
        hyp = "안녕"
        r = compute_cer(ref, hyp, "s9")
        # After normalization ref="안녕하세요" (5 chars), hyp="안녕" (2 chars)
        assert r.reference_length == 5
        assert r.cer > 0.0

    def test_cer_can_exceed_one(self):
        # Many insertions: hypothesis much longer than reference
        r = compute_cer("a", "abcdefghij", "s10")
        assert r.cer > 1.0

    def test_sample_id_preserved(self):
        r = compute_cer("x", "x", "my-id")
        assert r.id == "my-id"


class TestAggregateCER:
    def _results(self, *pairs):
        return [compute_cer(ref, hyp, f"s{i}") for i, (ref, hyp) in enumerate(pairs)]

    def test_empty(self):
        agg = aggregate_cer([])
        assert agg.num_samples == 0
        assert agg.macro_cer == 0.0
        assert agg.micro_cer == 0.0

    def test_single_perfect(self):
        results = self._results(("hello", "hello"))
        agg = aggregate_cer(results)
        assert agg.num_samples == 1
        assert agg.macro_cer == 0.0
        assert agg.micro_cer == 0.0

    def test_macro_vs_micro(self):
        # Two samples: "a" vs "b" (CER=1.0, len=1) and "aaaaa" vs "aaaaa" (CER=0.0, len=5)
        results = self._results(("a", "b"), ("aaaaa", "aaaaa"))
        agg = aggregate_cer(results)
        # macro = (1.0 + 0.0) / 2 = 0.5
        assert abs(agg.macro_cer - 0.5) < 1e-9
        # micro = 1 / (1 + 5) = 1/6
        assert abs(agg.micro_cer - 1 / 6) < 1e-9
