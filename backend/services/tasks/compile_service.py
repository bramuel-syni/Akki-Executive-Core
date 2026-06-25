"""Phase F.4 — Task Compile orchestrator (2026-05-26).

Implements the 5-stage compile pipeline:

  1. Drafting           — Akki assembles a first cut from approved/
                          submitted contributions + manually-added
                          docs + output spec. Generates new
                          `state=draft, origin=akki_generated,
                          task_id=<id>` documents.
  2. Review & Editing   — pass-through. Users edit drafts via the
                          existing DocumentDrawer + prompted-edit
                          pipeline (E.3). The compile service marks
                          the stage complete on user signal.
  3. Circulation        — generates magic-link tokens scoped to the
                          drafts in this session, sends invites via
                          Postmark (`email_service.send_email`).
                          Reviewers comment via the link without an
                          Akki account.
  4. Final production   — applies circulation comments via the
                          prompted-edit pipeline (`apply_comment`).
  5. Commit             — sequentially commits each draft
                          (state → "committed"). Rollback on partial
                          failure.

All LLM calls route through Shield with a 3-second timeout fallback.
On timeout, the service emits a `task.compile.<purpose>.llm.timeout`
audit event and falls back to a deterministic template body.

Email send routes through Postmark (`email_service.send_email`). If
send fails, the magic link is still generated + persisted; the audit
row + UI surface the failure honestly. The reviewer can be given the
link manually.
"""
from __future__ import annotations

import asyncio
import json
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple


log = logging.getLogger("akki.tasks.compile")


SHIELD_LLM_TIMEOUT_SECONDS = 120.0  # JC-TM (2026-06-25) — bumped from
# F.4's original 3.0s default. The 3s budget guaranteed every compile
# LLM call timed out into the deterministic TODO-skeleton fallback,
# yielding "best-shape" docs that were just objective + success
# criteria + a "[TODO …]" placeholder. Board-pack section bodies
# routinely need 30-90s end-to-end through Shield (de-id → provider
# → re-id → audit → receipt). Mirrors the JC-WS Phase 1 per-method
# timeout fix in `_HTTPAdapterBase` (5s default kept for fast hops,
# 120s for LLM-bound hops). Compile-time LLM IS an LLM-bound hop;
# the budget needs to reflect that.

STAGES = (
    "drafting",
    "review",
    "circulation",
    "final_production",
    "commit",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


# ═════════════════════════════════════════════════════════════════════
# Shield wrapper with 3-second timeout
# ═════════════════════════════════════════════════════════════════════
async def shield_invoke_bounded(
    *, purpose: str, content: str, tenant_id: str,
    consumer_id: str = "tasks", user_id: str,
    model_preference: str = "balanced",
) -> Optional[Dict[str, Any]]:
    """Wraps `shield_invoke` in a 3-second timeout. Returns None on
    timeout or any failure so callers can fall back to deterministic
    behaviour without distinguishing the failure mode."""
    try:
        from contracts import get_synisense  # Phase 4.0 — was direct shield_invoke import
    except Exception:
        return None
    try:
        result = (await asyncio.wait_for(
            get_synisense().shield_invoke(
                purpose=purpose, content=content,
                account_id=tenant_id, consumer_id=consumer_id,
                user_id=user_id, model_preference=model_preference,
            ),
            timeout=SHIELD_LLM_TIMEOUT_SECONDS,
        )).raw
        return result
    except asyncio.TimeoutError:
        log.warning("shield timeout: purpose=%s timeout=%.1fs", purpose, SHIELD_LLM_TIMEOUT_SECONDS)
        # Audit event surfaced via the caller (it has db handle).
        return {"__timeout__": True, "purpose": purpose}
    except Exception as e:  # noqa: BLE001
        log.warning("shield failed: purpose=%s err=%s", purpose, e)
        return None


async def _record_llm_timeout(db, *, task_id: str, account_id: str, purpose: str) -> None:
    try:
        await db.audit_log.insert_one({
            "id":            str(uuid.uuid4()),
            "account_id":    account_id,
            "action":        "task.compile.llm.timeout",
            "resource_type": "task",
            "resource_id":   task_id,
            "metadata":      {"purpose": purpose, "timeout_s": SHIELD_LLM_TIMEOUT_SECONDS},
            "created_at":    _now_iso(),
        })
    except Exception as e:  # noqa: BLE001
        log.warning("timeout audit insert failed: %s", e)


# ═════════════════════════════════════════════════════════════════════
# Stage helpers
# ═════════════════════════════════════════════════════════════════════
def _empty_session() -> Dict[str, Any]:
    return {
        "active":                 False,
        "current_stage":          None,
        "draft_artefact_ids":     [],
        "review_artefact_ids":    [],
        "circulation": {
            "enabled":         False,
            "reviewer_emails": [],
            "sent_at":         None,
            "comments":        [],
            "closed_at":       None,
        },
        "final_artefact_ids":     [],
        "committed_artefact_ids": [],
        "started_at":             None,
        "completed_at":           None,
    }


async def _audit(db, *, task_id: str, account_id: str, action: str,
                 ctx_id: Optional[str], metadata: Optional[Dict[str, Any]] = None) -> None:
    try:
        await db.audit_log.insert_one({
            "id":            str(uuid.uuid4()),
            "account_id":    account_id,
            "context_id":    ctx_id,
            "action":        action,
            "resource_type": "task",
            "resource_id":   task_id,
            "metadata":      metadata or {},
            "created_at":    _now_iso(),
        })
    except Exception as e:  # noqa: BLE001
        log.warning("audit insert failed (%s): %s", action, e)


async def _set_session(db, *, task_id: str, session: Dict[str, Any]) -> None:
    await db.tasks.update_one(  # tenancy:allow-no-account-id — service invoked by router with tenant-gated entry; row-id-targeted update
        {"id": task_id},
        {"$set": {"compile_session": session, "updated_at": _now_iso()}},
    )


# ═════════════════════════════════════════════════════════════════════
# Stage 1 — Drafting
# ═════════════════════════════════════════════════════════════════════
def _build_drafting_prompt(task: Dict[str, Any], contributions: List[Dict[str, Any]]) -> str:
    spec = task.get("output_spec") or {}
    tpl_id = spec.get("template_id") or "free_text"
    tpl_descr = spec.get("free_text") or ""
    parts = [
        "You are an executive ghostwriter. Generate a polished first-cut",
        "draft for the following task. Return ONLY the document body in",
        "plain prose with section headings as ALL-CAPS lines. No JSON.",
        "",
        f"TASK: {task.get('name', '')}",
        f"OBJECTIVE: {task.get('objective', '')}",
        f"SUCCESS CRITERIA: {task.get('success_criteria', '')}",
        f"OUTPUT SPEC: template={tpl_id}; free_text={tpl_descr[:600]}",
        "",
        "INPUTS (contributor summaries):",
    ]
    if not contributions:
        parts.append("  • (no contributions yet — draft a placeholder skeleton with TODO markers)")
    else:
        for c in contributions[:10]:
            parts.append(f"  • {c.get('role') or c.get('name')}: {c.get('contribution') or '(no description)'}")
    return "\n".join(parts)


_TEMPLATE_PACK_SHAPES: Dict[str, List[str]] = {
    "board_pack":     ["Executive Summary", "Performance", "Risk", "Strategy", "Governance"],
    "committee_pack": ["Chair Foreword", "Topic Deep Dive", "Recommendations", "Sign-off"],
    "strategy_deck":  ["Narrative Arc"],
    "fundraising":    ["Pitch Deck", "Financial Model"],
}


def _fallback_draft_body(task: Dict[str, Any], section: Optional[str] = None) -> str:
    head = (section or task.get("name") or "Untitled draft").upper()
    return (
        f"{head}\n\n"
        f"Objective: {task.get('objective') or '—'}\n\n"
        f"Success criteria: {task.get('success_criteria') or '—'}\n\n"
        "[TODO — Akki could not generate the full draft body within the\n"
        "shield-timeout window. This skeleton has the spec captured;\n"
        "edit inline or use the prompted-edit composer to expand.]\n"
    )


# ═════════════════════════════════════════════════════════════════════
# JC-TM Stage 1 — Bridge Compile (2026-06-25)
#
# Per the JC-TM canonical spec (`/app/memory/JC_TM_CANONICAL_SPEC.md`
# § Part 0 + § Integration point with JC-WS):
#
#   "REUSE existing engines. Critically: compile must produce documents
#    through the SAME generators and the SAME export wizard as Document
#    Generation (board packs, committee packs, briefings, decks,
#    financial models/XLS). Do NOT build a parallel generation stack."
#
# Compile now becomes a thin orchestrator that routes approved
# contributions through the work_studio_export two-pass pipeline. Each
# requested output format produces a single composed document
# (e.g. board_pack DOCX with all sections as headings — the
# "forward-to-a-board good" shape JC-WS Phase 1 proved). The bridge
# inherits JC-WS Phase 1's three invariants verbatim:
#
#   1. Commit lifecycle  — work_studio_exports.lifecycle_state
#                           "draft" → "committed" on commit.
#   2. Edit-lock         — PATCH after commit → 409 (enforced by
#                           routers/work_studio_overlay.py:134-138).
#   3. Confidence pct    — real numeric pct from the shared scorer
#                           (_score_and_mirror_confidence).
#
# Mapping from task.output_spec.template_id → work_studio_export _VALID_KINDS.
# Unknown templates fall back to "report" (the most permissive shape).
# ═════════════════════════════════════════════════════════════════════
_TPL_TO_EXPORT_KIND: Dict[str, str] = {
    "board_pack":      "board_pack",
    "committee_pack":  "committee_pack",
    "strategy_deck":   "deck",
    "deck":            "deck",
    "fundraising":     "report",   # cover the underlying pitch as a report;
                                    # the user can refine into deck later.
    "minutes":         "minutes",
    "report":          "report",
    "brief":           "brief",
    "briefing":        "brief",
    "free_text":       "report",
}


def _build_export_body(task: Dict[str, Any], contributions: List[Dict[str, Any]],
                       *, source_document_ids: Optional[List[str]] = None):
    """Compose an ExportRequestIn from a task + approved contributions.
    The three required string fields map naturally onto the existing
    work_studio_export Pass-1/Pass-2 prompt shape:
      • description — approved contributor inputs (the body to ground in)
      • objective   — the task's verbatim objective
      • scope       — the task's verbatim success criteria

    JC-TM Stage 2 (2026-06-25) — `source_document_ids` carries the
    contributor-uploaded document IDs through to the export pipeline.
    When provided, the work_studio_export Pass-1 prompt grounds in the
    extracted text of those documents AND the confidence scorer rewards
    cited sources (raises `confidence_pct` from the hollow ~30-40 range
    to the realistic ~70+ range). Without it, the scorer correctly
    flags thin grounding.
    """
    # Lazy-import inside the function so the module-level import graph
    # stays acyclic. See routers/compilations.py:234-235 for prior art.
    from routers.work_studio_export import ExportRequestIn

    objective_text = (task.get("objective") or task.get("name") or "Compile task")[:1900]
    scope_text     = (task.get("success_criteria") or "Produce a professional document.")[:1900]

    desc_parts = [
        f"Task: {task.get('name', '')}",
        "",
        "Approved contributor inputs:",
    ]
    if not contributions:
        desc_parts.append(
            "  (no approved contributions yet — produce a polished placeholder "
            "skeleton with TODO markers and a board-ready voice)"
        )
    else:
        for c in contributions[:10]:
            name    = c.get("name") or c.get("email") or "Contributor"
            role    = c.get("role") or "—"
            summary = (c.get("contribution") or c.get("note") or "(no description)")[:600]
            status  = c.get("status") or "—"
            desc_parts.append(f"  • {name} ({role}) — status={status}: {summary}")
    desc_text = "\n".join(desc_parts)[:1900]

    return ExportRequestIn(
        description=desc_text or "Compile task from approved contributions.",
        objective=objective_text or "Compile task.",
        scope=scope_text or "Produce a professional document.",
        output_format="auto",
        source_document_ids=source_document_ids or None,
    )


async def run_drafting(db, *, task: Dict[str, Any], account_id: str) -> List[str]:
    """JC-TM Stage 1 Bridge — routes through work_studio_export's
    `_run_export` per the canonical-spec rule "compile must produce
    documents through the SAME generators and the SAME export wizard
    as Document Generation".

    Per the user dispatch: one work_studio_exports row per requested
    format (option (a) — sections appear as headings inside one
    composed document). Each row carries `source_task_id=<task_id>` so
    the TaskDrawer can pivot to the artefact.

    The legacy plain-text-to-db.documents writer survives only as an
    emergency fallback when _run_export raises a non-recoverable error
    for every requested format, so the slice never strands.

    Returns the list of created work_studio_exports IDs (or legacy
    db.documents IDs if the bridge fully fell through to fallback)."""
    tid = task["id"]
    ctx_id = task.get("context_id")
    session = task.get("compile_session") or _empty_session()
    session["active"]          = True
    session["current_stage"]   = "drafting"
    if not session.get("started_at"):
        session["started_at"]  = _now_iso()
    await _set_session(db, task_id=tid, session=session)
    await _audit(db, task_id=tid, account_id=account_id,
                 action="task.compile.drafting.started", ctx_id=ctx_id,
                 metadata={"output_spec": task.get("output_spec"),
                           "bridge":      "work_studio_export"})

    # Pull contributions that are submitted/approved.
    contributions = [
        m for m in (task.get("team") or [])
        if m.get("status") in ("submitted", "approved")
    ]

    # JC-TM Stage 2 (2026-06-25) — load-bearing `source_document_ids`
    # wiring. The contributor portal (`POST /api/tasks/contribute/{token}/upload`)
    # and the email-reply pipeline (`routers/inbound_email.py:691,720`)
    # both write to `db.documents` with `task_id=<tid>`. Pull every
    # contributor upload that's `state="ready"` (or unset for older
    # rows) and forward its `id` to the export pipeline as explicit
    # grounding. This is the single change that turns the Stage 1
    # hollow 40/30 confidence_pct into a realistic 70+ when real
    # uploads exist; without contributor uploads, the list stays
    # empty and the scorer correctly flags thin grounding.
    #
    # The grounding lookups in work_studio_export (`_grounding_from_selected_docs`,
    # `_resolve_source_blobs_for_scoring`) BOTH filter by `context_id`,
    # but contributor uploads today only carry `task_id` + `account_id`
    # (see `routers/tasks.py:1229-1247`). We backfill `context_id` on
    # the doc rows here so the downstream lookups find them. This is
    # not synthesis — the task IS the originating surface, the task
    # IS scoped to its context, and the contributor doc IS related to
    # that context. The backfill is idempotent (it only sets if
    # missing).
    src_docs = await db.documents.find(
        {"task_id": tid,
         "$or": [{"status": "ready"}, {"status": {"$exists": False}}],
         "extracted_text": {"$ne": ""}},
        {"_id": 0, "id": 1, "name": 1, "contributor_email": 1, "origin": 1,
         "context_id": 1},
    ).to_list(length=50)
    source_document_ids: List[str] = []
    for d in src_docs:
        if not d.get("id"):
            continue
        source_document_ids.append(d["id"])
        # Idempotent backfill: only stamp context_id when missing.
        if ctx_id and not d.get("context_id"):
            try:
                await db.documents.update_one(  # tenancy:allow-no-account-id — doc pre-validated by task_id match on the parent task already gated upstream; row-id-targeted backfill
                    {"id": d["id"], "context_id": {"$exists": False}},
                    {"$set": {"context_id": ctx_id}},
                )
            except Exception as e:  # noqa: BLE001
                log.warning("JC-TM Stage 2: context_id backfill failed for doc=%s: %s",
                            d["id"], e)
    if source_document_ids:
        log.info("JC-TM Stage 2: wiring %d source_document_ids into compile for task=%s",
                 len(source_document_ids), tid)

    spec    = task.get("output_spec") or {}
    tpl_id  = spec.get("template_id")
    formats_in = spec.get("formats") or ["docx"]
    valid_formats = {"docx", "pptx", "pdf"}
    formats = [f for f in formats_in if f in valid_formats] or ["docx"]

    # Lazy-import to avoid circular ref (work_studio_export imports
    # services indirectly).
    from routers.work_studio_export import _run_export, _VALID_KINDS

    kind = _TPL_TO_EXPORT_KIND.get((tpl_id or "").lower(), "report")
    if kind not in _VALID_KINDS:
        kind = "report"

    body = _build_export_body(task, contributions, source_document_ids=source_document_ids)

    created_export_ids: List[str] = []
    bridge_errors:      List[Dict[str, Any]] = []

    for fmt in formats:
        # Pre-create the work_studio_exports row with source_task_id
        # so the linkback is preserved even if _run_export raises mid-run.
        # Schema mirrors routers/work_studio_export.py:2012-2047 + the
        # bridge-only `source_task_id` field for the TaskDrawer pivot.
        export_id = str(uuid.uuid4())
        created_at = _now_iso()
        row = {
            "id":                export_id,
            "context_id":        ctx_id,
            "account_id":        account_id,
            "kind":              kind,
            "output_format":     fmt,
            "status":            "running",
            "description_chars": len(body.description),
            "objective_chars":   len(body.objective),
            "scope_chars":       len(body.scope),
            "created_at":        created_at,
            "completed_at":      None,
            "file_name":         None,
            "file_path":         None,
            "sha256":            None,
            "sensitivity_band":  None,
            "error":             None,
            "refusal_text":      None,
            "chat_audit_id":     None,
            "source_count":      len(source_document_ids),
            "contributor_count": max(1, len(contributions)),
            "akki_generated":    True,
            "lifecycle_state":   "draft",
            # JC-TM Stage 1 Bridge link-back to the task.
            "source_task_id":    tid,
        }
        await db.work_studio_exports.insert_one(row)

        try:
            await _run_export(
                export_id=export_id, account_id=account_id,
                context_id=ctx_id, kind=kind,
                output_format=fmt, body=body,
            )
            # _run_export itself stamps the row with status=complete /
            # status=failed; we trust that and just record the id.
            created_export_ids.append(export_id)
        except Exception as e:  # noqa: BLE001
            log.exception("JC-TM bridge: _run_export crashed for fmt=%s", fmt)
            bridge_errors.append({"format": fmt, "error": str(e)[:300],
                                  "export_id": export_id})
            await db.work_studio_exports.update_one(
                {"id": export_id, "context_id": ctx_id},
                {"$set": {"status": "failed",
                          "error": f"bridge:{type(e).__name__}: {str(e)[:200]}",
                          "completed_at": _now_iso()}},
            )

    # Honest fallback — only if EVERY format failed do we drop to the
    # legacy plain-text writer so the slice never strands. The fallback
    # is explicitly tagged so downstream evidence is honest.
    fallback_doc_ids: List[str] = []
    if not created_export_ids:
        log.warning("JC-TM bridge: every format failed; falling back to legacy plain-text writer")
        sections = _TEMPLATE_PACK_SHAPES.get(tpl_id, [task.get("name") or "Draft"])
        for section in sections:
            did = f"doc-{uuid.uuid4().hex[:10]}"
            doc = {
                "id":                did,
                "context_id":        ctx_id,
                "account_id":        account_id,
                "task_id":           tid,
                "name":              f"{task.get('name', 'Draft')} — {section}",
                "extracted_text":    _fallback_draft_body(task, section),
                "state":             "draft",
                "origin":            "akki_generated",
                "status":            "ready",
                "doc_type":          tpl_id or "free_text",
                "compile_session":   {"task_id": tid, "stage": "drafting_fallback",
                                       "section": section},
                "created_at":        _now_iso(),
            }
            await db.documents.insert_one(dict(doc))
            fallback_doc_ids.append(did)

    session["draft_artefact_ids"]  = created_export_ids or fallback_doc_ids
    session["draft_artefact_kind"] = "work_studio_export" if created_export_ids else "legacy_document"
    if fallback_doc_ids:
        session["fallback_legacy_doc_ids"] = fallback_doc_ids
    if bridge_errors:
        session["bridge_errors"] = bridge_errors
    session["current_stage"] = "drafting"
    await _set_session(db, task_id=tid, session=session)
    await _audit(db, task_id=tid, account_id=account_id,
                 action="task.compile.drafting.completed", ctx_id=ctx_id,
                 metadata={"draft_artefact_ids": session["draft_artefact_ids"],
                           "draft_artefact_kind": session["draft_artefact_kind"],
                           "formats":             formats,
                           "kind":                kind,
                           "source_document_ids_n": len(source_document_ids),
                           "bridge_failures":     len(bridge_errors),
                           "fallback_used":       bool(fallback_doc_ids)})
    return session["draft_artefact_ids"]


# ═════════════════════════════════════════════════════════════════════
# Stage 2 — Review & Editing  (advance only — editing is via E.3)
# ═════════════════════════════════════════════════════════════════════
async def complete_review(db, *, task: Dict[str, Any], account_id: str, skip_circulation: bool) -> Dict[str, Any]:
    tid = task["id"]
    session = task.get("compile_session") or _empty_session()
    session["review_artefact_ids"] = list(session.get("draft_artefact_ids") or [])
    if skip_circulation:
        session["current_stage"]                = "final_production"
        session["circulation"]["enabled"]       = False
    else:
        session["current_stage"]                = "circulation"
        session["circulation"]["enabled"]       = True
    await _set_session(db, task_id=tid, session=session)
    await _audit(db, task_id=tid, account_id=account_id,
                 action="task.compile.review.completed",
                 ctx_id=task.get("context_id"),
                 metadata={"skip_circulation": skip_circulation})
    return session


# ═════════════════════════════════════════════════════════════════════
# Stage 3 — Circulation
# ═════════════════════════════════════════════════════════════════════
def _gen_token() -> str:
    return secrets.token_urlsafe(32)


async def send_circulation(db, *, task: Dict[str, Any], account_id: str,
                            reviewer_emails: List[str], message: Optional[str],
                            base_url: str) -> Dict[str, Any]:
    """Generates per-reviewer magic-link tokens, persists them, and
    sends invite emails via Postmark. If Postmark send fails for a
    reviewer, the link is still persisted; the failure is recorded on
    the per-reviewer status."""
    tid = task["id"]
    ctx_id = task.get("context_id")
    session = task.get("compile_session") or _empty_session()
    expires = datetime.now(timezone.utc) + timedelta(days=14)
    sent_status: List[Dict[str, Any]] = []
    for email in reviewer_emails:
        token = _gen_token()
        try:
            await db.task_circulation_tokens.insert_one({
                "id":                str(uuid.uuid4()),
                "token":              token,
                "task_id":            tid,
                "reviewer_email":     email.strip().lower(),
                "draft_artefact_ids": list(session.get("draft_artefact_ids") or []),
                "expires_at":         expires.isoformat(),
                "used":               False,
                "created_at":         _now_iso(),
            })
        except Exception as e:  # noqa: BLE001
            log.error("token persist failed: %s", e)
            sent_status.append({"email": email, "status": "persist_failed"})
            continue
        url = f"{base_url.rstrip('/')}/circulation/{token}"
        # Send via Postmark.
        sent = "queued"
        try:
            from email_service import send_email
            subject = f"Please review: {task.get('name', 'Draft')}"
            text = (
                f"You've been asked to review a draft for: {task.get('name', '')}.\n\n"
                f"{message or ''}\n\n"
                f"Open the review link: {url}\n\n"
                f"This link expires on {expires.date().isoformat()}.\n"
            )
            html = (
                f"<p>You've been asked to review a draft for: <b>{task.get('name', '')}</b>.</p>"
                f"<p>{message or ''}</p>"
                f"<p><a href='{url}'>Open the review link</a></p>"
                f"<p style='color:#888;font-size:12px'>Expires {expires.date().isoformat()}.</p>"
            )
            resp = await send_email(to=email, subject=subject, text=text, html=html)
            sent = (resp or {}).get("mode") or "sent"
        except Exception as e:  # noqa: BLE001
            log.warning("circulation send failed for %s: %s", email, e)
            sent = "send_failed"
        sent_status.append({"email": email, "status": sent, "token": token, "url": url})
        await _audit(db, task_id=tid, account_id=account_id,
                     action="task.compile.circulation.invite_sent", ctx_id=ctx_id,
                     metadata={"reviewer_email": email, "status": sent})

    session["circulation"]["enabled"]         = True
    session["circulation"]["reviewer_emails"] = [e.strip().lower() for e in reviewer_emails]
    session["circulation"]["sent_at"]         = _now_iso()
    session["circulation"]["sent_status"]     = sent_status
    session["current_stage"]                  = "circulation"
    await _set_session(db, task_id=tid, session=session)
    return {"sent": sent_status, "expires_at": expires.isoformat()}


async def add_circulation_comment(db, *, token: str, comment_text: str,
                                   doc_id: Optional[str] = None,
                                   span: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    row = await db.task_circulation_tokens.find_one({"token": token, "used": False})
    if not row:
        return {"ok": False, "reason": "invalid_or_expired_token"}
    try:
        exp = datetime.fromisoformat((row.get("expires_at") or "").replace("Z", "+00:00"))
    except (ValueError, TypeError):
        exp = None
    if exp and exp < datetime.now(timezone.utc):
        return {"ok": False, "reason": "invalid_or_expired_token"}
    tid = row["task_id"]
    t = await db.tasks.find_one({"id": tid})  # tenancy:allow-no-account-id — service invoked by router with tenant-gated entry; row-id-targeted readback
    if not t:
        return {"ok": False, "reason": "task_missing"}
    session = t.get("compile_session") or _empty_session()
    cmt = {
        "id":         str(uuid.uuid4()),
        "reviewer":   row["reviewer_email"],
        "comment":    (comment_text or "").strip()[:4000],
        "doc_id":     doc_id,
        "created_at": _now_iso(),
    }
    # Debt W4 (2026-05-26) — inline-comment span. Optional. When
    # present, the comment is anchored at a text span. Multiple
    # comments on the same span are allowed (group by `span.start +
    # ":" + span.end` on the review surface).
    if span and isinstance(span, dict):
        try:
            start = int(span.get("start", 0))
            end   = int(span.get("end", 0))
            text  = (span.get("text") or "").strip()[:2000]
            if 0 <= start <= end and text:
                cmt["span"] = {"start": start, "end": end, "text": text}
        except (ValueError, TypeError):
            pass
    session["circulation"]["comments"].append(cmt)
    await _set_session(db, task_id=tid, session=session)
    await _audit(db, task_id=tid, account_id=t.get("account_id"),
                 action="task.compile.circulation.comment_received",
                 ctx_id=t.get("context_id"),
                 metadata={"reviewer": row["reviewer_email"], "doc_id": doc_id,
                           "len": len(cmt["comment"]),
                           "inline": bool(cmt.get("span"))})
    return {"ok": True, "comment_id": cmt["id"], "task_id": tid,
            "inline": bool(cmt.get("span"))}


async def close_circulation(db, *, task: Dict[str, Any], account_id: str) -> Dict[str, Any]:
    tid = task["id"]
    session = task.get("compile_session") or _empty_session()
    session["circulation"]["closed_at"] = _now_iso()
    session["current_stage"]            = "final_production"
    await _set_session(db, task_id=tid, session=session)
    await _audit(db, task_id=tid, account_id=account_id,
                 action="task.compile.circulation.closed",
                 ctx_id=task.get("context_id"),
                 metadata={"comment_count": len(session["circulation"]["comments"])})
    return session


# ═════════════════════════════════════════════════════════════════════
# Stage 4 — Final production
# ═════════════════════════════════════════════════════════════════════
async def apply_comment(db, *, task: Dict[str, Any], account_id: str,
                          comment_id: str, action: str) -> Dict[str, Any]:
    """For action='apply': feeds the comment through the prompted-edit
    pipeline on the doc the comment was attached to. For 'discard':
    marks the comment dismissed. For 'edit_manual': records intent
    (the user edits in the DocumentDrawer themselves)."""
    tid = task["id"]
    session = task.get("compile_session") or _empty_session()
    comment = next((c for c in (session.get("circulation") or {}).get("comments", []) if c["id"] == comment_id), None)
    if not comment:
        return {"ok": False, "reason": "comment_not_found"}
    if action == "apply" and comment.get("doc_id"):
        # Trigger a prompted-edit rewrite via Shield.
        doc = await db.documents.find_one({"id": comment["doc_id"], "task_id": tid}, {"_id": 0})
        if doc and doc.get("extracted_text"):
            prompt = (
                "Rewrite the document body below to address this reviewer\n"
                "comment. Apply the suggestion faithfully — do not invent\n"
                "facts. Return the FULL rewritten body, no preamble.\n\n"
                f"REVIEWER COMMENT: {comment['comment']}\n\n"
                f"CURRENT BODY:\n{doc['extracted_text'][:8000]}\n"
            )
            result = await shield_invoke_bounded(
                purpose="task_manager.compile.apply_comment",
                content=prompt,
                tenant_id=account_id, user_id=account_id, consumer_id="tasks",
            )
            if result and result.get("__timeout__"):
                await _record_llm_timeout(db, task_id=tid, account_id=account_id,
                                          purpose="apply_comment")
            new_body = (result or {}).get("response", "").strip() if result and not result.get("__timeout__") else ""
            if new_body:
                await db.documents.update_one(  # tenancy:allow-no-account-id — `doc` loaded above at L454 with `{"id": doc_id, "task_id": tid}` (task_id is an alt-key for documents per Phase 2.2 widening); this is the matching write of the rewritten body.
                    {"id": doc["id"]},
                    {"$set": {"extracted_text": new_body, "updated_at": _now_iso()}},
                )
    comment["status"] = "applied" if action == "apply" else action
    await _set_session(db, task_id=tid, session=session)
    await _audit(db, task_id=tid, account_id=account_id,
                 action=f"task.compile.final_production.comment_{action}",
                 ctx_id=task.get("context_id"),
                 metadata={"comment_id": comment_id, "doc_id": comment.get("doc_id")})
    return {"ok": True, "comment_id": comment_id, "action": action}


async def complete_final_production(db, *, task: Dict[str, Any], account_id: str) -> Dict[str, Any]:
    tid = task["id"]
    session = task.get("compile_session") or _empty_session()
    session["final_artefact_ids"] = list(session.get("draft_artefact_ids") or [])
    session["current_stage"]      = "commit"
    await _set_session(db, task_id=tid, session=session)
    await _audit(db, task_id=tid, account_id=account_id,
                 action="task.compile.final_production.completed",
                 ctx_id=task.get("context_id"))
    return session


# ═════════════════════════════════════════════════════════════════════
# Stage 5 — Commit (sequential with rollback on partial failure)
# ═════════════════════════════════════════════════════════════════════
async def run_commit(db, *, task: Dict[str, Any], account_id: str) -> Dict[str, Any]:
    """Commit all draft documents to state="committed". Mongo's
    Motor client doesn't expose multi-doc transactions in our
    deployment so we do sequential commits + a best-effort rollback
    if any commit fails midway. Per the brief's explicit scope cut.

    JC-TM Stage 1 Bridge (2026-06-25) — branches on
    `session.draft_artefact_kind`:
      • "work_studio_export" — flip
        `work_studio_exports.lifecycle_state` "draft" → "committed";
        this inherits JC-WS Phase 1's PATCH-after-commit → 409
        edit-lock invariant verbatim (enforced by
        routers/work_studio_overlay.py:134-138).
      • "legacy_document" (fallback path only) — flip
        `db.documents.state` "draft" → "committed" per the F.4
        original behaviour.
    """
    tid = task["id"]
    ctx_id = task.get("context_id")
    session = task.get("compile_session") or _empty_session()
    ids = list(session.get("final_artefact_ids") or session.get("draft_artefact_ids") or [])
    if not ids:
        return {"ok": False, "reason": "no_drafts"}
    artefact_kind = session.get("draft_artefact_kind") or "legacy_document"
    committed: List[str] = []
    failed: Optional[str] = None

    if artefact_kind == "work_studio_export":
        # JC-TM Stage 1 Bridge — flip lifecycle_state on the
        # work_studio_exports rows. Each row's `source_task_id` already
        # links back to this task (set in run_drafting).
        for eid in ids:
            try:
                res = await db.work_studio_exports.update_one(
                    {"id": eid, "context_id": ctx_id, "lifecycle_state": "draft"},
                    {"$set": {"lifecycle_state": "committed",
                              "committed_at":    _now_iso()}},
                )
                if res.modified_count != 1:
                    # Either the row is missing, the context_id mismatched,
                    # or it's already in a non-draft state. The slice's
                    # last call should always find rows in draft state
                    # (run_drafting just created them); anything else is a
                    # real failure we should surface.
                    row = await db.work_studio_exports.find_one(
                        {"id": eid, "context_id": ctx_id}, {"_id": 0, "lifecycle_state": 1},
                    )
                    if row and row.get("lifecycle_state") == "committed":
                        # Already committed by an earlier idempotent call — treat as success.
                        committed.append(eid)
                        continue
                    failed = eid
                    break
                committed.append(eid)
            except Exception as e:  # noqa: BLE001
                log.error("bridge commit failed for export_id=%s: %s", eid, e)
                failed = eid
                break
        if failed is not None:
            for eid in committed:
                try:
                    await db.work_studio_exports.update_one(
                        {"id": eid, "context_id": ctx_id},
                        {"$set": {"lifecycle_state": "draft"},
                         "$unset": {"committed_at": ""}},
                    )
                except Exception as e:  # noqa: BLE001
                    log.error("bridge rollback failed for export_id=%s: %s", eid, e)
            await _audit(db, task_id=tid, account_id=account_id,
                         action="task.compile.commit.failed", ctx_id=ctx_id,
                         metadata={"failed_artefact": failed,
                                   "rolled_back":     committed,
                                   "artefact_kind":   artefact_kind})
            return {"ok": False, "reason": "partial_commit_failed", "failed": failed}
    else:
        # Legacy path — flip db.documents.state. Only reached when
        # run_drafting's bridge fully failed for every requested format
        # and dropped to its plain-text fallback writer.
        for did in ids:
            try:
                res = await db.documents.update_one(
                    {"id": did, "task_id": tid, "state": "draft"},
                    {"$set": {"state": "committed", "committed_at": _now_iso()}},
                )
                if res.modified_count != 1:
                    failed = did
                    break
                committed.append(did)
            except Exception as e:  # noqa: BLE001
                log.error("commit failed for %s: %s", did, e)
                failed = did
                break
        if failed is not None:
            for did in committed:
                try:
                    await db.documents.update_one(  # tenancy:allow-no-account-id — rollback path; `did` was just committed by the same task-scoped commit loop above (L516, `task_id` alt-key gated); state restore is within-task.
                        {"id": did}, {"$set": {"state": "draft"}, "$unset": {"committed_at": ""}},
                    )
                except Exception as e:  # noqa: BLE001
                    log.error("rollback failed for %s: %s", did, e)
            await _audit(db, task_id=tid, account_id=account_id,
                         action="task.compile.commit.failed", ctx_id=ctx_id,
                         metadata={"failed_doc": failed, "rolled_back": committed,
                                   "artefact_kind": artefact_kind})
            return {"ok": False, "reason": "partial_commit_failed", "failed": failed}

    # All committed — wrap up the session.
    session["committed_artefact_ids"] = committed
    session["current_stage"]          = "commit"
    session["completed_at"]           = _now_iso()
    session["active"]                 = False

    # Decide whether to auto-close the task. We close only if EVERY
    # draft in the session committed AND the task has no other open
    # drafts. The "open drafts" count uses the right collection for
    # the artefact kind in play.
    if artefact_kind == "work_studio_export":
        other_drafts = await db.work_studio_exports.count_documents({
            "source_task_id": tid, "lifecycle_state": "draft",
        })
    else:
        other_drafts = await db.documents.count_documents({
            "task_id": tid, "state": "draft",
        })
    task_closed = False
    update_fields: Dict[str, Any] = {"compile_session": session, "updated_at": _now_iso()}
    if other_drafts == 0:
        update_fields["state"] = "closed"
        task_closed = True
    await db.tasks.update_one({"id": tid}, {"$set": update_fields})  # tenancy:allow-no-account-id — service invoked by router with tenant-gated entry; row-id-targeted update
    if task_closed:
        await _audit(db, task_id=tid, account_id=account_id,
                     action="task.state.auto_closed", ctx_id=ctx_id,
                     metadata={"reason": "compile.commit"})
    await _audit(db, task_id=tid, account_id=account_id,
                 action="task.compile.commit.completed", ctx_id=ctx_id,
                 metadata={"committed_artefact_ids": committed,
                           "task_closed":             task_closed,
                           "artefact_kind":           artefact_kind})
    return {"ok": True, "committed": committed, "task_closed": task_closed,
            "artefact_kind": artefact_kind}
