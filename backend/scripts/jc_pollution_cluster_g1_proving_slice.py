#!/usr/bin/env python
"""P5.7-Cluster-G.1 Proving Slice
================================
Canonical Spec: /app/memory/jc_artifacts/FAILING_TEST_TRACKER.md
                + /app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_G.md §1 (G.1 sub-sprint)
                + /app/memory/sprints/CLUSTER_F_RETROSPECTIVE.md §5 (banked patterns)

Validates the Cluster-G.1 M1 batch (5 files / 37 sync tests / 5 sites)
mechanical sync→async conversion under cross-file/cross-cluster
pollution scenarios + the closure-schedule lock at M1_CEILING=0 end state.

Target: ≥15 GREEN rows.

  Row  1   tests/test_phase_p2_b2_rate_limits.py in isolation post-fix
  Row  2   tests/test_phase_p3_3_mfa.py in isolation post-fix
  Row  3   tests/test_phase_p4_cohort_funnel.py in isolation post-fix
  Row  4   tests/test_phase_p5_6_csrf_cookie_domain.py in isolation post-fix
  Row  5   tests/test_phase_p5_corrections.py in isolation post-fix
  Row  6   ALL 5 G.1 files combined post-fix (single pytest invocation)
  Row  7   G.1 + autosave (Cluster-F's previously polluted target) post-fix
  Row  8   G.1 + phase4_2 (A+D defensive) post-fix
  Row  9   G.1 + p5_10 (Cluster-E defensive) post-fix
  Row 10   G.1 + synisense_security (F.6 defensive) post-fix
  Row 11   Log scan: zero "Future attached to a different loop" in Row 6 stdout
  Row 12   AST source-assertion: zero `def _run(` + zero `asyncio.get_event_loop().run_until_complete` in G.1 files
  Row 13   Bespoke-run invariant catcher PASSES (test_no_bespoke_run_helper_in_tests)
  Row 14   Bespoke-run invariant drift detector PASSES (test_grandfathered_entries_match_actual_helpers)
  Row 15   Bespoke-run invariant count-ceiling PASSES with M1_CEILING=0, M2_CEILING=26

  Bonus Row 16   Inventory slice sibling re-run — M1=0/0 ceiling, M2=26/26 ceiling, zero drift

HARD STOP at proving-slice close. No chaining to G.2.
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

# G.1 files (verified against bespoke_run_helper_grandfathered.yml YAML at scope-memo close)
G1_FILES = [
    "tests/test_phase_p2_b2_rate_limits.py",
    "tests/test_phase_p3_3_mfa.py",
    "tests/test_phase_p4_cohort_funnel.py",
    "tests/test_phase_p5_6_csrf_cookie_domain.py",
    "tests/test_phase_p5_corrections.py",
]
# Defensive pairings (Cluster-F prior cluster-fixed files)
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
    """Run a pytest invocation, return (passed_bool, last_line, full_stdout, duration_sec)."""
    start = time.time()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", *PYTEST_FLAGS, *file_list],
        cwd=str(BACKEND), capture_output=True, text=True, timeout=900,
    )
    duration = time.time() - start
    out = proc.stdout + proc.stderr
    last = [l for l in out.splitlines() if "passed" in l or "failed" in l or "error" in l.lower()]
    last_line = last[-1] if last else "(no summary line)"
    passed = proc.returncode == 0 and "failed" not in last_line.lower()
    return passed, last_line, out, duration


def _color(passed):
    return "GREEN" if passed else "RED  "


def main():
    print("=" * 76)
    print("P5.7-Cluster-G.1 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_G.md §1")
    print("=" * 76)

    results = []
    row6_out = ""

    # Rows 1-5: per-file isolation
    for i, f in enumerate(G1_FILES, 1):
        ok, line, _, dur = _run_pytest([f], f"Row {i}")
        print(f"  Row {i:2d}  {_color(ok)}  {f} in isolation post-fix")
        print(f"            {line}  [dur={dur:.1f}s]")
        results.append((i, ok))

    # Row 6: ALL 5 G.1 combined
    ok, line, row6_out, dur = _run_pytest(G1_FILES, "Row 6")
    print(f"  Row  6  {_color(ok)}  ALL 5 G.1 files combined post-fix")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((6, ok))

    # Row 7: G.1 + autosave (B.2 polluter pair, post-fix)
    ok, line, _, dur = _run_pytest(G1_FILES + [AUTOSAVE], "Row 7")
    print(f"  Row  7  {_color(ok)}  G.1 + autosave (B.2 polluter pair, post-fix)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((7, ok))

    # Row 8: G.1 + phase4_2 (A+D defensive)
    ok, line, _, dur = _run_pytest(G1_FILES + [PHASE4_2], "Row 8")
    print(f"  Row  8  {_color(ok)}  G.1 + phase4_2 (A+D defensive)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((8, ok))

    # Row 9: G.1 + p5_10 (Cluster-E defensive)
    ok, line, _, dur = _run_pytest(G1_FILES + [P5_10], "Row 9")
    print(f"  Row  9  {_color(ok)}  G.1 + p5_10 (Cluster-E defensive)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((9, ok))

    # Row 10: G.1 + synisense_security (F.6 defensive)
    ok, line, _, dur = _run_pytest(G1_FILES + [SYNISENSE], "Row 10")
    print(f"  Row 10  {_color(ok)}  G.1 + synisense_security (F.6 defensive)")
    print(f"            {line}  [dur={dur:.1f}s]")
    results.append((10, ok))

    # Row 11: Log scan — zero "Future attached to a different loop" in Row 6
    occurrences = row6_out.count("Future attached to a different loop")
    ok = occurrences == 0
    print(f"  Row 11  {_color(ok)}  log scan: zero 'Future attached to a different loop'")
    print(f"            occurrences={occurrences} in Row 6's full stdout")
    results.append((11, ok))

    # Row 12: AST source-assertion — zero `_run` helper + zero asyncio.run pattern in G.1 files
    bad_files = []
    for f in G1_FILES:
        src = (BACKEND / f).read_text()
        tree = ast.parse(src)
        # Check 1: no module-level `def _run(`
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == "_run":
                bad_files.append(f"{f}: still has `def _run(...)` at line {node.lineno}")
        # Check 2: no `asyncio.get_event_loop().run_until_complete` literal substring
        if "asyncio.get_event_loop().run_until_complete" in src:
            bad_files.append(f"{f}: still has 'asyncio.get_event_loop().run_until_complete' literal")
        # Check 3: no `asyncio.run(` inside test_* function bodies (M2 leak check)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith("test_"):
                for sub in ast.walk(node):
                    if isinstance(sub, ast.Call):
                        # asyncio.run(...)
                        if (isinstance(sub.func, ast.Attribute)
                            and sub.func.attr == "run"
                            and isinstance(sub.func.value, ast.Name)
                            and sub.func.value.id == "asyncio"):
                            bad_files.append(f"{f}: asyncio.run() inside test_{node.name.removeprefix('test_')} line {sub.lineno}")
    ok = not bad_files
    print(f"  Row 12  {_color(ok)}  AST source-assertion: zero `_run` helpers + zero asyncio.run in test bodies")
    if bad_files:
        for b in bad_files:
            print(f"            BAD: {b}")
    else:
        print("            All 5 G.1 files clean of _run helpers + asyncio.run-in-test patterns")
    results.append((12, ok))

    # Rows 13-15: bespoke-run invariant — catcher + drift + count-ceiling
    inv_file = "tests/invariants/test_no_bespoke_run_helper.py"
    ok, line, inv_out, dur = _run_pytest([inv_file], "Rows 13-15")
    print(f"  Rows 13-15  {_color(ok)}  bespoke-run invariant (catcher + drift + count-ceiling M1=0/M2=26)")
    print(f"            {line}  [dur={dur:.1f}s]")
    if ok and "3 passed" in line:
        results.append((13, True))
        results.append((14, True))
        results.append((15, True))
    else:
        results.append((13, ok))
        results.append((14, ok))
        results.append((15, ok))

    # Bonus Row 16: inventory slice sibling
    inv_slice = REPO / "backend" / "scripts" / "jc_polluter_inventory_slice.py"
    start = time.time()
    proc = subprocess.run(
        [sys.executable, str(inv_slice)],
        cwd=str(BACKEND), capture_output=True, text=True, timeout=120,
    )
    dur = time.time() - start
    out = proc.stdout + proc.stderr
    ok = proc.returncode == 0 and "3/3 GREEN" in out
    print(f"  Row 16  {_color(ok)}  inventory slice sibling re-run (M1=0/0, M2=26/26, zero drift)")
    summary_lines = [l for l in out.splitlines() if "GREEN" in l or "ceiling" in l.lower() or "drift" in l.lower()]
    if summary_lines:
        print(f"            {summary_lines[-1]}  [dur={dur:.1f}s]")
    else:
        print(f"            (inventory slice ran; see full output)  [dur={dur:.1f}s]")
    results.append((16, ok))

    # Summary
    print("=" * 76)
    greens = sum(1 for _, ok in results if ok)
    total = len(results)
    print(f"RESULT  {greens}/{total} GREEN")
    print("=" * 76)
    return 0 if greens == total else 1


if __name__ == "__main__":
    sys.exit(main())
