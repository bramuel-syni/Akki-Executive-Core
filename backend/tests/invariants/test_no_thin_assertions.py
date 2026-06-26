"""INVARIANT — no thin assertions in test bodies.

Canonical Spec: /app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md
                (structural enforcement: a rig fix that greens a test
                which asserts nothing is worse than the red — it hides
                the gap)
Sprint memo:    /app/memory/sprints/INVARIANT_NO_THIN_ASSERTIONS.md
Twin slice:     backend/scripts/jc_invariant_thin_assertions_slice.py
                (classifier proving-slice + baseline scanner)

This invariant fails the build if any test function in
`backend/tests/` matches one of the THIN_PATTERNS (T1..T5):

  T1. `try: pass` (no assertion inside the try body)
  T2. body == `pass` (with optional docstring)
  T3. `assert <constant>` (e.g. `assert True`)
  T4. body contains only `pytest.skip(...)`
  T5. docstring-only body

Two-tier exemption mechanism:

  (a) **File-based grandfather list** at
      `backend/tests/invariants/thin_assertions_grandfathered.yml` —
      seeded at invariant ship time with the 9 entries the baseline
      scan surfaced. Entries roll up to FTT-027..035 in
      `FAILING_TEST_TRACKER.md` for individual rewrite. Removing an
      entry is a deliberate close-out.

  (b) **In-source marker** — `@pytest.mark.acceptable_thin_assertion`
      decorator + a `# reason:` comment within 3 lines of the `def`.
      For genuinely intentional thin assertions (import-side-effect
      checks, etc.). Adding the marker requires a sprint memo
      justification — surface in code review.

Tier (a) is the audit trail for legacy entries; tier (b) is the
forward-going policy for new tests. Both are deliberate exemptions
with a paper trail.
"""
from __future__ import annotations

import ast
import pathlib
from typing import Iterable

import pytest

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover — bail with a clear message
    yaml = None  # type: ignore[assignment]


REPO = pathlib.Path(__file__).resolve().parents[3]
BACKEND = REPO / "backend"
TESTS_DIR = BACKEND / "tests"
GRANDFATHER_FILE = TESTS_DIR / "invariants" / "thin_assertions_grandfathered.yml"

ACCEPTABLE_MARKER = "acceptable_thin_assertion"
REASON_PREFIX = "# reason:"


# ─────────────────────────────────────────────────────────────────────
# Classifier (mirrors backend/scripts/jc_invariant_thin_assertions_slice.py)
# ─────────────────────────────────────────────────────────────────────

def _strip_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        return body[1:]
    return body


def _only_pass(body: list[ast.stmt]) -> bool:
    stripped = _strip_docstring(body)
    return len(stripped) == 1 and isinstance(stripped[0], ast.Pass)


def _try_pass_only(body: list[ast.stmt]) -> bool:
    stripped = _strip_docstring(body)
    if not stripped:
        return False
    for node in stripped:
        if isinstance(node, ast.Try):
            inner = _strip_docstring(node.body)
            if len(inner) == 1 and isinstance(inner[0], ast.Pass):
                return True
            break
    return False


def _bare_assert_constant(body: list[ast.stmt]) -> tuple[bool, str]:
    stripped = _strip_docstring(body)
    if len(stripped) != 1 or not isinstance(stripped[0], ast.Assert):
        return False, ""
    test = stripped[0].test
    if isinstance(test, ast.Constant):
        return True, f"assert {test.value!r}"
    return False, ""


def _only_pytest_skip(body: list[ast.stmt]) -> bool:
    stripped = _strip_docstring(body)
    if len(stripped) != 1:
        return False
    stmt = stripped[0]
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        call = stmt.value
        if (
            isinstance(call.func, ast.Attribute)
            and call.func.attr == "skip"
            and isinstance(call.func.value, ast.Name)
            and call.func.value.id == "pytest"
        ):
            return True
    return False


def _docstring_only(body: list[ast.stmt]) -> bool:
    return (
        len(body) == 1
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    )


def classify(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str | None, str]:
    body = fn.body
    if _docstring_only(body):
        return "T5", "docstring-only body"
    if _only_pass(body):
        return "T2", "body == pass"
    if _try_pass_only(body):
        return "T1", "try: pass (no assertion inside)"
    ok, evidence = _bare_assert_constant(body)
    if ok:
        return "T3", evidence
    if _only_pytest_skip(body):
        return "T4", "only pytest.skip(...)"
    return None, ""


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


def _has_reason_comment_near(text: str, fn_lineno: int) -> bool:
    lines = text.splitlines()
    start = max(0, fn_lineno - 4)
    for i in range(start, min(len(lines), fn_lineno)):
        if REASON_PREFIX in lines[i]:
            return True
    return False


# ─────────────────────────────────────────────────────────────────────
# Grandfather list loader
# ─────────────────────────────────────────────────────────────────────

def _load_grandfather() -> set[tuple[str, str]]:
    """Return {(file_relpath, func_name)} for every grandfathered entry."""
    if yaml is None:
        return set()
    if not GRANDFATHER_FILE.exists():
        return set()
    data = yaml.safe_load(GRANDFATHER_FILE.read_text(encoding="utf-8")) or {}
    out: set[tuple[str, str]] = set()
    for entry in (data.get("entries") or []):
        f = entry.get("file") or ""
        fn = entry.get("func") or ""
        if f and fn:
            out.add((f, fn))
    return out


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


def _scan_file(p: pathlib.Path) -> list[dict]:
    findings: list[dict] = []
    try:
        src = p.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return findings
    try:
        tree = ast.parse(src, filename=str(p))
    except SyntaxError:
        # Defer to dedicated syntax-error invariants.
        return findings
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not node.name.startswith("test_"):
            continue
        pattern, evidence = classify(node)
        if pattern is None:
            continue
        marker_exempt = (
            _has_acceptable_marker(node)
            and _has_reason_comment_near(src, node.lineno)
        )
        findings.append({
            "file": str(p.relative_to(REPO)),
            "func": node.name,
            "lineno": node.lineno,
            "pattern": pattern,
            "evidence": evidence,
            "marker_exempt": marker_exempt,
        })
    return findings


# ─────────────────────────────────────────────────────────────────────
# Invariant body
# ─────────────────────────────────────────────────────────────────────

def test_no_thin_assertions_in_tests():
    """Build-breaking guard: no thin-assertion test functions allowed.

    Allowed exits:
      - File-based grandfather list at `thin_assertions_grandfathered.yml`
        (legacy entries, FTT-027..035 follow-up)
      - In-source `@pytest.mark.acceptable_thin_assertion` + `# reason:`

    Any other thin-assertion test FAILS the build with a clear pointer
    to the rewrite-or-allowlist decision.
    """
    if yaml is None:
        pytest.skip("PyYAML not installed; cannot read grandfather list")

    grandfathered = _load_grandfather()
    violations: list[dict] = []

    for p in _iter_test_files():
        for f in _scan_file(p):
            key = (f["file"], f["func"])
            if key in grandfathered:
                continue
            if f["marker_exempt"]:
                continue
            violations.append(f)

    if violations:
        lines = [
            "",
            "🟥 Thin-assertion guard tripped — these tests assert nothing.",
            "",
            "Each finding is one of:",
            "  T1. try: pass (no assertion inside)",
            "  T2. body == pass (with optional docstring)",
            "  T3. assert <constant>",
            "  T4. only pytest.skip(...)",
            "  T5. docstring-only body",
            "",
            "Resolution options:",
            "  (1) Rewrite the test with a real assertion (preferred).",
            "  (2) Add the entry to `backend/tests/invariants/"
            "thin_assertions_grandfathered.yml` (legacy carryover only).",
            "  (3) Mark the test with `@pytest.mark.acceptable_thin_assertion`"
            " and add a `# reason: ...` comment within 3 lines of the def.",
            "",
            "Findings:",
        ]
        for v in violations:
            lines.append(f"  [{v['pattern']}] {v['file']}:{v['lineno']} "
                         f"{v['func']}() — {v['evidence']}")
        pytest.fail("\n".join(lines))


def test_grandfather_list_does_not_drift():
    """Soft guard: every entry in the grandfather list MUST still
    exist on disk as a real test function with a thin-assertion
    body. If an entry no longer triggers the classifier, the test
    has been rewritten or removed — surface so the entry can be
    deleted from the YAML.

    This is a build-failing assertion: a stale grandfather entry is
    audit drift.
    """
    if yaml is None:
        pytest.skip("PyYAML not installed; cannot read grandfather list")

    grandfathered = _load_grandfather()
    if not grandfathered:
        return  # nothing to check

    # Index of (file, func) → pattern from a fresh scan.
    live: dict[tuple[str, str], str] = {}
    for p in _iter_test_files():
        for f in _scan_file(p):
            live[(f["file"], f["func"])] = f["pattern"]

    stale: list[tuple[str, str]] = []
    for entry in sorted(grandfathered):
        if entry not in live:
            stale.append(entry)

    if stale:
        lines = [
            "",
            "🟧 Grandfather list drift — these entries no longer trigger "
            "the thin-assertion classifier (test rewritten or removed):",
            "",
        ]
        for f, fn in stale:
            lines.append(f"  {f} :: {fn}")
        lines.append("")
        lines.append("Remove these entries from "
                     "`backend/tests/invariants/thin_assertions_grandfathered.yml`.")
        pytest.fail("\n".join(lines))
