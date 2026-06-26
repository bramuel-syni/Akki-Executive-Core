#!/usr/bin/env python3
"""P5.7-Cluster-F.2 fix-sprint proving slice.

Canonical Spec: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1`
                (sub-sprint F.2 = security_headers + cookie_hardening
                + health_composite — three M1 polluters; mechanical
                sync→async conversion identical to Cluster-E)

Target: ≥12 GREEN.

  Row 1   : test_phase_p2_b1_security_headers in isolation -> 5/5 PASS
  Row 2   : test_phase_p3_2_cookie_hardening in isolation -> 2/2 PASS
  Row 3   : test_phase_p2_d2_health_composite in isolation -> 4/4 PASS
  Row 4   : security_headers + autosave paired -> all PASS
  Row 5   : cookie_hardening + autosave paired -> all PASS
  Row 6   : health_composite + autosave paired -> all PASS
  Row 7   : Combined F.2 (all 3 files together) -> 11/11 PASS
  Row 8   : Combined F.2 + autosave -> 14/14 PASS
  Row 9   : security_headers + bounce_webhook (A+D-fixed) defensive -> all PASS
  Row 10  : cookie_hardening + p5_10 (Cluster-E-fixed) defensive -> all PASS
  Row 11  : Log scan: zero 'Future attached to a different loop' across
            paired Row 8's full stdout
  Row 12  : Source-assertion sanity — none of the 3 files contains a
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

F2_FILES = [
    "tests/test_phase_p2_b1_security_headers.py",
    "tests/test_phase_p3_2_cookie_hardening.py",
    "tests/test_phase_p2_d2_health_composite.py",
]
AUTOSAVE = "tests/test_track_b_phase_b5_g6_notes_autosave.py"
BOUNCE_WEBHOOK = "tests/test_phase_p5_7_5_bounce_webhook.py"
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
    print("P5.7-Cluster-F.2 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1")
    print("=" * 76)
    rows: List[Dict] = []

    # ── Rows 1-3 — isolation per file ──
    expected_isolation = [
        (F2_FILES[0], "5 passed"),
        (F2_FILES[1], "2 passed"),
        (F2_FILES[2], "4 passed"),
    ]
    for idx, (f, expected) in enumerate(expected_isolation, start=1):
        rc, summary, _ = _run_pytest([f])
        ok = (rc == 0 and expected in summary)
        rows.append(row(idx, f"{f} in isolation post-fix ({expected})", ok, summary))

    # ── Rows 4-6 — each file paired with autosave ──
    for idx, f in enumerate(F2_FILES, start=4):
        rc, summary, _ = _run_pytest([f, AUTOSAVE])
        ok = (rc == 0 and "failed" not in summary)
        rows.append(row(idx, f"{f} + autosave (B.2 polluter pair, post-fix)", ok, summary))

    # ── Row 7 — Combined F.2 (all 3 together) ──
    rc, summary, _ = _run_pytest(F2_FILES)
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(7, "Combined F.2 (all 3 files together) — 11 PASS expected", ok, summary))

    # ── Row 8 — Combined F.2 + autosave (full polluter sweep) ──
    rc, summary, full_stdout_r8 = _run_pytest(F2_FILES + [AUTOSAVE], capture_full=True)
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(8, "Combined F.2 + autosave — 14 PASS expected", ok, summary))

    # ── Row 9 — security_headers + bounce_webhook (A+D-fixed) defensive ──
    rc, summary, _ = _run_pytest([F2_FILES[0], BOUNCE_WEBHOOK])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(9, f"{F2_FILES[0]} + {BOUNCE_WEBHOOK} (A+D defensive)", ok, summary))

    # ── Row 10 — cookie_hardening + p5_10 (Cluster-E-fixed) defensive ──
    rc, summary, _ = _run_pytest([F2_FILES[1], P5_10])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(10, f"{F2_FILES[1]} + {P5_10} (Cluster-E defensive)", ok, summary))

    # ── Row 11 — Log scan on Row 8's full stdout ──
    bad_phrase = "attached to a different loop"
    occurrences = full_stdout_r8.lower().count(bad_phrase.lower())
    ok = (occurrences == 0)
    rows.append(row(11, "log scan: zero 'Future attached to a different loop'",
                    ok, f"occurrences={occurrences} in Row 8's full stdout"))

    # ── Row 12 — Source-assertion: no _run helper, no get_event_loop().run_until_complete ──
    bad_markers = []
    for f in F2_FILES:
        src = (BACKEND / f).read_text(encoding="utf-8")
        if re.search(r"^def\s+_run\s*\(", src, re.MULTILINE):
            bad_markers.append(f"{f}: still has 'def _run' helper")
        if re.search(r"asyncio\.get_event_loop\(\)\.run_until_complete", src):
            bad_markers.append(f"{f}: still has 'asyncio.get_event_loop().run_until_complete'")
    ok = (not bad_markers)
    rows.append(row(12, "source-assertion: no _run / get_event_loop.run_until_complete",
                    ok, "\n".join(bad_markers) if bad_markers else "all 3 files clean"))

    # ── Final tally ──
    green = sum(1 for r in rows if r["status"] == "GREEN")
    total = len(rows)
    print("=" * 76)
    print(f"RESULT  {green}/{total} GREEN")
    print("=" * 76)
    return 0 if green == total else 1


if __name__ == "__main__":
    sys.exit(main())
