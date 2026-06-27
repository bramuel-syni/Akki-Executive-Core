#!/usr/bin/env python3
"""P5.7-Cluster-F.3 fix-sprint proving slice.

Canonical Spec: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1`
                (sub-sprint F.3 = csrf + session_timeout +
                session_reauth — 3 M1 polluters; mechanical sync→async
                conversion identical to Cluster-E / Cluster-F.2 /
                Cluster-F.1 / Cluster-F.4 / Cluster-F.5 pattern;
                advance scan memo P5_7_FIX_SCOPE_CLUSTER_F3_ADVANCE.md
                §5 verdict LOW risk)

Target: ≥13 GREEN (same standard shape as F.5).

  Row  1  : csrf in isolation → 7 PASS
  Row  2  : session_timeout in isolation → 5 PASS
  Row  3  : session_reauth in isolation → 4 PASS
  Row  4  : csrf + autosave (B.2 polluter pair) → all PASS
  Row  5  : session_timeout + autosave → all PASS
  Row  6  : session_reauth + autosave → all PASS
  Row  7  : Combined F.3 → 16 PASS expected
  Row  8  : Combined F.3 + autosave → 19 PASS expected
  Row  9  : csrf + phase4_2 (A+D defensive) → all PASS
  Row 10  : session_timeout + p5_10 (Cluster-E defensive) → all PASS
  Row 11  : Log scan: zero 'Future attached to a different loop'
            across paired Row 8's full stdout
  Row 12  : Source-assertion: no F.3 file contains _run helper
            or asyncio.get_event_loop().run_until_complete
  Row 13  : Bespoke-run invariant PASSES with M1_CEILING=5 (closure-
            schedule lock validated; 8 → 5 ratchet)
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

F3_FILES = [
    "tests/test_phase_p3_1_csrf.py",
    "tests/test_phase_p3_4_session_timeout.py",
    "tests/test_phase_p5_5_session_reauth.py",
]
AUTOSAVE = "tests/test_track_b_phase_b5_g6_notes_autosave.py"
PHASE4_2 = "tests/test_phase4_2_http_transport_smoke.py"
P5_10 = "tests/test_phase_p5_10_audit_panel_direct_linkage.py"
BESPOKE_INVARIANT = "tests/invariants/test_no_bespoke_run_helper.py"


def _run_pytest(args: List[str], capture_full: bool = False) -> Tuple[int, str, str]:
    started = time.time()
    proc = subprocess.run(
        PYTEST_BASE + args, cwd=str(BACKEND),
        capture_output=True, text=True, timeout=ROW_TIMEOUT_S,
    )
    dur = time.time() - started
    summary = ""
    for line in (proc.stdout or "").splitlines()[::-1]:
        s = line.strip()
        if " passed" in s or " failed" in s or " error" in s:
            summary = s
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
    print("P5.7-Cluster-F.3 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1")
    print("=" * 76)
    rows: List[Dict] = []

    # ── Rows 1-3 — isolation per file ──
    expected_isolation = [
        (F3_FILES[0], "7 passed"),
        (F3_FILES[1], "5 passed"),
        (F3_FILES[2], "4 passed"),
    ]
    for idx, (f, expected) in enumerate(expected_isolation, start=1):
        rc, summary, _ = _run_pytest([f])
        ok = (rc == 0 and expected in summary)
        rows.append(row(idx, f"{f} in isolation post-fix ({expected})", ok, summary))

    # ── Rows 4-6 — each F.3 file paired with autosave ──
    for idx, f in enumerate(F3_FILES, start=4):
        rc, summary, _ = _run_pytest([f, AUTOSAVE])
        ok = (rc == 0 and "failed" not in summary)
        rows.append(row(idx, f"{f} + autosave (B.2 polluter pair, post-fix)", ok, summary))

    # ── Row 7 — Combined F.3 ──
    rc, summary, _ = _run_pytest(F3_FILES)
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(7, "Combined F.3 (all 3 files) — 16 PASS expected", ok, summary))

    # ── Row 8 — Combined F.3 + autosave ──
    rc, summary, full_stdout_r8 = _run_pytest(F3_FILES + [AUTOSAVE], capture_full=True)
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(8, "Combined F.3 + autosave — 19 PASS expected", ok, summary))

    # ── Row 9 — csrf + phase4_2 (A+D defensive) ──
    rc, summary, _ = _run_pytest([F3_FILES[0], PHASE4_2])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(9, f"{F3_FILES[0]} + {PHASE4_2} (A+D defensive)", ok, summary))

    # ── Row 10 — session_timeout + p5_10 (Cluster-E defensive) ──
    rc, summary, _ = _run_pytest([F3_FILES[1], P5_10])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(10, f"{F3_FILES[1]} + {P5_10} (Cluster-E defensive)", ok, summary))

    # ── Row 11 — Log scan on Row 8's full stdout ──
    bad_phrase = "attached to a different loop"
    occurrences = full_stdout_r8.lower().count(bad_phrase.lower())
    ok = (occurrences == 0)
    rows.append(row(11, "log scan: zero 'Future attached to a different loop'",
                    ok, f"occurrences={occurrences} in Row 8's full stdout"))

    # ── Row 12 — Source-assertion ──
    bad_markers = []
    for f in F3_FILES:
        src = (BACKEND / f).read_text(encoding="utf-8")
        if re.search(r"^def\s+_run\s*\(", src, re.MULTILINE):
            bad_markers.append(f"{f}: still has 'def _run' helper")
        if re.search(r"asyncio\.get_event_loop\(\)\.run_until_complete", src):
            bad_markers.append(f"{f}: still has 'asyncio.get_event_loop().run_until_complete'")
    ok = (not bad_markers)
    rows.append(row(12, "source-assertion: no _run / get_event_loop.run_until_complete",
                    ok, "\n".join(bad_markers) if bad_markers else "all 3 F.3 files clean"))

    # ── Row 13 — Bespoke-run invariant PASSES with M1_CEILING=5 ──
    rc, summary, _ = _run_pytest([BESPOKE_INVARIANT])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(13, "bespoke-run invariant PASSES (F.3 entries removed + M1_CEILING=5)",
                    ok, summary))

    green = sum(1 for r in rows if r["status"] == "GREEN")
    total = len(rows)
    print("=" * 76)
    print(f"RESULT  {green}/{total} GREEN")
    print("=" * 76)
    return 0 if green == total else 1


if __name__ == "__main__":
    sys.exit(main())
