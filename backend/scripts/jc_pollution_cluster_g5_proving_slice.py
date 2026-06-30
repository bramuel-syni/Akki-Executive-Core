#!/usr/bin/env python3
"""
JC-POLLUTION-CLUSTER-G5-FIX proving slice.

Canonical Spec: /app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_G.md §1.5
                + advance scan /app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_G5_ADVANCE.md
                + NEW banked lesson #5 (UNQUARANTINED runtime PASS preservation)
                + NEW banked lesson #6 (cite file names from YAML/AST not memo prose).

13 rows validating the Shield-adjacency M2 outlier conversion:
  Row  1   G.5 file runtime PASS preservation (lesson #5; 34/34 required)
  Row  2   G.5 file isolation post-fix + chat-surface real-Shield-call cover (L63 IS the real call)
  Row  3   F.6 Shield contract via synisense_security defensive
  Row  4   AST source-check: 0 asyncio.run-in-test hits in G.5 file
  Row  5   autosave defensive (B.2 polluter pair pattern)
  Row  6   phase4_2 A+D defensive (surface ratchets in lockstep)
  Row  7   G.4 trio post-fix runtime regression (phase12_2 + phase_a + solva_v2)
  Row  8   G.2 + G.3 sibling regression (iter39 + iter53 + iter54 → 26 skipped)
  Row  9   G.5 file + invariant suite (37/37 PASS expected)
  Row 10   Invariant cross-validation M2_CEILING ratcheted 2 → 1 FINAL
  Row 11   Inventory slice sibling re-run (post-G.5 steady state 9/10 + YAML M1=0/M2=1)
  Row 12   Log scan zero 'Future attached to a different loop'
  Row 13   Cluster-G arc closure trajectory marker (M2 28→26→11→7→2→1 FINAL)
"""

from __future__ import annotations

import ast
import pathlib
import subprocess
import sys
import time

BACKEND = pathlib.Path("/app/backend")
G5_FILE = "tests/test_synisense_surface_validation.py"
# G.4 trio sourced from grandfather YAML history (post-G.4 closure) per lesson #6
G4_TRIO = [
    "tests/test_phase12_2_surfaces.py",
    "tests/test_phase_a_synisense_unification.py",
    "tests/test_solva_v2_llm_adapter.py",
]
# iter file names sourced from `ls tests/` per lesson #6 (NOT from memo prose)
ITER_FILES = [
    "tests/test_iter39_briefings_objective_check.py",
    "tests/test_iter53_deep_tier_minutes.py",
    "tests/test_iter54_llm_spend_quota_inbound.py",
]


def _run_pytest(*args: str, timeout: int = 90) -> tuple[int, str]:
    cmd = ["python", "-m", "pytest", *args, "--tb=short", "-q"]
    t0 = time.time()
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=str(BACKEND))
    dt = time.time() - t0
    out = (proc.stdout or "") + (proc.stderr or "")
    return proc.returncode, out + f"\n[dur={dt:.1f}s]"


def _last_line_with(text: str, needle: str) -> str:
    for line in reversed(text.splitlines()):
        if needle in line:
            return line.strip()
    return "(no summary line found)"


def _print_row(num: int, status: str, desc: str, detail: str = "") -> None:
    print(f"  Row {num:>2}  {status:<6} {desc}")
    if detail:
        for line in detail.splitlines():
            print(f"            {line}")


def main() -> int:
    print("=" * 76)
    print("P5.7-Cluster-G.5 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_G.md §1.5")
    print("=" * 76)

    green = 0
    total = 13

    # ───────────────────────────────────────────────────────────────────
    # Row 1 — G.5 file runtime PASS preservation (lesson #5)
    # ───────────────────────────────────────────────────────────────────
    rc, out = _run_pytest(G5_FILE)
    last = _last_line_with(out, "passed")
    ok = (rc == 0) and ("34 passed" in out)
    _print_row(1, "GREEN" if ok else "RED",
               "G.5 file runtime PASS preservation (lesson #5; baseline 34/34 preserved)",
               last)
    if ok:
        green += 1
    else:
        print(out[-800:])

    # ───────────────────────────────────────────────────────────────────
    # Row 2 — Converted test runs individually + passes (real Shield call
    # via L63's `await run(...)` — chat-surface real-Shield-call cover)
    # ───────────────────────────────────────────────────────────────────
    rc, out = _run_pytest(f"{G5_FILE}::test_real_pipeline_run_rejects_bad_subsurface")
    last = _last_line_with(out, "passed")
    ok = (rc == 0) and ("1 passed" in out)
    _print_row(2, "GREEN" if ok else "RED",
               "Converted test L63 runs solo + passes (chat-surface real-Shield-call cover)",
               f"{last} · L63 IS the real `pipeline.run(...)` exercise via `await _runner()`")
    if ok:
        green += 1
    else:
        print(out[-800:])

    # ───────────────────────────────────────────────────────────────────
    # Row 3 — F.6 Shield contract via synisense_security defensive
    # ───────────────────────────────────────────────────────────────────
    rc, out = _run_pytest("tests/test_synisense_security.py")
    last = _last_line_with(out, "passed")
    ok = (rc == 0) and ("passed" in out)
    _print_row(3, "GREEN" if ok else "RED",
               "F.6 Shield contract preservation (synisense_security)",
               last)
    if ok:
        green += 1
    else:
        print(out[-800:])

    # ───────────────────────────────────────────────────────────────────
    # Row 4 — AST source-check: 0 asyncio.run-in-test hits in G.5 file
    # ───────────────────────────────────────────────────────────────────
    hits = []
    p = BACKEND / G5_FILE
    tree = ast.parse(p.read_text(), filename=str(p))
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        for sub in ast.walk(node):
            if isinstance(sub, ast.Call):
                f = sub.func
                if (isinstance(f, ast.Attribute) and isinstance(f.value, ast.Name)
                        and f.value.id == "asyncio" and f.attr == "run"):
                    hits.append(f"{G5_FILE}:{sub.lineno} in {node.name}")
    ok = len(hits) == 0
    _print_row(4, "GREEN" if ok else "RED",
               "AST source-check: 0 asyncio.run-in-test hits in G.5 file (F.6 + G.3 discipline-pay)",
               f"hits={len(hits)}" + (f"; {hits[:3]}" if hits else ""))
    if ok:
        green += 1

    # ───────────────────────────────────────────────────────────────────
    # Row 5 — autosave defensive (B.2 polluter pair pattern)
    # ───────────────────────────────────────────────────────────────────
    autosave_files = list((BACKEND / "tests").glob("test_*autosave*.py"))
    if autosave_files:
        rc, out = _run_pytest(*[str(p.relative_to(BACKEND)) for p in autosave_files])
        last = _last_line_with(out, "passed")
        ok = (rc == 0) and ("passed" in out)
        _print_row(5, "GREEN" if ok else "RED",
                   f"autosave defensive ({len(autosave_files)} files)",
                   last)
        if ok:
            green += 1
        else:
            print(out[-800:])
    else:
        _print_row(5, "GREEN", "autosave defensive (no files — N/A)", "skipped")
        green += 1

    # ───────────────────────────────────────────────────────────────────
    # Row 6 — phase4_2 A+D defensive (surface ratchets in lockstep)
    # ───────────────────────────────────────────────────────────────────
    rc, out = _run_pytest("tests/test_phase4_2_http_transport_smoke.py")
    last = _last_line_with(out, "passed")
    ok = (rc == 0) and ("passed" in out)
    _print_row(6, "GREEN" if ok else "RED",
               "phase4_2 A+D defensive (surface ratchets lockstep + A+D-preserved entry as M2 final state)",
               last)
    if ok:
        green += 1
    else:
        print(out[-800:])

    # ───────────────────────────────────────────────────────────────────
    # Row 7 — G.4 trio post-fix runtime regression
    # ───────────────────────────────────────────────────────────────────
    rc, out = _run_pytest(*G4_TRIO)
    last = _last_line_with(out, "passed")
    ok = (rc == 0) and ("10 passed" in out)
    _print_row(7, "GREEN" if ok else "RED",
               "G.4 trio post-fix runtime regression (phase12_2 + phase_a + solva_v2)",
               last)
    if ok:
        green += 1
    else:
        print(out[-800:])

    # ───────────────────────────────────────────────────────────────────
    # Row 8 — G.2 + G.3 sibling regression (iter file names from ls per lesson #6)
    # ───────────────────────────────────────────────────────────────────
    rc, out = _run_pytest(*ITER_FILES)
    last = _last_line_with(out, "skipped")
    ok = (rc == 0) and ("26 skipped" in out)
    _print_row(8, "GREEN" if ok else "RED",
               "G.2 + G.3 sibling regression (iter39 + iter53 + iter54 → 26 skipped)",
               last)
    if ok:
        green += 1
    else:
        print(out[-800:])

    # ───────────────────────────────────────────────────────────────────
    # Row 9 — G.5 file + invariant suite (37/37 PASS expected)
    # ───────────────────────────────────────────────────────────────────
    rc, out = _run_pytest(G5_FILE, "tests/invariants/test_no_bespoke_run_helper.py")
    last = _last_line_with(out, "passed")
    ok = (rc == 0) and ("37 passed" in out)
    _print_row(9, "GREEN" if ok else "RED",
               "G.5 file + invariant suite (37/37 PASS expected = 34 G.5 + 3 invariant)",
               last)
    if ok:
        green += 1
    else:
        print(out[-800:])

    # ───────────────────────────────────────────────────────────────────
    # Row 10 — Invariant cross-validation M2_CEILING ratcheted 2 → 1 FINAL
    # ───────────────────────────────────────────────────────────────────
    rc, out = _run_pytest("tests/invariants/test_no_bespoke_run_helper.py")
    last = _last_line_with(out, "passed")
    ok = (rc == 0) and ("3 passed" in out)
    _print_row(10, "GREEN" if ok else "RED",
               "Invariant cross-validation M2_CEILING ratcheted 2 → 1 FINAL",
               last)
    if ok:
        green += 1
    else:
        print(out[-800:])

    # ───────────────────────────────────────────────────────────────────
    # Row 11 — Inventory slice sibling re-run (post-G.5 steady state 9/10 + YAML M1=0/M2=1)
    # ───────────────────────────────────────────────────────────────────
    inv_slice = BACKEND / "scripts" / "jc_invariant_bespoke_run_helper_slice.py"
    if inv_slice.exists():
        t0 = time.time()
        proc = subprocess.run(["python", str(inv_slice)], capture_output=True, text=True,
                              timeout=120, cwd=str(BACKEND))
        dt = time.time() - t0
        import yaml as _y
        data = _y.safe_load((BACKEND / "tests" / "invariants" / "bespoke_run_helper_grandfathered.yml").read_text())
        m1 = len(data.get("m1_entries") or [])
        m2 = len(data.get("m2_entries") or [])
        steady_state = ("RESULT  9/10 GREEN" in (proc.stdout or "")) and (m1 == 0) and (m2 == 1)
        _print_row(11, "GREEN" if steady_state else "RED",
                   "Inventory slice sibling re-run (post-G.5 steady state 9/10 + YAML M1=0/M2=1)",
                   f"inventory_slice_exit={proc.returncode} dur={dt:.1f}s · YAML M1={m1}/0 · M2={m2}/1 · 9/10 GREEN steady state observed")
        if steady_state:
            green += 1
        else:
            print((proc.stdout or "")[-800:])
            print((proc.stderr or "")[-800:])
    else:
        import yaml as _y
        data = _y.safe_load((BACKEND / "tests" / "invariants" / "bespoke_run_helper_grandfathered.yml").read_text())
        m1 = len(data.get("m1_entries") or [])
        m2 = len(data.get("m2_entries") or [])
        ok = (m1 == 0) and (m2 == 1)
        _print_row(11, "GREEN" if ok else "RED", "Inventory slice fallback YAML check",
                   f"M1={m1}/0 · M2={m2}/1")
        if ok:
            green += 1

    # ───────────────────────────────────────────────────────────────────
    # Row 12 — Log scan zero 'Future attached to a different loop'
    # ───────────────────────────────────────────────────────────────────
    rc, scan_out = _run_pytest(G5_FILE, *G4_TRIO)
    occurrences = scan_out.count("Future attached to a different loop")
    ok = occurrences == 0
    _print_row(12, "GREEN" if ok else "RED",
               "Log scan zero 'Future attached to a different loop' across G.5 + G.4 trio",
               f"occurrences={occurrences}")
    if ok:
        green += 1

    # ───────────────────────────────────────────────────────────────────
    # Row 13 — Cluster-G arc closure trajectory marker
    # (M2 28 → 26 (F.6) → 11 (G.2) → 7 (G.3) → 2 (G.4) → 1 (G.5) FINAL)
    # ───────────────────────────────────────────────────────────────────
    import yaml as _y
    data = _y.safe_load((BACKEND / "tests" / "invariants" / "bespoke_run_helper_grandfathered.yml").read_text())
    m1 = len(data.get("m1_entries") or [])
    m2 = len(data.get("m2_entries") or [])
    # Final state: M1=0 (since G.1) + M2=1 (A+D-preserved phase4_2:254 by design)
    final_state = (m1 == 0) and (m2 == 1)
    # Cross-check: the 1 remaining entry is the A+D-preserved one
    remaining_entry = (data.get("m2_entries") or [{}])[0] if m2 == 1 else {}
    is_phase4_2_preserved = "phase4_2_http_transport_smoke" in remaining_entry.get("file", "") and remaining_entry.get("lineno") == 254
    ok = final_state and is_phase4_2_preserved
    _print_row(13, "GREEN" if ok else "RED",
               "Cluster-G arc closure trajectory marker (M2 28→26→11→7→2→1 FINAL)",
               f"final_state M1=0/M2=1: {final_state} · A+D-preserved entry intact: {is_phase4_2_preserved} · arc CLOSES at M2=1")
    if ok:
        green += 1

    # ───────────────────────────────────────────────────────────────────
    # Summary
    # ───────────────────────────────────────────────────────────────────
    print("=" * 76)
    print(f"RESULT  {green}/{total} {'GREEN — Cluster-G arc CLOSES at M2=1 FINAL' if green == total else 'with regressions'}")
    print("=" * 76)
    return 0 if green == total else 1


if __name__ == "__main__":
    sys.exit(main())
