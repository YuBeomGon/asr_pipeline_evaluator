from __future__ import annotations
"""
Prometheus metrics for the ASR serving pipeline.

Spec ref: .specify/asr-pipeline-spec.md § FR-002
  Required metric families:
    - asr_requests_total (counter, label: status)
    - asr_request_duration_seconds (histogram)
    - asr_errors_total (counter)

API contract: GET /metrics → text/plain; version=0.0.4
"""

from prometheus_client import Counter, Histogram, REGISTRY, generate_latest, CONTENT_TYPE_LATEST

# --- Metric definitions (FR-002) ---

asr_requests_total = Counter(
    "asr_requests_total",
    "Total number of ASR transcription requests",
    ["status"],  # "success" | "error"
)

asr_request_duration_seconds = Histogram(
    "asr_request_duration_seconds",
    "End-to-end request duration in seconds for ASR transcription",
)

asr_errors_total = Counter(
    "asr_errors_total",
    "Total number of ASR transcription errors",
)


def get_metrics_output() -> tuple[bytes, str]:
    """Return (body_bytes, content_type) for the /metrics endpoint."""
    return generate_latest(REGISTRY), CONTENT_TYPE_LATEST
