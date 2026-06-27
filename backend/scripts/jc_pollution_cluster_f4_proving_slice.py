#!/usr/bin/env python3
"""P5.7-Cluster-F.4 fix-sprint proving slice.

Canonical Spec: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1`
                (sub-sprint F.4 = bounce_webhook + waitlist_reminder
                — 2 M1 polluters · SendGrid surfaces · mechanical
                sync→async conversion identical to Cluster-E /
                Cluster-F.2 / Cluster-F.1 pattern)

Target: ≥11 GREEN. Row 11 NEW vs F.1: confirms the bespoke-run
invariant PASSES after F.4 files were removed from the grandfather
YAML — closure-schedule lock validated end-to-end.

  Row  1  : test_phase_p5_7_5_bounce_webhook in isolation → 5/5 PASS
  Row  2  : test_phase_p5_7_waitlist_reminder in isolation → 8/8 PASS
  Row  3  : bounce_webhook + autosave (B.2 polluter pair) → all PASS
  Row  4  : waitlist_reminder + autosave (B.2 polluter pair) → all PASS
  Row  5  : Combined F.4 (both files together) → 13/13 PASS
  Row  6  : Combined F.4 + autosave (full polluter sweep) → 16/16 PASS
  Row  7  : bounce_webhook + phase4_2 (A+D defensive) → all PASS
  Row  8  : waitlist_reminder + p5_10 (Cluster-E defensive) → all PASS
  Row  9  : Log scan — zero 'Future attached to a different loop'
            across paired Row 6's full stdout
  Row 10  : Source-assertion — neither F.4 file contains a `_run`
            helper or `asyncio.get_event_loop().run_until_complete`
  Row 11  : Bespoke-run invariant PASSES after F.4 grandfather entries
            REMOVED (closure-schedule lock validated end-to-end)
"""
from __future__ import annotations

import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

BACKEND = Path("/app/backend")
ROW_TIMEOUT_S = 180
PYTEST_BASE = [
    sys.executable, "-m", "pytest",
    "-q", "--no-header", "--tb=short",
    "-m", "not integration and not deploy_smoke and not runtime_playwright",
    "-p", "no:cacheprovider",
]

F4_FILES = [
    "tests/test_phase_p5_7_5_bounce_webhook.py",
    "tests/test_phase_p5_7_waitlist_reminder.py",
]
AUTOSAVE = "tests/test_track_b_phase_b5_g6_notes_autosave.py"
PHASE4_2 = "tests/test_phase4_2_http_transport_smoke.py"
P5_10 = "tests/test_phase_p5_10_audit_panel_direct_linkage.py"
BESPOKE_INVARIANT = "tests/invariants/test_no_bespoke_run_helper.py"


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
    print("P5.7-Cluster-F.4 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1")
    print("=" * 76)
    rows: List[Dict] = []

    # ── Rows 1-2 — isolation per file ──
    expected_isolation = [
        (F4_FILES[0], "5 passed"),
        (F4_FILES[1], "8 passed"),
    ]
    for idx, (f, expected) in enumerate(expected_isolation, start=1):
        rc, summary, _ = _run_pytest([f])
        ok = (rc == 0 and expected in summary)
        rows.append(row(idx, f"{f} in isolation post-fix ({expected})", ok, summary))

    # ── Rows 3-4 — each F.4 file paired with autosave ──
    for idx, f in enumerate(F4_FILES, start=3):
        rc, summary, _ = _run_pytest([f, AUTOSAVE])
        ok = (rc == 0 and "failed" not in summary)
        rows.append(row(idx, f"{f} + autosave (B.2 polluter pair, post-fix)", ok, summary))

    # ── Row 5 — Combined F.4 (both files together) ──
    rc, summary, _ = _run_pytest(F4_FILES)
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(5, "Combined F.4 (bounce + waitlist together) — 13 PASS expected", ok, summary))

    # ── Row 6 — Combined F.4 + autosave (full polluter sweep) ──
    rc, summary, full_stdout_r6 = _run_pytest(F4_FILES + [AUTOSAVE], capture_full=True)
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(6, "Combined F.4 + autosave — 16 PASS expected", ok, summary))

    # ── Row 7 — bounce_webhook + phase4_2 (A+D defensive) ──
    rc, summary, _ = _run_pytest([F4_FILES[0], PHASE4_2])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(7, f"{F4_FILES[0]} + {PHASE4_2} (A+D defensive)", ok, summary))

    # ── Row 8 — waitlist_reminder + p5_10 (Cluster-E defensive) ──
    rc, summary, _ = _run_pytest([F4_FILES[1], P5_10])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(8, f"{F4_FILES[1]} + {P5_10} (Cluster-E defensive)", ok, summary))

    # ── Row 9 — Log scan on Row 6's full stdout ──
    bad_phrase = "attached to a different loop"
    occurrences = full_stdout_r6.lower().count(bad_phrase.lower())
    ok = (occurrences == 0)
    rows.append(row(9, "log scan: zero 'Future attached to a different loop'",
                    ok, f"occurrences={occurrences} in Row 6's full stdout"))

    # ── Row 10 — Source-assertion: no _run helper, no get_event_loop.run_until_complete ──
    bad_markers = []
    for f in F4_FILES:
        src = (BACKEND / f).read_text(encoding="utf-8")
        if re.search(r"^def\s+_run\s*\(", src, re.MULTILINE):
            bad_markers.append(f"{f}: still has 'def _run' helper")
        if re.search(r"asyncio\.get_event_loop\(\)\.run_until_complete", src):
            bad_markers.append(f"{f}: still has 'asyncio.get_event_loop().run_until_complete'")
    ok = (not bad_markers)
    rows.append(row(10, "source-assertion: no _run / get_event_loop.run_until_complete",
                    ok, "\n".join(bad_markers) if bad_markers else "both F.4 files clean"))

    # ── Row 11 — Bespoke-run invariant PASSES (closure-schedule lock) ──
    # F.4 grandfather entries were REMOVED from the YAML; the invariant
    # must still PASS because the converted files no longer carry the
    # M1 pattern. End-to-end validation of the closure lock.
    rc, summary, _ = _run_pytest([BESPOKE_INVARIANT])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(11, "bespoke-run invariant PASSES (F.4 entries removed, files clean)",
                    ok, summary))

    # ── Final tally ──
    green = sum(1 for r in rows if r["status"] == "GREEN")
    total = len(rows)
    print("=" * 76)
    print(f"RESULT  {green}/{total} GREEN")
    print("=" * 76)
    return 0 if green == total else 1


if __name__ == "__main__":
    sys.exit(main())
