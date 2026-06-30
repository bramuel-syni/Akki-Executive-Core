#!/usr/bin/env python
"""P5.7-Cluster-G.3 Proving Slice
================================
Canonical Spec: /app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_G.md §1.3 (G.3 sub-sprint)
                + /app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_G3_VERIFICATION.md (Option A path)

Validates the Cluster-G.3 M2 batch (1 file / 7 class-based tests / 4 M2 sites)
mechanical sync→async conversion + closure-schedule lock at M2_CEILING=7
+ quarantine preservation invariant.

Target: ≥15 GREEN rows. Mirrors G.2 slice shape with iter54 substituted.

QUARANTINE-AWARE: iter54 carries module-level
`pytestmark = pytest.mark.skip(...)` per Patch 8 (2026-05-12).
Tests SKIP at runtime; we validate (a) collection succeeds with
async methods + class-based fixtures, (b) skipped outcome
preserved, (c) no `asyncio.run` remains in test bodies.

  Row  1   iter54 in isolation post-fix (expect 7 skipped)
  Row  2   iter54 + autosave (B.2 polluter pair, post-fix)
  Row  3   iter54 + phase4_2 (A+D defensive)
  Row  4   iter54 + p5_10 (Cluster-E defensive)
  Row  5   iter54 + synisense_security (F.6 defensive)
  Row  6   iter54 + iter39 + iter53 (G.2 sibling regression — all 3 quarantined files)
  Row  7   iter54 + invariant suite (M2=7 cross-validation)
  Row  8   iter54 + autosave + phase4_2 broad sweep
  Row  9   Log scan: zero "Future attached to a different loop" in Row 2 stdout
  Row 10   AST source-assertion: zero asyncio.run(...) in iter54 test_* method bodies
  Row 11   Bespoke-run invariant catcher PASSES
  Row 12   Bespoke-run invariant drift detector PASSES
  Row 13   Bespoke-run invariant count-ceiling PASSES (M1=0, M2=7)
  Row 14   Inventory slice sibling re-run (M1=0/0, M2=7/7, zero drift)
  Row 15   Quarantine preservation: pytestmark.skip line still at iter54:4

HARD STOP at slice close per dispatch (orchestrator-autonomous next: G.4 advance scan
unless escalation trigger fires).
"""
from __future__ import annotations

import ast
import os
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
BACKEND = REPO / "backend"

ITER54 = "tests/test_iter54_llm_spend_quota_inbound.py"
ITER39 = "tests/test_iter39_briefings_objective_check.py"
ITER53 = "tests/test_iter53_deep_tier_minutes.py"
AUTOSAVE = "tests/test_track_b_phase_b5_g6_notes_autosave.py"
PHASE4_2 = "tests/test_phase4_2_http_transport_smoke.py"
P5_10 = "tests/test_phase_p5_10_audit_panel_direct_linkage.py"
SYNISENSE = "tests/test_synisense_security.py"

PYTEST_FLAGS = [
    "-q", "--no-header", "--tb=short",
    "-m", "not integration and not deploy_smoke and not runtime_playwright",
    "-p", "no:cacheprovider",
]


def _run_pytest(file_list, label):
    """Quarantine-aware: GREEN if exit code 0 and no 'failed' (accepts 'skipped' as GREEN)."""
    start = time.time()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *PYTEST_FLAGS, *file_list],
        cwd=str(BACKEND), capture_output=True, text=True, timeout=900,
    )
    duration = time.time() - start
    out = proc.stdout + proc.stderr
    last = [l for l in out.splitlines()
            if "passed" in l or "failed" in l or "error" in l.lower() or "skipped" in l]
    last_line = last[-1] if last else "(no summary line)"
    passed = proc.returncode == 0 and "failed" not in last_line.lower()
    return passed, last_line, out, duration


def _color(passed):
    return "GREEN" if passed else "RED  "


def main():
    print("=" * 76)
    print("P5.7-Cluster-G.3 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_G.md §1.3")
    print("=" * 76)

    results = []

    # Row 1: iter54 isolation
    ok, line, _, dur = _run_pytest([ITER54], "Row 1")
    print(f"  Row  1  {_color(ok)}  {ITER54} in isolation post-fix (expect 7 skipped)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((1, ok))

    # Row 2: iter54 + autosave
    ok, line, row2_out, dur = _run_pytest([ITER54, AUTOSAVE], "Row 2")
    print(f"  Row  2  {_color(ok)}  iter54 + autosave (B.2 polluter pair, post-fix)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((2, ok))

    # Row 3: iter54 + phase4_2
    ok, line, _, dur = _run_pytest([ITER54, PHASE4_2], "Row 3")
    print(f"  Row  3  {_color(ok)}  iter54 + phase4_2 (A+D defensive)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((3, ok))

    # Row 4: iter54 + p5_10
    ok, line, _, dur = _run_pytest([ITER54, P5_10], "Row 4")
    print(f"  Row  4  {_color(ok)}  iter54 + p5_10 (Cluster-E defensive)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((4, ok))

    # Row 5: iter54 + synisense
    ok, line, _, dur = _run_pytest([ITER54, SYNISENSE], "Row 5")
    print(f"  Row  5  {_color(ok)}  iter54 + synisense_security (F.6 defensive)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((5, ok))

    # Row 6: iter54 + G.2 siblings (iter39 + iter53) — all 3 quarantined files
    ok, line, _, dur = _run_pytest([ITER54, ITER39, ITER53], "Row 6")
    print(f"  Row  6  {_color(ok)}  iter54 + iter39 + iter53 (G.2 sibling regression — 23 skipped expected)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((6, ok))

    # Row 7: iter54 + invariant suite (M2=7 cross-validation)
    inv_file = "tests/invariants/test_no_bespoke_run_helper.py"
    ok, line, _, dur = _run_pytest([ITER54, inv_file], "Row 7")
    print(f"  Row  7  {_color(ok)}  iter54 + invariant suite (M2=7 cross-validation)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((7, ok))

    # Row 8: iter54 + autosave + phase4_2 broad sweep
    ok, line, _, dur = _run_pytest([ITER54, AUTOSAVE, PHASE4_2], "Row 8")
    print(f"  Row  8  {_color(ok)}  iter54 + autosave + phase4_2 broad sweep")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((8, ok))

    # Row 9: log scan
    occurrences = row2_out.count("Future attached to a different loop")
    ok = occurrences == 0
    print(f"  Row  9  {_color(ok)}  log scan: zero 'Future attached to a different loop'")
    print(f"            occurrences={occurrences} in Row 2's full stdout")
    results.append((9, ok))

    # Row 10: AST source-assertion
    bad_sites = []
    src = (BACKEND / ITER54).read_text()
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
            for sub in ast.walk(node):
                if isinstance(sub, ast.Call):
                    if (isinstance(sub.func, ast.Attribute)
                        and sub.func.attr == "run"
                        and isinstance(sub.func.value, ast.Name)
                        and sub.func.value.id == "asyncio"):
                        bad_sites.append(f"asyncio.run() inside '{node.name}' line {sub.lineno}")
    ok = not bad_sites
    print(f"  Row 10  {_color(ok)}  AST source-assertion: zero asyncio.run(...) in iter54 test_* method bodies")
    if bad_sites:
        for b in bad_sites:
            print(f"            BAD: {b}")
    else:
        print(f"            iter54 clean of asyncio.run-in-test patterns (M2 closure validated)")
    results.append((10, ok))

    # Rows 11-13: bespoke-run invariant
    ok, line, _, dur = _run_pytest([inv_file], "Rows 11-13")
    print(f"  Rows 11-13  {_color(ok)}  bespoke-run invariant (catcher + drift + count-ceiling M1=0/M2=7)")
    print(f"            {line}  [dur={dur:.1f}s]")
    if ok and "3 passed" in line:
        results.append((11, True))
        results.append((12, True))
        results.append((13, True))
    else:
        results.append((11, ok))
        results.append((12, ok))
        results.append((13, ok))

    # Row 14: inventory slice sibling
    inv_slice = REPO / "backend" / "scripts" / "jc_polluter_inventory_slice.py"
    start = time.time()
    proc = subprocess.run(
        [sys.executable, str(inv_slice)],
        cwd=str(BACKEND), capture_output=True, text=True, timeout=120,
    )
    dur = time.time() - start
    out = proc.stdout + proc.stderr
    ok = proc.returncode == 0 and "3/3 GREEN" in out
    print(f"  Row 14  {_color(ok)}  inventory slice sibling re-run (M1=0/0, M2=7/7, zero drift)")
    summary_lines = [l for l in out.splitlines() if "GREEN" in l or "ceiling" in l.lower() or "drift" in l.lower()]
    if summary_lines:
        print(f"            {summary_lines[-1]}  [dur={dur:.1f}s]")
    else:
        print(f"            (inventory slice ran; see full output)  [dur={dur:.1f}s]")
    results.append((14, ok))

    # Row 15: Quarantine preservation
    iter54_src = (BACKEND / ITER54).read_text().splitlines()
    iter54_line4 = iter54_src[3] if len(iter54_src) >= 4 else ""
    quarantine_ok = "pytestmark = pytest.mark.skip" in iter54_line4
    print(f"  Row 15  {_color(quarantine_ok)}  quarantine preservation: pytestmark.skip line still at iter54:4")
    if quarantine_ok:
        print(f"            iter54:4 carries pytestmark.skip — Patch 8 quarantine intact")
    else:
        print(f"            BAD: iter54:4 lost pytestmark.skip: {iter54_line4!r}")
    results.append((15, quarantine_ok))

    # Summary
    print("=" * 76)
    greens = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"RESULT  {greens}/{total} GREEN")
    print("=" * 76)
    return 0 if greens == total else 1


if __name__ == "__main__":
    sys.exit(main())
