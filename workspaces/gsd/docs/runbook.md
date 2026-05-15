# Runbook

## Local development

```bash
# 1. Create virtualenv
python -m venv .venv && source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start server
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# 4. Verify
curl http://localhost:8000/healthz
# → {"status":"ok"}

curl http://localhost:8000/metrics
# → Prometheus text

curl -X POST http://localhost:8000/transcribe \
  -F "file=@/path/to/audio.wav"
# → {"request_id":"req_...","transcript":"..."}
```

## Docker

```bash
docker compose up --build
# Service available at http://localhost:8000
```

## Run tests

```bash
pytest tests/ -v
# or specific suite:
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/eval/ -v
```

## CER batch evaluation

```bash
# Using HTTP endpoint
curl -X POST http://localhost:8000/eval/cer \
  -H "Content-Type: application/json" \
  -d @pairs.json

# Using CLI
python -m src.eval.cer_runner --manifest data/manifest.jsonl
python -m src.eval.cer_runner --manifest data/manifest.jsonl --output report.json
```

## Configuration

| Env var | Default | Description |
|---------|---------|-------------|
| `ASR_BACKEND` | `mock` | Backend to use |
| `HOST` | `0.0.0.0` | Bind address |
| `PORT` | `8000` | HTTP port |
| `LOG_LEVEL` | `INFO` | DEBUG / INFO / WARNING / ERROR |

## Troubleshooting

### "Could not decode audio"
- Ensure file is a valid audio format (WAV, FLAC, OGG)
- The service requires `libsndfile` system library (installed in Dockerfile)

### ImportError on soundfile
- Install system library: `apt-get install -y libsndfile1` (Linux)
- On macOS: `brew install libsndfile`

### Prometheus metrics not updating
- Metrics are process-local; they reset on restart
- The `/metrics` endpoint uses the default global registry

## Health check

```bash
curl -f http://localhost:8000/healthz || echo "UNHEALTHY"
```

Expected: HTTP 200, body `{"status":"ok"}`
