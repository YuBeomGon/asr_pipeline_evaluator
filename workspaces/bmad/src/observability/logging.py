from __future__ import annotations
"""Structured JSON logging for the ASR serving pipeline.

Every log line in a request context includes `request_id`.
"""
import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    """Format log records as single-line JSON objects."""

    def format(self, record: logging.LogRecord) -> str:
        log_obj: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "module": record.name,
            "message": record.getMessage(),
        }

        # Include request_id if present (set by route handlers)
        if hasattr(record, "request_id"):
            log_obj["request_id"] = record.request_id

        # Include extra fields
        for key, value in record.__dict__.items():
            if key not in (
                "name", "msg", "args", "levelname", "levelno", "pathname",
                "filename", "module", "exc_info", "exc_text", "stack_info",
                "lineno", "funcName", "created", "msecs", "relativeCreated",
                "thread", "threadName", "processName", "process", "message",
                "request_id", "taskName",
            ):
                if not key.startswith("_"):
                    log_obj[key] = value

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj, ensure_ascii=False)


class RequestIDAdapter(logging.LoggerAdapter):
    """Logger adapter that injects request_id into every log record."""

    def process(self, msg: str, kwargs: Any) -> tuple[str, Any]:
        extra = kwargs.setdefault("extra", {})
        extra["request_id"] = self.extra.get("request_id", "")
        return msg, kwargs


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with JSON formatter."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))


def get_logger(name: str, request_id: str = "") -> RequestIDAdapter:
    """Return a logger adapter that includes request_id in every message."""
    logger = logging.getLogger(name)
    return RequestIDAdapter(logger, {"request_id": request_id})
