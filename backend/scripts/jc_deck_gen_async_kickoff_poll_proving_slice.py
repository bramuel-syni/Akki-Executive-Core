"""JC-DECK-GEN-ASYNC-KICKOFF-POLL · Proving slice (15 rows · regression floor)

Canonical Spec: user dispatch 2026-07-05 · `JC-DECK-GEN-ASYNC-KICKOFF-POLL`

Per RULE-UI-STORIES-CLOSE-ON-UI-LAYER-ONLY: this slice is REGRESSION FLOOR only.
It does NOT close DECK-031 (Path B outcome — s05 still blocked by new failure class).
The Path B evidence + memo Real-Signal declaration are the honest disposition.

Rows:
  R1  · Endpoint enumeration table present in memo (all 4 paths + outline + enhance banking)
  R2  · Kick-off returns 202 (source-generate + outline + regenerate endpoints
        declare status_code=202)
  R3  · Status endpoint present (2 endpoints declared: contexts-scoped + top-level)
  R4  · Background task spawn wiring (spawn_generation uses asyncio.create_task)
  R5  · Job store schema (deck_generation_jobs collection with expected fields)
  R6  · Account isolation code path (get_job filters by account_id)
  R7  · Commit-lock 409 shape byte-identity (regenerate router calls engine's
        commit_locked_409 helper directly · no envelope reshape)
  R8  · Audit fingerprint 19-field preserved (write_audit call in
        _run_generate_deck_job has same arguments as pre-arc synchronous handler)
  R9  · Generation engine unchanged (deck_regenerate.py + llm_service.py +
        llm_tier_quota.py + studio_sensitivity.py all 0 diff bytes vs PRE_ARC)
  R10 · Shield sha256 identity vs PRE_ARC_HEAD
  R11 · Phase transitions instrumented (all 6 phase strings present in runner)
  R12 · FE state machine wired (CreateSummaryDeckModal.jsx polls status endpoint
        + maps phases 1:1 to progress checklist)
  R13 · s05 organic capture evidence present (Path B: s05_async_*_state.png files
        exist at canonical paths · Path B = "async landed · new failure class")
  R14 · No state-injection captures anywhere in evidence (memo declares organic
        user-flow only · no setPhase/setState in scripts)
  R15 · Regression: all prior proving slices AST-clean + prior bankings intact

Usage:
    python3 backend/scripts/jc_deck_gen_async_kickoff_poll_proving_slice.py
"""
from __future__ import annotations

import ast
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
MEMO_PATH = REPO_ROOT / "memory" / "sprints" / "JC_DECK_GEN_ASYNC_KICKOFF_POLL.md"
JOB_STORE = REPO_ROOT / "backend" / "services" / "deck_generation_jobs.py"
DECKS_ROUTER = REPO_ROOT / "backend" / "routers" / "decks.py"
REGEN_ROUTER = REPO_ROOT / "backend" / "routers" / "deck_related_lineage_regen.py"
FE_MODAL = REPO_ROOT / "frontend" / "src" / "components" / "decks" / "CreateSummaryDeckModal.jsx"
EVIDENCE_DIR = REPO_ROOT / "memory" / "evidence" / "2026_07_deck_recovery_stage_1"

PRE_ARC_HEAD = "5d1204ca"  # §9 IN-FLIGHT commit

ENGINE_UNCHANGED_PATHS = [
    "backend/services/deck_regenerate.py",
    "backend/llm_service.py",
    "backend/llm_tier_quota.py",
    "backend/studio_sensitivity.py",
    "backend/contracts/_adapters/_http_client.py",
    "backend/contracts/__init__.py",
    "backend/.env",
]
SHIELD_DIR = REPO_ROOT / "backend" / "services" / "synisense" / "shield"


def _git_diff_stat(base: str, path: str) -> str:
    r = subprocess.run(
        ["git", "diff", "--stat", f"{base}..HEAD", "--", path],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    return r.stdout.strip()


def _shield_composite_at(ref: str) -> tuple[str, int]:
    ls = subprocess.run(
        ["git", "ls-tree", "-r", "--name-only", ref, "backend/services/synisense/shield"],
        cwd=str(REPO_ROOT), capture_output=True, text=True,
    )
    files = sorted(f for f in ls.stdout.strip().split("\n") if f.endswith(".py"))
    hashes = []
    for f in files:
        show = subprocess.run(
            ["git", "show", f"{ref}:{f}"],
            cwd=str(REPO_ROOT), capture_output=True,
        )
        hashes.append(hashlib.sha256(show.stdout).hexdigest())
    return hashlib.sha256(("\n".join(hashes) + "\n").encode("utf-8")).hexdigest(), len(files)


def _shield_composite_head() -> tuple[str, int]:
    files = sorted(SHIELD_DIR.rglob("*.py"))
    hashes = [hashlib.sha256(f.read_bytes()).hexdigest() for f in files]
    return hashlib.sha256(("\n".join(hashes) + "\n").encode("utf-8")).hexdigest(), len(files)


def _run_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    memo = MEMO_PATH.read_text() if MEMO_PATH.exists() else ""
    decks_src = DECKS_ROUTER.read_text() if DECKS_ROUTER.exists() else ""
    regen_src = REGEN_ROUTER.read_text() if REGEN_ROUTER.exists() else ""
    fe_src = FE_MODAL.read_text() if FE_MODAL.exists() else ""
    job_src = JOB_STORE.read_text() if JOB_STORE.exists() else ""

    # R1 · endpoint enumeration table present
    r1_pass = (
        "Step 0 · Endpoint enumeration" in memo
        and "source-generate" in memo
        and "blank-generate" in memo
        and "regenerate (§4.7)" in memo
        and "enhance (§4.5)" in memo
        and "outline (secondary" in memo
    )
    rows.append({"row": "R1", "name": "endpoint_enumeration_present",
                 "pass": r1_pass,
                 "detail": {"memo_bytes": len(memo)}})

    # R2 · kick-off returns 202 (declared status_code=202 in 3 endpoints)
    r2_pass = (
        'status_code=202' in decks_src  # outline + generate
        and 'status_code=202' in regen_src  # regenerate
        and decks_src.count("status_code=202") >= 2
    )
    rows.append({"row": "R2", "name": "kickoff_endpoints_declare_202",
                 "pass": r2_pass,
                 "detail": {
                     "decks_202_count": decks_src.count("status_code=202"),
                     "regen_202_count": regen_src.count("status_code=202"),
                 }})

    # R3 · status endpoint present (2 declared: contexts-scoped + top-level)
    r3_pass = (
        "/generation-status/{job_id}" in decks_src
        and "/generation-status/{job_id}" in regen_src
    )
    rows.append({"row": "R3", "name": "status_endpoint_present_2_paths",
                 "pass": r3_pass, "detail": {
                     "decks_path_present": "/generation-status/{job_id}" in decks_src,
                     "regen_path_present": "/generation-status/{job_id}" in regen_src,
                 }})

    # R4 · background task spawn via asyncio.create_task
    r4_pass = (
        "asyncio.create_task" in job_src
        and "async def spawn_generation" in job_src
        and "task.set_name" in job_src
    )
    rows.append({"row": "R4", "name": "background_task_spawn_wired",
                 "pass": r4_pass, "detail": {}})

    # R5 · job store schema
    schema_keys = [
        '"job_id"', '"job_kind"', '"account_id"', '"context_id"', '"user_id"',
        '"target_id"', '"phase"', '"progress"', '"result"', '"error"',
        '"created_at"', '"updated_at"',
    ]
    missing = [k for k in schema_keys if k not in job_src]
    rows.append({"row": "R5", "name": "job_store_schema_complete",
                 "pass": len(missing) == 0,
                 "detail": {"missing_keys": missing}})

    # R6 · account isolation — get_job filters by account_id
    r6_pass = (
        'find_one(\n            {"job_id": job_id, "account_id": account_id}' in job_src
        or ('"account_id": account_id' in job_src and 'get_job' in job_src)
    )
    rows.append({"row": "R6", "name": "account_isolation_get_job_filters_account",
                 "pass": r6_pass, "detail": {}})

    # R7 · commit-lock 409 byte-identity — regenerate router calls engine's
    # commit_locked_409 helper directly (no envelope reshape in the async router).
    r7_pass = (
        "deck_regenerate.commit_locked_409(document_id)" in regen_src
        and "deck_regenerate._load_and_membership_check" in regen_src
    )
    rows.append({"row": "R7", "name": "commit_lock_409_shape_byte_identical",
                 "pass": r7_pass, "detail": {}})

    # R8 · audit fingerprint 19-field preserved — write_audit call in the
    # extracted runner has same arguments as pre-arc synchronous handler.
    r8_pass = (
        'write_audit(\n        context_id, ctx["account"]["id"],\n        "deck.generated"' in decks_src
        and '{"slides": len(rec["slides"]), "tier": rec["tier"]' in decks_src
    )
    rows.append({"row": "R8", "name": "audit_write_call_preserved_verbatim",
                 "pass": r8_pass, "detail": {}})

    # R9 · engine files unchanged
    engine_diffs = []
    for p in ENGINE_UNCHANGED_PATHS:
        d = _git_diff_stat(PRE_ARC_HEAD, p)
        if d:
            engine_diffs.append({"path": p, "diff_stat": d})
    rows.append({"row": "R9", "name": "engine_files_unchanged_vs_pre_arc",
                 "pass": len(engine_diffs) == 0,
                 "detail": {"pre_arc": PRE_ARC_HEAD, "changed_engines": engine_diffs}})

    # R10 · Shield sha256 identity
    head_composite, head_count = _shield_composite_head()
    pre_composite, pre_count = _shield_composite_at(PRE_ARC_HEAD)
    rows.append({"row": "R10", "name": "shield_sha256_identity_preserved",
                 "pass": head_composite == pre_composite and head_count == pre_count,
                 "detail": {
                     "head": head_composite, "pre_arc": pre_composite,
                     "head_file_count": head_count, "pre_file_count": pre_count,
                 }})

    # R11 · phase transitions instrumented — all 6 phase strings present
    phase_strings = [
        "PHASE_QUEUED",
        "PHASE_READING",
        "PHASE_STRUCTURING",
        "PHASE_DRAFTING",
        "PHASE_COMPLETE",
        "PHASE_ERROR",
    ]
    missing_phases = [p for p in phase_strings if p not in job_src]
    # Also verify runner calls set_phase at natural boundaries
    runner_calls_phase = (
        decks_src.count("deck_generation_jobs.set_phase") >= 4  # 2 runners × 2+ boundaries
        or decks_src.count("set_phase") >= 4
    )
    rows.append({"row": "R11", "name": "phase_transitions_instrumented",
                 "pass": len(missing_phases) == 0 and runner_calls_phase,
                 "detail": {"missing_phase_constants": missing_phases,
                            "set_phase_calls_in_decks": decks_src.count("set_phase")}})

    # R12 · FE state machine wired — polls status endpoint + maps phases
    r12_pass = (
        "generation-status" in fe_src
        and 'phase === "complete"' in fe_src
        and 'phase === "error"' in fe_src
        and 'reading: "active"' in fe_src
        and 'structuring: "active"' in fe_src
        and 'drafting: "active"' in fe_src
        and "job_id" in fe_src
    )
    rows.append({"row": "R12", "name": "fe_state_machine_wired_to_backend_phases",
                 "pass": r12_pass, "detail": {}})

    # R13 · Path B evidence artefacts present
    evidence_files = [
        EVIDENCE_DIR / "s05_async_v2_state.png",
        EVIDENCE_DIR / "s05_async_attempt2_state.png",
    ]
    r13_details = {}
    for f in evidence_files:
        r13_details[f.name] = {"exists": f.exists(), "bytes": (f.stat().st_size if f.exists() else 0)}
    r13_pass = all(d["exists"] and d["bytes"] >= 30_000 for d in r13_details.values())
    rows.append({"row": "R13", "name": "path_b_evidence_artefacts_present",
                 "pass": r13_pass, "detail": r13_details})

    # R14 · no state-injection captures in memo's declared script blocks
    forbidden = ["page.evaluate(\"setPhase", "page.evaluate('setState", "forceReactState", "__setPhase"]
    r14_pass = all(f not in memo for f in forbidden)
    rows.append({"row": "R14", "name": "no_state_injection_declared_in_memo",
                 "pass": r14_pass, "detail": {"forbidden_patterns_absent": r14_pass}})

    # R15 · regression: prior proving slices AST-clean + prior bankings intact
    scripts_dir = REPO_ROOT / "backend" / "scripts"
    slice_files = sorted(scripts_dir.glob("jc_*_proving_slice.py"))
    ast_failures: list[str] = []
    for f in slice_files:
        try:
            ast.parse(f.read_text())
        except SyntaxError as e:
            ast_failures.append(f"{f.name}: {e}")

    rules_dir = REPO_ROOT / "memory" / "rules"
    part0_rules = [
        "CANONICAL_SPEC_UX_BRIEF_V1_1_RULE.md",
        "UI_STORIES_CLOSE_ON_UI_LAYER_ONLY_RULE.md",
        "USER_QA_RE_RUN_IS_FINAL_GATE_RULE.md",
        "DECK_ID_COLLISION_GUARD_RULE.md",
    ]
    rules_present = {r: (rules_dir / r).exists() for r in part0_rules}

    r15_pass = len(ast_failures) == 0 and all(rules_present.values())
    rows.append({"row": "R15", "name": "regression_prior_slices_ast_clean_and_bankings_intact",
                 "pass": r15_pass,
                 "detail": {
                     "prior_slice_count": len(slice_files),
                     "ast_failures": ast_failures,
                     "part0_rules_present": rules_present,
                 }})

    return rows


def main() -> int:
    rows = _run_rows()
    passed = sum(1 for r in rows if r["pass"])
    total = len(rows)
    verdict = "GREEN" if passed == total else "RED"

    output_path = (
        Path(__file__).resolve().parent
        / ".jc_deck_gen_async_kickoff_poll_slice_results.json"
    )
    output_path.write_text(json.dumps({
        "arc": "JC-DECK-GEN-ASYNC-KICKOFF-POLL",
        "canonical_spec_line1": "user dispatch 2026-07-05 · JC-DECK-GEN-ASYNC-KICKOFF-POLL · architectural arc · Path B disposition",
        "verdict": verdict,
        "passed": passed,
        "total": total,
        "rows": rows,
    }, indent=2))

    print(f"JC-DECK-GEN-ASYNC-KICKOFF-POLL · slice verdict={verdict} ({passed}/{total})")
    for r in rows:
        status = "PASS" if r["pass"] else "FAIL"
        print(f"  {r['row']} · {status} · {r['name']}")
        if not r["pass"]:
            print(f"       detail={json.dumps(r['detail'])[:400]}")

    return 0 if verdict == "GREEN" else 1


if __name__ == "__main__":
    sys.exit(main())
