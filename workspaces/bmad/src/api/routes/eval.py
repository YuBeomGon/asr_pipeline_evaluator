"""POST /eval/cer route."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException

from src.api.models import (
    CERAggregate,
    CERRequest,
    CERResponse,
    CERSampleResponse,
)
from src.eval import CERCalculator
from src.observability import get_logger

router = APIRouter()
_log = get_logger(__name__)
_calculator = CERCalculator()


@router.post("/eval/cer", response_model=CERResponse, tags=["evaluation"])
async def eval_cer(request: CERRequest) -> CERResponse:
    """Compute Character Error Rate for a batch of reference/hypothesis pairs.

    - Normalization: NFKC → lowercase → collapse whitespace → remove spaces.
    - CER = (S + D + I) / N (reference character count after normalization).
    - Returns per-sample results and aggregate statistics.
    """
    _log.info("CER evaluation request", extra={"n_pairs": len(request.pairs)})

    try:
        pairs = [
            {"id": p.id, "reference": p.reference, "hypothesis": p.hypothesis}
            for p in request.pairs
        ]
        results, aggregate = _calculator.compute_batch(pairs)
    except Exception as e:
        _log.exception(f"CER computation failed: {e}")
        raise HTTPException(status_code=500, detail="CER computation error")

    sample_responses = [
        CERSampleResponse(
            id=r.id,
            reference=r.reference,
            hypothesis=r.hypothesis,
            cer=round(r.cer, 6),
            substitutions=r.substitutions,
            deletions=r.deletions,
            insertions=r.insertions,
            reference_length=r.reference_length,
        )
        for r in results
    ]

    aggregate_response = CERAggregate(
        mean_cer=round(aggregate.mean_cer, 6),
        total_samples=aggregate.total_samples,
        total_reference_chars=aggregate.total_reference_chars,
        total_errors=aggregate.total_errors,
    )

    _log.info(
        "CER evaluation complete",
        extra={
            "mean_cer": round(aggregate.mean_cer, 4),
            "total_samples": aggregate.total_samples,
        },
    )

    return CERResponse(results=sample_responses, aggregate=aggregate_response)
