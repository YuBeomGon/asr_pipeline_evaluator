# GSD Task List: ASR Serving Pipeline v1

## Status legend: [ ] todo | [x] done | [~] in progress

---

## Phase 1: Project Skeleton

- [x] TASKS.md (this file)
- [x] requirements.txt
- [x] Dockerfile
- [x] docker-compose.yml
- [x] README.md
- [x] src/__init__.py stubs for all packages

## Phase 2: Config

- [x] src/config/settings.py — pydantic Settings with env vars (host, port, log_level, backend)

## Phase 3: Observability

- [x] src/observability/logging.py — structured JSON logger with request_id field
- [x] src/observability/metrics.py — prometheus_client counters/histograms

## Phase 4: ASR Backend

- [x] src/backends/base.py — ASRBackend ABC + TranscriptResult dataclass
- [x] src/backends/mock.py — MockASRBackend: deterministic response, no GPU

## Phase 5: Audio Preprocessing

- [x] src/audio/processor.py — resample to 16kHz mono, return numpy + duration_seconds

## Phase 6: Eval / CER

- [x] src/eval/cer.py — CER function: NFKC→lower→collapse whitespace→char edit distance
- [x] src/eval/cer_runner.py — CLI: `python -m src.eval.cer_runner --manifest <path>`
- [x] src/eval/normalizer.py — Korean NFC + punctuation normalization

## Phase 7: API

- [x] src/api/main.py — FastAPI app setup, lifespan, CORS
- [x] src/api/routes/health.py — GET /healthz
- [x] src/api/routes/metrics.py — GET /metrics (prometheus text)
- [x] src/api/routes/transcribe.py — POST /transcribe (multipart)
- [x] src/api/routes/eval.py — POST /eval/cer
- [x] src/api/schemas.py — request/response pydantic models

## Phase 8: Tests

- [x] tests/unit/test_cer.py — unit tests for CER math + edge cases
- [x] tests/unit/test_normalizer.py — unit tests for normalization
- [x] tests/integration/test_api.py — httpx TestClient: /healthz, /metrics, /transcribe, /eval/cer
- [x] tests/eval/test_eval_smoke.py — smoke: load JSONL manifest, compute CER, assert sane values

## Phase 9: Docs

- [x] docs/architecture.md
- [x] docs/api.md
- [x] docs/eval_protocol.md
- [x] docs/implementation_scope.md
- [x] docs/runbook.md

## Phase 10: Verify

- [x] pip install -r requirements.txt
- [x] pytest tests/ — all pass
- [x] rsync to outputs/gsd/
