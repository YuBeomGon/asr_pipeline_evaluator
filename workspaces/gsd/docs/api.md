# API Reference

Base URL: `http://localhost:8000`

---

## GET /healthz

Liveness probe.

**Response 200:**
```json
{"status": "ok"}
```

---

## GET /metrics

Prometheus metrics in text exposition format.

**Response 200** (`Content-Type: text/plain; version=0.0.4`):
```
# HELP asr_requests_total Total ASR transcribe requests
# TYPE asr_requests_total counter
asr_requests_total{status="success"} 42.0
...
```

Minimum metrics:
- `asr_requests_total` — counter, label `status` (`success` | `error`)
- `asr_request_duration_seconds` — histogram
- `asr_errors_total` — counter

---

## POST /transcribe

Transcribe an audio file.

**Request:** `multipart/form-data`
- `file`: audio file (WAV, FLAC, OGG, etc.)

**Response 200:**
```json
{
  "request_id": "req_550e8400-e29b-41d4-a716-446655440000",
  "transcript": "안녕하세요 이것은 모의 전사입니다",
  "confidence": 0.95,
  "audio_duration_seconds": 2.35,
  "timing": {
    "preprocess_ms": 12.5,
    "inference_ms": 1.2,
    "postprocess_ms": 0.3,
    "total_ms": 14.0
  },
  "model": {
    "backend": "mock",
    "name": "mock-asr",
    "version": "0.1.0"
  }
}
```

**Errors:**
- `400` — empty file
- `422` — audio decoding failed
- `500` — unexpected server error

---

## POST /eval/cer

Compute Character Error Rate for a list of pairs.

**Request body (JSON):**
```json
{
  "pairs": [
    {"id": "s1", "reference": "이것은 테스트입니다", "hypothesis": "이것은 테스트"},
    {"id": "s2", "reference": "hello world", "hypothesis": "hello world"}
  ]
}
```

**Response 200:**
```json
{
  "aggregate": {
    "num_samples": 2,
    "total_edit_distance": 4,
    "total_reference_length": 14,
    "macro_cer": 0.285714,
    "micro_cer": 0.285714
  },
  "samples": [
    {
      "id": "s1",
      "reference_normalized": "이것은테스트입니다",
      "hypothesis_normalized": "이것은테스트",
      "edit_distance": 3,
      "reference_length": 9,
      "cer": 0.333333
    },
    {
      "id": "s2",
      "reference_normalized": "helloworld",
      "hypothesis_normalized": "helloworld",
      "edit_distance": 0,
      "reference_length": 10,
      "cer": 0.0
    }
  ]
}
```

CER formula: `(S + D + I) / N` where N = reference character count after normalization.
