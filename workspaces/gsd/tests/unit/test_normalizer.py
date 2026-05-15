"""Unit tests for text normalization."""
from __future__ import annotations

import unicodedata

import pytest

from src.eval.normalizer import normalize_for_cer, normalize_transcript


class TestNormalizeForCER:
    def test_lowercase(self):
        assert normalize_for_cer("Hello") == "hello"

    def test_strips_spaces(self):
        # spaces removed for char-level
        assert normalize_for_cer("hello world") == "helloworld"

    def test_collapses_multiple_spaces(self):
        assert normalize_for_cer("a  b  c") == "abc"

    def test_strips_leading_trailing_whitespace(self):
        assert normalize_for_cer("  hello  ") == "hello"

    def test_nfkc_normalization(self):
        # Fullwidth chars -> ASCII via NFKC
        full = "ｈｅｌｌｏ"  # ｈｅｌｌｏ
        assert normalize_for_cer(full) == "hello"

    def test_nfc_for_korean(self):
        # Korean text should round-trip through NFKC+NFC unchanged
        korean = "안녕하세요"
        result = normalize_for_cer(korean)
        # Result should only contain the Korean chars without spaces
        assert len(result) == 5  # 안녕하세요 = 5 chars

    def test_empty_string(self):
        assert normalize_for_cer("") == ""

    def test_numbers_preserved(self):
        assert normalize_for_cer("123") == "123"

    def test_tab_and_newline_collapsed(self):
        assert normalize_for_cer("a\tb\nc") == "abc"


class TestNormalizeTranscript:
    def test_strips_whitespace(self):
        assert normalize_transcript("  hello  ") == "hello"

    def test_nfc_applied(self):
        # compose a decomposed Korean char
        decomposed = "가"  # ᄀ + ᅡ = 가 (decomposed)
        result = normalize_transcript(decomposed)
        # NFC should produce the precomposed form
        assert result == unicodedata.normalize("NFC", decomposed)

    def test_empty_string(self):
        assert normalize_transcript("") == ""
