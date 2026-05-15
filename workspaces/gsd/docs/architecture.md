# Architecture

## Overview

The ASR serving pipeline is a FastAPI application with a clean layered structure:

```
HTTP Client
    │
    ▼
FastAPI (src/api/main.py)
    │  ┌─ GET /healthz
    │  ├─ GET /metrics
    │  ├─ POST /transcribe ─────────────────────┐
    │  └─ POST /eval/cer                        │
    │                                           ▼
    │                              Audio Preprocessor
    │                              (src/audio/processor.py)
    │                              resample → 16 kHz mono
    │                                           │
    │                                           ▼
    │                              ASRBackend (ABC)
    │                              ├─ MockASRBackend (default)
    │                              └─ [future: WhisperBackend, etc.]
    │                                           │
    │                                           ▼
    │                              Postprocessor (normalizer.py)
    │                              NFC, strip whitespace
    │
    ├─ Metrics (src/observability/metrics.py)
    │  prometheus_client counters/histograms
    │
    └─ Logging (src/observability/logging.py)
       JSON-structured, request_id in every line
```

## Key design decisions

### Backend abstraction
`ASRBackend` is an ABC with a single method `transcribe(audio: ndarray, sr: int) -> TranscriptResult`. Adding a new backend (e.g., Whisper) requires only implementing this interface — no API changes needed.

### Audio preprocessing
All audio is resampled to 16 kHz mono before inference. This is done in `src/audio/processor.py` using `soundfile` + `librosa`. Duration is computed from the resampled array length.

### Request IDs
Every `/transcribe` call gets a `req_<uuid4>` string, returned in the response and injected into all log lines for that request.

### CER evaluation
Two paths to CER:
1. **HTTP endpoint** `POST /eval/cer` — for online eval or testing
2. **CLI** `python -m src.eval.cer_runner --manifest <file>` — for batch eval from JSONL

Both use the same `compute_cer` / `aggregate_cer` functions.

### Prometheus metrics
`asr_requests_total{status}`, `asr_request_duration_seconds`, `asr_errors_total` are registered at module import time in `src/observability/metrics.py`.

## Configuration
All tunables are in `src/config/settings.py` (pydantic-settings), read from env vars or `.env` file.
