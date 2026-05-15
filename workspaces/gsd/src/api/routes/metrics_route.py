"""GET /metrics — Prometheus exposition format."""
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import Response

from src.observability.metrics import get_metrics_text

router = APIRouter()


@router.get("/metrics")
async def metrics() -> Response:
    """Expose Prometheus metrics in text format (version=0.0.4)."""
    data = get_metrics_text()
    return Response(
        content=data,
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )
