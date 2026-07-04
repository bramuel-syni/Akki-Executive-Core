"""JC-WS-DECK-A6-BACKEND-SOURCE-CONTEXT-PATCH (2026-07-04) — source_context CRUD.

Canonical spec: /app/memory/sprints/JC_WS_DECK_A6_BACKEND_SOURCE_CONTEXT_PATCH.md
             + /app/memory/rules/TAB_HONESTY_RULE.md
             + /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A6

Complements A6-MVP frontend (DECK-040 + DECK-043 shipped 2026-07-02) by
adding the backend PATCH endpoint that persists source-context edits
on Deck documents. Unblocks DECK-044 (the last uncovered A6 story).

F.6 discipline-pay: N/A · user-authored content, no LLM path, no Shield
routing required. This module contains NO `shield_invoke`, NO `synisense`
reference, NO LLM SDK import (positive AST assertion enforced by the
A6-backend proving slice R10).

Endpoints (all under `/api/deck-source-context/{document_id}`):
  GET   — returns {document_id, content, updated_at, updated_by} or 404
          when document missing. Content=null when never set (deterministic
          FE render — no error round-trip for empty state).
  PATCH — upserts source_context + timestamps + updated_by; body {content: str};
          returns updated record.

Auth model:
  - Unauthenticated → 401 (via `Depends(get_current_account)`).
  - Not a member of the document's context → 403.
  - Document not found → 404.

Persistence (additive schema on the `documents` collection):
  - source_context             : str | null (up to 8000 chars, trimmed).
  - source_context_updated_at  : ISO8601 UTC string (only churns on
                                 source-context bearing PATCHes).
  - source_context_updated_by  : account_id (str) of last saver.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from core import db, get_current_account, iso as _iso, now as _now


log = logging.getLogger("work_studio.deck_source_context")

router = APIRouter(prefix="/api")


MAX_SOURCE_CONTEXT_CHARS = 8000  # matches notes cap for consistency


class DeckSourceContextPatchBody(BaseModel):
    content: str = Field(..., description="Full source-context content (user-authored plain text).")


class DeckSourceContextResponse(BaseModel):
    document_id: str
    content: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None


async def _load_doc_and_check_membership(
    document_id: str, account_id: str,
) -> Dict[str, Any]:
    """Fetch the document and verify the current account has active
    membership in its context. Raises HTTPException(404) if the document
    doesn't exist, 403 if the account is not a member of the context.

    Returns the document dict on success.
    """
    doc = await db.documents.find_one(
        {"id": document_id},
        {"_id": 0},
    )
    if not doc:
        raise HTTPException(status_code=404, detail="document_not_found")
    context_id = doc.get("context_id")
    if not context_id:
        # A document without a context_id is a schema violation; treat as 404
        # for the caller (do not leak internal state).
        raise HTTPException(status_code=404, detail="document_not_found")
    membership = await db.memberships.find_one(
        {"context_id": context_id, "account_id": account_id, "status": "active"},
        {"_id": 0},
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this context")
    return doc


@router.get(
    "/deck-source-context/{document_id}",
    response_model=DeckSourceContextResponse,
)
async def get_source_context(
    document_id: str,
    me: Dict[str, Any] = Depends(get_current_account),
):
    doc = await _load_doc_and_check_membership(document_id, me["id"])
    return {
        "document_id": document_id,
        "content": doc.get("source_context"),
        "updated_at": doc.get("source_context_updated_at"),
        "updated_by": doc.get("source_context_updated_by"),
    }


@router.patch(
    "/deck-source-context/{document_id}",
    response_model=DeckSourceContextResponse,
)
async def patch_source_context(
    document_id: str,
    body: DeckSourceContextPatchBody,
    me: Dict[str, Any] = Depends(get_current_account),
):
    _ = await _load_doc_and_check_membership(document_id, me["id"])
    # Trim + cap. Empty string clears the field (matches notes semantics:
    # "empty string clears; non-empty stores trimmed").
    content_clean = (body.content or "").strip()[:MAX_SOURCE_CONTEXT_CHARS]
    now_iso = _iso(_now())
    set_fields: Dict[str, Any] = {
        "source_context": content_clean or None,
        "source_context_updated_at": now_iso,
        "source_context_updated_by": me["id"],
        # Also bump the doc's general updated_at so any adjacent listing
        # surface reflects that the doc changed (matches the notes-PATCH
        # convention in routers/documents.py).
        "updated_at": now_iso,
    }
    await db.documents.update_one(
        {"id": document_id},
        {"$set": set_fields},
    )
    return {
        "document_id": document_id,
        "content": content_clean or None,
        "updated_at": now_iso,
        "updated_by": me["id"],
    }
