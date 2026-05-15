from __future__ import annotations
"""
CLI entry point for batch CER evaluation.

Spec ref: .specify/asr-pipeline-spec.md § FR-013
  python -m src.eval.cer_runner --manifest <path> [--output <path>]

Spec ref: .specify/asr-pipeline-spec.md § FR-012
  JSONL manifest format: {"id":"...", "audio":"...", "reference":"...", "hypothesis":""}

Usage:
    python -m src.eval.cer_runner --manifest path/to/manifest.jsonl
    python -m src.eval.cer_runner --manifest path/to/manifest.jsonl --output results.json
"""

import argparse
import json
import sys
import warnings
from pathlib import Path

from src.eval.cer import compute_cer_batch, CERBatchResult


def load_manifest(manifest_path: Path) -> list[dict]:
    """
    Load a JSONL manifest file.

    Spec ref: .specify/asr-pipeline-spec.md § FR-012
      Fields: id, audio, reference, hypothesis
      Fields `audio` and `hypothesis` are optional.

    Returns:
        List of dicts with at least 'id' and 'reference'.

    Raises:
        SystemExit: If the file cannot be read or parsed.
    """
    if not manifest_path.exists():
        print(f"ERROR: manifest file not found: {manifest_path}", file=sys.stderr)
        sys.exit(1)

    pairs: list[dict] = []
    with manifest_path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as exc:
                print(
                    f"WARNING: skipping malformed JSONL at line {lineno}: {exc}",
                    file=sys.stderr,
                )
                continue

            sample_id = obj.get("id", f"sample_{lineno:04d}")
            reference = obj.get("reference", "")
            hypothesis = obj.get("hypothesis", "")

            if not reference:
                warnings.warn(
                    f"Sample '{sample_id}' has empty reference; will be excluded from aggregate CER.",
                    stacklevel=2,
                )

            pairs.append({
                "id": sample_id,
                "reference": reference,
                "hypothesis": hypothesis,
            })

    return pairs


def print_results(result: CERBatchResult) -> None:
    """Print CER results as JSON to stdout."""
    output = {
        "overall_cer": result.overall_cer,
        "total_reference_chars": result.total_reference_chars,
        "total_edits": result.total_edits,
        "num_samples": len(result.pairs),
        "num_scored": sum(1 for p in result.pairs if p.cer is not None),
        "pairs": [
            {
                "id": p.id,
                "cer": p.cer,
                "reference_chars": p.reference_chars,
                "edits": p.edits,
            }
            for p in result.pairs
        ],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))


def main(argv: list[str] | None = None) -> int:
    """
    Main entry point for the CER runner CLI.

    Returns:
        0 on success, 1 on error.
    """
    parser = argparse.ArgumentParser(
        description="Batch CER evaluation from a JSONL manifest.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m src.eval.cer_runner --manifest manifest.jsonl
  python -m src.eval.cer_runner --manifest manifest.jsonl --output results.json
        """,
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
        help="Optional path to write JSON results (default: stdout)",
    )

    args = parser.parse_args(argv)

    pairs = load_manifest(args.manifest)
    if not pairs:
        print("ERROR: no valid samples found in manifest", file=sys.stderr)
        return 1

    result = compute_cer_batch(pairs)

    if args.output:
        output_data = {
            "overall_cer": result.overall_cer,
            "total_reference_chars": result.total_reference_chars,
            "total_edits": result.total_edits,
            "num_samples": len(result.pairs),
            "num_scored": sum(1 for p in result.pairs if p.cer is not None),
            "pairs": [
                {
                    "id": p.id,
                    "cer": p.cer,
                    "reference_chars": p.reference_chars,
                    "edits": p.edits,
                }
                for p in result.pairs
            ],
        }
        args.output.write_text(
            json.dumps(output_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Results written to {args.output}", file=sys.stderr)
    else:
        print_results(result)

    return 0


if __name__ == "__main__":
    sys.exit(main())
