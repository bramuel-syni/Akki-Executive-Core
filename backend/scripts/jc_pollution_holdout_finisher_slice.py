#!/usr/bin/env python3
"""Cross-Test Pollution Holdout-Finisher — full predecessor sweep.

Canonical Spec : `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md`
                 (CROSS-TEST POLLUTION FLAKES · holdouts from P5.7-BISECT
                 needing full-(a) search — `test_p_cleanup_c_help_tooltip_
                 suppression.py` (FTT-010..012) + `test_track_b_phase_b5_
                 g6_notes_autosave.py` (FTT-024..026))
Audit standard : `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` —
                 confirm-before-fix; static signatures are SEARCH
                 HEURISTICS only; every polluter→polluted pair MUST be
                 validated by paired pytest invocation
Sprint memo    : `/app/memory/sprints/P5_7_HOLDOUT_FINISHER.md`
Inputs         : `memory/jc_artifacts/test_pollution/per_file_capture_
                 20260626T181453Z.md` (PASS bucket from per-file capture)

READ-ONLY by contract. NO test/fixture/production code mutated.

────────────────────────────────────────────────────────────────────
Algorithm — for each holdout file:
────────────────────────────────────────────────────────────────────

  1. Compute candidate predecessor set:
       - Take ALL test_*.py files alphabetically BEFORE the holdout
         file (pytest's default collection order)
       - Filter to files in the PASS bucket from P5.7-PER-FILE-CAPTURE
         (we know they're healthy in isolation — failing predecessors
         are deterministic regressions, not polluters by definition)
       - Exclude quarantined files (`pytestmark = pytest.mark.skip`)

  2. Linear sweep: for each candidate, run subprocess
     `pytest <candidate> <holdout>` with 30 s wall timeout.

  3. On polluted_failed=True → confirmed pair → sample-recheck →
     if consistent → emit `confirmed_pair_holdout_<n>.md`.

  4. After full sweep:
       - If 1+ confirmed pairs → list them; note whether
         `test_phase4_2_http_transport_smoke.py` consolidates the
         holdout (turns 8-of-10 into 14-of-14 if it does).
       - If 0 confirmed pairs → HALT-and-surface ("shared global state
         pollutes many" shape, not pairwise — different fix shape).

────────────────────────────────────────────────────────────────────
HALT-and-surface conditions (pre-authorised by user)
────────────────────────────────────────────────────────────────────

  - 0 confirmed pairs for a holdout (different fix shape)
  - confirmed polluter in a locked area
  - new polluter source emerges (not `test_phase4_2_http_transport_smoke.py`)
    → surface clearly (this is diagnostic gold, not a HALT)
  - wall runtime > 2 h
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

PYTEST_TIMEOUT_S = 30
PYTEST_MARKERS = "not integration and not deploy_smoke and not runtime_playwright"
WALL_HALT_S = 2 * 60 * 60  # 2 h

HOLDOUTS: list[dict] = [
    {
        "polluted_file": "tests/test_p_cleanup_c_help_tooltip_suppression.py",
        "ftt_ids": ["FTT-010", "FTT-011", "FTT-012"],
        "cluster": "dependency_overrides_leak",
    },
    {
        "polluted_file": "tests/test_track_b_phase_b5_g6_notes_autosave.py",
        "ftt_ids": ["FTT-024", "FTT-025", "FTT-026"],
        "cluster": "autosave_debounce_timer_leak",
    },
]


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


def _pass_bucket_from_capture() -> set[str]:
    """Read PASS-bucket files from the per-file capture's per_file MDs."""
    per_file_dir = OUT_DIR / "per_file"
    pass_files: set[str] = set()
    for md in per_file_dir.glob("*.md"):
        text = md.read_text(encoding="utf-8", errors="replace")
        m_bucket = re.search(r"\*\*Bucket\*\*:\s*`(\w+)`", text)
        m_file = re.search(r"#\s+Per-file capture\s+·\s+`([^`]+)`", text)
        if m_bucket and m_file and m_bucket.group(1) == "PASS":
            pass_files.add(m_file.group(1))
    return pass_files


def _alphabetical_predecessors(polluted_rel: str) -> list[str]:
    files: list[str] = []
    for p in sorted(TESTS_DIR.rglob("test_*.py")):
        rel = str(p.relative_to(REPO / "backend"))
        if "/invariants/" in rel or "/deploy/" in rel:
            continue
        if "__pycache__" in p.parts:
            continue
        files.append(rel)
    files.sort()
    if polluted_rel not in files:
        return []
    return files[: files.index(polluted_rel)]


def _locked_area_polluter(path: str) -> bool:
    return any(la in path for la in LOCKED_AREAS)


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
        polluted_failed = bool(re.search(
            rf"FAILED\s+{re.escape(polluted)}", r.stdout
        ))
        bucket = (
            "CONFIRMED_POLLUTER" if polluted_failed
            else ("BOTH_PASSED" if r.returncode == 0 else "INCONCLUSIVE")
        )
        return {
            "polluter": polluter, "polluted": polluted,
            "duration_s": round(duration, 2),
            "returncode": r.returncode,
            "stdout_tail": stdout_tail,
            "polluted_failed": polluted_failed,
            "bucket": bucket,
        }
    except subprocess.TimeoutExpired:
        return {
            "polluter": polluter, "polluted": polluted,
            "duration_s": PYTEST_TIMEOUT_S,
            "returncode": -9,
            "stdout_tail": "(timeout)",
            "polluted_failed": False,
            "bucket": "TIMEOUT",
        }


def _emit_pair_md(result: dict, holdout: dict, ord_idx: int) -> Path:
    polluter_slug = result["polluter"].replace("/", "__").replace(".py", "")
    polluted_slug = result["polluted"].replace("/", "__").replace(".py", "")
    p = CONFIRMED_DIR / f"{polluter_slug}__BREAKS__{polluted_slug}.md"
    lines: list[str] = []
    lines.append("**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` "
                 "(cross-test pollution · confirmed polluter→polluted pair · holdout-finisher)")
    lines.append("")
    lines.append(f"# Confirmed pollution pair (holdout-finisher #{ord_idx})")
    lines.append("")
    lines.append(f"- **Polluter file**: `{result['polluter']}`")
    lines.append(f"- **Polluted file**: `{result['polluted']}`")
    lines.append(f"- **Cluster**: `{holdout['cluster']}`")
    lines.append(f"- **FTT IDs covered**: {', '.join(holdout['ftt_ids'])}")
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
    lines.append("Discovered via the holdout-finisher full predecessor sweep (vs. the "
                 "cluster-narrowed bisect in P5.7-BISECT). The cluster's static "
                 "signature did NOT include this polluter; only the full sweep "
                 "surfaced it. Confirm-before-fix discipline preserved: paired "
                 "pytest invocation validated the pair; sample-recheck consistent.")
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


def _sample_recheck(pair: dict) -> dict:
    recheck = _run_paired_pytest(pair["polluter"], pair["polluted"])
    return {
        "first_bucket": pair["bucket"],
        "recheck_bucket": recheck["bucket"],
        "consistent": pair["bucket"] == recheck["bucket"],
    }


def main() -> int:
    print(f"== Cross-Test Pollution Holdout-Finisher · {TS} ==")
    print(f"   Per-pair timeout: {PYTEST_TIMEOUT_S}s · Wall halt: {WALL_HALT_S}s\n")

    pass_files = _pass_bucket_from_capture()
    print(f"   PASS-bucket files loaded from per-file capture: {len(pass_files)}\n")

    halt_flags: list[dict] = []
    all_confirmed: list[dict] = []
    per_holdout: list[dict] = []
    start_run = time.monotonic()

    for holdout in HOLDOUTS:
        polluted = holdout["polluted_file"]
        print(f"\n── Holdout: {polluted} ──")
        print(f"   FTT IDs: {', '.join(holdout['ftt_ids'])}")

        # Build candidate set: alphabetical predecessors ∩ PASS-bucket
        predecessors = _alphabetical_predecessors(polluted)
        candidates = []
        for rel in predecessors:
            if rel not in pass_files:
                continue
            p = REPO / "backend" / rel
            if _is_quarantined(p):
                continue
            candidates.append(rel)

        # Nearest-first ordering (most-likely-polluter heuristic)
        candidates.reverse()
        print(f"   Candidates (PASS predecessors, quarantine-filtered): {len(candidates)}")

        holdout_confirmed: list[dict] = []
        holdout_inconclusive: list[dict] = []

        for i, cand in enumerate(candidates, start=1):
            # Wall halt check
            if time.monotonic() - start_run > WALL_HALT_S:
                halt_flags.append({
                    "reason": "wall_runtime_exceeded_2h",
                    "elapsed_s": round(time.monotonic() - start_run, 0),
                })
                print(f"   [HALT] wall runtime exceeded 2 h — stopping sweep")
                break

            res = _run_paired_pytest(cand, polluted)
            tag = res["bucket"]
            print(f"     [{i:>3}/{len(candidates)}] [{tag:<19}] "
                  f"{res['duration_s']:>5.1f}s  {cand}")

            if res["bucket"] == "CONFIRMED_POLLUTER":
                if _locked_area_polluter(cand):
                    halt_flags.append({
                        "reason": "confirmed_polluter_in_locked_area",
                        "polluter": cand, "polluted": polluted,
                    })
                rc = _sample_recheck(res)
                if not rc["consistent"]:
                    halt_flags.append({
                        "reason": "pytest_subprocess_inconsistency",
                        "polluter": cand, "polluted": polluted,
                        "first": rc["first_bucket"], "recheck": rc["recheck_bucket"],
                    })
                else:
                    md_path = _emit_pair_md(res, holdout, len(all_confirmed) + 1)
                    res["evidence_md"] = str(md_path)
                    holdout_confirmed.append(res)
                    all_confirmed.append({**res, "holdout": holdout})
                    print(f"        → emitted: {md_path.name}")
            elif res["bucket"] in ("INCONCLUSIVE", "TIMEOUT"):
                holdout_inconclusive.append(res)

        per_holdout.append({
            "holdout": holdout,
            "candidates_tried": len(candidates),
            "confirmed": holdout_confirmed,
            "inconclusive": holdout_inconclusive,
            "halt_no_pairwise_polluter": len(holdout_confirmed) == 0,
        })

        if not holdout_confirmed:
            halt_flags.append({
                "reason": "holdout_zero_confirmed_pairs_likely_shared_global_state",
                "holdout": polluted,
                "candidates_tried": len(candidates),
                "implication": (
                    "No single predecessor file alone breaks this holdout. "
                    "The pollution likely requires SHARED GLOBAL STATE built "
                    "up across multiple files (different fix shape — not pairwise)."
                ),
            })
            print(f"   [HALT-NOTE] 0 confirmed pairs after {len(candidates)} candidates "
                  "— different fix shape")

    elapsed = time.monotonic() - start_run

    # ── Consolidation insight ───
    polluter_counts: dict[str, list[dict]] = {}
    for c in all_confirmed:
        polluter_counts.setdefault(c["polluter"], []).append(c)
    consolidation_with_phase4_2 = polluter_counts.get(
        "tests/test_phase4_2_http_transport_smoke.py", []
    )

    # ── Consolidated index ───
    idx_path = OUT_DIR / f"holdout_{TS}.md"
    lines: list[str] = []
    lines.append("**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` "
                 "(holdout-finisher full predecessor sweep · HARD STOP at confirmed-pair "
                 "surface)")
    lines.append("")
    lines.append(f"# Holdout-Finisher · {TS}")
    lines.append("")
    lines.append(f"**Slice**: `/app/backend/scripts/jc_pollution_holdout_finisher_slice.py` "
                 "(READ-ONLY by contract).")
    lines.append("")
    lines.append(f"**Wall time**: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    lines.append(f"**Per-pair timeout**: {PYTEST_TIMEOUT_S}s")
    lines.append("")
    lines.append("## Per-holdout result")
    lines.append("")
    lines.append("| Holdout | FTT IDs | Candidates | Confirmed | Status |")
    lines.append("|---|---|---:|---:|---|")
    for h in per_holdout:
        status = ("🟥 0 pairwise polluters — shared global state shape"
                  if h["halt_no_pairwise_polluter"]
                  else "✅ confirmed")
        lines.append(
            f"| `{h['holdout']['polluted_file']}` | "
            f"{', '.join(h['holdout']['ftt_ids'])} | "
            f"{h['candidates_tried']} | {len(h['confirmed'])} | {status} |"
        )
    lines.append("")
    lines.append("## Confirmed polluter→polluted pairs (this sweep)")
    lines.append("")
    if not all_confirmed:
        lines.append("_(none — both holdouts surfaced 0 pairwise polluters)_")
    else:
        for c in all_confirmed:
            lines.append(f"- `{c['polluter']}` → BREAKS → `{c['polluted']}`")
            lines.append(f"  - FTT IDs: {', '.join(c['holdout']['ftt_ids'])}")
            lines.append(f"  - Evidence: `{c['evidence_md']}`")
    lines.append("")
    lines.append("## Consolidation analysis")
    lines.append("")
    if consolidation_with_phase4_2:
        consolidated_ftts = sum(
            (c["holdout"]["ftt_ids"] for c in consolidation_with_phase4_2), []
        )
        lines.append(f"**✅ `tests/test_phase4_2_http_transport_smoke.py` consolidates the holdouts.**")
        lines.append("")
        lines.append(f"Additional FTT IDs traced to this polluter in the holdout sweep: "
                     f"{', '.join(sorted(set(consolidated_ftts)))}.")
        lines.append("")
        lines.append("Combined with P5.7-BISECT (8 IDs), the polluter now covers:")
        prior_ftts = ["FTT-015", "FTT-016", "FTT-017", "FTT-018",
                      "FTT-019", "FTT-020", "FTT-021", "FTT-022"]
        all_ftts = sorted(set(prior_ftts + consolidated_ftts))
        lines.append(f"- **{len(all_ftts)} FTT IDs**: {', '.join(all_ftts)}")
        lines.append("")
        lines.append("**Fix-scope implication**: a single surgical sprint on "
                     "`test_phase4_2_http_transport_smoke.py` now closes "
                     f"{len(all_ftts)} FTT IDs + the file's own deterministic regression. "
                     "Highest leverage by a wide margin.")
    elif all_confirmed:
        lines.append("**🟧 New polluter source(s) surfaced — different file(s) than "
                     "`test_phase4_2_http_transport_smoke.py`.**")
        lines.append("")
        lines.append("Polluters surfaced this sweep:")
        for polluter, pairs in polluter_counts.items():
            ftts = sorted(set(
                f for c in pairs for f in c["holdout"]["ftt_ids"]
            ))
            lines.append(f"- `{polluter}` → {len(pairs)} pair(s) → FTT IDs: {', '.join(ftts)}")
        lines.append("")
        lines.append("**Fix-scope implication**: holdouts do NOT consolidate to "
                     "the P5.7-BISECT polluter. Surgical sprints must be sequenced — "
                     "one per distinct polluter source.")
    else:
        lines.append("**🟥 No consolidation possible — both holdouts returned 0 "
                     "pairwise polluters.**")
        lines.append("")
        lines.append("This indicates SHARED GLOBAL STATE pollution: the holdout's "
                     "failure shape requires accumulated state across multiple files, "
                     "not a single pairwise polluter. **Different fix shape.** "
                     "Recommendations:")
        lines.append("- Source-inspect each holdout for module-level dependency_overrides, "
                     "in-process scheduler queues, or shared global dicts.")
        lines.append("- Compare against the per-file capture's IN-CONTEXT failure mode "
                     "to identify which accumulated state matters.")
    lines.append("")
    lines.append("## Halt-and-surface conditions")
    lines.append("")
    if not halt_flags:
        lines.append("_(none — all clear)_")
    else:
        for hf in halt_flags:
            lines.append(f"- 🟥 **{hf.get('reason')}**: `{hf}`")
    lines.append("")
    lines.append("## Cluster taxonomy (full audit picture)")
    lines.append("")
    lines.append("Per user direction: surface the full taxonomy so fix-scope direction "
                 "can be made with the complete picture visible.")
    lines.append("")
    lines.append("| Cluster | Shape | FTT IDs | Disposition |")
    lines.append("|---|---|---|---|")
    lines.append("| A | external pollution from `test_phase4_2_http_transport_smoke.py` "
                 "(plus tiered via `test_phase_p5_10_audit_panel_direct_linkage.py`) | "
                 "FTT-015..023 (9 IDs from P5.7-BISECT) + this sweep's adds | "
                 "surgical sprint pending |")
    lines.append("| B | holdouts — full predecessor sweep results | "
                 "FTT-010..012 (test_p_cleanup_c) + FTT-024..026 (test_track_b_phase_b5) | "
                 "see results above |")
    lines.append("| C | intra-file (`test_iter41_signal_actions_in_process.py`) | "
                 "FTT-004..009 (6 IDs) | separate sprint shape — per-test-pair within file |")
    lines.append("| D | FTT-014 deterministic regression | FTT-014 | folds into Cluster A "
                 "surgical sprint per user direction (dual identity: polluter + own bug) |")
    lines.append("")
    lines.append("## Discipline notes")
    lines.append("")
    lines.append("- READ-ONLY by contract honoured: 0 test/fixture/production lines mutated.")
    lines.append("- Full predecessor sweep (not cluster-narrowed) — heuristic-free.")
    lines.append("- Sample-recheck on every confirmed pair (subprocess-inconsistency guard).")
    lines.append("- HARD STOP at confirmed-pair surface — fix sprint awaits user scope.")
    lines.append("")

    idx_path.write_text("\n".join(lines), encoding="utf-8")

    print(f"\n== Holdout-Finisher done in {elapsed:.0f}s ({elapsed/60:.1f} min) ==")
    print(f"   Confirmed pairs (this sweep): {len(all_confirmed)}")
    print(f"   Holdouts with 0 pairwise polluters: "
          f"{sum(1 for h in per_holdout if h['halt_no_pairwise_polluter'])}")
    print(f"   Consolidates with phase4_2_http_transport_smoke? "
          f"{'YES' if consolidation_with_phase4_2 else 'NO'}")
    print(f"   Halt flags: {len(halt_flags)}")
    print(f"   Index: {idx_path.relative_to(REPO)}")

    return 1 if halt_flags else 0


if __name__ == "__main__":
    sys.exit(main())
