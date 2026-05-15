from __future__ import annotations
"""Health check route."""
from fastapi import APIRouter

from src.api.models import HealthResponse
from src.backends import get_backend
from src.observability import get_logger

router = APIRouter()
_log = get_logger(__name__)


@router.get("/healthz", response_model=HealthResponse, tags=["observability"])
async def healthz() -> HealthResponse:
    """Liveness check. Returns 200 ok if the service is running."""
    _log.info("Health check")
    return HealthResponse(status="ok")
