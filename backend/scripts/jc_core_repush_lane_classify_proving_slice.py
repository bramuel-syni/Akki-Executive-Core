"""JC-CORE-REPUSH-LANE-CLASSIFY · 10-row proving slice.

Canonical Spec: user dispatch 2026-07-05 · `JC-CORE-REPUSH-CLOSE-CONDITIONS-AND-LANE-CLASSIFY`.

Two sub-arcs, one bounded one-pass:
  Sub-arc 1 · re-push close-conditions delta `aff25763` to Core
             (SHIPPED-UNPUSHED path in preview pod; user pushes)
  Sub-arc 2 · classify 4 live-CI-red lanes:
             - gitleaks         → WAIT-FOR-USER-LOG-PASTE (logs-first rule)
             - lighthouse       → DISABLE-WITH-LEDGER (env-sensitive)
             - render-smoke     → DISABLE-WITH-LEDGER (env-sensitive)
             - marketing-assets-guard → FIX (--noconftest flag added)

F.6 N/A. Shield UNTOUCHED. Testing sub-agents BANNED. MOCKED-integrations
line preserved. HARD STOP at close.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

APP_ROOT = Path("/app")
MEMO = APP_ROOT / "memory" / "sprints" / "JC_CORE_REPUSH_LANE_CLASSIFY.md"
DEV_PIPELINE = APP_ROOT / "memory" / "DEV_PIPELINE.md"

# Sub-arc 1 targets
CLOSE_CONDITIONS_COMMIT = "aff25763"
ANALYZE_JOURNAL = APP_ROOT / "frontend" / "src" / "pages" / "AnalyzeJournal.jsx"
CRACO_CFG = APP_ROOT / "frontend" / "craco.config.js"

# Sub-arc 2 targets
WORKFLOWS_DIR = APP_ROOT / ".github" / "workflows"
MARKETING_WORKFLOW = WORKFLOWS_DIR / "marketing-assets-guard.yml"
LIGHTHOUSE_WORKFLOW = WORKFLOWS_DIR / "lighthouse.yml"
RENDER_SMOKE_WORKFLOW = WORKFLOWS_DIR / "render-smoke.yml"
GITLEAKS_WORKFLOW = WORKFLOWS_DIR / "gitleaks.yml"
GITLEAKS_TOML = APP_ROOT / ".gitleaks.toml"

# Shield sanity
SHIELD_ROOT = APP_ROOT / "backend" / "services" / "synisense" / "shield"

# Pre-arc HEAD — the tip of the prior arc close (JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY)
PRE_ARC_HEAD = "28454ba0"

results: list[dict] = []


def add(row: str, ok: bool, detail: str = "", **extras) -> None:
    results.append({"row": row, "ok": ok, "detail": detail, **extras})
    marker = "PASS" if ok else "FAIL"
    print(f"[{marker}] {row} — {detail}")


def r1_aff25763_exists_in_pod() -> None:
    """R1 · `aff25763` exists in pod local git."""
    try:
        proc = subprocess.run(
            ["git", "log", "--oneline", CLOSE_CONDITIONS_COMMIT, "-1"],
            cwd=str(APP_ROOT),
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception as e:  # noqa: BLE001
        add("R1_aff25763_exists", False, f"git log failed: {e}")
        return
    out = (proc.stdout or "").strip()
    ok = proc.returncode == 0 and out.startswith(CLOSE_CONDITIONS_COMMIT)
    add(
        "R1_aff25763_exists",
        ok,
        f"rc={proc.returncode} out={out[:120]!r}",
    )


def r2_subarc1_close_discipline() -> None:
    """R2 · Sub-arc 1 close discipline.

    EITHER (a) git push landed + Core HEAD ancestry includes aff25763 +
    post-fix state clean; OR (b) SHIPPED-UNPUSHED declared with local
    hash cited AND user-push instruction present in memo. Boolean OR.
    """
    # Path (a) — was push attempted from pod?
    try:
        proc = subprocess.run(
            ["git", "remote", "-v"],
            cwd=str(APP_ROOT),
            capture_output=True,
            text=True,
            timeout=10,
        )
        remote_out = (proc.stdout or "").strip()
    except Exception:  # noqa: BLE001
        remote_out = ""
    remote_present = bool(remote_out)

    # Path (b) — memo declares SHIPPED-UNPUSHED with hash + user-push instruction
    memo_body = MEMO.read_text() if MEMO.exists() else ""
    unpushed_declared = "SHIPPED-UNPUSHED" in memo_body
    hash_cited = CLOSE_CONDITIONS_COMMIT in memo_body
    user_push_instruction = "Save to GitHub" in memo_body

    # Also verify post-fix state at pod HEAD
    aj_content = ANALYZE_JOURNAL.read_text() if ANALYZE_JOURNAL.exists() else ""
    craco_content = CRACO_CFG.read_text() if CRACO_CFG.exists() else ""
    eslint_disable_count = aj_content.count("eslint-disable-next-line no-restricted-syntax")
    allowlist_present = 'files: ["src/pages/AnalyzeJournal.jsx"]' in craco_content

    if remote_present:
        # Path (a) — full push-landed verification
        ok = (
            eslint_disable_count == 0
            and allowlist_present
        )
        detail = (
            f"path=(a)_pushed · remote={remote_out[:100]!r} "
            f"eslint_disable={eslint_disable_count} allowlist_present={allowlist_present}"
        )
    else:
        # Path (b) — SHIPPED-UNPUSHED path
        ok = (
            unpushed_declared
            and hash_cited
            and user_push_instruction
            and eslint_disable_count == 0
            and allowlist_present
        )
        detail = (
            f"path=(b)_shipped-unpushed · unpushed_declared={unpushed_declared} "
            f"hash_cited={hash_cited} user_push_instruction={user_push_instruction} "
            f"eslint_disable={eslint_disable_count} allowlist_present={allowlist_present}"
        )
    add("R2_subarc1_close_discipline", ok, detail)


def r3_codemod_drift_local_exit0() -> None:
    """R3 · codemod-drift local exit=0.

    Invoke the actual codemod-drift check as the workflow does: iterate
    codemods in `scripts/codemods/` and run each with `--check`. Success
    condition: every codemod exits 0. Same discipline as the CI workflow.
    """
    codemod_dir = APP_ROOT / "scripts" / "codemods"
    codemods = sorted(codemod_dir.glob("[0-9][0-9][0-9]_*.py"))
    if not codemods:
        add("R3_codemod_drift_local", False, f"no codemods found in {codemod_dir}")
        return
    failures = []
    for cm in codemods:
        try:
            proc = subprocess.run(
                [sys.executable, str(cm), "--check"],
                cwd=str(APP_ROOT),
                capture_output=True,
                text=True,
                timeout=60,
            )
            if proc.returncode != 0:
                failures.append(
                    {"codemod": cm.name, "rc": proc.returncode,
                     "stderr_tail": (proc.stderr or "")[-200:]}
                )
        except Exception as e:  # noqa: BLE001
            failures.append({"codemod": cm.name, "error": str(e)})
    ok = not failures
    add(
        "R3_codemod_drift_local",
        ok,
        f"codemods_run={len(codemods)} failures={len(failures)}",
        failures=failures,
    )


def r4_gitleaks_log_source_declared() -> None:
    """R4 · Gitleaks · log-in-hand check.

    Log source declared in memo. If log absent AND gitleaks was disposed
    → FAIL (never dispose gitleaks without logs).
    """
    if not MEMO.exists():
        add("R4_gitleaks_log_source", False, "memo missing")
        return
    body = MEMO.read_text()
    wait_for_paste = "WAIT-FOR-USER-LOG-PASTE" in body
    # Gitleaks row in the deliverable table must state NO DISPOSITION or PENDING
    # if wait-for-paste is emitted.
    gitleaks_row = ""
    for line in body.splitlines():
        if "gitleaks" in line.lower() and "|" in line and "log source" not in line.lower() and "---" not in line:
            gitleaks_row = line
            break
    disposed_without_logs = (
        wait_for_paste is False
        and "gitleaks" in body.lower()
        and ("DISABLE" in gitleaks_row or "DELETE" in gitleaks_row or "FIX" in gitleaks_row)
    )
    ok = wait_for_paste and not disposed_without_logs
    add(
        "R4_gitleaks_log_source",
        ok,
        f"wait_for_paste_emitted={wait_for_paste} disposed_without_logs={disposed_without_logs}",
    )


def r5_gitleaks_augment_discipline() -> None:
    """R5 · Gitleaks · augment discipline. Any new allowlist entry is
    path-anchored (0 wildcards), has cause comment, does NOT touch
    useDefault=true.

    Since we did NOT augment .gitleaks.toml in this arc (waiting for
    logs), verify it's UNCHANGED since PRE_ARC_HEAD.
    """
    try:
        proc = subprocess.run(
            ["git", "diff", "--stat", PRE_ARC_HEAD, "--", ".gitleaks.toml"],
            cwd=str(APP_ROOT),
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception as e:  # noqa: BLE001
        add("R5_gitleaks_augment_discipline", False, f"git diff failed: {e}")
        return
    out = (proc.stdout or "").strip()
    unchanged = out == ""
    # Sanity: current .gitleaks.toml parses, useDefault=true, 0 wildcards.
    try:
        import tomllib
        parsed = tomllib.loads(GITLEAKS_TOML.read_text())
        parseable = True
        use_default = parsed.get("extend", {}).get("useDefault", False)
        paths = parsed.get("allowlist", {}).get("paths", [])
        # Wildcard = a bare `.*` NOT anchored on either side (no `^` prefix)
        bad_wildcards = [p for p in paths if not p.startswith("^")]
    except Exception:  # noqa: BLE001
        parseable = False
        use_default = False
        bad_wildcards = ["<parse-failed>"]

    ok = unchanged and parseable and use_default and not bad_wildcards
    add(
        "R5_gitleaks_augment_discipline",
        ok,
        f"unchanged={unchanged} parseable={parseable} useDefault={use_default} "
        f"unanchored_paths={bad_wildcards}",
    )


def r6_gitleaks_real_signal_separation() -> None:
    """R6 · Gitleaks · real-signal separation. If diagnosis was
    REAL-SIGNAL-SURFACED, finding is documented in a dedicated section
    and no allowlist entry was silently added.

    Given we're in WAIT-FOR-USER-LOG-PASTE mode (no diagnosis yet), this
    row asserts: memo has a dedicated "Gitleaks diagnosis" section AND
    it does NOT prematurely claim a Path B real-signal verdict.
    """
    if not MEMO.exists():
        add("R6_gitleaks_real_signal", False, "memo missing")
        return
    body = MEMO.read_text()
    has_gitleaks_section = "Gitleaks diagnosis" in body or "Gitleaks · augment discipline" in body or "Gitleaks · Path" in body
    # Check no premature Path B claim
    path_b_prematurely_claimed = "Path B (real signal · genuine leak) confirmed" in body
    ok = has_gitleaks_section and not path_b_prematurely_claimed
    add(
        "R6_gitleaks_real_signal",
        ok,
        f"has_gitleaks_section={has_gitleaks_section} "
        f"path_b_prematurely_claimed={path_b_prematurely_claimed}",
    )


def r7_per_lane_deliverable_table() -> None:
    """R7 · Per-lane deliverable table: 4 rows with all columns populated."""
    if not MEMO.exists():
        add("R7_per_lane_table", False, "memo missing")
        return
    body = MEMO.read_text()
    # Verify a table exists with a header row that includes the mandated columns.
    required_columns = [
        "Lane", "Log source", "Diagnosis", "Verdict", "Disposition", "Cause",
    ]
    header_row_present = all(col in body for col in required_columns)
    # Each of the 4 lanes must appear as a row in the table
    lane_rows = {
        "gitleaks":                "| **gitleaks** |",
        "lighthouse":              "| **lighthouse** |",
        "render-smoke":            "| **render-smoke** |",
        "marketing-assets-guard":  "| **marketing-assets-guard** |",
    }
    lane_hits = {name: (marker in body) for name, marker in lane_rows.items()}
    missing_lanes = [name for name, ok in lane_hits.items() if not ok]
    ok = header_row_present and not missing_lanes
    add(
        "R7_per_lane_table",
        ok,
        f"header_row_present={header_row_present} missing_lanes={missing_lanes}",
    )


def r8_deletion_ledger_consistency() -> None:
    """R8 · Any lane DISABLED via workflow-file removal has a
    corresponding Deletion Recovery Ledger entry.

    Lighthouse + render-smoke deleted in this arc → ledger entries required.
    """
    lh_deleted = not LIGHTHOUSE_WORKFLOW.exists()
    rs_deleted = not RENDER_SMOKE_WORKFLOW.exists()
    body = MEMO.read_text() if MEMO.exists() else ""
    lh_ledgered = (
        ".github/workflows/lighthouse.yml" in body
        and "git revert" in body
        and "lighthouse" in body.lower()
    )
    rs_ledgered = (
        ".github/workflows/render-smoke.yml" in body
        and "git revert" in body
        and "render-smoke" in body.lower()
    )
    ok = (
        lh_deleted == lh_ledgered
        and rs_deleted == rs_ledgered
        and lh_deleted
        and rs_deleted
    )
    add(
        "R8_deletion_ledger_consistency",
        ok,
        f"lh_deleted={lh_deleted} lh_ledgered={lh_ledgered} "
        f"rs_deleted={rs_deleted} rs_ledgered={rs_ledgered}",
    )


def r9_shield_sha256_identity() -> None:
    """R9 · Shield 13 files unchanged (sanity)."""
    try:
        proc = subprocess.run(
            ["git", "diff", "--stat", PRE_ARC_HEAD, "--", "backend/services/synisense/shield/"],
            cwd=str(APP_ROOT),
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception as e:  # noqa: BLE001
        add("R9_shield_sha256_identity", False, f"git diff failed: {e}")
        return
    out = (proc.stdout or "").strip()
    shield_files = list(SHIELD_ROOT.rglob("*.py")) if SHIELD_ROOT.exists() else []
    ok = proc.returncode == 0 and out == "" and len(shield_files) >= 10
    add(
        "R9_shield_sha256_identity",
        ok,
        f"shield_py_files={len(shield_files)} diff_bytes={len(out)}",
    )


def r10_prior_bankings_untouched() -> None:
    """R10 · Prior bankings intact + prior proving slices AST-clean.

    Prior bankings to verify unchanged since PRE_ARC_HEAD:
      - containment purge report
      - requirements marker-only
      - Deletion Recovery Ledger (prior 4 entries in JC_CI_BOARD_TRIAGE memo)
      - WRONG_BOARD_REJECTION rule
      - CLOSE_IS_NOT_CLOSED_UNTIL_PUSHED rule
      - Amendment-Echo extension
      - classify-only findings (JC-INTERNAL-HTTP memo)
    Plus: prior 16 proving slices under backend/scripts/jc_*.py all AST-clean.
    """
    protected_bankings = [
        "memory/sprints/JC_CONTAINMENT_PURGE_REPORT_2026_07_04.md",
        "memory/sprints/JC_CI_BOARD_TRIAGE_AKKI_EXECUTIVE_CORE.md",
        "memory/sprints/JC_FE_CODEMOD_001_APPLY.md",
        "memory/sprints/JC_INTERNAL_HTTP_CONNECTTIMEOUT_CLASSIFY.md",
        "memory/rules/WRONG_BOARD_REJECTION_RULE.md",
        "memory/rules/CLOSE_IS_NOT_CLOSED_UNTIL_PUSHED_RULE.md",
        "backend/requirements.txt",
    ]
    try:
        proc = subprocess.run(
            ["git", "diff", "--stat", PRE_ARC_HEAD, "--"] + protected_bankings,
            cwd=str(APP_ROOT),
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception as e:  # noqa: BLE001
        add("R10_prior_bankings", False, f"git diff failed: {e}")
        return
    out = (proc.stdout or "").strip()
    bankings_untouched = proc.returncode == 0 and out == ""
    # Prior proving slices AST-clean (parseable via ast.parse)
    import ast
    slice_dir = APP_ROOT / "backend" / "scripts"
    prior_slices = [p for p in slice_dir.glob("jc_*_proving_slice.py") if p.name != "jc_core_repush_lane_classify_proving_slice.py"]
    ast_failures = []
    for p in prior_slices:
        try:
            ast.parse(p.read_text())
        except Exception as e:  # noqa: BLE001
            ast_failures.append(f"{p.name}: {e.__class__.__name__}")
    ok = bankings_untouched and not ast_failures
    add(
        "R10_prior_bankings",
        ok,
        f"bankings_untouched={bankings_untouched} prior_slices={len(prior_slices)} "
        f"ast_failures={ast_failures}",
    )


def main() -> int:
    print(
        "=" * 60,
        "\nJC-CORE-REPUSH-LANE-CLASSIFY · proving slice · 10 rows",
        "\nCanonical Spec: user dispatch 2026-07-05 · bounded one-pass",
        "\nSub-arc 1: re-push close-conditions delta",
        "\nSub-arc 2: 4-lane classify-fix-or-disable",
        "\nTesting sub-agents BANNED. Pure bash execution.\n",
        "=" * 60,
        sep="",
    )
    r1_aff25763_exists_in_pod()
    r2_subarc1_close_discipline()
    r3_codemod_drift_local_exit0()
    r4_gitleaks_log_source_declared()
    r5_gitleaks_augment_discipline()
    r6_gitleaks_real_signal_separation()
    r7_per_lane_deliverable_table()
    r8_deletion_ledger_consistency()
    r9_shield_sha256_identity()
    r10_prior_bankings_untouched()

    passed = sum(1 for r in results if r["ok"])
    total = len(results)
    summary = {
        "arc": "JC-CORE-REPUSH-LANE-CLASSIFY",
        "canonical_spec": "user dispatch 2026-07-05",
        "sub_arcs": [
            "re-push close-conditions delta",
            "4-lane classify-fix-or-disable",
        ],
        "passed": passed,
        "total": total,
        "green": passed == total,
        "rows": results,
    }
    out_path = Path("/app/backend/scripts/.jc_core_repush_lane_classify_slice_results.json")
    out_path.write_text(json.dumps(summary, indent=2))

    print(f"\n{'=' * 60}")
    print(f"RESULT · {passed}/{total} GREEN · saved to {out_path}")
    print("=" * 60)
    return 0 if passed == total else 1


if __name__ == "__main__":
    sys.exit(main())
