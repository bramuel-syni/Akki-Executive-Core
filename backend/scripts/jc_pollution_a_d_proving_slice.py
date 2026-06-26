#!/usr/bin/env python3
"""
P5.7-A+D fix-sprint proving slice.

Canonical spec: /app/memory/sprints/P5_7_FIX_SCOPE.md §2.1

Validates that the three surgical patches to
`tests/test_phase4_2_http_transport_smoke.py` close Cluster A
(env-leak + asyncio-loop-policy mutation downstream pollution)
AND Cluster D (FTT-014 stale-sha deterministic regression in the
same file).

Slice rows (target 11/11 GREEN):

  Row 1  : Polluter file in isolation -> 8/8 PASS (closes FTT-014)
  Row 2  : Standalone env-restoration assertion -> os.environ pre/post
           the polluter function are byte-identical
  Row 3  : Standalone asyncio-loop-policy restoration -> after the
           polluter test runs, asyncio.get_event_loop() returns a
           non-closed loop (or raises cleanly, never the stale-closed
           state that caused the cascade)
  Row 4  : Polluter + cookie_hardening (FTT-015, FTT-016) -> all PASS
  Row 5  : Polluter + audit_panel_direct_linkage (FTT-017, FTT-018) -> all PASS
  Row 6  : Polluter + bounce_webhook (FTT-019..FTT-022) -> all PASS
  Row 7  : Polluter + audit_panel + task_lifecycle (FTT-023 tiered) -> all PASS
  Row 8  : All four polluted files together with polluter at front -> all PASS
  Row 9  : Polluter + sample auth-state-sensitive file (autosave) -> all PASS
           (defensive: confirms B.2 isn't unintentionally regressed by A+D)
  Row 10 : Surface-ratchet live re-check -> /api/* sha matches the new
           hardcoded EXPECTED value
  Row 11 : Polluter file in isolation re-run after slice end -> still 8/8 PASS
           (sanity check that running the slice didn't pollute itself)

READ-ONLY by contract on every file EXCEPT
`tests/test_phase4_2_http_transport_smoke.py` (already patched).
The slice writes nothing.
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Dict, List, Tuple

BACKEND = Path("/app/backend")
ROW_TIMEOUT_S = 120  # 2 min per pair; generous given fastest pair is < 7 s
PYTEST_BASE = [
    sys.executable, "-m", "pytest",
    "-q", "--no-header", "--tb=line",
    "-m", "not integration and not deploy_smoke and not runtime_playwright",
    "-p", "no:cacheprovider",
]
SUPERVISOR_HOST = "http://127.0.0.1:8001"
POLLUTER = "tests/test_phase4_2_http_transport_smoke.py"

# Polluted files keyed by FTT cluster (per P5_7_FIX_SCOPE.md §2.1)
POLLUTED = {
    "FTT-015,016": "tests/test_phase_p3_2_cookie_hardening.py",
    "FTT-017,018": "tests/test_phase_p5_10_audit_panel_direct_linkage.py",
    "FTT-019..022": "tests/test_phase_p5_7_5_bounce_webhook.py",
    "FTT-023": "tests/test_track_b_phase2_task_lifecycle.py",
}

# Cluster B.2 polluted file for the defensive row 9
AUTOSAVE = "tests/test_track_b_phase_b5_g6_notes_autosave.py"


def _run_pytest(args: List[str]) -> Tuple[int, str, str]:
    """Run pytest with the given args; return (exit_code, stdout_tail, full_summary)."""
    cmd = PYTEST_BASE + args
    started = time.time()
    proc = subprocess.run(
        cmd,
        cwd=str(BACKEND),
        capture_output=True,
        text=True,
        timeout=ROW_TIMEOUT_S,
    )
    dur = time.time() - started
    # Extract the "X passed, Y failed in N s" summary
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
    print("P5.7-A+D Proving Slice — Canonical Spec: P5_7_FIX_SCOPE.md §2.1")
    print("=" * 76)
    rows: List[Dict] = []

    # ── Row 1 — Polluter file in isolation -> 8/8 PASS ──
    rc, summary, tail = _run_pytest([POLLUTER])
    ok = (rc == 0 and "8 passed" in summary)
    rows.append(row(1, "polluter file in isolation (8/8 PASS post-fix)", ok, summary))

    # ── Row 2 — env-restoration assertion ──
    # The probe must mirror conftest.py's preload behaviour so we measure
    # the POLLUTER's mutation in isolation, not conftest+polluter combined.
    # conftest.py:34 calls load_dotenv("/app/backend/.env") at collection.
    # We replicate that load BEFORE snapshotting so the diff captures only
    # what the polluter test itself adds/changes.
    probe_script = """
import json, os, sys
sys.path.insert(0, '/app/backend')
os.chdir('/app/backend')
# Mirror conftest.py preload so we measure the polluter alone.
from dotenv import load_dotenv
load_dotenv('/app/backend/.env')
load_dotenv('/app/frontend/.env')
for k, v in [
    ('CSRF_TEST_BYPASS_HEADER', '1'),
    ('RATE_LIMIT_DISABLED', '1'),
    ('COHORT_NOTIFY_DISABLED', 'true'),
]:
    os.environ.setdefault(k, v)
os.environ['COHORT_EMAILS_ENABLED'] = 'false'
# Snapshot AFTER mirroring conftest's pre-state.
snap_before = dict(os.environ)
# Run only the polluter test in this process.
import pytest
rc = pytest.main([
    'tests/test_phase4_2_http_transport_smoke.py::test_http_mode_adapter_class_reconstructs_dto',
    '-q', '--no-header', '--tb=no', '-p', 'no:cacheprovider',
])
snap_after = dict(os.environ)
diff_added = {k: snap_after[k] for k in snap_after if k not in snap_before}
diff_removed = {k: snap_before[k] for k in snap_before if k not in snap_after}
diff_changed = {k: (snap_before[k], snap_after[k]) for k in snap_before
                if k in snap_after and snap_before[k] != snap_after[k]}
print(json.dumps({
    'pytest_rc': rc,
    'added_keys': sorted(diff_added.keys()),
    'removed_keys': sorted(diff_removed.keys()),
    'changed_keys': sorted(diff_changed.keys()),
}))
"""
    probe_proc = subprocess.run(
        [sys.executable, "-c", probe_script],
        capture_output=True, text=True, timeout=ROW_TIMEOUT_S,
        cwd=str(BACKEND),
    )
    # Parse last JSON line from probe stdout
    diff_blob = None
    for line in (probe_proc.stdout or "").splitlines()[::-1]:
        line_s = line.strip()
        if line_s.startswith("{"):
            try:
                diff_blob = json.loads(line_s)
                break
            except Exception:
                continue
    if diff_blob is None:
        rows.append(row(2, "env-restoration (snapshot pre/post)", False,
                        "probe failed to emit JSON; stderr tail follows\n" +
                        (probe_proc.stderr or "")[-400:]))
    else:
        added = diff_blob.get("added_keys", [])
        removed = diff_blob.get("removed_keys", [])
        changed = diff_blob.get("changed_keys", [])
        # PYTEST_CURRENT_TEST and similar pytest-internal keys are
        # tolerated. TIKTOKEN_CACHE_DIR is set by the tiktoken library
        # on first import (not by the polluter test). Otherwise: zero
        # added/changed/removed = pass.
        TOLERATED_ADDED = {"PYTEST_CURRENT_TEST", "PYTEST_VERSION", "TIKTOKEN_CACHE_DIR"}
        bad_added = [k for k in added if k not in TOLERATED_ADDED]
        ok2 = (
            diff_blob.get("pytest_rc") == 0
            and not bad_added
            and not removed
            and not changed
        )
        detail = (
            f"pytest_rc={diff_blob.get('pytest_rc')} "
            f"added={added!r} changed={changed!r} removed={removed!r}"
        )
        rows.append(row(2, "env-restoration (snapshot pre/post)", ok2, detail))

    # ── Row 3 — asyncio loop-policy restoration ──
    loop_probe = """
import asyncio, sys, json, pytest, os
sys.path.insert(0, '/app/backend')
os.chdir('/app/backend')
# Snapshot what get_event_loop() returns BEFORE the polluter runs.
prev_loop_closed_before = None
try:
    prev = asyncio.get_event_loop_policy().get_event_loop()
    prev_loop_closed_before = prev.is_closed()
except RuntimeError:
    prev_loop_closed_before = 'RuntimeError-no-loop'
rc = pytest.main([
    'tests/test_phase4_2_http_transport_smoke.py::test_http_mode_adapter_class_reconstructs_dto',
    '-q', '--no-header', '--tb=no', '-p', 'no:cacheprovider',
])
# AFTER the polluter: get_event_loop() should either give a usable loop
# OR raise cleanly (never give a stale closed loop).
loop_after_state = None
try:
    loop_after = asyncio.get_event_loop_policy().get_event_loop()
    loop_after_state = 'closed' if loop_after.is_closed() else 'open'
except RuntimeError:
    loop_after_state = 'RuntimeError-no-loop'
print(json.dumps({
    'pytest_rc': rc,
    'loop_before': prev_loop_closed_before,
    'loop_after': loop_after_state,
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
        rows.append(row(3, "asyncio loop-policy restoration", False,
                        "loop-probe failed to emit JSON; stderr tail follows\n" +
                        (loop_proc.stderr or "")[-400:]))
    else:
        ok3 = (
            loop_blob.get("pytest_rc") == 0
            and loop_blob.get("loop_after") != "closed"
        )
        detail = (
            f"pytest_rc={loop_blob.get('pytest_rc')} "
            f"loop_before={loop_blob.get('loop_before')!r} "
            f"loop_after={loop_blob.get('loop_after')!r}"
        )
        rows.append(row(3, "asyncio loop-policy restoration", ok3, detail))

    # ── Rows 4-7 — paired pytest invocations per cluster ──
    for i, (cluster_label, polluted_file) in enumerate(POLLUTED.items(), start=4):
        # Row 7 (FTT-023) is tiered: polluter + intermediate + final polluted
        if cluster_label == "FTT-023":
            args = [POLLUTER,
                    "tests/test_phase_p5_10_audit_panel_direct_linkage.py",
                    polluted_file]
        else:
            args = [POLLUTER, polluted_file]
        rc, summary, tail = _run_pytest(args)
        ok = (rc == 0 and "failed" not in summary)
        rows.append(row(i, f"polluter + {polluted_file} ({cluster_label})", ok, summary))

    # ── Row 8 — all four polluted files together with polluter at front ──
    all_files = [POLLUTER] + list(POLLUTED.values())
    rc, summary, tail = _run_pytest(all_files)
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(8, "polluter + all 4 polluted files together", ok, summary))

    # ── Row 9 — Cluster B.2 defensive (autosave) ──
    # A+D fix should NOT regress B.2's polluted file. It might or might
    # not close some of B.2's polluters — that's measured separately in
    # the inter-cluster sweep, NOT here. Here we just confirm running the
    # polluter + autosave doesn't break the autosave file.
    rc, summary, tail = _run_pytest([POLLUTER, AUTOSAVE])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(9, f"polluter + {AUTOSAVE} (B.2 defensive)", ok, summary))

    # ── Row 10 — Live surface-ratchet re-check ──
    try:
        with urllib.request.urlopen(f"{SUPERVISOR_HOST}/api/openapi.json", timeout=15) as resp:
            spec_body = resp.read().decode()
        spec = json.loads(spec_body)
        api_paths = sorted(p for p in spec.get("paths", {}).keys() if p.startswith("/api/"))
        live_sha = hashlib.sha256("\n".join(api_paths).encode()).hexdigest()[:16]
        EXPECTED = "31e1d9769f632472"
        ok10 = (live_sha == EXPECTED)
        detail = f"live_sha={live_sha} EXPECTED={EXPECTED} path_count={len(api_paths)}"
        rows.append(row(10, "live /api/* surface-ratchet sha match", ok10, detail))
    except Exception as e:
        rows.append(row(10, "live /api/* surface-ratchet sha match", False, f"error: {e!r}"))

    # ── Row 11 — Polluter in isolation re-run (self-pollution check) ──
    rc, summary, tail = _run_pytest([POLLUTER])
    ok = (rc == 0 and "8 passed" in summary)
    rows.append(row(11, "polluter in isolation re-run (self-pollution check)", ok, summary))

    # ── Final tally ──
    green = sum(1 for r in rows if r["status"] == "GREEN")
    total = len(rows)
    print("=" * 76)
    print(f"RESULT  {green}/{total} GREEN")
    print("=" * 76)
    return 0 if green == total else 1


if __name__ == "__main__":
    sys.exit(main())
