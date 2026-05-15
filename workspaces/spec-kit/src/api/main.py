"""
FastAPI application entry point for the ASR serving pipeline.

Spec ref: .specify/asr-pipeline-spec.md § NFR-001
  Service MUST start with: uvicorn src.api.main:app --host 0.0.0.0 --port 8000

Start command:
    uvicorn src.api.main:app --host 0.0.0.0 --port 8000
"""

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI

from src.api.routes import router
from src.backends.mock import MockASRBackend
from src.config.settings import settings
from src.observability.logging import configure_logging, get_logger

configure_logging(settings.log_level)
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifespan: initialise backend on startup, clean up on shutdown.

    Spec ref: .specify/asr-pipeline-spec.md § NFR-005
      All ASR calls go through the ASRBackend interface.
    """
    # Initialise the ASR backend (v1 always uses MockASRBackend)
    backend = MockASRBackend()
    app.state.backend = backend
    logger.info(
        "ASR backend initialised",
        extra={"backend": backend.backend_name, "config_backend": settings.backend},
    )

    yield

    logger.info("ASR serving pipeline shutting down")


app = FastAPI(
    title="ASR Serving Pipeline",
    description=(
        "Production-oriented v1 ASR serving pipeline with CER evaluation. "
        "Spec: .specify/asr-pipeline-spec.md"
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.api.main:app",
        host=settings.host,
        port=settings.port,
        log_config=None,  # Use our structured logger
    )
