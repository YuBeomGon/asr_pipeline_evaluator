# CER Evaluation Protocol

## Formula

```
CER = (substitutions + deletions + insertions) / reference_character_count
```

- **Substitutions (S)**: a reference character replaced by a different character
- **Deletions (D)**: a reference character absent from the hypothesis
- **Insertions (I)**: a character in the hypothesis not in the reference
- **reference_character_count**: length of the normalized reference string

CER can exceed 1.0 if the hypothesis contains many spurious insertions.

## Normalization Pipeline

Applied to **both** reference and hypothesis before scoring:

1. **Unicode NFKC normalization** — decomposes and re-composes characters;
   covers NFC for Korean jamo; converts full-width ASCII to half-width.
2. **Lowercase** — `text.lower()`
3. **Strip and collapse whitespace** — `text.strip()` then `re.sub(r"\s+", " ", text)`
4. **Remove all spaces** — before character-level scoring, spaces are dropped.

### Korean-specific notes

- Korean characters (Hangul syllable blocks, U+AC00–U+D7A3) are treated as
  individual characters in the edit distance.
- Spaces between Korean words are removed by step 4; spacing differences do
  not affect CER.
- NFC ensures that Korean jamo written in decomposed form (NFD) are composed
  before comparison.

## CLI Usage

```bash
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl
python -m src.eval.cer_runner --manifest path/to/manifest.jsonl --output results.json
```

## Manifest Format

JSONL (one JSON object per line):

```json
{"id": "sample_001", "audio": "audio/sample_001.wav", "reference": "한국어 텍스트", "hypothesis": ""}
```

- `id` (required): unique sample identifier
- `reference` (required): ground-truth transcript
- `hypothesis` (required for meaningful CER, defaults to `""` if absent): ASR output
- `audio` (optional): path to audio file (not used for CER-only evaluation)

## API Usage

```bash
curl -X POST http://localhost:8000/eval/cer \
  -H "Content-Type: application/json" \
  -d '{"pairs": [{"id": "s1", "reference": "안녕하세요", "hypothesis": "안녕하세요"}]}'
```

## Edge Cases

| Scenario | Behaviour |
|----------|-----------|
| Empty reference + empty hypothesis | CER = 0.0 |
| Empty reference + non-empty hypothesis | CER = 1.0, all counted as insertions |
| Reference = hypothesis after normalization | CER = 0.0 |
| CER > 1.0 | Allowed when insertions > ref_len |
