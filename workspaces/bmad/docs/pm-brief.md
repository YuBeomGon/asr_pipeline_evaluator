# PM Brief: ASR Serving Pipeline v1

**BMAD Phase**: PM  
**Agent**: John (Product Manager)  
**Date**: 2026-05-15  
**Status**: Approved

---

## 1. Problem Statement

Speech recognition services are deployed today without consistent quality measurement infrastructure. Teams have no reliable way to compute Character Error Rate (CER) from production traffic, no common backend abstraction to swap ASR engines, and no standardized API contract to enable cross-team integration.

**Jobs-to-be-done:**
- ML engineers need to benchmark ASR model quality with CER at scale.
- Platform engineers need a swap-friendly backend abstraction that lets them trial new ASR engines (Whisper, Azure, Google, custom) without rewriting the serving layer.
- Operations teams need health, metrics, and structured logs so incidents can be detected and diagnosed from dashboards.

---

## 2. Stakeholders

| Role | Representative | Need |
|------|---------------|------|
| ML Engineer | Internal team | CER evaluation endpoint + CLI runner |
| Backend Engineer | Internal team | Clean abstraction layer, reproducible local dev |
| DevOps / SRE | Internal team | Prometheus metrics, health check, structured logs |
| QA Lead | Internal team | Deterministic test coverage without GPU |

---

## 3. Success Criteria

1. **CER correctness**: `/eval/cer` returns `CER = (S+D+I) / N` per-sample and aggregate, normalized per protocol.
2. **Backend abstraction**: Swapping `MockASRBackend` for a real backend requires changing one config line or environment variable, not rewriting routes.
3. **Local reproducibility**: `docker compose up` starts the service; `pytest tests/` passes without GPU or network calls.
4. **Observability**: Prometheus scrape target at `/metrics` exposes `asr_requests_total`, `asr_request_duration_seconds`, `asr_errors_total`.
5. **API contract**: `/healthz`, `/transcribe`, `/eval/cer` match the agreed contract exactly (field names, types, status codes).
6. **Korean language support**: CER normalization handles Unicode NFKC, NFC, Korean whitespace, and punctuation correctly.

---

## 4. Scope Boundaries

### In Scope (v1)
- FastAPI serving app with three endpoints: `/healthz`, `/transcribe`, `/eval/cer`
- `ASRBackend` abstract base class + `MockASRBackend` implementation
- Audio preprocessing: resample to 16 kHz mono, return duration
- Transcript postprocessing: Korean NFC normalization, punctuation handling
- CER evaluator: Python module + `/eval/cer` HTTP endpoint + `python -m src.eval.cer_runner` CLI
- Prometheus metrics via `prometheus_client`
- Structured logging with `request_id` in every line
- pytest unit, integration, and eval smoke tests
- Dockerfile + docker-compose.yml for local dev
- Documentation: architecture, API, eval protocol, implementation scope, runbook

### Out of Scope (v1)
- Real GPU inference (Whisper, Wav2Vec2, etc.)
- Model training or fine-tuning
- Speaker diarization
- Authentication / authorization
- Billing or quota enforcement
- Full horizontal autoscaling
- Streaming transcription

---

## 5. Acceptance Criteria

| ID | Criterion | Verification |
|----|-----------|-------------|
| AC-1 | `GET /healthz` returns `{"status":"ok"}` with HTTP 200 | Integration test |
| AC-2 | `POST /transcribe` returns required JSON fields with `req_` prefix UUID | Integration test |
| AC-3 | `POST /eval/cer` returns per-sample and aggregate CER | Unit + integration test |
| AC-4 | `python -m src.eval.cer_runner --manifest <path>` prints JSONL results | Eval smoke test |
| AC-5 | `GET /metrics` returns Prometheus text format with required metrics | Integration test |
| AC-6 | CER of identical strings = 0.0; CER of empty hypothesis ≈ 1.0 | Unit test |
| AC-7 | `MockASRBackend` returns deterministic transcript (no GPU/network) | Unit test |
| AC-8 | All pytest tests pass | CI |

---

## 6. Constraints

- Python 3.11+
- No GPU required for any test
- No external network calls in tests (use `httpx.AsyncClient` with `app` directly)
- Secrets must not be hardcoded; use environment variables via Pydantic Settings

---

## 7. Definition of Done

- [ ] All 8 acceptance criteria verified
- [ ] `pytest tests/` exits 0
- [ ] `docker compose up` starts service on port 8000
- [ ] `GET /healthz` returns 200
- [ ] Architecture, API, and runbook docs present and accurate
- [ ] QA checklist signed off
