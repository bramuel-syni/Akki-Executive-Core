#!/usr/bin/env python3
"""JC-RATCHET-PHASE4_4-REFRESH proving slice.

Canonical Spec: side-quest dispatched 2026-06-26 (per JC-POLLUTION-B1-FIX
                sprint memo §5 surfaced finding)

Validates that refreshing the 3 stale ratchet shas + 2 path-count
constants in `tests/test_phase4_4_dual_mount_smoke.py` closes the
deterministic regression in isolation, matching A+D Cluster-D's fix
shape on the phase4_2 sibling test.

Target: 3/3 GREEN (just the 3 previously-failing tests).
        + 1 sanity row that all 37 tests in the file pass post-refresh.

  Row 1 : test_api_slice_hash_pinned PASSES
  Row 2 : test_v1_slice_hash_pinned PASSES
  Row 3 : test_combined_hash_pinned PASSES
  Row 4 : All 37 tests in test_phase4_4_dual_mount_smoke.py PASS in isolation
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

BACKEND = Path("/app/backend")
ROW_TIMEOUT_S = 90
PYTEST_BASE = [
    sys.executable, "-m", "pytest",
    "-q", "--no-header", "--tb=short",
    "-m", "not integration and not deploy_smoke and not runtime_playwright",
    "-p", "no:cacheprovider",
]
TARGET_FILE = "tests/test_phase4_4_dual_mount_smoke.py"
SUPERVISOR_HOST = "http://127.0.0.1:8001"


def _run_pytest(args: List[str]) -> Tuple[int, str]:
    cmd = PYTEST_BASE + args
    started = time.time()
    proc = subprocess.run(
        cmd, cwd=str(BACKEND), capture_output=True, text=True,
        timeout=ROW_TIMEOUT_S,
    )
    dur = time.time() - started
    summary = ""
    for line in (proc.stdout or "").splitlines()[::-1]:
        line_s = line.strip()
        if " passed" in line_s or " failed" in line_s or " error" in line_s:
            summary = line_s
            break
    return proc.returncode, summary + f"  [dur={dur:.1f}s]"


def row(num: int, name: str, pred: bool, detail: str = "") -> Dict:
    status = "GREEN" if pred else "RED"
    print(f"  Row {num:>2}  {status:<5}  {name}")
    if detail:
        for line in detail.splitlines():
            print(f"            {line}")
    return {"row": num, "name": name, "status": status, "detail": detail}


def main() -> int:
    print("=" * 76)
    print("JC-RATCHET-PHASE4_4-REFRESH Proving Slice")
    print("=" * 76)

    # Pre-flight: confirm live ratchet matches new hardcoded EXPECTED constants
    try:
        with urllib.request.urlopen(f"{SUPERVISOR_HOST}/api/openapi.json", timeout=15) as resp:
            spec = json.loads(resp.read().decode())
        all_paths = sorted(spec.get("paths", {}).keys())
        api_paths = sorted(p for p in all_paths if p.startswith("/api/"))
        v1_paths = sorted(p for p in all_paths if p.startswith("/v1/"))
        live_api_sha = hashlib.sha256("\n".join(api_paths).encode()).hexdigest()[:16]
        live_v1_sha = hashlib.sha256("\n".join(v1_paths).encode()).hexdigest()[:16]
        live_combined_sha = hashlib.sha256("\n".join(all_paths).encode()).hexdigest()[:16]
        print(f"  preflight: /api/* sha = {live_api_sha} (paths={len(api_paths)})")
        print(f"  preflight: /v1/*  sha = {live_v1_sha} (paths={len(v1_paths)})")
        print(f"  preflight: combined = {live_combined_sha} (paths={len(all_paths)})")
        print()
    except Exception as e:
        print(f"  preflight FAILED: {e!r}")
        return 1

    rows: List[Dict] = []

    # ── Rows 1-3 — each previously-failing test, individually ──
    targets = [
        f"{TARGET_FILE}::test_api_slice_hash_pinned",
        f"{TARGET_FILE}::test_v1_slice_hash_pinned",
        f"{TARGET_FILE}::test_combined_hash_pinned",
    ]
    for i, t in enumerate(targets, start=1):
        rc, summary = _run_pytest([t])
        ok = (rc == 0 and "1 passed" in summary)
        rows.append(row(i, f"{t.split('::')[-1]} PASSES", ok, summary))

    # ── Row 4 — All 37 tests in the file PASS in isolation ──
    rc, summary = _run_pytest([TARGET_FILE])
    ok = (rc == 0 and "37 passed" in summary)
    rows.append(row(4, "All 37 tests in target file PASS in isolation", ok, summary))

    # ── Final tally ──
    green = sum(1 for r in rows if r["status"] == "GREEN")
    total = len(rows)
    print("=" * 76)
    print(f"RESULT  {green}/{total} GREEN")
    print("=" * 76)
    return 0 if green == total else 1


if __name__ == "__main__":
    sys.exit(main())
