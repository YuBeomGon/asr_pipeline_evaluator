"""Character Error Rate (CER) calculator.

BMAD Developer: Implements the normalization pipeline and edit-distance
algorithm exactly as specified in docs/eval_protocol.md.

CER = (S + D + I) / N
where N = character count of reference after normalization.
"""
from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from typing import Sequence

# editdistance library is listed in requirements.txt for optional use.
# This implementation uses a pure-Python DP algorithm for full S/D/I decomposition,
# which is required for the CER response schema (not just total distance).


# --------------------------------------------------------------------------- #
# Normalization
# --------------------------------------------------------------------------- #

def normalize_text(text: str) -> str:
    """Normalize text for CER evaluation.

    Pipeline (per eval_protocol.md):
      1. NFKC normalization (handles compatibility chars, full/half-width)
      2. Lowercase
      3. Collapse whitespace to single space, strip
      4. Remove all spaces (CER is char-level, spaces not scored)

    Args:
        text: Input string (any Unicode).

    Returns:
        Normalized string with no spaces.
    """
    # Step 1: NFKC
    s = unicodedata.normalize("NFKC", text)
    # Step 2: Lowercase
    s = s.lower()
    # Step 3: Collapse whitespace
    s = re.sub(r"\s+", " ", s).strip()
    # Step 4: Remove spaces
    s = s.replace(" ", "")
    return s


def normalize_transcript(text: str) -> str:
    """NFC normalization for output transcripts (not for CER scoring).

    Used by the /transcribe endpoint to ensure consistent Korean output.
    """
    return unicodedata.normalize("NFC", text)


# --------------------------------------------------------------------------- #
# Edit distance
# --------------------------------------------------------------------------- #

def levenshtein_distance(a: str, b: str) -> tuple[int, int, int]:
    """Compute character-level Levenshtein distance.

    Returns:
        Tuple of (substitutions, deletions, insertions).

    Note: If editdistance library is available, total edit ops are computed
    via that library (faster). The S/D/I decomposition uses the DP table.
    """
    return _levenshtein_dp(a, b)


def _levenshtein_dp(a: str, b: str) -> tuple[int, int, int]:
    """Dynamic programming Levenshtein with backtracking for S/D/I counts."""
    m, n = len(a), len(b)

    # Build DP table
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j - 1],  # substitution
                    dp[i - 1][j],      # deletion
                    dp[i][j - 1],      # insertion
                )

    # Backtrack to count S/D/I
    substitutions = deletions = insertions = 0
    i, j = m, n
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1]:
            i -= 1
            j -= 1
        elif i > 0 and j > 0 and dp[i][j] == dp[i - 1][j - 1] + 1:
            substitutions += 1
            i -= 1
            j -= 1
        elif i > 0 and dp[i][j] == dp[i - 1][j] + 1:
            deletions += 1
            i -= 1
        else:
            insertions += 1
            j -= 1

    return substitutions, deletions, insertions


# --------------------------------------------------------------------------- #
# Sample result
# --------------------------------------------------------------------------- #

@dataclass
class CERSampleResult:
    id: str
    reference: str
    hypothesis: str
    cer: float
    substitutions: int
    deletions: int
    insertions: int
    reference_length: int  # chars after normalization


@dataclass
class CERAggregate:
    mean_cer: float
    total_samples: int
    total_reference_chars: int
    total_errors: int


# --------------------------------------------------------------------------- #
# Calculator
# --------------------------------------------------------------------------- #

class CERCalculator:
    """Batch CER calculator."""

    def compute_pair(
        self,
        id: str,
        reference: str,
        hypothesis: str,
    ) -> CERSampleResult:
        """Compute CER for a single reference/hypothesis pair."""
        ref_norm = normalize_text(reference)
        hyp_norm = normalize_text(hypothesis)

        n = len(ref_norm)
        if n == 0:
            return CERSampleResult(
                id=id,
                reference=reference,
                hypothesis=hypothesis,
                cer=0.0,
                substitutions=0,
                deletions=0,
                insertions=0,
                reference_length=0,
            )

        s, d, i = levenshtein_distance(ref_norm, hyp_norm)
        total_errors = s + d + i
        cer = total_errors / n

        return CERSampleResult(
            id=id,
            reference=reference,
            hypothesis=hypothesis,
            cer=cer,
            substitutions=s,
            deletions=d,
            insertions=i,
            reference_length=n,
        )

    def compute_batch(
        self,
        pairs: Sequence[dict],
    ) -> tuple[list[CERSampleResult], CERAggregate]:
        """Compute CER for a batch of pairs.

        Args:
            pairs: List of dicts with keys 'id', 'reference', 'hypothesis'.

        Returns:
            (results_list, aggregate)
        """
        results: list[CERSampleResult] = []
        for pair in pairs:
            result = self.compute_pair(
                id=pair["id"],
                reference=pair["reference"],
                hypothesis=pair["hypothesis"],
            )
            results.append(result)

        total_samples = len(results)
        if total_samples == 0:
            aggregate = CERAggregate(
                mean_cer=0.0,
                total_samples=0,
                total_reference_chars=0,
                total_errors=0,
            )
        else:
            total_ref_chars = sum(r.reference_length for r in results)
            total_errors = sum(r.substitutions + r.deletions + r.insertions for r in results)
            mean_cer = sum(r.cer for r in results) / total_samples
            aggregate = CERAggregate(
                mean_cer=mean_cer,
                total_samples=total_samples,
                total_reference_chars=total_ref_chars,
                total_errors=total_errors,
            )

        return results, aggregate
