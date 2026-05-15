from __future__ import annotations
"""GET /healthz — liveness / readiness probe."""
from fastapi import APIRouter

from src.api.schemas import HealthResponse
from src.backends.registry import get_backend
from src.observability.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/healthz", response_model=HealthResponse, tags=["health"])
async def health_check() -> HealthResponse:
    """
    Return service health status.

    Checks backend liveness. Returns {"status": "ok"} if healthy,
    {"status": "degraded"} if the backend reports unhealthy.
    """
    try:
        backend = get_backend()
        healthy = backend.health_check()
        status = "ok" if healthy else "degraded"
    except Exception:
        logger.exception("Health check failed")
        status = "error"

    logger.debug("Health check", extra={"health_status": status})
    return HealthResponse(status=status)
