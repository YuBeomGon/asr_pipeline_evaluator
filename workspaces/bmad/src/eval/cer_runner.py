from __future__ import annotations
"""CER runner CLI.

BMAD Developer: Run as `python -m src.eval.cer_runner --manifest <path>`

Reads a JSONL manifest (one JSON object per line), computes per-sample CER,
prints aggregate, and optionally writes results to --output JSONL file.

Manifest JSONL format:
  {"id": "s1", "audio": "audio/s1.wav", "reference": "한국어", "hypothesis": ""}

The 'hypothesis' field may be empty (offline evaluation mode).
The 'audio' field is present for format compatibility but is not used by the
CLI runner (audio is already transcribed — hypothesis is the ASR output).
"""
import argparse
import json
import sys
from pathlib import Path

from .cer import CERCalculator


def load_manifest(manifest_path: str) -> list[dict]:
    """Load JSONL manifest file."""
    path = Path(manifest_path)
    if not path.exists():
        print(f"ERROR: Manifest file not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    records: list[dict] = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"ERROR: Invalid JSON on line {lineno}: {e}", file=sys.stderr)
                sys.exit(1)

            for field in ("id", "reference", "hypothesis"):
                if field not in record:
                    print(
                        f"ERROR: Missing field '{field}' on line {lineno}: {line}",
                        file=sys.stderr,
                    )
                    sys.exit(1)

            records.append(record)

    return records


def run(manifest_path: str, output_path: str | None = None) -> dict:
    """Run CER evaluation on a manifest file.

    Returns:
        dict with 'results' and 'aggregate' keys.
    """
    calculator = CERCalculator()
    pairs = load_manifest(manifest_path)

    results, aggregate = calculator.compute_batch(pairs)

    # Format output
    output: dict = {
        "results": [
            {
                "id": r.id,
                "reference": r.reference,
                "hypothesis": r.hypothesis,
                "cer": round(r.cer, 6),
                "substitutions": r.substitutions,
                "deletions": r.deletions,
                "insertions": r.insertions,
                "reference_length": r.reference_length,
            }
            for r in results
        ],
        "aggregate": {
            "mean_cer": round(aggregate.mean_cer, 6),
            "total_samples": aggregate.total_samples,
            "total_reference_chars": aggregate.total_reference_chars,
            "total_errors": aggregate.total_errors,
        },
    }

    # Print each result as JSONL
    for result in output["results"]:
        print(json.dumps(result, ensure_ascii=False))

    # Print aggregate
    print(json.dumps({"aggregate": output["aggregate"]}, ensure_ascii=False))

    # Write to output file if specified
    if output_path:
        out_path = Path(output_path)
        with open(out_path, "w", encoding="utf-8") as f:
            for result in output["results"]:
                f.write(json.dumps(result, ensure_ascii=False) + "\n")
            f.write(json.dumps({"aggregate": output["aggregate"]}, ensure_ascii=False) + "\n")
        print(f"Results written to: {out_path}", file=sys.stderr)

    return output


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compute CER from a JSONL manifest file",
        prog="python -m src.eval.cer_runner",
    )
    parser.add_argument(
        "--manifest",
        required=True,
        help="Path to JSONL manifest file",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional path to write JSONL results",
    )
    args = parser.parse_args()

    run(manifest_path=args.manifest, output_path=args.output)


if __name__ == "__main__":
    main()
