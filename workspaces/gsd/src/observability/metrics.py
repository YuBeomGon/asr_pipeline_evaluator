"""Prometheus metrics definitions."""
from __future__ import annotations

from prometheus_client import Counter, Histogram, REGISTRY, generate_latest, CollectorRegistry

# Use default registry
_requests_total = Counter(
    "asr_requests_total",
    "Total ASR transcribe requests",
    ["status"],
)

_request_duration = Histogram(
    "asr_request_duration_seconds",
    "ASR request end-to-end latency in seconds",
    buckets=[0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0],
)

_errors_total = Counter(
    "asr_errors_total",
    "Total ASR processing errors",
)


def inc_request(status: str = "success") -> None:
    _requests_total.labels(status=status).inc()


def observe_duration(seconds: float) -> None:
    _request_duration.observe(seconds)


def inc_error() -> None:
    _errors_total.inc()


def get_metrics_text() -> bytes:
    return generate_latest(REGISTRY)
