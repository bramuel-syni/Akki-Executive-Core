"""
Phase C.3 — Work Studio: From-source bridge.

Bridges Solva sessions and chat artefacts into the kind-aware Work
Studio storage so the existing block composer + Enhance + Export can
operate on Solva-originated artefacts without parallel pipelines.

  POST /api/contexts/{cid}/work-studio/from-source

Body shape:
  {
    source_type: "solva_session" | "chat_artefact",
    source_id:   str,
    kind:        "briefing" | "deck" | "report",
    company_label: str (optional),
    document_type: str (optional),
    programme:     str | null
  }

What the route does, atomically:
  1. Resolves the source. solva_session → require synthesis.body.
                          chat_artefact → assemble Solva-shaped envelope
                          from the chat's assistant messages.
  2. Builds a Brief via C.1 `build_brief_from_solva` at depth=board_summary,
     fidelity=low (board-edit-friendly seed; export fidelity stays an
     independent choice at export time).
  3. Persists the Brief via C.2 `ensure_brief_persisted` — yields a
     stable `brief_id`.
  4. Inserts a kind-row in db.boardpacks / db.decks / db.reports with:
       - id, context_id, account_id, kind-specific metadata
       - title, opening_paragraph, body  (so the existing
         _seed_blocks_from_artefact picks them up cleanly when the user
         first opens the composer)
       - top-level brief_id field      (per the user's directive — no
         nested metadata; subsequent reads are simpler)
       - origin = {source_type, source_id}    (audit-friendly trail)
  5. Returns:
       {
         kind, artefact_id, brief_id,
         redirect_url: "/app/studio/composer/{kind}/{artefact_id}"
       }

This route does NOT touch the C.1 generators or Solva engines. It
reads and writes only.

Chunk 5 — 2026-05-13 — sister endpoint
  POST /api/contexts/{cid}/work-studio/artefacts
adds the three create-from-Work-Studio paths the QA report flagged
(WS-R09 / R10 / R11 / R13 / R14): create a draft Deck or draft Report
from a Blank starting point, an existing Work-Studio brief, or an
external (already-uploaded) document. Inserts into the same
db.decks / db.reports collections used by the block composer.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional
from contracts.responses import (
    ArtefactRedirectResponse,
)

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator

from core import db, require_context_membership, write_audit
from work_studio import (
    build_brief_from_solva,
    ensure_brief_persisted,
    brief_to_dict,
)

logger = logging.getLogger("akki.work_studio.from_source")

router = APIRouter(prefix="/api")

_VALID_KINDS = {"briefing", "deck", "report"}
_VALID_SOURCES = {"solva_session", "chat_artefact"}

# Kind-aware Mongo collection map. Mirrors `studio_blocks._artefact_collection`.
_KIND_COLLECTION = {
    "briefing": "boardpacks",
    "deck": "decks",
    "report": "reports",
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Brief → artefact prose assembly (so studio_blocks._seed_blocks_from_artefact
# does the right thing on first composer open).
# ---------------------------------------------------------------------------
def _assemble_prose(brief_dict: Dict[str, Any]) -> Dict[str, str]:
    """Flatten the Brief sections into title / opening_paragraph / body
    that the existing seed-blocks helper already understands.

    The block composer's `_seed_blocks_from_artefact` reads:
       briefing → title, opening_paragraph, items[], body
       deck     → title, slides[], body
       report   → title, body
    We hand it title + opening_paragraph + body and let the seeder
    paragraph-split the body. Sections with kicker labels become inline
    headings via blank-line breaks (the splitter respects them)."""
    title = brief_dict.get("title") or "Untitled brief"
    opening = brief_dict.get("cover_lead_paragraph") or ""
    chunks: List[str] = []
    for sec in brief_dict.get("sections") or []:
        sec_title = (sec.get("title") or "").strip()
        kicker = (sec.get("kicker") or "").strip()
        if sec_title:
            chunks.append(sec_title)
        if kicker:
            chunks.append(f"({kicker})")
        for para in sec.get("body_paragraphs") or []:
            if para and para.strip():
                chunks.append(para.strip())
        for b in sec.get("bullets") or []:
            if b and b.strip():
                chunks.append(f"• {b.strip()}")
        for tbl in sec.get("tables") or []:
            tbl_title = (tbl.get("title") or "").strip()
            if tbl_title:
                chunks.append(tbl_title)
            headers = tbl.get("headers") or []
            if headers:
                chunks.append(" | ".join(str(h) for h in headers))
            for row in tbl.get("rows") or []:
                chunks.append(" | ".join(str(c) for c in row))
        chunks.append("")  # blank line — paragraph break for the seeder
    closing = brief_dict.get("closing_recap") or ""
    if closing:
        chunks.append(closing)
    body = "\n\n".join(c for c in chunks if c.strip())
    return {
        "title": title,
        "opening_paragraph": opening,
        "body": body,
    }


# ---------------------------------------------------------------------------
# Request / response models
# ---------------------------------------------------------------------------
class FromSourceRequest(BaseModel):
    source_type: Literal["solva_session", "chat_artefact"]
    source_id: str = Field(..., min_length=1, max_length=128)
    kind: Literal["briefing", "deck", "report"]
    company_label: str = Field("Akki", max_length=80)
    document_type: str = Field("", max_length=80)
    programme: Optional[str] = Field(None, max_length=80)


# ---------------------------------------------------------------------------
# Source resolvers
# ---------------------------------------------------------------------------
async def _resolve_solva_session(account_id: str, source_id: str) -> Dict[str, Any]:
    session = await db.solva_v2_sessions.find_one(
        {"id": source_id, "account_id": account_id},
    )
    if not session:
        raise HTTPException(status_code=404, detail="solva_session_not_found")
    if not (session.get("synthesis") or {}).get("body"):
        raise HTTPException(
            status_code=409,
            detail={
                "code": "synthesis_not_ready",
                "message": ("Run this Solva session through synthesis "
                            "before composing from it."),
            },
        )
    return session


async def _resolve_chat_envelope(account_id: str, source_id: str) -> Dict[str, Any]:
    """Reduce a chat down to a Solva-shaped envelope so the C.1 builder
    works without a parallel code path. Mirrors the same shaping the C.1
    export endpoint already does for `chat_artefact`.

    Chunk 6 (2026-05-13, WS-R19): the returned envelope now carries
    `title_override` set to the chat's own title — `build_brief_from_solva`
    consumes it to set the brief.title verbatim (no submodule prefix,
    200-char cap). This stops the DOCX cover from displaying e.g.
    `"Clarity Read: Q3 board meeting — strategic review of expansion plans into…"`
    truncated mid-word; the user sees their full chat title instead.
    """
    chat = await db.chats.find_one({"id": source_id, "account_id": account_id})
    if not chat:
        raise HTTPException(status_code=404, detail="chat_not_found")
    msgs_cursor = db.chat_messages.find({"chat_id": source_id}).sort("created_at", 1)
    msgs = await msgs_cursor.to_list(2000)
    full = "\n\n".join((m.get("content") or "").strip()
                       for m in msgs if m.get("role") == "assistant")
    if not full.strip():
        raise HTTPException(
            status_code=409,
            detail={
                "code": "chat_empty",
                "message": "This chat has no assistant content to compose from yet.",
            },
        )
    chat_title = (chat.get("title") or "").strip()
    return {
        "id": chat["id"],
        "submodule": "seek_clarity",
        "intent": chat_title or "Chat artefact",
        # Chunk 6 — chat title becomes the brief title verbatim.
        "title_override": chat_title or None,
        "synthesis": {
            "body": full,
            "claims": [],
            "recommendations": [],
            "validation": {
                "verdict": "informational", "confidence": 0,
                "validator_provider": "—", "validator_model": "—",
            },
        },
    }


# ---------------------------------------------------------------------------
# Endpoint
# ---------------------------------------------------------------------------
@router.post("/contexts/{context_id}/work-studio/from-source", response_model=Optional[ArtefactRedirectResponse])
async def create_from_source(
    context_id: str,
    body: FromSourceRequest,
    ctx: Dict[str, Any] = Depends(require_context_membership()),
):
    if body.kind not in _VALID_KINDS:
        raise HTTPException(status_code=422, detail="unsupported_kind")
    if body.source_type not in _VALID_SOURCES:
        raise HTTPException(status_code=422, detail="unsupported_source_type")

    account = ctx["account"]
    account_id = account["id"]

    # 1) Resolve source -----------------------------------------------------
    if body.source_type == "solva_session":
        envelope = await _resolve_solva_session(account_id, body.source_id)
    else:
        envelope = await _resolve_chat_envelope(account_id, body.source_id)

    # 2) Build Brief at LOW fidelity (per user's call #2 — composer-edit
    # friendly seed; export fidelity is independent at export time).
    document_type = body.document_type or {
        "briefing": "Board Briefing",
        "deck": "Board Deck",
        "report": "Report",
    }[body.kind]

    brief = build_brief_from_solva(
        envelope,
        company_label=body.company_label or "Akki",
        document_type=document_type,
        programme=body.programme,
        depth="board_summary",
        fidelity="low",
        # Chunk 6 (2026-05-13, WS-R19): thread the chat title verbatim
        # when present so the cover renders the user's own words.
        title_override=envelope.get("title_override"),
    )

    # 3) Persist Brief — yields a stable brief_id (idempotent).
    parent = await ensure_brief_persisted(
        db,
        brief=brief,
        account_id=account_id,
        context_id=context_id,
        source_type=body.source_type,
        source_id=body.source_id,
    )
    brief_id = parent["id"]
    revision_id = parent["active_revision_id"]

    # 4) Insert kind-row.  The block composer's existing
    # _seed_blocks_from_artefact reads title / opening_paragraph / body
    # — assemble them from the Brief snapshot now.
    brief_dict = brief_to_dict(brief)
    prose = _assemble_prose(brief_dict)
    artefact_id = str(uuid.uuid4())
    now = _now_iso()

    artefact_row: Dict[str, Any] = {
        "id": artefact_id,
        "context_id": context_id,
        "account_id": account_id,
        "title": prose["title"],
        "opening_paragraph": prose["opening_paragraph"],
        "body": prose["body"],
        "status": "draft",
        # Top-level brief_id pointer per the user's directive.
        "brief_id": brief_id,
        "active_revision_id": revision_id,
        # Audit-friendly trail of where this came from.
        "origin": {
            "source_type": body.source_type,
            "source_id": body.source_id,
            "company_label": body.company_label or "Akki",
            "document_type": document_type,
            "programme": body.programme,
        },
        "created_at": now,
        "updated_at": now,
    }
    # Decks have a few legacy fields the existing UI expects; populate
    # them defensively with the Brief title so list views render cleanly.
    if body.kind == "deck":
        artefact_row["slides"] = []
        artefact_row["subject"] = prose["title"]
    if body.kind == "report":
        artefact_row["subject"] = prose["title"]

    coll_name = _KIND_COLLECTION[body.kind]
    coll = getattr(db, coll_name)
    await coll.insert_one(artefact_row)

    # 5) Audit and return.
    try:
        await write_audit(
            context_id=context_id, account_id=account_id,
            action="work_studio.from_source.created",
            resource_type=f"work_studio_artefact.{body.kind}",
            resource_id=artefact_id,
            metadata={
                "kind": body.kind,
                "artefact_id": artefact_id,
                "brief_id": brief_id,
                "source_type": body.source_type,
                "source_id": body.source_id,
            },
        )
    except Exception:
        logger.exception("from_source: audit write failed (non-fatal)")

    return {
        "kind": body.kind,
        "artefact_id": artefact_id,
        "brief_id": brief_id,
        "active_revision_id": revision_id,
        "redirect_url": f"/app/studio/composer/{body.kind}/{artefact_id}",
    }



# ═════════════════════════════════════════════════════════════════════════
# Chunk 5 (2026-05-13) — Create-from-Work-Studio.
#
# Sister endpoint to /from-source. Where /from-source seeds a draft from
# an existing Solva session or chat, /artefacts creates a draft from one
# of three Work-Studio-native sources:
#
#   - blank              — empty body, user composes from scratch
#   - brief              — references a db.work_studio_briefs row by uuid
#   - external_document  — references a db.documents row by uuid
#
# Only `deck` and `report` kinds are accepted here. `briefing` artefacts
# in Work Studio go through the C.1 ExportModal pipeline (entirely
# separate code path); this endpoint refuses `kind=briefing` to avoid
# accidental double-creation of brief rows.
# ═════════════════════════════════════════════════════════════════════════
_VALID_CREATE_KINDS = {"deck", "report"}
_VALID_CREATE_SOURCES = {"blank", "brief", "external_document"}


class CreateArtefactRequest(BaseModel):
    kind: Literal["deck", "report"]
    title: str = Field(..., min_length=1, max_length=200)
    source: Literal["blank", "brief", "external_document"]
    # JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE (2026-07-02) — DECK-018 +
    # DECK-022 multi-select briefs / documents. The new plural fields
    # are the primary contract. The singular fields (below) are kept
    # for BACKWARD COMPAT for one release — the `model_validator`
    # coerces singular → plural pre-flight and logs a deprecation
    # WARNING every time a client sends the singular form (visible in
    # aggregated log grep so we know when to remove).
    #
    # Aggregate-id form (`briefing::<uuid>`) still tolerated per Chunk 5.
    source_brief_ids: List[str] = Field(default_factory=list, max_length=25)
    source_document_ids: List[str] = Field(default_factory=list, max_length=25)
    # DEPRECATED: singular forms. Kept for backward-compat only.
    source_brief_id: Optional[str] = Field(None, max_length=128)
    source_document_id: Optional[str] = Field(None, max_length=128)

    @model_validator(mode="after")
    def _coerce_singular_to_plural(self) -> "CreateArtefactRequest":
        """Coerce legacy singular fields into the plural arrays.

        Emits a WARNING log so ops can grep for `create_artefact.deprecated_singular_field`
        and know when the last client migrated off the singular form.
        """
        if self.source_brief_id and not self.source_brief_ids:
            self.source_brief_ids = [self.source_brief_id]
            logger.warning(
                "create_artefact.deprecated_singular_field field=source_brief_id "
                "kind=%s source=%s — migrate client to source_brief_ids plural.",
                self.kind, self.source,
            )
        if self.source_document_id and not self.source_document_ids:
            self.source_document_ids = [self.source_document_id]
            logger.warning(
                "create_artefact.deprecated_singular_field field=source_document_id "
                "kind=%s source=%s — migrate client to source_document_ids plural.",
                self.kind, self.source,
            )
        return self


def _strip_agg_prefix(raw: str, expected_kind: str) -> str:
    """Tolerate the aggregate-id form (`<kind>::<uuid>`) coming from
    the briefings/aggregates listing. Returns the raw uuid if a
    prefix is present, otherwise returns the input unchanged."""
    if not raw or "::" not in raw:
        return raw or ""
    prefix, _, suffix = raw.partition("::")
    if prefix == expected_kind:
        return suffix
    # Unknown prefix — return as-is so the downstream lookup fails
    # with a clean 404 rather than silently truncating.
    return raw


@router.post("/contexts/{context_id}/work-studio/artefacts", status_code=201, response_model=Optional[ArtefactRedirectResponse])
async def create_work_studio_artefact(
    context_id: str,
    body: CreateArtefactRequest,
    ctx: Dict[str, Any] = Depends(require_context_membership()),
):
    """Create a draft Deck or Report from one of three sources.

    The artefact row is inserted into the same kind-aware collection
    (`db.decks` / `db.reports`) the block composer reads from. The
    response carries a `redirect_url` pointing at the composer surface
    so the frontend can hard-redirect after the toast.

    422 paths:
      - `kind` is not deck/report (briefing is handled elsewhere)
      - `source` is not blank/brief/external_document
      - `source=brief` with no `source_brief_id`
      - `source=external_document` with no `source_document_id`

    404 paths:
      - `source_brief_id` doesn't resolve in this account/context
      - `source_document_id` doesn't resolve in this context
    """
    # Defence-in-depth — Pydantic Literal already gates these but
    # explicit raise gives a friendlier error.
    if body.kind not in _VALID_CREATE_KINDS:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Unsupported kind `{body.kind}`. "
                f"Work Studio create accepts: {sorted(_VALID_CREATE_KINDS)}."
            ),
        )
    if body.source not in _VALID_CREATE_SOURCES:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Unsupported source `{body.source}`. "
                f"Allowed: {sorted(_VALID_CREATE_SOURCES)}."
            ),
        )

    account = ctx["account"]
    account_id = account["id"]
    title = body.title.strip()

    description: Optional[str] = None
    body_text: str = ""
    brief_ids: List[str] = []
    document_ids: List[str] = []

    # ── Source-specific resolution ────────────────────────────────────
    if body.source == "brief":
        if not body.source_brief_ids:
            raise HTTPException(
                status_code=422,
                detail=(
                    "`source_brief_ids` is required when source=brief "
                    "(or the deprecated singular `source_brief_id`)."
                ),
            )
        # JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE (2026-07-02) — DECK-018
        # multi-select briefs. Iterate the plural array; concatenate each
        # brief's active-revision prose with a `\n\n---\n\n` divider so
        # the composer opens with a coherent multi-brief seed the user
        # can further edit.
        prose_parts: List[str] = []
        title_parts: List[str] = []
        for raw_bid in body.source_brief_ids:
            bid = _strip_agg_prefix(raw_bid, "briefing")
            brief = await db.work_studio_briefs.find_one(
                {"id": bid, "context_id": context_id, "account_id": account_id},
                {"_id": 0},
            )
            if not brief:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Brief `{bid}` not found in this workspace "
                        f"(or you don't have access)."
                    ),
                )
            brief_ids.append(brief["id"])
            title_parts.append(brief.get("title") or "Untitled brief")
            revision = await db.work_studio_brief_revisions.find_one(
                {"id": brief.get("active_revision_id"), "brief_id": brief["id"]},
                {"_id": 0, "snapshot": 1},
            )
            snapshot = (revision or {}).get("snapshot") or {}
            if snapshot:
                prose = _assemble_prose(snapshot)
                body_piece = prose["body"] or ""
                if prose.get("opening_paragraph"):
                    body_piece = (
                        prose["opening_paragraph"].strip()
                        + ("\n\n" + body_piece if body_piece else "")
                    )
                if body_piece:
                    # Prepend a brief title header when combining multiple briefs.
                    if len(body.source_brief_ids) > 1:
                        body_piece = f"## {brief.get('title') or 'Untitled brief'}\n\n{body_piece}"
                    prose_parts.append(body_piece)
        body_text = "\n\n---\n\n".join(prose_parts) if prose_parts else ""
        description = (
            f"Composed from brief: {title_parts[0]}" if len(title_parts) == 1
            else f"Composed from {len(title_parts)} briefs"
        )

    elif body.source == "external_document":
        if not body.source_document_ids:
            raise HTTPException(
                status_code=422,
                detail=(
                    "`source_document_ids` is required when "
                    "source=external_document (or the deprecated singular "
                    "`source_document_id`)."
                ),
            )
        # JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE (2026-07-02) — DECK-022
        # multi-select external documents. Iterate the plural array;
        # seed body from each doc's akki_summary / preview / stub.
        seed_parts: List[str] = []
        doc_title_parts: List[str] = []
        for did in body.source_document_ids:
            doc = await db.documents.find_one(
                {"id": did, "context_id": context_id},
                {
                    "_id": 0, "id": 1, "name": 1, "preview": 1,
                    "akki_summary": 1, "extracted_text": 1,
                },
            )
            if not doc:
                raise HTTPException(
                    status_code=404,
                    detail=(
                        f"Document `{did}` not found in this workspace."
                    ),
                )
            document_ids.append(doc["id"])
            doc_title_parts.append(doc.get("name") or "Untitled document")
            seed_text = (doc.get("akki_summary") or doc.get("preview") or "").strip()
            if not seed_text:
                seed_text = f"Composed from document: {doc.get('name') or 'Untitled document'}."
            if len(body.source_document_ids) > 1:
                seed_text = f"## {doc.get('name') or 'Untitled document'}\n\n{seed_text}"
            seed_parts.append(seed_text)
        body_text = "\n\n---\n\n".join(seed_parts)
        description = (
            f"Composed from document: {doc_title_parts[0]}" if len(doc_title_parts) == 1
            else f"Composed from {len(doc_title_parts)} documents"
        )

    else:
        # blank — composer's seed renders title + a fallback paragraph;
        # no body needed.
        description = "Draft started from blank."

    # ── Insert ─────────────────────────────────────────────────────────
    artefact_id = str(uuid.uuid4())
    now = _now_iso()
    # JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE (2026-07-02) — plural
    # arrays land on the DB row. Singular `brief_id` + `source_document_id`
    # are kept as backward-compat mirrors of the FIRST element (so any
    # downstream reader that still reads the singular field sees a
    # sensible value); a future dispatch will drop them once the audit
    # shows zero singular reads remain.
    brief_id_singular = brief_ids[0] if brief_ids else None
    document_id_singular = document_ids[0] if document_ids else None
    artefact_row: Dict[str, Any] = {
        "id": artefact_id,
        "context_id": context_id,
        "account_id": account_id,
        "title": title,
        "description": description,
        "body": body_text,
        "status": "draft",
        "source": body.source,
        # Plural (new primary contract, A2)
        "brief_ids": brief_ids,
        "source_document_ids": document_ids,
        # Singular (backward-compat mirrors of first element, to be
        # removed in a follow-on dispatch)
        "brief_id": brief_id_singular,
        "source_document_id": document_id_singular,
        "origin": {
            "source": body.source,
            "brief_ids": brief_ids,
            "document_ids": document_ids,
            # Backward-compat mirrors
            "brief_id": brief_id_singular,
            "document_id": document_id_singular,
        },
        "created_at": now,
        "updated_at": now,
    }
    # Kind-specific defaults the listing surface expects.
    if body.kind == "deck":
        artefact_row["slides"] = []
        artefact_row["subject"] = title
    if body.kind == "report":
        artefact_row["subject"] = title
        # The block composer reads `body` for reports; chain stays
        # empty here (the multi-tier review-chain flow is a separate
        # path in routers/cycle.py — Work-Studio-created reports are
        # composer artefacts, not chain artefacts).
        artefact_row["chain"] = []

    coll_name = _KIND_COLLECTION[body.kind]
    coll = getattr(db, coll_name)
    await coll.insert_one(artefact_row)

    # ── Audit ──────────────────────────────────────────────────────────
    try:
        await write_audit(
            context_id=context_id, account_id=account_id,
            action="work_studio.artefact.created",
            resource_type=f"work_studio_artefact.{body.kind}",
            resource_id=artefact_id,
            metadata={
                "kind": body.kind,
                "source": body.source,
                "brief_ids": brief_ids,
                "document_ids": document_ids,
                # Backward-compat mirrors.
                "brief_id": brief_id_singular,
                "document_id": document_id_singular,
                "title": title,
            },
        )
    except Exception:
        logger.exception("create_work_studio_artefact: audit write failed (non-fatal)")

    return {
        "kind": body.kind,
        "artefact_id": artefact_id,
        "brief_ids": brief_ids,
        "document_ids": document_ids,
        # Backward-compat singular mirrors of the first element (removed
        # in a follow-on dispatch once no client reads the singular).
        "brief_id": brief_id_singular,
        "document_id": document_id_singular,
        "redirect_url": f"/app/studio/composer/{body.kind}/{artefact_id}",
    }



# ═════════════════════════════════════════════════════════════════════════
# T3.1 (2026-05-25) — Add to Work Studio from a Document Journal item.
#
# Implements spec §4.A → D5: the Document Journal "Add to Work Studio"
# modal asks the user to choose one of five artefact types and creates
# a draft artefact card seeded from the chosen document. Differs from
# `/work-studio/artefacts` above (which is deck/report only) in that
# the new endpoint accepts the full 5-kind taxonomy from D5 — Board
# Pack, Minutes, Committee Pack, Deck, Report — and lands the row in
# the unified `work_studio_exports` aggregate so the Work Studio
# listing surfaces the card immediately (DocumentCardsSection reads
# from this same collection).
#
# G8 ratified routing is handled CLIENT-SIDE on the redirect_url: the
# frontend post-modal navigation routes Board Pack + Committee Pack to
# the dedicated page (`/app/work-studio/document/{aid}`) and the
# remaining three to the listing with `?pulse=<aid>` so the new card
# pulses on arrival.
# ═════════════════════════════════════════════════════════════════════════
_VALID_FROM_DOC_KINDS = {
    "board_pack", "committee_pack", "minutes", "deck", "report",
}


class FromDocumentRequest(BaseModel):
    kind: Literal["board_pack", "committee_pack", "minutes", "deck", "report"]
    source_doc_id: str = Field(..., min_length=1, max_length=128)


@router.post(
    "/contexts/{context_id}/work-studio/from-document",
    status_code=201,
    response_model=Optional[ArtefactRedirectResponse],
)
async def create_work_studio_from_document(
    context_id: str,
    body: FromDocumentRequest,
    ctx: Dict[str, Any] = Depends(require_context_membership()),
):
    """Create a Draft Work Studio artefact seeded from a Document
    Journal item.

    422 paths:
      - `kind` not in the D5 5-kind set (Pydantic Literal blocks first)

    404 paths:
      - `source_doc_id` doesn't resolve in this context
    """
    if body.kind not in _VALID_FROM_DOC_KINDS:
        raise HTTPException(
            status_code=422,
            detail=(
                f"Unsupported kind `{body.kind}`. "
                f"D5 accepts: {sorted(_VALID_FROM_DOC_KINDS)}."
            ),
        )

    account = ctx["account"]
    account_id = account["id"]

    doc = await db.documents.find_one(
        {"id": body.source_doc_id, "context_id": context_id},
        {"_id": 0, "id": 1, "name": 1, "original_filename": 1},
    )
    if not doc:
        raise HTTPException(
            status_code=404,
            detail=(
                f"Document `{body.source_doc_id}` not found in this workspace."
            ),
        )
    doc_title = doc.get("name") or doc.get("original_filename") or "Document"

    artefact_id = str(uuid.uuid4())
    now = _now_iso()
    row = {
        "id": artefact_id,
        "context_id": context_id,
        "account_id": account_id,
        # D5 lands the new artefact as Draft. Lifecycle moves to
        # in_review when the user opens it; committed via the
        # commit-pack flow (W3/W5, deferred to T4).
        "kind": body.kind,
        "title": doc_title,
        "status": "draft",
        "lifecycle_state": "draft",
        "output_format": "docx",
        "source_document_ids": [doc["id"]],
        "structured_content": None,
        "origin": {
            "source": "document_journal_add",
            "document_id": doc["id"],
        },
        "created_at": now,
        "updated_at": now,
    }
    await db.work_studio_exports.insert_one(row)

    try:
        await write_audit(
            context_id=context_id, account_id=account_id,
            action="work_studio.artefact.created_from_document",
            resource_type=f"work_studio_artefact.{body.kind}",
            resource_id=artefact_id,
            metadata={
                "kind": body.kind,
                "source": "document_journal_add",
                "document_id": doc["id"],
                "title": doc_title,
            },
        )
    except Exception:
        logger.exception(
            "create_work_studio_from_document: audit write failed (non-fatal)"
        )

    # G8 ratified routing (frontend honours this redirect_url unless
    # it wants to land on the listing-with-pulse experience instead).
    if body.kind in {"board_pack", "committee_pack"}:
        redirect_url = f"/app/work-studio/document/{artefact_id}"
    else:
        redirect_url = f"/app/work-studio?kind={body.kind}&pulse={artefact_id}"

    return {
        "kind": body.kind,
        "artefact_id": artefact_id,
        "title": doc_title,
        "redirect_url": redirect_url,
    }
