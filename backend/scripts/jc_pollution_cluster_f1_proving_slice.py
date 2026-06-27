#!/usr/bin/env python3
"""P5.7-Cluster-F.1 fix-sprint proving slice.

Canonical Spec: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1`
                (sub-sprint F.1 = password_change + admin_force_reset
                — 2 M1 polluters; mechanical sync→async conversion
                identical to Cluster-E / Cluster-F.2 pattern)

Target: ≥10 GREEN.

  Row  1  : test_phase_p2_b4_password_change in isolation → 4/4 PASS
  Row  2  : test_phase_p2_b6_admin_force_reset in isolation → 4/4 PASS
  Row  3  : b4 + autosave (B.2 polluter→polluted pair) → all PASS
  Row  4  : b6 + autosave (B.2 polluter→polluted pair) → all PASS
  Row  5  : Combined F.1 (b4 + b6) → 8/8 PASS
  Row  6  : Combined F.1 + autosave (full polluter sweep) → 11/11 PASS
  Row  7  : b4 + phase4_2 (A+D defensive — Cluster-A polluter, post-fix) → all PASS
  Row  8  : b6 + p5_10 (Cluster-E defensive — converted polluter) → all PASS
  Row  9  : Log scan — zero 'Future attached to a different loop' across
            paired Row 6's full stdout
  Row 10  : Source-assertion sanity — neither F.1 file contains a
            `_run` helper or `asyncio.get_event_loop().run_until_complete`
            line post-conversion
"""
from __future__ import annotations

import re
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

F1_FILES = [
    "tests/test_phase_p2_b4_password_change.py",
    "tests/test_phase_p2_b6_admin_force_reset.py",
]
AUTOSAVE = "tests/test_track_b_phase_b5_g6_notes_autosave.py"
PHASE4_2 = "tests/test_phase4_2_http_transport_smoke.py"
P5_10 = "tests/test_phase_p5_10_audit_panel_direct_linkage.py"


def _run_pytest(args: List[str], capture_full: bool = False) -> Tuple[int, str, str]:
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
    body = proc.stdout or "" if capture_full else "\n".join((proc.stdout or "").splitlines()[-20:])
    return proc.returncode, summary + f"  [dur={dur:.1f}s]", body


def row(num: int, name: str, pred: bool, detail: str = "") -> Dict:
    status = "GREEN" if pred else "RED"
    print(f"  Row {num:>2}  {status:<5}  {name}")
    if detail:
        for line in detail.splitlines():
            print(f"            {line}")
    return {"row": num, "name": name, "status": status, "detail": detail}


def main() -> int:
    print("=" * 76)
    print("P5.7-Cluster-F.1 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1")
    print("=" * 76)
    rows: List[Dict] = []

    # ── Rows 1-2 — isolation per file ──
    expected_isolation = [
        (F1_FILES[0], "4 passed"),
        (F1_FILES[1], "4 passed"),
    ]
    for idx, (f, expected) in enumerate(expected_isolation, start=1):
        rc, summary, _ = _run_pytest([f])
        ok = (rc == 0 and expected in summary)
        rows.append(row(idx, f"{f} in isolation post-fix ({expected})", ok, summary))

    # ── Rows 3-4 — each F.1 file paired with autosave (B.2 polluted pair) ──
    for idx, f in enumerate(F1_FILES, start=3):
        rc, summary, _ = _run_pytest([f, AUTOSAVE])
        ok = (rc == 0 and "failed" not in summary)
        rows.append(row(idx, f"{f} + autosave (B.2 polluter pair, post-fix)", ok, summary))

    # ── Row 5 — Combined F.1 (both files together) ──
    rc, summary, _ = _run_pytest(F1_FILES)
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(5, "Combined F.1 (b4 + b6 together) — 8 PASS expected", ok, summary))

    # ── Row 6 — Combined F.1 + autosave (full polluter sweep) ──
    rc, summary, full_stdout_r6 = _run_pytest(F1_FILES + [AUTOSAVE], capture_full=True)
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(6, "Combined F.1 + autosave — 11 PASS expected", ok, summary))

    # ── Row 7 — b4 + phase4_2 (Cluster-A defensive — A+D-fixed polluter) ──
    rc, summary, _ = _run_pytest([F1_FILES[0], PHASE4_2])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(7, f"{F1_FILES[0]} + {PHASE4_2} (A+D defensive)", ok, summary))

    # ── Row 8 — b6 + p5_10 (Cluster-E defensive — converted polluter) ──
    rc, summary, _ = _run_pytest([F1_FILES[1], P5_10])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(8, f"{F1_FILES[1]} + {P5_10} (Cluster-E defensive)", ok, summary))

    # ── Row 9 — Log scan on Row 6's full stdout ──
    bad_phrase = "attached to a different loop"
    occurrences = full_stdout_r6.lower().count(bad_phrase.lower())
    ok = (occurrences == 0)
    rows.append(row(9, "log scan: zero 'Future attached to a different loop'",
                    ok, f"occurrences={occurrences} in Row 6's full stdout"))

    # ── Row 10 — Source-assertion: no _run helper, no get_event_loop.run_until_complete ──
    bad_markers = []
    for f in F1_FILES:
        src = (BACKEND / f).read_text(encoding="utf-8")
        if re.search(r"^def\s+_run\s*\(", src, re.MULTILINE):
            bad_markers.append(f"{f}: still has 'def _run' helper")
        if re.search(r"asyncio\.get_event_loop\(\)\.run_until_complete", src):
            bad_markers.append(f"{f}: still has 'asyncio.get_event_loop().run_until_complete'")
    ok = (not bad_markers)
    rows.append(row(10, "source-assertion: no _run / get_event_loop.run_until_complete",
                    ok, "\n".join(bad_markers) if bad_markers else "both F.1 files clean"))

    # ── Final tally ──
    green = sum(1 for r in rows if r["status"] == "GREEN")
    total = len(rows)
    print("=" * 76)
    print(f"RESULT  {green}/{total} GREEN")
    print("=" * 76)
    return 0 if green == total else 1


if __name__ == "__main__":
    sys.exit(main())
