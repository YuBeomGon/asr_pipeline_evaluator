# Runbook

## Local Development

### Prerequisites
- Python 3.11+
- `libsndfile1` (for soundfile): `sudo apt-get install libsndfile1`

### Setup

```bash
cd workspaces/openspec

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Run the server

```bash
# Development (auto-reload)
ASR_DEBUG=true uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

# Production-like
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### Test the API

```bash
# Health check
curl http://localhost:8000/healthz

# Metrics
curl http://localhost:8000/metrics

# Transcribe (requires a WAV file)
curl -X POST http://localhost:8000/transcribe \
  -F "file=@/path/to/audio.wav"

# CER evaluation
curl -X POST http://localhost:8000/eval/cer \
  -H "Content-Type: application/json" \
  -d '{
    "pairs": [
      {
        "id": "s1",
        "reference": "안녕하세요 반갑습니다",
        "hypothesis": "안녕하세요 반갑습니다"
      }
    ]
  }'
```

### Run tests

```bash
# All tests
pytest tests/

# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Eval smoke tests
pytest tests/eval/ -v

# With coverage
pip install pytest-cov
pytest tests/ --cov=src --cov-report=term-missing
```

### Batch CER evaluation from manifest

```bash
# Run CER evaluation from a JSONL manifest
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl

# With output file
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl --output results.json
```

### Interactive API docs

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

## Docker

### Build and run

```bash
# Build image
docker build -t openspec-asr:latest .

# Run container
docker run -p 8000:8000 openspec-asr:latest

# With docker-compose
docker compose up
```

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ASR_BACKEND` | `mock` | ASR backend (`mock` only in v1) |
| `ASR_LOG_LEVEL` | `INFO` | Log level |
| `ASR_LOG_FORMAT` | `json` | `json` or `text` |
| `ASR_DEBUG` | `false` | Enable debug mode + CORS |
| `ASR_MOCK_TRANSCRIPT` | `안녕하세요 반갑습니다` | Mock transcript |
| `ASR_MOCK_CONFIDENCE` | `0.95` | Mock confidence score |
| `ASR_MOCK_INFERENCE_DELAY_MS` | `10.0` | Simulated inference latency |
| `ASR_TARGET_SAMPLE_RATE` | `16000` | Audio resample target (Hz) |
| `ASR_MAX_AUDIO_BYTES` | `52428800` | Max upload size (50 MB) |

## Troubleshooting

### `soundfile.LibsndfileError: Error opening...`
The audio file is corrupt or in an unsupported format.
Supported formats: WAV, FLAC, OGG, AIFF, AU.
MP3 is not supported by soundfile without additional plugins.

### `libsndfile` not found
Install the system library:
```bash
# Ubuntu/Debian
sudo apt-get install libsndfile1
# macOS
brew install libsndfile
```

### Port 8000 already in use
```bash
# Find and kill the process
lsof -i :8000 | grep LISTEN
kill -9 <PID>
```

### Tests fail with import errors
Ensure you're running pytest from the project root (`workspaces/openspec/`)
with the virtual environment activated:
```bash
cd workspaces/openspec
source .venv/bin/activate
pytest tests/
```
