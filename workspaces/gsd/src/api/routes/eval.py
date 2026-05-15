"""POST /eval/cer — CER computation endpoint."""
from __future__ import annotations

from fastapi import APIRouter

from src.api.schemas import CERAggregate, CERRequest, CERResponse, CERSampleResult
from src.eval.cer import aggregate_cer, compute_cer

router = APIRouter()


@router.post("/eval/cer", response_model=CERResponse)
async def eval_cer(body: CERRequest) -> CERResponse:
    """Compute character error rate for a list of reference/hypothesis pairs."""
    results = [
        compute_cer(pair.reference, pair.hypothesis, sample_id=pair.id)
        for pair in body.pairs
    ]
    agg = aggregate_cer(results)

    return CERResponse(
        aggregate=CERAggregate(
            num_samples=agg.num_samples,
            total_edit_distance=agg.total_edit_distance,
            total_reference_length=agg.total_reference_length,
            macro_cer=round(agg.macro_cer, 6),
            micro_cer=round(agg.micro_cer, 6),
        ),
        samples=[
            CERSampleResult(
                id=r.id,
                reference_normalized=r.reference_normalized,
                hypothesis_normalized=r.hypothesis_normalized,
                edit_distance=r.edit_distance,
                reference_length=r.reference_length,
                cer=round(r.cer, 6),
            )
            for r in results
        ],
    )
