# API Contract

## GET /healthz

Response 200:

```json
{"status":"ok"}
```

## GET /metrics

Return **Prometheus text exposition format** (`Content-Type: text/plain; version=0.0.4`). Include at minimum:

- request counter
- request latency histogram (e.g. `asr_request_duration_seconds`)
- error counter

## POST /transcribe

Request: multipart form with `file` audio upload.

Response 200:

```json
{
  "request_id": "req_...",
  "transcript": "recognized text",
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

## POST /eval/cer

Accept JSON or file references to reference/hypothesis pairs and return per-sample plus aggregate CER.
