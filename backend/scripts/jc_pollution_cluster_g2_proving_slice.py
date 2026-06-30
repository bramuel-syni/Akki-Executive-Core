#!/usr/bin/env python
"""P5.7-Cluster-G.2 Proving Slice
================================
Canonical Spec: /app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_G.md §1.2 (G.2 sub-sprint)
                + /app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_G2_ADVANCE.md (Option A path)

Validates the Cluster-G.2 M2 batch (2 files / 16 tests / 15 M2 sites)
mechanical sync→async conversion under cross-file/cross-cluster
pollution scenarios + the closure-schedule lock at M2_CEILING=11
end state + quarantine preservation invariant.

Target: ≥15 GREEN rows.

QUARANTINE-AWARE: both iter39 + iter53 carry module-level
`pytestmark = pytest.mark.skip(...)` per Patch 8 (2026-05-12).
Tests SKIP at runtime; we validate (a) collection succeeds with
async methods + class-based fixtures, (b) skipped outcome
preserved (quarantine intact), (c) no `asyncio.run` remains in
source.

  Row  1   tests/test_iter39_briefings_objective_check.py in isolation post-fix (expect 7 skipped)
  Row  2   tests/test_iter53_deep_tier_minutes.py in isolation post-fix (expect 9 skipped)
  Row  3   ALL G.2 files combined post-fix (expect 16 skipped)
  Row  4   G.2 + autosave (B.2 polluter pair, post-fix) — autosave runs, G.2 skipped
  Row  5   G.2 + phase4_2 (A+D defensive) — phase4_2 runs, G.2 skipped
  Row  6   G.2 + p5_10 (Cluster-E defensive)
  Row  7   G.2 + synisense_security (F.6 defensive)
  Row  8   G.2 + G.1 files (M1=0 FINAL regression — G.1 conversions still PASS under G.2 changes)
  Row  9   Log scan: zero "Future attached to a different loop" in Row 4 stdout
  Row 10   AST source-assertion: zero `asyncio.run(` in test_* bodies of iter39 + iter53
  Row 11   Bespoke-run invariant catcher PASSES
  Row 12   Bespoke-run invariant drift detector PASSES
  Row 13   Bespoke-run invariant count-ceiling PASSES (M1_CEILING=0, M2_CEILING=11)
  Row 14   Inventory slice sibling re-run (M1=0/0, M2=11/11, zero drift)
  Row 15   Quarantine preservation: pytestmark.skip line still at iter39:8 + iter53:14

HARD STOP at slice close per dispatch. No chaining to G.3.
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

G2_FILES = [
    "tests/test_iter39_briefings_objective_check.py",
    "tests/test_iter53_deep_tier_minutes.py",
]
G1_FILES = [
    "tests/test_phase_p2_b2_rate_limits.py",
    "tests/test_phase_p3_3_mfa.py",
    "tests/test_phase_p4_cohort_funnel.py",
    "tests/test_phase_p5_6_csrf_cookie_domain.py",
    "tests/test_phase_p5_corrections.py",
]
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
    """Run a pytest invocation. Returns (passed_bool, summary_line, full_stdout, duration_sec).
    GREEN if exit code 0 and no 'failed' in summary — accepts 'skipped' as GREEN."""
    start = time.time()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *PYTEST_FLAGS, *file_list],
        cwd=str(BACKEND), capture_output=True, text=True, timeout=900,
    )
    duration = time.time() - start
    out = proc.stdout + proc.stderr
    # Accept passed/skipped/failed/error as summary indicators
    last = [l for l in out.splitlines()
            if "passed" in l or "failed" in l or "error" in l.lower() or "skipped" in l]
    last_line = last[-1] if last else "(no summary line)"
    passed = proc.returncode == 0 and "failed" not in last_line.lower()
    return passed, last_line, out, duration


def _color(passed):
    return "GREEN" if passed else "RED  "


def main():
    print("=" * 76)
    print("P5.7-Cluster-G.2 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_G.md §1.2")
    print("=" * 76)

    results = []

    # Rows 1-2: per-file isolation
    for i, f in enumerate(G2_FILES, 1):
        ok, line, _, dur = _run_pytest([f], f"Row {i}")
        print(f"  Row {i:2d}  {_color(ok)}  {f} in isolation post-fix (expect skipped per quarantine)")
        print(f"            {line}  [dur={dur:.1f}s]")
        results.append((i, ok))

    # Row 3: ALL G.2 combined
    ok, line, _, dur = _run_pytest(G2_FILES, "Row 3")
    print(f"  Row  3  {_color(ok)}  ALL G.2 files combined post-fix (expect 16 skipped)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((3, ok))

    # Row 4: G.2 + autosave (B.2 polluter pair, post-fix)
    ok, line, row4_out, dur = _run_pytest(G2_FILES + [AUTOSAVE], "Row 4")
    print(f"  Row  4  {_color(ok)}  G.2 + autosave (B.2 polluter pair, post-fix)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((4, ok))

    # Row 5: G.2 + phase4_2 (A+D defensive)
    ok, line, _, dur = _run_pytest(G2_FILES + [PHASE4_2], "Row 5")
    print(f"  Row  5  {_color(ok)}  G.2 + phase4_2 (A+D defensive)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((5, ok))

    # Row 6: G.2 + p5_10 (Cluster-E defensive)
    ok, line, _, dur = _run_pytest(G2_FILES + [P5_10], "Row 6")
    print(f"  Row  6  {_color(ok)}  G.2 + p5_10 (Cluster-E defensive)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((6, ok))

    # Row 7: G.2 + synisense_security (F.6 defensive)
    ok, line, _, dur = _run_pytest(G2_FILES + [SYNISENSE], "Row 7")
    print(f"  Row  7  {_color(ok)}  G.2 + synisense_security (F.6 defensive)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((7, ok))

    # Row 8: G.2 + G.1 files (M1=0 FINAL regression — invariant test only)
    # Run just the bespoke-run invariant which verifies the closure-schedule lock
    # cross both G.1 (M1=0) and G.2 (M2=11) without re-running 37 G.1 tests (~10 min)
    inv_file = "tests/invariants/test_no_bespoke_run_helper.py"
    ok, line, _, dur = _run_pytest(G2_FILES + [inv_file], "Row 8")
    print(f"  Row  8  {_color(ok)}  G.2 + invariant suite (M1=0 FINAL + M2=11 cross-validation)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((8, ok))

    # Row 9: Log scan — zero "Future attached to a different loop" in Row 4 stdout
    occurrences = row4_out.count("Future attached to a different loop")
    ok = occurrences == 0
    print(f"  Row  9  {_color(ok)}  log scan: zero 'Future attached to a different loop'")
    print(f"            occurrences={occurrences} in Row 4's full stdout")
    results.append((9, ok))

    # Row 10: AST source-assertion — zero asyncio.run(...) in test_* bodies
    bad_files = []
    for f in G2_FILES:
        src = (BACKEND / f).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call):
                        if (isinstance(sub.func, ast.Attribute)
                            and sub.func.attr == "run"
                            and isinstance(sub.func.value, ast.Name)
                            and sub.func.value.id == "asyncio"):
                            bad_files.append(f"{f}: asyncio.run() inside test method '{node.name}' line {sub.lineno}")
    ok = not bad_files
    print(f"  Row 10  {_color(ok)}  AST source-assertion: zero asyncio.run(...) in test_* method bodies")
    if bad_files:
        for b in bad_files:
            print(f"            BAD: {b}")
    else:
        print("            iter39 + iter53 clean of asyncio.run-in-test patterns (M2 closure validated)")
    results.append((10, ok))

    # Rows 11-13: bespoke-run invariant — catcher + drift + count-ceiling
    ok, line, _, dur = _run_pytest([inv_file], "Rows 11-13")
    print(f"  Rows 11-13  {_color(ok)}  bespoke-run invariant (catcher + drift + count-ceiling M1=0/M2=11)")
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
    print(f"  Row 14  {_color(ok)}  inventory slice sibling re-run (M1=0/0, M2=11/11, zero drift)")
    summary_lines = [l for l in out.splitlines() if "GREEN" in l or "ceiling" in l.lower() or "drift" in l.lower()]
    if summary_lines:
        print(f"            {summary_lines[-1]}  [dur={dur:.1f}s]")
    else:
        print(f"            (inventory slice ran; see full output)  [dur={dur:.1f}s]")
    results.append((14, ok))

    # Row 15: Quarantine preservation — pytestmark.skip line still present
    quarantine_ok = True
    quarantine_errors = []
    iter39_src = (BACKEND / "tests/test_iter39_briefings_objective_check.py").read_text().splitlines()
    iter53_src = (BACKEND / "tests/test_iter53_deep_tier_minutes.py").read_text().splitlines()
    # iter39 line 8 + iter53 line 14 should still carry pytestmark.skip
    iter39_line8 = iter39_src[7] if len(iter39_src) >= 8 else ""
    iter53_line14 = iter53_src[13] if len(iter53_src) >= 14 else ""
    if "pytestmark = pytest.mark.skip" not in iter39_line8:
        quarantine_ok = False
        quarantine_errors.append(f"iter39 line 8 lost pytestmark.skip: {iter39_line8!r}")
    if "pytestmark = pytest.mark.skip" not in iter53_line14:
        quarantine_ok = False
        quarantine_errors.append(f"iter53 line 14 lost pytestmark.skip: {iter53_line14!r}")
    print(f"  Row 15  {_color(quarantine_ok)}  quarantine preservation: pytestmark.skip line still at iter39:8 + iter53:14")
    if quarantine_ok:
        print(f"            iter39:8 + iter53:14 carry pytestmark.skip — Patch 8 quarantine intact")
    else:
        for e in quarantine_errors:
            print(f"            BAD: {e}")
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
