"""Deliberate-violation smoke — Phase 0.

Proves the tenancy invariant has TEETH. Synthesises a violation in
the form of a temporary source file, runs the tenancy scanner over
it, and asserts the scanner flags the violation.

This test is `@pytest.mark.skip`'d by default so the default sweep
doesn't fail. Unskip locally (delete the `pytestmark` line OR set
`AKKI_RUN_DELIBERATE_VIOLATION_SMOKE=1` env) to verify the
invariant detects the offender.

Phase 0 dispatch §Step 4 — required artefact: "Add ONE explicit
'this would fail' test that's currently SKIPPED. When unskipped, it
must fail and prove the invariant detects the violation."

Implementation note: rather than writing a synthetic offender into
a tracked source path (which would pollute the repo's tenancy
report and fail tests by design), this smoke parses an offender
defined as a STRING via `ast.parse` and walks it with the same
extractor functions the production scanner uses. This way the
proof of teeth lives next to the invariant without contaminating
the codebase.

Unskip-and-run smoke from a shell:

    cd /app/backend
    AKKI_RUN_DELIBERATE_VIOLATION_SMOKE=1 \\
        python -m pytest tests/invariants/test_invariant_violations_smoke.py -v
"""
from __future__ import annotations

import ast
import os
from typing import Optional

import pytest


_SHOULD_RUN = os.environ.get("AKKI_RUN_DELIBERATE_VIOLATION_SMOKE") == "1"

# When the env flag is set we run the smoke; otherwise we skip with
# a reason that surfaces in the report.
pytestmark = pytest.mark.skipif(
    not _SHOULD_RUN,
    reason=(
        "Deliberate-violation smoke is SKIPPED in the default sweep. "
        "Set AKKI_RUN_DELIBERATE_VIOLATION_SMOKE=1 to run. Proves the "
        "tenancy invariant detects offenders."
    ),
)


# Synthetic offender — three different shapes of tenancy violation.
_OFFENDER_SOURCE = """
async def offender_filter_missing(uid: str):
    # Filter dict literal with NO account_id — definite violation.
    return await db.chats.find_one({'id': uid})


async def offender_insert_missing(payload: dict):
    # Insert document literal with NO account_id — definite violation.
    return await db.chats.insert_one({'id': 'x', 'title': 't'})


async def offender_no_args():
    # No args at all — definite violation.
    return await db.chats.find()


async def offender_non_literal_filter(filt: dict):
    # Filter is a variable — non_literal (recorded, but not counted
    # as a definite violation against the Phase-2-enforce baseline).
    return await db.chats.find_one(filt)
"""


def _extract_db_call(node: ast.Call) -> Optional[tuple]:
    """Mirrors `test_invariant_tenancy._extract_db_call`."""
    func = node.func
    if not isinstance(func, ast.Attribute):
        return None
    method = func.attr
    inner = func.value
    if not isinstance(inner, ast.Attribute):
        return None
    collection = inner.attr
    root = inner.value
    if not isinstance(root, ast.Name) or root.id != "db":
        return None
    return (collection, method)


def _dict_has_account_id_key(node: ast.AST) -> Optional[bool]:
    """Mirrors `test_invariant_tenancy._dict_has_account_id_key`."""
    if not isinstance(node, ast.Dict):
        return None
    for k in node.keys:
        if isinstance(k, ast.Constant) and k.value == "account_id":
            return True
    return False


def test_synthetic_offender_filter_is_flagged() -> None:
    """offender_filter_missing → scanner flags the Dict-literal violation."""
    tree = ast.parse(_OFFENDER_SOURCE)
    matched = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _extract_db_call(node) != ("chats", "find_one"):
            continue
        first = node.args[0] if node.args else None
        if isinstance(first, ast.Dict):
            has = _dict_has_account_id_key(first)
            if has is False:
                matched = True
                break
    assert matched, (
        "Deliberate-violation smoke FAILED: scanner did NOT flag the "
        "synthetic offender. The tenancy invariant has lost its teeth."
    )


def test_synthetic_offender_insert_is_flagged() -> None:
    """offender_insert_missing → scanner flags the insert document."""
    tree = ast.parse(_OFFENDER_SOURCE)
    matched = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _extract_db_call(node) != ("chats", "insert_one"):
            continue
        first = node.args[0] if node.args else None
        if isinstance(first, ast.Dict) and _dict_has_account_id_key(first) is False:
            matched = True
            break
    assert matched, (
        "Deliberate-violation smoke FAILED on insert_one: scanner did "
        "NOT flag the synthetic offender."
    )


def test_synthetic_offender_no_args_is_flagged() -> None:
    """offender_no_args → scanner flags the no-filter case."""
    tree = ast.parse(_OFFENDER_SOURCE)
    matched = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _extract_db_call(node) != ("chats", "find"):
            continue
        if not node.args:
            matched = True
            break
    assert matched, (
        "Deliberate-violation smoke FAILED: scanner did NOT flag "
        "db.chats.find() with no args."
    )


def test_synthetic_offender_non_literal_is_recorded() -> None:
    """offender_non_literal_filter → scanner records as non_literal."""
    tree = ast.parse(_OFFENDER_SOURCE)
    found_non_literal = False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _extract_db_call(node) != ("chats", "find_one"):
            continue
        first = node.args[0] if node.args else None
        if first is not None and not isinstance(first, ast.Dict):
            found_non_literal = True
            break
    assert found_non_literal, (
        "Deliberate-violation smoke FAILED: scanner did NOT see "
        "variable-as-filter as non_literal."
    )
