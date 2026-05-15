"""
Unit tests for transcript normalization (postprocessing).

Spec ref: .specify/asr-pipeline-spec.md § FR-004
  - Korean NFC normalization
  - Whitespace collapse
  - Punctuation handling
"""

import unicodedata
import pytest
from src.audio.postprocessing import postprocess_transcript


class TestPostprocessTranscript:
    def test_nfc_normalization(self):
        # Construct decomposed Korean string (NFD) and verify it's normalized to NFC
        text_nfd = unicodedata.normalize("NFD", "안녕하세요")
        result = postprocess_transcript(text_nfd)
        # Result should be NFC
        assert result == unicodedata.normalize("NFC", "안녕하세요")

    def test_strip_leading_trailing_whitespace(self):
        assert postprocess_transcript("  hello  ") == "hello"

    def test_collapse_internal_whitespace(self):
        assert postprocess_transcript("hello   world") == "hello world"

    def test_empty_string(self):
        assert postprocess_transcript("") == ""

    def test_korean_unchanged(self):
        text = "안녕하세요 반갑습니다"
        result = postprocess_transcript(text)
        assert result == text

    def test_multiple_spaces_between_words(self):
        assert postprocess_transcript("a  b  c") == "a b c"

    def test_newline_collapsed(self):
        assert postprocess_transcript("hello\nworld") == "hello world"

    def test_tab_collapsed(self):
        assert postprocess_transcript("hello\tworld") == "hello world"
