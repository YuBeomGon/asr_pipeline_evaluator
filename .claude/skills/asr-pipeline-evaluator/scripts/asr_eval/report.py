"""Report generation for ASR pipeline evaluator."""
from __future__ import annotations

import json
from pathlib import Path


def write_json(path: str | Path, data: dict) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _fmt_score(value: float) -> str:
    return f"{value:.2f}"


def leaderboard_markdown(results: list[dict]) -> str:
    ranked = sorted(results, key=lambda r: r.get("total_score", 0), reverse=True)
    lines = [
        "# ASR Pipeline Bakeoff Leaderboard",
        "",
        "| Rank | Candidate | Score | Pytest | Notes |",
        "|---:|---|---:|---|---|",
    ]
    for i, r in enumerate(ranked, 1):
        label = r.get("label", Path(r.get("target", "candidate")).name)
        test = r.get("pytest", {})
        if not test.get("available"):
            pytest_status = "not detected"
        else:
            pytest_status = "pass" if test.get("passed") else "fail"
        notes = []
        if r.get("file_count_scanned", 0) == 0:
            notes.append("no readable files")
        if r.get("api_smoke"):
            notes.append("api smoke included")
        lines.append(
            f"| {i} | {label} | {_fmt_score(float(r.get('total_score', 0)))} | "
            f"{pytest_status} | {', '.join(notes) or '-'} |"
        )
    lines.append("")
    return "\n".join(lines)


def scorecard_markdown(result: dict) -> str:
    label = result.get("label", Path(result.get("target", "candidate")).name)
    lines = [
        f"# Scorecard: {label}",
        "",
        f"Target: `{result.get('target')}`",
        "",
        f"Total score: **{_fmt_score(float(result.get('total_score', 0)))} / 100**",
        "",
    ]
    lines.extend(["## Category scores", "", "| Category | Score |", "|---|---:|"])
    for cat, score in result.get("category_scores", {}).items():
        lines.append(f"| {cat} | {_fmt_score(float(score))} |")
    lines.append("")

    lines.extend(["## Evidence", "", "| Category | Points | Finding | Files |", "|---|---:|---|---|"])
    for ev in result.get("evidence", []):
        files = ", ".join(ev.get("files", [])[:3]) or "-"
        lines.append(f"| {ev.get('category')} | {ev.get('points')}/{ev.get('max_points')} | {ev.get('reason')} | {files} |")
    lines.append("")

    test = result.get("pytest")
    if test:
        lines.append("## Pytest")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(test, ensure_ascii=False, indent=2)[:6000])
        lines.append("```")
        lines.append("")

    api = result.get("api_smoke")
    if api:
        lines.append("## API smoke")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(api, ensure_ascii=False, indent=2)[:4000])
        lines.append("```")
        lines.append("")
    return "\n".join(lines)


def failure_analysis_markdown(results: list[dict]) -> str:
    lines = ["# Failure Analysis", ""]
    for r in sorted(results, key=lambda x: x.get("total_score", 0)):
        label = r.get("label", Path(r.get("target", "candidate")).name)
        lines.append(f"## {label}")
        lines.append("")
        weak = []
        for cat, score in r.get("category_scores", {}).items():
            max_score = float(r.get("weights", {}).get(cat, 0) or 0)
            if max_score and float(score) < max_score * 0.5:
                weak.append((cat, score, max_score))
        if not weak:
            lines.append("No category below 50% of its weight in the automated rubric.")
        else:
            lines.append("Weak categories:")
            for cat, score, max_score in weak:
                lines.append(f"- {cat}: {_fmt_score(float(score))} / {_fmt_score(max_score)}")
        test = r.get("pytest", {})
        if test.get("available") and not test.get("passed"):
            lines.append("- pytest failed or timed out; inspect scorecard stderr/stdout tails.")
        lines.append("")
    return "\n".join(lines)
