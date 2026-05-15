# Runbook: ASR Serving Pipeline

**Spec ref**: `.specify/asr-pipeline-spec.md § NFR-001`

## Prerequisites

- Python 3.11+
- pip

## Local Setup (without Docker)

```bash
cd /path/to/workspaces/spec-kit

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

## Local Setup (with Docker)

```bash
cd /path/to/workspaces/spec-kit

# Build and start
docker compose up --build

# Stop
docker compose down
```

## Run Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Eval smoke tests only
pytest tests/eval/ -v
```

## Verify API

```bash
# Health check
curl http://localhost:8000/healthz

# Metrics
curl http://localhost:8000/metrics

# Transcribe a WAV file
curl -X POST http://localhost:8000/transcribe \
  -F "file=@/path/to/audio.wav"

# CER evaluation
curl -X POST http://localhost:8000/eval/cer \
  -H "Content-Type: application/json" \
  -d '{
    "pairs": [
      {"id": "s1", "reference": "안녕하세요", "hypothesis": "안녕하세요"}
    ]
  }'
```

## Batch CER Evaluation

```bash
# Run against a JSONL manifest
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl

# Save results to file
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl --output results.json
```

## Configuration

Set environment variables (all prefixed with `ASR_`):

```bash
export ASR_LOG_LEVEL=DEBUG
export ASR_MOCK_TRANSCRIPT="custom transcript"
export ASR_MOCK_CONFIDENCE=0.95
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

Or use a `.env` file:
```
ASR_LOG_LEVEL=DEBUG
ASR_MOCK_TRANSCRIPT=custom transcript
```

## Monitoring

- Metrics: `GET /metrics` returns Prometheus text format
- Health: `GET /healthz` returns `{"status":"ok"}`
- Logs: structured JSON to stdout, one line per event

### Key Metrics

| Metric | Alert Threshold |
|--------|----------------|
| `asr_requests_total{status="error"}` | > 5% of total |
| `asr_request_duration_seconds_p99` | > 5 seconds |
| `asr_errors_total` (rate) | > 0.1/sec sustained |

## Troubleshooting

### Service won't start
- Check Python 3.11+ is installed: `python3 --version`
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check port 8000 is not in use: `lsof -i :8000`

### 422 on /transcribe
- Check that the audio file is a valid format (WAV, FLAC, OGG)
- Check that the file is not empty
- Check logs for detailed error message

### CER results unexpected
- Verify normalization: run `python -c "from src.eval.cer import normalize_for_cer; print(normalize_for_cer('your text'))"`
- Ensure hypothesis and reference are not swapped

## Adding a Real ASR Backend

1. Create `src/backends/<name>.py` subclassing `ASRBackend`
2. Implement `transcribe(audio_bytes, sample_rate) -> TranscriptResult`
3. Wire it in `src/api/main.py` lifespan by checking `settings.backend`
4. Set `ASR_BACKEND=<name>` in environment
