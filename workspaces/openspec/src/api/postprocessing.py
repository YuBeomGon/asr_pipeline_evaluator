from __future__ import annotations
"""
Transcript postprocessing: normalization applied AFTER ASR inference.
Applied to the raw backend output before returning to the client.

Normalization steps:
  1. Unicode NFC normalization (Korean jamo composition)
  2. Strip leading/trailing whitespace
  3. Collapse internal whitespace runs
  4. Handle common Korean punctuation edge cases
"""
import re
import unicodedata


def postprocess_transcript(raw: str) -> str:
    """
    Normalize a raw ASR transcript for Korean text.

    Args:
        raw: Raw transcript string from the ASR backend.

    Returns:
        Normalized transcript string.
    """
    if not raw:
        return raw

    # Step 1: NFC normalization (correct Korean jamo composition)
    text = unicodedata.normalize("NFC", raw)

    # Step 2: Strip outer whitespace
    text = text.strip()

    # Step 3: Collapse multiple whitespace characters into a single space
    text = re.sub(r"\s+", " ", text)

    # Step 4: Remove spaces before Korean punctuation characters
    # e.g. "안녕 ." -> "안녕."  "감사합니다 ," -> "감사합니다,"
    text = re.sub(r"\s+([.,!?;:。、！？；：])", r"\1", text)

    return text
