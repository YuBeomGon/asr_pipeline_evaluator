"""Optional runtime test execution for candidate repositories."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def has_tests(target: Path) -> bool:
    if (target / "tests").exists():
        return True
    return any(p.name.startswith("test_") and p.suffix == ".py" for p in target.rglob("*.py"))


def _find_python(target: Path) -> str:
    for candidate in [target / ".venv" / "bin" / "python", target / ".venv" / "bin" / "python3"]:
        if candidate.exists():
            return str(candidate)
    return sys.executable


def run_pytest(target: str | Path, timeout_seconds: int = 120) -> dict:
    target = Path(target).resolve()
    if not has_tests(target):
        return {"available": False, "passed": False, "reason": "no tests detected"}

    python = _find_python(target)
    cmd = [python, "-m", "pytest", "-q"]
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(target),
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout_seconds,
        )
        return {
            "available": True,
            "passed": proc.returncode == 0,
            "returncode": proc.returncode,
            "command": " ".join(cmd),
            "stdout_tail": proc.stdout[-4000:],
            "stderr_tail": proc.stderr[-4000:],
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "available": True,
            "passed": False,
            "timeout": True,
            "command": " ".join(cmd),
            "stdout_tail": (exc.stdout or "")[-4000:] if isinstance(exc.stdout, str) else "",
            "stderr_tail": (exc.stderr or "")[-4000:] if isinstance(exc.stderr, str) else "",
        }
    except Exception as exc:
        return {"available": True, "passed": False, "error": repr(exc), "command": " ".join(cmd)}


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("target")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    print(json.dumps(run_pytest(args.target, args.timeout), ensure_ascii=False, indent=2))
