"""Character Error Rate (CER) computation.

CER = (S + D + I) / N
where N = number of characters in the reference (after normalization).

Normalization applied before scoring:
  NFKC → NFC → lowercase → collapse whitespace → remove spaces
"""
from __future__ import annotations

from dataclasses import dataclass

import editdistance

from .normalizer import normalize_for_cer


@dataclass
class CERResult:
    id: str
    reference: str
    hypothesis: str
    reference_normalized: str
    hypothesis_normalized: str
    edit_distance: int
    reference_length: int
    cer: float  # 0.0 = perfect, can exceed 1.0 if many insertions


def compute_cer(
    reference: str,
    hypothesis: str,
    sample_id: str = "",
) -> CERResult:
    """Compute CER for a single reference/hypothesis pair."""
    ref_norm = normalize_for_cer(reference)
    hyp_norm = normalize_for_cer(hypothesis)

    dist = editdistance.eval(ref_norm, hyp_norm)
    ref_len = len(ref_norm)

    if ref_len == 0:
        # If reference is empty, CER = 0 if hypothesis also empty, else 1.0
        cer = 0.0 if len(hyp_norm) == 0 else 1.0
    else:
        cer = dist / ref_len

    return CERResult(
        id=sample_id,
        reference=reference,
        hypothesis=hypothesis,
        reference_normalized=ref_norm,
        hypothesis_normalized=hyp_norm,
        edit_distance=dist,
        reference_length=ref_len,
        cer=cer,
    )


@dataclass
class AggregateCER:
    num_samples: int
    total_edit_distance: int
    total_reference_length: int
    macro_cer: float  # mean of per-sample CERs
    micro_cer: float  # total_edit_distance / total_reference_length


def aggregate_cer(results: list[CERResult]) -> AggregateCER:
    """Compute aggregate CER statistics over a list of results."""
    if not results:
        return AggregateCER(
            num_samples=0,
            total_edit_distance=0,
            total_reference_length=0,
            macro_cer=0.0,
            micro_cer=0.0,
        )

    total_dist = sum(r.edit_distance for r in results)
    total_ref = sum(r.reference_length for r in results)
    macro = sum(r.cer for r in results) / len(results)
    micro = total_dist / total_ref if total_ref > 0 else 0.0

    return AggregateCER(
        num_samples=len(results),
        total_edit_distance=total_dist,
        total_reference_length=total_ref,
        macro_cer=macro,
        micro_cer=micro,
    )
