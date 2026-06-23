"""Deliberate-violation smoke — Phase 4.0 (cross-context calls).

Proves the cross-context-calls invariant has TEETH. Synthesises both
classes of violation as in-memory AST trees and runs the production
scanner's extractor functions over them; asserts each is flagged.

Mirrors the Phase 0 tenancy deliberate-violation smoke (file:
`tests/invariants/test_invariant_violations_smoke.py`). SKIPPED by
default. Set `AKKI_RUN_DELIBERATE_CROSS_CONTEXT_VIOLATION_SMOKE=1` to
run.

Phase 4.0 dispatch §Part C step 11 — required artefact: "Add the
deliberate-violation smoke for cross-context calls — a deliberately-
skipped test that, when unskipped, deliberately writes a cross-
context direct call and asserts the invariant fails. Same pattern as
Phase 0's tenancy deliberate-violation. Proves the enforce has
teeth."

Unskip-and-run smoke from a shell:

    cd /app/backend
    AKKI_RUN_DELIBERATE_CROSS_CONTEXT_VIOLATION_SMOKE=1 \\
        python -m pytest tests/invariants/test_invariant_cross_context_violations_smoke.py -v
"""
from __future__ import annotations

import ast
import os
import sys
from pathlib import Path

import pytest

# Make the production scanner module importable via the standard
# `tests/invariants/` package path; this mirrors the Phase 0 smoke.
_INV_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_INV_DIR))

from test_invariant_cross_context_calls import (  # noqa: E402
    CROSS_CONTEXT_PRIMITIVES,
    AKKI_OWNED_COLLECTIONS,
    _call_name,
    _detect_db_calls,
    _file_context,
    _is_contract_call,
    _line_is_escape_hatched,
)


_SHOULD_RUN = (
    os.environ.get("AKKI_RUN_DELIBERATE_CROSS_CONTEXT_VIOLATION_SMOKE") == "1"
)

pytestmark = pytest.mark.skipif(
    not _SHOULD_RUN,
    reason=(
        "Deliberate-cross-context-violation smoke is SKIPPED in the default "
        "sweep. Set AKKI_RUN_DELIBERATE_CROSS_CONTEXT_VIOLATION_SMOKE=1 to "
        "run. Proves the cross-context invariant detects offenders."
    ),
)


# ─────────────────────── deliberate-violation samples ───────────────────────

_DELIBERATE_PRIMITIVE_CALL_AKKI = """\
# This SYNTHETIC akki-router file calls a SyniSense primitive directly,
# WITHOUT going via the contract. The invariant must flag it.
from services.synisense.shield.client import invoke as shield_invoke

async def some_handler(tenant_id):
    return await shield_invoke(  # NOT routed through contracts!
        purpose="health.ping",
        content="hi",
        tenant_id=tenant_id,
        consumer_id="test",
        user_id=tenant_id,
    )
"""

_DELIBERATE_DB_CALL_FROM_SYNISENSE = """\
# This SYNTHETIC synisense-engine file reads Akki's `accounts`
# collection directly. The invariant must flag it.
from core import db

async def harvest(tenant_id):
    row = await db.accounts.find_one({"id": tenant_id})  # cross-context db read
    return row
"""

_PROPER_CONTRACT_CALL = """\
# This SYNTHETIC akki-router file routes through the contracts package.
# The invariant must NOT flag it.
from contracts import get_synisense

async def some_handler(tenant_id):
    result = (await get_synisense().shield_invoke(
        purpose="health.ping",
        content="hi",
        account_id=tenant_id,
        consumer_id="test",
        user_id=tenant_id,
    )).raw
    return result["response"]
"""


def _scan_synthetic(source: str, *, file_path: str):
    """Mini-scanner that mirrors the production walk."""
    source_lines = source.splitlines()
    tree = ast.parse(source, filename=file_path)
    my_ctx = _file_context(file_path)
    flagged = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if _line_is_escape_hatched(source_lines, node.lineno):
            continue
        name = _call_name(node)
        if name and name in CROSS_CONTEXT_PRIMITIVES:
            owner = CROSS_CONTEXT_PRIMITIVES[name]
            if _is_contract_call(node):
                continue
            if owner != my_ctx and my_ctx != "contracts":
                flagged.append(("primitive_call", name, owner, my_ctx))
                continue
        db_call = _detect_db_calls(node)
        if db_call is None:
            continue
        coll, method = db_call
        if coll not in AKKI_OWNED_COLLECTIONS:
            continue
        if my_ctx in ("synisense", "solva"):
            flagged.append((
                "db_read_from_other_context",
                f"db.{coll}.{method}", "akki", my_ctx,
            ))
    return flagged


# ─────────────────────── tests ───────────────────────

def test_primitive_call_outside_contract_is_detected() -> None:
    """An akki-context file calling `shield_invoke` directly is
    flagged as a `primitive_call` violation."""
    flagged = _scan_synthetic(
        _DELIBERATE_PRIMITIVE_CALL_AKKI,
        file_path="/app/backend/routers/synthetic_offender.py",
    )
    assert any(
        kind == "primitive_call" and name == "shield_invoke"
        for kind, name, _, _ in flagged
    ), f"Expected to flag a primitive-call violation, got: {flagged!r}"


def test_db_call_from_synisense_to_akki_collection_is_detected() -> None:
    """A synisense-context file calling `db.accounts.find_one` is
    flagged as a `db_read_from_other_context` violation."""
    flagged = _scan_synthetic(
        _DELIBERATE_DB_CALL_FROM_SYNISENSE,
        file_path="/app/backend/services/synisense/synthetic_offender.py",
    )
    assert any(
        kind == "db_read_from_other_context"
        and name == "db.accounts.find_one"
        for kind, name, _, _ in flagged
    ), f"Expected to flag a db-read violation, got: {flagged!r}"


def test_contract_routed_call_is_NOT_flagged() -> None:
    """A call going via `get_synisense().shield_invoke(...)` must
    pass through the scanner without being flagged."""
    flagged = _scan_synthetic(
        _PROPER_CONTRACT_CALL,
        file_path="/app/backend/routers/proper_offender_fake.py",
    )
    assert flagged == [], (
        f"Contract-routed call should NOT be flagged; got: {flagged!r}"
    )
