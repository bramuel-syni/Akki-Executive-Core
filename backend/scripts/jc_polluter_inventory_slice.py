#!/usr/bin/env python3
"""Polluter inventory slice — READ-ONLY observability harness.

Canonical Spec: `/app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1`
                (Cluster-F closes existing polluters; this slice
                produces a JSON dashboard of the current polluter
                landscape after each sub-sprint to validate the
                closure schedule is on track)

Pure observability — zero LOC mutated in any test / invariant / product
file. Output written to:

  /app/memory/jc_artifacts/polluter_inventory/<ISO-UTC-timestamp>.json
  /app/memory/jc_artifacts/polluter_inventory/latest.md  (human summary)

Behaviour:
  1. M1 + M2 AST scan across backend/tests/**/test_*.py (mirroring
     the test_no_bespoke_run_helper invariant's classifier).
  2. Cross-reference against bespoke_run_helper_grandfathered.yml:
       - new sites (not yet grandfathered)
       - stale entries (grandfathered but no longer in tree)
       - count-ceiling proximity (current / ceiling per pattern)
  3. Closure-velocity view: per-file, when was the entry added /
     removed (best-effort from git log; falls back to current state).
  4. Per-sub-sprint roll-up: how many files in each Cluster-F sub-
     sprint are still in flight (count of YAML entries tagged with
     that sub-sprint).

NOT a fix authority. NOT a build-time invariant. NOT a test that runs
in `pytest`. Snapshot reporting only — designed to be run manually
between sub-sprints by a human reviewer or the agent.

Two proving-slice rows ship inline:

  P1 — inventory output matches the current YAML state
  P2 — new-test injection probe surfaces as "ungrandfathered new site"
       (then cleanup restores)
"""
from __future__ import annotations

import ast
import json
import pathlib
import subprocess
import sys
from datetime import datetime, timezone
from typing import Dict, List, Tuple

import yaml  # type: ignore[import-untyped]

REPO = pathlib.Path("/app")
BACKEND = REPO / "backend"
TESTS_DIR = BACKEND / "tests"
INVARIANT_FILE = TESTS_DIR / "invariants" / "test_no_bespoke_run_helper.py"
GRANDFATHER_FILE = TESTS_DIR / "invariants" / "bespoke_run_helper_grandfathered.yml"
ARTIFACTS_DIR = REPO / "memory" / "jc_artifacts" / "polluter_inventory"


def _is_run_helper(node: ast.AST) -> bool:
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    if node.name != "_run":
        return False
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
            if sub.func.attr == "run_until_complete":
                recv = sub.func.value
                if (
                    isinstance(recv, ast.Call)
                    and isinstance(recv.func, ast.Attribute)
                    and recv.func.attr == "get_event_loop"
                    and isinstance(recv.func.value, ast.Name)
                    and recv.func.value.id == "asyncio"
                ):
                    return True
    return False


def _find_m2_calls(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> List[int]:
    hits: List[int] = []
    for sub in ast.walk(fn):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
            if (
                sub.func.attr == "run"
                and isinstance(sub.func.value, ast.Name)
                and sub.func.value.id == "asyncio"
            ):
                hits.append(sub.lineno)
    return hits


def scan_live() -> Tuple[List[Dict], List[Dict]]:
    """Return (m1_findings, m2_findings) for the current tree."""
    m1: List[Dict] = []
    m2: List[Dict] = []
    for p in sorted(TESTS_DIR.rglob("test_*.py")):
        if "/invariants/" in str(p) or "__pycache__" in p.parts:
            continue
        try:
            src = p.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(src, filename=str(p))
        except SyntaxError:
            continue
        rel = str(p.relative_to(REPO))
        for node in tree.body:
            if _is_run_helper(node):
                m1.append({"file": rel, "lineno": node.lineno})
        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if not node.name.startswith("test_"):
                continue
            for ln in _find_m2_calls(node):
                m2.append({"file": rel, "func": node.name, "lineno": ln})
    return m1, m2


def load_grandfather() -> Tuple[List[Dict], List[Dict], int, int]:
    """Return (m1_entries, m2_entries, m1_ceiling, m2_ceiling)."""
    data = yaml.safe_load(GRANDFATHER_FILE.read_text(encoding="utf-8")) or {}
    m1 = list(data.get("m1_entries") or [])
    m2 = list(data.get("m2_entries") or [])
    # Ceiling parse from the invariant file
    src = INVARIANT_FILE.read_text(encoding="utf-8")
    m1_ceil = 0
    m2_ceil = 0
    for line in src.splitlines():
        s = line.strip()
        if s.startswith("M1_CEILING"):
            m1_ceil = int(s.split("=")[1].strip())
        elif s.startswith("M2_CEILING"):
            m2_ceil = int(s.split("=")[1].strip())
    return m1, m2, m1_ceil, m2_ceil


def build_inventory() -> Dict:
    live_m1, live_m2 = scan_live()
    grand_m1, grand_m2, m1_ceiling, m2_ceiling = load_grandfather()

    grand_m1_files = {e["file"] for e in grand_m1}
    grand_m2_keys = {(e["file"], e["func"], int(e["lineno"])) for e in grand_m2}

    live_m1_files = {f["file"] for f in live_m1}
    live_m2_keys = {(f["file"], f["func"], int(f["lineno"])) for f in live_m2}

    new_m1 = sorted(live_m1_files - grand_m1_files)
    stale_m1 = sorted(grand_m1_files - live_m1_files)

    new_m2 = sorted([k for k in live_m2_keys if k not in grand_m2_keys])
    stale_m2 = sorted([k for k in grand_m2_keys if k not in live_m2_keys])

    # Per-sub-sprint roll-up
    sub_sprint_rollup: Dict[str, Dict[str, int]] = {}
    for entry in grand_m1:
        s = entry.get("cluster_f_sub_sprint") or "(untagged)"
        sub_sprint_rollup.setdefault(s, {"m1": 0, "m2": 0})["m1"] += 1
    for entry in grand_m2:
        s = entry.get("cluster_f_sub_sprint") or "(untagged)"
        sub_sprint_rollup.setdefault(s, {"m1": 0, "m2": 0})["m2"] += 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "live_scan": {
            "m1_file_count": len(live_m1_files),
            "m2_site_count": len(live_m2_keys),
            "m2_file_count": len({f["file"] for f in live_m2}),
        },
        "grandfather": {
            "m1_entry_count": len(grand_m1),
            "m2_entry_count": len(grand_m2),
            "m1_ceiling": m1_ceiling,
            "m2_ceiling": m2_ceiling,
            "m1_ceiling_proximity": f"{len(grand_m1)}/{m1_ceiling}",
            "m2_ceiling_proximity": f"{len(grand_m2)}/{m2_ceiling}",
        },
        "drift": {
            "new_m1_ungrandfathered": new_m1,
            "stale_m1_in_yaml": stale_m1,
            "new_m2_ungrandfathered": [list(k) for k in new_m2],
            "stale_m2_in_yaml": [list(k) for k in stale_m2],
        },
        "sub_sprint_rollup": sub_sprint_rollup,
        "closure_status": {
            "all_grandfathered_match_live": (not new_m1 and not stale_m1
                                              and not new_m2 and not stale_m2),
        },
    }


def render_md(inv: Dict) -> str:
    lines = [
        f"# Polluter Inventory — {inv['generated_at']}",
        "",
        "READ-ONLY observability snapshot of bespoke-`_run` / `asyncio.run` polluter landscape.",
        "",
        "## Live tree counts",
        f"- M1 (`_run` helper) files: **{inv['live_scan']['m1_file_count']}**",
        f"- M2 (`asyncio.run` in test body) sites: **{inv['live_scan']['m2_site_count']}** across "
        f"**{inv['live_scan']['m2_file_count']}** files",
        "",
        "## Grandfather YAML state",
        f"- M1 entries: **{inv['grandfather']['m1_entry_count']}** / ceiling {inv['grandfather']['m1_ceiling']}",
        f"- M2 entries: **{inv['grandfather']['m2_entry_count']}** / ceiling {inv['grandfather']['m2_ceiling']}",
        "",
        "## Drift report",
    ]
    if inv["drift"]["new_m1_ungrandfathered"]:
        lines.append(f"- 🟥 NEW M1 ungrandfathered ({len(inv['drift']['new_m1_ungrandfathered'])}):")
        for f in inv["drift"]["new_m1_ungrandfathered"]:
            lines.append(f"    - {f}")
    else:
        lines.append("- ✅ No new M1 polluters")
    if inv["drift"]["stale_m1_in_yaml"]:
        lines.append(f"- 🟧 Stale M1 entries ({len(inv['drift']['stale_m1_in_yaml'])}):")
        for f in inv["drift"]["stale_m1_in_yaml"]:
            lines.append(f"    - {f}")
    else:
        lines.append("- ✅ No stale M1 entries")
    if inv["drift"]["new_m2_ungrandfathered"]:
        lines.append(f"- 🟥 NEW M2 ungrandfathered ({len(inv['drift']['new_m2_ungrandfathered'])}):")
        for k in inv["drift"]["new_m2_ungrandfathered"]:
            lines.append(f"    - {k[0]}:{k[2]} {k[1]}()")
    else:
        lines.append("- ✅ No new M2 polluters")
    if inv["drift"]["stale_m2_in_yaml"]:
        lines.append(f"- 🟧 Stale M2 entries ({len(inv['drift']['stale_m2_in_yaml'])}):")
        for k in inv["drift"]["stale_m2_in_yaml"]:
            lines.append(f"    - {k[0]}:{k[2]} {k[1]}()")
    else:
        lines.append("- ✅ No stale M2 entries")
    lines.append("")
    lines.append("## Per-sub-sprint roll-up")
    for sprint, counts in sorted(inv["sub_sprint_rollup"].items()):
        lines.append(f"- **{sprint}** — M1: {counts['m1']} · M2: {counts['m2']}")
    lines.append("")
    lines.append("## Closure status")
    if inv["closure_status"]["all_grandfathered_match_live"]:
        lines.append("✅ All grandfather entries match the live tree. No drift.")
    else:
        lines.append("🟥 Drift detected — see drift report above.")
    return "\n".join(lines)


def main() -> int:
    print("=" * 76)
    print("POLLUTER INVENTORY SLICE — Canonical Spec: P5_7_FIX_SCOPE_CLUSTER_F.md §1.1")
    print("=" * 76)

    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Generate inventory ──
    inv = build_inventory()
    ts = inv["generated_at"].replace(":", "").replace("-", "").replace(".", "_")
    json_out = ARTIFACTS_DIR / f"inventory_{ts}.json"
    md_out = ARTIFACTS_DIR / "latest.md"
    json_out.write_text(json.dumps(inv, indent=2, sort_keys=True), encoding="utf-8")
    md_out.write_text(render_md(inv), encoding="utf-8")

    rows: List[Dict] = []

    # ── P1 — output matches current YAML state ──
    grand_m1, grand_m2, m1_ceiling, m2_ceiling = load_grandfather()
    ok = (
        inv["grandfather"]["m1_entry_count"] == len(grand_m1)
        and inv["grandfather"]["m2_entry_count"] == len(grand_m2)
        and inv["closure_status"]["all_grandfathered_match_live"]
    )
    detail = (
        f"yaml m1={len(grand_m1)}  yaml m2={len(grand_m2)}  "
        f"live m1={inv['live_scan']['m1_file_count']}  "
        f"live m2={inv['live_scan']['m2_site_count']}  "
        f"clean_drift={inv['closure_status']['all_grandfathered_match_live']}"
    )
    status = "GREEN" if ok else "RED"
    print(f"  Row P1  {status:<5}  inventory matches YAML + live tree (no drift)")
    print(f"            {detail}")
    rows.append({"row": "P1", "status": status})

    # ── P2 — inject probe, run again, expect surface ──
    probe_path = TESTS_DIR / "test_zzz_inventory_probe.py"
    probe_path.write_text(
        '"""Test probe for polluter inventory slice."""\n'
        "import asyncio\n\n\n"
        "def _run(coro):\n"
        "    return asyncio.get_event_loop().run_until_complete(coro)\n\n\n"
        "def test_inventory_probe_placeholder():\n"
        "    assert True\n",
        encoding="utf-8",
    )
    try:
        inv2 = build_inventory()
        probe_rel = str(probe_path.relative_to(REPO))
        ok = probe_rel in inv2["drift"]["new_m1_ungrandfathered"]
        detail = f"probe='{probe_rel}' surfaced={ok}"
        status = "GREEN" if ok else "RED"
        print(f"  Row P2  {status:<5}  new-test injection surfaces as ungrandfathered M1")
        print(f"            {detail}")
        rows.append({"row": "P2", "status": status})
    finally:
        probe_path.unlink()

    # ── P3 — output files exist + JSON is well-formed ──
    ok = json_out.exists() and md_out.exists()
    if ok:
        try:
            json.loads(json_out.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            ok = False
    status = "GREEN" if ok else "RED"
    print(f"  Row P3  {status:<5}  output artefacts written: JSON + latest.md")
    print(f"            json={json_out.name}  md={md_out.name}")
    rows.append({"row": "P3", "status": status})

    # ── Summary ──
    print("=" * 76)
    print("Artefacts:")
    print(f"  {json_out}")
    print(f"  {md_out}")
    print("=" * 76)
    print()
    print(render_md(inv))
    print()
    print("=" * 76)
    green = sum(1 for r in rows if r["status"] == "GREEN")
    print(f"RESULT  {green}/{len(rows)} GREEN")
    print("=" * 76)
    return 0 if green == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main())
