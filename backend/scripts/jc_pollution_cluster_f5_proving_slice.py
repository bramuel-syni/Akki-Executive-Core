#!/usr/bin/env python3
"""P5.7-Cluster-F.5 fix-sprint proving slice.

Canonical Spec: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1`
                (sub-sprint F.5 = microsoft_pkce + inbox_migration +
                admin_button_and_badge — 3 M1 polluters · largest
                test-count group · mechanical sync→async conversion
                identical to Cluster-F.4 / F.1 / F.2 / E pattern)

Target: ≥12 GREEN.

  Row  1  : microsoft_pkce in isolation → 7/7 PASS
  Row  2  : inbox_migration in isolation → 7/7 PASS (1 may skip without env)
  Row  3  : admin_button_and_badge in isolation → 4/4 PASS
  Row  4  : microsoft_pkce + autosave (B.2 polluter pair) → all PASS
  Row  5  : inbox_migration + autosave (B.2 polluter pair) → all PASS
  Row  6  : admin_button_and_badge + autosave (B.2 polluter pair) → all PASS
  Row  7  : Combined F.5 (all 3 files) → 18 PASS expected
  Row  8  : Combined F.5 + autosave (full polluter sweep) → 21 PASS expected
  Row  9  : microsoft_pkce + phase4_2 (A+D defensive) → all PASS
  Row 10  : inbox_migration + p5_10 (Cluster-E defensive) → all PASS
  Row 11  : Log scan — zero 'Future attached to a different loop'
            across paired Row 8's full stdout
  Row 12  : Source-assertion — no F.5 file contains a `_run` helper
            or `asyncio.get_event_loop().run_until_complete`
  Row 13  : Bespoke-run invariant PASSES with M1_CEILING=8 (closure-
            schedule lock validated end-to-end post-F.5 ratchet)
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

F5_FILES = [
    "tests/test_phase_p2_a2_microsoft_pkce.py",
    "tests/test_phase_p5_8_inbox_migration.py",
    "tests/test_phase_p5_9_admin_button_and_badge.py",
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
    print("P5.7-Cluster-F.5 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1")
    print("=" * 76)
    rows: List[Dict] = []

    # ── Rows 1-3 — isolation per file ──
    # Note: inbox_migration's test_p5_8_1_sendgrid_inbound_rejects_wrong_auth
    # may skip if SENDGRID_INBOUND_AUTH_USERNAME/_PASSWORD aren't set.
    # Accept either "7 passed" or "6 passed, 1 skipped" outcomes for that file.
    expected_isolation = [
        (F5_FILES[0], lambda s: "7 passed" in s),
        (F5_FILES[1], lambda s: ("7 passed" in s) or ("6 passed" in s and "skipped" in s)),
        (F5_FILES[2], lambda s: "4 passed" in s),
    ]
    for idx, (f, check) in enumerate(expected_isolation, start=1):
        rc, summary, _ = _run_pytest([f])
        ok = (rc == 0 and check(summary))
        rows.append(row(idx, f"{f} in isolation post-fix", ok, summary))

    # ── Rows 4-6 — each F.5 file paired with autosave ──
    for idx, f in enumerate(F5_FILES, start=4):
        rc, summary, _ = _run_pytest([f, AUTOSAVE])
        ok = (rc == 0 and "failed" not in summary)
        rows.append(row(idx, f"{f} + autosave (B.2 polluter pair, post-fix)", ok, summary))

    # ── Row 7 — Combined F.5 (all 3 files together) ──
    rc, summary, _ = _run_pytest(F5_FILES)
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(7, "Combined F.5 (all 3 files together) — 18 PASS expected (some may skip)",
                    ok, summary))

    # ── Row 8 — Combined F.5 + autosave (full polluter sweep) ──
    rc, summary, full_stdout_r8 = _run_pytest(F5_FILES + [AUTOSAVE], capture_full=True)
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(8, "Combined F.5 + autosave — 21 PASS expected (some may skip)",
                    ok, summary))

    # ── Row 9 — microsoft_pkce + phase4_2 (A+D defensive) ──
    rc, summary, _ = _run_pytest([F5_FILES[0], PHASE4_2])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(9, f"{F5_FILES[0]} + {PHASE4_2} (A+D defensive)", ok, summary))

    # ── Row 10 — inbox_migration + p5_10 (Cluster-E defensive) ──
    rc, summary, _ = _run_pytest([F5_FILES[1], P5_10])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(10, f"{F5_FILES[1]} + {P5_10} (Cluster-E defensive)", ok, summary))

    # ── Row 11 — Log scan on Row 8's full stdout ──
    bad_phrase = "attached to a different loop"
    occurrences = full_stdout_r8.lower().count(bad_phrase.lower())
    ok = (occurrences == 0)
    rows.append(row(11, "log scan: zero 'Future attached to a different loop'",
                    ok, f"occurrences={occurrences} in Row 8's full stdout"))

    # ── Row 12 — Source-assertion: no _run helper, no get_event_loop.run_until_complete ──
    bad_markers = []
    for f in F5_FILES:
        src = (BACKEND / f).read_text(encoding="utf-8")
        if re.search(r"^def\s+_run\s*\(", src, re.MULTILINE):
            bad_markers.append(f"{f}: still has 'def _run' helper")
        if re.search(r"asyncio\.get_event_loop\(\)\.run_until_complete", src):
            bad_markers.append(f"{f}: still has 'asyncio.get_event_loop().run_until_complete'")
    ok = (not bad_markers)
    rows.append(row(12, "source-assertion: no _run / get_event_loop.run_until_complete",
                    ok, "\n".join(bad_markers) if bad_markers else "all 3 F.5 files clean"))

    # ── Row 13 — Bespoke-run invariant PASSES (closure-schedule lock) ──
    rc, summary, _ = _run_pytest([BESPOKE_INVARIANT])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(13, "bespoke-run invariant PASSES (F.5 entries removed + M1_CEILING=8)",
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
