# QA Checklist: ASR Serving Pipeline v1

**BMAD Phase**: QA  
**Date**: 2026-05-15

---

## 1. Acceptance Criteria Verification

| ID | Criterion | Status | Test |
|----|-----------|--------|------|
| AC-1 | `GET /healthz` returns `{"status":"ok"}` with HTTP 200 | [ ] | `tests/integration/test_health.py::test_healthz_returns_200` |
| AC-2 | `POST /transcribe` returns required JSON fields with `req_` prefix UUID | [ ] | `tests/integration/test_transcribe.py::test_transcribe_request_id_prefix` |
| AC-3 | `POST /eval/cer` returns per-sample and aggregate CER | [ ] | `tests/integration/test_metrics.py::test_eval_cer_response_schema` |
| AC-4 | `python -m src.eval.cer_runner --manifest <path>` prints JSONL results | [ ] | `tests/eval/test_eval_smoke.py::test_cli_runs_without_error` |
| AC-5 | `GET /metrics` returns Prometheus text format with required metrics | [ ] | `tests/integration/test_metrics.py::test_metrics_contains_required_metrics` |
| AC-6 | CER of identical strings = 0.0; CER of empty hypothesis ≈ 1.0 | [ ] | `tests/unit/test_cer.py::test_perfect_match_cer_zero`, `test_empty_hypothesis_cer_one` |
| AC-7 | `MockASRBackend` returns deterministic transcript (no GPU/network) | [ ] | `tests/unit/test_normalization.py::test_deterministic_for_same_input` |
| AC-8 | All pytest tests pass | [ ] | `pytest tests/` |

---

## 2. Unit Test Coverage

### CER Module (`src/eval/cer.py`)
- [ ] `normalize_text`: NFKC, lowercase, whitespace collapse, space removal
- [ ] `normalize_text`: empty string
- [ ] `normalize_text`: Korean characters preserved
- [ ] `normalize_text`: full-width to ASCII
- [ ] `levenshtein_distance`: identical strings → (0, 0, 0)
- [ ] `levenshtein_distance`: empty → full (all insertions)
- [ ] `levenshtein_distance`: full → empty (all deletions)
- [ ] `levenshtein_distance`: one substitution
- [ ] `CERCalculator.compute_pair`: perfect match CER=0
- [ ] `CERCalculator.compute_pair`: empty hypothesis CER=1
- [ ] `CERCalculator.compute_pair`: empty reference → CER=0
- [ ] `CERCalculator.compute_pair`: spaces ignored in reference count
- [ ] `CERCalculator.compute_batch`: aggregate mean computation

### Audio Module (`src/audio/preprocessor.py`)
- [ ] Mono 16kHz WAV passthrough
- [ ] Stereo → mono downmix
- [ ] 8kHz → 16kHz resampling
- [ ] Duration accuracy
- [ ] Invalid bytes → ValueError
- [ ] Output dtype float32

### Backend Module (`src/backends/`)
- [ ] `MockASRBackend.transcribe` returns `TranscriptResult`
- [ ] Confidence in [0.0, 1.0]
- [ ] Backend name = "mock"
- [ ] `MockASRBackend.health` returns True
- [ ] Deterministic for same input

---

## 3. Integration Test Coverage

### GET /healthz
- [ ] Returns 200
- [ ] Returns `{"status":"ok"}`
- [ ] Content-Type is application/json

### POST /transcribe
- [ ] Returns 200 for valid WAV
- [ ] Response has all required fields
- [ ] `request_id` starts with `req_`
- [ ] `request_id` is unique across calls
- [ ] `timing` has all four fields (all numeric)
- [ ] `model.backend == "mock"`
- [ ] `confidence` in [0.0, 1.0]
- [ ] `audio_duration_seconds > 0`
- [ ] Stereo audio handled without error
- [ ] Invalid audio bytes → 422
- [ ] Missing file → 422

### GET /metrics
- [ ] Returns 200
- [ ] Content-Type contains `text/plain`
- [ ] Contains `asr_requests_total`
- [ ] Contains `asr_request_duration_seconds`
- [ ] Contains `asr_errors_total`

### POST /eval/cer
- [ ] Perfect match → CER=0.0
- [ ] Empty hypothesis → CER=1.0
- [ ] Response has `results` and `aggregate`
- [ ] Aggregate `total_samples` matches input count
- [ ] Empty pairs list → 422
- [ ] `reference_length` excludes spaces

---

## 4. Eval Smoke Test Coverage

- [ ] CLI exits 0
- [ ] All output lines are valid JSON
- [ ] Last line has `aggregate` key
- [ ] `total_samples` == 5 (fixture manifest)
- [ ] `sample_001` CER == 0.0 (perfect match)
- [ ] `sample_004` CER == 1.0 (empty hypothesis)
- [ ] `--output` flag writes JSONL file

---

## 5. Non-Functional Checks

- [ ] No GPU or network calls in any test
- [ ] No hardcoded secrets in source code
- [ ] All settings via environment variables
- [ ] `docker compose up --build` starts service
- [ ] `GET /healthz` returns 200 after container start
- [ ] `pytest tests/` passes in < 60 seconds

---

## 6. Known Limitations (v1)

- No real ASR backend: only `MockASRBackend` implemented
- No authentication: `/transcribe` is open
- No rate limiting
- No request body size limit on audio upload
- Metrics are in-memory only (reset on restart); no persistence
- CER runner CLI does not call the API to re-transcribe audio (offline eval only)

---

## Sign-off

| Role | Name | Date | Signature |
|------|------|------|-----------|
| QA Lead | — | 2026-05-15 | (pending test run) |
| PM | John | 2026-05-15 | (pending AC verification) |
