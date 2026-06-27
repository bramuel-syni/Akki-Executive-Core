#!/usr/bin/env python3
"""INVARIANT-NO-BESPOKE-RUN-HELPER + thin-assertion ceiling proving slice.

Canonical Spec: /app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1
                (Cluster-F closes existing polluters; this invariant
                prevents the anti-pattern from re-introducing itself)

Target: ≥10 GREEN.

Two invariants exercised:

  A. test_no_bespoke_run_helper.py (NEW Step 4.5)
     A1 — baseline scan finds the seeded 13 M1 + 28 M2 sites
     A2 — invariant passes against the baseline YAML (grandfathered)
     A3 — drift detector passes against the baseline YAML
     A4 — count ceiling passes at M1=13/M2=28 baseline
     A5 — NEGATIVE probe: inject NEW M1 helper into a fresh test file
          → invariant FAILS · cleanup restores GREEN
     A6 — NEGATIVE probe: inject NEW M2 asyncio.run in a fresh test file
          → invariant FAILS · cleanup restores GREEN
     A7 — MARKER probe: same M2 inject + `@pytest.mark.acceptable_bespoke_run`
          + `# reason:` comment → invariant PASSES
     A8 — DRIFT probe: add fake entry to YAML pointing at non-existent file
          → drift detector FAILS · cleanup restores GREEN

  B. test_no_thin_assertions.py count-ceiling (Step 4 fix)
     B1 — baseline YAML has 9 entries; ceiling is 10; invariant PASSES
     B2 — bumping ceiling to 8 (below 9) → invariant FAILS · cleanup restores
"""
from __future__ import annotations

import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path("/app")
BACKEND = REPO / "backend"
TESTS_DIR = BACKEND / "tests"
INVARIANTS_DIR = TESTS_DIR / "invariants"

BESPOKE_INVARIANT = "tests/invariants/test_no_bespoke_run_helper.py"
THIN_INVARIANT = "tests/invariants/test_no_thin_assertions.py"
BESPOKE_YAML = INVARIANTS_DIR / "bespoke_run_helper_grandfathered.yml"

PYTEST_BASE = [
    sys.executable, "-m", "pytest",
    "-q", "--no-header", "--tb=short",
    "-m", "not integration and not deploy_smoke and not runtime_playwright",
    "-p", "no:cacheprovider",
]


def _run_pytest(args: List[str]) -> Tuple[int, str]:
    started = time.time()
    proc = subprocess.run(
        PYTEST_BASE + args, cwd=str(BACKEND),
        capture_output=True, text=True, timeout=90,
    )
    dur = time.time() - started
    summary = ""
    for line in (proc.stdout or "").splitlines()[::-1]:
        s = line.strip()
        if " passed" in s or " failed" in s or " error" in s:
            summary = s
            break
    return proc.returncode, summary + f"  [dur={dur:.1f}s]"


def row(num: int, name: str, pred: bool, detail: str = "") -> Dict:
    status = "GREEN" if pred else "RED"
    print(f"  Row {num:>2}  {status:<5}  {name}")
    if detail:
        for line in detail.splitlines():
            print(f"            {line}")
    return {"row": num, "name": name, "status": status, "detail": detail}


def _inject_probe(content: str) -> Path:
    """Write a temp test file into backend/tests/ that ships with cleanup."""
    target = TESTS_DIR / "test_zzz_bespoke_run_probe.py"
    target.write_text(content, encoding="utf-8")
    return target


def _cleanup_probe(p: Path) -> None:
    if p.exists():
        p.unlink()


def main() -> int:  # noqa: C901
    print("=" * 76)
    print("INVARIANT-NO-BESPOKE-RUN-HELPER Proving Slice — "
          "Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1")
    print("=" * 76)
    rows: List[Dict] = []

    # ── Row A1 — baseline scan finds seeded sites ──
    try:
        import yaml as _yaml
        data = _yaml.safe_load(BESPOKE_YAML.read_text(encoding="utf-8"))
        m1_count = len(data.get("m1_entries") or [])
        m2_count = len(data.get("m2_entries") or [])
        ok = (m1_count == 13 and m2_count == 28)
        rows.append(row(1, "baseline YAML has 13 M1 + 28 M2 entries", ok,
                        f"m1_count={m1_count}  m2_count={m2_count}"))
    except Exception as e:  # pragma: no cover
        rows.append(row(1, "baseline YAML readable", False, str(e)))

    # ── Row A2 — invariant PASSES at baseline ──
    rc, summary = _run_pytest([BESPOKE_INVARIANT + "::test_no_bespoke_run_helper_in_tests"])
    ok = (rc == 0 and "passed" in summary)
    rows.append(row(2, "bespoke-run guard PASSES at baseline (everything grandfathered)",
                    ok, summary))

    # ── Row A3 — drift detector PASSES at baseline ──
    rc, summary = _run_pytest([BESPOKE_INVARIANT + "::test_grandfather_list_does_not_drift"])
    ok = (rc == 0 and "passed" in summary)
    rows.append(row(3, "drift detector PASSES at baseline (no stale entries)", ok, summary))

    # ── Row A4 — count-ceiling PASSES at baseline ──
    rc, summary = _run_pytest([BESPOKE_INVARIANT + "::test_grandfather_count_below_ceiling"])
    ok = (rc == 0 and "passed" in summary)
    rows.append(row(4, "count-ceiling PASSES at baseline (M1=13<=13, M2=28<=28)",
                    ok, summary))

    # ── Row A5 — NEGATIVE M1 probe: inject new _run helper, expect FAIL ──
    probe = _inject_probe(
        '"""Test probe for invariant-no-bespoke-run-helper (M1)."""\n'
        "import asyncio\n\n\n"
        "def _run(coro):\n"
        "    return asyncio.get_event_loop().run_until_complete(coro)\n\n\n"
        "def test_probe_placeholder():\n"
        "    assert True\n"
    )
    try:
        rc, summary = _run_pytest([BESPOKE_INVARIANT + "::test_no_bespoke_run_helper_in_tests"])
        ok = (rc != 0 and "failed" in summary)
        rows.append(row(5, "NEGATIVE M1 probe: inject new _run helper → invariant FAILS",
                        ok, summary))
    finally:
        _cleanup_probe(probe)

    # ── Row A6 — NEGATIVE M2 probe: inject new asyncio.run in test body ──
    probe = _inject_probe(
        '"""Test probe for invariant-no-bespoke-run-helper (M2)."""\n'
        "import asyncio\n\n\n"
        "async def _coro():\n"
        "    return 1\n\n\n"
        "def test_probe_m2():\n"
        "    result = asyncio.run(_coro())\n"
        "    assert result == 1\n"
    )
    try:
        rc, summary = _run_pytest([BESPOKE_INVARIANT + "::test_no_bespoke_run_helper_in_tests"])
        ok = (rc != 0 and "failed" in summary)
        rows.append(row(6, "NEGATIVE M2 probe: inject new asyncio.run → invariant FAILS",
                        ok, summary))
    finally:
        _cleanup_probe(probe)

    # ── Row A7 — MARKER probe: same M2 inject + acceptable_bespoke_run marker ──
    probe = _inject_probe(
        '"""Test probe for invariant-no-bespoke-run-helper (M2 marker exemption)."""\n'
        "import asyncio\n"
        "import pytest\n\n\n"
        "async def _coro():\n"
        "    return 1\n\n\n"
        "# reason: pure-Python coroutine, no Motor I/O, loop-isolated\n"
        "@pytest.mark.acceptable_bespoke_run\n"
        "def test_probe_m2_marker():\n"
        "    result = asyncio.run(_coro())\n"
        "    assert result == 1\n"
    )
    try:
        rc, summary = _run_pytest([BESPOKE_INVARIANT + "::test_no_bespoke_run_helper_in_tests"])
        ok = (rc == 0 and "passed" in summary)
        rows.append(row(7, "MARKER probe: M2 site + `acceptable_bespoke_run` marker → PASS",
                        ok, summary))
    finally:
        _cleanup_probe(probe)

    # ── Row A8 — DRIFT probe: add fake entry to YAML, expect drift detector to FAIL ──
    original_yaml = BESPOKE_YAML.read_text(encoding="utf-8")
    drifted = original_yaml.rstrip() + (
        "\n\n  - file: backend/tests/test_does_not_exist_xyz.py\n"
        "    lineno: 1\n"
        "    cluster_f_sub_sprint: \"drift-probe\"\n"
        "    reason: drift probe — file does not exist on disk\n"
    )
    # Inject under m1_entries
    drifted = original_yaml.replace(
        "# M2 entries — asyncio.run(...) inside a test_* function body",
        "  - file: backend/tests/test_does_not_exist_xyz.py\n"
        "    lineno: 1\n"
        "    cluster_f_sub_sprint: \"drift-probe\"\n"
        "    reason: drift probe — file does not exist on disk\n\n"
        "# M2 entries — asyncio.run(...) inside a test_* function body",
        1,
    )
    try:
        BESPOKE_YAML.write_text(drifted, encoding="utf-8")
        rc, summary = _run_pytest([BESPOKE_INVARIANT + "::test_grandfather_list_does_not_drift"])
        ok = (rc != 0 and "failed" in summary)
        rows.append(row(8, "DRIFT probe: stale YAML entry → drift detector FAILS",
                        ok, summary))
    finally:
        BESPOKE_YAML.write_text(original_yaml, encoding="utf-8")

    # ── Row B1 — thin-assertion ceiling PASSES at baseline (9 ≤ 10) ──
    rc, summary = _run_pytest([THIN_INVARIANT + "::test_grandfather_count_below_ceiling"])
    ok = (rc == 0 and "passed" in summary)
    rows.append(row(9, "thin-assertion count-ceiling PASSES (9 ≤ 10)", ok, summary))

    # ── Row B2 — bump ceiling probe: temporarily set ceiling to 8 → expect FAIL ──
    thin_path = BACKEND / "tests/invariants/test_no_thin_assertions.py"
    original_thin = thin_path.read_text(encoding="utf-8")
    bumped_thin = original_thin.replace(
        "GRANDFATHER_CEILING = 10",
        "GRANDFATHER_CEILING = 8",
        1,
    )
    try:
        thin_path.write_text(bumped_thin, encoding="utf-8")
        rc, summary = _run_pytest([THIN_INVARIANT + "::test_grandfather_count_below_ceiling"])
        ok = (rc != 0 and "failed" in summary)
        rows.append(row(10, "thin-assertion ceiling probe: lower ceiling to 8 → FAILS",
                        ok, summary))
    finally:
        thin_path.write_text(original_thin, encoding="utf-8")

    # ── Final tally ──
    green = sum(1 for r in rows if r["status"] == "GREEN")
    total = len(rows)
    print("=" * 76)
    print(f"RESULT  {green}/{total} GREEN")
    print("=" * 76)
    return 0 if green == total else 1


if __name__ == "__main__":
    sys.exit(main())
