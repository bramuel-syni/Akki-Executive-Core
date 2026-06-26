#!/usr/bin/env python3
"""P5.7-B.1 fix-sprint proving slice.

Canonical Spec: `/app/memory/sprints/P5_7_FIX_SCOPE.md §3`

Validates that demoting the `transport` fixture from `scope="module"`
to function-scope on `tests/test_p_cleanup_c_help_tooltip_suppression.py`
closes the SHARED-GLOBAL-STATE pollution that produced 0 pairwise
polluters in P5.7-HOLDOUT-FINISHER's 69-candidate sweep but FAIL_IN_CONTEXT
in the broad suite (FTT-010..012).

Target: 4/4 GREEN.

  Row 1  : File PASSES in isolation post-fix (5/5 PASS - regression-free)
  Row 2  : File PASSES paired with a random PASS-bucket predecessor
           (the original broad-suite failure mode simulated at minimum scope)
  Row 3  : All 5 tests (covering FTT-010..012 and 2 siblings) PASS when
           run in a broad-suite-simulating order (3 random predecessors
           + the polluted file)
  Row 4  : Fixture-scope sanity — confirm `transport` is now function-
           scoped by reading the source post-fix (single-line assertion)
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
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

POLLUTED = "tests/test_p_cleanup_c_help_tooltip_suppression.py"

# Predecessors known clean of the wrong-loop-binding bug:
#   - phase4_2_http_transport_smoke.py: A+D-fixed (env+loop-policy snapshot/restore)
#   - phase_p5_10_audit_panel_direct_linkage.py: Cluster-E-fixed (async-converted)
#   - track_b_phase2_task_lifecycle.py: pure @pytest.mark.asyncio file, no _run
#     helper, no sync tests. This was the polluted file in FTT-023; verified
#     clean in isolation post-Cluster-E.
# Deliberately NOT used: any of the 14 still-unconverted Cluster-F polluters
# (test_phase_p3_1_csrf, test_phase_p5_8_inbox_migration, etc.) — they would
# drag in wrong-loop-binding pollution independent of B.1's mechanism and
# muddy the Row 3 signal. Also deliberately NOT used:
# test_phase4_4_dual_mount_smoke.py — it has its own pre-existing 3-failure
# deterministic regression (stale ratchet shas) that would falsely surface as
# Row 3 RED. That file's regression is a separate parked issue.
PASS_PREDECESSORS = [
    "tests/test_phase4_2_http_transport_smoke.py",
    "tests/test_phase_p5_10_audit_panel_direct_linkage.py",
    "tests/test_track_b_phase2_task_lifecycle.py",
]


def _run_pytest(args: List[str]) -> Tuple[int, str, str]:
    cmd = PYTEST_BASE + args
    started = time.time()
    proc = subprocess.run(
        cmd, cwd=str(BACKEND), capture_output=True, text=True,
        timeout=ROW_TIMEOUT_S,
    )
    dur = time.time() - started
    summary_line = ""
    for line in (proc.stdout or "").splitlines()[::-1]:
        line_s = line.strip()
        if " passed" in line_s or " failed" in line_s or " error" in line_s:
            summary_line = line_s
            break
    tail = "\n".join((proc.stdout or "").splitlines()[-20:])
    return proc.returncode, summary_line + f"  [dur={dur:.1f}s]", tail


def row(num: int, name: str, pred: bool, detail: str = "") -> Dict:
    status = "GREEN" if pred else "RED"
    print(f"  Row {num:>2}  {status:<5}  {name}")
    if detail:
        for line in detail.splitlines():
            print(f"            {line}")
    return {"row": num, "name": name, "status": status, "detail": detail}


def main() -> int:
    print("=" * 76)
    print("P5.7-B.1 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE.md §3")
    print("=" * 76)
    rows: List[Dict] = []

    # ── Row 1 — File in isolation post-fix ──
    rc, summary, _ = _run_pytest([POLLUTED])
    ok = (rc == 0 and "5 passed" in summary)
    rows.append(row(1, "polluted file in isolation post-fix (5/5 PASS)", ok, summary))

    # ── Row 2 — File paired with one random PASS-bucket predecessor ──
    rc, summary, _ = _run_pytest([PASS_PREDECESSORS[0], POLLUTED])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(2, f"paired with {PASS_PREDECESSORS[0]} (broad-suite simulation 1)", ok, summary))

    # ── Row 3 — Broad-suite simulation with 3 predecessors ──
    rc, summary, _ = _run_pytest(PASS_PREDECESSORS + [POLLUTED])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(3, "paired with 3 PASS-bucket predecessors (broad-suite simulation)", ok, summary))

    # ── Row 4 — Fixture-scope sanity (source assertion) ──
    src = (BACKEND / POLLUTED).read_text(encoding="utf-8")
    # The fixture should be function-scoped post-fix (either explicit
    # `scope="function"` or no scope kwarg, which defaults to function).
    has_module_scope = bool(re.search(
        r'@pytest_asyncio\.fixture\s*\(\s*scope\s*=\s*[\'"]module[\'"]\s*\)\s*\n\s*async\s+def\s+transport',
        src,
    ))
    has_function_scope = bool(re.search(
        r'@pytest_asyncio\.fixture\s*\(\s*scope\s*=\s*[\'"]function[\'"]\s*\)\s*\n\s*async\s+def\s+transport',
        src,
    ))
    ok = (not has_module_scope) and has_function_scope
    detail = f"module_scope_marker_present={has_module_scope}  function_scope_marker_present={has_function_scope}"
    rows.append(row(4, "fixture-scope sanity (transport is now function-scoped)", ok, detail))

    # ── Final tally ──
    green = sum(1 for r in rows if r["status"] == "GREEN")
    total = len(rows)
    print("=" * 76)
    print(f"RESULT  {green}/{total} GREEN")
    print("=" * 76)
    return 0 if green == total else 1


if __name__ == "__main__":
    sys.exit(main())
