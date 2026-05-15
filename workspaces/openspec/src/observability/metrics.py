from __future__ import annotations
"""
Prometheus metrics definitions for the ASR serving pipeline.
All metrics are registered on a single CollectorRegistry instance.
"""
from functools import lru_cache

from prometheus_client import (
    CollectorRegistry,
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)


class ASRMetrics:
    """Container for all Prometheus metrics used by the ASR pipeline."""

    def __init__(self, registry: CollectorRegistry) -> None:
        self.registry = registry

        self.requests_total = Counter(
            "asr_requests_total",
            "Total number of ASR requests processed",
            labelnames=["status"],
            registry=registry,
        )

        self.request_duration_seconds = Histogram(
            "asr_request_duration_seconds",
            "End-to-end ASR request duration in seconds",
            buckets=(0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
            registry=registry,
        )

        self.errors_total = Counter(
            "asr_errors_total",
            "Total number of ASR errors",
            registry=registry,
        )

        self.audio_duration_seconds = Histogram(
            "asr_audio_duration_seconds",
            "Duration of audio files submitted for transcription (seconds)",
            buckets=(1.0, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
            registry=registry,
        )

        self.inference_duration_seconds = Histogram(
            "asr_inference_duration_seconds",
            "ASR backend inference duration in seconds",
            buckets=(0.01, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
            registry=registry,
        )

    def expose(self) -> tuple[str, str]:
        """Return (body, content_type) for the /metrics endpoint."""
        body = generate_latest(self.registry).decode("utf-8")
        return body, CONTENT_TYPE_LATEST


@lru_cache(maxsize=1)
def get_metrics() -> ASRMetrics:
    """Return the singleton ASRMetrics instance."""
    registry = CollectorRegistry()
    return ASRMetrics(registry)
