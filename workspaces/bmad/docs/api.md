# API Reference: ASR Serving Pipeline v1

**BMAD Phase**: Architect  
**Date**: 2026-05-15

---

## Base URL

```
http://localhost:8000
```

---

## GET /healthz

Returns service liveness status.

**Response 200**
```json
{"status": "ok"}
```

---

## GET /metrics

Returns Prometheus text exposition format.

**Content-Type**: `text/plain; version=0.0.4`

**Minimum exported metrics**:
```
# HELP asr_requests_total Total ASR transcription requests
# TYPE asr_requests_total counter
asr_requests_total{status="success"} 42.0
asr_requests_total{status="error"} 1.0

# HELP asr_request_duration_seconds ASR request processing duration
# TYPE asr_request_duration_seconds histogram
asr_request_duration_seconds_bucket{le="0.005"} 0.0
...

# HELP asr_errors_total Total ASR errors
# TYPE asr_errors_total counter
asr_errors_total 1.0
```

---

## POST /transcribe

Transcribe uploaded audio file.

**Request**: `multipart/form-data`

| Field | Type | Description |
|-------|------|-------------|
| `file` | binary | Audio file (WAV, FLAC, OGG, MP3) |

**Response 200**
```json
{
  "request_id": "req_550e8400-e29b-41d4-a716-446655440000",
  "transcript": "인식된 텍스트",
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

**Response 422** — validation error (missing file)  
**Response 500** — internal processing error

---

## POST /eval/cer

Compute Character Error Rate for a batch of reference/hypothesis pairs.

**Request**: `application/json`

```json
{
  "pairs": [
    {
      "id": "sample_001",
      "reference": "한국어 텍스트",
      "hypothesis": "한국어 텍스트"
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
      "reference": "한국어 텍스트",
      "hypothesis": "한국어 텍스트",
      "cer": 0.0,
      "substitutions": 0,
      "deletions": 0,
      "insertions": 0,
      "reference_length": 7
    }
  ],
  "aggregate": {
    "mean_cer": 0.0,
    "total_samples": 1,
    "total_reference_chars": 7,
    "total_errors": 0
  }
}
```

**Notes**:
- CER is computed at character level after normalization (see eval_protocol.md).
- `reference_length` is the character count after normalization (spaces removed).
- If reference is empty after normalization, CER is reported as `0.0` for that sample.

---

## CLI: python -m src.eval.cer_runner

```bash
python -m src.eval.cer_runner \
  --manifest path/to/manifest.jsonl \
  [--output results.jsonl]
```

**Manifest JSONL format** (one JSON object per line):
```json
{"id": "sample_001", "audio": "audio/sample_001.wav", "reference": "한국어 텍스트", "hypothesis": "인식 결과"}
```

**Output**: JSONL with per-sample CER + aggregate printed to stdout (and optionally written to `--output`).
