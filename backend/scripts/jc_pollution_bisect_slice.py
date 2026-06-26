#!/usr/bin/env python3
"""Cross-Test Pollution Bisect — statically-narrowed predecessor search.

Canonical Spec : `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md`
                 (CROSS-TEST POLLUTION FLAKES section · 18 FTT IDs / 7 files
                 confirmed FAIL_IN_CONTEXT by P5.7-PER-FILE-CAPTURE)
Audit standard : `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` —
                 CSRF-grade discipline: every polluter→polluted pair MUST
                 be confirmed dynamically by paired pytest invocation.
                 The P5.7-DIAG static cluster signatures are SEARCH
                 HEURISTICS for the candidate predecessor list — NOT a
                 fix. (a) full binary-search fallback is the next step
                 for any file that lands in the holdout bucket.
Sprint memo    : `/app/memory/sprints/P5_7_BISECT.md`

READ-ONLY by contract. NO test/fixture/production code mutated.

────────────────────────────────────────────────────────────────────
Algorithm
────────────────────────────────────────────────────────────────────

For each of the 7 confirmed FAIL_IN_CONTEXT files:

  1. Determine the file's P5.7-DIAG cluster hypothesis.
  2. Build the candidate predecessor list:
        - cluster.pattern_keys → AST/regex scan of all `test_*.py`
        - restrict to files that pytest would COLLECT BEFORE the polluted
          file (alphabetical predecessors only; pytest default order)
        - exclude quarantined test files (modules with
          `pytestmark = pytest.mark.skip(...)` at module body)
        - cap at MAX_CANDIDATES_PER_FILE (30) — closest alphabetical
          predecessors first
  3. For each candidate, run subprocess pytest with the two files in
     order: `pytest <candidate> <polluted_file>` with a 30 s wall
     timeout, `-p no:cacheprovider`, marker filter `not integration
     and not deploy_smoke and not runtime_playwright`.
  4. Bucket the result:
        - polluted_file PASSes → NOT-A-POLLUTER (candidate doesn't
          break it in this pairing)
        - polluted_file FAILs → CONFIRMED POLLUTER pair → emit MD at
          `/app/memory/jc_artifacts/test_pollution/confirmed_pairs/`
        - TIMEOUT → INCONCLUSIVE (note candidate; do not auto-classify)
  5. If a file's full candidate list returns 0 confirmed pairs → file
     goes to HOLDOUTS bucket (next sprint: full (a) binary search).

────────────────────────────────────────────────────────────────────
HALT-and-surface conditions (pre-authorised by user)
────────────────────────────────────────────────────────────────────

  - confirmed polluter in a locked area (Shield · WS Generate Doc UI
    · Track-2 schema · Monitor pre-warmer) → HALT for review
  - polluter chain requires 3+ tests in order (not pairwise) → HALT;
    detected when (i) file lands in holdouts AND (ii) static-cluster
    hypothesis would otherwise suggest a deterministic polluter chain
    — surface as a separate-shape sprint
  - pytest-forked / subprocess produces inconsistent results across
    re-runs on a confirmed pair → HALT; sample-re-run is built in
    via SAMPLE_RECHECK
  - shared_fixture_state_iter41 cluster (in-file pollution) — this
    bisect's predecessor-search shape does NOT apply; surface
    explicitly as a separate "intra-file polluter analysis" sprint

────────────────────────────────────────────────────────────────────
Output
────────────────────────────────────────────────────────────────────

  - per-pair MD: `/app/memory/jc_artifacts/test_pollution/confirmed_pairs/<polluter>__<polluted>.md`
  - consolidated index: `/app/memory/jc_artifacts/test_pollution/bisect_<UTC ts>.md`

Exit codes:
  0 → bisect ran clean
  1 → at least one HALT condition tripped
"""
from __future__ import annotations

import datetime as _dt
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO / "backend" / "tests"
OUT_DIR = REPO / "memory" / "jc_artifacts" / "test_pollution"
CONFIRMED_DIR = OUT_DIR / "confirmed_pairs"
CONFIRMED_DIR.mkdir(parents=True, exist_ok=True)
TS = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

LOCKED_AREAS = (
    "services/synisense/",
    "services/solva_v2/",
    "components/work_studio/",
    "services/monitor/background_tracker",
)

MAX_CANDIDATES_PER_FILE = 30
PYTEST_TIMEOUT_S = 30
PYTEST_MARKERS = "not integration and not deploy_smoke and not runtime_playwright"

# ─────────────────────────────────────────────────────────────────────
# Static polluter-pattern catalog (mirrors P5.7-DIAG)
# ─────────────────────────────────────────────────────────────────────
PATTERNS = {
    "asyncio_run_in_sync_test": re.compile(r"^\s+asyncio\.run\(", re.M),
    "module_level_dependency_override": re.compile(
        r"^(?!\s)\s*app\.dependency_overrides\[", re.M
    ),
    "in_body_dependency_override": re.compile(
        r"app\.dependency_overrides\[", re.M
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
    "sendgrid_env_marker": re.compile(
        r"SENDGRID_(?:INBOUND|WEBHOOK|API_KEY|BOUNCE)", re.M
    ),
    "tenant_override_marker": re.compile(
        r"(?:tenant_id|TenantContext|get_tenant_from_request)", re.M
    ),
    "autosave_timer_marker": re.compile(
        r"(?:debounce|TimerHandle|asyncio\.sleep|threading\.Timer)", re.M
    ),
}

# ─────────────────────────────────────────────────────────────────────
# Cluster → polluted file + candidate pattern keys
# ─────────────────────────────────────────────────────────────────────
CLUSTERS: list[dict] = [
    {
        "cluster": "shared_fixture_state_iter41",
        "polluted_file": "tests/test_iter41_signal_actions_in_process.py",
        "ftt_ids": ["FTT-004", "FTT-005", "FTT-006", "FTT-007", "FTT-008", "FTT-009"],
        "shape": "in_file",   # IN-FILE pollution; this bisect shape doesn't apply
        "pattern_keys": [],
    },
    {
        "cluster": "dependency_overrides_leak",
        "polluted_file": "tests/test_p_cleanup_c_help_tooltip_suppression.py",
        "ftt_ids": ["FTT-010", "FTT-011", "FTT-012"],
        "shape": "external",
        "pattern_keys": [
            "module_level_dependency_override",
            "in_body_dependency_override",
        ],
    },
    {
        "cluster": "env_or_motor_loop_state__p3_2",
        "polluted_file": "tests/test_phase_p3_2_cookie_hardening.py",
        "ftt_ids": ["FTT-015", "FTT-016"],
        "shape": "external",
        "pattern_keys": [
            "env_mutation_without_cleanup",
            "env_del_no_restore",
            "monkeypatch_setenv_module_scope",
        ],
    },
    {
        "cluster": "env_or_motor_loop_state__p5_10",
        "polluted_file": "tests/test_phase_p5_10_audit_panel_direct_linkage.py",
        "ftt_ids": ["FTT-017", "FTT-018"],
        "shape": "external",
        "pattern_keys": [
            "env_mutation_without_cleanup",
            "env_del_no_restore",
            "monkeypatch_setenv_module_scope",
        ],
    },
    {
        "cluster": "sendgrid_env_stub_leak",
        "polluted_file": "tests/test_phase_p5_7_5_bounce_webhook.py",
        "ftt_ids": ["FTT-019", "FTT-020", "FTT-021", "FTT-022"],
        "shape": "external",
        "pattern_keys": [
            "sendgrid_env_marker",
            "env_mutation_without_cleanup",
            "env_del_no_restore",
        ],
    },
    {
        "cluster": "tenant_resolver_stub_leak",
        "polluted_file": "tests/test_track_b_phase2_task_lifecycle.py",
        "ftt_ids": ["FTT-023"],
        "shape": "external",
        "pattern_keys": [
            "module_level_dependency_override",
            "tenant_override_marker",
            "in_body_dependency_override",
        ],
    },
    {
        "cluster": "autosave_debounce_timer_leak",
        "polluted_file": "tests/test_track_b_phase_b5_g6_notes_autosave.py",
        "ftt_ids": ["FTT-024", "FTT-025", "FTT-026"],
        "shape": "external",
        "pattern_keys": [
            "autosave_timer_marker",
            "module_scope_fixture",
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────

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
            "pytestmark = pytest.mark.skip",
            'pytestmark = pytest.mark.skip(reason="quarantined',
            "Patch 8 quarantined",
        )
    )


def _all_test_files() -> list[Path]:
    out: list[Path] = []
    for p in sorted(TESTS_DIR.rglob("test_*.py")):
        rel = str(p.relative_to(REPO / "backend"))
        if "/invariants/" in rel or "/deploy/" in rel:
            continue
        if "__pycache__" in p.parts:
            continue
        out.append(p)
    return out


def _alphabetical_predecessors(polluted_rel: str) -> list[str]:
    """Files that pytest collects BEFORE the polluted file in default
    alphabetical order. Returns repo-relative-to-backend paths."""
    files = _all_test_files()
    rels = [str(p.relative_to(REPO / "backend")) for p in files]
    rels.sort()
    if polluted_rel not in rels:
        return []
    idx = rels.index(polluted_rel)
    return rels[:idx]


def _file_matches_any_pattern(p: Path, pattern_keys: list[str]) -> bool:
    text = _read(p)
    for k in pattern_keys:
        if PATTERNS[k].search(text):
            return True
    return False


def _candidate_predecessors(cluster: dict) -> list[str]:
    """Return ordered list of candidate predecessor files for the cluster.
    Order: nearest-to-polluted-file alphabetically, then second-nearest, etc.
    Capped at MAX_CANDIDATES_PER_FILE."""
    polluted_rel = cluster["polluted_file"]
    pred = _alphabetical_predecessors(polluted_rel)
    candidates: list[str] = []
    for rel in reversed(pred):  # nearest-first ordering
        p = REPO / "backend" / rel
        if _is_quarantined(p):
            continue
        if _file_matches_any_pattern(p, cluster["pattern_keys"]):
            candidates.append(rel)
            if len(candidates) >= MAX_CANDIDATES_PER_FILE:
                break
    return candidates


def _locked_area_polluter(path: str) -> bool:
    return any(la in path for la in LOCKED_AREAS)


# ─────────────────────────────────────────────────────────────────────
# Pytest runner
# ─────────────────────────────────────────────────────────────────────

def _run_paired_pytest(polluter: str, polluted: str) -> dict:
    cmd = [
        sys.executable, "-m", "pytest", polluter, polluted,
        "-q", "--no-header", "--tb=no",
        "-m", PYTEST_MARKERS,
        "-p", "no:cacheprovider",
    ]
    start = time.monotonic()
    try:
        r = subprocess.run(
            cmd, cwd=str(REPO / "backend"),
            capture_output=True, text=True, timeout=PYTEST_TIMEOUT_S,
        )
        duration = time.monotonic() - start
        stdout_tail = "\n".join(r.stdout.splitlines()[-30:])
        # Detect polluted-side failures: look for `FAILED <polluted>` in stdout
        polluted_failed = bool(re.search(
            rf"FAILED\s+{re.escape(polluted)}", r.stdout
        ))
        return {
            "polluter": polluter,
            "polluted": polluted,
            "duration_s": round(duration, 2),
            "returncode": r.returncode,
            "stdout_tail": stdout_tail,
            "polluted_failed": polluted_failed,
            "bucket": (
                "CONFIRMED_POLLUTER" if polluted_failed
                else ("BOTH_PASSED" if r.returncode == 0 else "INCONCLUSIVE")
            ),
        }
    except subprocess.TimeoutExpired:
        duration = time.monotonic() - start
        return {
            "polluter": polluter,
            "polluted": polluted,
            "duration_s": round(duration, 2),
            "returncode": -9,
            "stdout_tail": "(timeout)",
            "polluted_failed": False,
            "bucket": "TIMEOUT",
        }


# ─────────────────────────────────────────────────────────────────────
# Confirmed-pair MD emitter
# ─────────────────────────────────────────────────────────────────────

def _emit_pair_md(result: dict, cluster: dict) -> Path:
    polluter_slug = result["polluter"].replace("/", "__").replace(".py", "")
    polluted_slug = result["polluted"].replace("/", "__").replace(".py", "")
    p = CONFIRMED_DIR / f"{polluter_slug}__BREAKS__{polluted_slug}.md"
    lines: list[str] = []
    lines.append("**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` "
                 "(cross-test pollution · confirmed polluter→polluted pair)")
    lines.append("")
    lines.append(f"# Confirmed pollution pair")
    lines.append("")
    lines.append(f"- **Polluter file**: `{result['polluter']}`")
    lines.append(f"- **Polluted file**: `{result['polluted']}`")
    lines.append(f"- **Cluster**: `{cluster['cluster']}`")
    lines.append(f"- **FTT IDs covered**: {', '.join(cluster['ftt_ids'])}")
    lines.append(f"- **Locked area polluter?**: "
                 f"{'🟥 YES (HALT)' if _locked_area_polluter(result['polluter']) else 'no'}")
    lines.append(f"- **Pair duration**: {result['duration_s']} s")
    lines.append(f"- **Exit code**: {result['returncode']}")
    lines.append("")
    lines.append("## Reproduction command")
    lines.append("```bash")
    lines.append(f"cd /app/backend && python -m pytest {result['polluter']} "
                 f"{result['polluted']} -q --no-header --tb=no "
                 f"-m '{PYTEST_MARKERS}' -p no:cacheprovider")
    lines.append("```")
    lines.append("")
    lines.append("## STDOUT tail (failure output)")
    lines.append("```")
    lines.append(result["stdout_tail"])
    lines.append("```")
    lines.append("")
    lines.append("## Suspected leaked state (static-signature hypothesis)")
    lines.append("Per the cluster signature (search heuristic):")
    lines.append("")
    for k in cluster["pattern_keys"]:
        lines.append(f"- `{k}`")
    lines.append("")
    lines.append("Actual root cause requires source inspection of the polluter file "
                 "and the polluted assertion. This MD records the *confirmed* pair "
                 "by paired pytest execution; the fix-scope decision and leaked-state "
                 "characterisation are deferred to the next sprint per the HARD STOP "
                 "contract.")
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


# ─────────────────────────────────────────────────────────────────────
# Sample-recheck for confirmed pairs (consistency guard)
# ─────────────────────────────────────────────────────────────────────

def _sample_recheck(pair: dict) -> dict:
    """Re-run a confirmed pair once to detect pytest-subprocess
    inconsistency. If the second run reverses the outcome → flag."""
    recheck = _run_paired_pytest(pair["polluter"], pair["polluted"])
    return {
        "first_bucket": pair["bucket"],
        "recheck_bucket": recheck["bucket"],
        "consistent": pair["bucket"] == recheck["bucket"],
    }


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

def main() -> int:
    print(f"== Cross-Test Pollution Bisect · {TS} ==")
    print(f"   Per-pair timeout: {PYTEST_TIMEOUT_S}s")
    print(f"   Max candidates per file: {MAX_CANDIDATES_PER_FILE}")
    print(f"   Confirmed-pair output: {CONFIRMED_DIR.relative_to(REPO)}\n")

    halt_flags: list[dict] = []
    holdouts: list[dict] = []
    intra_file_clusters: list[dict] = []
    cluster_results: list[dict] = []

    start_run = time.monotonic()

    for cluster in CLUSTERS:
        polluted = cluster["polluted_file"]
        print(f"\n── Cluster: {cluster['cluster']} ──")
        print(f"   Polluted file: {polluted}")
        print(f"   FTT IDs:       {', '.join(cluster['ftt_ids'])}")

        # ── In-file shape: skip predecessor search; surface for next sprint ──
        if cluster["shape"] == "in_file":
            print(f"   [SKIPPED] in-file pollution shape — predecessor search "
                  "doesn't apply. Surfaced for next sprint.")
            intra_file_clusters.append(cluster)
            cluster_results.append({**cluster, "confirmed_pairs": [],
                                    "holdout": False, "intra_file": True})
            continue

        candidates = _candidate_predecessors(cluster)
        print(f"   Candidates (static-signature, predecessor-restricted, capped at "
              f"{MAX_CANDIDATES_PER_FILE}): {len(candidates)}")
        for c in candidates[:5]:
            print(f"      · {c}")
        if len(candidates) > 5:
            print(f"      · …and {len(candidates) - 5} more")

        if not candidates:
            print(f"   [HOLDOUT] no static-signature candidates among "
                  "predecessors — straight to holdouts.")
            holdouts.append({**cluster, "reason": "no_static_candidates"})
            cluster_results.append({**cluster, "confirmed_pairs": [],
                                    "holdout": True})
            continue

        confirmed_pairs: list[dict] = []
        inconclusive_pairs: list[dict] = []
        for i, cand in enumerate(candidates, start=1):
            res = _run_paired_pytest(cand, polluted)
            tag = res["bucket"]
            print(f"     [{i:>2}/{len(candidates)}] [{tag:<19}] "
                  f"{res['duration_s']:>5.1f}s  {cand}")
            if res["bucket"] == "CONFIRMED_POLLUTER":
                # Locked-area halt check
                if _locked_area_polluter(cand):
                    halt_flags.append({
                        "reason": "confirmed_polluter_in_locked_area",
                        "polluter": cand,
                        "polluted": polluted,
                        "cluster": cluster["cluster"],
                    })
                # Sample-recheck for consistency
                rc = _sample_recheck(res)
                if not rc["consistent"]:
                    halt_flags.append({
                        "reason": "pytest_subprocess_inconsistency",
                        "polluter": cand,
                        "polluted": polluted,
                        "first": rc["first_bucket"],
                        "recheck": rc["recheck_bucket"],
                    })
                else:
                    md_path = _emit_pair_md(res, cluster)
                    confirmed_pairs.append({**res, "evidence_md": str(md_path)})
            elif res["bucket"] == "INCONCLUSIVE":
                inconclusive_pairs.append(res)
            elif res["bucket"] == "TIMEOUT":
                inconclusive_pairs.append(res)
            # BOTH_PASSED → no action (candidate not a polluter)

        if not confirmed_pairs:
            print(f"   [HOLDOUT] 0 confirmed pairs after {len(candidates)} "
                  "candidates — file goes to full-(a) binary-search next sprint.")
            holdouts.append({
                **cluster,
                "reason": "no_confirmed_pair_in_static_candidate_set",
                "candidates_tried": len(candidates),
                "inconclusive": len(inconclusive_pairs),
            })
        else:
            print(f"   [DONE] {len(confirmed_pairs)} confirmed polluter(s).")
        cluster_results.append({
            **cluster,
            "candidates_tried": len(candidates),
            "confirmed_pairs": confirmed_pairs,
            "inconclusive_pairs": inconclusive_pairs,
            "holdout": not confirmed_pairs,
        })

    elapsed = time.monotonic() - start_run

    # ─── Consolidated index ───
    idx_path = OUT_DIR / f"bisect_{TS}.md"
    lines: list[str] = []
    lines.append("**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` "
                 "(cross-test pollution bisect · statically-narrowed search · HARD STOP "
                 "at confirmed-pair surface)")
    lines.append("")
    lines.append(f"# Cross-Test Pollution Bisect · {TS}")
    lines.append("")
    lines.append(f"**Audit standard**: `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` "
                 "— every polluter→polluted pair MUST be confirmed by paired pytest "
                 "execution. Static cluster signatures are SEARCH HEURISTICS only.")
    lines.append("")
    lines.append(f"**Slice**: `/app/backend/scripts/jc_pollution_bisect_slice.py` "
                 "(READ-ONLY by contract).")
    lines.append("")
    lines.append(f"**Per-pair timeout**: {PYTEST_TIMEOUT_S}s")
    lines.append(f"**Max candidates per file**: {MAX_CANDIDATES_PER_FILE}")
    lines.append(f"**Wall time**: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    lines.append("")
    lines.append("## Cluster-level summary")
    lines.append("")
    lines.append("| Cluster | Polluted file | FTT IDs | Candidates | Confirmed | Status |")
    lines.append("|---|---|---|---:|---:|---|")
    for cr in cluster_results:
        if cr.get("intra_file"):
            status = "🟧 intra-file shape (separate sprint)"
            cand_n = "—"
            conf_n = "—"
        elif cr.get("holdout"):
            status = "🟨 HOLDOUT (full-(a) bisect next)"
            cand_n = str(cr.get("candidates_tried", 0))
            conf_n = "0"
        else:
            status = "✅ confirmed"
            cand_n = str(cr.get("candidates_tried", 0))
            conf_n = str(len(cr["confirmed_pairs"]))
        lines.append(f"| `{cr['cluster']}` | `{cr['polluted_file']}` | "
                     f"{', '.join(cr['ftt_ids'])} | {cand_n} | {conf_n} | {status} |")
    lines.append("")
    lines.append("## Confirmed polluter→polluted pairs")
    lines.append("")
    any_confirmed = any(
        cr.get("confirmed_pairs") for cr in cluster_results
    )
    if not any_confirmed:
        lines.append("_(none — all clusters in holdouts or intra-file. Full-(a) binary "
                     "search is the next sprint scope.)_")
    else:
        for cr in cluster_results:
            for cp in cr.get("confirmed_pairs", []):
                lines.append(f"- `{cp['polluter']}` → BREAKS → `{cp['polluted']}`")
                lines.append(f"  - Cluster: `{cr['cluster']}`")
                lines.append(f"  - FTT IDs: {', '.join(cr['ftt_ids'])}")
                lines.append(f"  - Evidence: `{cp['evidence_md']}`")
    lines.append("")
    lines.append("## Holdouts (full-(a) binary search next sprint)")
    lines.append("")
    if not holdouts:
        lines.append("_(none)_")
    else:
        lines.append("| Cluster | File | Reason | Candidates tried |")
        lines.append("|---|---|---|---:|")
        for h in holdouts:
            lines.append(f"| `{h['cluster']}` | `{h['polluted_file']}` | "
                         f"{h.get('reason')} | {h.get('candidates_tried', 0)} |")
    lines.append("")
    lines.append("## Intra-file clusters (separate sprint shape)")
    lines.append("")
    if not intra_file_clusters:
        lines.append("_(none)_")
    else:
        for c in intra_file_clusters:
            lines.append(f"- **`{c['cluster']}`** — `{c['polluted_file']}` — "
                         f"FTT IDs: {', '.join(c['ftt_ids'])}. In-file pollution "
                         "shape requires per-test-pair invocation WITHIN the file; "
                         "predecessor-search shape doesn't apply.")
    lines.append("")
    lines.append("## Halt-and-surface conditions")
    lines.append("")
    if not halt_flags:
        lines.append("_(none — all clear)_")
    else:
        for hf in halt_flags:
            lines.append(f"- 🟥 **{hf.get('reason')}**: `{hf}`")
    lines.append("")
    lines.append("## Discipline notes")
    lines.append("")
    lines.append("- READ-ONLY by contract honoured: 0 test/fixture/production lines mutated.")
    lines.append("- Static cluster signatures used as SEARCH HEURISTICS only (per user "
                 "direction); every confirmed pair was validated by paired pytest "
                 "execution.")
    lines.append("- Each confirmed pair was re-run once (sample-recheck) to detect "
                 "subprocess inconsistency; only consistent results emitted as evidence.")
    lines.append("- Fix scope on confirmed pairs is OUT OF SCOPE for this sprint — "
                 "HARD STOP per user direction; surface, wait.")
    lines.append("")

    idx_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"\n== Bisect done in {elapsed:.0f}s ({elapsed/60:.1f} min) ==")
    total_confirmed = sum(len(cr.get("confirmed_pairs", [])) for cr in cluster_results)
    print(f"   Confirmed polluter pairs: {total_confirmed}")
    print(f"   Holdouts (full-(a) next): {len(holdouts)}")
    print(f"   Intra-file clusters:      {len(intra_file_clusters)}")
    print(f"   Halt flags:               {len(halt_flags)}")
    print(f"   Index: {idx_path.relative_to(REPO)}")

    return 1 if halt_flags else 0


if __name__ == "__main__":
    sys.exit(main())
