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
from services import deck_retrieval, deck_lineage, deck_regenerate, deck_generation_jobs


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


class RegenerateAsyncResponse(BaseModel):
    """JC-DECK-GEN-ASYNC-KICKOFF-POLL (2026-07-05) — kickoff handle."""
    job_id: str
    phase: str
    status_url: str


class RegenerateStatusResponse(BaseModel):
    job_id: str
    phase: str
    progress: int
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


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
    response_model=RegenerateAsyncResponse,
    status_code=202,
    responses={409: {"description": "Committed deck cannot be regenerated"}},
)
async def post_regenerate(
    document_id: str,
    body: RegenerateBody = Body(default_factory=RegenerateBody),
    me: Dict[str, Any] = Depends(get_current_account),
):
    """F.6 SHIELD-ROUTED · JC-DECK-GEN-ASYNC-KICKOFF-POLL (2026-07-05) — async kickoff.

    Returns 202 with a job handle. The Shield-routed LLM call runs in a
    background asyncio task; the FE polls `/api/decks/generation-status/{job_id}`.

    Pre-conditions validated synchronously BEFORE returning 202:
      - Document must exist + caller must be a member of its context (else
        `deck_regenerate._load_and_membership_check` raises 404/403).
      - Document must not be committed (else raises 409 with compile-bridge
        shape — byte-identical to A10 standard).

    Engine (`services.deck_regenerate.regenerate_deck`) is UNCHANGED — this
    router just wraps it in a background task and instruments phase transitions
    on the shared `deck_generation_jobs` collection. Shield chokepoint invocation,
    audit fingerprint (19 fields), and version-chain semantics are preserved.
    """
    # Synchronous pre-flight: same membership + commit-lock checks the engine
    # performs at the top of regenerate_deck. Failing here means we never
    # spawn a background task on a doomed request.
    parent = await deck_regenerate._load_and_membership_check(document_id, me["id"])
    if parent.get("lifecycle_state") == "committed":
        # Re-raise via the same helper the engine uses so 409 envelope is
        # byte-identical to compile-bridge (A10 standard).
        raise deck_regenerate.commit_locked_409(document_id)

    context_id = parent.get("context_id")

    # Create or return existing in-flight job.
    job = await deck_generation_jobs.create_job(
        job_kind="regenerate",
        account_id=me["id"],
        context_id=context_id,
        user_id=me["id"],
        target_id=document_id,
    )

    if job["phase"] != deck_generation_jobs.PHASE_QUEUED:
        return {
            "job_id": job["job_id"],
            "phase": job["phase"],
            "status_url": f"/api/decks/generation-status/{job['job_id']}",
        }

    prompt = body.prompt
    account_id = me["id"]

    async def _runner(job_id: str) -> Dict[str, Any]:
        # ------ Phase: reading_sources — load parent text (already loaded, but
        # this is the observable checkpoint before the LLM fire) -------
        await deck_generation_jobs.set_phase(
            job_id, deck_generation_jobs.PHASE_READING, progress=10,
        )
        # ------ Phase: structuring — Shield-routed LLM call (engine untouched) -
        await deck_generation_jobs.set_phase(
            job_id, deck_generation_jobs.PHASE_STRUCTURING, progress=35,
        )
        try:
            engine_result = await deck_regenerate.regenerate_deck(
                document_id=document_id,
                account_id=account_id,
                prompt_override=prompt,
            )
        except Exception as e:  # noqa: BLE001 — propagate as job error
            status_code = getattr(e, "status_code", 500)
            detail = getattr(e, "detail", str(e))
            await deck_generation_jobs.set_error(job_id, {
                "type": e.__class__.__name__,
                "message": str(detail)[:1000],
                "status": status_code,
            })
            return {}
        # ------ Phase: drafting — post-Shield persistence completed by engine --
        await deck_generation_jobs.set_phase(
            job_id, deck_generation_jobs.PHASE_DRAFTING, progress=80,
        )
        # ------ Phase: complete -------
        await deck_generation_jobs.set_result(job_id, engine_result)
        return engine_result

    await deck_generation_jobs.spawn_generation(job["job_id"], _runner)

    return {
        "job_id": job["job_id"],
        "phase": deck_generation_jobs.PHASE_QUEUED,
        "status_url": f"/api/decks/generation-status/{job['job_id']}",
    }


@router.get(
    "/decks/generation-status/{job_id}",
    response_model=RegenerateStatusResponse,
)
async def get_regenerate_status(
    job_id: str,
    me: Dict[str, Any] = Depends(get_current_account),
):
    """JC-DECK-GEN-ASYNC-KICKOFF-POLL (2026-07-05) — poll endpoint for regenerate
    (and any future top-level `/decks` async generation surfaces).

    Account-scoped: returns 404 if job not found OR belongs to another account
    (indistinguishable to prevent enumeration).
    """
    from fastapi import HTTPException
    job = await deck_generation_jobs.get_job(job_id, account_id=me["id"])
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return {
        "job_id": job["job_id"],
        "phase": job["phase"],
        "progress": job.get("progress", 0),
        "result": job.get("result"),
        "error": job.get("error"),
        "created_at": job.get("created_at"),
        "updated_at": job.get("updated_at"),
    }
