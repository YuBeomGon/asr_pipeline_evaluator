# ASR Serving Pipeline (GSD)

Production-oriented v1 ASR serving pipeline scaffold. Built using the GSD (Get Shit Done) approach: concrete tasks, working code, no ceremony.

## Quick start

```bash
# Install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Run the API server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Run tests
pytest tests/ -v

# Docker
docker compose up --build
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /healthz | Health check |
| GET | /metrics | Prometheus metrics |
| POST | /transcribe | Transcribe audio file |
| POST | /eval/cer | Compute CER for text pairs |

## CER CLI

```bash
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl --output report.json
```

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ASR_BACKEND` | `mock` | Backend name (`mock`) |
| `HOST` | `0.0.0.0` | Bind host |
| `PORT` | `8000` | Bind port |
| `LOG_LEVEL` | `INFO` | Logging level |

## Architecture

See `docs/architecture.md` for full design. Short version:
- FastAPI handles HTTP, request IDs, structured logging
- `ASRBackend` ABC allows swapping mock → real model
- Audio preprocessor resamples to 16kHz mono
- CER evaluator uses char-level edit distance with Unicode NFKC normalization
- Prometheus metrics exposed at `/metrics`

## Known limitations (v1 scope)

- No real ASR model (mock backend only)
- No authentication / rate limiting
- No horizontal scaling / queue
- No diarization
