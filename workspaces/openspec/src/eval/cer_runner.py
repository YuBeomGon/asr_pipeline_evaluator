"""
CLI entry point for batch CER evaluation from a JSONL manifest.

Usage:
    python -m src.eval.cer_runner --manifest path/to/manifest.jsonl
    python -m src.eval.cer_runner --manifest path/to/manifest.jsonl --output results.json

Manifest format (JSONL, one sample per line):
    {"id": "sample_001", "audio": "audio/sample_001.wav", "reference": "hello world", "hypothesis": "helo world"}

The "audio" field is optional for CER-only evaluation.
The "hypothesis" field is required; if absent, it defaults to "".
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .cer import CEREvaluator


def load_manifest(manifest_path: Path) -> list[dict]:
    """Load a JSONL manifest file and return a list of records."""
    records = []
    with open(manifest_path, encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                print(
                    f"ERROR: Line {line_no} in {manifest_path} is not valid JSON: {exc}",
                    file=sys.stderr,
                )
                sys.exit(1)

            # Validate required fields
            if "id" not in record:
                print(
                    f"ERROR: Line {line_no} missing required field 'id'",
                    file=sys.stderr,
                )
                sys.exit(1)
            if "reference" not in record:
                print(
                    f"ERROR: Line {line_no} missing required field 'reference'",
                    file=sys.stderr,
                )
                sys.exit(1)

            # hypothesis is required; default to empty string if absent
            record.setdefault("hypothesis", "")
            records.append(record)

    return records


def run(manifest_path: Path, output_path: Path | None = None) -> dict:
    """
    Run CER evaluation on a manifest file.

    Args:
        manifest_path: Path to the JSONL manifest.
        output_path: Optional path to write JSON results.

    Returns:
        Results dict with 'results' and 'aggregate' keys.
    """
    records = load_manifest(manifest_path)
    if not records:
        print("ERROR: Manifest is empty", file=sys.stderr)
        sys.exit(1)

    evaluator = CEREvaluator()
    aggregate = evaluator.evaluate_batch(records)

    results = {
        "results": [
            {
                "id": r.id,
                "reference": r.reference,
                "hypothesis": r.hypothesis,
                "cer": r.cer,
                "substitutions": r.substitutions,
                "deletions": r.deletions,
                "insertions": r.insertions,
                "reference_length": r.reference_length,
            }
            for r in aggregate.per_sample
        ],
        "aggregate": {
            "mean_cer": aggregate.mean_cer,
            "total_substitutions": aggregate.total_substitutions,
            "total_deletions": aggregate.total_deletions,
            "total_insertions": aggregate.total_insertions,
            "total_reference_length": aggregate.total_reference_length,
            "total_samples": aggregate.total_samples,
        },
    }

    # Print summary to stdout
    print(f"Evaluated {aggregate.total_samples} sample(s)")
    print(f"Mean CER:          {aggregate.mean_cer:.4f}")
    print(f"Total ref chars:   {aggregate.total_reference_length}")
    print(f"Total subs:        {aggregate.total_substitutions}")
    print(f"Total deletions:   {aggregate.total_deletions}")
    print(f"Total insertions:  {aggregate.total_insertions}")

    print("\nPer-sample CER:")
    for r in aggregate.per_sample:
        print(f"  [{r.id}] CER={r.cer:.4f}  ref_len={r.reference_length}  S={r.substitutions}  D={r.deletions}  I={r.insertions}")

    if output_path:
        output_path.write_text(
            json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"\nResults written to: {output_path}")

    return results


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch CER evaluation from a JSONL manifest"
    )
    parser.add_argument(
        "--manifest",
        required=True,
        type=Path,
        help="Path to JSONL manifest file",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path to write JSON results",
    )
    args = parser.parse_args()

    if not args.manifest.exists():
        print(f"ERROR: Manifest file not found: {args.manifest}", file=sys.stderr)
        sys.exit(1)

    run(args.manifest, args.output)


if __name__ == "__main__":
    main()
