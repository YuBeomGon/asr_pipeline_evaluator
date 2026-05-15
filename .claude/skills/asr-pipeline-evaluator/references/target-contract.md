# Target ASR Serving Pipeline Contract

Use this contract when comparing Spec Kit, OpenSpec, GSD, and BMAD outputs.


For exact implementation scope, also use:

```text
.claude/skills/asr-pipeline-evaluator/assets/baseline/IMPLEMENTATION_SCOPE.md
docs/07-implementation-scope.md
```

## Required endpoints

- `GET /healthz`: returns service health.
- `GET /metrics`: returns Prometheus-style metrics or a structured metrics summary.
- `POST /transcribe`: accepts audio upload and returns transcript metadata.
- `POST /eval/cer` or CLI equivalent: computes CER from reference/hypothesis pairs.

## Required response fields for `/transcribe`

```json
{
  "request_id": "string",
  "transcript": "string",
  "confidence": 0.0,
  "audio_duration_seconds": 0.0,
  "timing": {
    "preprocess_ms": 0.0,
    "inference_ms": 0.0,
    "postprocess_ms": 0.0,
    "total_ms": 0.0
  },
  "model": {
    "backend": "mock|whisper|triton|remote",
    "name": "string",
    "version": "string"
  }
}
```

## Required module boundaries

- API layer
- audio ingestion/preprocessing layer
- ASR backend interface
- backend implementation, including `MockASRBackend`
- postprocessing/transcript normalization layer
- CER evaluation layer
- observability/logging/metrics layer
- configuration layer

## Default CER normalization policy

1. Unicode normalize with NFKC.
2. Lowercase.
3. Trim leading/trailing whitespace.
4. Collapse repeated whitespace to one space.
5. Remove spaces before character-level CER unless the task explicitly requires spaces to count.
6. Report the policy in docs and tests.

## Candidate pass expectations

A candidate does not need a real GPU model to pass v1. It must run locally using a mock backend and be clearly replaceable with Whisper, Triton, or a remote ASR service.


## Required candidate documentation

Each candidate should include docs or README sections covering:

- architecture
- API usage
- eval protocol
- implementation scope
- known limitations
- runbook
