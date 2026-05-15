# ASR Serving Pipeline Requirements

Build a production-oriented speech recognition serving pipeline with CER evaluation.

This document is paired with `IMPLEMENTATION_SCOPE.md`. If there is ambiguity, treat `IMPLEMENTATION_SCOPE.md` as the source of truth for what is required, optional, and out of scope for v1.

## Core requirements

1. Provide `/transcribe` API.
2. Accept local audio file upload.
3. Include audio preprocessing layer.
4. Define `ASRBackend` interface.
5. Include `MockASRBackend` for local tests.
6. Return transcript, confidence, duration, request_id, model metadata, and timing metadata.
7. Provide CER evaluation using reference/hypothesis pairs.
8. Support eval manifest in JSONL.
9. Include `/healthz` and `/metrics` (Prometheus text exposition format) endpoints, plus `POST /eval/cer` or equivalent eval CLI.
10. Include unit tests, integration tests, and eval smoke test.
11. Include Dockerfile and local run instructions.
12. Include architecture document and runbook.
13. Include implementation scope and known limitations documentation.

## Constraints

- Keep model implementation pluggable.
- Do not hard-code a specific ASR provider.
- CER normalization policy must be explicit.
- The system must be runnable locally without a GPU using `MockASRBackend`.
- The implementation must be easy to replace with Whisper, Triton, vLLM-style server, or remote ASR endpoint later.
- Use clear module boundaries.
- Avoid overengineering.
