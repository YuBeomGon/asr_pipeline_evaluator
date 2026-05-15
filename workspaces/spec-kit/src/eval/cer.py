from __future__ import annotations
"""
Character Error Rate (CER) evaluation logic.

Spec ref: .specify/asr-pipeline-spec.md § CER Evaluation Protocol

Formula:
    CER = (S + D + I) / N
    where N = reference character count (after normalization, spaces removed)

Normalization pipeline (applied to BOTH reference and hypothesis):
    1. Unicode NFKC normalization
    2. Lowercase
    3. Trim + collapse internal whitespace to single space
    4. Remove all spaces before character-level alignment

Edge cases:
    - Empty reference (after normalization) → CER = None (excluded from aggregate)
    - Empty hypothesis, non-empty reference → CER = 1.0 (all deletions)
    - CER may exceed 1.0 when insertions > 0 in a short reference
"""

import unicodedata
import re
from dataclasses import dataclass

import editdistance


def normalize_for_cer(text: str) -> str:
    """
    Apply the CER normalization pipeline.

    Spec ref: .specify/asr-pipeline-spec.md § CER Evaluation Protocol → Normalization Pipeline

    Steps:
      1. NFKC normalization (handles Korean composed/decomposed jamo)
      2. Lowercase
      3. Trim + collapse whitespace
      4. Remove all spaces (for character-level scoring)

    Args:
        text: Raw text string (reference or hypothesis).

    Returns:
        Normalized string with spaces removed, ready for character-level edit distance.
    """
    # Step 1: NFKC normalization
    text = unicodedata.normalize("NFKC", text)

    # Step 2: Lowercase
    text = text.lower()

    # Step 3: Trim + collapse whitespace
    text = re.sub(r"\s+", " ", text).strip()

    # Step 4: Remove spaces for character-level alignment
    text = text.replace(" ", "")

    return text


@dataclass
class CERSampleResult:
    """CER result for a single reference/hypothesis pair."""
    id: str
    cer: float | None        # None when reference is empty (undefined)
    reference_chars: int     # character count after normalization (spaces removed)
    edits: int               # Levenshtein edit distance (chars)


@dataclass
class CERBatchResult:
    """Aggregate CER result for a batch of pairs."""
    pairs: list[CERSampleResult]
    overall_cer: float
    total_reference_chars: int
    total_edits: int


def compute_cer_sample(
    sample_id: str,
    reference: str,
    hypothesis: str,
) -> CERSampleResult:
    """
    Compute CER for a single (reference, hypothesis) pair.

    Spec ref: .specify/asr-pipeline-spec.md § FR-010
    """
    ref_norm = normalize_for_cer(reference)
    hyp_norm = normalize_for_cer(hypothesis)

    ref_len = len(ref_norm)

    if ref_len == 0:
        # Spec: empty reference → CER undefined
        return CERSampleResult(id=sample_id, cer=None, reference_chars=0, edits=0)

    edits = editdistance.eval(ref_norm, hyp_norm)
    cer = edits / ref_len

    return CERSampleResult(
        id=sample_id,
        cer=cer,
        reference_chars=ref_len,
        edits=edits,
    )


def compute_cer_batch(
    pairs: list[dict],  # each: {"id": str, "reference": str, "hypothesis": str}
) -> CERBatchResult:
    """
    Compute CER for a list of pairs and return aggregate statistics.

    Spec ref: .specify/asr-pipeline-spec.md § FR-010, FR-012
    """
    sample_results: list[CERSampleResult] = []
    total_ref_chars = 0
    total_edits = 0

    for pair in pairs:
        result = compute_cer_sample(
            sample_id=pair["id"],
            reference=pair.get("reference", ""),
            hypothesis=pair.get("hypothesis", ""),
        )
        sample_results.append(result)
        if result.cer is not None:
            total_ref_chars += result.reference_chars
            total_edits += result.edits

    overall_cer = (total_edits / total_ref_chars) if total_ref_chars > 0 else 0.0

    return CERBatchResult(
        pairs=sample_results,
        overall_cer=overall_cer,
        total_reference_chars=total_ref_chars,
        total_edits=total_edits,
    )
