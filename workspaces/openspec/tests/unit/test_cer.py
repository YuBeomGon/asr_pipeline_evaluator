from __future__ import annotations
"""
Unit tests for CER evaluator and normalization.
Tests cover: normalization pipeline, Levenshtein correctness,
CER calculation, edge cases, Korean text.
"""
import pytest

from src.eval.cer import CEREvaluator, normalize_for_cer


# --- Normalization tests ---

class TestNormalizeForCER:
    def test_nfkc_normalization(self):
        # Half-width characters should be normalized to full-width ASCII
        text = "ｈｅｌｌｏ"  # fullwidth hello
        assert normalize_for_cer(text) == "hello"

    def test_lowercase(self):
        assert normalize_for_cer("Hello World") == "helloworld"

    def test_strip_whitespace(self):
        assert normalize_for_cer("  hello  ") == "hello"

    def test_collapse_internal_whitespace(self):
        assert normalize_for_cer("hello   world") == "helloworld"

    def test_remove_spaces(self):
        assert normalize_for_cer("a b c") == "abc"

    def test_korean_no_change(self):
        # Korean characters should pass through unchanged (already NFC/NFKC)
        result = normalize_for_cer("안녕하세요")  # annyeonghaseyo
        assert result == "안녕하세요"

    def test_korean_with_spaces(self):
        # Spaces between Korean words should be removed
        result = normalize_for_cer("안녕하세요 반갑습니다")
        assert result == "안녕하세요반갑습니다"

    def test_empty_string(self):
        assert normalize_for_cer("") == ""

    def test_only_spaces(self):
        assert normalize_for_cer("   ") == ""

    def test_mixed_korean_english(self):
        result = normalize_for_cer("Hello 안녕")
        assert result == "hello안녕"

    def test_precomposed_korean(self):
        # Standard precomposed Korean syllable block passes through NFKC unchanged
        # U+C544 = 아 (ah)
        text = "아"
        result = normalize_for_cer(text)
        assert result == "아"

    def test_nfkc_composed_hangul(self):
        # Standard Korean text round-trips through NFKC correctly
        text = "안녕하세요"  # 안녕하세요
        result = normalize_for_cer(text)
        assert result == "안녕하세요"


# --- CER evaluator tests ---

class TestCEREvaluator:
    def setup_method(self):
        self.evaluator = CEREvaluator()

    # Perfect match
    def test_perfect_match(self):
        result = self.evaluator.evaluate_pair("t1", "hello", "hello")
        assert result.cer == pytest.approx(0.0)
        assert result.substitutions == 0
        assert result.deletions == 0
        assert result.insertions == 0

    # Perfect match Korean
    def test_perfect_match_korean(self):
        result = self.evaluator.evaluate_pair(
            "t1",
            "안녕하세요",
            "안녕하세요",
        )
        assert result.cer == pytest.approx(0.0)
        assert result.reference_length == 5

    # Single substitution
    def test_single_substitution(self):
        # "abc" vs "axc" => 1 substitution, ref_len=3, CER = 1/3
        result = self.evaluator.evaluate_pair("t1", "abc", "axc")
        assert result.substitutions == 1
        assert result.cer == pytest.approx(1 / 3)

    # Single deletion (char in ref missing from hyp)
    def test_single_deletion(self):
        # ref="abc", hyp="ac" => 1 deletion
        result = self.evaluator.evaluate_pair("t1", "abc", "ac")
        assert result.deletions == 1
        assert result.cer == pytest.approx(1 / 3)

    # Single insertion (extra char in hyp)
    def test_single_insertion(self):
        # ref="ac", hyp="abc" => 1 insertion, ref_len=2, CER = 1/2
        result = self.evaluator.evaluate_pair("t1", "ac", "abc")
        assert result.insertions == 1
        assert result.cer == pytest.approx(1 / 2)

    # Empty hypothesis
    def test_empty_hypothesis(self):
        result = self.evaluator.evaluate_pair("t1", "hello", "")
        assert result.cer == pytest.approx(1.0)
        assert result.deletions == 5

    # Empty reference
    def test_empty_reference(self):
        result = self.evaluator.evaluate_pair("t1", "", "")
        assert result.cer == pytest.approx(0.0)

    def test_empty_reference_nonempty_hypothesis(self):
        result = self.evaluator.evaluate_pair("t1", "", "hello")
        assert result.cer == pytest.approx(1.0)

    # Normalization applied in evaluate_pair
    def test_normalization_applied(self):
        # Spaces are removed before scoring
        result = self.evaluator.evaluate_pair("t1", "hello world", "hello world")
        assert result.cer == pytest.approx(0.0)
        assert result.reference == "helloworld"

    def test_case_insensitive(self):
        result = self.evaluator.evaluate_pair("t1", "Hello", "hello")
        assert result.cer == pytest.approx(0.0)

    # Korean CER with error
    def test_korean_cer_with_error(self):
        # ref="오늘날씨가좋네요" (8 chars after space removal)
        # hyp="오늘날씨가좋아요" — 네->아: 1 substitution
        result = self.evaluator.evaluate_pair(
            "t1",
            "오늘 날씨가 좋네요",
            "오늘 날씨가 좋아요",
        )
        assert result.reference_length == 8
        assert result.cer == pytest.approx(1 / 8)

    # Batch evaluation
    def test_batch_evaluation(self):
        pairs = [
            {"id": "s1", "reference": "abc", "hypothesis": "abc"},
            {"id": "s2", "reference": "abc", "hypothesis": "axc"},
        ]
        agg = self.evaluator.evaluate_batch(pairs)
        assert agg.total_samples == 2
        assert agg.per_sample[0].cer == pytest.approx(0.0)
        assert agg.per_sample[1].cer == pytest.approx(1 / 3)
        assert agg.mean_cer == pytest.approx((0.0 + 1 / 3) / 2)

    def test_batch_aggregate_totals(self):
        pairs = [
            {"id": "s1", "reference": "abc", "hypothesis": "axc"},  # 1 sub
            {"id": "s2", "reference": "abc", "hypothesis": "ab"},   # 1 del
        ]
        agg = self.evaluator.evaluate_batch(pairs)
        assert agg.total_substitutions == 1
        assert agg.total_deletions == 1
        assert agg.total_insertions == 0
        assert agg.total_reference_length == 6


# --- Postprocessing tests ---

class TestPostprocessing:
    def test_nfc_normalization(self):
        from src.api.postprocessing import postprocess_transcript
        # Already NFC Korean should pass through unchanged
        text = "안녕하세요"  # 안녕하세요
        assert postprocess_transcript(text) == "안녕하세요"

    def test_strip_whitespace(self):
        from src.api.postprocessing import postprocess_transcript
        assert postprocess_transcript("  hello  ") == "hello"

    def test_collapse_whitespace(self):
        from src.api.postprocessing import postprocess_transcript
        assert postprocess_transcript("hello   world") == "hello world"

    def test_punctuation_cleanup(self):
        from src.api.postprocessing import postprocess_transcript
        assert postprocess_transcript("안녕 .") == "안녕."

    def test_empty_string(self):
        from src.api.postprocessing import postprocess_transcript
        assert postprocess_transcript("") == ""
