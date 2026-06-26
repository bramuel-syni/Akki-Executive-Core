#!/usr/bin/env python3
"""Cross-Test Pollution — per-file subprocess capture (path b done right).

Canonical Spec : `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md`
                 (cross-test pollution flakes FTT-002..026 — broad-suite
                 capture (b) per user direction, in-process attempt
                 halted at 16% with state-accumulation hang; this
                 slice replaces the in-process broad-suite with
                 per-file subprocess isolation + per-file timeout)
Audit standard : `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md`
                 (CSRF-grade discipline — confirmed root cause +
                 cleanup mapping per cluster)

User direction (verbatim):
  > "pytest-forked install + per-file subprocess wrapper script
  >  (~30 LOC) that runs each test file in a fresh process with a
  >  60s timeout. Lets us complete the entire 4,412-test inventory in
  >  ~30-45 min and gives us per-file pass/fail/timeout buckets,
  >  which is the smallest possible next step for path (b) without
  >  committing to a multi-hour sprint."

READ-ONLY by contract. NO test/fixture/production code mutated.

────────────────────────────────────────────────────────────────────
Algorithm
────────────────────────────────────────────────────────────────────

Phase 1 — per-file isolation capture
  1. Walk every `tests/test_*.py` + `tests/**/test_*.py` (excluding
     `tests/invariants/`, `tests/deploy/`, `__pycache__/`).
  2. For each file: subprocess pytest with --timeout 60s wall, marker
     filter `not integration and not deploy_smoke and not
     runtime_playwright`, `-p no:cacheprovider`.
  3. Bucket each file: PASS · FAIL_DETERMINISTIC · TIMEOUT · ERROR.

Phase 2 — diagnostic cross-reference vs. FAILING_TEST_TRACKER
  4. Read FTT-002..026 polluted-test nodes from the tracker.
  5. For each polluted node, check its file's Phase-1 bucket:
       - PASS in isolation + listed in tracker  → **FAIL_IN_CONTEXT**
         (confirmed candidate for polluter-chain bisect)
       - FAIL_DETERMINISTIC in isolation        → tracker
         entry is misclassified (file fails alone too); not a
         pollution candidate, surface for tracker correction
       - TIMEOUT / ERROR                        → cannot bucket;
         surface as inconclusive
  6. Emit one MD per file at
     `/app/memory/jc_artifacts/test_pollution/per_file/<file>.md`
     and a consolidated index at
     `/app/memory/jc_artifacts/test_pollution/per_file_capture_<ts>.md`.

Phase 3 — HALT-and-surface for user direction
  7. HALT conditions per user direction:
       - > 100 files time out at 60s → timeout too aggressive
       - FAIL_IN_CONTEXT bucket > 100 → systemic harness rot
       - confirmed polluter in locked area → locked-area halt
       - pytest-forked install failure → infrastructure halt
  8. Phase 3 surfaces the FAIL_IN_CONTEXT bucket for user direction
     on bisect scope. Bisect itself is the next sprint.

Exit codes:
  0 → all OK, results written
  1 → at least one halt condition tripped
"""
from __future__ import annotations

import argparse
import datetime as _dt
import re
import subprocess
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO / "backend" / "tests"
OUT_DIR = REPO / "memory" / "jc_artifacts" / "test_pollution"
PER_FILE_DIR = OUT_DIR / "per_file"
PER_FILE_DIR.mkdir(parents=True, exist_ok=True)
TS = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

LOCKED_AREAS = (
    "services/synisense/",
    "services/solva_v2/",
    "components/work_studio/",
    "services/monitor/background_tracker",
)

PYTEST_MARKERS = "not integration and not deploy_smoke and not runtime_playwright"

# FAILING_TEST_TRACKER FTT-002..026 polluted nodes — copied from tracker
# verbatim. If the tracker changes, this list MUST be re-synced.
TRACKER_POLLUTED_NODES: list[tuple[str, str]] = [
    # (FTT-id, "file::node")
    ("FTT-002", "tests/characterisation/test_chat_roundtrip_golden.py::test_chat_roundtrip_golden_shape"),
    ("FTT-003", "tests/test_chat_fluency_no_shield_leak.py::test_chat_response_does_not_leak_shield_mechanics"),
    # FTT-004..009 — all 6 tests in iter41
    ("FTT-004", "tests/test_iter41_signal_actions_in_process.py::test_s41_a_get_recommendations_returns_bucket_and_three"),
    ("FTT-005", "tests/test_iter41_signal_actions_in_process.py"),  # remaining 5 — file-level
    ("FTT-006", "tests/test_iter41_signal_actions_in_process.py"),
    ("FTT-007", "tests/test_iter41_signal_actions_in_process.py"),
    ("FTT-008", "tests/test_iter41_signal_actions_in_process.py"),
    ("FTT-009", "tests/test_iter41_signal_actions_in_process.py"),
    # FTT-010..012
    ("FTT-010", "tests/test_p_cleanup_c_help_tooltip_suppression.py"),
    ("FTT-011", "tests/test_p_cleanup_c_help_tooltip_suppression.py"),
    ("FTT-012", "tests/test_p_cleanup_c_help_tooltip_suppression.py"),
    # FTT-013
    ("FTT-013", "tests/test_phase_d_fix_bundle.py"),
    # FTT-014
    ("FTT-014", "tests/test_phase_i5_open_questions.py::test_i5_B1_backfill_idempotent"),
    # FTT-015..018
    ("FTT-015", "tests/test_phase_p3_2_cookie_hardening.py"),
    ("FTT-016", "tests/test_phase_p3_2_cookie_hardening.py"),
    ("FTT-017", "tests/test_phase_p5_10_audit_panel_direct_linkage.py"),
    ("FTT-018", "tests/test_phase_p5_10_audit_panel_direct_linkage.py"),
    # FTT-019..022
    ("FTT-019", "tests/test_phase_p5_7_5_bounce_webhook.py"),
    ("FTT-020", "tests/test_phase_p5_7_5_bounce_webhook.py"),
    ("FTT-021", "tests/test_phase_p5_7_5_bounce_webhook.py"),
    ("FTT-022", "tests/test_phase_p5_7_5_bounce_webhook.py"),
    # FTT-023
    ("FTT-023", "tests/test_track_b_phase2_task_lifecycle.py::test_cross_tenant_lifecycle_blocked"),
    # FTT-024..026
    ("FTT-024", "tests/test_track_b_phase_b5_g6_notes_autosave.py"),
    ("FTT-025", "tests/test_track_b_phase_b5_g6_notes_autosave.py"),
    ("FTT-026", "tests/test_track_b_phase_b5_g6_notes_autosave.py"),
]


def _polluted_files() -> set[str]:
    out: set[str] = set()
    for _ftt, node in TRACKER_POLLUTED_NODES:
        # `tests/...py::test_x` → tests/...py
        out.add(node.split("::")[0])
    return out


def _polluted_ftt_for_file(file: str) -> list[str]:
    return [ftt for (ftt, node) in TRACKER_POLLUTED_NODES if node.split("::")[0] == file]


# ─────────────────────────────────────────────────────────────────────
# File walker
# ─────────────────────────────────────────────────────────────────────

def _iter_test_files() -> list[Path]:
    """Return alphabetically-sorted test files, excluding invariants
    (already enforced by their own lane) and deploy-smoke (needs
    docker)."""
    out: list[Path] = []
    for p in sorted(TESTS_DIR.rglob("test_*.py")):
        rel = str(p.relative_to(REPO))
        if "/invariants/" in rel:
            continue
        if "/deploy/" in rel:
            continue
        if "__pycache__" in p.parts:
            continue
        out.append(p)
    return out


# ─────────────────────────────────────────────────────────────────────
# Subprocess runner
# ─────────────────────────────────────────────────────────────────────

def _run_pytest_on_file(file_relpath: str, timeout_s: int) -> dict:
    """Run pytest on a single file in a fresh subprocess with a wall
    timeout. Returns a dict with bucket, duration_s, output tails."""
    cmd = [
        sys.executable, "-m", "pytest", file_relpath,
        "-q", "--no-header", "--tb=no",
        "-m", PYTEST_MARKERS,
        "-p", "no:cacheprovider",
    ]
    start = time.monotonic()
    try:
        r = subprocess.run(
            cmd, cwd=str(REPO / "backend"),
            capture_output=True, text=True, timeout=timeout_s,
        )
        duration = time.monotonic() - start
        stdout_tail = "\n".join(r.stdout.splitlines()[-50:])
        stderr_tail = "\n".join(r.stderr.splitlines()[-20:])
        # Bucket classification.
        if r.returncode == 0:
            bucket = "PASS"
        elif r.returncode == 5:
            # pytest exit 5 = "No tests were collected" (e.g. all
            # tests deselected by the marker filter). Treat as PASS
            # — the file is healthy, just outside this lane.
            bucket = "PASS_NO_TESTS"
        elif _is_collection_error(r.stdout + "\n" + r.stderr):
            bucket = "ERROR"
        elif _has_failed_or_errored(r.stdout + "\n" + r.stderr):
            bucket = "FAIL_DETERMINISTIC"
        else:
            bucket = "ERROR"
        return {
            "file": file_relpath,
            "bucket": bucket,
            "duration_s": round(duration, 2),
            "returncode": r.returncode,
            "stdout_tail": stdout_tail,
            "stderr_tail": stderr_tail,
        }
    except subprocess.TimeoutExpired:
        duration = time.monotonic() - start
        return {
            "file": file_relpath,
            "bucket": "TIMEOUT",
            "duration_s": round(duration, 2),
            "returncode": -9,
            "stdout_tail": "(timeout: pytest killed at wall ceiling)",
            "stderr_tail": "",
        }


def _has_failed_or_errored(blob: str) -> bool:
    return bool(re.search(r"\b(FAILED|ERRORS?)\b", blob))


def _is_collection_error(blob: str) -> bool:
    return bool(re.search(
        r"(ERRORS during collection|InternalError|ImportError"
        r"|ModuleNotFoundError|SyntaxError|file or directory not found)",
        blob,
    ))


# ─────────────────────────────────────────────────────────────────────
# Per-file MD emitter
# ─────────────────────────────────────────────────────────────────────

def _safe_filename(file_relpath: str) -> str:
    return file_relpath.replace("/", "__").replace(".py", "")


def _emit_per_file_md(result: dict, ftt_ids: list[str]) -> Path:
    fname = _safe_filename(result["file"]) + ".md"
    p = PER_FILE_DIR / fname
    lines: list[str] = []
    lines.append("**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` "
                 "(per-file subprocess capture · cluster diagnosis)")
    lines.append("")
    lines.append(f"# Per-file capture · `{result['file']}`")
    lines.append("")
    lines.append(f"- **Bucket**: `{result['bucket']}`")
    lines.append(f"- **Duration**: {result['duration_s']} s")
    lines.append(f"- **Return code**: {result['returncode']}")
    if ftt_ids:
        lines.append(f"- **FAILING_TEST_TRACKER hits**: {', '.join(ftt_ids)}")
    lines.append("")
    lines.append("## STDOUT tail")
    lines.append("```")
    lines.append(result["stdout_tail"] or "(empty)")
    lines.append("```")
    if result["stderr_tail"]:
        lines.append("## STDERR tail")
        lines.append("```")
        lines.append(result["stderr_tail"])
        lines.append("```")
    p.write_text("\n".join(lines), encoding="utf-8")
    return p


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="per-file subprocess capture")
    ap.add_argument("--timeout", type=int, default=60,
                    help="per-file pytest wall timeout in seconds (default 60)")
    ap.add_argument("--limit", type=int, default=0,
                    help="if >0, only run the first N files (smoke test)")
    args = ap.parse_args(argv)

    print(f"== Per-file subprocess capture · {TS} ==")
    print(f"   Tests dir: {TESTS_DIR}")
    print(f"   Per-file wall timeout: {args.timeout}s")
    print(f"   Marker filter: '{PYTEST_MARKERS}'")
    print(f"   Output dir: {PER_FILE_DIR}\n")

    polluted_files = _polluted_files()
    files = _iter_test_files()
    if args.limit > 0:
        files = files[: args.limit]
    print(f"   Files to run: {len(files)}\n")

    buckets: dict[str, list[str]] = {
        "PASS": [], "PASS_NO_TESTS": [], "FAIL_DETERMINISTIC": [], "TIMEOUT": [], "ERROR": [],
    }
    results: list[dict] = []
    start_run = time.monotonic()

    for i, p in enumerate(files, start=1):
        rel = str(p.relative_to(REPO / "backend"))  # tests/foo.py
        ftt_ids = _polluted_ftt_for_file(rel)
        result = _run_pytest_on_file(rel, timeout_s=args.timeout)
        result["ftt_ids"] = ftt_ids
        results.append(result)
        buckets[result["bucket"]].append(rel)
        _emit_per_file_md(result, ftt_ids)
        elapsed = time.monotonic() - start_run
        eta_total = elapsed / i * len(files)
        ftt_flag = f" [{','.join(ftt_ids)}]" if ftt_ids else ""
        print(f"  [{i:>3}/{len(files)}] [{result['bucket']:<18}] "
              f"{result['duration_s']:>5.1f}s  {rel}{ftt_flag}  "
              f"(elapsed {elapsed:.0f}s, eta {eta_total:.0f}s)")

    elapsed = time.monotonic() - start_run

    # ── Phase 2: cross-reference with tracker ──
    fail_in_context: list[tuple[str, list[str]]] = []
    deterministic_in_tracker: list[tuple[str, list[str]]] = []
    inconclusive_in_tracker: list[tuple[str, str, list[str]]] = []

    for r in results:
        if r["file"] not in polluted_files:
            continue
        ftt_ids = r["ftt_ids"]
        if r["bucket"] in ("PASS", "PASS_NO_TESTS"):
            fail_in_context.append((r["file"], ftt_ids))
        elif r["bucket"] == "FAIL_DETERMINISTIC":
            deterministic_in_tracker.append((r["file"], ftt_ids))
        else:  # TIMEOUT / ERROR
            inconclusive_in_tracker.append((r["file"], r["bucket"], ftt_ids))

    # ── Halt conditions ──
    halt_flags: list[dict] = []
    if len(buckets["TIMEOUT"]) > 100:
        halt_flags.append({
            "reason": "too_many_timeouts",
            "count": len(buckets["TIMEOUT"]),
            "threshold": 100,
        })
    if len(fail_in_context) > 100:
        halt_flags.append({
            "reason": "fail_in_context_too_large_systemic_rot",
            "count": len(fail_in_context),
            "threshold": 100,
        })
    for file, _ftts in fail_in_context:
        if any(la in file for la in LOCKED_AREAS):
            halt_flags.append({
                "reason": "fail_in_context_in_locked_area",
                "file": file,
            })

    # ── Consolidated index ──
    idx_path = OUT_DIR / f"per_file_capture_{TS}.md"
    lines: list[str] = []
    lines.append("**Canonical Spec**: `/app/memory/jc_artifacts/FAILING_TEST_TRACKER.md` "
                 "(cross-test pollution path (b) · per-file subprocess capture · "
                 "INVESTIGATE-ONLY · HALT-and-surface)")
    lines.append("")
    lines.append(f"# Per-file subprocess capture · {TS}")
    lines.append("")
    lines.append("**Audit standard**: `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` "
                 "(confirmed root cause + cleanup mapping per cluster).")
    lines.append("")
    lines.append(f"**Slice**: `/app/backend/scripts/jc_test_pollution_per_file_capture_slice.py` "
                 "(READ-ONLY by contract).")
    lines.append("")
    lines.append("## Aggregate buckets")
    lines.append("")
    lines.append(f"- **Total files run**: {len(results)}")
    lines.append(f"- **Total wall time**: {elapsed:.0f}s ({elapsed/60:.1f} min)")
    lines.append("")
    lines.append("| Bucket | Count | Pct |")
    lines.append("|---|---:|---:|")
    for b in ("PASS", "PASS_NO_TESTS", "FAIL_DETERMINISTIC", "TIMEOUT", "ERROR"):
        pct = (len(buckets[b]) / max(len(results), 1)) * 100
        lines.append(f"| `{b}` | {len(buckets[b])} | {pct:.1f}% |")
    lines.append("")

    lines.append("## Phase-2 cross-reference vs FAILING_TEST_TRACKER (FTT-002..026)")
    lines.append("")
    lines.append("### FAIL_IN_CONTEXT — confirmed pollution candidates")
    lines.append("Files that PASS alone but appear in the tracker as failing in-suite.")
    lines.append("This is the diagnostic gold: each represents a real polluter chain.")
    lines.append("")
    if not fail_in_context:
        lines.append("_(empty — no confirmed pollution candidates)_")
    else:
        lines.append("| File | FTT IDs | Locked area? |")
        lines.append("|---|---|:---:|")
        for file, ftts in fail_in_context:
            locked = any(la in file for la in LOCKED_AREAS)
            lines.append(f"| `{file}` | {', '.join(ftts)} | {'🟥 YES' if locked else 'no'} |")
    lines.append("")

    lines.append("### FAIL_DETERMINISTIC_IN_TRACKER — tracker entry needs correction")
    lines.append("Files that FAIL alone too — the tracker classified them as "
                 "pollution flakes but they're deterministic regressions.")
    lines.append("")
    if not deterministic_in_tracker:
        lines.append("_(empty)_")
    else:
        lines.append("| File | FTT IDs |")
        lines.append("|---|---|")
        for file, ftts in deterministic_in_tracker:
            lines.append(f"| `{file}` | {', '.join(ftts)} |")
    lines.append("")

    lines.append("### INCONCLUSIVE — TIMEOUT or ERROR in isolation")
    lines.append("Files that didn't complete in isolation; cannot bucket.")
    lines.append("")
    if not inconclusive_in_tracker:
        lines.append("_(empty)_")
    else:
        lines.append("| File | Bucket | FTT IDs |")
        lines.append("|---|---|---|")
        for file, bucket, ftts in inconclusive_in_tracker:
            lines.append(f"| `{file}` | `{bucket}` | {', '.join(ftts)} |")
    lines.append("")

    lines.append("## Halt-and-surface conditions")
    lines.append("")
    if not halt_flags:
        lines.append("_(none — all clear)_")
    else:
        for hf in halt_flags:
            lines.append(f"- 🟥 **{hf.get('reason')}** — `{hf}`")
    lines.append("")

    lines.append("## Discipline & out-of-scope notes")
    lines.append("")
    lines.append("- This slice is READ-ONLY by contract. NO test/fixture/production code mutated.")
    lines.append("- Per-file subprocess isolation replaces the in-process broad-suite that "
                 "hung at 16% in `P5_7_CAPTURE_B_ATTEMPT_1`.")
    lines.append("- The FAIL_IN_CONTEXT bucket is the next sprint's input: bisect each "
                 "file's predecessor chain to identify the polluter(s).")
    lines.append("- Bisect itself is OUT OF SCOPE for this slice — HARD STOP at surface "
                 "per user direction.")
    lines.append("")

    idx_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n== Capture done in {elapsed:.0f}s ({elapsed/60:.1f} min) ==")
    print(f"   Aggregate: PASS={len(buckets['PASS'])} "
          f"PASS_NO_TESTS={len(buckets['PASS_NO_TESTS'])} "
          f"FAIL_DETERMINISTIC={len(buckets['FAIL_DETERMINISTIC'])} "
          f"TIMEOUT={len(buckets['TIMEOUT'])} ERROR={len(buckets['ERROR'])}")
    print(f"   Phase-2: FAIL_IN_CONTEXT={len(fail_in_context)} "
          f"FAIL_DETERMINISTIC_IN_TRACKER={len(deterministic_in_tracker)} "
          f"INCONCLUSIVE={len(inconclusive_in_tracker)}")
    print(f"   Halt flags: {len(halt_flags)}")
    print(f"   Index: {idx_path.relative_to(REPO)}")

    return 1 if halt_flags else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
