"""JC-WS-DECK-A10-BACKEND-RETRIEVAL-LINEAGE-REGENERATE (2026-07-04) — regenerate (F.6 Shield-routed).

Canonical spec: /app/memory/sprints/JC_WS_DECK_A10_BACKEND_RETRIEVAL_LINEAGE_REGENERATE.md
             + /app/memory/sprints/JC_WS_DECK_A9_BACKEND_DECK_SIGNAL_EXTRACTION.md (A9 chokepoint pattern reused)

F.6 discipline-pay: SHIELD-ROUTED. Regeneration is an LLM path. Routes
through the existing SyniSense Shield chokepoint via
`contracts.get_synisense.shield_invoke` (identical to Chat and A9).
`services/synisense/shield/**` is UNTOUCHED (R10 asserts 0-diff).

Commit-lock: if the source document's `state == "committed"`, the caller
must be rejected with 409 BEFORE the Shield call fires (don't burn a
Shield audit event on a doomed request). The 409 envelope shape matches
the compile-bridge convention: `{"code": <str>, "message": <str>}` at
`detail` — same structure the compile bridge uses (see
`routers/work_studio_phase_c.py:98/130/195`).

Version chain: regenerate creates a NEW `documents` row (never mutates
the prior). Prior versions are always retrievable — R8 asserts this
explicitly. New row's fields:
  - `id`: fresh UUID
  - `context_id`: same as parent
  - `state`: "draft"
  - `version_number`: parent.version_number + 1 (default 1 if parent is version 1)
  - `regenerated_from`: parent.id
  - `regenerate_shield_audit_id`: Shield audit_id from this call
  - `extracted_text`: Shield's outbound-saw content (the LLM-regenerated body)
  - Metadata inherited from parent: category, doc_kind, source_channel, source_document_ids, data_trust
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from fastapi import HTTPException

from contracts import get_synisense  # F.6 canonical Shield chokepoint (same as A9)
from core import db, iso as _iso, now as _now

logger = logging.getLogger("work_studio.deck_regenerate")


PURPOSE = "work_studio.deck.regenerate"
CONSUMER_ID = "deck_regenerate"


REGEN_SYSTEM_PROMPT = (
    "You are regenerating a deck document. Rewrite the given deck content "
    "with improved clarity, tighter structure, and executive-ready phrasing. "
    "Preserve all factual claims and section headings. Return the regenerated "
    "content as plain text, no preface, no code fences."
)


def commit_locked_409(document_id: str) -> HTTPException:
    """Compile-bridge-shape 409 envelope for committed-state regenerate
    attempts. Envelope shape matches `routers/work_studio_phase_c.py`
    convention: `{"code": <str>, "message": <str>}`.
    """
    return HTTPException(
        status_code=409,
        detail={
            "code": "deck_already_committed",
            "message": (
                f"Document {document_id!r} is committed and cannot be regenerated. "
                "Create a new draft to iterate."
            ),
        },
    )


async def _load_and_membership_check(
    document_id: str, account_id: str,
) -> Dict[str, Any]:
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


async def regenerate_deck(
    *,
    document_id: str,
    account_id: str,
    prompt_override: Optional[str] = None,
) -> Dict[str, Any]:
    """Regenerate a deck. Fires Shield → LLM → re-id, then persists a
    NEW documents row referencing the parent via `regenerated_from`.

    Raises HTTPException(409) with compile-bridge-shape envelope if the
    source document is committed. Raises 404 if missing, 403 if
    cross-context.

    Returns the newly-created document (sanitized shape) plus Shield audit id.
    """
    parent = await _load_and_membership_check(document_id, account_id)

    # Commit-lock BEFORE Shield call. The documents collection uses
    # `lifecycle_state` (not `state`) for the committed/draft distinction
    # (per work_studio_export.py:2098 and DocumentOverlay.jsx:211/504).
    if parent.get("lifecycle_state") == "committed":
        raise commit_locked_409(document_id)

    # Compose the regeneration prompt content: parent's extracted text.
    parent_text = (parent.get("extracted_text") or parent.get("preview") or parent.get("name") or "")
    # Cap at 24000 chars (matches A9 pattern for Shield-bound content).
    content = parent_text[:24000]
    if prompt_override and isinstance(prompt_override, str):
        # Append user hint to system-msg without touching parent content.
        system_msg = REGEN_SYSTEM_PROMPT + f"\n\nAdditional guidance: {prompt_override[:1000]}"
    else:
        system_msg = REGEN_SYSTEM_PROMPT

    # Shield invocation (F.6 SHIELD-ROUTED chokepoint).
    contract = get_synisense()
    result = await contract.shield_invoke(
        purpose=PURPOSE,
        content=content,
        account_id=account_id,
        consumer_id=CONSUMER_ID,
        user_id=account_id,
        model_preference="analytical",
        internal_caller=True,
        system_msg=system_msg,
    )
    regenerated_text = result.raw.get("response") or ""
    shield_audit_id: Optional[str] = result.audit_id

    # Persist new version row.
    now = _now()
    now_iso_str = _iso(now)
    new_id = str(uuid.uuid4())
    new_version = int(parent.get("version_number") or 1) + 1
    new_doc = {
        "id": new_id,
        "context_id": parent["context_id"],
        "name": (parent.get("name") or "Regenerated deck") + f" (v{new_version})",
        # New drafts always start in `draft` lifecycle_state (per
        # DocumentOverlay.jsx committed/draft convention).
        "lifecycle_state": "draft",
        "version_number": new_version,
        "regenerated_from": document_id,
        "regenerate_shield_audit_id": shield_audit_id,
        "extracted_text": regenerated_text,
        "extracted_chars": len(regenerated_text),
        # Inherit metadata from parent.
        "category": parent.get("category"),
        "doc_kind": parent.get("doc_kind"),
        "source_channel": parent.get("source_channel"),
        "source_document_ids": list(parent.get("source_document_ids") or []),
        "data_trust": parent.get("data_trust", "unrated"),
        "uploaded_by_email": parent.get("uploaded_by_email"),
        "created_at": now_iso_str,
        "updated_at": now_iso_str,
    }
    await db.documents.insert_one(new_doc)
    # Strip Mongo internals if any before returning.
    new_doc.pop("_id", None)
    return {
        "new_document": new_doc,
        "regenerated_from": document_id,
        "shield_audit_event_id": shield_audit_id,
        "version_number": new_version,
    }
