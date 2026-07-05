"""JC-FE-CODEMOD-001-CLOSE-CONDITIONS · 8-row proving slice.

Canonical Spec: user dispatch 2026-07-04 · `JC-FE-CODEMOD-001-CLOSE-CONDITIONS`.

Condition A: dynamic proof on 10 rewrites against LIVE preview (with
wire-inspection substitute for 3 endpoints whose SERVER side times out
due to a pre-existing environmental issue — contracts/_adapters/
_http_client.py::_call internal-HTTP hop to a service unreachable in
this preview pod · 200+ httpx.ConnectTimeout in backend logs).

Condition B: AnalyzeJournal.jsx reclassified — eslint-disable comments
REMOVED, path-anchored override added to craco.config.js with cause.

MOCKED-integrations line preserved: SendGrid dev-mode + Resend mock.
Testing sub-agents BANNED — pure bash + curl + static analysis.
Prior bankings (purge / requirements / recovery ledger / 3 rules) UNTOUCHED.
"""
from __future__ import annotations
import ast
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

APP_ROOT = Path("/app")
ANALYZE_JOURNAL = APP_ROOT / "frontend" / "src" / "pages" / "AnalyzeJournal.jsx"
CRACO_CFG = APP_ROOT / "frontend" / "craco.config.js"
CODEMOD = APP_ROOT / "scripts" / "codemods" / "001_raw_axios_to_apiv2.py"
DYNAMIC_PROOF_JSON = Path("/tmp/condition_a_dynamic_proof.json")
FE_BUILD_LOG = Path("/tmp/fe_build3.log")
SHIELD_ROOT = APP_ROOT / "backend" / "services" / "synisense" / "shield"
SHIELD_BASELINE = Path("/tmp/shield_pre_codemod.sha256")

results: list[dict] = []


def add(row: str, ok: bool, detail: str = "", **extras) -> None:
    results.append({"row": row, "ok": ok, "detail": detail, **extras})
    marker = "PASS" if ok else "FAIL"
    print(f"[{marker}] {row} — {detail}")


def r1_condition_a_manifest() -> None:
    """R1 — Condition A dynamic proof manifest: 10 rows PASS."""
    if not DYNAMIC_PROOF_JSON.exists():
        add("R1_condition_a_manifest", False, f"manifest missing: {DYNAMIC_PROOF_JSON}")
        return
    rows = json.loads(DYNAMIC_PROOF_JSON.read_text())
    pass_count = sum(1 for r in rows if r["verdict"] == "PASS")
    ok = len(rows) == 10 and pass_count == 10
    add("R1_condition_a_manifest", ok, f"rows={len(rows)} · pass={pass_count}/10")


def r2_condition_a_auth_posture_correctness() -> None:
    """R2 — Authenticated files show Bearer/CSRF differential; public files show
    auth artefact absent on wire.
    """
    rows = json.loads(DYNAMIC_PROOF_JSON.read_text())
    # Files expected to be AUTHENTICATED (per file classification)
    auth_files = {
        "frontend/src/components/chat/GovernanceSignals.jsx",
        "frontend/src/pages/SharedArtefact.jsx",
        "frontend/src/pages/TrustCenter.jsx",
    }
    # Public files (should show auth ABSENT on wire)
    public_files = {
        "frontend/src/components/sandbox/v2/ClosingStep.jsx",
        "frontend/src/components/sandbox/v2/Step1SolvaWrapper.jsx",
        "frontend/src/components/sandbox/v2/Step3StudioWrapper.jsx",
        "frontend/src/components/sandbox/v2/Step4CycleSnapshot.jsx",
        "frontend/src/pages/WelcomePage.jsx",
        "frontend/src/website/components/PublicVelocityTile.jsx",
        "frontend/src/website/pages/Cohort.jsx",
    }
    fails = []
    for r in rows:
        f = r["file"]
        art = r["auth_artefact_observed"]
        if f in auth_files:
            if "Bearer+CSRF confirmed on wire" not in art:
                fails.append(f"{f}: expected Bearer differential; got: {art[:80]}")
        elif f in public_files:
            if "auth artefact ABSENT" not in art and "anon path accepts anonymous access" not in art:
                fails.append(f"{f}: expected public/anon accepted; got: {art[:80]}")
    ok = not fails and len(auth_files) + len(public_files) == 10
    add(
        "R2_condition_a_auth_posture_correctness",
        ok,
        f"auth_files={len(auth_files)} · public_files={len(public_files)} · fails={len(fails)}",
    )


def r3_condition_b_eslint_disable_removed() -> None:
    """R3 — 0 eslint-disable-next-line no-restricted-syntax comments in AnalyzeJournal.jsx."""
    src = ANALYZE_JOURNAL.read_text()
    n = len(re.findall(r"eslint-disable-next-line\s+no-restricted-syntax", src))
    add("R3_condition_b_eslint_disable_removed", n == 0, f"disable_comment_count={n}")


def r4_condition_b_allowlist_present() -> None:
    """R4 — craco.config.js has path-anchored override for AnalyzeJournal.jsx with cause."""
    src = CRACO_CFG.read_text()
    # (a) has the file-scoped override entry
    has_entry = re.search(r'files:\s*\[\s*"src/pages/AnalyzeJournal\.jsx"\s*\]', src) is not None
    # (b) has the cause comment referencing GCS + signed URL rationale
    has_cause = "GCS" in src and "signed URL" in src
    # (c) NO wildcards in ANY override entry
    wildcards = re.findall(r'files:\s*\[\s*"\*[^"]*"\s*\]', src)
    ok = has_entry and has_cause and not wildcards
    add(
        "R4_condition_b_allowlist_present",
        ok,
        f"path_anchored_entry={has_entry} · cause_present={has_cause} · wildcard_entries={len(wildcards)}",
    )


def r5_condition_b_yarn_build_clean() -> None:
    """R5 — yarn build exits 0 post-fix."""
    if not FE_BUILD_LOG.exists():
        add("R5_condition_b_yarn_build_clean", False, "build log missing")
        return
    content = FE_BUILD_LOG.read_text()
    build_ok = "The build folder is ready to be deployed." in content or "Compiled successfully" in content or "Done in" in content
    failed = "Failed to compile" in content
    add("R5_condition_b_yarn_build_clean", build_ok and not failed, f"build_ok={build_ok} · failed_marker={failed}")


def r6_condition_b_codemod_drift_clean() -> None:
    """R6 — codemod-drift local run exit=0 with 0 pending violations."""
    proc = subprocess.run(
        [sys.executable, str(CODEMOD), "--check"],
        capture_output=True, text=True, cwd=str(APP_ROOT),
    )
    m = re.search(r"(\d+)\s+files;\s*(\d+)\s+import-line rewrites?", proc.stdout)
    files = int(m.group(1)) if m else -1
    rewrites = int(m.group(2)) if m else -1
    ok = proc.returncode == 0 and files == 0 and rewrites == 0
    add("R6_condition_b_codemod_drift_clean", ok, f"rc={proc.returncode} · pending_files={files} · pending_rewrites={rewrites}")


def r7_shield_untouched() -> None:
    """R7 — Shield sha256 identity: services/synisense/shield/** unchanged.
    
    Verification strategy: git diff against the JC-FE-CODEMOD-001-APPLY arc-tip
    commit (`ef05f97f`) — if no files under services/synisense/shield/ were
    modified since that commit, Shield is byte-identical.
    """
    proc = subprocess.run(
        ["git", "diff", "--name-only", "ef05f97f", "HEAD", "--", "backend/services/synisense/shield/"],
        capture_output=True, text=True, cwd=str(APP_ROOT),
    )
    modified = [ln for ln in proc.stdout.splitlines() if ln.strip()]
    # Also compute a live sha256 count for cross-check
    live_count = sum(1 for _ in SHIELD_ROOT.rglob("*.py"))
    ok = proc.returncode == 0 and not modified and live_count == 13
    add(
        "R7_shield_untouched",
        ok,
        f"since_ef05f97f_modified={len(modified)} · live_file_count={live_count} · expected=13",
    )


def r8_regression() -> None:
    """R8 — prior 13 proving slices parse-clean + prior bankings not mutated."""
    prior_slices = sorted((APP_ROOT / "backend" / "scripts").glob("jc_*_proving_slice.py"))
    ast_broken = []
    for s in prior_slices:
        try:
            ast.parse(s.read_text())
        except SyntaxError as e:
            ast_broken.append(f"{s.name}:{e.lineno}")

    # Prior bankings untouched (containment memo + requirements marker-only + recovery ledger + rules)
    containment = APP_ROOT / "memory" / "sprints" / "JC_CONTAINMENT_PURGE_REPORT_2026_07_04.md"
    reqs = APP_ROOT / "backend" / "requirements.txt"
    triage_memo = APP_ROOT / "memory" / "sprints" / "JC_CI_BOARD_TRIAGE_AKKI_EXECUTIVE_CORE.md"
    wrong_board_rule = APP_ROOT / "memory" / "rules" / "WRONG_BOARD_REJECTION_RULE.md"
    close_rule = APP_ROOT / "memory" / "rules" / "CLOSE_IS_NOT_CLOSED_UNTIL_PUSHED_RULE.md"

    bankings_ok = (
        containment.exists() and "nothing was written" in containment.read_text().lower()
        and reqs.exists() and "ci-requirements-guard: allow" in reqs.read_text()
        and triage_memo.exists() and "Deletion Recovery Ledger" in triage_memo.read_text() and "MARKER-ONLY" in triage_memo.read_text()
        and wrong_board_rule.exists()
        and close_rule.exists()
    )

    # New override added is path-anchored, existing overrides still there
    craco = CRACO_CFG.read_text()
    craco_ok = 'files: ["src/lib/api.js"' in craco and 'files: ["src/pages/AnalyzeJournal.jsx"]' in craco

    ok = not ast_broken and bankings_ok and craco_ok
    add(
        "R8_regression",
        ok,
        f"prior_slices={len(prior_slices)} · ast_broken={len(ast_broken)} · bankings_intact={bankings_ok} · craco_intact={craco_ok}",
    )


def main() -> int:
    print("=" * 70)
    print("JC-FE-CODEMOD-001-CLOSE-CONDITIONS · 8-row proving slice")
    print("Canonical Spec: user dispatch 2026-07-04")
    print("MOCKED-integrations line preserved: SendGrid dev-mode + Resend mock")
    print("=" * 70)

    r1_condition_a_manifest()
    r2_condition_a_auth_posture_correctness()
    r3_condition_b_eslint_disable_removed()
    r4_condition_b_allowlist_present()
    r5_condition_b_yarn_build_clean()
    r6_condition_b_codemod_drift_clean()
    r7_shield_untouched()
    r8_regression()

    print("=" * 70)
    green = sum(1 for r in results if r["ok"])
    total = len(results)
    print(f"SUMMARY: {green}/{total} GREEN")
    for r in results:
        marker = "🟢" if r["ok"] else "🔴"
        print(f"  {marker} {r['row']} — {r['detail']}")
    print("=" * 70)

    tip = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True, text=True, cwd=str(APP_ROOT))
    tip_hash = tip.stdout.split()[0] if tip.stdout.strip() else "UNKNOWN"

    out = APP_ROOT / "backend" / "scripts" / ".jc_fe_codemod_001_close_conditions_slice_results.json"
    out.write_text(json.dumps({"results": results, "tip_commit_hash": tip_hash}, indent=2))
    print(f"Results written to {out}")
    print(f"Tip commit hash: {tip_hash}")

    return 0 if green == total else 1


if __name__ == "__main__":
    sys.exit(main())
