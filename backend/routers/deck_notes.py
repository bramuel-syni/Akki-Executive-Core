"""JC-WS-DECK-A8-BACKEND-PERSISTENCE (2026-07-02) — deck_notes CRUD.

Canonical spec: /app/memory/rules/TAB_HONESTY_RULE.md
             + /app/memory/sprints/JC_WS_DECK_A8_BACKEND_PERSISTENCE.md

Account-scoped private deck notes. User-authored content — NO LLM path,
NO Shield routing (F.6 discipline-pay N/A).

Endpoints (all under `/api/deck-notes/{document_id}`):
  GET    — returns {content, updated_at} or 404
  PUT    — upsert; body {content: str}; returns updated record
  DELETE — remove; returns 204

All routes filter by authenticated `account_id`. Cross-account queries
return 404 (implicit isolation via account_id scoping — Account B's GET
for Account A's document_id simply misses the compound-key lookup).
Unauthenticated requests are rejected by `Depends(get_current_account)`.
"""
from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field

from core import db, get_current_account, iso as _iso, now as _now


log = logging.getLogger("work_studio.deck_notes")

router = APIRouter(prefix="/api")


class DeckNotePutBody(BaseModel):
    content: str = Field(..., description="Full notes content (user-authored plain text).")


class DeckNoteResponse(BaseModel):
    document_id: str
    content: str
    updated_at: str


@router.get(
    "/deck-notes/{document_id}",
    response_model=Optional[DeckNoteResponse],
    responses={404: {"description": "No notes exist for this document under the authenticated account."}},
)
async def get_deck_note(
    document_id: str,
    me: Dict[str, Any] = Depends(get_current_account),
):
    row = await db.deck_notes.find_one(
        {"account_id": me["id"], "document_id": document_id},
        {"_id": 0, "content": 1, "updated_at": 1, "document_id": 1},
    )
    if not row:
        raise HTTPException(status_code=404, detail="deck_note_not_found")
    return {
        "document_id": document_id,
        "content": row.get("content", ""),
        "updated_at": row.get("updated_at") or _iso(_now()),
    }


@router.put(
    "/deck-notes/{document_id}",
    response_model=DeckNoteResponse,
)
async def put_deck_note(
    document_id: str,
    body: DeckNotePutBody,
    me: Dict[str, Any] = Depends(get_current_account),
):
    now = _now()
    now_iso = _iso(now)
    existing = await db.deck_notes.find_one(
        {"account_id": me["id"], "document_id": document_id},
        {"_id": 0, "id": 1, "created_at": 1},
    )
    if existing:
        await db.deck_notes.update_one(
            {"account_id": me["id"], "document_id": document_id},
            {"$set": {"content": body.content, "updated_at": now_iso}},
        )
    else:
        await db.deck_notes.insert_one({
            "id": str(uuid.uuid4()),
            "account_id": me["id"],
            "document_id": document_id,
            "content": body.content,
            "created_at": now_iso,
            "updated_at": now_iso,
        })
    return {
        "document_id": document_id,
        "content": body.content,
        "updated_at": now_iso,
    }


@router.delete(
    "/deck-notes/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_deck_note(
    document_id: str,
    me: Dict[str, Any] = Depends(get_current_account),
):
    await db.deck_notes.delete_one(
        {"account_id": me["id"], "document_id": document_id},
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
