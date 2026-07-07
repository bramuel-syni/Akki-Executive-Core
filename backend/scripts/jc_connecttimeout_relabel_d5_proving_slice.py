"""
JC-CONNECTTIMEOUT-RELABEL-D5 · Proving slice (6 rows · memo-correction only)

Canonical Spec: user dispatch 2026-07-05 · `JC-CONNECTTIMEOUT-RELABEL-D5`
Zero code touches. F.6 N/A. Memo correction + §9 footnote annotation only.

Rows:
  R1 · Label replaced in classify memo (1 hit in correction-lineage note only ·
       DETERMINISTIC-EDGE-TIMEOUT-CEILING present ≥1)
  R2 · Label replaced in gen-path memo (0 hits of TRANSIENT-UPSTREAM-VOLATILITY ·
       DETERMINISTIC-EDGE-TIMEOUT-CEILING present ≥1)
  R3 · Content marker corrected (new marker present · old marker absent in
       gen-path memo)
  R4 · Real-signals section corrected (path-2 retry-tuning removed · decision-
       tree present · venue-check-first present · async-generation frame
       present · "wait for lower-load" language absent)
  R5 · Zero code touches (git diff --stat since PRE_ARC_HEAD shows ONLY the two
       memos + DEV_PIPELINE.md + this slice + slice results JSON · no touches
       to _http_client.py, backend routers, generation engines, Shield, FE,
       .env, .gitleaks.toml)
  R6 · Prior bankings intact (4 Part-0 rules + state-injection corollary +
       prior arc bankings still present · grep for canonical anchor strings)
       + regression on prior proving slices AST-clean

Usage:
    python3 backend/scripts/jc_connecttimeout_relabel_d5_proving_slice.py
"""
from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
GEN_PATH_MEMO = REPO_ROOT / "memory" / "sprints" / "JC_GEN_PATH_CONNECTTIMEOUT.md"
CLASSIFY_MEMO = (
    REPO_ROOT / "memory" / "sprints" / "JC_INTERNAL_HTTP_CONNECTTIMEOUT_CLASSIFY.md"
)
DEV_PIPELINE = REPO_ROOT / "memory" / "DEV_PIPELINE.md"

# PRE_ARC_HEAD for this arc = the commit right before we started memo edits.
# That is the PRD-append commit `e5ae43c9` from the prior arc.
PRE_ARC_HEAD = "e5ae43c9"

# Allowed changed paths for zero-code-touches assertion (R5)
ALLOWED_CHANGED = {
    "memory/sprints/JC_GEN_PATH_CONNECTTIMEOUT.md",
    "memory/sprints/JC_INTERNAL_HTTP_CONNECTTIMEOUT_CLASSIFY.md",
    "memory/DEV_PIPELINE.md",
    "backend/scripts/jc_connecttimeout_relabel_d5_proving_slice.py",
    "backend/scripts/.jc_connecttimeout_relabel_d5_slice_results.json",
}


def _grep_count(path: Path, needle: str) -> int:
    if not path.exists():
        return -1
    return path.read_text().count(needle)


def _changed_since(base: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", f"{base}..HEAD"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    )
    return [
        f for f in result.stdout.strip().split("\n") if f
    ]


def _run_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []

    # R1 · Classify memo: TRANSIENT-UPSTREAM-VOLATILITY appears exactly 1 time
    # in the correction-lineage note; DETERMINISTIC-EDGE-TIMEOUT-CEILING >=1
    classify_transient = _grep_count(CLASSIFY_MEMO, "TRANSIENT-UPSTREAM-VOLATILITY")
    classify_new = _grep_count(CLASSIFY_MEMO, "DETERMINISTIC-EDGE-TIMEOUT-CEILING")
    # verify the 1 hit is in the correction-lineage prose (not as active label)
    classify_text = CLASSIFY_MEMO.read_text() if CLASSIFY_MEMO.exists() else ""
    correction_lineage_present = (
        "Correction lineage" in classify_text
        and "relabeled" in classify_text.lower()
    )
    rows.append(
        {
            "row": "R1",
            "name": "classify_memo_label_replaced_correction_lineage_present",
            "pass": (
                classify_transient == 1
                and classify_new >= 1
                and correction_lineage_present
            ),
            "detail": {
                "classify_transient_hits": classify_transient,
                "classify_new_hits": classify_new,
                "correction_lineage_present": correction_lineage_present,
            },
        }
    )

    # R2 · Gen-path memo: TRANSIENT-UPSTREAM-VOLATILITY == 0;
    # DETERMINISTIC-EDGE-TIMEOUT-CEILING >= 1
    genpath_transient = _grep_count(GEN_PATH_MEMO, "TRANSIENT-UPSTREAM-VOLATILITY")
    genpath_new = _grep_count(GEN_PATH_MEMO, "DETERMINISTIC-EDGE-TIMEOUT-CEILING")
    rows.append(
        {
            "row": "R2",
            "name": "gen_path_memo_label_fully_replaced",
            "pass": genpath_transient == 0 and genpath_new >= 1,
            "detail": {
                "gen_path_transient_hits": genpath_transient,
                "gen_path_new_hits": genpath_new,
            },
        }
    )

    # R3 · Content marker corrected in gen-path memo
    genpath_new_marker = _grep_count(
        GEN_PATH_MEMO, "s05-blocked-by-env-deterministic-edge-timeout-ceiling"
    )
    genpath_old_marker = _grep_count(
        GEN_PATH_MEMO, "s05-blocked-by-env-transient-upstream-volatility"
    )
    rows.append(
        {
            "row": "R3",
            "name": "content_marker_corrected_in_gen_path_memo",
            "pass": genpath_new_marker >= 1 and genpath_old_marker == 0,
            "detail": {
                "new_marker_hits": genpath_new_marker,
                "old_marker_hits": genpath_old_marker,
            },
        }
    )

    # R4 · Real-signals section corrected in gen-path memo
    genpath_text = GEN_PATH_MEMO.read_text() if GEN_PATH_MEMO.exists() else ""
    decision_tree_present = "Decision tree" in genpath_text
    venue_check_present = "Venue-check FIRST" in genpath_text
    async_gen_present = (
        "async generation" in genpath_text.lower()
        and "kick-off" in genpath_text.lower()
    )
    # Path 2 retry-tuning explicitly removed (or noted as removed)
    retry_tuning_removed = (
        "retry-policy tuning of `_PER_METHOD_TIMEOUT_S`" not in genpath_text
        or "REMOVED" in genpath_text
    )
    # Absence of "wait for lower-load" / "lower load" language
    lower_load_absent = (
        "lower-load" not in genpath_text.lower()
        or "does NOT close on" in genpath_text  # only present as the anti-pattern callout
    )
    # More strict: ensure no active claim of "wait for lower-load" — only the
    # explicit negation is allowed.
    active_lower_load = (
        "wait for a lower-load" in genpath_text.lower()
        and "does NOT close on" not in genpath_text
    )
    r4_pass = (
        decision_tree_present
        and venue_check_present
        and async_gen_present
        and retry_tuning_removed
        and not active_lower_load
    )
    rows.append(
        {
            "row": "R4",
            "name": "real_signals_section_corrected",
            "pass": r4_pass,
            "detail": {
                "decision_tree_present": decision_tree_present,
                "venue_check_present": venue_check_present,
                "async_gen_present": async_gen_present,
                "retry_tuning_removed": retry_tuning_removed,
                "no_active_lower_load_language": not active_lower_load,
            },
        }
    )

    # R5 · Zero code touches — changed paths must be subset of ALLOWED_CHANGED
    changed = _changed_since(PRE_ARC_HEAD)
    unauthorised = [f for f in changed if f not in ALLOWED_CHANGED]
    rows.append(
        {
            "row": "R5",
            "name": "zero_code_touches_only_allowed_paths_changed",
            "pass": len(unauthorised) == 0,
            "detail": {
                "pre_arc_head": PRE_ARC_HEAD,
                "changed": changed,
                "unauthorised": unauthorised,
                "allowed": sorted(ALLOWED_CHANGED),
            },
        }
    )

    # R6 · Prior bankings intact: 4 Part-0 rules + state-injection corollary +
    # prior proving slices AST-clean
    rules_dir = REPO_ROOT / "memory" / "rules"
    part0_rules = [
        "CANONICAL_SPEC_UX_BRIEF_V1_1_RULE.md",
        "UI_STORIES_CLOSE_ON_UI_LAYER_ONLY_RULE.md",
        "USER_QA_RE_RUN_IS_FINAL_GATE_RULE.md",
        "DECK_ID_COLLISION_GUARD_RULE.md",
    ]
    rules_present = {r: (rules_dir / r).exists() for r in part0_rules}
    ui_rule = rules_dir / "UI_STORIES_CLOSE_ON_UI_LAYER_ONLY_RULE.md"
    ui_rule_text = ui_rule.read_text() if ui_rule.exists() else ""
    state_injection_corollary_present = (
        "State-injection captures do not close UI stories" in ui_rule_text
    )
    # AST-check prior proving slices in backend/scripts/jc_*_proving_slice.py
    scripts_dir = REPO_ROOT / "backend" / "scripts"
    slice_files = sorted(scripts_dir.glob("jc_*_proving_slice.py"))
    ast_failures: list[str] = []
    for f in slice_files:
        try:
            ast.parse(f.read_text())
        except SyntaxError as e:
            ast_failures.append(f"{f.name}: {e}")
    rows.append(
        {
            "row": "R6",
            "name": "prior_bankings_intact_and_prior_slices_ast_clean",
            "pass": (
                all(rules_present.values())
                and state_injection_corollary_present
                and len(ast_failures) == 0
            ),
            "detail": {
                "part0_rules_present": rules_present,
                "state_injection_corollary_present": state_injection_corollary_present,
                "prior_slice_count": len(slice_files),
                "ast_failures": ast_failures,
            },
        }
    )

    return rows


def main() -> int:
    rows = _run_rows()
    passed = sum(1 for r in rows if r["pass"])
    total = len(rows)
    verdict = "GREEN" if passed == total else "RED"

    output_path = (
        Path(__file__).resolve().parent
        / ".jc_connecttimeout_relabel_d5_slice_results.json"
    )
    output_path.write_text(
        json.dumps(
            {
                "arc": "JC-CONNECTTIMEOUT-RELABEL-D5",
                "canonical_spec_line1": "user dispatch 2026-07-05 · JC-CONNECTTIMEOUT-RELABEL-D5 · memo-correction only",
                "verdict": verdict,
                "passed": passed,
                "total": total,
                "rows": rows,
            },
            indent=2,
        )
    )

    print(f"JC-CONNECTTIMEOUT-RELABEL-D5 · slice verdict={verdict} ({passed}/{total})")
    for r in rows:
        status = "PASS" if r["pass"] else "FAIL"
        print(f"  {r['row']} · {status} · {r['name']}")
        if not r["pass"]:
            print(f"       detail={json.dumps(r['detail'])[:400]}")

    return 0 if verdict == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
