# CER Evaluation Protocol

## Formula

```
CER = (S + D + I) / N
```

- **S** = substitutions
- **D** = deletions
- **I** = insertions
- **N** = number of characters in the normalized reference

CER can exceed 1.0 when the hypothesis contains many insertions relative to a short reference.

## Normalization pipeline

Applied to **both** reference and hypothesis before computing edit distance:

1. **Unicode NFKC** — compatibility decomposition then canonical composition (converts fullwidth chars, etc.)
2. **Unicode NFC** — canonical composition (Korean precomposed form)
3. **Lowercase** — case-fold for Latin characters
4. **Trim and collapse whitespace** — leading/trailing stripped, multiple spaces collapsed to one
5. **Remove spaces** — spaces removed before char-level scoring

Implementation: `src/eval/normalizer.py::normalize_for_cer`

## Aggregate metrics

| Metric | Formula |
|--------|---------|
| Micro CER | `total_edit_distance / total_reference_length` |
| Macro CER | `mean(per_sample_CER)` |

Use **micro CER** as primary metric (weighted by utterance length).

## Manifest format (JSONL)

Each line is a JSON object:
```json
{"id": "sample_001", "audio": "audio/sample_001.wav", "reference": "한국어 텍스트", "hypothesis": ""}
```

Fields:
- `id`: unique sample identifier
- `audio`: path to audio file (optional, used by runner if provided)
- `reference`: ground truth transcription
- `hypothesis`: ASR system output (empty string = silence/rejected)

## CLI usage

```bash
# Basic
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl

# With JSON report output
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl --output report.json
```

## HTTP API usage

```bash
curl -X POST http://localhost:8000/eval/cer \
  -H "Content-Type: application/json" \
  -d '{"pairs": [{"id": "s1", "reference": "안녕하세요", "hypothesis": "안녕"}]}'
```
