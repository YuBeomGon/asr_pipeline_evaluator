# Architecture: ASR Serving Pipeline (Spec Kit v1)

**Spec ref**: `.specify/asr-pipeline-spec.md § Component Boundaries`

## Overview

The ASR Serving Pipeline is a FastAPI-based HTTP service that exposes:
- Audio transcription via a clean backend abstraction
- CER (Character Error Rate) evaluation as a first-class endpoint
- Prometheus metrics and structured JSON logging for production observability

## Component Map

```
┌──────────────────────────────────────────────────────────────────┐
│                         FastAPI Application                      │
│  ┌─────────────┐  ┌──────────────┐  ┌────────────────────────┐  │
│  │  /healthz   │  │  /transcribe │  │     /eval/cer          │  │
│  └─────────────┘  └──────┬───────┘  └────────────┬───────────┘  │
│                           │                       │              │
│               ┌───────────▼──────────┐  ┌────────▼───────────┐  │
│               │  Audio Preprocessor  │  │   CER Evaluator    │  │
│               │  (16kHz mono resamp) │  │  (Levenshtein)     │  │
│               └───────────┬──────────┘  └────────────────────┘  │
│                           │                                      │
│               ┌───────────▼──────────┐                          │
│               │    ASRBackend ABC    │                          │
│               │  ┌────────────────┐  │                          │
│               │  │ MockASRBackend │  │                          │
│               │  └────────────────┘  │                          │
│               └──────────────────────┘                          │
│                                                                  │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │               Observability Layer                         │  │
│  │  Prometheus metrics  │  Structured JSON logger            │  │
│  └───────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────┘
```

## Module Responsibilities

| Module | Path | Responsibility |
|--------|------|---------------|
| API routes | `src/api/routes.py` | HTTP endpoint handlers, request orchestration |
| FastAPI app | `src/api/main.py` | Application factory, lifespan, backend wiring |
| Schemas | `src/api/schemas.py` | Pydantic request/response models |
| Audio preprocessing | `src/audio/preprocessing.py` | Decode → mono → 16 kHz resample → AudioChunk |
| Transcript postprocessing | `src/audio/postprocessing.py` | NFC normalize, whitespace collapse |
| ASRBackend ABC | `src/backends/base.py` | Abstract interface + data models |
| MockASRBackend | `src/backends/mock.py` | Deterministic mock, no GPU/network |
| CER logic | `src/eval/cer.py` | NFKC normalize + Levenshtein + CER formula |
| CER CLI | `src/eval/cer_runner.py` | JSONL manifest batch evaluation |
| Metrics | `src/observability/metrics.py` | Prometheus counters and histograms |
| Logging | `src/observability/logging.py` | Structured JSON logger + RequestLogger adapter |
| Settings | `src/config/settings.py` | Pydantic-settings env-driven configuration |

## Data Flow: POST /transcribe

```
Client
  │ multipart/form-data (file=<audio bytes>)
  ▼
routes.transcribe()
  │ generate request_id = "req_" + uuid4().hex
  │ read file bytes
  ▼
audio.preprocessing.preprocess_audio(bytes) → AudioChunk
  │ soundfile.read() → (samples, orig_sr)
  │ stereo → mono (mean across channels)
  │ resample to 16 kHz (scipy.signal.resample_poly)
  ▼
backends.MockASRBackend.transcribe(samples.tobytes(), sample_rate) → TranscriptResult
  │ deterministic mock transcript
  │ compute duration from float32 byte count
  ▼
audio.postprocessing.postprocess_transcript(transcript) → str
  │ NFC normalize
  │ whitespace collapse
  ▼
Prometheus metrics updated
  │ asr_requests_total{status="success"}.inc()
  │ asr_request_duration_seconds.observe(seconds)
  ▼
TranscribeResponse returned to client
```

## Backend Abstraction (NFR-005)

The `ASRBackend` abstract class ensures the API layer never depends on a specific ASR engine:

```python
class ASRBackend(ABC):
    @abstractmethod
    def transcribe(self, audio_bytes: bytes, sample_rate: int) -> TranscriptResult: ...
```

To add a real backend (e.g., Whisper, wav2vec2):
1. Subclass `ASRBackend` in `src/backends/`
2. Set `ASR_BACKEND=whisper` in environment
3. Wire it in `src/api/main.py` lifespan

## CER Evaluation

CER is computed via Levenshtein edit distance at character level after normalization:

```
CER = (S + D + I) / N
```

Normalization pipeline:
1. NFKC Unicode normalization (Korean jamo compatibility)
2. Lowercase
3. Trim + collapse whitespace
4. Remove all spaces (character-level alignment)

## Configuration

All settings are in `src/config/settings.py` and environment-prefixed with `ASR_`:

| Env Var | Default | Description |
|---------|---------|-------------|
| `ASR_HOST` | `0.0.0.0` | Bind host |
| `ASR_PORT` | `8000` | Bind port |
| `ASR_LOG_LEVEL` | `INFO` | Log level |
| `ASR_BACKEND` | `mock` | Backend type |
| `ASR_MOCK_TRANSCRIPT` | `안녕하세요 테스트 음성입니다` | Mock output |
| `ASR_MOCK_CONFIDENCE` | `0.98` | Mock confidence |
| `ASR_TARGET_SAMPLE_RATE` | `16000` | Audio resample target |
