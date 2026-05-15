# Runbook: ASR Serving Pipeline v1

**BMAD Phase**: Architect / Developer  
**Date**: 2026-05-15

---

## 1. Local Development

### Prerequisites
- Python 3.11+
- Docker + Docker Compose (optional, for container run)

### Quick Start (native)

```bash
cd workspaces/bmad

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
# .venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Start the service
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Verify
curl http://localhost:8000/healthz
```

### Quick Start (Docker)

```bash
cd workspaces/bmad

docker compose up --build

# Verify
curl http://localhost:8000/healthz
```

---

## 2. Running Tests

```bash
# All tests
pytest tests/ -v

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Eval smoke tests
pytest tests/eval/ -v

# With coverage
pytest tests/ --cov=src --cov-report=term-missing
```

---

## 3. API Usage Examples

### Health Check
```bash
curl http://localhost:8000/healthz
# {"status":"ok"}
```

### Transcribe Audio
```bash
curl -X POST http://localhost:8000/transcribe \
  -F "file=@sample.wav"
```

### CER Evaluation (HTTP)
```bash
curl -X POST http://localhost:8000/eval/cer \
  -H "Content-Type: application/json" \
  -d '{
    "pairs": [
      {"id": "s1", "reference": "안녕하세요", "hypothesis": "안녕하세요"},
      {"id": "s2", "reference": "테스트", "hypothesis": "텍스트"}
    ]
  }'
```

### CER Evaluation (CLI)
```bash
python -m src.eval.cer_runner \
  --manifest tests/fixtures/manifest.jsonl

# With output file
python -m src.eval.cer_runner \
  --manifest tests/fixtures/manifest.jsonl \
  --output results.jsonl
```

---

## 4. Metrics

Prometheus scrape target: `http://localhost:8000/metrics`

Key metrics:
| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `asr_requests_total` | Counter | `status` | Total transcription requests |
| `asr_request_duration_seconds` | Histogram | — | End-to-end request duration |
| `asr_errors_total` | Counter | — | Total errors |

---

## 5. Switching ASR Backends

Set `ASR_BACKEND` environment variable:

```bash
# Mock (default, no GPU needed)
ASR_BACKEND=mock uvicorn src.api.main:app ...

# Future: Whisper local (requires GPU + whisper package)
ASR_BACKEND=whisper uvicorn src.api.main:app ...

# Future: Azure Cognitive Services
ASR_BACKEND=azure AZURE_SPEECH_KEY=... uvicorn src.api.main:app ...
```

---

## 6. Configuration Reference

| Env Var | Default | Description |
|---------|---------|-------------|
| `ASR_BACKEND` | `mock` | Backend name (mock, whisper, azure, google) |
| `LOG_LEVEL` | `INFO` | Logging level |
| `HOST` | `0.0.0.0` | Bind host |
| `PORT` | `8000` | Bind port |
| `MOCK_TRANSCRIPT` | `""` | Fixed text for MockASRBackend (empty = use default) |

---

## 7. Troubleshooting

### Service won't start
- Check Python version: `python --version` (must be 3.11+)
- Check requirements installed: `pip list | grep fastapi`
- Check port not in use: `lsof -i :8000`

### Tests fail with import errors
- Ensure you're in the `workspaces/bmad/` directory
- Ensure `PYTHONPATH` includes project root: `export PYTHONPATH=.`

### CER results seem wrong
- Verify normalization: run `python -c "from src.eval.cer import normalize; print(normalize('your text'))"` 
- Check manifest JSONL format (one JSON object per line, no trailing commas)

### Metrics not showing
- Verify Prometheus client is installed: `pip show prometheus_client`
- Check Content-Type header: should be `text/plain; version=0.0.4`
