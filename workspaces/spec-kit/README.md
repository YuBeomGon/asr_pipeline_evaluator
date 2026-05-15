# ASR Serving Pipeline — Spec Kit Implementation

Production-oriented v1 ASR serving pipeline built with Spec Kit's spec-first philosophy.

**Formal spec**: `.specify/asr-pipeline-spec.md`

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Or with Docker:
```bash
docker compose up --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /healthz | Health check → `{"status":"ok"}` |
| GET | /metrics | Prometheus metrics (text/plain) |
| POST | /transcribe | Transcribe audio file (multipart) |
| POST | /eval/cer | CER evaluation (JSON body) |

## Run Tests

```bash
pytest tests/ -v
```

## Batch CER Evaluation

```bash
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl
```

## Architecture

See `docs/architecture.md` for full component diagram and data flows.

## Key Design Decisions (Spec-First)

1. **Spec before code**: All contracts, component boundaries, and edge cases are defined in `.specify/asr-pipeline-spec.md` before any implementation.
2. **Backend abstraction** (`ASRBackend` ABC): The API layer never depends on a specific ASR engine — `MockASRBackend` is the only v1 backend.
3. **CER as first-class feature**: `/eval/cer` endpoint and `cer_runner` CLI are both implemented, not bolted on.
4. **Observability by default**: Every log line includes `request_id`; Prometheus metrics are updated on every request.

## Configuration

| Env Var | Default | Description |
|---------|---------|-------------|
| `ASR_LOG_LEVEL` | `INFO` | Log verbosity |
| `ASR_BACKEND` | `mock` | Backend type |
| `ASR_MOCK_TRANSCRIPT` | `안녕하세요 테스트 음성입니다` | Mock output text |
| `ASR_MOCK_CONFIDENCE` | `0.98` | Mock confidence score |
| `ASR_TARGET_SAMPLE_RATE` | `16000` | Audio resample target (Hz) |
