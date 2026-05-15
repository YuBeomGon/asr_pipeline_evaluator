# Implementation Scope: ASR Serving Pipeline v1

**Spec ref**: `.specify/asr-pipeline-spec.md § Assumptions`

## What Is Included in v1

| Feature | Status |
|---------|--------|
| FastAPI REST API | Included |
| GET /healthz | Included |
| GET /metrics (Prometheus) | Included |
| POST /transcribe (multipart audio) | Included |
| POST /eval/cer | Included |
| ASRBackend abstract class | Included |
| MockASRBackend (deterministic, no GPU) | Included |
| Audio preprocessing: 16 kHz mono resample | Included |
| Transcript postprocessing: NFC normalize | Included |
| Request ID generation (req_ + uuid4) | Included |
| Prometheus metrics (3 required metric families) | Included |
| Structured JSON logging with request_id | Included |
| CER evaluation (Levenshtein, NFKC normalization) | Included |
| CER CLI runner (python -m src.eval.cer_runner) | Included |
| JSONL manifest support | Included |
| pytest unit tests | Included |
| pytest integration tests | Included |
| pytest eval smoke tests | Included |
| Dockerfile | Included |
| docker-compose.yml | Included |
| Architecture documentation | Included |
| API documentation | Included |
| Runbook | Included |

## What Is Explicitly Out of Scope for v1

| Feature | Rationale |
|---------|-----------|
| Real GPU inference (Whisper, wav2vec2, etc.) | Requires model weights and GPU hardware |
| Model training or fine-tuning | Research/ML engineering concern |
| Speaker diarization | v2+ feature |
| Authentication / API keys | v2+ feature |
| Rate limiting | v2+ feature |
| Billing / usage metering | v2+ feature |
| Full horizontal autoscaling | Infrastructure concern |
| Streaming transcription | v2+ feature |
| Real-time WebSocket API | v2+ feature |
| Multitenancy | v2+ feature |
| Persistent storage / databases | Stateless service in v1 |

## Extension Points for Real Backends

To swap in a real ASR backend:

1. Implement `ASRBackend` in `src/backends/<name>.py`
2. Add the backend to `src/api/main.py` lifespan switch:
   ```python
   if settings.backend == "whisper":
       backend = WhisperBackend()
   ```
3. Add any backend-specific dependencies to `requirements.txt`
4. Set `ASR_BACKEND=<name>` in the environment or `.env`

The API contract and CER evaluation are backend-agnostic.
