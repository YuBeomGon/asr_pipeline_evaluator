from __future__ import annotations
from .health import router as health_router
from .transcribe import router as transcribe_router
from .eval import router as eval_router

__all__ = ["health_router", "transcribe_router", "eval_router"]
