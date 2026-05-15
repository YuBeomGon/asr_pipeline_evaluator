"""CLI entrypoint for CER evaluation from a JSONL manifest.

Usage:
    python -m src.eval.cer_runner --manifest path/to/manifest.jsonl
    python -m src.eval.cer_runner --manifest path/to/manifest.jsonl --output report.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .cer import compute_cer, aggregate_cer, CERResult


def load_manifest(path: Path) -> list[dict]:
    """Load JSONL manifest. Each line: {"id": ..., "reference": ..., "hypothesis": ...}"""
    records = []
    with open(path, encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"WARNING: Line {lineno} is not valid JSON, skipping: {exc}", file=sys.stderr)
    return records


def run(manifest_path: Path, output_path: Path | None = None) -> dict:
    records = load_manifest(manifest_path)
    if not records:
        print("ERROR: Manifest is empty.", file=sys.stderr)
        sys.exit(1)

    results: list[CERResult] = []
    for rec in records:
        sample_id = rec.get("id", "")
        ref = rec.get("reference", "")
        hyp = rec.get("hypothesis", "")
        result = compute_cer(ref, hyp, sample_id=sample_id)
        results.append(result)

    agg = aggregate_cer(results)

    report = {
        "aggregate": {
            "num_samples": agg.num_samples,
            "total_edit_distance": agg.total_edit_distance,
            "total_reference_length": agg.total_reference_length,
            "macro_cer": round(agg.macro_cer, 6),
            "micro_cer": round(agg.micro_cer, 6),
        },
        "samples": [
            {
                "id": r.id,
                "reference_normalized": r.reference_normalized,
                "hypothesis_normalized": r.hypothesis_normalized,
                "edit_distance": r.edit_distance,
                "reference_length": r.reference_length,
                "cer": round(r.cer, 6),
            }
            for r in results
        ],
    }

    if output_path:
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Report written to {output_path}", file=sys.stderr)

    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Compute CER from a JSONL manifest")
    parser.add_argument("--manifest", required=True, type=Path, help="Path to .jsonl manifest")
    parser.add_argument("--output", type=Path, default=None, help="Write JSON report to this file")
    args = parser.parse_args()

    report = run(args.manifest, args.output)

    # Print summary to stdout
    agg = report["aggregate"]
    print(f"Samples     : {agg['num_samples']}")
    print(f"Micro CER   : {agg['micro_cer']:.4f}")
    print(f"Macro CER   : {agg['macro_cer']:.4f}")
    print(f"Edit dist   : {agg['total_edit_distance']}")
    print(f"Ref chars   : {agg['total_reference_length']}")


if __name__ == "__main__":
    main()
