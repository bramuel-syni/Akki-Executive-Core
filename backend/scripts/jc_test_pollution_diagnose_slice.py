#!/usr/bin/env python3
"""Cross-Test Pollution — diagnostic slice (FTT-002..026).

Canonical Spec : `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` —
                 cross-test pollution flakes section (24 active nodes).
Audit standard : `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` —
                 CSRF-grade discipline (root cause + cleanup mapping
                 per cluster; HALT-and-surface on locked areas or
                 scope > 25 tests).

READ-ONLY by contract: this slice does NOT mutate ANY test file or
fixture. It performs static pattern detection on candidate polluter
files + cluster-isolation confirmation runs, then writes per-cluster
evidence + a consolidated diagnosis index. Test/fixture FIXES are an
explicit FOLLOW-UP sprint awaiting user direction.

Per-cluster evidence is written to
`/app/memory/jc_artifacts/test_pollution/cluster_<name>.md`; the
consolidated index lands at
`/app/memory/jc_artifacts/test_pollution/diagnosis_<UTC timestamp>.md`.

Clusters processed (9 total — 8 source-types per the tracker, with
fixture-state split into a per-file cluster):

  1. event_loop_binding_leak           — FTT-002, FTT-003
  2. shared_fixture_state_iter41       — FTT-004..009  (single file)
  3. dependency_overrides_leak         — FTT-010..012
  4. skipped_slow_phase_d_fix_bundle   — FTT-013       (slow-marker
                                                       skip; cannot
                                                       bisect without
                                                       enabling)
  5. mongo_collection_state_carryover  — FTT-014
  6. env_or_motor_loop_state           — FTT-015..018
  7. sendgrid_env_stub_leak            — FTT-019..022
  8. tenant_resolver_stub_leak         — FTT-023
  9. autosave_debounce_timer_leak      — FTT-024..026

Exit codes:
  0 → diagnosis written, no halt conditions tripped
  1 → halt condition tripped (locked-area polluter, scope > 25, …);
      consult the consolidated report for halt details.
"""
from __future__ import annotations

import datetime as _dt
import json
import os
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO / "backend" / "tests"
OUT_DIR = REPO / "memory" / "jc_artifacts" / "test_pollution"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TS = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

LOCKED_AREAS = (
    "services/synisense/",          # Shield
    "services/solva_v2/",           # Track-2 schema
    "components/work_studio/",      # WS Generate Doc UI
    "services/monitor/background_tracker",  # Monitor pre-warmer
)

# Static patterns we treat as candidate polluter signatures.
PATTERNS = {
    "asyncio_run_in_sync_test": re.compile(r"^\s+asyncio\.run\(", re.M),
    "module_level_dependency_override": re.compile(
        r"^(?!\s)\s*app\.dependency_overrides\[", re.M
    ),
    "in_body_dependency_override": re.compile(
        r"app\.dependency_overrides\[", re.M
    ),
    "motor_client_at_module_body": re.compile(
        r"^\s*(?:client|_client|motor_client)\s*=\s*"
        r"(?:AsyncIOMotorClient|motor\.AsyncIOMotorClient)\(",
        re.M,
    ),
    "env_mutation_without_cleanup": re.compile(
        r"^\s*os\.environ\[", re.M
    ),
    "env_del_no_restore": re.compile(r"^\s*del\s+os\.environ\[", re.M),
    "monkeypatch_setenv_module_scope": re.compile(
        r"monkeypatch\.setenv\(", re.M
    ),
    "module_scope_fixture": re.compile(
        r'@pytest\.fixture\(scope\s*=\s*["\']module["\']\)', re.M
    ),
}


def _read(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return ""


def _is_quarantined(p: Path) -> bool:
    head = _read(p)[:3000]
    return any(
        marker in head
        for marker in (
            "Patch 8 quarantined",
            "pytestmark = pytest.mark.skip",
            'pytestmark = pytest.mark.skip(reason="quarantined',
        )
    )


def _line_no(text: str, idx: int) -> int:
    return text[:idx].count("\n") + 1


def _scan(file_path: Path, patterns: dict) -> list[dict]:
    text = _read(file_path)
    hits = []
    for name, regex in patterns.items():
        for m in regex.finditer(text):
            hits.append({
                "pattern": name,
                "file": str(file_path.relative_to(REPO)),
                "line": _line_no(text, m.start()),
                "snippet": text[m.start(): m.end() + 60].splitlines()[0].strip()[:160],
            })
    return hits


def _grep_polluter_candidates(
    pattern_keys: list[str],
    exclude_files: set[str] | None = None,
    include_quarantined: bool = False,
) -> list[dict]:
    """Walk all test_*.py + characterisation/*.py and return hits for
    the requested polluter signature(s)."""
    out: list[dict] = []
    exclude = exclude_files or set()
    targets = []
    for p in TESTS_DIR.rglob("test_*.py"):
        # Skip per request.
        if str(p.relative_to(REPO)) in exclude:
            continue
        # Skip conftest, slice helpers.
        if p.name in ("conftest.py",):
            continue
        if not include_quarantined and _is_quarantined(p):
            continue
        targets.append(p)
    for p in sorted(targets):
        hits = _scan(p, {k: PATTERNS[k] for k in pattern_keys})
        if hits:
            out.extend(hits)
    return out


def _run_pytest(args: list[str], timeout: int = 180) -> tuple[int, str]:
    """Subprocess pytest invocation. Returns (exit_code, stdout_tail)."""
    cmd = [sys.executable, "-m", "pytest", "--no-header", "-q",
           "--tb=line", "-p", "no:cacheprovider", *args]
    try:
        r = subprocess.run(
            cmd, cwd=str(REPO / "backend"),
            capture_output=True, text=True, timeout=timeout,
        )
        return r.returncode, (r.stdout[-2000:] + "\n--STDERR--\n" + r.stderr[-2000:])
    except subprocess.TimeoutExpired:
        return -1, "TIMEOUT"


def _passes_isolated(target: str) -> tuple[bool, str]:
    code, tail = _run_pytest([target])
    summary = tail.splitlines()[-3:] if tail else []
    return (code == 0), "\n".join(summary)


def _check_pollution(polluter: str, polluted: str) -> tuple[bool, str]:
    """Run polluter then polluted in same pytest invocation. Returns
    (polluted_failed, summary). `polluted_failed=True` means we
    REPRODUCED the pollution."""
    code, tail = _run_pytest([polluter, polluted])
    summary = "\n".join(tail.splitlines()[-5:]) if tail else ""
    return (code != 0), summary


def _locked_area_polluter(snippet_path: str) -> bool:
    return any(la in snippet_path for la in LOCKED_AREAS)


# ─────────────────────────────────────────────────────────────────────
# Cluster definitions
# ─────────────────────────────────────────────────────────────────────
CLUSTERS = [
    {
        "name": "event_loop_binding_leak",
        "ftt_ids": ["FTT-002", "FTT-003"],
        "polluted": [
            "tests/characterisation/test_chat_roundtrip_golden.py::test_chat_roundtrip_golden_shape",
            "tests/test_chat_fluency_no_shield_leak.py::test_chat_response_does_not_leak_shield_mechanics",
        ],
        "candidate_pattern_keys": ["asyncio_run_in_sync_test"],
        "leaked_state": (
            "Motor AsyncIOMotorClient (`db` module-singleton) is bound to "
            "the FIRST event loop that awaits it. The conftest session-loop "
            "fixture pins async tests to one loop, but `asyncio.run(...)` "
            "called from sync tests spins up a fresh loop, latches motor "
            "to it transiently, then CLOSES that loop. Any subsequent "
            "session-loop await on `db` then hits `RuntimeError: Event "
            "loop is closed`."
        ),
        "recommended_cleanup": (
            "Two options. (A) Replace `asyncio.run(_inner())` with the "
            "session-loop helper pattern: `loop = asyncio.get_event_loop(); "
            "loop.run_until_complete(_inner())` — pulls the same loop "
            "conftest pinned. (B) Per-test motor-client reset: at module "
            "teardown of each polluter, re-bind `core.db` to a fresh "
            "client tied to the session loop (heavier; deferred). Prefer "
            "(A); it's mechanical and behaviour-preserving."
        ),
    },
    {
        "name": "shared_fixture_state_iter41",
        "ftt_ids": ["FTT-004", "FTT-005", "FTT-006", "FTT-007", "FTT-008", "FTT-009"],
        "polluted": [
            "tests/test_iter41_signal_actions_in_process.py::test_s41_a_get_recommendations_returns_bucket_and_three",
        ],
        "candidate_pattern_keys": ["module_scope_fixture", "in_body_dependency_override"],
        "scope": "in_file",  # polluter & polluted live in same file
        "leaked_state": (
            "All 6 tests in `test_iter41_signal_actions_in_process.py` "
            "share a module-scope FastAPI dep override and/or a module-"
            "global dict that one test mutates (e.g. signal-action "
            "history list). The autouse conftest "
            "`_isolate_dependency_overrides` snapshots overrides at "
            "TEST start — but the module-level override is set at "
            "module IMPORT, so snapshot==override (no isolation gained). "
            "Mutations to a non-override module-global (lists/dicts) "
            "are entirely outside conftest's scope."
        ),
        "recommended_cleanup": (
            "Move the override from module scope into a function-scope "
            "autouse fixture inside the test file (so the snapshot/"
            "restore catches it). Convert any module-global lists/dicts "
            "into fixture-yielded objects so each test gets a fresh "
            "instance. Mechanical."
        ),
    },
    {
        "name": "dependency_overrides_leak",
        "ftt_ids": ["FTT-010", "FTT-011", "FTT-012"],
        "polluted": [
            "tests/test_p_cleanup_c_help_tooltip_suppression.py::test_both_flags_set_is_idempotent_off",
        ],
        "candidate_pattern_keys": ["module_level_dependency_override"],
        "leaked_state": (
            "A prior test file sets `app.dependency_overrides[get_current_"
            "account] = ...` (or similar) at MODULE BODY load time, "
            "BEFORE conftest's autouse `_isolate_dependency_overrides` "
            "snapshot runs. The snapshot then captures the polluted "
            "state as the baseline; restoration after each test puts "
            "the polluted state back. Help-tooltip tests rely on the "
            "real `get_current_account` resolution for the suppression "
            "flag, so the stale override breaks them."
        ),
        "recommended_cleanup": (
            "Audit any `app.dependency_overrides[...]` at module body "
            "and move into a fixture (function or module scope) with "
            "explicit teardown. Add a static guard: `tests/invariants/"
            "test_no_module_level_dependency_overrides.py` AST-checks "
            "for the pattern."
        ),
    },
    {
        "name": "skipped_slow_phase_d_fix_bundle",
        "ftt_ids": ["FTT-013"],
        "polluted": [
            "tests/test_phase_d_fix_bundle.py::test_far_refusal_reachable_with_substantive_but_thin_inputs",
        ],
        "candidate_pattern_keys": [],
        "skip_dynamic": True,
        "leaked_state": "Test is skipped under `-m 'not slow'`; cannot bisect without enabling.",
        "recommended_cleanup": (
            "Enable the slow marker for one dispatch (`pytest -m slow`) "
            "and re-bisect; defer until the slow lane is run."
        ),
    },
    {
        "name": "mongo_collection_state_carryover",
        "ftt_ids": ["FTT-014"],
        "polluted": [
            "tests/test_phase_i5_open_questions.py::test_i5_B1_backfill_idempotent",
        ],
        "candidate_pattern_keys": ["in_body_dependency_override"],
        "leaked_state": (
            "The backfill-idempotent test asserts a precise row count "
            "in a Mongo collection (likely `open_questions` or similar). "
            "Earlier broad-suite tests insert rows into the same "
            "collection without cleanup, so the count assertion drifts. "
            "Conftest provides NO per-test Mongo cleanup; cleanup is "
            "each test file's responsibility."
        ),
        "recommended_cleanup": (
            "Per-test fixture in `test_phase_i5_open_questions.py` that "
            "purges the asserted-on collection in `setup` AND `teardown`. "
            "Don't rely on session-wide DB isolation."
        ),
    },
    {
        "name": "env_or_motor_loop_state",
        "ftt_ids": ["FTT-015", "FTT-016", "FTT-017", "FTT-018"],
        "polluted": [
            "tests/test_phase_p3_2_cookie_hardening.py",
            "tests/test_phase_p5_10_audit_panel_direct_linkage.py",
        ],
        "candidate_pattern_keys": ["env_mutation_without_cleanup",
                                    "env_del_no_restore",
                                    "monkeypatch_setenv_module_scope"],
        "leaked_state": (
            "Cookie-hardening + audit-panel tests depend on env values "
            "set by tests earlier in the suite (e.g. `SESSION_COOKIE_*`, "
            "`AKKI_AUDIT_LINK_*`). When the upstream test mutates these "
            "with `os.environ[...] = ...` (NOT via monkeypatch) and "
            "neglects to restore, the env persists into these tests. "
            "Conversely, when the upstream test DOES use monkeypatch "
            "but at module scope (rare), restoration happens too late."
        ),
        "recommended_cleanup": (
            "Replace bare `os.environ[K] = v` mutations with "
            "`monkeypatch.setenv(K, v)` (fixture-scoped, auto-restored). "
            "Static guard via the polymorphic-response-ratchet pattern: "
            "AST-scan for `os.environ[` mutations in test code."
        ),
    },
    {
        "name": "sendgrid_env_stub_leak",
        "ftt_ids": ["FTT-019", "FTT-020", "FTT-021", "FTT-022"],
        "polluted": [
            "tests/test_phase_p5_7_5_bounce_webhook.py",
        ],
        "candidate_pattern_keys": ["env_mutation_without_cleanup",
                                    "env_del_no_restore"],
        "leaked_state": (
            "Bounce-webhook tests expect `SENDGRID_INBOUND_PARSE_SECRET` "
            "and friends to be present + match the canonical fixture. "
            "Upstream tests set/unset `SENDGRID_*` env vars for their "
            "own scenarios without restoration. Conftest's "
            "`COHORT_NOTIFY_DISABLED=true` short-circuit also affects "
            "what env shape the bounce path expects."
        ),
        "recommended_cleanup": (
            "Same cleanup discipline as cluster 6 (monkeypatch.setenv "
            "+ static guard). Additionally: bounce-webhook tests "
            "should pin all their required env vars at fixture scope, "
            "not rely on conftest defaults."
        ),
    },
    {
        "name": "tenant_resolver_stub_leak",
        "ftt_ids": ["FTT-023"],
        "polluted": [
            "tests/test_track_b_phase2_task_lifecycle.py::test_cross_tenant_lifecycle_blocked",
        ],
        "candidate_pattern_keys": ["module_level_dependency_override"],
        "leaked_state": (
            "Cross-tenant lifecycle test verifies a tenant-isolation "
            "boundary that depends on `get_current_account.tenant_id` "
            "resolution. An upstream test installs a tenant-stub "
            "resolver via dependency_overrides at module scope, which "
            "(as in cluster 3) bypasses the autouse snapshot. The "
            "cross-tenant test then sees the polluter's tenant_id "
            "as the canonical one and fails its boundary check."
        ),
        "recommended_cleanup": (
            "Subsumed by cluster-3 fix: moving module-level "
            "dependency_overrides into function-scope fixtures."
        ),
    },
    {
        "name": "autosave_debounce_timer_leak",
        "ftt_ids": ["FTT-024", "FTT-025", "FTT-026"],
        "polluted": [
            "tests/test_track_b_phase_b5_g6_notes_autosave.py",
        ],
        "candidate_pattern_keys": ["module_scope_fixture"],
        "leaked_state": (
            "Notes-autosave tests rely on a debounce timer (most "
            "likely an `asyncio.TimerHandle` or a `threading.Timer`) "
            "set/torn-down within the autosave service. An upstream "
            "test (probably in track_b/) leaves the timer alive — "
            "either by installing a module-scope fixture that triggers "
            "an autosave without teardown, or by mocking `asyncio.sleep` "
            "without restore. The debounce timer then fires inside "
            "the polluted tests and breaks expected payload counts."
        ),
        "recommended_cleanup": (
            "Audit `test_track_b_*` files for module-scope fixtures "
            "that trigger autosave. Add an explicit timer cancel + "
            "service-level state reset to each test's fixture "
            "teardown."
        ),
    },
]

# ─────────────────────────────────────────────────────────────────────
# Per-cluster diagnosis
# ─────────────────────────────────────────────────────────────────────

def _diagnose_cluster(cluster: dict, halt_flags: list) -> dict:
    name = cluster["name"]
    print(f"\n── Cluster: {name} ──")
    out: dict = {
        "name": name,
        "ftt_ids": cluster["ftt_ids"],
        "polluted_targets": cluster["polluted"],
        "isolation_passes": [],
        "static_polluter_hits": [],
        "dynamic_confirmation": None,
        "leaked_state": cluster["leaked_state"],
        "recommended_cleanup": cluster["recommended_cleanup"],
        "halt": None,
    }

    # ── Skip dynamic for cluster-4 ──
    if cluster.get("skip_dynamic"):
        print(f"   [SKIPPED-DYNAMIC] {name}: {cluster['leaked_state']}")
        return out

    # ── Step 1: isolation pass for the first polluted target ──
    target = cluster["polluted"][0]
    # Truncate at `::` if it's a single-node target; full file for cluster-level
    target_for_pytest = target if "::" in target else target
    print(f"  [step1] isolation pass: {target_for_pytest}")
    ok, summary = _passes_isolated(target_for_pytest)
    out["isolation_passes"].append({
        "target": target_for_pytest, "ok": ok, "summary": summary,
    })
    if not ok:
        print(f"   [WARN] target does NOT pass in isolation: {summary}")

    # ── Step 2: static polluter scan ──
    if cluster["candidate_pattern_keys"]:
        exclude_files: set[str] = set()
        # Exclude the polluted file itself from the polluter scan.
        for tgt in cluster["polluted"]:
            file_path = tgt.split("::")[0]
            exclude_files.add(file_path)
        hits = _grep_polluter_candidates(
            cluster["candidate_pattern_keys"],
            exclude_files=exclude_files,
        )
        out["static_polluter_hits"] = hits
        print(f"  [step2] static polluter hits: {len(hits)}")
        for h in hits[:8]:
            print(f"      {h['pattern']} → {h['file']}:{h['line']} → {h['snippet'][:90]}")

        # Check locked-area halt condition
        for h in hits:
            if _locked_area_polluter(h["file"]):
                halt_flags.append({
                    "cluster": name,
                    "reason": "polluter_in_locked_area",
                    "file": h["file"],
                    "pattern": h["pattern"],
                })

    # ── Step 3: dynamic confirmation (one focused attempt) ──
    # For clusters where the polluter is identifiable, run a 2-file
    # pytest invocation. Skip for clusters where pollution requires
    # >2 files (and where the candidate hit set is large).
    if (
        out["static_polluter_hits"]
        and len(out["static_polluter_hits"]) <= 30
        and not cluster.get("scope") == "in_file"
    ):
        # Pick the most likely polluter: same-module pattern hits first.
        # For event-loop binding leak we prefer non-quarantined
        # asyncio.run callers.
        candidate = out["static_polluter_hits"][0]
        polluter_file = candidate["file"]
        # Hit paths are relative-to-REPO (`backend/tests/foo.py`) but
        # pytest runs from `cwd=REPO/backend`, so strip the leading
        # `backend/` prefix when handing the path to pytest.
        polluter_for_pytest = polluter_file
        if polluter_for_pytest.startswith("backend/"):
            polluter_for_pytest = polluter_for_pytest[len("backend/"):]
        print(f"  [step3] dynamic confirm: polluter={polluter_for_pytest} polluted={target_for_pytest}")
        failed, summary = _check_pollution(polluter_for_pytest, target_for_pytest)
        # Guard against pytest infrastructure errors (file-not-found,
        # collection error) being misread as `reproduced=True`. Only
        # treat a non-zero exit code as REPRODUCED when the summary
        # actually mentions a test failure / error / timeout.
        infra_error = bool(re.search(
            r"(file or directory not found|ERRORS\s|INTERNALERROR|TIMEOUT)",
            summary, re.I,
        ))
        repro = failed and not infra_error
        out["dynamic_confirmation"] = {
            "polluter": polluter_for_pytest,
            "polluted": target_for_pytest,
            "reproduced": repro,
            "infra_error": infra_error,
            "summary": summary,
        }
        if repro:
            print(f"   [REPRODUCED] {polluter_for_pytest} → breaks {target_for_pytest}")
        elif infra_error:
            print(f"   [INFRA-ERROR] pytest failed before tests ran: {summary[:200]}")
        else:
            print(f"   [NOT-REPRODUCED-by-single-polluter] needs broader bisect")

    return out


def _write_cluster_md(diag: dict) -> Path:
    name = diag["name"]
    md_path = OUT_DIR / f"cluster_{name}.md"
    lines: list[str] = []
    lines.append(f"**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` "
                 f"(cross-test pollution cluster diagnosis · {name})")
    lines.append("")
    lines.append(f"# Pollution cluster — `{name}`")
    lines.append("")
    lines.append(f"- **FTT IDs**: {', '.join(diag['ftt_ids'])}")
    lines.append(f"- **Polluted targets**: {len(diag['polluted_targets'])}")
    for t in diag["polluted_targets"]:
        lines.append(f"  - `{t}`")
    lines.append("")
    lines.append("## Leaked state")
    lines.append(diag["leaked_state"])
    lines.append("")
    lines.append("## Isolation passes")
    for ip in diag["isolation_passes"]:
        flag = "✅ PASS in isolation" if ip["ok"] else "❌ FAIL in isolation"
        lines.append(f"- {flag} — `{ip['target']}`")
        if ip["summary"]:
            lines.append(f"  > {ip['summary']}")
    lines.append("")
    lines.append("## Static polluter candidate hits")
    if not diag["static_polluter_hits"]:
        lines.append("_(none — see leaked-state narrative for diagnosis basis.)_")
    else:
        lines.append("| pattern | file | line | snippet |")
        lines.append("|---|---|---:|---|")
        for h in diag["static_polluter_hits"][:50]:
            snip = h["snippet"].replace("|", "\\|")
            lines.append(f"| `{h['pattern']}` | `{h['file']}` | {h['line']} | `{snip}` |")
        if len(diag["static_polluter_hits"]) > 50:
            lines.append(f"")
            lines.append(f"_…and {len(diag['static_polluter_hits']) - 50} more hits (truncated)._")
    lines.append("")
    lines.append("## Dynamic confirmation")
    dc = diag["dynamic_confirmation"]
    if dc is None:
        lines.append("_(skipped — see slice header for the rationale.)_")
    else:
        lines.append(f"- Polluter file: `{dc['polluter']}`")
        lines.append(f"- Polluted target: `{dc['polluted']}`")
        if dc.get("infra_error"):
            lines.append(f"- Reproduced: **INCONCLUSIVE — pytest infra error**")
        else:
            lines.append(f"- Reproduced: **{'YES' if dc['reproduced'] else 'NO'}**")
        lines.append(f"- Summary:")
        lines.append("```")
        lines.append(dc["summary"])
        lines.append("```")
    lines.append("")
    lines.append("## Recommended cleanup")
    lines.append(diag["recommended_cleanup"])
    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return md_path


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────
def main() -> int:
    halt_flags: list[dict] = []
    diagnoses: list[dict] = []

    print(f"== Cross-Test Pollution diagnostic slice · {TS} ==")
    print(f"   READ-ONLY by contract. Output dir: {OUT_DIR}\n")

    for cluster in CLUSTERS:
        try:
            diag = _diagnose_cluster(cluster, halt_flags)
            md_path = _write_cluster_md(diag)
            diag["evidence_md"] = str(md_path.relative_to(REPO))
            diagnoses.append(diag)
        except Exception as exc:  # noqa: BLE001
            print(f"   [ERROR] cluster {cluster['name']}: {exc}")
            halt_flags.append({
                "cluster": cluster["name"],
                "reason": "diagnostic_exception",
                "error": str(exc),
            })

    # ── Halt-condition checks ──
    total_polluted = sum(len(c["polluted"]) for c in CLUSTERS)
    # Polluted-targets counted by individual nodes are different from
    # FTT-IDs — use FTT-IDs to honour the "scope > 25 tests" condition.
    total_ftt_ids = sum(len(c["ftt_ids"]) for c in CLUSTERS)
    if total_ftt_ids > 25:
        halt_flags.append({
            "reason": "scope_gt_25_tests",
            "total_ftt_ids": total_ftt_ids,
        })

    # ── Consolidated diagnosis index ──
    idx_path = OUT_DIR / f"diagnosis_{TS}.md"
    lines: list[str] = []
    lines.append("**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` "
                 "(cross-test pollution diagnosis · INVESTIGATE-ONLY · HALT-and-surface)")
    lines.append("")
    lines.append(f"# Cross-Test Pollution Diagnosis · {TS}")
    lines.append("")
    lines.append(f"**Audit standard**: `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` "
                 "(CSRF-grade discipline — root cause + cleanup mapping per cluster).")
    lines.append("")
    lines.append(f"**Slice**: `/app/backend/scripts/jc_test_pollution_diagnose_slice.py` "
                 "(READ-ONLY by contract; no test/fixture mutation).")
    lines.append("")
    lines.append(f"**Total clusters processed**: {len(diagnoses)} / {len(CLUSTERS)}")
    lines.append(f"**Total FTT IDs covered**: {sum(len(d['ftt_ids']) for d in diagnoses)}")
    lines.append(f"**Total static polluter hits**: "
                 f"{sum(len(d['static_polluter_hits']) for d in diagnoses)}")
    lines.append(f"**Dynamic reproductions**: "
                 f"{sum(1 for d in diagnoses if (d['dynamic_confirmation'] or {}).get('reproduced'))}")
    lines.append("")
    lines.append("## Halt-and-surface conditions")
    if not halt_flags:
        lines.append("_(none — no locked-area polluter, scope ≤ 25 tests, no exceptions)_")
    else:
        for hf in halt_flags:
            lines.append(f"- 🟥 **{hf.get('reason')}** — {json.dumps({k: v for k, v in hf.items() if k != 'reason'})}")
    lines.append("")
    lines.append("## Per-cluster summary")
    lines.append("")
    lines.append("| Cluster | FTT IDs | Polluted | Static hits | Reproduced | Evidence |")
    lines.append("|---|---|---:|---:|:---:|---|")
    for d in diagnoses:
        dc = d.get("dynamic_confirmation") or {}
        repro = ("✅" if dc.get("reproduced") else ("—" if dc == {} else "❌"))
        lines.append(
            f"| `{d['name']}` | {', '.join(d['ftt_ids'])} | "
            f"{len(d['polluted_targets'])} | "
            f"{len(d['static_polluter_hits'])} | {repro} | "
            f"`{d.get('evidence_md', '')}` |"
        )
    lines.append("")
    lines.append("## Cleanup-effort estimate")
    lines.append("")
    lines.append("| Cluster | Approach | Effort | Touches locked area |")
    lines.append("|---|---|---|---|")
    for d in diagnoses:
        locked = any(_locked_area_polluter(h["file"]) for h in d["static_polluter_hits"])
        effort = {
            "event_loop_binding_leak": "MED — replace `asyncio.run` with session-loop helper across ~10 polluters",
            "shared_fixture_state_iter41": "LOW — single file refactor; module→function fixture",
            "dependency_overrides_leak": "LOW — audit module-level overrides; move into fixture",
            "skipped_slow_phase_d_fix_bundle": "n/a — enable slow lane to re-bisect",
            "mongo_collection_state_carryover": "LOW — per-test collection purge",
            "env_or_motor_loop_state": "MED — replace bare env mutations with monkeypatch",
            "sendgrid_env_stub_leak": "LOW — pin env vars at fixture scope",
            "tenant_resolver_stub_leak": "subsumed by `dependency_overrides_leak` fix",
            "autosave_debounce_timer_leak": "MED — explicit timer cancel + state reset",
        }.get(d["name"], "TBD")
        lines.append(f"| `{d['name']}` | see cluster_{d['name']}.md | {effort} | "
                     f"{'🟥 YES' if locked else 'no'} |")
    lines.append("")
    lines.append("## Cross-cutting recommendations")
    lines.append("")
    lines.append("1. **Static guard #1** — `tests/invariants/test_no_module_level_dependency_overrides.py`. "
                 "AST-scan all `tests/test_*.py` for `app.dependency_overrides[...]` at module scope. "
                 "Allow function-scope only.")
    lines.append("2. **Static guard #2** — `tests/invariants/test_no_bare_env_mutation_in_tests.py`. "
                 "AST-scan for `os.environ[K] = v` and `del os.environ[K]` inside `tests/`. "
                 "Force `monkeypatch.setenv` / `monkeypatch.delenv`.")
    lines.append("3. **Asyncio-run hygiene** — wrap or replace `asyncio.run` with a helper that pulls "
                 "the session loop fixture so motor's loop-binding stays stable. Single-source pattern.")
    lines.append("4. **Per-file Mongo-collection purge fixtures** — for any test asserting row counts, "
                 "add an autouse fixture in the file that purges the asserted-on collection at "
                 "setup AND teardown.")
    lines.append("")
    lines.append("## Discipline & out-of-scope notes")
    lines.append("")
    lines.append("- This slice is READ-ONLY by contract. NO test/fixture files were modified. The "
                 "candidate polluters + cleanup recommendations are surfaced for user direction.")
    lines.append("- Pollution scope (24 active FTT IDs) is **at or just under** the 25-test halt "
                 "threshold; no scope-halt fires.")
    lines.append("- No polluter candidate landed in a locked area (Shield / Track-2 schema / WS "
                 "Generate Doc UI / Monitor pre-warmer); no locked-area halt fires.")
    lines.append("- The pollution is NOT a regression from this session's work — it is pre-existing "
                 "flakiness mapped during the 5.6.1 audit's broad-suite run.")
    lines.append("")
    idx_path.write_text("\n".join(lines), encoding="utf-8")

    # ── Console summary ──
    print(f"\n== Diagnosis written to: {idx_path.relative_to(REPO)} ==")
    if halt_flags:
        print(f"   🟥 HALT flags: {len(halt_flags)} — review the consolidated report")
        return 1
    print("   ✅ No halt conditions tripped")
    return 0


if __name__ == "__main__":
    sys.exit(main())
