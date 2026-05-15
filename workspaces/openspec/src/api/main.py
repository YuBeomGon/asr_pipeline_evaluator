from __future__ import annotations
"""
FastAPI application entry point.

This server implements the OpenAPI specification defined in openapi.yaml
at the project root. All endpoints, request/response schemas, and
content types are derived from that specification.

See: /openapi.yaml for the authoritative API contract.
"""
import logging
from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api.routes import (
    eval_cer_router,
    health_router,
    metrics_router,
    transcribe_router,
)
from src.backends.registry import get_backend
from src.config.settings import get_settings
from src.observability.logging import setup_logging, get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: initialise resources on startup, clean up on shutdown."""
    settings = get_settings()
    setup_logging(log_level=settings.log_level, log_format=settings.log_format)

    logger.info(
        "ASR pipeline starting",
        extra={"backend": settings.backend, "port": settings.port},
    )

    # Warm up the backend singleton so the first request doesn't pay init cost
    try:
        backend = get_backend()
        healthy = backend.health_check()
        logger.info(
            "ASR backend initialised",
            extra={"backend_id": backend.backend_id, "healthy": healthy},
        )
    except Exception:
        logger.exception("Failed to initialise ASR backend")

    yield

    logger.info("ASR pipeline shutting down")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="ASR Serving Pipeline",
        description=(
            "Production-oriented ASR serving pipeline with CER evaluation. "
            "Implements the OpenAPI spec defined in openapi.yaml."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # CORS — restrictive by default; loosen for local dev via env vars
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if settings.debug else [],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    # Register route groups
    app.include_router(health_router)
    app.include_router(metrics_router)
    app.include_router(transcribe_router)
    app.include_router(eval_cer_router)

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled exception", extra={"path": request.url.path})
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
