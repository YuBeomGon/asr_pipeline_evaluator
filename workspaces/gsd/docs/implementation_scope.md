# Implementation Scope (v1)

## What IS in v1

| Feature | Status |
|---------|--------|
| FastAPI HTTP server | Done |
| GET /healthz liveness probe | Done |
| GET /metrics Prometheus text | Done |
| POST /transcribe multipart audio | Done |
| POST /eval/cer HTTP endpoint | Done |
| ASRBackend ABC | Done |
| MockASRBackend (deterministic, no GPU) | Done |
| Audio resample to 16 kHz mono | Done |
| Transcript NFC normalization | Done |
| Request ID (req_ + UUID4) | Done |
| Structured JSON logging w/ request_id | Done |
| Prometheus metrics (3 required) | Done |
| CER CLI (python -m src.eval.cer_runner) | Done |
| JSONL manifest support | Done |
| Unit tests (CER + normalizer) | Done |
| Integration tests (all endpoints) | Done |
| Eval smoke tests | Done |
| Dockerfile | Done |
| docker-compose.yml | Done |
| Architecture doc | Done |
| API doc | Done |
| Eval protocol doc | Done |
| Runbook | Done |

## What is NOT in v1

| Feature | Reason |
|---------|--------|
| Real ASR model (Whisper, etc.) | Requires GPU/model download; out of local scope |
| Model training | Out of scope for serving pipeline |
| Speaker diarization | Future enhancement |
| Authentication / API keys | Future enhancement |
| Rate limiting | Future enhancement |
| Horizontal scaling / work queue | Future enhancement |
| Real-time streaming WebSocket | Future enhancement |
| Billing / usage tracking | Future enhancement |
| Full autoscaling | Future enhancement |
| VAD (Voice Activity Detection) | Future enhancement |

## Adding a real backend

1. Create `src/backends/whisper.py` implementing `ASRBackend`
2. Register it in `src/backends/__init__.py::get_backend`
3. Set `ASR_BACKEND=whisper` env var
4. The rest of the stack (API, metrics, logging, CER) stays unchanged
