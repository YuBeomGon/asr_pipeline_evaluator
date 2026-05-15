# OpenSpec ASR Serving Pipeline

A production-oriented v1 ASR (Automatic Speech Recognition) serving pipeline
built following OpenSpec's **API-first** philosophy:

1. Write the OpenAPI 3.1 specification (`openapi.yaml`) first.
2. Implement the FastAPI server that matches the spec exactly.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000

# Run tests
pytest tests/

# Batch CER evaluation
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/healthz` | Health check → `{"status": "ok"}` |
| GET | `/metrics` | Prometheus metrics |
| POST | `/transcribe` | Upload audio, get transcript |
| POST | `/eval/cer` | Compute CER for ref/hyp pairs |

Interactive docs: http://localhost:8000/docs

## Architecture

- **OpenAPI spec**: `openapi.yaml` (authoritative contract)
- **FastAPI app**: `src/api/main.py`
- **ASR backend**: `src/backends/` (abstract + mock)
- **Audio preprocessing**: `src/audio/preprocessing.py`
- **CER evaluator**: `src/eval/cer.py`
- **Observability**: `src/observability/` (Prometheus + structured logging)

See `docs/architecture.md` for full details.

## Configuration

All settings via environment variables (prefix `ASR_`):

```bash
ASR_BACKEND=mock
ASR_LOG_LEVEL=INFO
ASR_LOG_FORMAT=json  # or 'text'
ASR_MOCK_TRANSCRIPT="안녕하세요 반갑습니다"
ASR_MOCK_CONFIDENCE=0.95
ASR_TARGET_SAMPLE_RATE=16000
```

## Docker

```bash
docker build -t openspec-asr .
docker run -p 8000:8000 openspec-asr

# or
docker compose up
```

## Testing

```bash
pytest tests/unit/          # CER logic, audio, backend
pytest tests/integration/   # API endpoint tests
pytest tests/eval/          # CER runner + manifest smoke tests
```

## CER Evaluation Protocol

```
CER = (S + D + I) / reference_character_count
```

Normalization: NFKC → lowercase → collapse whitespace → remove spaces

See `docs/eval_protocol.md` for full details.
