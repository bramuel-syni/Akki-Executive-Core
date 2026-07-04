"""JC-WS-DECK-A9-BACKEND-DECK-SIGNAL-EXTRACTION (2026-07-04) — deck_signals CRUD + extract.

Canonical spec: /app/memory/sprints/JC_WS_DECK_A9_BACKEND_DECK_SIGNAL_EXTRACTION.md

F.6 discipline-pay: FULL. Extract endpoint routes through the existing
SyniSense Shield chokepoint via `services.synisense.deck_signal_extraction`
(which imports `contracts.get_synisense`). NO direct LLM SDK import.

Endpoints (all under `/api/decks/{document_id}/signals`):
  POST  /extract         — fire extraction (LLM path via Shield); returns record
  GET   (base)           — fetch current signals record + timestamps + class + audit_id
  PATCH /{signal_id}     — toggle `addressed` (no LLM re-invocation)

Auth model:
  - Unauthenticated → 401/403 (auth dep + CSRF gate).
  - Non-member of document's context → 403.
  - Document not found → 404.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from core import db, get_current_account, iso as _iso, now as _now
from services.synisense.deck_signal_extraction import (
    extract_deck_signals, signals_to_dict,
)


log = logging.getLogger("work_studio.deck_signals")

router = APIRouter(prefix="/api")


# ─── Pydantic surfaces ─────────────────────────────────────────

class SignalItem(BaseModel):
    id: str
    text: str
    category: str
    confidence: float
    addressed: bool = False


class DeckSignalsResponse(BaseModel):
    document_id: str
    signals: List[SignalItem] = Field(default_factory=list)
    derivation_class: Optional[str] = None
    shield_audit_event_id: Optional[str] = None
    source_deck_updated_at: Optional[str] = None
    updated_at: Optional[str] = None
    created_at: Optional[str] = None


class SignalPatchBody(BaseModel):
    addressed: bool


# ─── Shared helper ─────────────────────────────────────────────

async def _load_doc_and_check_membership(
    document_id: str, account_id: str,
) -> Dict[str, Any]:
    """Fetch document + verify current account is a member of its context."""
    doc = await db.documents.find_one({"id": document_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="document_not_found")
    context_id = doc.get("context_id")
    if not context_id:
        raise HTTPException(status_code=404, detail="document_not_found")
    membership = await db.memberships.find_one(
        {"context_id": context_id, "account_id": account_id, "status": "active"},
        {"_id": 0},
    )
    if not membership:
        raise HTTPException(status_code=403, detail="Not a member of this context")
    return doc


# ─── Index bootstrap ───────────────────────────────────────────

_INDEX_ENSURED = False


async def _ensure_deck_signals_index() -> None:
    """Idempotent — creates the unique compound index on first call."""
    global _INDEX_ENSURED
    if _INDEX_ENSURED:
        return
    try:
        await db.deck_signals.create_index(
            [("account_id", 1), ("document_id", 1)],
            unique=True,
            name="deck_signals_account_doc_uq",
        )
        _INDEX_ENSURED = True
    except Exception as e:  # noqa: BLE001
        log.warning("deck_signals index bootstrap failed: %s", e)


# ─── Endpoints ────────────────────────────────────────────────

@router.post(
    "/decks/{document_id}/signals/extract",
    response_model=DeckSignalsResponse,
)
async def post_extract(
    document_id: str,
    me: Dict[str, Any] = Depends(get_current_account),
):
    """Fire deck-signal extraction. LLM path via Shield chokepoint."""
    await _ensure_deck_signals_index()
    doc = await _load_doc_and_check_membership(document_id, me["id"])
    extracted = await extract_deck_signals(
        deck_document=doc, account_context={"account_id": me["id"]},
    )
    payload = signals_to_dict(extracted)
    now_iso = _iso(_now())
    # Upsert record — one signal set per (account_id, document_id).
    existing = await db.deck_signals.find_one(
        {"account_id": me["id"], "document_id": document_id},
        {"_id": 0, "id": 1, "created_at": 1},
    )
    if existing:
        await db.deck_signals.update_one(
            {"account_id": me["id"], "document_id": document_id},
            {"$set": {**payload, "updated_at": now_iso}},
        )
        created_at = existing.get("created_at") or now_iso
    else:
        record = {
            "id": str(uuid.uuid4()),
            **payload,
            "created_at": now_iso,
            "updated_at": now_iso,
        }
        await db.deck_signals.insert_one(record)
        created_at = now_iso
    return {
        **payload,
        "created_at": created_at,
        "updated_at": now_iso,
    }


@router.get(
    "/decks/{document_id}/signals",
    response_model=Optional[DeckSignalsResponse],
)
async def get_signals(
    document_id: str,
    me: Dict[str, Any] = Depends(get_current_account),
):
    await _ensure_deck_signals_index()
    _ = await _load_doc_and_check_membership(document_id, me["id"])
    row = await db.deck_signals.find_one(
        {"account_id": me["id"], "document_id": document_id},
        {"_id": 0},
    )
    if not row:
        # Deterministic empty response — FE renders "Extract signals" affordance.
        return {
            "document_id": document_id,
            "signals": [],
            "derivation_class": None,
            "shield_audit_event_id": None,
            "source_deck_updated_at": None,
            "updated_at": None,
            "created_at": None,
        }
    return row


@router.patch(
    "/decks/{document_id}/signals/{signal_id}",
    response_model=DeckSignalsResponse,
)
async def patch_signal(
    document_id: str,
    signal_id: str,
    body: SignalPatchBody,
    me: Dict[str, Any] = Depends(get_current_account),
):
    await _ensure_deck_signals_index()
    _ = await _load_doc_and_check_membership(document_id, me["id"])
    row = await db.deck_signals.find_one(
        {"account_id": me["id"], "document_id": document_id},
        {"_id": 0},
    )
    if not row:
        raise HTTPException(status_code=404, detail="deck_signals_not_found")
    signals = row.get("signals") or []
    updated = False
    for s in signals:
        if s.get("id") == signal_id:
            s["addressed"] = body.addressed
            updated = True
            break
    if not updated:
        raise HTTPException(status_code=404, detail="signal_id_not_found")
    now_iso = _iso(_now())
    await db.deck_signals.update_one(
        {"account_id": me["id"], "document_id": document_id},
        {"$set": {"signals": signals, "updated_at": now_iso}},
    )
    row["signals"] = signals
    row["updated_at"] = now_iso
    return row
