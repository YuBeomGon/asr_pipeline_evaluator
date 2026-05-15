# Human Review — ASR Pipeline Bakeoff

Review date: 2026-05-15
Reviewers: asr-architect, asr-evaluator, asr-ops-reviewer, asr-qa-reviewer (parallel specialist agents)
Candidates: outputs/spec-kit, outputs/openspec, outputs/gsd, outputs/bmad

---

## Summary

Automated rubric scored all four candidates 100/100 and all pytest suites passed, which masked
significant qualitative differences. This specialist review reveals that the four frameworks
produced meaningfully distinct outputs in architecture clarity, CER correctness, operational
readiness, and test depth. OpenSpec is the strongest overall candidate; Spec-Kit has the most
correct CER evaluation; GSD and BMAD both have substantive correctness defects.

---

## Candidate Ranking

| Rank | Candidate | Architecture | CER Eval | Ops Readiness | Test Quality | Notable Strength | Critical Weakness |
|---:|---|:---:|:---:|:---:|:---:|---|---|
| 1 | OpenSpec | 5 | 3 | 5 | 5 | ContextVar logging, injectable metrics registry, 413 enforcement, non-root Docker | Macro CER reported as primary aggregate (non-standard) |
| 2 | Spec-Kit | 3 | 5 | 4 | 4 | Correct micro-CER, proper empty-ref exclusion, resampling integration test | `bytes` backend interface forces unnecessary round-trip serialization |
| 3 | BMAD | 4 | 2 | 3 | 4 | Decorator-based backend registry, subprocess CLI smoke test | Empty-ref + non-empty hypothesis → CER=0.0 (hallucination rewarded) |
| 4 | GSD | 3 | 4 | 2 | 3 | Separate normalizer module, both macro+micro CER, librosa resampler | Global mutable `_BACKEND` silently falls back to mock in production |

---

## Per-Candidate Review

### Spec-Kit

**Architecture (3/5)**

Module layout is clean: `backends/`, `audio/`, `api/`, `eval/`, `config/`, `observability/`.
The critical flaw is the `ASRBackend` abstract interface signature:

```python
# src/backends/base.py
def transcribe(self, audio_bytes: bytes, sample_rate: int) -> TranscriptResult
```

This forces every real backend to accept raw bytes and re-deserialize them. The route at
`routes.py:132` converts a numpy array to bytes: `chunk.samples.tobytes()`, and the mock at
`mock.py:59` immediately converts back: `np.frombuffer(audio_bytes, dtype=np.float32)`. All other
candidates pass `np.ndarray` directly, which is the interface expected by Whisper, wav2vec2, and
Triton. Replacing the mock with any real backend requires implementing this serialization
convention or the interface comment "concrete backends decide" will cause silent inconsistency.
No `health_check` abstract method on the backend contract.

Backend injection via `app.state.backend` is the canonical FastAPI pattern — correctly used.
Normalization documentation is the clearest of the four: NFC (display) vs NFKC (CER) distinction
is explicit in both `audio/postprocessing.py` and `eval/cer.py`.

**CER Evaluation (5/5)**

The strongest CER design of the four candidates.

- Formula: `edits / len(ref_norm)` using `editdistance` library — correct.
- Empty reference: returns `cer=None` and is excluded from aggregate numerator and denominator.
  This matches the EVAL_PROTOCOL baseline exactly.
- Aggregation: micro-CER (`total_edits / total_ref_chars`) — standard ASR convention.
- Eval test: asserts `overall_cer == pytest.approx(3/11)` with explicit arithmetic, including
  a test that verifies empty-reference samples are excluded from the aggregate.
- JSONL runner: warns and skips malformed lines without crashing.

Only gap: no S/D/I decomposition (uses `editdistance.eval()` which returns total edit count only).
Deliberate design choice, architecturally consistent, but less informative for error analysis.

**Operational Readiness (4/5)**

- Health: GET /healthz returns `{"status":"ok"}` unconditionally. Backend-blind — a broken
  backend still reports healthy.
- Metrics: three instruments (`asr_requests_total`, `asr_request_duration_seconds`,
  `asr_errors_total`). Missing `audio_duration_seconds` and `inference_duration_seconds`.
  Default Prometheus bucket configuration (not ASR-tuned).
- Logging: hand-rolled `StructuredJsonFormatter` with consistent `request_id` via
  `RequestLogger` adapter. Fallback sentinel `"-"` for system logs is cosmetic noise.
- Error handling: preprocessing failures correctly caught and forwarded as 422. No catch path
  for backend exceptions — if `backend.transcribe()` raises, FastAPI returns a raw 500.
- Runbook: 139 lines, well-organized, covers local setup, Docker, CER, env vars, and
  troubleshooting. Strong for v1.
- Dockerfile: single-stage, runs as root. No file size limit. No inference timeout.

**Test Quality (4/5)**

71 tests across unit/integration/eval. The resampling integration test
(`test_resampling_44k_stereo`) sends a synthesized 44.1 kHz stereo WAV and expects HTTP 200 —
the strongest single integration check in the field. CER runner tests call `main()` directly and
assert exact arithmetic (`3/11`). Test fixtures generate real PCM WAV bytes via `soundfile`.
No dedicated backend unit test file; backend correctness is verified only transitively.

---

### OpenSpec

**Architecture (5/5)**

The most complete ASRBackend abstract contract:

```python
# src/backends/base.py
def transcribe(self, audio: np.ndarray, sample_rate: int) -> TranscriptResult  # correct type
def health_check(self) -> bool  # required by contract
```

`ASRBackendError` is defined in `base.py` and caught explicitly in the route — the correct typed
error propagation pattern. Backend injection via `lru_cache` registry (`backends/registry.py`)
is clean: adding Whisper requires implementing `ASRBackend`, registering it, and setting
`ASR_BACKEND=whisper`. Zero API-layer changes.

Logging uses `contextvars.ContextVar` (`request_id_var`) — the only async-correct propagation
mechanism. The `LoggerAdapter` approach used by other candidates can lose context across `await`
boundaries in concurrent requests.

Metrics use an injectable `CollectorRegistry` — the only design that supports isolated metrics
in parallel tests without `ValueError: Duplicated timeseries` errors.

Postprocessing isolated in `src/api/postprocessing.py` with the most thorough implementation:
NFC, strip, whitespace collapse, and Korean punctuation cleanup. `openapi.yaml` as the
authoritative contract source is a meaningful production signal.

**CER Evaluation (3/5)**

Per-sample CER formula is correct with full S/D/I decomposition via a custom Levenshtein DP.

Critical deficit: `evaluate_batch` computes `mean_cer` as arithmetic mean of per-sample CERs
(macro-average), not `total_edits / total_ref_chars` (micro-average). The standard for ASR
evaluation is micro-average because it weights each character equally rather than each utterance.

```python
# src/eval/cer.py:232
mean_cer = sum(r.cer for r in results) / n  # macro — non-standard
```

The integration test at `tests/integration/test_eval_cer.py:69` does not detect this because
the test case happens to make macro and micro numerically equal. Any real evaluation with
heterogeneous utterance lengths will produce a misleading aggregate.

Empty-reference policy: assigns `cer=0.0` (both empty) or `cer=1.0` (hypothesis non-empty).
These samples are included in the aggregate rather than excluded — diverges from EVAL_PROTOCOL.

**Operational Readiness (5/5)**

- Health: calls `backend.health_check()` and returns `"ok"` / `"degraded"` / `"error"` — the
  only tri-state, backend-aware health check. Dockerfile includes a `HEALTHCHECK` directive.
- Metrics: five instruments with domain-tuned buckets — `asr_requests_total`,
  `asr_request_duration_seconds` (buckets 0.05–10.0), `asr_errors_total`,
  `asr_audio_duration_seconds` (buckets 1.0–300.0), `asr_inference_duration_seconds`
  (buckets 0.01–5.0). Both audio and inference histograms are observed in the route.
- Logging: ContextVar-based request ID propagation is the only async-safe approach. Startup logs
  correctly omit the field rather than emitting a sentinel.
- Error handling: 413 for files exceeding `max_audio_bytes` (configurable via env) is the only
  correct file-size enforcement in the field. Typed `ASRBackendError` catch is correct. Gap:
  `detail=f"ASR inference failed: {exc}"` leaks exception messages to the client.
- Dockerfile: non-root user (`USER appuser`) — only candidate with this security hardening.
- Runbook: 154 lines, most complete — includes interactive docs reference (`/docs`, `/redoc`),
  all curl examples, full env var table, Docker instructions.

**Test Quality (5/5)**

83 tests, best per-route file organization (one file per endpoint in `tests/integration/`).
Dedicated `tests/unit/test_backends.py` exercises `health_check()`, `backend_id`,
`model_version`, determinism, and `inference_ms`. Postprocessing punctuation test
(`"안녕 ."` → `"안녕."`) is unique to this candidate. CER unit tests separately assert
`substitutions`, `deletions`, `insertions` as distinct fields — most granular decomposition.
Korean manifest test with exact `cer = approx(1/8)` for a real linguistic substitution.
Gap: no resampling integration test, no metrics counter-increment test after transcription.

---

### GSD

**Architecture (3/5)**

The normalizer module (`src/eval/normalizer.py`) is the best-designed normalization boundary:
`normalize_for_cer()` and `normalize_transcript()` are clean pure functions importable by both
evaluator and postprocessor without either owning the policy.

The librosa resampler (`librosa.resample`) is the most production-appropriate choice — it
includes anti-aliasing unlike the linear interpolation used by other candidates.

Critical production safety risk:

```python
# src/api/routes/transcribe.py
_BACKEND: ASRBackend | None = None

def _get_backend() -> ASRBackend:
    global _BACKEND
    if _BACKEND is None:
        _BACKEND = MockASRBackend()  # silent fallback
    return _BACKEND
```

A misconfigured production deployment that bypasses lifespan silently serves mock transcripts
instead of failing. This is a production safety issue, not a style concern.
Additionally, `TARGET_SR = 16_000` is a hardcoded module constant — changing the target sample
rate requires editing source, not config.

**CER Evaluation (4/5)**

The only candidate that computes and exposes both micro and macro CER:

```python
# src/eval/cer.py:82-83
macro = sum(r.cer for r in results) / len(results)
micro = total_dist / total_ref if total_ref > 0 else 0.0
```

And the only one with a test that explicitly discriminates between them:

```python
def test_macro_vs_micro(self):
    # one short + one long reference: macro=0.5, micro=1/6
    assert abs(agg.macro_cer - 0.5) < 1e-9
    assert abs(agg.micro_cer - 1 / 6) < 1e-9
```

Normalization separated into dedicated `normalizer.py` is architecturally clean. Gap:
redundant NFC step after NFKC (NFKC output is already NFC — the second call is a no-op that
creates documentation noise). Empty-reference samples are not excluded from aggregate but assigned
CER=0.0 or 1.0, diverging from EVAL_PROTOCOL.

**Operational Readiness (2/5)**

- Health: unconditional `{"status":"ok"}` — backend-blind. Compose healthcheck uses `curl`
  which is not installed in the Dockerfile (`ffmpeg` and `libsndfile1` are, but not curl).
  The container healthcheck silently fails in production.
- Metrics: three instruments with decent bucket tuning. No `audio_duration_seconds` or
  `inference_duration_seconds`. Minor bug: `observe_duration()` recalculates elapsed time
  rather than using the already-computed `total_ms`.
- Logging: uses `pythonjsonlogger` — functional, but field names follow Python logging convention
  rather than the spec's `timestamp`/`level`/`message` schema.
- Settings: no `env_prefix`. Bare field names `host`, `port`, `log_level` collide with common
  shell and container runtime variables. `LOG_LEVEL=INFO` in `docker-compose.yml` confirms
  reliance on unprefixed vars — silent misconfiguration risk in Kubernetes.
- CORS: `allow_origins=["*"]` with `allow_methods=["*"]` — maximally permissive, inappropriate.
- Bonus: bundled Prometheus service in `docker-compose.yml` with `docs/prometheus.yml` scrape
  config — the only candidate ready for metrics collection out of the box.

**Test Quality (3/5)**

42 tests — smallest count. All integration tests in a single file (`test_api.py`, 153 lines).
No dedicated audio preprocessing unit tests. No backend unit tests. The eval smoke test uses
range checks only (`0.0 < r.cer < 1.0`) rather than exact values — would not detect a regression
from CER=0.375 to CER=0.9. The `test_macro_vs_micro` unit test is the only test in the field
that simultaneously validates both aggregation methods with exact arithmetic.

Behavioral disagreement: `test_eval_cer_empty_pairs` asserts HTTP 200 for an empty pairs list.
All other candidates assert 422. This is the only case where all four candidates produce
genuinely different API behavior for the same input.

---

### BMAD

**Architecture (4/5)**

Decorator-based backend registry in `src/backends/registry.py` is the most scalable backend
discovery pattern — adding Whisper only requires decorating the class with `@register("whisper")`.
The abstract contract includes `health() -> bool`. CER implementation supports full S/D/I
decomposition.

Two significant gaps:

1. Postprocessing is inlined as a one-liner in the route:
   ```python
   # src/api/routes/transcribe.py:70
   transcript = unicodedata.normalize("NFC", result.text)
   ```
   Any expansion (punctuation cleanup, whitespace normalization) requires modifying route code.
   This is the weakest postprocessing boundary of the four.

2. `MockASRBackend` derives its response from `duration_ms % len(_DEFAULT_TRANSCRIPTS)` — a
   non-deterministic mock. Audio files of different lengths produce different transcripts. For a
   CER pipeline where the mock output must be predictable, this breaks determinism.

The `@register` decorator exists but `mock.py` does not use it — the only backend in v1 is
registered manually. The decorator is untested infrastructure.

**CER Evaluation (2/5)**

Substantive correctness bug:

```python
# src/eval/cer.py:160-170
if n == 0:
    return CERSampleResult(cer=0.0, ...)  # always 0.0 regardless of hypothesis
```

When the reference is empty and the hypothesis is non-empty (hallucinated output), BMAD returns
CER=0.0 — the best possible score. The test explicitly asserts this wrong behavior:

```python
def test_empty_reference_returns_zero(self):
    result = self.calc.compute_pair("s1", "", "텍스트")
    assert result.cer == 0.0  # 3-char hallucination rewarded with perfect score
```

This makes the aggregate look better than it is whenever a system generates output for empty
references. The eval protocol doc documents this behavior as the spec, meaning the bug is
enshrined at the documentation level.

Additional: macro-only aggregate (no micro-CER). The batch stores `total_reference_chars` and
`total_errors` but does not compute `micro_cer = total_errors / total_reference_chars`.

**Operational Readiness (3/5)**

- Health: `health()` abstract method is defined and `MockASRBackend.health()` returns `True`,
  but the `/healthz` route does not call it. Dead code from the operational perspective.
- Metrics: three instruments with well-tuned buckets. Idempotent factory using
  `REGISTRY._names_to_collectors` (private attribute) — fragile if prometheus_client changes
  internals.
- Logging: always emits `"request_id": ""` for non-request-scoped loggers (e.g., `/eval/cer`
  route generates no request ID). Empty string is worse than omitting the field.
- Error handling: 500 paths are clean (no exception message leakage). 422 leaks `str(e)` from
  preprocessing.
- `.env.example` file is the only candidate to provide a concrete operator starting point.
  The metrics table in the runbook (types, labels, descriptions) is operationally useful.
- Dockerfile: single-stage, runs as root. No file size limit. No inference timeout.

**Test Quality (4/5)**

70 tests. Subprocess-based CLI smoke test is the strongest in the field:

```python
subprocess.run([sys.executable, "-m", "src.eval.cer_runner", "--manifest", fixture_path, ...])
```

This is the only candidate that validates `python -m src.eval.cer_runner` works end-to-end
as a real subprocess invocation. On-disk `tests/fixtures/manifest.jsonl` with 5 real Korean
reference/hypothesis pairs is the only committed fixture file — inspectable and reproducible.
Dedicated `TestLevenshteinDistance` unit tests verify S/D/I at function level (unique to BMAD).
`test_deterministic_for_same_input` checks both `text` and `confidence` across two calls.

Gaps: missing empty-file integration test for `/transcribe`. CER runner module-level test uses
range check only (`0.0 <= mean_cer <= 1.0`). Eval/CER integration tests placed in
`test_metrics.py` (wrong file — reduces reviewability).

---

## Dimension Scores Summary

| Dimension | Spec-Kit | OpenSpec | GSD | BMAD |
|---|:---:|:---:|:---:|:---:|
| **Architecture** | | | | |
| ASR architecture clarity | 3 | 5 | 3 | 4 |
| Backend replaceability | 3 | 5 | 3 | 4 |
| Audio preprocessing boundaries | 4 | 4 | 3 | 4 |
| Extensibility to real backends | 3 | 5 | 3 | 4 |
| **CER Evaluation** | | | | |
| CER formula correctness | 5 | 5 | 5 | 4 |
| Normalization policy clarity | 5 | 5 | 4 | 5 |
| Aggregation correctness | 5 | 2 | 5 | 2 |
| Edge case handling | 5 | 3 | 3 | 2 |
| **Operations** | | | | |
| Health check quality | 2 | 5 | 2 | 2 |
| Metrics completeness | 3 | 5 | 3 | 3 |
| Logging quality | 4 | 5 | 3 | 3 |
| Error handling | 3 | 4 | 4 | 3 |
| Operational documentation | 4 | 5 | 3 | 4 |
| **Tests** | | | | |
| Test realism | 4 | 4 | 3 | 4 |
| API contract coverage | 4 | 4 | 3 | 3 |
| CER eval test quality | 4 | 4 | 3 | 5 |
| CI readiness | 4 | 4 | 3 | 4 |
| **Total (85 max)** | **65** | **75** | **56** | **61** |

---

## Disagreements with Automated Score

The automated rubric scored all four candidates 100/100. This review identifies the following
substantive differences that the rubric missed:

1. **Backend interface type (Spec-Kit)**: The `bytes` abstract interface at
   `outputs/spec-kit/src/backends/base.py` forces serialization round-trips that the `ndarray`
   interface used by the other three candidates avoids. The rubric checked that an abstract
   backend class exists — it did not check the interface type.

2. **CER aggregation method (OpenSpec, BMAD)**: Both report macro-average CER as the primary
   metric. The standard ASR convention is micro-average. The rubric checked that a CER endpoint
   exists and returns a numeric aggregate — it did not check the aggregation formula.

3. **Empty-reference CER bug (BMAD)**: `outputs/bmad/src/eval/cer.py:160-170` returns `cer=0.0`
   when reference is empty and hypothesis is non-empty. A hallucinated transcript receives a
   perfect CER score. The rubric checked that the CER function accepts empty inputs without
   crashing — it did not check the correctness of the returned value.

4. **Global mutable backend (GSD)**: `outputs/gsd/src/api/routes/transcribe.py:20-33` silently
   falls back to `MockASRBackend()` when the backend is not initialized. A misconfigured
   production deployment serves mock transcripts without any error. The rubric checked that a
   mock backend is present — it did not check the injection pattern safety.

5. **Health check depth**: All four candidates have a `/healthz` endpoint. Only OpenSpec routes
   through `backend.health_check()`. The rubric checked endpoint existence — it did not check
   whether the health check is backend-aware.

6. **File size enforcement**: Only OpenSpec enforces a maximum upload size (413 response).
   The rubric did not check for file size limits.

7. **Docker security**: Only OpenSpec runs as a non-root user. The rubric did not check the
   container user.

---

## Final Recommendation

**For a production-oriented v1 ASR serving pipeline, OpenSpec is the recommended choice.**

OpenSpec is the only candidate that gets the production-critical concerns right simultaneously:
async-safe logging (ContextVar), backend-aware health check, five properly bucketed metrics
instruments, typed backend errors, injectable metrics registry for test safety, 413 file size
enforcement, and non-root container user.

The CER aggregation gap (macro instead of micro) is a real defect but is correctable with a
two-line fix to `evaluate_batch`. The bytes-vs-ndarray architecture defect in Spec-Kit would
require changing the abstract interface and the route — a larger refactor.

**Spec-Kit ranks second** specifically for CER evaluation: it is the only candidate with
correct micro-aggregate, proper empty-reference exclusion (`cer=None`), exact arithmetic test
assertions, and a resampling integration test. If CER correctness is the primary criterion
(as stated in CLAUDE.md), Spec-Kit's CER design should be adopted into whichever candidate
moves forward.

**BMAD ranks third.** The decorator-based backend registry and subprocess CLI smoke tests are
genuine strengths. The empty-reference CER bug (hallucination → CER=0.0) is a production
correctness issue that must be fixed before any real evaluation.

**GSD ranks fourth.** The global mutable `_BACKEND` with silent mock fallback is a production
safety risk that disqualifies it for deployment without remediation. The normalizer module and
dual macro+micro CER design are the strongest architectural choices and should be adopted
by whichever candidate moves forward.

### Recommended Next Steps

1. Apply OpenSpec's ContextVar logging, injectable metrics registry, and 413 enforcement
   pattern to the other candidates.
2. Apply Spec-Kit's micro-CER aggregation and `cer=None` empty-reference policy to OpenSpec,
   GSD, and BMAD.
3. Fix BMAD's empty-reference CER bug: when `ref_len == 0` and `hypothesis` is non-empty,
   return `cer=None` (excluded) or `cer=1.0` (penalized), not `cer=0.0`.
4. Fix GSD's global mutable backend: use `app.state.backend` or a `lru_cache` registry; remove
   the silent mock fallback.
5. Add inference timeout (`asyncio.wait_for`) and global exception handler to all four candidates.
6. Add the `ASR_` env prefix to GSD and BMAD settings classes to prevent shell variable collision.
