from __future__ import annotations
"""
CER (Character Error Rate) evaluator.

Protocol:
    CER = (substitutions + deletions + insertions) / reference_character_count

Normalization pipeline (applied to both reference and hypothesis):
    1. Unicode NFKC normalization
    2. Lowercase
    3. Trim and collapse whitespace
    4. Remove all spaces before character-level scoring

Korean-specific considerations:
    - Korean NFC normalization is applied (NFKC is a superset)
    - Korean characters are treated individually as characters
    - Spaces between Korean words are removed before CER scoring
"""
import re
import unicodedata
from dataclasses import dataclass, field
from typing import List


def normalize_for_cer(text: str) -> str:
    """
    Apply the standard CER normalization pipeline.

    Steps:
        1. Unicode NFKC normalization (covers NFC for Korean)
        2. Lowercase
        3. Strip leading/trailing whitespace
        4. Collapse internal whitespace runs to single space
        5. Remove all spaces (character-level scoring)

    Args:
        text: Raw transcript string.

    Returns:
        Normalized string ready for character-level edit distance.
    """
    # Step 1: NFKC normalization (also applies NFC for Korean jamo)
    text = unicodedata.normalize("NFKC", text)

    # Step 2: Lowercase
    text = text.lower()

    # Step 3: Strip and collapse whitespace
    text = text.strip()
    text = re.sub(r"\s+", " ", text)

    # Step 4: Remove spaces before character-level scoring
    text = text.replace(" ", "")

    return text


def _levenshtein(ref: str, hyp: str) -> tuple[int, int, int]:
    """
    Compute character-level Levenshtein edit operations.

    Returns:
        (substitutions, deletions, insertions)
        where deletions are chars in ref missing from hyp,
        and insertions are chars in hyp missing from ref.
    """
    n = len(ref)
    m = len(hyp)

    # dp[i][j] = edit distance between ref[:i] and hyp[:j]
    dp = [[0] * (m + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = i
    for j in range(m + 1):
        dp[0][j] = j

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref[i - 1] == hyp[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j - 1],  # substitution
                    dp[i - 1][j],      # deletion (ref char deleted)
                    dp[i][j - 1],      # insertion (hyp char inserted)
                )

    # Backtrace to count operations
    i, j = n, m
    substitutions = 0
    deletions = 0
    insertions = 0

    while i > 0 or j > 0:
        if i > 0 and j > 0 and ref[i - 1] == hyp[j - 1]:
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


@dataclass
class CERPairResult:
    """CER result for a single reference/hypothesis pair."""

    id: str
    reference: str
    """Normalized reference string."""
    hypothesis: str
    """Normalized hypothesis string."""
    cer: float
    substitutions: int
    deletions: int
    insertions: int
    reference_length: int


@dataclass
class CERAggregate:
    """Aggregate CER statistics across all samples."""

    mean_cer: float
    total_substitutions: int
    total_deletions: int
    total_insertions: int
    total_reference_length: int
    total_samples: int
    per_sample: List[CERPairResult] = field(default_factory=list)


class CEREvaluator:
    """
    Evaluates CER for one or more reference/hypothesis pairs.
    Applies the standard normalization pipeline before scoring.
    """

    def evaluate_pair(self, sample_id: str, reference: str, hypothesis: str) -> CERPairResult:
        """
        Evaluate CER for a single pair.

        Args:
            sample_id: Identifier for the sample.
            reference: Ground truth transcript (raw).
            hypothesis: ASR output (raw).

        Returns:
            CERPairResult with normalized strings and edit distance breakdown.
        """
        norm_ref = normalize_for_cer(reference)
        norm_hyp = normalize_for_cer(hypothesis)

        ref_len = len(norm_ref)

        if ref_len == 0:
            # Empty reference: CER is 0 if hyp is also empty, else undefined (treat as 1.0)
            if len(norm_hyp) == 0:
                return CERPairResult(
                    id=sample_id,
                    reference=norm_ref,
                    hypothesis=norm_hyp,
                    cer=0.0,
                    substitutions=0,
                    deletions=0,
                    insertions=0,
                    reference_length=0,
                )
            else:
                return CERPairResult(
                    id=sample_id,
                    reference=norm_ref,
                    hypothesis=norm_hyp,
                    cer=1.0,
                    substitutions=0,
                    deletions=0,
                    insertions=len(norm_hyp),
                    reference_length=0,
                )

        subs, dels, ins = _levenshtein(norm_ref, norm_hyp)
        cer = (subs + dels + ins) / ref_len

        return CERPairResult(
            id=sample_id,
            reference=norm_ref,
            hypothesis=norm_hyp,
            cer=cer,
            substitutions=subs,
            deletions=dels,
            insertions=ins,
            reference_length=ref_len,
        )

    def evaluate_batch(
        self,
        pairs: list[dict],
    ) -> CERAggregate:
        """
        Evaluate CER for a batch of pairs.

        Args:
            pairs: List of dicts with keys: 'id', 'reference', 'hypothesis'.

        Returns:
            CERAggregate with per-sample results and aggregate statistics.
        """
        results: list[CERPairResult] = []
        for pair in pairs:
            result = self.evaluate_pair(
                sample_id=pair["id"],
                reference=pair["reference"],
                hypothesis=pair["hypothesis"],
            )
            results.append(result)

        total_subs = sum(r.substitutions for r in results)
        total_dels = sum(r.deletions for r in results)
        total_ins = sum(r.insertions for r in results)
        total_ref_len = sum(r.reference_length for r in results)
        n = len(results)

        mean_cer = sum(r.cer for r in results) / n if n > 0 else 0.0

        return CERAggregate(
            mean_cer=mean_cer,
            total_substitutions=total_subs,
            total_deletions=total_dels,
            total_insertions=total_ins,
            total_reference_length=total_ref_len,
            total_samples=n,
            per_sample=results,
        )
