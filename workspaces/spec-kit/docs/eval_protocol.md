# CER Evaluation Protocol

**Spec ref**: `.specify/asr-pipeline-spec.md § CER Evaluation Protocol`

## Formula

```
CER = (S + D + I) / N
```

| Symbol | Meaning |
|--------|---------|
| S | Substitutions — reference character replaced by a different one |
| D | Deletions — reference character missing in hypothesis |
| I | Insertions — hypothesis character not in reference |
| N | Number of characters in the normalized reference |

## Normalization Pipeline

Applied to **both** reference and hypothesis before scoring:

1. **NFKC normalization** — resolve Unicode compatibility characters (e.g., decomposed Korean jamo → composed jamo)
2. **Lowercase** — `text.lower()`
3. **Trim + collapse whitespace** — `re.sub(r"\s+", " ", text).strip()`
4. **Remove all spaces** — `text.replace(" ", "")` — character-level alignment ignores word boundaries

## Edge Cases

| Scenario | Result |
|----------|--------|
| Reference empty after normalization | `cer = null`; excluded from aggregate |
| Hypothesis empty, reference non-empty | `cer = 1.0` (all deletions) |
| Many insertions vs short reference | `cer > 1.0` (allowed) |

## Aggregate CER

```
overall_cer = total_edits / total_reference_chars
```

Samples with `cer = null` (empty reference) are excluded from both numerator and denominator.

## JSONL Manifest Format

One JSON object per line:

```jsonl
{"id":"sample_001","audio":"audio/sample_001.wav","reference":"한국어 텍스트","hypothesis":""}
{"id":"sample_002","audio":"audio/sample_002.wav","reference":"hello world","hypothesis":"hello word"}
```

| Field | Required | Description |
|-------|----------|-------------|
| `id` | Yes | Unique sample identifier |
| `reference` | Yes | Ground-truth transcript |
| `audio` | No | Path to audio file (informational) |
| `hypothesis` | No | ASR output (defaults to `""` if absent) |

## CLI Usage

```bash
# Print results to stdout
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl

# Write results to file
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl --output results.json
```

## API Usage

```bash
curl -X POST http://localhost:8000/eval/cer \
  -H "Content-Type: application/json" \
  -d '{
    "pairs": [
      {"id": "s1", "reference": "안녕하세요", "hypothesis": "안녕하세요"}
    ]
  }'
```
