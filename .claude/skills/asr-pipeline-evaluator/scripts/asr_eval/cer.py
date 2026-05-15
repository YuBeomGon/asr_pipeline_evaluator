"""Pure-Python CER utilities for ASR evaluation.

The implementation intentionally avoids external dependencies so it can act as the
reference calculation when comparing candidate ASR pipeline repositories.
"""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, Iterator, Optional


@dataclass
class CerResult:
    reference: str
    hypothesis: str
    normalized_reference: str
    normalized_hypothesis: str
    substitutions: int
    deletions: int
    insertions: int
    reference_chars: int
    cer: float

    @property
    def errors(self) -> int:
        return self.substitutions + self.deletions + self.insertions

    def to_dict(self) -> dict:
        data = asdict(self)
        data["errors"] = self.errors
        return data


def normalize_text(text: str, *, remove_spaces: bool = True, lowercase: bool = True) -> str:
    """Normalize text for character-level ASR comparison.

    Default policy:
    - unicode NFKC normalization
    - lowercase
    - trim and collapse whitespace
    - remove spaces for character-level CER

    Adjust remove_spaces=False for languages/tasks where spaces should count.
    """
    text = unicodedata.normalize("NFKC", text or "")
    if lowercase:
        text = text.lower()
    text = re.sub(r"\s+", " ", text.strip())
    if remove_spaces:
        text = text.replace(" ", "")
    return text


def _levenshtein_counts(ref: str, hyp: str) -> tuple[int, int, int]:
    """Return substitution, deletion, insertion counts for char sequences."""
    n, m = len(ref), len(hyp)
    # dp[i][j] = (cost, substitutions, deletions, insertions)
    dp: list[list[tuple[int, int, int, int]]] = [[(0, 0, 0, 0) for _ in range(m + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        cost, s, d, ins = dp[i - 1][0]
        dp[i][0] = (cost + 1, s, d + 1, ins)
    for j in range(1, m + 1):
        cost, s, d, ins = dp[0][j - 1]
        dp[0][j] = (cost + 1, s, d, ins + 1)

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if ref[i - 1] == hyp[j - 1]:
                candidates = [dp[i - 1][j - 1]]
            else:
                cost, s, d, ins = dp[i - 1][j - 1]
                candidates = [(cost + 1, s + 1, d, ins)]

            cost, s, d, ins = dp[i - 1][j]
            candidates.append((cost + 1, s, d + 1, ins))
            cost, s, d, ins = dp[i][j - 1]
            candidates.append((cost + 1, s, d, ins + 1))

            # Tie-break substitutions before deletions/insertions for stable reporting.
            dp[i][j] = min(candidates, key=lambda x: (x[0], x[2] + x[3], x[1]))

    _, substitutions, deletions, insertions = dp[n][m]
    return substitutions, deletions, insertions


def cer(reference: str, hypothesis: str, *, remove_spaces: bool = True, lowercase: bool = True) -> CerResult:
    norm_ref = normalize_text(reference, remove_spaces=remove_spaces, lowercase=lowercase)
    norm_hyp = normalize_text(hypothesis, remove_spaces=remove_spaces, lowercase=lowercase)
    s, d, i = _levenshtein_counts(norm_ref, norm_hyp)
    denominator = len(norm_ref)
    value = 0.0 if denominator == 0 and len(norm_hyp) == 0 else (s + d + i) / max(denominator, 1)
    return CerResult(
        reference=reference,
        hypothesis=hypothesis,
        normalized_reference=norm_ref,
        normalized_hypothesis=norm_hyp,
        substitutions=s,
        deletions=d,
        insertions=i,
        reference_chars=denominator,
        cer=value,
    )


def load_manifest(path: str | Path) -> list[dict]:
    records = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line_no, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSONL at {path}:{line_no}: {exc}") from exc
    return records


def evaluate_pairs(records: Iterable[dict], *, remove_spaces: bool = True, lowercase: bool = True) -> dict:
    per_sample = []
    total_errors = 0
    total_ref_chars = 0
    for idx, row in enumerate(records):
        ref = row.get("reference") or row.get("reference_text") or ""
        hyp = row.get("hypothesis") or row.get("hypothesis_text") or ""
        result = cer(ref, hyp, remove_spaces=remove_spaces, lowercase=lowercase)
        data = result.to_dict()
        data["id"] = row.get("id", f"sample-{idx+1}")
        per_sample.append(data)
        total_errors += result.errors
        total_ref_chars += max(result.reference_chars, 0)

    aggregate_cer = 0.0 if total_ref_chars == 0 and total_errors == 0 else total_errors / max(total_ref_chars, 1)
    return {
        "aggregate": {
            "samples": len(per_sample),
            "errors": total_errors,
            "reference_chars": total_ref_chars,
            "cer": aggregate_cer,
        },
        "per_sample": per_sample,
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Compute reference CER for a JSONL manifest.")
    parser.add_argument("manifest", help="JSONL with id, reference, hypothesis fields")
    parser.add_argument("--keep-spaces", action="store_true", help="Count spaces as CER characters")
    parser.add_argument("--case-sensitive", action="store_true", help="Do not lowercase before CER")
    args = parser.parse_args()

    output = evaluate_pairs(
        load_manifest(args.manifest),
        remove_spaces=not args.keep_spaces,
        lowercase=not args.case_sensitive,
    )
    print(json.dumps(output, ensure_ascii=False, indent=2))
