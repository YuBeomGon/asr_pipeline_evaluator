# ASR Serving Pipeline (BMAD Implementation)

A production-oriented v1 ASR serving pipeline scaffold built using the
**BMAD** (Business Manager And Developer) role-based, phase-driven methodology.

## BMAD Phases

| Phase | Artifact | Agent |
|-------|----------|-------|
| PM | `docs/pm-brief.md` | John (Product Manager) |
| Architect | `docs/architecture.md`, `docs/api.md` | Winston (Architect) |
| Developer | `src/`, tests | Amelia (Developer) |
| QA | `docs/qa-checklist.md` | QA Lead |

## Quick Start

```bash
# Native (recommended for development)
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.api.main:app --host 0.0.0.0 --port 8000 --reload

# Docker
docker compose up --build
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/healthz` | Liveness check |
| `GET` | `/metrics` | Prometheus metrics |
| `POST` | `/transcribe` | Transcribe audio file |
| `POST` | `/eval/cer` | Compute CER batch |

## Running Tests

```bash
pytest tests/ -v
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/eval/ -v
```

## CER Evaluation CLI

```bash
python -m src.eval.cer_runner --manifest tests/fixtures/manifest.jsonl
```

## Configuration

Set environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `ASR_BACKEND` | `mock` | Backend: mock, whisper, azure, google |
| `LOG_LEVEL` | `INFO` | Logging level |
| `MOCK_TRANSCRIPT` | (Korean default) | Fixed text for mock backend |
| `MOCK_CONFIDENCE` | `0.98` | Mock confidence score |

## Architecture

See `docs/architecture.md` for full component diagram and data flow.

## Korean Language Support

- CER evaluation uses NFKC normalization + space removal
- Transcript output uses NFC normalization
- Korean Hangul characters are preserved correctly through all normalization steps

## Extending with Real Backends

1. Implement `ASRBackend` in `src/backends/yourbackend.py`
2. Register it in `src/backends/registry.py`
3. Set `ASR_BACKEND=yourbackend` environment variable

No route changes required.
