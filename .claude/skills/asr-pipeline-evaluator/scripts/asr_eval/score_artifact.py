"""Static and lightweight dynamic scoring for ASR serving pipeline repositories."""
from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

TEXT_EXTENSIONS = {
    ".py", ".md", ".txt", ".yaml", ".yml", ".json", ".toml", ".ini", ".cfg",
    ".sh", ".dockerfile", ".env", ".example", ".rst", ".js", ".ts", ".tsx", ".jsx",
}

DEFAULT_RUBRIC = {
    "functionality": 20,
    "asr_pipeline_structure": 15,
    "cer_evaluation": 15,
    "serving_api_quality": 15,
    "tests": 10,
    "operations": 10,
    "maintainability": 10,
    "documentation": 5,
}

@dataclass
class Evidence:
    category: str
    points: float
    max_points: float
    reason: str
    files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "category": self.category,
            "points": round(self.points, 2),
            "max_points": self.max_points,
            "reason": self.reason,
            "files": self.files[:10],
        }


def load_rubric(path: str | Path | None) -> dict:
    if not path:
        return dict(DEFAULT_RUBRIC)
    p = Path(path)
    if not p.exists():
        return dict(DEFAULT_RUBRIC)
    text = p.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore
        data = yaml.safe_load(text) or {}
        weights = data.get("weights", data)
        return {k: float(v) for k, v in weights.items() if isinstance(v, (int, float))}
    except Exception:
        weights = {}
        for line in text.splitlines():
            m = re.match(r"^\s*([a-zA-Z0-9_\-]+)\s*:\s*([0-9.]+)\s*$", line)
            if m:
                weights[m.group(1).replace("-", "_")] = float(m.group(2))
        return weights or dict(DEFAULT_RUBRIC)


def iter_text_files(root: Path, max_files: int = 600, max_bytes: int = 2_000_000) -> Iterable[Path]:
    skipped_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}
    count = 0
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skipped_dirs]
        for name in filenames:
            p = Path(dirpath) / name
            if count >= max_files:
                return
            if p.suffix.lower() in TEXT_EXTENSIONS or name in {"Dockerfile", "Makefile", "README"}:
                try:
                    if p.stat().st_size <= max_bytes:
                        count += 1
                        yield p
                except OSError:
                    continue


def collect_corpus(root: Path) -> tuple[str, dict[str, str]]:
    files: dict[str, str] = {}
    chunks = []
    for p in iter_text_files(root):
        try:
            rel = str(p.relative_to(root))
            text = p.read_text(encoding="utf-8", errors="ignore")
            files[rel] = text
            chunks.append(f"\n# FILE: {rel}\n{text[:20000]}")
        except Exception:
            continue
    return "\n".join(chunks).lower(), files


def find_files(files: dict[str, str], patterns: list[str]) -> list[str]:
    out = []
    for name, text in files.items():
        hay = (name + "\n" + text).lower()
        if any(re.search(p, hay, flags=re.I | re.M) for p in patterns):
            out.append(name)
    return sorted(set(out))


def add(evidence: list[Evidence], category: str, points: float, max_points: float, reason: str, files: list[str] | None = None) -> None:
    evidence.append(Evidence(category, points, max_points, reason, files or []))


def score_static(root: str | Path, rubric_path: str | Path | None = None) -> dict:
    root = Path(root).resolve()
    weights = load_rubric(rubric_path)
    corpus, files = collect_corpus(root)
    evidence: list[Evidence] = []

    file_names = set(files.keys())
    readmes = [f for f in file_names if Path(f).name.lower() in {"readme.md", "readme", "architecture.md", "runbook.md"}]
    py_files = [f for f in file_names if f.endswith(".py")]

    def has(*patterns: str) -> bool:
        return any(re.search(p, corpus, flags=re.I | re.M) for p in patterns)

    def fmatch(*patterns: str) -> list[str]:
        return find_files(files, list(patterns))

    cat = "functionality"
    add(evidence, cat, 5 if has(r"/transcribe", r"transcribe\s*\(") else 0, 5, "transcription endpoint or handler", fmatch(r"/transcribe", r"transcribe\s*\("))
    add(evidence, cat, 3 if has(r"uploadfile", r"multipart", r"audio_file", r"file\s*:", r"wav|flac|mp3") else 0, 3, "audio upload/input handling", fmatch(r"uploadfile|multipart|wav|flac|mp3"))
    add(evidence, cat, 4 if has(r"class\s+asrbackend", r"protocol\s*\(.*asr", r"abstract.*asr", r"mockasrbackend", r"asrbackend") else 0, 4, "ASR backend abstraction", fmatch(r"asrbackend|mockasrbackend|abstract.*asr"))
    add(evidence, cat, 3 if has(r"transcript", r"confidence", r"request_id", r"duration") and has(r"timing|latency|elapsed") else 0, 3, "response schema includes transcript/confidence/request/timing fields", fmatch(r"transcript|confidence|request_id|duration|latency|timing"))
    add(evidence, cat, 3 if has(r"try:", r"except", r"raise\s+http", r"error", r"timeout") else 0, 3, "error handling paths", fmatch(r"except|httpexception|timeout|error"))
    add(evidence, cat, 2 if has(r"pydantic", r"settings", r"env", r"config", r"\.env") else 0, 2, "configuration/env management", fmatch(r"settings|config|\.env|pydantic"))

    cat = "asr_pipeline_structure"
    add(evidence, cat, 3 if has(r"preprocess", r"resample", r"normaliz.*audio", r"sample_rate") else 0, 3, "preprocessing layer", fmatch(r"preprocess|resample|sample_rate|normaliz.*audio"))
    add(evidence, cat, 3 if has(r"chunk", r"batch", r"vad", r"window") else 0, 3, "chunking/batching/VAD consideration", fmatch(r"chunk|batch|vad|window"))
    add(evidence, cat, 3 if has(r"asrbackend", r"whisper", r"triton", r"remote.*asr", r"mockasr") else 0, 3, "model adapter boundary", fmatch(r"asrbackend|whisper|triton|remote.*asr|mockasr"))
    add(evidence, cat, 3 if has(r"postprocess", r"normalize_text", r"punctuation", r"transcript.*normal") else 0, 3, "postprocessing/transcript normalization", fmatch(r"postprocess|normalize_text|transcript.*normal|punctuation"))
    add(evidence, cat, 3 if has(r"async", r"queue", r"worker", r"concurrent", r"stream") else 0, 3, "async/queue/streaming extensibility", fmatch(r"async|queue|worker|concurrent|stream"))

    cat = "cer_evaluation"
    add(evidence, cat, 5 if has(r"character error rate", r"\bcer\b", r"substitution", r"levenshtein", r"jiwer") else 0, 5, "CER calculation implementation/reference", fmatch(r"\bcer\b|character error rate|levenshtein|jiwer"))
    add(evidence, cat, 3 if has(r"jsonl", r"manifest", r"reference", r"hypothesis") else 0, 3, "manifest/reference/hypothesis support", fmatch(r"jsonl|manifest|reference|hypothesis"))
    add(evidence, cat, 3 if has(r"unicode", r"lower", r"collapse", r"whitespace", r"normalization policy") else 0, 3, "explicit CER normalization policy", fmatch(r"unicode|lower|collapse|whitespace|normalization policy"))
    add(evidence, cat, 2 if has(r"aggregate", r"per_sample", r"per-sample", r"mean", r"summary") else 0, 2, "per-sample and aggregate metrics", fmatch(r"aggregate|per_sample|per-sample|summary"))
    add(evidence, cat, 2 if has(r"empty", r"missing", r"invalid", r"zero", r"division") else 0, 2, "CER failure/edge-case handling", fmatch(r"empty|missing|invalid|zero|division"))

    cat = "serving_api_quality"
    add(evidence, cat, 3 if has(r"openapi", r"fastapi", r"schema", r"pydantic", r"response_model") else 0, 3, "API schema/OpenAPI clarity", fmatch(r"openapi|fastapi|schema|response_model|pydantic"))
    add(evidence, cat, 3 if has(r"latency", r"duration", r"elapsed", r"time.perf_counter") else 0, 3, "latency measurement", fmatch(r"latency|duration|elapsed|perf_counter"))
    add(evidence, cat, 3 if has(r"async", r"worker", r"queue", r"semaphore", r"concurrent") else 0, 3, "concurrency consideration", fmatch(r"async|worker|queue|semaphore|concurrent"))
    add(evidence, cat, 2 if has(r"timeout", r"retry", r"backoff", r"circuit") else 0, 2, "timeout/retry/backoff", fmatch(r"timeout|retry|backoff|circuit"))
    add(evidence, cat, 2 if has(r"stream", r"sse", r"websocket", r"chunked") else 0, 2, "streaming extension path", fmatch(r"stream|websocket|sse|chunked"))
    add(evidence, cat, 2 if has(r"/healthz", r"/health", r"/metrics", r"prometheus") else 0, 2, "health and metrics endpoints", fmatch(r"/healthz|/health|/metrics|prometheus"))

    cat = "tests"
    test_files = [f for f in file_names if re.search(r"(^|/)tests?/|test_.*\.py$|.*_test\.py$", f)]
    add(evidence, cat, 3 if test_files and has(r"pytest|unittest|assert") else 0, 3, "unit tests", test_files[:10])
    add(evidence, cat, 3 if test_files and has(r"testclient|httpx|requests|integration|/transcribe") else 0, 3, "integration/API tests", test_files[:10])
    add(evidence, cat, 2 if has(r"eval.*smoke|cer.*test|manifest.*test|test.*cer") else 0, 2, "eval smoke tests", fmatch(r"eval.*smoke|cer.*test|manifest.*test|test.*cer"))
    add(evidence, cat, 2 if has(r"github/workflows|makefile|tox|nox|pytest", r"ci") else 0, 2, "CI-ready test command", fmatch(r"github/workflows|makefile|tox|nox|pytest|ci"))

    cat = "operations"
    add(evidence, cat, 3 if any(Path(f).name.lower() == "dockerfile" for f in file_names) or has(r"docker-compose|compose.yaml|compose.yml") else 0, 3, "Docker or compose support", fmatch(r"docker|compose"))
    add(evidence, cat, 2 if has(r"request_id", r"trace", r"correlation", r"logging") else 0, 2, "structured logging/request tracing", fmatch(r"request_id|trace|correlation|logging"))
    add(evidence, cat, 2 if has(r"metrics", r"prometheus", r"histogram", r"counter") else 0, 2, "metrics", fmatch(r"metrics|prometheus|histogram|counter"))
    add(evidence, cat, 2 if has(r"runbook", r"deploy", r"kubernetes", r"k8s", r"helm") else 0, 2, "deployment/runbook", fmatch(r"runbook|deploy|kubernetes|k8s|helm"))
    add(evidence, cat, 1 if has(r"rollback", r"fallback", r"degrad", r"mockasr") else 0, 1, "rollback/fallback consideration", fmatch(r"rollback|fallback|degrad|mockasr"))

    cat = "maintainability"
    src_like = [f for f in file_names if f.startswith(("src/", "app/", "service/", "asr")) and f.endswith(".py")]
    add(evidence, cat, 3 if len(src_like) >= 3 or has(r"routers?", r"services?", r"adapters?", r"schemas?") else 0, 3, "module boundaries", src_like[:10] or fmatch(r"router|service|adapter|schema"))
    add(evidence, cat, 2 if has(r"settings", r"config", r"env", r"toml", r"yaml") else 0, 2, "configuration separation", fmatch(r"settings|config|env|toml|yaml"))
    add(evidence, cat, 2 if any(Path(f).name.lower() in {"requirements.txt", "pyproject.toml", "poetry.lock", "uv.lock", "pdm.lock"} for f in file_names) else 0, 2, "dependency management", [f for f in file_names if Path(f).name.lower() in {"requirements.txt", "pyproject.toml", "poetry.lock", "uv.lock", "pdm.lock"}])
    add(evidence, cat, 2 if len(py_files) > 0 and not has(r"mega|god object") else (1 if py_files else 0), 2, "basic code organization/simplicity", py_files[:10])
    add(evidence, cat, 1 if has(r"mockasr|whisper|triton|remote.*asr|backend") else 0, 1, "model/vendor replacement path", fmatch(r"mockasr|whisper|triton|remote.*asr|backend"))

    cat = "documentation"
    add(evidence, cat, 1 if has(r"architecture", r"component", r"sequence", r"pipeline") and readmes else 0, 1, "architecture documentation", readmes)
    add(evidence, cat, 1 if has(r"eval protocol", r"cer", r"reference", r"hypothesis") else 0, 1, "eval protocol", fmatch(r"eval protocol|cer|reference|hypothesis"))
    add(evidence, cat, 1 if has(r"curl", r"/transcribe", r"api usage", r"request") else 0, 1, "API usage examples", fmatch(r"curl|/transcribe|api usage|request"))
    add(evidence, cat, 1 if has(r"implementation scope", r"out of scope", r"must implement", r"candidate scope") else 0, 1, "implementation scope documentation", fmatch(r"implementation scope|out of scope|must implement|candidate scope"))
    add(evidence, cat, 1 if has(r"known limitations", r"limitations", r"future work", r"todo") else 0, 1, "known limitations", fmatch(r"known limitations|limitations|future work|todo"))

    raw_by_category = {k: 0.0 for k in weights}
    max_by_category = {k: 0.0 for k in weights}
    for ev in evidence:
        raw_by_category.setdefault(ev.category, 0.0)
        max_by_category.setdefault(ev.category, 0.0)
        raw_by_category[ev.category] += ev.points
        max_by_category[ev.category] += ev.max_points

    normalized = {}
    total = 0.0
    for cat_name, target_weight in weights.items():
        max_points = max_by_category.get(cat_name, 0.0)
        raw = raw_by_category.get(cat_name, 0.0)
        score = 0.0 if max_points <= 0 else (raw / max_points) * float(target_weight)
        normalized[cat_name] = round(score, 2)
        total += score

    return {
        "target": str(root),
        "total_score": round(total, 2),
        "weights": weights,
        "category_scores": normalized,
        "raw_category_points": {k: round(v, 2) for k, v in raw_by_category.items()},
        "raw_category_max": {k: round(v, 2) for k, v in max_by_category.items()},
        "evidence": [ev.to_dict() for ev in evidence],
        "file_count_scanned": len(files),
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Score one ASR pipeline artifact statically.")
    parser.add_argument("target")
    parser.add_argument("--rubric")
    parser.add_argument("--out")
    args = parser.parse_args()
    result = score_static(args.target, args.rubric)
    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
    else:
        print(text)
