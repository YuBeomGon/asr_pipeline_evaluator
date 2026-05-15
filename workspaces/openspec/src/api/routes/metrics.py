from __future__ import annotations
"""GET /metrics — Prometheus text exposition format."""
from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from src.observability.metrics import get_metrics

router = APIRouter()

PROMETHEUS_CONTENT_TYPE = "text/plain; version=0.0.4; charset=utf-8"


@router.get("/metrics", tags=["metrics"])
async def prometheus_metrics() -> PlainTextResponse:
    """
    Return Prometheus metrics in text exposition format.
    Content-Type: text/plain; version=0.0.4
    """
    metrics = get_metrics()
    body, _ct = metrics.expose()
    return PlainTextResponse(content=body, media_type=PROMETHEUS_CONTENT_TYPE)
