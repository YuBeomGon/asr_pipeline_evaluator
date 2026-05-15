# Implementation Scope

This document defines what **is** and **is not** included in this v1 scaffold.

## In Scope (v1)

| Feature | Status | Notes |
|---------|--------|-------|
| OpenAPI 3.1 specification | Done | `openapi.yaml` |
| GET /healthz | Done | Returns `{"status": "ok"}` |
| GET /metrics (Prometheus) | Done | 5 metrics |
| POST /transcribe | Done | multipart file upload |
| POST /eval/cer | Done | JSON body, per-sample + aggregate |
| `ASRBackend` abstract base class | Done | `src/backends/base.py` |
| `MockASRBackend` (no GPU) | Done | Deterministic, configurable |
| Audio preprocessing (resample to 16kHz mono) | Done | `soundfile` + linear interp |
| Transcript NFC normalization | Done | Korean jamo composition |
| Request IDs (`req_<UUID4>`) | Done | All endpoints |
| Structured JSON logging | Done | `request_id` in every line |
| Prometheus metrics | Done | `prometheus_client` |
| CER evaluator (Levenshtein) | Done | `src/eval/cer.py` |
| JSONL manifest CLI | Done | `python -m src.eval.cer_runner` |
| Unit tests | Done | CER, audio, backend |
| Integration tests | Done | All endpoints via TestClient |
| Eval smoke tests | Done | CER runner with manifests |
| Dockerfile | Done | `python:3.11-slim` |
| docker-compose.yml | Done | Single service |
| README | Done | |
| Architecture docs | Done | |

## Out of Scope (v1)

| Feature | Reason |
|---------|--------|
| Real ASR inference (Whisper, NeMo, etc.) | Requires GPU; use MockASRBackend instead |
| Model downloading | Network dependency |
| Speaker diarization | Not in v1 scope |
| Authentication / API keys | Not in v1 scope |
| Billing / rate limiting | Not in v1 scope |
| Autoscaling | Not in v1 scope |
| Persistent storage / database | Not in v1 scope |
| Real-time streaming ASR | Not in v1 scope |
| Model training / fine-tuning | Not in v1 scope |
| Word-level timestamps | Not in v1 scope |
| Confidence per word | Aggregate confidence only |
| Multi-model routing | Single backend per deployment |

## Adding a Real Backend

The `ASRBackend` interface (`src/backends/base.py`) makes it straightforward to
plug in a real model without modifying the API layer:

1. Implement `ASRBackend` in a new file under `src/backends/`.
2. Register the factory in `src/backends/registry.py`.
3. Set `ASR_BACKEND=<name>` in the environment.
4. Add model-specific dependencies to `requirements.txt`.
