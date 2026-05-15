"""Text normalization for CER evaluation.

Pipeline:
  1. Unicode NFKC normalization
  2. NFC normalization (Korean canonical form)
  3. Lowercase
  4. Trim and collapse whitespace
  5. Strip spaces before char-level CER scoring
"""
from __future__ import annotations

import re
import unicodedata


def normalize_for_cer(text: str) -> str:
    """Return normalized string ready for character-level edit distance."""
    # Step 1: NFKC (compatibility decomposition then canonical composition)
    text = unicodedata.normalize("NFKC", text)
    # Step 2: NFC for Korean
    text = unicodedata.normalize("NFC", text)
    # Step 3: Lowercase
    text = text.lower()
    # Step 4: Collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()
    # Step 5: Remove spaces for char-level scoring
    text = text.replace(" ", "")
    return text


def normalize_transcript(text: str) -> str:
    """Post-process a raw transcript for display/storage (NOT for CER).

    Applies NFC and strips leading/trailing whitespace.
    """
    text = unicodedata.normalize("NFC", text)
    text = text.strip()
    return text
