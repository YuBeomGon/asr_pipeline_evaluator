from __future__ import annotations
from .health import router as health_router
from .metrics import router as metrics_router
from .transcribe import router as transcribe_router
from .eval_cer import router as eval_cer_router

__all__ = ["health_router", "metrics_router", "transcribe_router", "eval_cer_router"]
