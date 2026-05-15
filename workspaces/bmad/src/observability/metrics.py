from __future__ import annotations
"""Prometheus metrics registry for the ASR serving pipeline.

BMAD Developer note: Use the singleton registry here; do not create
additional registries in tests (use the default registry or reset it).
"""
from contextlib import contextmanager
from typing import Generator

from prometheus_client import Counter, Histogram, REGISTRY


# --------------------------------------------------------------------------- #
# Metric definitions
# --------------------------------------------------------------------------- #

def _make_counter(name: str, doc: str, labelnames: list[str] | None = None) -> Counter:
    """Create or retrieve an existing counter (idempotent for tests)."""
    labelnames = labelnames or []
    try:
        return Counter(name, doc, labelnames)
    except ValueError:
        # Already registered — retrieve from registry
        return REGISTRY._names_to_collectors.get(name)  # type: ignore[attr-defined]


def _make_histogram(name: str, doc: str, buckets: tuple = Histogram.DEFAULT_BUCKETS) -> Histogram:
    try:
        return Histogram(name, doc, buckets=buckets)
    except ValueError:
        return REGISTRY._names_to_collectors.get(name)  # type: ignore[attr-defined]


ASR_REQUESTS_TOTAL: Counter = _make_counter(
    "asr_requests_total",
    "Total ASR transcription requests",
    labelnames=["status"],
)

ASR_REQUEST_DURATION: Histogram = _make_histogram(
    "asr_request_duration_seconds",
    "ASR request processing duration in seconds",
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

ASR_ERRORS_TOTAL: Counter = _make_counter(
    "asr_errors_total",
    "Total ASR transcription errors",
)


@contextmanager
def track_request(status: str = "success") -> Generator[None, None, None]:
    """Context manager that records request duration and increments counters."""
    with ASR_REQUEST_DURATION.time():
        try:
            yield
            ASR_REQUESTS_TOTAL.labels(status=status).inc()
        except Exception:
            ASR_ERRORS_TOTAL.inc()
            ASR_REQUESTS_TOTAL.labels(status="error").inc()
            raise
