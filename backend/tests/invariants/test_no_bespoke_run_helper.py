"""INVARIANT — no bespoke `_run` helper or unguarded `asyncio.run` in test bodies.

Canonical Spec: /app/memory/sprints/P5_7_FIX_SCOPE_CLUSTER_F.md §1.1
                (Cluster-F closes 14 existing polluter files using
                this anti-pattern; this invariant prevents the
                anti-pattern from re-introducing itself in NEW test
                files going forward)
Sprint memo:    /app/memory/sprints/INVARIANT_NO_BESPOKE_RUN_HELPER.md
Twin slice:     backend/scripts/jc_invariant_bespoke_run_helper_slice.py
                (classifier proving-slice + baseline scanner)

This invariant fails the build if any test file in `backend/tests/`
introduces one of two anti-patterns without exemption:

  M1 — Module-level helper:
       `def _run(coro): return asyncio.get_event_loop()
        .run_until_complete(coro)`
       Wrong-loop-binding mechanism (Cluster-E / Cluster-F root cause).

  M2 — Direct `asyncio.run(...)` call inside a test_* function body
       Policy-mutation mechanism (A+D-style env+loop-policy leak).

Two-tier exemption mechanism (same shape as thin-assertion guard):

  (a) **File-based grandfather list** at
      `backend/tests/invariants/bespoke_run_helper_grandfathered.yml` —
      seeded at invariant ship time with the 13 M1 + 28 M2 sites
      the baseline scan surfaced. Entries roll up to Cluster-F sub-
      sprints (F.3, F.4, F.5, F.6) for closure; sites NOT in Cluster-F
      scope are tagged "Cluster-G (post-F)" for future dispatch.

  (b) **In-source marker** — `@pytest.mark.acceptable_bespoke_run`
      decorator + a `# reason:` comment within 3 lines of the offending
      call / helper def. For genuinely intentional uses (e.g. pure-Python
      coroutine that has no Motor I/O and is verified loop-isolated).

Removing an entry from the YAML is a deliberate close-out: the test
was converted to async or the asyncio.run was justified-and-marked.
The companion drift detector (`test_grandfather_list_does_not_drift`)
FAILS the build if a YAML entry no longer matches a live anti-pattern
— stale entry == audit drift.
"""
from __future__ import annotations

import ast
import pathlib
from typing import Iterable

import pytest

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover
    yaml = None  # type: ignore[assignment]


REPO = pathlib.Path(__file__).resolve().parents[3]
BACKEND = REPO / "backend"
TESTS_DIR = BACKEND / "tests"
GRANDFATHER_FILE = TESTS_DIR / "invariants" / "bespoke_run_helper_grandfathered.yml"

ACCEPTABLE_MARKER = "acceptable_bespoke_run"
REASON_PREFIX = "# reason:"


# ─────────────────────────────────────────────────────────────────────
# Classifier
# ─────────────────────────────────────────────────────────────────────

def _is_run_helper_def(node: ast.AST) -> bool:
    """Match `def _run(coro): return asyncio.get_event_loop()
    .run_until_complete(coro)` at module level."""
    if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        return False
    if node.name != "_run":
        return False
    # Walk the function body looking for asyncio.get_event_loop().run_until_complete
    for sub in ast.walk(node):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
            if sub.func.attr == "run_until_complete":
                # Verify the receiver is asyncio.get_event_loop() call
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


def _find_asyncio_run_in_test_body(
    fn: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[int]:
    """Return list of linenos of `asyncio.run(...)` calls within fn body."""
    hits: list[int] = []
    for sub in ast.walk(fn):
        if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Attribute):
            if (
                sub.func.attr == "run"
                and isinstance(sub.func.value, ast.Name)
                and sub.func.value.id == "asyncio"
            ):
                hits.append(sub.lineno)
    return hits


def _has_acceptable_marker(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for dec in fn.decorator_list:
        if (
            isinstance(dec, ast.Attribute)
            and dec.attr == ACCEPTABLE_MARKER
            and isinstance(dec.value, ast.Attribute)
            and dec.value.attr == "mark"
        ):
            return True
        if (
            isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Attribute)
            and dec.func.attr == ACCEPTABLE_MARKER
        ):
            return True
    return False


def _has_reason_comment_near(text: str, lineno: int) -> bool:
    lines = text.splitlines()
    start = max(0, lineno - 4)
    for i in range(start, min(len(lines), lineno)):
        if REASON_PREFIX in lines[i]:
            return True
    return False


# ─────────────────────────────────────────────────────────────────────
# Grandfather list loader
# ─────────────────────────────────────────────────────────────────────

def _load_grandfather() -> tuple[set[str], set[tuple[str, str, int]]]:
    """Return (M1 grandfather file set, M2 grandfather (file, func, lineno) set)."""
    if yaml is None:
        return set(), set()
    if not GRANDFATHER_FILE.exists():
        return set(), set()
    data = yaml.safe_load(GRANDFATHER_FILE.read_text(encoding="utf-8")) or {}
    m1: set[str] = set()
    for entry in (data.get("m1_entries") or []):
        f = entry.get("file") or ""
        if f:
            m1.add(f)
    m2: set[tuple[str, str, int]] = set()
    for entry in (data.get("m2_entries") or []):
        f = entry.get("file") or ""
        fn = entry.get("func") or ""
        ln = entry.get("lineno") or 0
        if f and fn:
            m2.add((f, fn, int(ln)))
    return m1, m2


# ─────────────────────────────────────────────────────────────────────
# File walker
# ─────────────────────────────────────────────────────────────────────

def _iter_test_files() -> Iterable[pathlib.Path]:
    for p in sorted(TESTS_DIR.rglob("test_*.py")):
        if "/invariants/" in str(p):
            continue
        if "__pycache__" in p.parts:
            continue
        yield p


def _scan_file(p: pathlib.Path) -> tuple[list[dict], list[dict]]:
    """Return (m1_findings, m2_findings) for one file."""
    m1_findings: list[dict] = []
    m2_findings: list[dict] = []
    try:
        src = p.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return m1_findings, m2_findings
    try:
        tree = ast.parse(src, filename=str(p))
    except SyntaxError:
        return m1_findings, m2_findings
    rel = str(p.relative_to(REPO))
    # M1 — module-level _run helper
    for node in tree.body:
        if _is_run_helper_def(node):
            m1_findings.append({
                "file": rel,
                "lineno": node.lineno,
            })
    # M2 — asyncio.run() in test_* function body
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        marker_exempt = (
            _has_acceptable_marker(node)
            and _has_reason_comment_near(src, node.lineno)
        )
        for hit_lineno in _find_asyncio_run_in_test_body(node):
            m2_findings.append({
                "file": rel,
                "func": node.name,
                "lineno": hit_lineno,
                "marker_exempt": marker_exempt,
            })
    return m1_findings, m2_findings


# ─────────────────────────────────────────────────────────────────────
# Invariant body
# ─────────────────────────────────────────────────────────────────────

def test_no_bespoke_run_helper_in_tests():
    """Build-breaking guard: no NEW bespoke `_run` helper or unguarded
    `asyncio.run(...)` in test bodies.

    Allowed exits:
      - File-based grandfather list at `bespoke_run_helper_grandfathered.yml`
        (legacy entries, Cluster-F sub-sprint follow-up)
      - In-source `@pytest.mark.acceptable_bespoke_run` + `# reason:`

    Any other site FAILS the build with a clear pointer to the
    rewrite-or-allowlist decision.
    """
    if yaml is None:
        pytest.skip("PyYAML not installed; cannot read grandfather list")

    m1_grand, m2_grand = _load_grandfather()
    m1_violations: list[dict] = []
    m2_violations: list[dict] = []

    for p in _iter_test_files():
        m1_hits, m2_hits = _scan_file(p)
        for f in m1_hits:
            if f["file"] in m1_grand:
                continue
            m1_violations.append(f)
        for f in m2_hits:
            key = (f["file"], f["func"], f["lineno"])
            if key in m2_grand:
                continue
            if f["marker_exempt"]:
                continue
            m2_violations.append(f)

    if m1_violations or m2_violations:
        lines = [
            "",
            "🟥 Bespoke `_run` / `asyncio.run` guard tripped.",
            "",
            "Each finding is one of:",
            "  M1. module-level `def _run(coro): return asyncio.get_event_loop()"
            ".run_until_complete(coro)` helper",
            "  M2. `asyncio.run(...)` call inside a test_* function body",
            "",
            "Both patterns risk binding Motor / FastAPI middleware to a loop",
            "different from the pytest-asyncio session-scoped event loop, which",
            "causes `RuntimeError: Future attached to a different loop` in",
            "downstream async tests (Cluster-E + Cluster-F root cause).",
            "",
            "Resolution options:",
            "  (1) Convert the test to `@pytest.mark.asyncio + async def`",
            "      and use `await coro` instead of the helper (preferred).",
            "  (2) Add the entry to `backend/tests/invariants/"
            "bespoke_run_helper_grandfathered.yml` (legacy carryover only).",
            "  (3) Mark the offending test with",
            "      `@pytest.mark.acceptable_bespoke_run` + `# reason: ...`",
            "      comment within 3 lines of the def (M2 only — M1 helper",
            "      cannot use the in-source marker; the helper itself isn't",
            "      a test function).",
            "",
        ]
        if m1_violations:
            lines.append("M1 findings (`def _run` helper):")
            for v in m1_violations:
                lines.append(f"  [M1] {v['file']}:{v['lineno']}")
            lines.append("")
        if m2_violations:
            lines.append("M2 findings (`asyncio.run` in test body):")
            for v in m2_violations:
                lines.append(
                    f"  [M2] {v['file']}:{v['lineno']} {v['func']}()"
                )
        pytest.fail("\n".join(lines))


def test_grandfather_list_does_not_drift():
    """Soft guard: every entry in the grandfather list MUST still
    match a live anti-pattern on disk. If an entry no longer triggers
    the classifier, the file has been converted — surface so the
    entry can be deleted from the YAML.
    """
    if yaml is None:
        pytest.skip("PyYAML not installed; cannot read grandfather list")

    m1_grand, m2_grand = _load_grandfather()
    if not m1_grand and not m2_grand:
        return

    live_m1: set[str] = set()
    live_m2: set[tuple[str, str, int]] = set()
    for p in _iter_test_files():
        m1_hits, m2_hits = _scan_file(p)
        for f in m1_hits:
            live_m1.add(f["file"])
        for f in m2_hits:
            live_m2.add((f["file"], f["func"], f["lineno"]))

    stale_m1 = sorted(m1_grand - live_m1)
    stale_m2 = sorted(m2_grand - live_m2)

    if stale_m1 or stale_m2:
        lines = [
            "",
            "🟧 Bespoke-run grandfather list drift — these entries no longer ",
            "match a live anti-pattern (file converted to async or marker added):",
            "",
        ]
        if stale_m1:
            lines.append("Stale M1 entries:")
            for f in stale_m1:
                lines.append(f"  {f}")
            lines.append("")
        if stale_m2:
            lines.append("Stale M2 entries:")
            for f, fn, ln in stale_m2:
                lines.append(f"  {f}:{ln} {fn}()")
            lines.append("")
        lines.append(
            "Remove these entries from "
            "`backend/tests/invariants/bespoke_run_helper_grandfathered.yml`."
        )
        pytest.fail("\n".join(lines))


# ─────────────────────────────────────────────────────────────────────
# Count-ceiling enforcement (Step 4 — same shape as thin-assertion
# guard but added here to lock the Cluster-F closure schedule)
# ─────────────────────────────────────────────────────────────────────

# Hard ceiling: M1 entries must be <= 5 (post-F.3 baseline). M2
# entries must be <= 26 (post-F.6 baseline, ratcheted down from
# 28 → 26 by F.6's 2-site close). Cluster-F is now COMPLETE; both
# ceilings will only ratchet down from here as Cluster-G sub-sprints
# ship. The ceiling LOCKS the trajectory; a new addition to either
# YAML section pushes the count past the ceiling and fails the build.
M1_CEILING = 0
M2_CEILING = 26


def test_grandfather_count_below_ceiling():
    """Hard ceiling: grandfather YAML cannot quietly grow past the
    seeded baseline. New polluters must be either:
      - converted (preferred — Cluster-F mechanical pattern)
      - or marked with `@pytest.mark.acceptable_bespoke_run` + `# reason:`

    Never silently added to the YAML.
    """
    if yaml is None:
        pytest.skip("PyYAML not installed; cannot read grandfather list")

    m1_grand, m2_grand = _load_grandfather()

    failures: list[str] = []
    if len(m1_grand) > M1_CEILING:
        failures.append(
            f"M1 grandfather count {len(m1_grand)} exceeds ceiling {M1_CEILING}. "
            "New M1 polluter detected — convert to async (preferred) or justify."
        )
    if len(m2_grand) > M2_CEILING:
        failures.append(
            f"M2 grandfather count {len(m2_grand)} exceeds ceiling {M2_CEILING}. "
            "New M2 polluter detected — convert to async (preferred) or "
            "mark with @pytest.mark.acceptable_bespoke_run + # reason:."
        )

    if failures:
        pytest.fail("\n".join(["", "🟥 Bespoke-run grandfather ceiling breached.", ""] + failures))
