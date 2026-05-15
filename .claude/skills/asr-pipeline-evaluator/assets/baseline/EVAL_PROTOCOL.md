# CER Evaluation Protocol

Use character error rate:

```text
CER = (substitutions + deletions + insertions) / reference_character_count
```

## Normalization

- Unicode NFKC.
- Lowercase.
- Trim and collapse whitespace.
- Remove spaces before character-level scoring unless the experiment declares otherwise.

## Manifest format

JSONL, one sample per line:

```json
{"id":"sample_001","audio":"audio/sample_001.wav","reference":"hello world","hypothesis":"helo world"}
```

The `audio` field is optional for CER-only sanity checks.
