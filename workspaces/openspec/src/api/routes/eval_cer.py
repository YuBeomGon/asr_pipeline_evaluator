from __future__ import annotations
"""POST /eval/cer — CER evaluation endpoint."""
import uuid

from fastapi import APIRouter, HTTPException, status

from src.api.schemas import (
    CERAggregate,
    CERRequest,
    CERResponse,
    CERSampleResult,
)
from src.eval.cer import CEREvaluator
from src.observability.logging import get_logger, request_id_var

router = APIRouter()
logger = get_logger(__name__)
_evaluator = CEREvaluator()


@router.post(
    "/eval/cer",
    response_model=CERResponse,
    status_code=status.HTTP_200_OK,
    tags=["evaluation"],
)
async def evaluate_cer(body: CERRequest) -> CERResponse:
    """
    Compute Character Error Rate (CER) for reference/hypothesis pairs.

    Normalization pipeline (applied to both ref and hyp):
      NFKC -> lowercase -> trim/collapse whitespace -> remove spaces

    Returns per-sample CER and aggregate statistics.
    """
    request_id = f"req_{uuid.uuid4()}"
    token = request_id_var.set(request_id)

    logger.info(
        "CER evaluation request",
        extra={"num_pairs": len(body.pairs)},
    )

    try:
        pairs_as_dicts = [
            {"id": p.id, "reference": p.reference, "hypothesis": p.hypothesis}
            for p in body.pairs
        ]
        aggregate = _evaluator.evaluate_batch(pairs_as_dicts)

        logger.info(
            "CER evaluation complete",
            extra={
                "num_samples": aggregate.total_samples,
                "mean_cer": aggregate.mean_cer,
            },
        )

        return CERResponse(
            results=[
                CERSampleResult(
                    id=r.id,
                    reference=r.reference,
                    hypothesis=r.hypothesis,
                    cer=r.cer,
                    substitutions=r.substitutions,
                    deletions=r.deletions,
                    insertions=r.insertions,
                    reference_length=r.reference_length,
                )
                for r in aggregate.per_sample
            ],
            aggregate=CERAggregate(
                mean_cer=aggregate.mean_cer,
                total_substitutions=aggregate.total_substitutions,
                total_deletions=aggregate.total_deletions,
                total_insertions=aggregate.total_insertions,
                total_reference_length=aggregate.total_reference_length,
                total_samples=aggregate.total_samples,
            ),
        )
    except Exception as exc:
        logger.exception("CER evaluation failed")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"CER evaluation error: {exc}",
        )
    finally:
        request_id_var.reset(token)
