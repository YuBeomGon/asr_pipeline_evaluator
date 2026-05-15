# API Reference

The authoritative API contract is `openapi.yaml` at the project root.
This document provides a human-readable summary.

## Endpoints

### GET /healthz

Liveness/readiness probe.

**Response 200**
```json
{"status": "ok"}
```

`status` values: `"ok"` | `"degraded"` | `"error"`

---

### GET /metrics

Prometheus text exposition format (for scraping by Prometheus or Grafana Agent).

**Content-Type**: `text/plain; version=0.0.4`

**Metrics included**:
| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `asr_requests_total` | counter | `status` | Total requests |
| `asr_request_duration_seconds` | histogram | — | End-to-end latency |
| `asr_errors_total` | counter | — | Total errors |
| `asr_audio_duration_seconds` | histogram | — | Input audio duration |
| `asr_inference_duration_seconds` | histogram | — | Backend inference latency |

---

### POST /transcribe

Upload an audio file and receive the transcription.

**Request**: `multipart/form-data`
- `file` (required): Audio file (WAV, FLAC, OGG)

**Response 200**
```json
{
  "request_id": "req_550e8400-e29b-41d4-a716-446655440000",
  "transcript": "안녕하세요 반갑습니다",
  "confidence": 0.95,
  "audio_duration_seconds": 1.0,
  "timing": {
    "preprocess_ms": 5.1,
    "inference_ms": 10.2,
    "postprocess_ms": 0.1,
    "total_ms": 15.4
  },
  "model": {
    "backend": "mock",
    "name": "mock-asr",
    "version": "0.1.0"
  }
}
```

**Error responses**:
- `400` — Empty or undecodable audio file
- `413` — File exceeds size limit (50 MB default)
- `422` — Missing `file` field
- `500` — Internal error

---

### POST /eval/cer

Compute Character Error Rate for one or more reference/hypothesis pairs.

**Request body**
```json
{
  "pairs": [
    {
      "id": "sample_001",
      "reference": "안녕하세요 반갑습니다",
      "hypothesis": "안녕하세요 반갑습니다"
    }
  ]
}
```

**Response 200**
```json
{
  "results": [
    {
      "id": "sample_001",
      "reference": "안녕하세요반갑습니다",
      "hypothesis": "안녕하세요반갑습니다",
      "cer": 0.0,
      "substitutions": 0,
      "deletions": 0,
      "insertions": 0,
      "reference_length": 10
    }
  ],
  "aggregate": {
    "mean_cer": 0.0,
    "total_substitutions": 0,
    "total_deletions": 0,
    "total_insertions": 0,
    "total_reference_length": 10,
    "total_samples": 1
  }
}
```

Note: `reference` and `hypothesis` in the response are the **normalized** strings
(NFKC + lowercase + spaces removed), not the raw inputs.
