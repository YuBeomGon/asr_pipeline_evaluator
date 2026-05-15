# Architecture: ASR Serving Pipeline v1

**BMAD Phase**: Architect  
**Agent**: Winston (System Architect)  
**Date**: 2026-05-15  
**Status**: Approved

---

## 1. Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                        FastAPI App                           │
│  ┌──────────┐  ┌─────────────┐  ┌──────────────────────┐    │
│  │ /healthz │  │ /transcribe │  │     /eval/cer        │    │
│  └──────────┘  └──────┬──────┘  └──────────┬───────────┘    │
│                        │                    │                │
│         ┌──────────────▼──────┐  ┌─────────▼──────────┐     │
│         │  AudioPreprocessor  │  │   CERCalculator    │     │
│         │  (src/audio/)       │  │   (src/eval/)      │     │
│         └──────────┬──────────┘  └────────────────────┘     │
│                    │                                         │
│         ┌──────────▼──────────┐                             │
│         │    ASRBackend       │  ← abstract interface       │
│         │  (src/backends/)    │                             │
│         │  MockASRBackend     │  ← default implementation   │
│         └─────────────────────┘                             │
│                                                              │
│  ┌─────────────────────────────────────────────────────┐    │
│  │            Observability Layer                       │    │
│  │  PrometheusMiddleware | StructuredLogger | RequestID │    │
│  └─────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## 2. Module Boundaries

| Module | Path | Responsibility |
|--------|------|---------------|
| API layer | `src/api/` | Route definitions, request/response models, FastAPI app factory |
| Audio | `src/audio/` | Resample, mono conversion, duration, byte-to-numpy |
| Backends | `src/backends/` | `ASRBackend` ABC, `MockASRBackend`, backend registry/factory |
| Eval | `src/eval/` | CER calculation, normalization pipeline, CLI runner, manifest I/O |
| Observability | `src/observability/` | Prometheus metrics registry, structured logger factory |
| Config | `src/config/` | Pydantic Settings, environment variable bindings |

---

## 3. Data Flow: POST /transcribe

```
Client
  │ multipart/form-data (audio file)
  ▼
FastAPI route (src/api/routes/transcribe.py)
  │  generate request_id = "req_" + uuid4
  │  log: request received
  ▼
AudioPreprocessor.preprocess(audio_bytes)
  │  → numpy array (16kHz mono) + audio_duration_seconds
  │  → time: preprocess_ms
  ▼
ASRBackend.transcribe(audio_array, sample_rate=16000)
  │  → TranscriptResult(text, confidence)
  │  → time: inference_ms
  ▼
Postprocessor.normalize(text)
  │  → NFC normalized, punctuation-cleaned text
  │  → time: postprocess_ms
  ▼
PrometheusMiddleware
  │  → increment asr_requests_total{status="success"}
  │  → observe asr_request_duration_seconds
  ▼
JSON response → Client
```

---

## 4. Data Flow: POST /eval/cer

```
Client
  │ JSON {"pairs": [{"id":"...","reference":"...","hypothesis":"..."}]}
  ▼
FastAPI route (src/api/routes/eval.py)
  ▼
CERCalculator.compute_batch(pairs)
  │  per pair:
  │    normalize(reference)  → NFKC → lower → collapse_ws → strip_spaces
  │    normalize(hypothesis) → same
  │    levenshtein_chars(ref_chars, hyp_chars) → S, D, I
  │    CER = (S+D+I) / len(ref_chars) if len(ref_chars) > 0 else 0.0
  │  aggregate: mean CER, total chars, total errors
  ▼
JSON response → Client
```

---

## 5. Backend Abstraction Design

```python
# src/backends/base.py
class TranscriptResult(BaseModel):
    text: str
    confidence: float
    backend: str
    name: str
    version: str

class ASRBackend(ABC):
    @abstractmethod
    def transcribe(self, audio: np.ndarray, sample_rate: int) -> TranscriptResult: ...
    
    @abstractmethod
    def health(self) -> bool: ...
```

Backends are registered by name in `src/backends/registry.py`. The active backend is selected via `SETTINGS.asr_backend` (env var `ASR_BACKEND`, default `"mock"`).

---

## 6. CER Normalization Pipeline

```
input string
  ↓ unicodedata.normalize("NFKC", s)
  ↓ .lower()
  ↓ re.sub(r'\s+', ' ', s).strip()
  ↓ s.replace(' ', '')           ← remove all spaces before char-level diff
  → normalized char sequence
```

Korean-specific: Korean characters survive NFKC normalization correctly. NFC is used for final transcript output. NFKC is used only for CER normalization (handles compatibility chars, half-width/full-width variants).

---

## 7. Observability Design

### Metrics (Prometheus)
```
asr_requests_total{status="success"|"error"}   Counter
asr_request_duration_seconds                    Histogram (buckets: .005,.01,.025,.05,.1,.25,.5,1,2.5,5)
asr_errors_total                                Counter
```

### Structured Logging
- JSON lines format
- Fields: `timestamp`, `level`, `request_id`, `message`, `module`
- Every log line in a request context includes `request_id`

---

## 8. Tech Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Web framework | FastAPI | Async, auto OpenAPI, wide adoption |
| Audio I/O | soundfile + scipy.signal | Lightweight, no heavy deps, handles WAV/FLAC/OGG |
| Metrics | prometheus_client | Standard library, zero-config text exposition |
| CER distance | Manual Levenshtein OR editdistance | editdistance if available, else pure Python fallback |
| Settings | Pydantic BaseSettings | Env-var binding, validation, no secrets in code |
| Tests | pytest + httpx.AsyncClient | Fast, no server startup, async-native |
| Container | python:3.11-slim | Small image, deterministic |

---

## 9. Configuration

All runtime config via environment variables (`.env` file for local dev):

```
ASR_BACKEND=mock          # backend to use: mock | whisper | azure | google
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
MOCK_TRANSCRIPT=          # optional fixed text for MockASRBackend
```

---

## 10. File Tree

```
workspaces/bmad/
├── _bmad/                    # BMAD config (read-only)
├── docs/
│   ├── pm-brief.md
│   ├── architecture.md
│   ├── api.md
│   ├── eval_protocol.md
│   ├── implementation_scope.md
│   ├── runbook.md
│   └── qa-checklist.md
├── src/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py           # FastAPI app factory
│   │   ├── models.py         # Pydantic request/response schemas
│   │   └── routes/
│   │       ├── __init__.py
│   │       ├── health.py
│   │       ├── transcribe.py
│   │       └── eval.py
│   ├── audio/
│   │   ├── __init__.py
│   │   └── preprocessor.py
│   ├── backends/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── mock.py
│   │   └── registry.py
│   ├── eval/
│   │   ├── __init__.py
│   │   ├── cer.py
│   │   └── cer_runner.py
│   ├── observability/
│   │   ├── __init__.py
│   │   ├── metrics.py
│   │   └── logging.py
│   └── config/
│       ├── __init__.py
│       └── settings.py
├── tests/
│   ├── conftest.py
│   ├── unit/
│   │   ├── test_cer.py
│   │   └── test_normalization.py
│   ├── integration/
│   │   ├── test_health.py
│   │   ├── test_transcribe.py
│   │   └── test_metrics.py
│   └── eval/
│       └── test_eval_smoke.py
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```
