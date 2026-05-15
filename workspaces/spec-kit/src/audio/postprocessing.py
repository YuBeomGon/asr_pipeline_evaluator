"""
Transcript postprocessing for the ASR serving pipeline.

Spec ref: .specify/asr-pipeline-spec.md § FR-011
  - Korean NFC normalization (NFC is the standard form for Korean; NFKC is used
    for CER comparison; NFC is used for display/storage)
  - Punctuation handling
  - Whitespace normalization

Note: NFC is the canonical form for stored/displayed Korean text.
      NFKC is used only during CER scoring (see src/eval/cer.py).
"""

import unicodedata
import re


def postprocess_transcript(text: str) -> str:
    """
    Normalize a raw ASR transcript for Korean text.

    Steps:
      1. NFC Unicode normalization (Korean canonical form)
      2. Strip leading/trailing whitespace
      3. Collapse internal whitespace runs to a single space

    Args:
        text: Raw transcript string from ASR backend.

    Returns:
        Normalized transcript string.
    """
    # Step 1: NFC normalization — canonical form for Korean (FR-004)
    text = unicodedata.normalize("NFC", text)

    # Step 2: Collapse internal whitespace
    text = re.sub(r"\s+", " ", text)

    # Step 3: Strip edges
    text = text.strip()

    return text
