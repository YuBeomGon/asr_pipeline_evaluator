"""HTTP smoke probes for a running ASR serving candidate.

This module does not start target services by default. For fairness, start each
candidate with the same policy, then pass --base-url to probe health/metrics.
"""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path


def _request(method: str, url: str, data: bytes | None = None, headers: dict | None = None, timeout: float = 5.0) -> dict:
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    start = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read(2000).decode("utf-8", errors="replace")
            elapsed = time.perf_counter() - start
            return {"ok": 200 <= resp.status < 500, "status": resp.status, "elapsed_seconds": elapsed, "body_head": body[:1000]}
    except urllib.error.HTTPError as exc:
        body = exc.read(2000).decode("utf-8", errors="replace")
        return {"ok": True, "status": exc.code, "elapsed_seconds": time.perf_counter() - start, "body_head": body[:1000]}
    except Exception as exc:
        return {"ok": False, "error": repr(exc), "elapsed_seconds": time.perf_counter() - start}


def probe(base_url: str) -> dict:
    base = base_url.rstrip("/")
    checks = {
        "healthz": _request("GET", f"{base}/healthz"),
        "health": _request("GET", f"{base}/health"),
        "metrics": _request("GET", f"{base}/metrics"),
    }
    health_ok = checks["healthz"].get("ok") or checks["health"].get("ok")
    metrics_ok = checks["metrics"].get("ok") and checks["metrics"].get("status", 0) < 500
    return {
        "base_url": base_url,
        "health_ok": bool(health_ok),
        "metrics_ok": bool(metrics_ok),
        "checks": checks,
    }


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Probe a running ASR service.")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    print(json.dumps(probe(args.base_url), ensure_ascii=False, indent=2))
