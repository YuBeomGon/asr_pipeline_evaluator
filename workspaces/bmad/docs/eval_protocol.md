# CER Evaluation Protocol

**BMAD Phase**: Architect  
**Date**: 2026-05-15

---

## 1. Formula

```
CER = (S + D + I) / N
```

Where:
- **S** = character substitutions
- **D** = character deletions  
- **I** = character insertions
- **N** = number of characters in the *reference* after normalization

If N = 0 (empty reference after normalization), CER = 0.0 for that sample.

---

## 2. Normalization Pipeline

Applied identically to both reference and hypothesis before scoring:

```
Step 1: Unicode NFKC normalization
        unicodedata.normalize("NFKC", text)
        → resolves compatibility equivalents (e.g., ＡＢＣ → ABC, ㈜ → (주))

Step 2: Lowercase
        text.lower()

Step 3: Collapse whitespace
        re.sub(r'\s+', ' ', text).strip()

Step 4: Remove all spaces
        text.replace(' ', '')
        → CER is character-level; spaces are not scored
```

Note: NFC normalization is used for final transcript output from the `/transcribe` endpoint, but **NFKC is used for CER evaluation** to handle compatibility characters.

---

## 3. Korean Language Handling

- Korean Hangul characters (U+AC00–U+D7A3) survive NFKC normalization intact.
- Korean jamo (U+3131–U+318E) are preserved.
- Full-width Latin (U+FF01–U+FF5E) is normalized to ASCII equivalents.
- Korean punctuation (。,、·) and spaces (U+3000, U+00A0) are collapsed.

---

## 4. Edit Distance Algorithm

Levenshtein distance computed at the character level using dynamic programming.

Costs: substitution = 1, deletion = 1, insertion = 1.

Reference implementation: `src/eval/cer.py::levenshtein_distance(a: str, b: str) -> tuple[int, int, int]`

---

## 5. Manifest Format

JSONL file, one object per line:

```json
{"id": "sample_001", "audio": "audio/sample_001.wav", "reference": "한국어 텍스트", "hypothesis": ""}
```

Fields:
| Field | Required | Description |
|-------|----------|-------------|
| `id` | yes | Unique sample identifier |
| `audio` | yes | Path to audio file (relative or absolute) |
| `reference` | yes | Ground-truth transcript |
| `hypothesis` | yes | ASR hypothesis (may be empty string for offline eval) |

---

## 6. Aggregate Metrics

Reported for each manifest run:
- `mean_cer`: arithmetic mean of per-sample CER
- `total_samples`: count of evaluated samples
- `total_reference_chars`: sum of reference character lengths (post-normalization)
- `total_errors`: sum of all edit operations across samples

---

## 7. Example

```
reference:  "안녕하세요"
hypothesis: "안녕 하세요"

After normalization:
  ref_chars:  ['안','녕','하','세','요']   N=5
  hyp_chars:  ['안','녕','하','세','요']   (space removed)

Edit distance: 0 substitutions, 0 deletions, 0 insertions
CER = 0/5 = 0.0
```

```
reference:  "테스트"
hypothesis: "텍스트"

ref_chars:  ['테','스','트']   N=3
hyp_chars:  ['텍','스','트']

Edit distance: 1 substitution (테→텍)
CER = 1/3 ≈ 0.333
```
