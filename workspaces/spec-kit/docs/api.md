# API Reference: ASR Serving Pipeline

**Spec ref**: `.specify/asr-pipeline-spec.md § API Contract`

Base URL: `http://localhost:8000`

---

## GET /healthz

Liveness/readiness probe.

**Response 200**:
```json
{"status": "ok"}
```

---

## GET /metrics

Prometheus metrics endpoint.

**Response 200** (Content-Type: `text/plain; version=0.0.4`):

Standard Prometheus exposition format. Required metric families:

| Metric | Type | Labels | Description |
|--------|------|--------|-------------|
| `asr_requests_total` | Counter | `status` (`success`\|`error`) | Total transcription requests |
| `asr_request_duration_seconds` | Histogram | — | End-to-end request duration |
| `asr_errors_total` | Counter | — | Total errors |

---

## POST /transcribe

Submit an audio file for transcription.

**Request**: `multipart/form-data`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `file` | File | Yes | Audio file (WAV, FLAC, OGG, …) |

**Response 200**:
```json
{
  "request_id": "req_3f4a1b2c...",
  "transcript": "안녕하세요 테스트 음성입니다",
  "confidence": 0.98,
  "audio_duration_seconds": 1.0,
  "timing": {
    "preprocess_ms": 12.5,
    "inference_ms": 0.03,
    "postprocess_ms": 0.1,
    "total_ms": 12.63
  },
  "model": {
    "backend": "mock",
    "name": "mock-asr",
    "version": "0.1.0"
  }
}
```

**Response 422**:
```json
{"detail": "Empty audio file"}
```

### Notes
- Audio is resampled to 16 kHz mono internally.
- `request_id` is always `req_` followed by a UUID4 hex string.
- `confidence` is in range [0.0, 1.0].

---

## POST /eval/cer

Compute Character Error Rate for reference/hypothesis text pairs.

**Request body** (JSON):
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

**Response 200**:
```json
{
  "pairs": [
    {
      "id": "sample_001",
      "cer": 0.0,
      "reference_chars": 7,
      "edits": 0
    }
  ],
  "overall_cer": 0.0,
  "total_reference_chars": 7,
  "total_edits": 0
}
```

### CER Field Notes
- `cer` for a sample is `null` when reference is empty (undefined).
- `overall_cer` excludes samples with empty references.
- CER may exceed 1.0 when insertions outnumber reference characters.
- Normalization: NFKC → lowercase → whitespace collapse → remove spaces.

---

## Error Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 422 | Validation error (empty file, bad audio, empty pairs list) |
| 500 | Internal server error |
