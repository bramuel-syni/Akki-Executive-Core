"""JC-WS-DECK-A10-BACKEND-RETRIEVAL-LINEAGE-REGENERATE (2026-07-04) — lineage graph.

Canonical spec: /app/memory/sprints/JC_WS_DECK_A10_BACKEND_RETRIEVAL_LINEAGE_REGENERATE.md

F.6 discipline-pay: N/A. Graph traversal only — no LLM path, no Shield
routing. This module MUST NOT import `contracts.get_synisense` or any
LLM SDK. R11 of the A10-backend proving slice enforces this positively.

Lineage model:
  - `regenerated_from` field on a documents row is the backbone edge
    (points to the immediate parent doc_id).
  - `version_number` gives ordering within a chain.
  - Ancestors = walk `regenerated_from` up until null.
  - Descendants = walk children (rows where `regenerated_from` = current id).
  - Siblings = other rows with the same `regenerated_from` (fan-out from
    same parent — multiple regeneration branches).

Account isolation: every walk step verifies the traversed doc is
reachable to the caller via context membership. Off-account lineage is
truncated at the boundary (never leaks).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set

from core import db

logger = logging.getLogger("work_studio.deck_lineage")


MAX_LINEAGE_DEPTH = 20


async def _account_context_ids(account_id: str) -> Set[str]:
    """The set of context_ids the account has active membership in.
    Cached at call scope (small enough for per-request usage)."""
    ctxs = set()
    async for m in db.memberships.find(
        {"account_id": account_id, "status": "active"},
        {"_id": 0, "context_id": 1},
    ):
        ctxs.add(m["context_id"])
    return ctxs


async def _fetch_doc_scoped(doc_id: str, allowed_ctxs: Set[str]) -> Optional[Dict[str, Any]]:
    doc = await db.documents.find_one(
        {"id": doc_id}, {
            "_id": 0, "id": 1, "context_id": 1, "name": 1,
            "state": 1, "lifecycle_state": 1, "version_number": 1, "regenerated_from": 1,
            "regenerate_shield_audit_id": 1, "created_at": 1, "updated_at": 1,
        },
    )
    if not doc:
        return None
    if doc.get("context_id") not in allowed_ctxs:
        return None  # boundary: silently truncate at ownership edge
    return doc


async def get_lineage(
    *,
    document_id: str,
    account_id: str,
) -> Dict[str, Any]:
    """Return `{document, ancestors: [...], descendants: [...], siblings: [...]}`.

    Ancestors ordered oldest-first (root → immediate-parent).
    Descendants ordered by depth then created_at.
    Siblings: docs sharing the same `regenerated_from` (excluding self).

    Returns `{document: None, ...}` if the document isn't reachable to
    the caller (account isolation boundary preserved silently).
    """
    allowed = await _account_context_ids(account_id)
    if not allowed:
        return {"document": None, "ancestors": [], "descendants": [], "siblings": []}

    self_doc = await _fetch_doc_scoped(document_id, allowed)
    if not self_doc:
        return {"document": None, "ancestors": [], "descendants": [], "siblings": []}

    # Ancestors — walk regenerated_from up.
    ancestors: List[Dict[str, Any]] = []
    cursor_id = self_doc.get("regenerated_from")
    depth = 0
    while cursor_id and depth < MAX_LINEAGE_DEPTH:
        parent = await _fetch_doc_scoped(cursor_id, allowed)
        if not parent:
            break
        ancestors.append(parent)
        cursor_id = parent.get("regenerated_from")
        depth += 1
    ancestors.reverse()  # oldest-first (root → immediate-parent)

    # Descendants — breadth-first via regenerated_from = current id.
    descendants: List[Dict[str, Any]] = []
    frontier: List[str] = [document_id]
    depth = 0
    while frontier and depth < MAX_LINEAGE_DEPTH:
        next_frontier: List[str] = []
        for parent_id in frontier:
            cursor = db.documents.find(
                {"regenerated_from": parent_id},
                {
                    "_id": 0, "id": 1, "context_id": 1, "name": 1,
                    "state": 1, "lifecycle_state": 1, "version_number": 1, "regenerated_from": 1,
                    "regenerate_shield_audit_id": 1, "created_at": 1, "updated_at": 1,
                },
            )
            async for child in cursor:
                if child.get("context_id") not in allowed:
                    continue
                descendants.append(child)
                next_frontier.append(child["id"])
        frontier = next_frontier
        depth += 1

    # Siblings — same regenerated_from as self, excluding self.
    siblings: List[Dict[str, Any]] = []
    self_parent = self_doc.get("regenerated_from")
    if self_parent:
        cursor = db.documents.find(
            {"regenerated_from": self_parent, "id": {"$ne": document_id}},
            {
                "_id": 0, "id": 1, "context_id": 1, "name": 1,
                "state": 1, "lifecycle_state": 1, "version_number": 1, "regenerated_from": 1,
                "regenerate_shield_audit_id": 1, "created_at": 1, "updated_at": 1,
            },
        )
        async for sib in cursor:
            if sib.get("context_id") in allowed:
                siblings.append(sib)

    return {
        "document": self_doc,
        "ancestors": ancestors,
        "descendants": descendants,
        "siblings": siblings,
    }
