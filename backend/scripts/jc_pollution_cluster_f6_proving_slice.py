#!/usr/bin/env python3
"""P5.7-Cluster-F.6 fix-sprint proving slice.

Canonical Spec: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1 + §6`
                (sub-sprint F.6 = synisense_security — 1 M2 outlier
                file · Shield-adjacency · TWO-DISPATCH approach;
                advance scan memo P5_7_FIX_SCOPE_CLUSTER_F6_ADVANCE.md
                §3 verdict LOW risk; final Cluster-F sub-sprint)

Target: 11 GREEN. Single-file scope; smaller than F.5's 13.

  Row  1  : synisense_security in isolation post-fix → 3 PASS
  Row  2  : F.6 + autosave (B.2 polluter pair, post-fix) → all PASS
  Row  3  : F.6 + phase4_2 (A+D defensive) → all PASS
  Row  4  : F.6 + p5_10 (Cluster-E defensive) → all PASS
  Row  5  : F.6 + microsoft_pkce (F.5 defensive) → all PASS
  Row  6  : F.6 + csrf (F.3 defensive) → all PASS
  Row  7  : Combined F.6 + autosave + ALL prior cluster-fixed files
            (broad sweep — final pollution-surface-empty validation)
            → all PASS
  Row  8  : Log scan: zero 'Future attached to a different loop'
            across Row 7's full stdout
  Row  9  : AST source-assertion: zero `asyncio.run(...)` calls inside
            `test_*` function bodies of the F.6 file (M2-specific
            shape; not looking for `_run` helper since F.6 was M2)
  Row 10  : Bespoke-run invariant PASSES with M2_CEILING=26 + drift
            detector PASS (closure-schedule lock validated; 28 → 26)
  Row 11  : Shield-contract regression check (AST-level) — both
            M2-converted tests STILL invoke `pipeline_run(...)` with
            same modes (`shield_reversible` + `redact`) AND test 1
            STILL asserts on the same leaky-key absence set
            (`shield_map`, `mapping`, `originals`, `envelope`)
"""
from __future__ import annotations

import ast
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

F6_FILE = "tests/test_synisense_security.py"
AUTOSAVE = "tests/test_track_b_phase_b5_g6_notes_autosave.py"
PHASE4_2 = "tests/test_phase4_2_http_transport_smoke.py"
P5_10 = "tests/test_phase_p5_10_audit_panel_direct_linkage.py"
F5_DEFENSIVE = "tests/test_phase_p2_a2_microsoft_pkce.py"
F3_DEFENSIVE = "tests/test_phase_p3_1_csrf.py"
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


def main() -> int:  # noqa: C901
    print("=" * 76)
    print("P5.7-Cluster-F.6 Proving Slice — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1 + §6")
    print("=" * 76)
    rows: List[Dict] = []

    # ── Row 1 — isolation ──
    rc, summary, _ = _run_pytest([F6_FILE])
    ok = (rc == 0 and "3 passed" in summary)
    rows.append(row(1, f"{F6_FILE} in isolation post-fix (3 passed)", ok, summary))

    # ── Row 2 — F.6 + autosave ──
    rc, summary, _ = _run_pytest([F6_FILE, AUTOSAVE])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(2, f"{F6_FILE} + autosave (B.2 polluter pair, post-fix)", ok, summary))

    # ── Row 3 — F.6 + phase4_2 (A+D defensive) ──
    rc, summary, _ = _run_pytest([F6_FILE, PHASE4_2])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(3, f"{F6_FILE} + {PHASE4_2} (A+D defensive)", ok, summary))

    # ── Row 4 — F.6 + p5_10 (Cluster-E defensive) ──
    rc, summary, _ = _run_pytest([F6_FILE, P5_10])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(4, f"{F6_FILE} + {P5_10} (Cluster-E defensive)", ok, summary))

    # ── Row 5 — F.6 + microsoft_pkce (F.5 defensive) ──
    rc, summary, _ = _run_pytest([F6_FILE, F5_DEFENSIVE])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(5, f"{F6_FILE} + {F5_DEFENSIVE} (F.5 defensive)", ok, summary))

    # ── Row 6 — F.6 + csrf (F.3 defensive) ──
    rc, summary, _ = _run_pytest([F6_FILE, F3_DEFENSIVE])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(6, f"{F6_FILE} + {F3_DEFENSIVE} (F.3 defensive)", ok, summary))

    # ── Row 7 — Broad sweep (F.6 + autosave + ALL prior cluster-fixed) ──
    broad_set = [F6_FILE, AUTOSAVE, PHASE4_2, P5_10, F5_DEFENSIVE, F3_DEFENSIVE]
    rc, summary, full_stdout_r7 = _run_pytest(broad_set, capture_full=True)
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(7, "Broad sweep (F.6 + autosave + all prior cluster-fixed)", ok, summary))

    # ── Row 8 — Log scan on Row 7's full stdout ──
    bad_phrase = "attached to a different loop"
    occurrences = full_stdout_r7.lower().count(bad_phrase.lower())
    ok = (occurrences == 0)
    rows.append(row(8, "log scan: zero 'Future attached to a different loop'",
                    ok, f"occurrences={occurrences} in Row 7's full stdout"))

    # ── Row 9 — AST source-assertion: zero asyncio.run() calls in test bodies ──
    src = (BACKEND / F6_FILE).read_text(encoding="utf-8")
    tree = ast.parse(src, filename=F6_FILE)
    m2_hits = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        for sub in ast.walk(node):
            if (
                isinstance(sub, ast.Call)
                and isinstance(sub.func, ast.Attribute)
                and sub.func.attr == "run"
                and isinstance(sub.func.value, ast.Name)
                and sub.func.value.id == "asyncio"
            ):
                m2_hits.append((node.name, sub.lineno))
    ok = (not m2_hits)
    rows.append(row(9, "AST source-assertion: zero asyncio.run() in test_* bodies",
                    ok, f"hits={m2_hits}" if m2_hits else "no asyncio.run() calls remain"))

    # ── Row 10 — Bespoke-run invariant + drift detector PASSES ──
    rc, summary, _ = _run_pytest([BESPOKE_INVARIANT])
    ok = (rc == 0 and "failed" not in summary)
    rows.append(row(10, "bespoke-run invariant PASSES (M2_CEILING=26 + drift detector)",
                    ok, summary))

    # ── Row 11 — Shield-contract regression check (AST-level) ──
    # Both M2-converted tests MUST still invoke pipeline_run with the
    # same `mode=` argument values and test 1 MUST still assert on the
    # same leaky-key absence set.
    expected_modes = {"shield_reversible", "redact"}
    expected_leaky_keys = {"shield_map", "mapping", "originals", "envelope"}
    found_modes: set = set()
    found_leaky_keys: set = set()
    test1_name = "test_shield_reversible_produces_shield_map_id_only"
    test2_name = "test_redact_mode_never_creates_shield_map"
    test1_pipeline_call_found = False
    test2_pipeline_call_found = False

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name not in {test1_name, test2_name}:
            continue
        for sub in ast.walk(node):
            # Detect pipeline_run(...) call (could be `await pipeline_run(...)` post-conversion)
            if isinstance(sub, ast.Call):
                # The callable is `pipeline_run` (Name) — since `from services.synisense import run as pipeline_run`
                fn = sub.func
                is_pipeline_run = (
                    isinstance(fn, ast.Name) and fn.id == "pipeline_run"
                )
                if is_pipeline_run:
                    if node.name == test1_name:
                        test1_pipeline_call_found = True
                    elif node.name == test2_name:
                        test2_pipeline_call_found = True
                    for kw in sub.keywords:
                        if kw.arg == "mode" and isinstance(kw.value, ast.Constant):
                            found_modes.add(kw.value.value)
            # Detect leaky-key tuple in test1
            if node.name == test1_name and isinstance(sub, ast.Tuple):
                if all(isinstance(el, ast.Constant) and isinstance(el.value, str) for el in sub.elts):
                    tuple_values = {el.value for el in sub.elts}
                    if expected_leaky_keys.issubset(tuple_values):
                        found_leaky_keys = tuple_values & expected_leaky_keys

    failures = []
    if not test1_pipeline_call_found:
        failures.append(f"test1 ({test1_name}) does not invoke pipeline_run anymore")
    if not test2_pipeline_call_found:
        failures.append(f"test2 ({test2_name}) does not invoke pipeline_run anymore")
    if not expected_modes.issubset(found_modes):
        failures.append(
            f"pipeline_run mode-arg drift — expected {expected_modes}, "
            f"found {found_modes}"
        )
    if found_leaky_keys != expected_leaky_keys:
        failures.append(
            f"test1 leaky-key absence assertion drift — expected {expected_leaky_keys}, "
            f"found {found_leaky_keys}"
        )

    ok = not failures
    rows.append(row(
        11,
        "Shield-contract regression: pipeline_run modes + leaky-key absence set preserved",
        ok,
        "; ".join(failures) if failures else (
            f"modes={sorted(found_modes)} · leaky_keys={sorted(found_leaky_keys)} · "
            f"both test pipeline_run calls present"
        ),
    ))

    # ── Final tally ──
    green = sum(1 for r in rows if r["status"] == "GREEN")
    total = len(rows)
    print("=" * 76)
    print(f"RESULT  {green}/{total} GREEN")
    print("=" * 76)
    return 0 if green == total else 1


if __name__ == "__main__":
    sys.exit(main())
