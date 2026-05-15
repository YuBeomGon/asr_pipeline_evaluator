# Architecture

## Overview

This is an **OpenSpec-driven** ASR (Automatic Speech Recognition) serving pipeline.
The API contract is defined first in `openapi.yaml` (OpenAPI 3.1), and the FastAPI
implementation is derived from that specification.

## Design Principles

1. **API-first**: `openapi.yaml` is the single source of truth for all endpoints,
   request/response schemas, and content types.
2. **Backend abstraction**: `ASRBackend` is an abstract interface; swapping to
   Whisper, NeMo, or any real model requires only a new implementation class.
3. **Observable by default**: every request gets a `request_id`, structured JSON
   logs include `request_id`, and Prometheus metrics are emitted for every operation.
4. **No external dependencies at runtime**: `MockASRBackend` satisfies all API
   contracts with zero GPU or network requirements.

## Directory Structure

```
openspec/
├── openapi.yaml             # OpenAPI 3.1 spec (authoritative contract)
├── src/
│   ├── api/
│   │   ├── main.py          # FastAPI app creation + lifespan
│   │   ├── schemas.py       # Pydantic request/response models (mirror openapi.yaml)
│   │   ├── postprocessing.py # Transcript NFC normalization
│   │   └── routes/
│   │       ├── health.py    # GET /healthz
│   │       ├── metrics.py   # GET /metrics
│   │       ├── transcribe.py # POST /transcribe
│   │       └── eval_cer.py  # POST /eval/cer
│   ├── audio/
│   │   └── preprocessing.py # Load + resample audio to 16kHz mono float32
│   ├── backends/
│   │   ├── base.py          # ASRBackend ABC + TranscriptResult dataclass
│   │   ├── mock.py          # MockASRBackend (deterministic, no GPU)
│   │   └── registry.py      # Backend factory + singleton cache
│   ├── eval/
│   │   ├── cer.py           # CER algorithm + normalization pipeline
│   │   └── cer_runner.py    # CLI for batch CER from JSONL manifest
│   ├── observability/
│   │   ├── logging.py       # Structured JSON logging + request_id context
│   │   └── metrics.py       # Prometheus counters/histograms
│   └── config/
│       └── settings.py      # Pydantic Settings from env vars
├── tests/
│   ├── unit/                # CER, audio, backend unit tests
│   ├── integration/         # API endpoint tests via TestClient
│   └── eval/                # CER runner + manifest smoke tests
└── docs/
    ├── architecture.md      # This file
    ├── api.md               # API endpoint reference
    ├── eval_protocol.md     # CER protocol
    ├── implementation_scope.md
    └── runbook.md
```

## Request Flow: POST /transcribe

```
Client
  │
  ▼
POST /transcribe (multipart: file=<audio>)
  │
  ├─ Generate request_id = "req_<UUID4>"
  ├─ Inject request_id into logging context (contextvars)
  │
  ▼
AudioPreprocessor.preprocess(audio_bytes)
  ├─ soundfile.read() → float32 numpy array
  ├─ Stereo → mono (mean channels)
  └─ Resample to 16kHz (linear interpolation)
  │
  ▼
ASRBackend.transcribe(audio, sample_rate=16000)
  └─ MockASRBackend returns deterministic transcript + metadata
  │
  ▼
postprocess_transcript(raw)
  ├─ NFC normalization (Korean jamo composition)
  ├─ Strip + collapse whitespace
  └─ Remove spaces before punctuation
  │
  ▼
TranscribeResponse (JSON) + Prometheus metrics update
```

## CER Evaluation Flow

```
POST /eval/cer  OR  python -m src.eval.cer_runner --manifest path.jsonl
  │
  ▼
For each (id, reference, hypothesis):
  ├─ normalize_for_cer(reference): NFKC → lower → strip → no-spaces
  ├─ normalize_for_cer(hypothesis): same
  └─ Levenshtein edit distance → (S, D, I)
       CER = (S + D + I) / len(norm_ref)
  │
  ▼
CERAggregate: mean_cer, total S/D/I, total ref chars, total samples
```

## Backend Extension

To add a real ASR backend (e.g. OpenAI Whisper):

1. Create `src/backends/whisper.py` implementing `ASRBackend`.
2. Register it in `src/backends/registry.py`:
   ```python
   _REGISTRY["whisper"] = _make_whisper
   ```
3. Set `ASR_BACKEND=whisper` environment variable.

No changes to the API layer are required.

## Observability

### Logging
- Format: JSON lines (stdout), configurable via `ASR_LOG_FORMAT=text` for development.
- Every log record includes `request_id` when inside a request context.
- Log level: `ASR_LOG_LEVEL=INFO` (default).

### Metrics (Prometheus)
- `asr_requests_total{status="success|error"}` — counter
- `asr_request_duration_seconds` — histogram (end-to-end)
- `asr_errors_total` — counter
- `asr_audio_duration_seconds` — histogram
- `asr_inference_duration_seconds` — histogram

Exposed at `GET /metrics` in Prometheus text exposition format.
