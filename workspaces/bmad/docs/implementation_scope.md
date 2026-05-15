# Implementation Scope: ASR Serving Pipeline v1

**BMAD Phase**: Architect  
**Date**: 2026-05-15

---

## In Scope

### API
- `GET /healthz` → liveness check
- `GET /metrics` → Prometheus text format
- `POST /transcribe` → audio upload, preprocessing, inference, response
- `POST /eval/cer` → batch CER evaluation endpoint

### Backend Layer
- `ASRBackend` abstract base class (ABC)
- `MockASRBackend`: deterministic response, no GPU, no network
- Backend registry: select backend by name from env var

### Audio Preprocessing
- Accept audio bytes (WAV, FLAC preferred)
- Resample to 16 kHz using scipy.signal
- Convert to mono (average channels)
- Return `(numpy_array, duration_seconds)`

### Transcript Postprocessing
- Korean NFC normalization for `/transcribe` output
- Punctuation handling (strip trailing/leading punctuation from mock output)

### CER Evaluation
- Normalization pipeline: NFKC → lower → collapse_ws → strip_spaces
- Levenshtein at character level
- `/eval/cer` HTTP endpoint
- `python -m src.eval.cer_runner --manifest <path>` CLI
- JSONL manifest support

### Observability
- Prometheus counters and histogram via `prometheus_client`
- Structured JSON logging
- `request_id` = `"req_"` + UUID4 in every log line and response

### Tests
- Unit: CER logic, normalization edge cases, MockASRBackend
- Integration: all three API endpoints via `httpx.AsyncClient`
- Eval smoke: CLI runner with fixture manifest

### Deployment
- `Dockerfile` (python:3.11-slim)
- `docker-compose.yml` with service + port mapping
- `.env.example` for local dev

---

## Out of Scope (v1)

| Feature | Reason |
|---------|--------|
| Real GPU inference (Whisper, Wav2Vec2) | Not required for v1 scaffold |
| Model training / fine-tuning | Out of serving scope |
| Speaker diarization | Separate pipeline concern |
| Authentication / JWT | Not in API contract |
| Billing / quota | Platform concern |
| Streaming / WebSocket | Batch API sufficient for v1 |
| Horizontal autoscaling configs | Infrastructure concern |
| Real audio test fixtures > 10s | Not needed for unit/integration |

---

## Non-Goals

- The mock backend does NOT need to produce linguistically accurate Korean.
- The service does NOT need to connect to any external service in tests.
- v1 is a scaffold; extensibility and correctness matter more than raw throughput.
