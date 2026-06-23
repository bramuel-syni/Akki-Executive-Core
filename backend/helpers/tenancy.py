"""Tenancy filter / document builders — Phase 2.1.

This module is the single guarded entry point for assembling Mongo
filter dicts and insert documents against tenant-scoped collections.
Existing call sites can adopt the helpers incrementally; the Phase 2
tenancy invariant recognises both raw dict literals carrying
`account_id` AND the helper calls below.

Contract:
  - `tenant_filter(extra: dict, *, account_id: str) -> dict`
      Returns `{**extra, "account_id": account_id}`. Raises
      `ValueError` if `account_id` is empty/falsy.

  - `tenant_doc(doc: dict, *, account_id: str) -> dict`
      Returns `{**doc, "account_id": account_id}`. Raises
      `ValueError` if `account_id` is empty/falsy.

Both helpers are pure dict-builders. No I/O, no DB calls, no
side-effects. Forward-compatible with Phase 4's process / transport
split — when adapters move to HTTP, the builders continue to work
unchanged.

Discipline rails honoured:
  - R5 (Honesty Protocol): ValueError raised on empty/None
    account_id rather than silently swallowing. No fallback to a
    sentinel; callers must supply a real tenant id.
  - Behaviour-preserving: a compliant call site
    `db.X.find_one({"id": x, "account_id": current["id"]})` is
    semantically identical to
    `db.X.find_one(tenant_filter({"id": x}, account_id=current["id"]))`.
"""
from __future__ import annotations

from typing import Any, Dict


def tenant_filter(extra: Dict[str, Any], *, account_id: str) -> Dict[str, Any]:
    """Build a Mongo filter dict scoped to the given tenant.

    Returns a new dict with `account_id` mixed into `extra`. The
    original `extra` dict is NOT mutated.

    Raises:
        ValueError: if `account_id` is empty / None / falsy.
    """
    if not account_id:
        raise ValueError(
            "tenant_filter: account_id is required and must be non-empty"
        )
    return {**extra, "account_id": account_id}


def tenant_doc(doc: Dict[str, Any], *, account_id: str) -> Dict[str, Any]:
    """Build a Mongo insert document scoped to the given tenant.

    Returns a new dict with `account_id` mixed into `doc`. The
    original `doc` dict is NOT mutated.

    Raises:
        ValueError: if `account_id` is empty / None / falsy.
    """
    if not account_id:
        raise ValueError(
            "tenant_doc: account_id is required and must be non-empty"
        )
    return {**doc, "account_id": account_id}
