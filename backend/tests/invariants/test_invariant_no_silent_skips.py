"""Phase 5.5 Part A — invariant: no silent skips in the test suite.

Every `pytest.skip(...)` and `@pytest.mark.skip(...)` / `@pytest.mark.skipif(...)`
MUST carry an explicit, specific reason. This invariant fails the
build on any silent/generic skip the moment it lands.

Why this matters: silent skips mask broken tests. The codebase
already has ~100+ legitimate skips for things like
"HUMAN_REQUIRED: admin has no Solva v2 sessions seeded" — those are
honest, specific, and unblockable in this env. A new
`@pytest.mark.skip` with no reason hides an actual failure that
will be missed in code review.

The invariant operates as STATIC ANALYSIS (regex over the test
tree) — not via pytest collection — so it's fast and deterministic.

Banned patterns:
  - `pytest.skip()` — bare call, no reason argument.
  - `pytest.skip("")` — empty string reason.
  - `pytest.skip("<generic>")` where `<generic>` is one of
    {"WIP", "TODO", "fixme", "skip", "unsupported", "wip", "todo",
     "FIXME", "SKIP", "UNSUPPORTED", "xfail", "XFAIL"}.
  - `@pytest.mark.skip` (decorator with NO `reason=` kwarg).
  - `@pytest.mark.skip(reason="")` — empty.
  - `@pytest.mark.skipif(<cond>)` with no `reason=` kwarg.
  - `@pytest.mark.skipif(<cond>, reason="")` — empty.

Allowed:
  - `pytest.skip("HUMAN_REQUIRED: admin@akki.ai has no Solva v2 ...")` ✓
  - `pytest.skip(f"docker daemon unavailable: {e}")` (f-string is fine) ✓
  - `@pytest.mark.skip(reason="Phase 6 BC-mirror — restore in Phase 7")` ✓
  - `@pytest.mark.skipif(not LIVE_OPENAI, reason="needs real OpenAI key")` ✓

Whitelist: this invariant has NO whitelist. Every skip in the
codebase must carry a specific reason. That's the whole point.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import List, Tuple


TESTS_ROOT = Path(__file__).resolve().parent.parent

# Reasons that are too vague to count as honest. The invariant fails
# if any skip reason matches one of these (case-insensitive substring
# match would be too aggressive; we use exact-lowercase match instead
# to avoid false positives like "todo list" in a longer reason).
_GENERIC_REASONS = {
    "",
    "wip",
    "todo",
    "fixme",
    "skip",
    "skipped",
    "unsupported",
    "xfail",
    "n/a",
    "tbd",
    "see above",
    "see below",
}


def _is_generic(reason: str) -> bool:
    """Return True if the given reason is a generic placeholder."""
    return reason.strip().lower() in _GENERIC_REASONS


def _walk_python_test_files() -> List[Path]:
    """Yield every `test_*.py` and `conftest.py` under the tests tree."""
    out: List[Path] = []
    for path in TESTS_ROOT.rglob("*.py"):
        # Skip __pycache__ + this invariant itself.
        if "__pycache__" in path.parts:
            continue
        if path.name == "test_invariant_no_silent_skips.py":
            continue
        if path.name == "conftest.py" or path.name.startswith("test_"):
            out.append(path)
    return sorted(out)


def _check_pytest_skip_call(node: ast.Call) -> Tuple[bool, str]:
    """For a `pytest.skip(...)` Call node, return (is_ok, diagnostic).

    Accepted: at least one positional argument that's not an empty
    string OR a generic placeholder. f-strings, .format() calls, and
    `+` concatenations are accepted as "non-trivial dynamic reasons".
    """
    if not node.args:
        return False, "bare pytest.skip() — no reason"
    first = node.args[0]
    if isinstance(first, ast.Constant) and isinstance(first.value, str):
        if _is_generic(first.value):
            return False, f"generic pytest.skip(reason={first.value!r})"
    # Non-Constant first arg (variable, f-string, function call,
    # concatenation, etc.) — accept; can't statically prove it's
    # vacuous, and dynamic reasons are honest by convention.
    return True, ""


def _check_mark_skip_decorator(node: ast.Call, decorator_name: str) -> Tuple[bool, str]:
    """For an `@pytest.mark.skip(...)` / `@pytest.mark.skipif(...)`
    Call node, return (is_ok, diagnostic).

    Accepted: a `reason=` kwarg with a non-empty, non-generic value.
    """
    reason_kw = None
    for kw in node.keywords:
        if kw.arg == "reason":
            reason_kw = kw.value
            break
    if reason_kw is None:
        return False, f"@pytest.mark.{decorator_name}(...) with no reason= kwarg"
    if isinstance(reason_kw, ast.Constant) and isinstance(reason_kw.value, str):
        if _is_generic(reason_kw.value):
            return False, (
                f"@pytest.mark.{decorator_name}(reason={reason_kw.value!r}) — generic"
            )
    return True, ""


def _scan_for_silent_skips() -> List[str]:
    """Walk the test tree and return diagnostic strings for every
    silent / generic skip found."""
    diagnostics: List[str] = []
    for path in _walk_python_test_files():
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError) as exc:
            diagnostics.append(f"{path}: failed to parse — {exc}")
            continue

        for node in ast.walk(tree):
            # Catch `pytest.skip(...)` calls
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "skip"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "pytest"
            ):
                ok, diag = _check_pytest_skip_call(node)
                if not ok:
                    diagnostics.append(
                        f"{path.relative_to(TESTS_ROOT)}:{node.lineno}: {diag}"
                    )
                continue

            # Catch decorator-style @pytest.mark.skip / .skipif
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                attr_chain: list[str] = []
                cur = node.func
                while isinstance(cur, ast.Attribute):
                    attr_chain.append(cur.attr)
                    cur = cur.value
                if (
                    isinstance(cur, ast.Name)
                    and cur.id == "pytest"
                    and attr_chain[-2:] == ["mark", "skip"][::-1] + []
                ):
                    pass  # Will handle skip/skipif below

            # Decorator usage: walk function defs + class defs for
            # decorator_list entries that are Calls with .mark.skip/.skipif.
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                for deco in node.decorator_list:
                    if not isinstance(deco, ast.Call):
                        # Bare decorator like `@pytest.mark.skip` — no
                        # reason supplied. Banned.
                        if isinstance(deco, ast.Attribute):
                            attrs: list[str] = []
                            cur2 = deco
                            while isinstance(cur2, ast.Attribute):
                                attrs.append(cur2.attr)
                                cur2 = cur2.value
                            if (
                                isinstance(cur2, ast.Name)
                                and cur2.id == "pytest"
                                and attrs == ["skip", "mark"]
                            ):
                                diagnostics.append(
                                    f"{path.relative_to(TESTS_ROOT)}:{deco.lineno}: "
                                    f"bare @pytest.mark.skip with no reason"
                                )
                        continue
                    # @something(...) — check if it's .mark.skip or .mark.skipif
                    if isinstance(deco.func, ast.Attribute):
                        attrs2: list[str] = []
                        cur3: ast.expr = deco.func
                        while isinstance(cur3, ast.Attribute):
                            attrs2.append(cur3.attr)
                            cur3 = cur3.value
                        if (
                            isinstance(cur3, ast.Name)
                            and cur3.id == "pytest"
                            and len(attrs2) >= 2
                            and attrs2[-1] == "mark"
                            and attrs2[0] in ("skip", "skipif")
                        ):
                            ok, diag = _check_mark_skip_decorator(deco, attrs2[0])
                            if not ok:
                                diagnostics.append(
                                    f"{path.relative_to(TESTS_ROOT)}:{deco.lineno}: {diag}"
                                )
    return diagnostics


def test_no_silent_skips_in_test_tree() -> None:
    """No silent / generic skip in `backend/tests/`."""
    diagnostics = _scan_for_silent_skips()
    assert not diagnostics, (
        f"Phase 5.5 Part A invariant — found {len(diagnostics)} silent/generic skip(s) "
        f"in the test tree:\n  "
        + "\n  ".join(diagnostics[:50])
        + (f"\n  ... and {len(diagnostics) - 50} more" if len(diagnostics) > 50 else "")
        + "\n\nRemediation: replace bare skip / empty reason / generic placeholder "
        + "with an explicit, specific reason. Example:\n"
        + '  GOOD: pytest.skip("HUMAN_REQUIRED: admin has no Solva v2 sessions seeded")\n'
        + '  GOOD: @pytest.mark.skipif(not LIVE_LLM, reason="needs real LLM key")\n'
        + '  BAD : pytest.skip("WIP")\n'
        + '  BAD : @pytest.mark.skip\n'
    )
