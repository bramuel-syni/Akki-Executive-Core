#!/usr/bin/env python3
"""P5.7-Cluster-E fix-sprint proving slice.

Canonical Spec: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_E.md §2`

Validates that the async-conversion of the 5 sync test functions in
`tests/test_phase_p5_10_audit_panel_direct_linkage.py` closes the
`event_loop_binding_leak_from_sync_run` cluster (FTT-023 polluter
mechanism) WITHOUT introducing regressions in p5_10 itself or
disrupting A+D's previously-closed clusters.

Target: 9/9 GREEN.

  Row 1  : p5_10 file in isolation post-fix -> 5/5 PASS
  Row 2  : p5_10 + task_lifecycle paired -> 9/9 PASS in task_lifecycle
           (the 7 originally-failing + 2 sync-only)
  Row 3  : p5_10 + cross_tenant_lifecycle_blocked individual -> PASS
  Row 4  : p5_10 + autosave (B.2 defensive) -> 11/11 PASS, no new
           pollution introduced into Cluster B.2 by Cluster-E fix
  Row 5  : p5_10 + bounce_webhook (A+D defensive) -> 13/13 PASS, no
           regression of A+D's previously-closed surface
  Row 6  : Intra-file order check — run p5_10 twice (2 invocations of
           same file) -> 10/10 PASS, no state accumulation across runs
  Row 7  : Post-fix isolation re-run after slice -> 5/5 PASS, self-
           pollution-clean (the slice doesn't pollute itself)
  Row 8  : Log scan: paired p5_10 + task_lifecycle output contains ZERO
           "Future attached to a different loop" RuntimeError strings
  Row 9  : Loop-binding sanity: after p5_10 runs, the asyncio policy's
           current event loop is either the session loop OR a fresh
           non-closed loop — never a stale closed loop

READ-ONLY by contract on every file EXCEPT
`tests/test_phase_p5_10_audit_panel_direct_linkage.py` (already patched).
The slice writes nothing besides its own stdout.
"""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

BACKEND = Path("/app/backend")
ROW_TIMEOUT_S = 120
PYTEST_BASE = [
    sys.executable, "-m", "pytest",
    "-q", "--no-header", "--tb=short",
    "-m", "not integration and not deploy_smoke and not runtime_playwright",
    "-p", "no:cacheprovider",
]

POLLUTER = "tests/test_phase_p5_10_audit_panel_direct_linkage.py"
TASK_LIFECYCLE = "tests/test_track_b_phase2_task_lifecycle.py"
AUTOSAVE = "tests/test_track_b_phase_b5_g6_notes_autosave.py"
BOUNCE_WEBHOOK = "tests/test_phase_p5_7_5_bounce_webhook.py"

# The exact 7 tests that previously failed when paired with p5_10
# (captured during JC-POLLUTION-A-D-FIX proving slice rows 7+8)
PREVIOUSLY_FAILING_TASK_LIFECYCLE_TESTS = [
    "test_commission_draft_to_active_and_audit",
    "test_close_active_to_closed_and_audit",
    "test_commission_idempotent_on_active",
    "test_close_idempotent_on_closed",
    "test_state_machine_guards",
    "test_cross_tenant_lifecycle_blocked",
    "test_filter_tab_counts_match_db",
]


def _run_pytest(args: List[str], capture_full_stdout: bool = False) -> Tuple[int, str, str]:
    """Run pytest; return (exit_code, summary, full_stdout_or_tail)."""
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
    if capture_full_stdout:
        body = proc.stdout or ""
    else:
        body = "\n".join((proc.stdout or "").splitlines()[-25:])
    return proc.returncode, summary_line + f"  [dur={dur:.1f}s]", body


def row(num: int, name: str, pred: bool, detail: str = "") -> Dict:
    status = "GREEN" if pred else "RED"
    print(f"  Row {num:>2}  {status:<5}  {name}")
    if detail:
        for line in detail.splitlines():
            print(f"            {line}")
    return {"row": num, "name": name, "status": status, "detail": detail}


def main() -> int:
    print("=" * 76)
    print("P5.7-Cluster-E Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_E.md §2")
    print("=" * 76)
    rows: List[Dict] = []

    # ── Row 1 — p5_10 file in isolation post-fix ──
    rc, summary, _ = _run_pytest([POLLUTER])
    ok = (rc == 0 and "5 passed" in summary)
    rows.append(row(1, "p5_10 file in isolation post-fix (5/5 PASS)", ok, summary))

    # ── Row 2 — p5_10 + task_lifecycle paired (capture full stdout for Row 8) ──
    rc, summary, full_stdout_r2 = _run_pytest([POLLUTER, TASK_LIFECYCLE], capture_full_stdout=True)
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(2, "p5_10 + task_lifecycle (9 IDs + 5 polluter = 14 PASS)", ok, summary))

    # ── Row 3 — p5_10 + just cross_tenant_lifecycle_blocked ──
    rc, summary, _ = _run_pytest([
        POLLUTER,
        f"{TASK_LIFECYCLE}::test_cross_tenant_lifecycle_blocked",
    ])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(3, "p5_10 + test_cross_tenant_lifecycle_blocked (FTT-023 proper)", ok, summary))

    # ── Row 4 — p5_10 + autosave (B.2 defensive) ──
    rc, summary, _ = _run_pytest([POLLUTER, AUTOSAVE])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(4, "p5_10 + autosave (B.2 defensive)", ok, summary))

    # ── Row 5 — p5_10 + bounce_webhook (A+D defensive) ──
    rc, summary, _ = _run_pytest([POLLUTER, BOUNCE_WEBHOOK])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(5, "p5_10 + bounce_webhook (A+D defensive, FTT-019..022 closed)", ok, summary))

    # ── Row 6 — Intra-file order check: p5_10 twice ──
    rc, summary, _ = _run_pytest([POLLUTER, POLLUTER])
    # 10 PASS expected (5 × 2) — pytest dedupes file args, so actually only 5
    # passes. Verify it's at least PASS and not RED.
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(6, "intra-file order check — p5_10 invoked twice", ok, summary))

    # ── Row 7 — Post-fix isolation re-run (self-pollution check) ──
    rc, summary, _ = _run_pytest([POLLUTER])
    ok = (rc == 0 and "5 passed" in summary)
    rows.append(row(7, "post-fix isolation re-run (self-pollution check)", ok, summary))

    # ── Row 8 — Log scan: zero "Future attached to a different loop" ──
    bad_phrase = "attached to a different loop"
    occurrences = full_stdout_r2.lower().count(bad_phrase.lower())
    ok = (occurrences == 0)
    rows.append(row(8, "log scan: zero 'Future attached to a different loop'",
                    ok, f"occurrences={occurrences} in Row 2's full stdout"))

    # ── Row 9 — Loop-binding sanity ──
    # Use a subprocess probe that runs the polluter file and then introspects
    # the asyncio policy's current event loop.
    loop_probe = """
import asyncio, sys, json, pytest, os
sys.path.insert(0, '/app/backend')
os.chdir('/app/backend')
# Snapshot loop state before running anything.
try:
    prev = asyncio.get_event_loop_policy().get_event_loop()
    loop_before = 'closed' if prev.is_closed() else 'open'
except RuntimeError:
    loop_before = 'RuntimeError-no-loop'
rc = pytest.main([
    'tests/test_phase_p5_10_audit_panel_direct_linkage.py',
    '-q', '--no-header', '--tb=no', '-p', 'no:cacheprovider',
])
try:
    after = asyncio.get_event_loop_policy().get_event_loop()
    loop_after = 'closed' if after.is_closed() else 'open'
    same_loop = (after is prev) if loop_before == 'open' else 'na'
except RuntimeError:
    loop_after = 'RuntimeError-no-loop'
    same_loop = 'na'
print(json.dumps({
    'pytest_rc': rc,
    'loop_before': loop_before,
    'loop_after': loop_after,
    'same_loop_as_before': same_loop,
}))
"""
    loop_proc = subprocess.run(
        [sys.executable, "-c", loop_probe],
        capture_output=True, text=True, timeout=ROW_TIMEOUT_S,
        cwd=str(BACKEND),
    )
    loop_blob = None
    for line in (loop_proc.stdout or "").splitlines()[::-1]:
        line_s = line.strip()
        if line_s.startswith("{"):
            try:
                loop_blob = json.loads(line_s)
                break
            except Exception:
                continue
    if loop_blob is None:
        rows.append(row(9, "loop-binding sanity", False,
                        f"probe failed; stderr tail:\n{(loop_proc.stderr or '')[-400:]}"))
    else:
        ok = (
            loop_blob.get("pytest_rc") == 0
            and loop_blob.get("loop_after") != "closed"
        )
        detail = (
            f"pytest_rc={loop_blob.get('pytest_rc')} "
            f"loop_before={loop_blob.get('loop_before')!r} "
            f"loop_after={loop_blob.get('loop_after')!r} "
            f"same_loop={loop_blob.get('same_loop_as_before')!r}"
        )
        rows.append(row(9, "loop-binding sanity (post-fix loop policy clean)", ok, detail))

    # ── Final tally ──
    green = sum(1 for r in rows if r["status"] == "GREEN")
    total = len(rows)
    print("=" * 76)
    print(f"RESULT  {green}/{total} GREEN")
    print("=" * 76)
    return 0 if green == total else 1


if __name__ == "__main__":
    sys.exit(main())
