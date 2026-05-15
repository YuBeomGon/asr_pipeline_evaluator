#!/usr/bin/env python3
"""Run a fair ASR serving pipeline bakeoff across candidate repositories."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from asr_eval.cer import evaluate_pairs, load_manifest
from asr_eval.score_artifact import score_static
from asr_eval.test_runner import run_pytest
from asr_eval.api_smoke import probe as api_probe
from asr_eval.report import write_json, leaderboard_markdown, scorecard_markdown, failure_analysis_markdown


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Compare ASR serving pipeline artifacts.")
    parser.add_argument("--targets", nargs="+", required=True, help="Candidate repository directories")
    parser.add_argument("--labels", nargs="*", help="Optional labels matching targets")
    parser.add_argument("--rubric", help="Rubric YAML path")
    parser.add_argument("--manifest", help="JSONL with reference/hypothesis pairs for reference CER sanity report")
    parser.add_argument("--out", default="reports", help="Output report directory")
    parser.add_argument("--run-pytest", action="store_true", help="Run pytest inside each target if tests are detected")
    parser.add_argument("--pytest-timeout", type=int, default=120)
    parser.add_argument("--api-base-urls", nargs="*", help="Optional base URLs matching targets for API smoke checks")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)

    labels = args.labels or [Path(t).name for t in args.targets]
    if len(labels) != len(args.targets):
        raise SystemExit("--labels must have the same length as --targets")
    if args.api_base_urls and len(args.api_base_urls) != len(args.targets):
        raise SystemExit("--api-base-urls must have the same length as --targets")

    results = []
    for idx, target in enumerate(args.targets):
        label = labels[idx]
        result = score_static(target, args.rubric)
        result["label"] = label

        if args.run_pytest:
            result["pytest"] = run_pytest(target, timeout_seconds=args.pytest_timeout)
        else:
            result["pytest"] = {"available": False, "reason": "not requested; pass --run-pytest to enable"}

        if args.api_base_urls:
            result["api_smoke"] = api_probe(args.api_base_urls[idx])

        results.append(result)
        write_json(out / f"score-{label}.json", result)
        (out / f"scorecard-{label}.md").write_text(scorecard_markdown(result), encoding="utf-8")

    (out / "leaderboard.md").write_text(leaderboard_markdown(results), encoding="utf-8")
    (out / "failure-analysis.md").write_text(failure_analysis_markdown(results), encoding="utf-8")
    write_json(out / "all-scores.json", {"results": results})

    if args.manifest:
        cer_result = evaluate_pairs(load_manifest(args.manifest))
        write_json(out / "reference-cer.json", cer_result)

    print(f"Wrote reports to {out}")
    print((out / "leaderboard.md").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
