# ASR Pipeline Evaluation Rubric

The automated evaluator uses heuristics and runtime checks. Human review should confirm the intent behind each category.

## Functionality, 20

Look for a working `/transcribe` flow, audio input handling, ASR backend abstraction, response metadata, error handling, and config management.

## ASR pipeline structure, 15

The best implementations separate preprocessing, chunking/batching, model adapter, postprocessing, and sync/async extension points. Avoid tightly coupling FastAPI route handlers directly to model code.

## CER evaluation, 15

CER must be reproducible. Award full credit only when reference/hypothesis inputs, normalization policy, per-sample and aggregate metrics, and edge cases are handled clearly.

## Serving API quality, 15

Reward clear schema, latency measurement, concurrency/backpressure, timeout/retry policy, streaming extension path, and health/metrics endpoints.

## Tests, 10

Reward unit tests for CER and preprocessing, integration tests for API endpoints, eval smoke tests, and CI-ready commands.

## Operations, 10

Reward Docker/local execution, logging with request IDs, metrics, deployment/runbook instructions, and fallback/rollback consideration.

## Maintainability, 10

Reward clear module boundaries, settings separation, dependency management, simple code, and vendor/model replacement paths.

## Documentation, 5

Reward architecture documentation, eval protocol, API examples, implementation scope, and known limitations.
