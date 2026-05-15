"""FastAPI application factory.

BMAD Developer: Use `create_app()` to obtain the app instance.
The module-level `app` is the Uvicorn entrypoint.
"""
from __future__ import annotations

from fastapi import FastAPI, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from src.api.routes import eval_router, health_router, transcribe_router
from src.config import get_settings
from src.observability import configure_logging, get_logger


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()
    configure_logging(settings.log_level)

    log = get_logger(__name__)
    log.info("Creating ASR serving application", extra={"backend": settings.asr_backend})

    app = FastAPI(
        title="ASR Serving Pipeline",
        description="Production-oriented ASR serving pipeline with CER evaluation",
        version="1.0.0",
    )

    # ── Routers ──────────────────────────────────────────────────────────────
    app.include_router(health_router)
    app.include_router(transcribe_router)
    app.include_router(eval_router)

    # ── Metrics endpoint ─────────────────────────────────────────────────────
    @app.get("/metrics", tags=["observability"], include_in_schema=False)
    async def metrics(request: Request) -> Response:
        """Prometheus text format metrics."""
        data = generate_latest()
        return Response(
            content=data,
            media_type=CONTENT_TYPE_LATEST,
        )

    log.info("Application created successfully")
    return app


# Module-level app instance for Uvicorn
app = create_app()
