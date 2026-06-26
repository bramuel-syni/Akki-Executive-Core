#!/usr/bin/env python3
"""B.2 Remeasure — post-A+D delta sweep on `test_track_b_phase_b5_g6_notes_autosave.py`.

Canonical Spec: `/app/memory/sprints/P5_7_FIX_SCOPE.md §2.3`
                (inter-cluster measurement procedure between A+D ship
                and B.2 dispatch — sizes B.2's actual scope on real
                post-A+D evidence rather than the pre-A+D hypothesis
                of 15 polluters)

Predecessor:    `sprints/JC_POLLUTION_A_D_FIX.md` (A+D shipped 2026-06-26;
                test-file-only patch closed FTT-014..022 [tracker IDs
                FTT-015..022] + the Cluster D sibling regression)
Inputs:         15 confirmed B.2 pairs from P5.7-HOLDOUT-FINISHER at
                `memory/jc_artifacts/test_pollution/confirmed_pairs/
                *__BREAKS__*notes_autosave.md`

────────────────────────────────────────────────────────────────────
Algorithm
────────────────────────────────────────────────────────────────────

  For each of the 15 known polluters of `test_track_b_phase_b5_g6_notes_
  autosave.py` (the pre-A+D list):

    1. Run subprocess `pytest <polluter> <autosave>` with 30 s wall
       timeout (same harness as `jc_pollution_holdout_finisher_slice.py`).
    2. Sample-recheck on each confirmed pair (subprocess-inconsistency
       guard, same as the holdout-finisher).
    3. Classify each polluter into one of:
         - DISAPPEARED — pre-A+D was CONFIRMED_POLLUTER; post-A+D is
                         BOTH_PASSED → pollution was downstream of
                         A+D's env-leak or loop-policy mutation.
         - REMAINING   — both pre-A+D and post-A+D are CONFIRMED_POLLUTER
                         → pollution is genuine B.2 scope (independent
                         of A+D).
         - INCONCLUSIVE — TIMEOUT or subprocess-inconsistency or
                         INCONCLUSIVE bucket on either run.

  After the sweep:
    - Pre-A+D polluter count: 15 (fixed)
    - Post-A+D polluter count: N (measured)
    - Disappeared: 15 - N (downstream of A+D's env/loop leak; closed-by-A+D)
    - Remaining: N (genuine B.2 scope — sizes the fix sprint)

────────────────────────────────────────────────────────────────────
READ-ONLY by contract
────────────────────────────────────────────────────────────────────

  - NO test/fixture/product file is mutated by this slice
  - Per-pair markdowns + consolidated index are the only writes,
    both under `memory/jc_artifacts/test_pollution/b2_remeasure/`
  - HARD STOP at consolidated-index emission — no fix-coding triggered

────────────────────────────────────────────────────────────────────
HALT-and-surface conditions
────────────────────────────────────────────────────────────────────

  - Any polluter shows pytest-subprocess inconsistency on sample-recheck
    → HALT flag emitted, pair NOT counted as evidence (per discipline)
  - Wall runtime > 30 min (sanity guard; 15 pairs × ~6s ≈ 90s nominal)
  - Any polluter newly surfaces in a locked area (Shield, WS Generate
    Doc UI, Track-2 schema, Monitor pre-warmer) → HALT flag + locked-
    area warning surfaced separately
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
B2_DIR = OUT_DIR / "b2_remeasure"
B2_DIR.mkdir(parents=True, exist_ok=True)
TS = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

LOCKED_AREAS = (
    "services/synisense/",
    "services/solva_v2/",
    "components/work_studio/",
    "services/monitor/background_tracker",
)

PYTEST_TIMEOUT_S = 30
PYTEST_MARKERS = "not integration and not deploy_smoke and not runtime_playwright"
WALL_HALT_S = 30 * 60  # 30 min

POLLUTED = "tests/test_track_b_phase_b5_g6_notes_autosave.py"

# 15 confirmed polluters from P5.7-HOLDOUT-FINISHER (alphabetical for
# audit trail readability; insertion order is harness-irrelevant).
POLLUTERS_PRE_A_D: list[str] = [
    "tests/test_phase_p2_a2_microsoft_pkce.py",
    "tests/test_phase_p2_b1_security_headers.py",
    "tests/test_phase_p2_b4_password_change.py",
    "tests/test_phase_p2_b6_admin_force_reset.py",
    "tests/test_phase_p2_d2_health_composite.py",
    "tests/test_phase_p3_1_csrf.py",
    "tests/test_phase_p3_2_cookie_hardening.py",
    "tests/test_phase_p3_4_session_timeout.py",
    "tests/test_phase_p5_10_audit_panel_direct_linkage.py",
    "tests/test_phase_p5_5_session_reauth.py",
    "tests/test_phase_p5_7_5_bounce_webhook.py",
    "tests/test_phase_p5_7_waitlist_reminder.py",
    "tests/test_phase_p5_8_inbox_migration.py",
    "tests/test_phase_p5_9_admin_button_and_badge.py",
    "tests/test_synisense_security.py",
]


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


def _sample_recheck(pair: dict) -> dict:
    recheck = _run_paired_pytest(pair["polluter"], pair["polluted"])
    return {
        "first_bucket": pair["bucket"],
        "recheck_bucket": recheck["bucket"],
        "consistent": pair["bucket"] == recheck["bucket"],
    }


def _emit_per_polluter_md(polluter: str, result: dict, recheck: dict,
                          disposition: str) -> Path:
    slug = polluter.replace("/", "__").replace(".py", "")
    p = B2_DIR / f"{slug}.md"
    lines: list[str] = []
    lines.append("**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE.md §2.3` "
                 "(post-A+D B.2 remeasure)")
    lines.append("")
    lines.append(f"# B.2 remeasure · `{polluter}`")
    lines.append("")
    lines.append(f"- **Polluted file**: `{POLLUTED}`")
    lines.append(f"- **Pre-A+D bucket**: `CONFIRMED_POLLUTER` (from P5.7-HOLDOUT-FINISHER)")
    lines.append(f"- **Post-A+D bucket**: `{result['bucket']}` "
                 f"({result['duration_s']} s · exit {result['returncode']})")
    lines.append(f"- **Sample-recheck bucket**: `{recheck['recheck_bucket']}` · "
                 f"consistent: **{recheck['consistent']}**")
    lines.append(f"- **Disposition**: **{disposition}**")
    lines.append(f"- **Locked area polluter?**: "
                 f"{'🟥 YES (HALT)' if _locked_area_polluter(polluter) else 'no'}")
    lines.append("")
    lines.append("## Reproduction command")
    lines.append("```bash")
    lines.append(f"cd /app/backend && python -m pytest {polluter} {POLLUTED} "
                 f"-q --no-header --tb=short -m '{PYTEST_MARKERS}' -p no:cacheprovider")
    lines.append("```")
    lines.append("")
    lines.append("## STDOUT tail (post-A+D run)")
    lines.append("```")
    lines.append(result["stdout_tail"])
    lines.append("```")
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


def main() -> int:
    print(f"== B.2 Remeasure · post-A+D · {TS} ==")
    print(f"   Polluted file : `{POLLUTED}`")
    print(f"   Pre-A+D polluter count: {len(POLLUTERS_PRE_A_D)}")
    print(f"   Per-pair timeout: {PYTEST_TIMEOUT_S}s · Wall halt: {WALL_HALT_S}s")
    print()

    disappeared: list[dict] = []
    remaining: list[dict] = []
    inconclusive: list[dict] = []
    halt_flags: list[dict] = []
    locked_area_polluters: list[str] = []
    start_run = time.monotonic()

    for i, polluter in enumerate(POLLUTERS_PRE_A_D, start=1):
        if time.monotonic() - start_run > WALL_HALT_S:
            halt_flags.append({
                "reason": "wall_runtime_exceeded_30min",
                "elapsed_s": round(time.monotonic() - start_run, 0),
            })
            print(f"   [HALT] wall runtime exceeded — stopping sweep")
            break

        if _locked_area_polluter(polluter):
            locked_area_polluters.append(polluter)
            halt_flags.append({
                "reason": "locked_area_polluter",
                "polluter": polluter,
            })

        result = _run_paired_pytest(polluter, POLLUTED)
        # Sample-recheck for subprocess-inconsistency guard
        recheck = _sample_recheck(result)
        if not recheck["consistent"]:
            halt_flags.append({
                "reason": "pytest_subprocess_inconsistency",
                "polluter": polluter,
                "first": recheck["first_bucket"],
                "recheck": recheck["recheck_bucket"],
            })
            disposition = "INCONCLUSIVE (subprocess inconsistency)"
            inconclusive.append({"polluter": polluter, "result": result, "recheck": recheck})
        elif result["bucket"] == "CONFIRMED_POLLUTER":
            disposition = "REMAINING"
            remaining.append({"polluter": polluter, "result": result})
        elif result["bucket"] == "BOTH_PASSED":
            disposition = "DISAPPEARED"
            disappeared.append({"polluter": polluter, "result": result})
        else:
            disposition = f"INCONCLUSIVE ({result['bucket']})"
            inconclusive.append({"polluter": polluter, "result": result, "recheck": recheck})

        md_path = _emit_per_polluter_md(polluter, result, recheck, disposition)
        print(f"   [{i:>2}/{len(POLLUTERS_PRE_A_D)}] [{disposition:<35}] "
              f"{result['duration_s']:>5.1f}s  {polluter}")

    elapsed = time.monotonic() - start_run

    # ── Consolidated delta report ───
    idx_path = OUT_DIR / f"b2_remeasure_{TS}.md"
    lines: list[str] = []
    lines.append("**Canonical Spec**: `/app/memory/sprints/P5_7_FIX_SCOPE.md §2.3` "
                 "(B.2 inter-cluster measurement procedure — post-A+D · READ-ONLY · HARD STOP at index emission)")
    lines.append("")
    lines.append(f"# B.2 Remeasure · Post-A+D · {TS}")
    lines.append("")
    lines.append(f"**Slice**: `/app/backend/scripts/jc_pollution_b2_remeasure_slice.py` "
                 "(READ-ONLY by contract; 0 LOC mutated).")
    lines.append("")
    lines.append(f"**Wall time**: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    lines.append(f"**Per-pair timeout**: {PYTEST_TIMEOUT_S}s")
    lines.append("")
    lines.append("## Headline measurement")
    lines.append("")
    lines.append(f"- **Pre-A+D polluter count (P5.7-HOLDOUT-FINISHER)**: {len(POLLUTERS_PRE_A_D)}")
    lines.append(f"- **Post-A+D polluter count (this sweep, REMAINING)**: {len(remaining)}")
    lines.append(f"- **Disappeared (downstream of A+D's env / loop-policy leak)**: {len(disappeared)}")
    lines.append(f"- **Inconclusive (timeout / subprocess inconsistency / OTHER)**: {len(inconclusive)}")
    lines.append("")
    lines.append("**B.2 fix-sprint scope sized on real evidence**: "
                 f"{len(remaining)} genuine polluters (not the original 15-polluter hypothesis).")
    lines.append("")
    lines.append("## Disappeared polluters (closed-by-A+D)")
    lines.append("")
    if not disappeared:
        lines.append("_(none — every pre-A+D polluter still pollutes post-A+D; B.2's scope is unchanged at 15)_")
    else:
        lines.append("These polluters PASSED when paired with the autosave file post-A+D. "
                     "Their pre-A+D pollution was downstream of A+D's `load_dotenv` env-leak "
                     "and/or `asyncio.run` loop-policy mutation. **A+D's surgical patches "
                     "close them at source.**")
        lines.append("")
        for d in disappeared:
            lines.append(f"- `{d['polluter']}` → post-A+D `{d['result']['bucket']}` "
                         f"({d['result']['duration_s']}s)")
    lines.append("")
    lines.append("## Remaining polluters (genuine B.2 scope)")
    lines.append("")
    if not remaining:
        lines.append("_(none — A+D closed all 15 pre-A+D polluters; B.2 fix sprint is unnecessary)_")
    else:
        lines.append("These polluters STILL pollute the autosave file post-A+D. Their pollution "
                     "is INDEPENDENT of A+D's env/loop-policy leak. **These size B.2's actual "
                     "fix-sprint scope.**")
        lines.append("")
        for r in remaining:
            lines.append(f"- `{r['polluter']}` → still `CONFIRMED_POLLUTER` "
                         f"({r['result']['duration_s']}s)")
    lines.append("")
    lines.append("## Inconclusive results")
    lines.append("")
    if not inconclusive:
        lines.append("_(none — clean sweep)_")
    else:
        lines.append("Excluded from disappeared/remaining counts per discipline (sample-recheck "
                     "inconsistency or timeout). NOT evidence either way; fix sprint should re-run "
                     "these in isolation before sizing scope.")
        lines.append("")
        for i in inconclusive:
            lines.append(f"- `{i['polluter']}` → `{i['result']['bucket']}` "
                         f"(recheck: `{i['recheck']['recheck_bucket']}` · "
                         f"consistent: {i['recheck']['consistent']})")
    lines.append("")
    lines.append("## Halt-and-surface conditions")
    lines.append("")
    if not halt_flags:
        lines.append("_(none — all clear)_")
    else:
        for hf in halt_flags:
            lines.append(f"- 🟥 **{hf.get('reason')}**: `{hf}`")
    lines.append("")
    lines.append("## Per-polluter evidence")
    lines.append("")
    lines.append(f"Each polluter's per-pair MD lives at "
                 f"`{B2_DIR.relative_to(REPO)}/<polluter>.md`.")
    lines.append("")
    lines.append("## Discipline notes")
    lines.append("")
    lines.append("- READ-ONLY by contract: 0 test / fixture / product LOC mutated.")
    lines.append("- Same harness as `jc_pollution_holdout_finisher_slice.py` "
                 "(30 s per-pair timeout, sample-recheck on each confirmed pair).")
    lines.append("- Subprocess-inconsistency guard fires per discipline; inconsistent pairs "
                 "are NOT counted as evidence either way.")
    lines.append("- HARD STOP at index emission — no fix-coding triggered.")
    lines.append("")
    lines.append("## Implication for next dispatch")
    lines.append("")
    if not remaining and not inconclusive:
        lines.append("**B.2 fix sprint is UNNECESSARY** — A+D closed all 15 pre-A+D polluters. "
                     "Proceed directly to B.1 fix sprint dispatch.")
    elif len(remaining) == len(POLLUTERS_PRE_A_D):
        lines.append("**B.2 fix sprint scope is UNCHANGED at 15 polluters** — A+D had zero "
                     "delta on autosave. B.2 dispatch proceeds with original scope memo §2.2 plan.")
    else:
        lines.append(f"**B.2 fix sprint scope is REDUCED from 15 → {len(remaining)} polluters**. "
                     f"A+D closed {len(disappeared)} polluters at source. B.2 dispatch "
                     "should size its autouse-fixture hardening to the residual {len(remaining)} "
                     "polluters' actual mutation surface (each one's per-polluter MD lists "
                     "their concrete failure shape).")

    idx_path.write_text("\n".join(lines), encoding="utf-8")

    print()
    print(f"== B.2 Remeasure done in {elapsed:.0f}s ({elapsed/60:.1f} min) ==")
    print(f"   Pre-A+D polluter count : {len(POLLUTERS_PRE_A_D)}")
    print(f"   Disappeared (closed-by-A+D) : {len(disappeared)}")
    print(f"   Remaining (genuine B.2 scope) : {len(remaining)}")
    print(f"   Inconclusive : {len(inconclusive)}")
    print(f"   Halt flags : {len(halt_flags)}")
    print(f"   Index: {idx_path.relative_to(REPO)}")

    return 1 if halt_flags else 0


if __name__ == "__main__":
    sys.exit(main())
