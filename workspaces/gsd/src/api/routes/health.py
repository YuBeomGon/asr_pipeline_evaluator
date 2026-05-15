"""GET /healthz — liveness probe."""
from __future__ import annotations

from fastapi import APIRouter

from src.api.schemas import HealthResponse

router = APIRouter()


@router.get("/healthz", response_model=HealthResponse)
async def healthz() -> HealthResponse:
    """Return 200 with {'status': 'ok'} when the service is alive."""
    return HealthResponse(status="ok")
