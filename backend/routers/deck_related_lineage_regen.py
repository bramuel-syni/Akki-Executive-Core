"""JC-WS-DECK-A10-BACKEND-RETRIEVAL-LINEAGE-REGENERATE (2026-07-04) — 3 endpoints.

Canonical spec: /app/memory/sprints/JC_WS_DECK_A10_BACKEND_RETRIEVAL_LINEAGE_REGENERATE.md

Per-surface F.6 (banked in memo header verbatim):
  - GET /related  → F.6 N/A (metadata queries; uses `services.deck_retrieval`)
  - GET /lineage  → F.6 N/A (graph traversal; uses `services.deck_lineage`)
  - POST /regenerate → F.6 SHIELD-ROUTED (LLM path; uses `services.deck_regenerate`
                      which imports `contracts.get_synisense` — the canonical chokepoint)

Auth model (all three):
  - Unauthenticated → 401/403 (auth dep + CSRF gate).
  - Non-member of document's context → 403 for regenerate.
    Retrieval/lineage return empty/silent-truncate at the boundary
    (isolation via account_id-scoped queries in the underlying services).
  - Document not found → 404 (regenerate); retrieval returns [], lineage
    returns null-shaped envelope.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, Depends
from pydantic import BaseModel, Field

from core import db, get_current_account
from services import deck_retrieval, deck_lineage, deck_regenerate


log = logging.getLogger("work_studio.deck_related_lineage_regen")

router = APIRouter(prefix="/api")


# ─── Pydantic response models ─────────────────────────────────

class RelatedItem(BaseModel):
    id: str
    context_id: Optional[str] = None
    name: Optional[str] = None
    category: Optional[str] = None
    doc_kind: Optional[str] = None
    similarity_score: float
    source_document_ids: Optional[List[str]] = None


class LineageDoc(BaseModel):
    id: str
    context_id: Optional[str] = None
    name: Optional[str] = None
    state: Optional[str] = None
    version_number: Optional[int] = None
    regenerated_from: Optional[str] = None
    regenerate_shield_audit_id: Optional[str] = None


class LineageResponse(BaseModel):
    document: Optional[LineageDoc] = None
    ancestors: List[LineageDoc] = Field(default_factory=list)
    descendants: List[LineageDoc] = Field(default_factory=list)
    siblings: List[LineageDoc] = Field(default_factory=list)


class RegenerateBody(BaseModel):
    prompt: Optional[str] = None


class RegenerateResponse(BaseModel):
    new_document: Dict[str, Any]
    regenerated_from: str
    shield_audit_event_id: Optional[str]
    version_number: int


# ─── Endpoints ────────────────────────────────────────────────

@router.get(
    "/decks/{document_id}/related",
    response_model=List[RelatedItem],
)
async def get_related(
    document_id: str,
    limit: int = 10,
    me: Dict[str, Any] = Depends(get_current_account),
):
    """F.6 N/A · metadata-scored related decks, account-scoped."""
    items = await deck_retrieval.get_related_decks(
        document_id=document_id, account_id=me["id"], limit=limit,
    )
    return items


@router.get(
    "/decks/{document_id}/lineage",
    response_model=LineageResponse,
)
async def get_lineage(
    document_id: str,
    me: Dict[str, Any] = Depends(get_current_account),
):
    """F.6 N/A · lineage graph, account-scoped."""
    return await deck_lineage.get_lineage(
        document_id=document_id, account_id=me["id"],
    )


@router.post(
    "/decks/{document_id}/regenerate",
    response_model=RegenerateResponse,
    responses={409: {"description": "Committed deck cannot be regenerated"}},
)
async def post_regenerate(
    document_id: str,
    body: RegenerateBody = Body(default_factory=RegenerateBody),
    me: Dict[str, Any] = Depends(get_current_account),
):
    """F.6 SHIELD-ROUTED · regeneration via canonical chokepoint.

    Raises 409 (compile-bridge-shape envelope) if source is committed.
    Creates a NEW documents row referencing parent via `regenerated_from`.
    Prior versions are never mutated or deleted.
    """
    return await deck_regenerate.regenerate_deck(
        document_id=document_id,
        account_id=me["id"],
        prompt_override=body.prompt,
    )
