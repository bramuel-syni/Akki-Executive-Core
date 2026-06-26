#!/usr/bin/env python3
"""INVARIANT-NO-THIN-ASSERTIONS — proving slice + live-tree scanner.

Canonical Spec : `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md`
                 (structural enforcement of the audit standard: a rig
                 fix that greens a test which asserts nothing is worse
                 than the red — it hides the gap)
Sprint memo    : `/app/memory/sprints/INVARIANT_NO_THIN_ASSERTIONS.md`

This slice has two responsibilities, both READ-ONLY:

  1. **Scan-only mode** (no `--invariant` flag, default): walks every
     `tests/test_*.py` + `tests/**/test_*.py` (excluding `tests/invariants/`
     and `conftest.py`), AST-parses each, and classifies every test
     function body against the THIN_PATTERNS catalog. Output: a
     count + per-finding table written to
     `/app/memory/jc_artifacts/test_pollution/thin_assertions_baseline_<UTC ts>.md`.

  2. **Proving-slice mode** (with `--proving`): verifies the
     classifier itself against synthetic in-memory fixtures (known-bad
     and known-good). Reports pass/fail per fixture pair.

The slice is the *behavioural* twin of the invariant file
(`tests/invariants/test_no_thin_assertions.py`). The invariant uses
the same classifier; this slice exists so the classifier can be
exercised independently from the pytest collection lane.

THIN_PATTERNS catalog (mirrors invariant docstring):
  T1. `try: pass` only in the function body
  T2. Body consists of `pass` alone (with optional docstring)
  T3. `assert True` / `assert <constant>` (number, str literal)
  T4. Body contains only `pytest.skip(...)` (no other executable)
  T5. Docstring-only function body (no executable statements)

Allowlist mechanism (when the invariant ships): the decorator
`@pytest.mark.acceptable_thin_assertion` + a sibling `# reason:`
comment within 3 lines of the function `def` line exempts the test.

Exit codes:
  0 → scan OK (proving mode all GREEN) — operational summary printed
  1 → scan halt (>10 thin assertions found in live tree, OR proving
       mode reports a classifier defect)
"""
from __future__ import annotations

import argparse
import ast
import datetime as _dt
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TESTS_DIR = REPO / "backend" / "tests"
OUT_DIR = REPO / "memory" / "jc_artifacts" / "test_pollution"
OUT_DIR.mkdir(parents=True, exist_ok=True)
TS = _dt.datetime.now(_dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")

ACCEPTABLE_MARKER = "acceptable_thin_assertion"
REASON_PREFIX = "# reason:"


# ─────────────────────────────────────────────────────────────────────
# Classifier
# ─────────────────────────────────────────────────────────────────────

def _strip_docstring(body: list[ast.stmt]) -> list[ast.stmt]:
    """Return body with the leading docstring (if any) removed."""
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
    """Body has a single `try:` whose `body` reduces to `pass` only
    (ignoring docstrings) and no executable statements outside it."""
    stripped = _strip_docstring(body)
    # The `try` may be preceded by trivial assignments / requests
    # cleanup; the audit standard targets the case where the assertion
    # SHOULD be inside the try and ends up as `pass`. Conservative
    # heuristic: among ast.Try nodes in the function, the FIRST one
    # has a body that is exclusively `pass` (and only-pass means the
    # try's "main body" performs no test action).
    if not stripped:
        return False
    for node in stripped:
        if isinstance(node, ast.Try):
            inner = _strip_docstring(node.body)
            if len(inner) == 1 and isinstance(inner[0], ast.Pass):
                return True
            break  # only inspect the FIRST try
    return False


def _bare_assert_constant(body: list[ast.stmt]) -> tuple[bool, str]:
    """If the function's only executable statement is
    `assert <constant>` → flag. Constant = True / number / str literal."""
    stripped = _strip_docstring(body)
    if len(stripped) != 1 or not isinstance(stripped[0], ast.Assert):
        return False, ""
    test = stripped[0].test
    if isinstance(test, ast.Constant):
        return True, f"assert {test.value!r}"
    if isinstance(test, ast.NameConstant):  # pragma: no cover (py<3.8)
        return True, f"assert {test.value!r}"
    return False, ""


def _only_pytest_skip(body: list[ast.stmt]) -> bool:
    """Body's only executable statement is a `pytest.skip(...)` call."""
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
    # `pytest.skip(...)` may also surface as a single Raise — that's a
    # legitimate test-skip pattern outside this thin-assertion class.
    return False


def _docstring_only(body: list[ast.stmt]) -> bool:
    return (
        len(body) == 1
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    )


def classify(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> tuple[str | None, str]:
    """Return (pattern_id, evidence) if `fn` is a thin assertion,
    else (None, "").  pattern_id ∈ {T1..T5}."""
    body = fn.body
    # T5 first (most specific empty-shape).
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


# ─────────────────────────────────────────────────────────────────────
# Allowlist helpers
# ─────────────────────────────────────────────────────────────────────

def _has_acceptable_marker(fn: ast.FunctionDef | ast.AsyncFunctionDef) -> bool:
    for dec in fn.decorator_list:
        # @pytest.mark.acceptable_thin_assertion
        if (
            isinstance(dec, ast.Attribute)
            and dec.attr == ACCEPTABLE_MARKER
            and isinstance(dec.value, ast.Attribute)
            and dec.value.attr == "mark"
        ):
            return True
        # @pytest.mark.acceptable_thin_assertion("reason text") — Call form
        if (
            isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Attribute)
            and dec.func.attr == ACCEPTABLE_MARKER
        ):
            return True
    return False


def _has_reason_comment_near(text: str, fn_lineno: int) -> bool:
    """Return True if a `# reason:` comment exists within 3 lines
    BEFORE the function's `def` line."""
    lines = text.splitlines()
    start = max(0, fn_lineno - 4)
    for i in range(start, min(len(lines), fn_lineno)):
        if REASON_PREFIX in lines[i]:
            return True
    return False


# ─────────────────────────────────────────────────────────────────────
# File walker
# ─────────────────────────────────────────────────────────────────────

def _iter_test_files() -> list[Path]:
    out: list[Path] = []
    for p in sorted(TESTS_DIR.rglob("test_*.py")):
        # Exclude invariants directory (it contains the guard itself
        # plus other invariants that aren't tests in the thin-assertion
        # sense).
        if "/invariants/" in str(p):
            continue
        if "__pycache__" in p.parts:
            continue
        out.append(p)
    return out


def _scan_file(p: Path) -> list[dict]:
    findings: list[dict] = []
    try:
        src = p.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        return findings
    try:
        tree = ast.parse(src, filename=str(p))
    except SyntaxError as exc:
        findings.append({
            "file": str(p.relative_to(REPO)),
            "func": "<MODULE>",
            "lineno": exc.lineno or 0,
            "pattern": "SYNTAX-ERROR",
            "evidence": str(exc),
            "allowlisted": False,
        })
        return findings
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("test_"):
                continue
            pattern, evidence = classify(node)
            if pattern is None:
                continue
            allowlisted = (
                _has_acceptable_marker(node)
                and _has_reason_comment_near(src, node.lineno)
            )
            findings.append({
                "file": str(p.relative_to(REPO)),
                "func": node.name,
                "lineno": node.lineno,
                "pattern": pattern,
                "evidence": evidence,
                "allowlisted": allowlisted,
            })
    return findings


# ─────────────────────────────────────────────────────────────────────
# Scan mode
# ─────────────────────────────────────────────────────────────────────

def _scan_live_tree(threshold: int = 10) -> tuple[int, list[dict], Path]:
    all_findings: list[dict] = []
    for p in _iter_test_files():
        all_findings.extend(_scan_file(p))
    active = [f for f in all_findings if not f["allowlisted"]]

    out_path = OUT_DIR / f"thin_assertions_baseline_{TS}.md"
    lines: list[str] = []
    lines.append("**Canonical Spec**: `/app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md` "
                 "(structural enforcement: tests that assert nothing hide gaps)")
    lines.append("")
    lines.append(f"# Thin-assertion baseline scan · {TS}")
    lines.append("")
    lines.append(f"- **Files walked**: {len(_iter_test_files())}")
    lines.append(f"- **Findings (raw)**: {len(all_findings)}")
    lines.append(f"- **Findings (allowlisted via `@pytest.mark.acceptable_thin_assertion` "
                 "+ `# reason:` comment)**: "
                 f"{sum(1 for f in all_findings if f['allowlisted'])}")
    lines.append(f"- **Findings (ACTIVE — must close or allowlist)**: **{len(active)}**")
    lines.append(f"- **Halt threshold (>{threshold} → HALT)**: "
                 f"{'🟥 EXCEEDED' if len(active) > threshold else '✅ OK'}")
    lines.append("")
    lines.append("## Pattern catalog")
    lines.append("")
    lines.append("| ID | Pattern | Reason it's thin |")
    lines.append("|---|---|---|")
    lines.append("| T1 | `try: pass` (no assertion inside the try body) | Test runs zero substantive assertions — the `try` swallows nothing meaningful. |")
    lines.append("| T2 | body == `pass` (with optional docstring) | No statements executed under test. |")
    lines.append("| T3 | `assert <constant>` (e.g. `assert True`) | Constant assertion exercises nothing. |")
    lines.append("| T4 | body contains only `pytest.skip(...)` | Marker the test should be deleted or rewritten, not green-by-default. |")
    lines.append("| T5 | docstring-only body | Specification without verification. |")
    lines.append("")
    lines.append("## Active findings")
    if not active:
        lines.append("_(none — the live tree carries zero non-allowlisted thin assertions.)_")
    else:
        lines.append("| # | Pattern | File | Line | Function | Evidence |")
        lines.append("|---:|---|---|---:|---|---|")
        for i, f in enumerate(active, start=1):
            escaped_evidence = f["evidence"][:120].replace("|", "\\|")
            lines.append(
                f"| {i} | `{f['pattern']}` | `{f['file']}` | {f['lineno']} | "
                f"`{f['func']}` | `{escaped_evidence}` |"
            )
    lines.append("")
    if any(f["allowlisted"] for f in all_findings):
        lines.append("## Allowlisted findings")
        lines.append("| Pattern | File | Line | Function |")
        lines.append("|---|---|---:|---|")
        for f in all_findings:
            if f["allowlisted"]:
                lines.append(f"| `{f['pattern']}` | `{f['file']}` | {f['lineno']} | `{f['func']}` |")
        lines.append("")

    out_path.write_text("\n".join(lines), encoding="utf-8")
    return len(active), all_findings, out_path


# ─────────────────────────────────────────────────────────────────────
# Proving-slice mode (classifier self-test)
# ─────────────────────────────────────────────────────────────────────

PROVING_FIXTURES = [
    # (source code, function name, expected_pattern_or_None, description)
    ("""
def test_try_pass_only():
    \"\"\"docstring claims to verify X\"\"\"
    try:
        pass
    finally:
        pass
""", "test_try_pass_only", "T1", "try: pass with finally cleanup"),
    ("""
def test_only_pass():
    pass
""", "test_only_pass", "T2", "body == pass"),
    ("""
def test_only_pass_with_docstring():
    \"\"\"docstring\"\"\"
    pass
""", "test_only_pass_with_docstring", "T2", "docstring + pass"),
    ("""
def test_assert_true():
    assert True
""", "test_assert_true", "T3", "assert True"),
    ("""
def test_assert_constant_str():
    assert "ok"
""", "test_assert_constant_str", "T3", "assert string literal"),
    ("""
import pytest
def test_only_skip():
    pytest.skip("not implemented")
""", "test_only_skip", "T4", "only pytest.skip()"),
    ("""
def test_docstring_only():
    \"\"\"this is a spec without verification\"\"\"
""", "test_docstring_only", "T5", "docstring only"),
    # Negative cases — these MUST NOT be classified as thin.
    ("""
def test_real_assertion():
    x = 1 + 1
    assert x == 2
""", "test_real_assertion", None, "real assertion (negative case)"),
    ("""
def test_real_with_try():
    try:
        assert 1 == 1
    finally:
        pass
""", "test_real_with_try", None, "try with real assertion inside (negative)"),
    ("""
def test_legitimate_skip_with_marker():
    import pytest
    if some_condition:
        pytest.skip("conditional")
    assert real_work() == "ok"
""", "test_legitimate_skip_with_marker", None, "conditional skip + real assertion"),
]


def _proving_mode() -> int:
    print(f"== INVARIANT-NO-THIN-ASSERTIONS proving slice · {TS} ==\n")
    failed = 0
    for src, fname, expected, desc in PROVING_FIXTURES:
        tree = ast.parse(src)
        target = None
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == fname:
                target = node
                break
        if target is None:
            print(f"  [RED] {fname}: function not found in fixture src")
            failed += 1
            continue
        actual, evidence = classify(target)
        ok = (actual == expected)
        flag = "GREEN" if ok else "RED"
        print(f"  [{flag}] {fname} (expected={expected}, actual={actual}) — {desc}")
        if not ok:
            print(f"        evidence: {evidence!r}")
            failed += 1
    print()
    if failed:
        print(f"FAIL: {failed} fixture(s) misclassified")
        return 1
    print(f"OK: {len(PROVING_FIXTURES)}/{len(PROVING_FIXTURES)} classifier fixtures GREEN")
    return 0


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(description="thin-assertion guard slice + scanner")
    ap.add_argument("--proving", action="store_true",
                    help="run classifier self-test fixtures instead of live-tree scan")
    ap.add_argument("--halt-threshold", type=int, default=10,
                    help="HALT-and-surface threshold for live-tree scan (default 10)")
    args = ap.parse_args(argv)

    if args.proving:
        return _proving_mode()

    print(f"== INVARIANT-NO-THIN-ASSERTIONS live-tree scan · {TS} ==")
    print(f"   Tests dir: {TESTS_DIR}")
    print(f"   HALT threshold: >{args.halt_threshold} active findings\n")

    active_count, all_findings, out_path = _scan_live_tree(args.halt_threshold)
    print(f"   Total files scanned: {len(_iter_test_files())}")
    print(f"   Raw findings:        {len(all_findings)}")
    print(f"   Allowlisted:         {sum(1 for f in all_findings if f['allowlisted'])}")
    print(f"   ACTIVE findings:     {active_count}")
    print(f"   Baseline report:     {out_path.relative_to(REPO)}")

    if active_count > args.halt_threshold:
        print(f"\n🟥 HALT — active count {active_count} exceeds threshold {args.halt_threshold}")
        print("   Surface the baseline report and surface for user direction before shipping the invariant.")
        return 1
    print(f"\n✅ Active count {active_count} ≤ threshold {args.halt_threshold} — safe to ship invariant.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
