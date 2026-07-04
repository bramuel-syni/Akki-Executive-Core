"""JC-WS-DECK-A10-BACKEND-RETRIEVAL-LINEAGE-REGENERATE (2026-07-04) — retrieval + similarity.

Canonical spec: /app/memory/sprints/JC_WS_DECK_A10_BACKEND_RETRIEVAL_LINEAGE_REGENERATE.md

F.6 discipline-pay: N/A. Metadata queries only — no LLM path, no
Shield routing. This module MUST NOT import
`contracts.get_synisense` or any LLM SDK. R11 of the A10-backend
proving slice enforces this positively.

Retrieval scoring (metadata-only):
  - `source_document_ids` overlap (Jaccard-like)
  - `category` and `doc_kind` equality
  - `context_id` proximity (same-context bump)
  - Optional legacy `keywords` intersection if the target row carries them

Account isolation: every query is bounded by the requesting account's
context memberships. Cross-account rows are UNREACHABLE via this
service (R3/R4 assert isolation end-to-end).
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from core import db

logger = logging.getLogger("work_studio.deck_retrieval")


def _score_pair(source: Dict[str, Any], candidate: Dict[str, Any]) -> float:
    """Pure-metadata similarity score in [0, 1]. Higher = more related."""
    score = 0.0

    # (1) source_document_ids overlap — the strongest signal (both decks
    # generated from overlapping source doc sets).
    src_ids = set(source.get("source_document_ids") or [])
    cnd_ids = set(candidate.get("source_document_ids") or [])
    if src_ids and cnd_ids:
        overlap = src_ids & cnd_ids
        union = src_ids | cnd_ids
        if union:
            score += 0.5 * (len(overlap) / len(union))  # Jaccard, weighted 0.5

    # (2) Same category + same kind → bump.
    if source.get("category") and source.get("category") == candidate.get("category"):
        score += 0.15
    if source.get("doc_kind") and source.get("doc_kind") == candidate.get("doc_kind"):
        score += 0.10

    # (3) Same context — small bump (context-scoped users see co-context first).
    if source.get("context_id") == candidate.get("context_id"):
        score += 0.10

    # (4) Same source_channel (both akki-generated vs both uploaded).
    if source.get("source_channel") and source.get("source_channel") == candidate.get("source_channel"):
        score += 0.05

    # (5) Recent update bump — decks touched in the last 30 days by the
    # same account_context feel more relevant.
    #     (deferred — needs delta computation; keep the scorer pure)

    return round(min(1.0, score), 4)


async def get_related_decks(
    *,
    document_id: str,
    account_id: str,
    limit: int = 10,
) -> List[Dict[str, Any]]:
    """Return metadata-scored related decks for a source doc, scoped to
    the account's context memberships. Returns [] if the source doc
    isn't reachable to this account (isolation via membership scoping).
    """
    # Fetch source doc.
    source = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not source:
        return []
    # Enforce account access on the source itself.
    src_ctx = source.get("context_id")
    if not src_ctx:
        return []
    membership = await db.memberships.find_one(
        {"context_id": src_ctx, "account_id": account_id, "status": "active"},
        {"_id": 0},
    )
    if not membership:
        return []

    # Gather account's active contexts (retrieval boundary).
    account_ctxs = [
        m["context_id"]
        async for m in db.memberships.find(
            {"account_id": account_id, "status": "active"},
            {"_id": 0, "context_id": 1},
        )
    ]
    if not account_ctxs:
        return []

    # Candidate universe: decks in account's contexts, excluding the source itself.
    cursor = db.documents.find(
        {
            "context_id": {"$in": account_ctxs},
            "id": {"$ne": document_id},
            "$or": [
                {"category": "deck"},
                {"doc_kind": "deck"},
                {"doc_type": "deck"},
            ],
        },
        {
            "_id": 0, "id": 1, "context_id": 1, "name": 1, "category": 1,
            "doc_kind": 1, "source_channel": 1, "source_document_ids": 1,
            "created_at": 1, "updated_at": 1, "version_number": 1,
            "regenerated_from": 1, "data_trust": 1,
        },
    ).limit(500)
    candidates = await cursor.to_list(500)

    # Score + rank.
    scored: List[Dict[str, Any]] = []
    for cand in candidates:
        score = _score_pair(source, cand)
        if score <= 0.0:
            continue
        scored.append({**cand, "similarity_score": score})
    scored.sort(key=lambda r: r["similarity_score"], reverse=True)
    return scored[:limit]
