# Feature Specification: ASR Serving Pipeline v1

**Feature Branch**: `001-asr-serving-pipeline`

**Created**: 2026-05-15

**Status**: Approved

**Input**: Production-oriented v1 ASR serving pipeline with CER evaluation, mock ASR backend, Prometheus metrics, structured logging, and JSONL manifest support for Korean speech recognition.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Audio Transcription via REST API (Priority: P1)

An operator submits an audio file to the `/transcribe` endpoint and receives a structured JSON response with the transcribed text, confidence score, timing breakdown, and model metadata.

**Why this priority**: Core product capability — without transcription nothing else delivers value.

**Independent Test**: POST a WAV file to `/transcribe`, confirm the response schema matches the contract and `request_id` starts with `req_`.

**Acceptance Scenarios**:

1. **Given** a valid 16 kHz mono WAV file, **When** a client POSTs to `/transcribe` with `multipart/form-data`, **Then** the server responds 200 with `request_id`, `transcript`, `confidence`, `audio_duration_seconds`, `timing`, and `model` fields present and correctly typed.
2. **Given** an audio file of a format other than WAV, **When** a client POSTs to `/transcribe`, **Then** the server responds 422 with a descriptive error message and an `asr_errors_total` counter increment.
3. **Given** the service is under load, **When** multiple simultaneous requests arrive, **Then** each response carries a unique `request_id`.

---

### User Story 2 - Health Check (Priority: P1)

An orchestration layer (Kubernetes, load balancer) probes `/healthz` to determine service readiness.

**Why this priority**: Without a health check, the service cannot participate in any production environment.

**Independent Test**: GET `/healthz`, confirm 200 and `{"status":"ok"}`.

**Acceptance Scenarios**:

1. **Given** the service is running, **When** an orchestrator GETs `/healthz`, **Then** the server responds 200 with `{"status":"ok"}`.

---

### User Story 3 - Prometheus Metrics Scraping (Priority: P2)

A Prometheus server scrapes `/metrics` to ingest counters and histograms about request rates, latencies, and errors.

**Why this priority**: Essential for production observability without which SLO alerting is impossible.

**Independent Test**: GET `/metrics`, confirm `text/plain; version=0.0.4` Content-Type and presence of `asr_requests_total`, `asr_request_duration_seconds`, `asr_errors_total`.

**Acceptance Scenarios**:

1. **Given** at least one transcription request was processed, **When** Prometheus scrapes `/metrics`, **Then** `asr_requests_total{status="success"}` is non-zero and `asr_request_duration_seconds_bucket` lines are present.
2. **Given** a failed request, **When** Prometheus scrapes `/metrics`, **Then** `asr_errors_total` is incremented.

---

### User Story 4 - CER Evaluation via API (Priority: P2)

A QA engineer submits reference/hypothesis text pairs to `/eval/cer` and receives per-sample and aggregate CER scores.

**Why this priority**: CER evaluation is a first-class feature of the pipeline, not an afterthought.

**Independent Test**: POST `{"pairs": [{"id": "s1", "reference": "안녕하세요", "hypothesis": "안녕하세요"}]}` to `/eval/cer`, confirm `overall_cer` is `0.0`.

**Acceptance Scenarios**:

1. **Given** a perfect hypothesis equal to the reference, **When** POST to `/eval/cer`, **Then** `overall_cer` is `0.0` and the per-sample CER is `0.0`.
2. **Given** an empty reference string, **When** POST to `/eval/cer`, **Then** the per-sample CER is `null` (or the result explicitly marks it undefined) and the aggregate excludes it.
3. **Given** Korean text with Unicode variation, **When** POST to `/eval/cer`, **Then** NFKC normalization is applied before scoring.

---

### User Story 5 - CER Batch Evaluation via CLI (Priority: P2)

A researcher runs CER evaluation in batch against a JSONL manifest file offline, without the HTTP server running.

**Why this priority**: Allows reproducible offline evaluation of large test sets.

**Independent Test**: `python -m src.eval.cer_runner --manifest manifest.jsonl` exits 0 and prints a JSON summary with `overall_cer`.

**Acceptance Scenarios**:

1. **Given** a valid JSONL manifest, **When** `python -m src.eval.cer_runner --manifest <path>` is run, **Then** the CLI exits 0 and prints `overall_cer` to stdout.
2. **Given** a manifest with some empty references, **When** the CLI runs, **Then** those samples are skipped and a warning is emitted.

---

### Edge Cases

- What happens when the uploaded file is 0 bytes? → Return 422 with `"error": "Empty audio file"`.
- What happens when the hypothesis is empty but reference is non-empty? → CER = 1.0 (all characters deleted).
- What happens when the reference is empty? → CER is undefined; return `null` for that sample.
- How does the system handle non-audio MIME types submitted to `/transcribe`? → Return 422 with descriptive message.
- How does the system handle Unicode normalization edge cases in Korean (e.g., composed vs. decomposed jamo)? → Apply NFKC normalization before CER scoring.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST expose `GET /healthz` returning `{"status":"ok"}` with HTTP 200.
- **FR-002**: System MUST expose `GET /metrics` returning Prometheus text format with `asr_requests_total` (labels: status), `asr_request_duration_seconds` (histogram), and `asr_errors_total` counters.
- **FR-003**: System MUST expose `POST /transcribe` accepting `multipart/form-data` with a `file` field and returning the transcript response schema defined in the API Contract.
- **FR-004**: System MUST expose `POST /eval/cer` accepting JSON `{"pairs": [...]}` and returning per-sample and aggregate CER.
- **FR-005**: System MUST implement an `ASRBackend` abstract base class with method `transcribe(audio_bytes: bytes, sample_rate: int) -> TranscriptResult`.
- **FR-006**: System MUST implement `MockASRBackend` that returns a deterministic mock transcript without GPU or network calls.
- **FR-007**: System MUST preprocess audio to 16 kHz mono and compute audio duration in seconds.
- **FR-008**: System MUST assign each request a unique ID with prefix `req_` followed by a UUID4 hex.
- **FR-009**: System MUST include `request_id` in every structured log line.
- **FR-010**: System MUST implement CER as `(S + D + I) / N` where N is the reference character count, using Levenshtein edit distance at character level.
- **FR-011**: System MUST apply NFKC Unicode normalization, lowercase, and whitespace collapsing before CER character-level scoring. Spaces are removed before character-level alignment.
- **FR-012**: System MUST support JSONL manifest format with fields `id`, `audio`, `reference`, `hypothesis`.
- **FR-013**: System MUST provide a CLI entry point `python -m src.eval.cer_runner` with `--manifest` argument.
- **FR-014**: System MUST provide a `Dockerfile` and `docker-compose.yml` for containerized deployment.
- **FR-015**: System MUST provide pytest tests covering CER logic, normalization, API endpoints, and an eval smoke test.

### Non-Functional Requirements

- **NFR-001**: The service MUST start cleanly with `uvicorn src.api.main:app --host 0.0.0.0 --port 8000`.
- **NFR-002**: `MockASRBackend` MUST NOT require GPU, network, or any model weights.
- **NFR-003**: All log output MUST be structured JSON with at minimum `timestamp`, `level`, `request_id`, and `message` fields.
- **NFR-004**: CER computation MUST be correct for both ASCII and multi-byte Korean Unicode text.
- **NFR-005**: The system MUST NOT couple the API layer directly to any specific ASR engine — all ASR calls go through the `ASRBackend` interface.

### Key Entities

- **TranscriptResult**: `transcript: str`, `confidence: float`, `audio_duration_seconds: float`, `timing: TimingInfo`, `model: ModelInfo`
- **TimingInfo**: `preprocess_ms: float`, `inference_ms: float`, `postprocess_ms: float`, `total_ms: float`
- **ModelInfo**: `backend: str`, `name: str`, `version: str`
- **CERPair**: `id: str`, `reference: str`, `hypothesis: str`
- **CERSampleResult**: `id: str`, `cer: float | None`, `reference_chars: int`, `edits: int`
- **CERResponse**: `pairs: list[CERSampleResult]`, `overall_cer: float`, `total_reference_chars: int`, `total_edits: int`

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `GET /healthz` returns 200 and `{"status":"ok"}` within 50 ms on a cold-start container.
- **SC-002**: `GET /metrics` returns valid Prometheus text with all three required metric families after at least one transcription.
- **SC-003**: `POST /transcribe` with a valid WAV file returns 200 with all required schema fields within 500 ms using MockASRBackend.
- **SC-004**: `POST /eval/cer` with a perfect-match pair returns `overall_cer = 0.0`.
- **SC-005**: `python -m src.eval.cer_runner --manifest manifest.jsonl` exits 0 and prints `overall_cer` to stdout.
- **SC-006**: All pytest tests pass (`pytest tests/ -v` exits 0).
- **SC-007**: `docker build .` completes without errors.

---

## API Contract

### Endpoint: GET /healthz

**Response 200**:
```json
{"status": "ok"}
```

### Endpoint: GET /metrics

**Response 200** (Content-Type: `text/plain; version=0.0.4`):
Standard Prometheus exposition format. Required metric families:
- `asr_requests_total` — Counter, label `status` ∈ {`success`, `error`}
- `asr_request_duration_seconds` — Histogram, default buckets
- `asr_errors_total` — Counter

### Endpoint: POST /transcribe

**Request**: `multipart/form-data` with field `file` containing audio bytes.

**Response 200**:
```json
{
  "request_id": "req_<uuid4_hex>",
  "transcript": "<string>",
  "confidence": 0.98,
  "audio_duration_seconds": 2.35,
  "timing": {
    "preprocess_ms": 1.0,
    "inference_ms": 10.0,
    "postprocess_ms": 1.0,
    "total_ms": 12.0
  },
  "model": {
    "backend": "mock",
    "name": "mock-asr",
    "version": "0.1.0"
  }
}
```

**Response 422**: `{"detail": "<error message>"}` for invalid audio input.

### Endpoint: POST /eval/cer

**Request**:
```json
{
  "pairs": [
    {"id": "sample_001", "reference": "한국어 텍스트", "hypothesis": "한국어 텍스트"}
  ]
}
```

**Response 200**:
```json
{
  "pairs": [
    {
      "id": "sample_001",
      "cer": 0.0,
      "reference_chars": 7,
      "edits": 0
    }
  ],
  "overall_cer": 0.0,
  "total_reference_chars": 7,
  "total_edits": 0
}
```

---

## CER Evaluation Protocol

### Formula

```
CER = (S + D + I) / N
```
Where:
- S = number of character substitutions
- D = number of character deletions
- I = number of character insertions
- N = number of characters in the reference (after normalization)

### Normalization Pipeline (applied to both reference and hypothesis)

1. Apply Unicode NFKC normalization
2. Convert to lowercase
3. Trim leading/trailing whitespace; collapse internal whitespace to single space
4. Remove all spaces before character-level alignment

### Edge Cases

- If reference (after normalization) is empty: CER for that sample is `null`; exclude from aggregate.
- If hypothesis is empty and reference is non-empty: CER = 1.0 (all deletions).
- CER may exceed 1.0 if hypothesis has many insertions.

### JSONL Manifest Format

One JSON object per line:
```jsonl
{"id":"sample_001","audio":"audio/sample_001.wav","reference":"한국어 텍스트","hypothesis":""}
```
Fields `audio` and `hypothesis` are optional; if `hypothesis` is absent, it is treated as empty string.

---

## Component Boundaries

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

---

## Assumptions

- v1 uses `MockASRBackend` exclusively; real GPU-backed backends are out of scope.
- Korean (ko-KR) is the primary language; ASCII test cases are also supported.
- Docker image is based on `python:3.11-slim`.
- No authentication or rate limiting is required for v1.
- Audio input is expected to be WAV or any format readable by `soundfile`; other formats return 422.
- CER spaces-removed approach means word boundary information is not preserved in the character edit distance — this is intentional per the EVAL_PROTOCOL.
- Sample rate of uploaded audio may differ from 16 kHz and will be resampled.
