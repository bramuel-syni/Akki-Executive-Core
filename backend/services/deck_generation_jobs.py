"""JC-DECK-GEN-ASYNC-KICKOFF-POLL (2026-07-05) — deck generation job store + phase wrapper.

Canonical spec: /app/memory/sprints/JC_DECK_GEN_ASYNC_KICKOFF_POLL.md
Rationale: convert every generation-triggering deck path from synchronous LLM-await
to kick-off (immediate 202) + FE polling. Applies uniformly across source-generate /
blank-generate / regenerate / enhance (point-3 mandate).

F.6 N/A: this module does NOT invoke Shield or LLM endpoints directly. It is a thin
wrapper that:
  1. Persists job state in `deck_generation_jobs` collection.
  2. Spawns the existing generation engine call in a background asyncio task.
  3. Instruments the wrapper (not the engine) with phase transitions.

Untouchables preserved:
  - `services/synisense/shield/**` sha256-identical (R10 of arc slice).
  - Generation engines untouched (0 diff bytes on `llm_tier_quota.py`,
    `llm_service.py`, `services/deck_regenerate.py` engine body).
  - `_http_client.py::_call` / `BOUNDED_CONTEXT_TRANSPORT` / retry policy untouched.
  - Commit-lock 409 shape byte-identical to compile-bridge (A10 standard).
  - Audit fingerprint 19-field preserved (A9/A10 standard) — the underlying engine
    still writes the audit event unchanged.

Account isolation:
  - Every job row carries `account_id` + `context_id` + `user_id`.
  - `get_job()` filters by account_id; cross-account read returns None.
"""
from __future__ import annotations

import asyncio
import logging
import uuid
from datetime import datetime, timezone
from typing import Any, Callable, Dict, Optional, Awaitable

from core import db

logger = logging.getLogger("akki.decks.async_jobs")


COLLECTION = "deck_generation_jobs"

# Phase enum — same tokens the FE progress checklist maps against
PHASE_QUEUED = "queued"
PHASE_READING = "reading_sources"
PHASE_STRUCTURING = "structuring"
PHASE_DRAFTING = "drafting"
PHASE_COMPLETE = "complete"
PHASE_ERROR = "error"

VALID_PHASES = {
    PHASE_QUEUED,
    PHASE_READING,
    PHASE_STRUCTURING,
    PHASE_DRAFTING,
    PHASE_COMPLETE,
    PHASE_ERROR,
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


async def create_job(
    *,
    job_kind: str,  # e.g. "source_generate", "blank_generate", "regenerate", "enhance"
    account_id: str,
    context_id: Optional[str],
    user_id: Optional[str],
    target_id: Optional[str],  # outline_id / document_id depending on job_kind
    request_hash: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new generation job row in `queued` phase.

    Idempotency: if a job with matching (account_id, target_id, job_kind) is already
    in flight (queued / reading_sources / structuring / drafting), return that
    job's row instead of creating a duplicate. This mirrors the "same request →
    same job_id if in-flight" semantics from the dispatch.
    """
    if target_id:
        existing = await db[COLLECTION].find_one(
            {
                "account_id": account_id,
                "target_id": target_id,
                "job_kind": job_kind,
                "phase": {"$in": [PHASE_QUEUED, PHASE_READING, PHASE_STRUCTURING, PHASE_DRAFTING]},
            },
            {"_id": 0},
        )
        if existing:
            logger.info(
                "deck-gen-async · returning existing in-flight job job_id=%s kind=%s phase=%s",
                existing.get("job_id"), job_kind, existing.get("phase"),
            )
            return existing

    job = {
        "job_id": str(uuid.uuid4()),
        "job_kind": job_kind,
        "account_id": account_id,
        "context_id": context_id,
        "user_id": user_id,
        "target_id": target_id,
        "phase": PHASE_QUEUED,
        "progress": 0,
        "result": None,
        "error": None,
        "request_hash": request_hash,
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    await db[COLLECTION].insert_one(job)
    logger.info(
        "deck-gen-async · created job job_id=%s kind=%s account=%s target=%s",
        job["job_id"], job_kind, account_id, target_id,
    )
    return job


async def set_phase(
    job_id: str,
    phase: str,
    *,
    progress: Optional[int] = None,
) -> None:
    """Update a job's phase + optional progress. Idempotent."""
    if phase not in VALID_PHASES:
        raise ValueError(f"invalid phase: {phase}")
    upd: Dict[str, Any] = {"phase": phase, "updated_at": _now_iso()}
    if progress is not None:
        upd["progress"] = progress
    await db[COLLECTION].update_one({"job_id": job_id}, {"$set": upd})
    logger.info("deck-gen-async · job=%s phase=%s progress=%s", job_id, phase, progress)


async def set_result(job_id: str, result: Dict[str, Any]) -> None:
    """Mark job as COMPLETE with the engine's result payload."""
    await db[COLLECTION].update_one(
        {"job_id": job_id},
        {"$set": {
            "phase": PHASE_COMPLETE,
            "progress": 100,
            "result": result,
            "error": None,
            "updated_at": _now_iso(),
        }},
    )
    logger.info("deck-gen-async · job=%s COMPLETE", job_id)


async def set_error(job_id: str, error: Dict[str, Any]) -> None:
    """Mark job as ERROR with the exception's details (type/message/status)."""
    await db[COLLECTION].update_one(
        {"job_id": job_id},
        {"$set": {
            "phase": PHASE_ERROR,
            "error": error,
            "updated_at": _now_iso(),
        }},
    )
    logger.warning("deck-gen-async · job=%s ERROR type=%s", job_id, error.get("type"))


async def get_job(job_id: str, account_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a job by id, scoped to account. Cross-account read returns None."""
    return await db[COLLECTION].find_one(
        {"job_id": job_id, "account_id": account_id},
        {"_id": 0},
    )


async def spawn_generation(
    job_id: str,
    runner: Callable[[str], Awaitable[Dict[str, Any]]],
) -> None:
    """Spawn the runner as a fire-and-forget asyncio task.

    The runner is responsible for calling set_phase() at natural transitions
    and set_result() / set_error() at terminus. This wrapper only catches
    unhandled exceptions to prevent silent task loss.
    """
    async def _task_body() -> None:
        try:
            await runner(job_id)
        except Exception as e:  # noqa: BLE001 — top-level task guard
            logger.exception("deck-gen-async · job=%s runner crashed", job_id)
            await set_error(job_id, {
                "type": e.__class__.__name__,
                "message": str(e)[:1000],
                "status": 500,
            })

    # asyncio.create_task hands the coroutine to the running event loop.
    # The endpoint returns 202 before this task completes.
    task = asyncio.create_task(_task_body())
    # Attach a name for observability; return_value discarded intentionally.
    task.set_name(f"deck_gen_job:{job_id}")


async def ensure_indexes() -> None:
    """Idempotent index creation. Called from server startup."""
    coll = db[COLLECTION]
    await coll.create_index([("job_id", 1)], unique=True, name="deck_gen_jobs_job_id_uq")
    await coll.create_index(
        [("account_id", 1), ("target_id", 1), ("job_kind", 1), ("phase", 1)],
        name="deck_gen_jobs_inflight_lookup",
    )
    await coll.create_index([("created_at", -1)], name="deck_gen_jobs_created_desc")
