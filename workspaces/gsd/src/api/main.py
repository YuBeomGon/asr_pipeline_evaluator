"""FastAPI application factory and lifespan."""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.backends import get_backend
from src.config.settings import get_settings
from src.observability.logging import setup_logging, get_logger

from src.api.routes.health import router as health_router
from src.api.routes.metrics_route import router as metrics_router
from src.api.routes.transcribe import router as transcribe_router, set_backend
from src.api.routes.eval import router as eval_router

_logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    settings = get_settings()
    setup_logging(settings.log_level)
    _logger.info("Starting ASR service", extra={"backend": settings.asr_backend})

    backend = get_backend(settings.asr_backend)
    set_backend(backend)
    app.state.backend = backend

    _logger.info("Backend ready", extra={"backend": backend.name})
    yield
    _logger.info("Shutting down ASR service")


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="ASR Serving Pipeline",
        description="Production-oriented ASR pipeline with CER evaluation",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health_router, tags=["health"])
    app.include_router(metrics_router, tags=["observability"])
    app.include_router(transcribe_router, tags=["asr"])
    app.include_router(eval_router, tags=["eval"])

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    settings = get_settings()
    uvicorn.run("src.api.main:app", host=settings.host, port=settings.port, reload=False)
