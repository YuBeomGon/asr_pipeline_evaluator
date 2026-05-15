from __future__ import annotations
"""
Structured JSON logging for the ASR serving pipeline.

Spec ref: .specify/asr-pipeline-spec.md § NFR-003
  All log output MUST be structured JSON with at minimum:
    timestamp, level, request_id, message

Usage:
    from src.observability.logging import get_logger
    logger = get_logger(__name__)
    logger.info("transcription complete", request_id="req_abc", extra_key="value")
"""

import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any


class StructuredJsonFormatter(logging.Formatter):
    """Format log records as JSON lines with required fields."""

    def format(self, record: logging.LogRecord) -> str:
        log_entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "request_id": getattr(record, "request_id", "-"),
        }
        # Attach any extra fields added via LoggerAdapter or extra= dict
        for key, value in record.__dict__.items():
            if key not in (
                "args", "asctime", "created", "exc_info", "exc_text", "filename",
                "funcName", "id", "levelname", "levelno", "lineno", "module",
                "msecs", "message", "msg", "name", "pathname", "process",
                "processName", "relativeCreated", "stack_info", "thread",
                "threadName", "request_id",
            ):
                log_entry[key] = value

        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_entry, ensure_ascii=False)


def configure_logging(level: str = "INFO") -> None:
    """Configure root logger with JSON formatter."""
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(StructuredJsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(getattr(logging, level.upper(), logging.INFO))


def get_logger(name: str) -> logging.Logger:
    """Return a named logger; configure root if not yet set up."""
    return logging.getLogger(name)


class RequestLogger(logging.LoggerAdapter):
    """Logger adapter that injects request_id into every log record."""

    def __init__(self, logger: logging.Logger, request_id: str) -> None:
        super().__init__(logger, {"request_id": request_id})

    def process(self, msg: str, kwargs: Any) -> tuple[str, Any]:
        kwargs.setdefault("extra", {})
        kwargs["extra"]["request_id"] = self.extra["request_id"]
        return msg, kwargs
