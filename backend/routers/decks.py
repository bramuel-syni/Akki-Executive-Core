"""Decks — narrative slide-deck generation with budget guardrails.

Three-step pipeline that ensures deep-tier (Opus) calls only fire when
context is sufficient and the user has confirmed the research question.

  1. POST /contexts/{cid}/decks/outline       (STANDARD tier — free of deep budget)
       → Parses intent, surfaces available context (docs/signals/briefs),
         drafts a slide outline + research question + missing-context flags.
         User reviews & may iterate before committing a deep slot.

  2. POST /contexts/{cid}/decks/{outline_id}/generate   (DEEP tier — 1 slot)
       → Consumes a deck-quota slot ONLY after outline is approved.
         Renders the deck against the approved outline.

  3. POST /contexts/{cid}/decks/{deck_id}/quality_check  (FAST tier — free)
       → Scores the deck against the original intent + outline.
         If score < threshold we return refinement guidance rather than
         encouraging an expensive regen.

  4. POST /contexts/{cid}/decks/{deck_id}/feedback       (free)
       → User thumbs (up/down) + optional comment. Drives behaviour
         monitoring on /admin/llm-spend → Deck quality panel.

Telemetry: `deck_telemetry` collection captures outline iterations,
quality scores, regen counts, and user feedback for ops visibility.
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from core import db, iso, now, write_audit, require_context_membership, get_current_account
from contracts import get_synisense  # Phase 4.3 — signals reads route through SyniSense.
from services import deck_generation_jobs  # JC-DECK-GEN-ASYNC-KICKOFF-POLL 2026-07-05

logger = logging.getLogger("akki.decks")

router = APIRouter(tags=["decks"])


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
class OutlineIn(BaseModel):
    intent: str = Field(min_length=12, max_length=600)
    audience: Optional[str] = Field(None, max_length=120)
    target_slides: Optional[int] = Field(None, ge=4, le=20)
    parent_outline_id: Optional[str] = None  # iterating on a prior outline


class GenerateIn(BaseModel):
    outline_id: str
    confirmed: bool = False
    edits: Optional[Dict[str, Any]] = None  # user tweaks: {research_question, slides[]}


class FeedbackIn(BaseModel):
    rating: str = Field(pattern="^(up|down)$")
    comment: Optional[str] = Field(None, max_length=500)
    will_regenerate: bool = False
    regen_reason: Optional[str] = Field(
        None, pattern="^(audience_drift|weak_research_question|missing_evidence|wrong_tone|other)$"
    )


# ---------------------------------------------------------------------------
# Outline — STANDARD tier; cheap, gets the user to a clear research question
# and shows them which sources will be used. Critical guardrail: the user
# must confirm this before any deep call fires.
# ---------------------------------------------------------------------------
async def _gather_context_signals(account_id: str, context_id: str) -> Dict[str, Any]:
    """Pull a compact summary of available evidence for the LLM to plan against."""
    docs = await db.documents.find(
        {"context_id": context_id, "status": {"$in": ["extracted", "ready"]}},
        {"_id": 0, "id": 1, "name": 1, "doc_type": 1, "created_at": 1, "preview": 1,
         "extracted_chars": 1},
    ).sort("created_at", -1).to_list(length=40)

    signal_rows = await get_synisense().list_signals(
        account_id=account_id,
        context_id=context_id,
        status_excludes=["archived"],
        sort_by="created_at",
        order="desc",
        limit=30,
    )
    signals = [sig.raw or {} for sig in signal_rows]

    briefs = await db.briefs.find(
        {"context_id": context_id},
        {"_id": 0, "id": 1, "title": 1, "kind": 1, "objective": 1, "created_at": 1,
         "tier": 1},
    ).sort("created_at", -1).to_list(length=20)

    return {"docs": docs, "signals": signals, "briefs": briefs}


def _outline_prompt(intent: str, audience: Optional[str], target_slides: int,
                    ctx_name: str, evidence: Dict[str, Any],
                    learning_hint: Optional[str] = None) -> str:
    docs_block = "\n".join(
        f"- doc[{d['id'][:8]}] {d.get('name','(untitled)')} "
        f"({d.get('doc_type') or 'doc'}, {d.get('extracted_chars',0)} chars)"
        for d in evidence["docs"][:15]
    ) or "  (none)"
    sigs_block = "\n".join(
        f"- signal[{s['id'][:8]}] {s.get('title','(untitled)')} "
        f"({s.get('kind') or 'signal'})"
        for s in evidence["signals"][:15]
    ) or "  (none)"
    briefs_block = "\n".join(
        f"- brief[{b['id'][:8]}] {b.get('title','(untitled)')} ({b.get('kind') or 'brief'})"
        for b in evidence["briefs"][:10]
    ) or "  (none)"

    learning_block = ""
    if learning_hint:
        learning_block = (
            "\nLEARNING FROM THIS USER'S PRIOR DECKS\n"
            f"On their last regenerate they flagged: {learning_hint}.\n"
            "Use this as a corrective hint: tighten the research question, "
            "be sharper about audience, or call out missing evidence "
            "explicitly so they can fix the upstream gap rather than "
            "burning another deep slot.\n"
        )

    return (
        "You are AKKI's deck-planning model. Your job here is NOT to write the "
        "deck. Your job is to plan it cheaply and surface gaps so the user "
        "doesn't burn an expensive deep-tier generation on a weak prompt.\n\n"
        f"CONTEXT: {ctx_name}\n"
        f"AUDIENCE: {audience or 'unspecified — assume board/ExCo'}\n"
        f"TARGET LENGTH: {target_slides} slides.\n"
        f"USER INTENT: {intent}\n"
        + learning_block +
        "\nAVAILABLE EVIDENCE\n"
        "Documents:\n" + docs_block + "\n\n"
        "Signals:\n" + sigs_block + "\n\n"
        "Briefs:\n" + briefs_block + "\n\n"
        "Return STRICT JSON:\n"
        "{\n"
        '  "research_question": "<the one sharp question this deck should answer, in 1 sentence>",\n'
        '  "audience_assumed": "<the audience the planner assumed>",\n'
        '  "evidence_used": [{"id": "<doc/signal/brief id>", "kind": "doc|signal|brief", "why": "<one line>"}],\n'
        '  "missing_context": ["<one line per genuine gap; empty array if none>"],\n'
        '  "context_sufficiency": "sufficient|partial|insufficient",\n'
        '  "slides": [{"n": 1, "title": "<short>", "purpose": "<one line>", "key_points": ["<3-5 bullets>"]}, ...],\n'
        '  "estimated_cost_note": "<1 line, e.g. \\"Deep tier; consumes 1 of 3 daily deck slots\\"">\n'
        "}\n"
        "RULES:\n"
        "1. NEVER invent evidence ids — use only ids from the lists above.\n"
        "2. If `context_sufficiency` is `insufficient` or `partial`, the user "
        "should be discouraged from generating until they upload more docs. "
        "Be specific in `missing_context`.\n"
        "3. Slide count must equal target_slides.\n"
        "4. Be calm, editorial — AKKI house style. No marketing language.\n"
    )


@router.post("/api/contexts/{context_id}/decks/outline", status_code=202)
async def create_outline(
    context_id: str,
    body: OutlineIn,
    ctx: Dict[str, Any] = Depends(require_context_membership()),
):
    """JC-DECK-GEN-ASYNC-KICKOFF-POLL (2026-07-05) — async kick-off for outline planning.

    Returns 202 immediately with a `job_id` + `status_url` handle. The Shield-routed
    LLM outline call runs in a background task; the FE polls the status endpoint.

    Even though outline is a STANDARD-tier call (no deep-slot burn), it goes
    through Shield which has an internal 20s LLM provider timeout — so leaving
    it synchronous ships the same DETERMINISTIC-EDGE-TIMEOUT-CEILING bug the
    generate path had. Point-3 mandate: no existing endpoint left synchronous
    behind the ceiling.
    """
    account_id = ctx["account"]["id"]
    user_id = ctx["account"].get("id")
    # Snapshot the intent so the request body isn't referenced by the runner.
    intent_snapshot = body.intent.strip()
    audience_snapshot = body.audience
    target_slides_snapshot = body.target_slides or 8
    parent_outline_id_snapshot = body.parent_outline_id

    # Use a stable-ish target_id derived from the intent (so back-to-back
    # identical POSTs return the same in-flight job).
    import hashlib
    target_id = hashlib.sha256(
        f"outline:{context_id}:{intent_snapshot}:{parent_outline_id_snapshot or ''}".encode("utf-8")
    ).hexdigest()[:32]

    job = await deck_generation_jobs.create_job(
        job_kind="outline",
        account_id=account_id,
        context_id=context_id,
        user_id=user_id,
        target_id=target_id,
    )

    if job["phase"] != deck_generation_jobs.PHASE_QUEUED:
        return {
            "job_id": job["job_id"],
            "phase": job["phase"],
            "status_url": (
                f"/api/contexts/{context_id}/decks/generation-status/{job['job_id']}"
            ),
        }

    await deck_generation_jobs.spawn_generation(
        job["job_id"],
        lambda jid: _run_outline_job(
            job_id=jid,
            context_id=context_id,
            ctx=ctx,
            intent=intent_snapshot,
            audience=audience_snapshot,
            target_slides=target_slides_snapshot,
            parent_outline_id=parent_outline_id_snapshot,
        ),
    )

    return {
        "job_id": job["job_id"],
        "phase": deck_generation_jobs.PHASE_QUEUED,
        "status_url": (
            f"/api/contexts/{context_id}/decks/generation-status/{job['job_id']}"
        ),
    }


async def _run_outline_job(
    *,
    job_id: str,
    context_id: str,
    ctx: Dict[str, Any],
    intent: str,
    audience: Optional[str],
    target_slides: int,
    parent_outline_id: Optional[str],
) -> Dict[str, Any]:
    """Background runner for outline planning. Engine calls UNCHANGED — this
    function contains the exact same steps that used to run inline, annotated
    with phase markers.
    """
    await deck_generation_jobs.set_phase(
        job_id, deck_generation_jobs.PHASE_READING, progress=15,
    )
    ctx_name = ctx["context"].get("name") or "the company"
    evidence = await _gather_context_signals(ctx["account"]["id"], context_id)

    last_regen = await db.decks.find_one(
        {"context_id": context_id,
         "account_id": ctx["account"]["id"],
         "user_feedback.regen_reason": {"$nin": [None, ""]}},
        {"_id": 0, "user_feedback.regen_reason": 1, "user_feedback.comment": 1},
        sort=[("created_at", -1)],
    )
    learning_hint = None
    if last_regen and last_regen.get("user_feedback"):
        reason = last_regen["user_feedback"].get("regen_reason")
        comment = last_regen["user_feedback"].get("comment")
        if reason:
            label = {
                "audience_drift":         "the deck drifted from the audience",
                "weak_research_question": "the research question was too weak",
                "missing_evidence":       "key evidence was missing",
                "wrong_tone":             "the tone was off",
                "other":                  "the deck didn't land",
            }.get(reason, reason)
            learning_hint = label + (f" — user said: \"{comment}\"" if comment else "")

    prompt = _outline_prompt(
        intent, audience, target_slides, ctx_name, evidence,
        learning_hint=learning_hint,
    )

    await deck_generation_jobs.set_phase(
        job_id, deck_generation_jobs.PHASE_STRUCTURING, progress=50,
    )
    from llm_service import call_llm
    llm_out = await call_llm(
        module="decks.outline",
        user_query=prompt,
        response_format="json",
        tier="standard",   # ← never charges the deep budget
    )
    raw = llm_out.get("response") or "{}"
    parsed = _safe_json(raw)
    if not parsed or "slides" not in parsed:
        await deck_generation_jobs.set_error(job_id, {
            "type": "MalformedOutlineResponse",
            "message": "Outline planner returned malformed response.",
            "status": 502,
        })
        return {}

    await deck_generation_jobs.set_phase(
        job_id, deck_generation_jobs.PHASE_DRAFTING, progress=85,
    )

    # Iteration count if iterating on a prior outline.
    iteration = 1
    if parent_outline_id:
        parent = await db.deck_outlines.find_one(
            {"id": parent_outline_id, "context_id": context_id},
            {"_id": 0, "iteration": 1},
        )
        if parent:
            iteration = (parent.get("iteration") or 1) + 1

    outline_id = str(uuid.uuid4())
    rec = {
        "id": outline_id,
        "context_id": context_id,
        "account_id": ctx["account"]["id"],
        "intent": intent,
        "audience": audience,
        "target_slides": target_slides,
        "research_question": parsed.get("research_question"),
        "audience_assumed": parsed.get("audience_assumed"),
        "evidence_used": parsed.get("evidence_used") or [],
        "missing_context": parsed.get("missing_context") or [],
        "context_sufficiency": parsed.get("context_sufficiency") or "partial",
        "slides": parsed.get("slides") or [],
        "estimated_cost_note": parsed.get("estimated_cost_note"),
        "model": llm_out.get("model"),
        "tier": llm_out.get("tier"),
        "iteration": iteration,
        "parent_outline_id": parent_outline_id,
        "approved": False,
        "consumed_deck_id": None,
        "learning_hint_used": learning_hint,
        "created_at": iso(now()),
    }
    await db.deck_outlines.insert_one(rec)
    rec.pop("_id", None)
    await deck_generation_jobs.set_result(job_id, rec)
    return rec


# ---------------------------------------------------------------------------
# Generate — DEEP tier (Opus). Only fires after outline is approved.
# Consumes 1 deck-quota slot per call.
# ---------------------------------------------------------------------------
def _generate_prompt(outline: Dict[str, Any], ctx_name: str) -> str:
    slides_block = "\n".join(
        f"- Slide {s['n']}: {s.get('title','')} — {s.get('purpose','')}\n"
        f"  Key points: {'; '.join(s.get('key_points') or [])}"
        for s in outline.get("slides") or []
    )
    return (
        "Generate the full slide deck for AKKI in the calm, editorial house "
        "style. Each slide is a markdown block with a title and 3-6 bullet "
        "lines or a short paragraph. Use the approved outline; do not invent "
        "new slides or merge them.\n\n"
        f"CONTEXT: {ctx_name}\n"
        f"AUDIENCE: {outline.get('audience_assumed') or 'board/ExCo'}\n"
        f"RESEARCH QUESTION: {outline.get('research_question') or ''}\n\n"
        "APPROVED OUTLINE:\n" + slides_block + "\n\n"
        "Return STRICT JSON:\n"
        "{\n"
        '  "title": "<deck title, max 90 chars>",\n'
        '  "subtitle": "<single line, max 120 chars>",\n'
        '  "slides": [{"n": 1, "title": "<short>", "body_md": "<markdown body>"}, ...],\n'
        '  "speaker_notes": ["<one note per slide, 1-2 sentences each>"]\n'
        "}\n"
    )


# ---------------------------------------------------------------------------
# JC-DECK-GENERATE-CHUNKED-INVOCATION (2026-07-08) — A1 chunked invocation.
# Partitions the single LLM call into meta + N slide-batch chunks. Each chunk
# fits under the Shield 20s wait_for ceiling. All 14 governance controls
# (M1-M13 + M16) preserved by staying inside `call_llm_with_tier → call_llm →
# shield_invoke → invoke_with_metering`. Per-chunk 19-field audit row + 13-field
# trust receipt emitted N+1 times per user request (expected · honest metering).
# ---------------------------------------------------------------------------
# House-style directive shared across all chunk prompts so cross-chunk
# stylistic consistency is deterministic (not delegated to LLM inference).
_CHUNK_HOUSE_STYLE = (
    "Voice: calm, editorial, third person. Sentence length: medium. Avoid "
    "hype adjectives (transformative, revolutionary, groundbreaking). Use "
    "concrete nouns and specific numbers where the outline supplies them. "
    "Each slide body is 3-6 markdown bullet lines OR a short paragraph "
    "(pick one per slide). Never both. No headings inside the slide body."
)


def _generate_meta_prompt(outline: Dict[str, Any], ctx_name: str) -> str:
    """Chunk 0 · deck-level metadata (title + subtitle + high-level frame).

    Small, fast prompt — bounded output ~200-400 tokens. Fits well under 20s.
    """
    slide_titles = [s.get("title", "") for s in (outline.get("slides") or [])]
    return (
        "Produce the deck-level metadata (title + subtitle) for a slide "
        "deck about the following research question. Use the calm, editorial "
        "AKKI house style.\n\n"
        f"CONTEXT: {ctx_name}\n"
        f"AUDIENCE: {outline.get('audience_assumed') or 'board/ExCo'}\n"
        f"RESEARCH QUESTION: {outline.get('research_question') or ''}\n\n"
        "SLIDE TITLES (already approved by user; do not invent new slides):\n"
        + "\n".join(f"- {t}" for t in slide_titles) + "\n\n"
        f"{_CHUNK_HOUSE_STYLE}\n\n"
        "Return STRICT JSON only:\n"
        "{\n"
        '  "title": "<deck title, max 90 chars>",\n'
        '  "subtitle": "<single line, max 120 chars>"\n'
        "}\n"
    )


def _generate_chunk_prompt(
    outline: Dict[str, Any],
    ctx_name: str,
    chunk_slides: list,
    *,
    chunk_index: int,
    total_chunks: int,
    prior_titles: list,
) -> str:
    """Chunks 1..N · slide bodies for a contiguous batch of outline slides.

    Prior-titles context threads the cited-entity continuity axis (R-COH-5) —
    each chunk sees the titles produced in earlier chunks so entity/theme
    references remain consistent across chunk seams without duplicating full
    prior content (keeps chunk size bounded).
    """
    slides_block = "\n".join(
        f"- Slide {s['n']}: {s.get('title','')} — {s.get('purpose','')}\n"
        f"  Key points: {'; '.join(s.get('key_points') or [])}"
        for s in chunk_slides
    )
    prior_block = (
        "\nEARLIER-CHUNK SLIDE TITLES (for continuity; do NOT repeat their bodies):\n"
        + "\n".join(f"- {t}" for t in prior_titles) + "\n"
    ) if prior_titles else ""
    return (
        f"Produce the slide bodies for chunk {chunk_index} of {total_chunks} "
        "of a slide deck for AKKI. Use the approved outline; do NOT invent "
        "new slides, merge slides, or renumber. Preserve the slide `n` "
        "values from the outline verbatim.\n\n"
        f"CONTEXT: {ctx_name}\n"
        f"AUDIENCE: {outline.get('audience_assumed') or 'board/ExCo'}\n"
        f"RESEARCH QUESTION: {outline.get('research_question') or ''}\n"
        f"{prior_block}\n"
        "SLIDES FOR THIS CHUNK:\n" + slides_block + "\n\n"
        f"{_CHUNK_HOUSE_STYLE}\n\n"
        "Return STRICT JSON only:\n"
        "{\n"
        '  "slides": [{"n": <int>, "title": "<short>", "body_md": "<markdown body>"}, ...],\n'
        '  "speaker_notes": [{"n": <int>, "note": "<one note, 1-2 sentences>"}, ...]\n'
        "}\n"
        "The `slides` array must contain EXACTLY the slides listed above "
        "(same count, same `n` values, same order). Same for `speaker_notes`."
    )


def _partition_outline_slides(slides: list, *, chunk_size: int = 3) -> list:
    """Partition outline slides into contiguous chunks of at most `chunk_size`.

    Guarantees each chunk stays small enough that Shield's 20s wait_for cap on
    `invoke_with_metering` does not trigger. Empirically 2-3 slide bodies per
    chunk finishes well under 20s on Opus 4.6 tier.
    """
    return [slides[i:i + chunk_size] for i in range(0, len(slides), chunk_size)]


def _aggregate_chunks(
    meta_parsed: Dict[str, Any],
    chunk_parsed_list: list,
    outline: Dict[str, Any],
) -> Dict[str, Any]:
    """Merge meta + N chunk results into the final deck payload shape.

    Output shape identical to the pre-chunking `_generate_prompt` response
    contract — this preserves every downstream consumer (validator, sensitivity
    scorer, telemetry, FE parser). Aggregation is deterministic (no LLM call).
    """
    all_slides: list = []
    all_notes: list = []
    outline_slides = outline.get("slides") or []
    outline_by_n = {int(s.get("n", -1)): s for s in outline_slides if s.get("n") is not None}

    for ck in chunk_parsed_list:
        for slide in ck.get("slides") or []:
            all_slides.append(slide)
        for note in ck.get("speaker_notes") or []:
            all_notes.append(note)

    # Sort by outline `n` so the merged order matches the outline exactly.
    all_slides.sort(key=lambda s: int(s.get("n") or 0))
    all_notes.sort(key=lambda n: int(n.get("n") or 0) if isinstance(n, dict) else 0)

    # Flatten notes to the legacy shape (list of strings, per outline slide order).
    flat_notes = [
        (n.get("note") if isinstance(n, dict) else str(n))[:400]
        for n in all_notes
    ]

    # Backfill missing slides from outline (defensive — never lose an outline slide).
    seen_ns = {int(s.get("n") or 0) for s in all_slides}
    for outline_n, outline_slide in outline_by_n.items():
        if outline_n not in seen_ns:
            all_slides.append({
                "n": outline_n,
                "title": outline_slide.get("title") or f"Slide {outline_n}",
                "body_md": "",  # coherence check R-COH-3 will flag empty body
            })
    all_slides.sort(key=lambda s: int(s.get("n") or 0))

    return {
        "title": (meta_parsed.get("title") or "Untitled deck")[:120],
        "subtitle": (meta_parsed.get("subtitle") or "")[:200],
        "slides": all_slides,
        "speaker_notes": flat_notes,
    }


def _validate_coherence(assembled: Dict[str, Any], outline: Dict[str, Any]) -> Dict[str, Any]:
    """Coherence quality gate · R-COH-1..R-COH-5 · qualitative + quantitative.

    Returns {"ok": bool, "failures": [{"row": ..., "detail": ...}, ...]}.
    If any R-COH row fails, the caller should mark the job BLOCKED-ON-COHERENCE
    and surface the failure list. Does NOT ship SHIPPED.
    """
    failures: list = []
    slides = assembled.get("slides") or []
    outline_slides = outline.get("slides") or []
    outline_count = len(outline_slides)

    # R-COH-1 · no orphan section headers (every slide has both title and body)
    for s in slides:
        title = (s.get("title") or "").strip()
        body = (s.get("body_md") or "").strip()
        if title and not body:
            failures.append({
                "row": "R-COH-1",
                "detail": f"orphan section header · slide n={s.get('n')} title={title[:60]!r} · body_md empty",
            })
        elif body and not title:
            failures.append({
                "row": "R-COH-1",
                "detail": f"orphan body · slide n={s.get('n')} body_md non-empty but title empty",
            })

    # R-COH-2 · no duplicated titles across slides
    titles = [(s.get("title") or "").strip().lower() for s in slides if (s.get("title") or "").strip()]
    seen = set()
    dups = set()
    for t in titles:
        if t in seen:
            dups.add(t)
        seen.add(t)
    if dups:
        failures.append({
            "row": "R-COH-2",
            "detail": f"duplicated slide titles: {sorted(dups)[:5]}",
        })

    # R-COH-3 · no truncated bullets or sentences at chunk seams
    # Heuristic: body_md ending in a partial word (no trailing punctuation/newline)
    # and non-empty is a suspect truncation. Skip empty bodies (already R-COH-1).
    for s in slides:
        body = (s.get("body_md") or "").rstrip()
        if not body:
            continue
        last_char = body[-1]
        # Acceptable terminators: ., !, ?, ), ], `, quote marks, list closers
        if last_char not in {".", "!", "?", ")", "]", "`", '"', "'", "*", "_"}:
            # Also accept newline-terminated bullet groups
            if not body.endswith(("\n",)) and len(body.split()[-1]) > 2:
                # Word chars only — flag as suspect truncation
                if body.split()[-1].isalpha():
                    failures.append({
                        "row": "R-COH-3",
                        "detail": f"suspect truncation · slide n={s.get('n')} body ends {body[-40:]!r}",
                    })

    # R-COH-4 · narrative arc — slide count == outline count, ordered by n
    if len(slides) != outline_count:
        failures.append({
            "row": "R-COH-4",
            "detail": f"slide count mismatch · assembled={len(slides)} vs outline={outline_count}",
        })
    prev_n = -1
    for s in slides:
        n = int(s.get("n") or 0)
        if n <= prev_n:
            failures.append({
                "row": "R-COH-4",
                "detail": f"narrative arc broken · slide sequence not monotonic at n={n} (prev={prev_n})",
            })
            break
        prev_n = n

    # R-COH-5 · cited-entity continuity — heuristic: research_question terms
    # that appear in outline should not be introduced from scratch by "This
    # deck..." or "In this deck" phrasing multiple times (structural marker
    # for chunks that don't know about each other). Also verify count of
    # meta-references stays bounded.
    body_concat = " ".join((s.get("body_md") or "") for s in slides).lower()
    intro_markers = ["this deck examines", "this deck covers", "this deck explores"]
    intro_hits = sum(body_concat.count(m) for m in intro_markers)
    if intro_hits > 1:
        failures.append({
            "row": "R-COH-5",
            "detail": f"cited-entity continuity broken · '{intro_hits}' redundant deck-scope introductions across chunks",
        })

    return {"ok": not failures, "failures": failures}


@router.post("/api/contexts/{context_id}/decks/{outline_id}/generate", status_code=202)
async def generate_deck(
    context_id: str,
    outline_id: str,
    body: GenerateIn,
    ctx: Dict[str, Any] = Depends(require_context_membership()),
):
    """JC-DECK-GEN-ASYNC-KICKOFF-POLL (2026-07-05) — async kick-off.

    Returns 202 immediately with a `job_id` + `status_url` handle. The heavy
    LLM-await work runs in a background task; the FE polls the status endpoint.

    Pre-conditions (validated synchronously before returning 202):
      - `body.confirmed` must be True (invisible auto-confirm from FE per Stage 1).
      - Outline must exist in this context (404 if not).
      - Outline must not already have been consumed (409 with existing envelope).

    The engine invocation itself is UNCHANGED — this endpoint only wraps it in
    an asyncio background task and instruments phase transitions on a job row.
    Zero touches to `call_llm_with_tier`, `validate_independent`, the audit
    write, or the LLM adapters.
    """
    if not body.confirmed:
        raise HTTPException(
            status_code=400,
            detail="Deck generation requires explicit confirmation that the outline is approved.",
        )
    outline = await db.deck_outlines.find_one(
        {"id": outline_id, "context_id": context_id},
        {"_id": 0},
    )
    if not outline:
        raise HTTPException(status_code=404, detail="Outline not found.")
    if outline.get("consumed_deck_id"):
        raise HTTPException(
            status_code=409,
            detail="This outline has already produced a deck. Iterate the outline to make a new one.",
        )

    account_id = ctx["account"]["id"]
    user_id = ctx["account"].get("id")

    # Create a job row (or return existing in-flight job for idempotency).
    job = await deck_generation_jobs.create_job(
        job_kind="source_generate",
        account_id=account_id,
        context_id=context_id,
        user_id=user_id,
        target_id=outline_id,
    )

    # If the job is already terminal (unlikely — same target_id after commit),
    # short-circuit with the terminal state instead of spawning a new task.
    if job["phase"] not in (
        deck_generation_jobs.PHASE_QUEUED,
    ):
        return {
            "job_id": job["job_id"],
            "phase": job["phase"],
            "status_url": (
                f"/api/contexts/{context_id}/decks/generation-status/{job['job_id']}"
            ),
        }

    # Snapshot the request context so the background task doesn't rely on the
    # request lifecycle (which returns 202 immediately after this).
    edits = body.edits
    await deck_generation_jobs.spawn_generation(
        job["job_id"],
        lambda jid: _run_generate_deck_job(
            job_id=jid,
            context_id=context_id,
            outline_id=outline_id,
            ctx=ctx,
            edits=edits,
        ),
    )

    return {
        "job_id": job["job_id"],
        "phase": deck_generation_jobs.PHASE_QUEUED,
        "status_url": (
            f"/api/contexts/{context_id}/decks/generation-status/{job['job_id']}"
        ),
    }


async def _run_generate_deck_job(
    *,
    job_id: str,
    context_id: str,
    outline_id: str,
    ctx: Dict[str, Any],
    edits: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """Background runner for the source/blank generate flow.

    Instruments the wrapper with phase transitions at natural boundaries.
    The engine body (LLM call, validator, sensitivity, telemetry, audit) is
    UNCHANGED — this function contains the exact same steps that used to run
    inline, just annotated with phase markers before/after each block.
    """
    # ------ Phase: reading_sources — outline read + edit apply -------
    await deck_generation_jobs.set_phase(
        job_id, deck_generation_jobs.PHASE_READING, progress=10,
    )
    outline = await db.deck_outlines.find_one(
        {"id": outline_id, "context_id": context_id},
        {"_id": 0},
    )
    if not outline:
        await deck_generation_jobs.set_error(job_id, {
            "type": "OutlineNotFound", "message": "Outline vanished between kickoff and runner", "status": 404,
        })
        return {}

    edits_applied: Dict[str, Any] = {}
    if edits:
        if edits.get("research_question"):
            outline["research_question"] = edits["research_question"][:280]
            edits_applied["research_question"] = outline["research_question"]
        if edits.get("slides"):
            outline["slides"] = edits["slides"]
            edits_applied["slides_edited"] = True
        if edits.get("audience_assumed"):
            outline["audience_assumed"] = edits["audience_assumed"]
            edits_applied["audience_assumed"] = outline["audience_assumed"]

    ctx_name = ctx["context"].get("name") or "the company"

    # ------ Phase: structuring — CHUNKED LLM calls (JC-DECK-GENERATE-CHUNKED-INVOCATION 2026-07-08) --
    # A1 chunked invocation: partition the single ~30s LLM call into meta + N slide-batch chunks,
    # each fitting under the Shield 20s wait_for cap on `invoke_with_metering`. Preserves all 14
    # governance controls (M1-M13 + M16) — each chunk emits a full 19-field audit row + 13-field
    # trust receipt via the existing `call_llm_with_tier → call_llm → shield_invoke` chain.
    # No re-routing to streaming; stays inside the metering adapter.
    await deck_generation_jobs.set_phase(
        job_id, deck_generation_jobs.PHASE_STRUCTURING, progress=20,
    )
    from llm_tier_quota import call_llm_with_tier

    outline_slides = outline.get("slides") or []
    slide_chunks = _partition_outline_slides(outline_slides, chunk_size=3)
    total_chunks = 1 + len(slide_chunks)  # 1 meta + N slide-batch chunks
    logger.info(
        "deck-gen-chunked · job=%s outline_slides=%d chunk_count=%d (1 meta + %d slide-batch chunks of <=3 slides each)",
        job_id, len(outline_slides), total_chunks, len(slide_chunks),
    )

    # Chunk 0 · meta (title + subtitle)
    meta_prompt = _generate_meta_prompt(outline, ctx_name)
    meta_out, quota_state = await call_llm_with_tier(
        surface="deck",
        account_id=ctx["account"]["id"],
        requested_tier="deep",
        call_args={
            "module": "decks.generate.meta",
            "user_query": meta_prompt,
            "response_format": "json",
        },
    )
    meta_parsed = _safe_json(meta_out.get("response") or "{}") or {}
    if not meta_parsed.get("title"):
        await deck_generation_jobs.set_error(job_id, {
            "type": "MalformedGeneratorResponse",
            "message": "Deck generator returned malformed response (meta chunk missing title).",
            "status": 502,
        })
        return {}

    # Chunks 1..N · slide-batch bodies
    chunk_parsed_list: list = []
    prior_titles: list = []
    chunk_call_evidence: list = []  # per-chunk metering evidence for R-METER rows
    for i, chunk_slides in enumerate(slide_chunks, start=1):
        chunk_prompt = _generate_chunk_prompt(
            outline, ctx_name, chunk_slides,
            chunk_index=i, total_chunks=len(slide_chunks),
            prior_titles=prior_titles,
        )
        # Progress lifts smoothly from 20 to 65 across the chunk loop.
        chunk_progress = 20 + int(((i / max(1, len(slide_chunks))) * 45))
        await deck_generation_jobs.set_phase(
            job_id, deck_generation_jobs.PHASE_STRUCTURING, progress=chunk_progress,
        )
        chunk_out, quota_state = await call_llm_with_tier(
            surface="deck",
            account_id=ctx["account"]["id"],
            requested_tier="deep",
            call_args={
                "module": f"decks.generate.chunk_{i}_of_{len(slide_chunks)}",
                "user_query": chunk_prompt,
                "response_format": "json",
            },
        )
        chunk_parsed = _safe_json(chunk_out.get("response") or "{}") or {}
        if not chunk_parsed.get("slides"):
            await deck_generation_jobs.set_error(job_id, {
                "type": "MalformedGeneratorResponse",
                "message": f"Deck generator returned malformed response (chunk {i}/{len(slide_chunks)} missing slides).",
                "status": 502,
            })
            return {}
        chunk_parsed_list.append(chunk_parsed)
        prior_titles.extend(
            (s.get("title") or "") for s in chunk_parsed.get("slides") or []
        )
        # Per-chunk metering evidence — model + tier surfaced back by
        # call_llm_with_tier; audit row already written by Shield's
        # invoke_with_metering under the hood.
        chunk_call_evidence.append({
            "chunk_index": i,
            "slide_count": len(chunk_slides),
            "outline_n_range": [chunk_slides[0].get("n"), chunk_slides[-1].get("n")],
            "model": chunk_out.get("model"),
            "tier": chunk_out.get("tier"),
        })

    parsed = _aggregate_chunks(meta_parsed, chunk_parsed_list, outline)
    # llm_out surface for downstream code paths that expect a single result dict.
    llm_out = {
        "response": json.dumps(parsed),
        "model": meta_out.get("model"),
        "tier": meta_out.get("tier"),
    }

    if not parsed or "slides" not in parsed:
        await deck_generation_jobs.set_error(job_id, {
            "type": "MalformedGeneratorResponse",
            "message": "Deck aggregator returned malformed response.",
            "status": 502,
        })
        return {}

    # Coherence quality gate · R-COH-1..R-COH-5 (mandatory per user's A1 ruling).
    coherence = _validate_coherence(parsed, outline)
    if not coherence["ok"]:
        await deck_generation_jobs.set_error(job_id, {
            "type": "BlockedOnCoherence",
            "message": "Chunked deck failed coherence quality gate.",
            "failures": coherence["failures"],
            "chunk_evidence": chunk_call_evidence,
            "status": 502,
        })
        logger.warning(
            "deck-gen-chunked · job=%s BLOCKED-ON-COHERENCE · %d failures",
            job_id, len(coherence["failures"]),
        )
        return {}


    # ------ Phase: drafting — post-process (validator, sensitivity, telemetry) --
    await deck_generation_jobs.set_phase(
        job_id, deck_generation_jobs.PHASE_DRAFTING, progress=70,
    )

    deck_id = str(uuid.uuid4())
    rec = {
        "id": deck_id,
        "context_id": context_id,
        "account_id": ctx["account"]["id"],
        "outline_id": outline_id,
        "intent": outline.get("intent"),
        "research_question": outline.get("research_question"),
        "audience": outline.get("audience_assumed") or outline.get("audience"),
        "title": (parsed.get("title") or "Untitled deck")[:120],
        "subtitle": (parsed.get("subtitle") or "")[:200],
        "slides": parsed.get("slides") or [],
        "speaker_notes": parsed.get("speaker_notes") or [],
        "model": llm_out.get("model"),
        "model_id": llm_out.get("model"),
        "tier": llm_out.get("tier"),
        "quota": quota_state,
        "quality_check": None,
        "user_feedback": None,
        "regen_count": 0,
        "created_at": iso(now()),
    }
    # Iter64 — auto-score sensitivity on every saved artefact (Studio
    # surface contract). Deterministic regex-based scoring; no LLM call.
    try:
        from studio_sensitivity import score_sensitivity
        rec["sensitivity"] = score_sensitivity(rec)
    except Exception as e:  # noqa: BLE001
        logger.warning("Sensitivity scoring failed for deck %s: %s", deck_id, e)
        rec["sensitivity"] = None

    # Phase 11 ITEM B — independent-model validator. Best-effort and
    # non-blocking. The validator helper is contracted to ALWAYS return a
    # dict (even on cap, timeout, no-key, or exception) — null here would
    # mean we lost the diagnostic trail entirely. We therefore default to
    # a "qualified-with-reason" fallback when the import or call site
    # itself raises, so the persisted state is honest about why we
    # couldn't get a real verdict.
    validation_payload = {
        "verdict": "qualified", "confidence": 0,
        "notes": ["Validator wrapper failed before call; treat with normal scrutiny."],
        "validator_provider": "n/a", "validator_model": "n/a",
    }
    try:
        from llm_service import validate_independent
        slide_concat = "\n\n".join(
            f"{s.get('title','')}\n{s.get('body_md','')}"
            for s in (rec.get("slides") or [])
        )
        validation_payload = await validate_independent(
            kind="deck",
            content=slide_concat,
            objective=rec.get("research_question") or rec.get("intent"),
            surface="deck",
            account_id=ctx["account"]["id"],
        )
        logger.info(
            "deck validator persisted event=persisted surface=deck deck_id=%s "
            "verdict=%s provider=%s",
            deck_id,
            validation_payload.get("verdict"),
            validation_payload.get("validator_provider"),
        )
    except Exception as e:  # noqa: BLE001
        logger.warning(
            "deck validator wrapper failed event=wrapper_exception surface=deck "
            "deck_id=%s exc=%s reason=%s",
            deck_id, e.__class__.__name__, str(e)[:200],
        )
        validation_payload = {
            "verdict": "qualified", "confidence": 0,
            "notes": [f"Validator wrapper error ({e.__class__.__name__}); treat with normal scrutiny."],
            "validator_provider": "n/a", "validator_model": "n/a",
        }
    rec["validation"] = validation_payload
    await db.decks.insert_one(rec)
    rec.pop("_id", None)

    # Mark outline as consumed.
    await db.deck_outlines.update_one(
        {"id": outline_id, "context_id": context_id},
        {"$set": {
            "approved": True,
            "consumed_deck_id": deck_id,
            "approved_at": iso(now()),
            "edits_applied": edits_applied or None,
            # Snapshot the post-edit research_question / slides on the outline
            # so admin & history views show what was actually generated.
            "research_question": outline.get("research_question"),
            "slides": outline.get("slides"),
            "audience_assumed": outline.get("audience_assumed"),
        }},
    )

    # Telemetry — used by /admin/llm/spend → deck quality panel.
    await db.deck_telemetry.insert_one({
        "id": str(uuid.uuid4()),
        "deck_id": deck_id,
        "outline_id": outline_id,
        "context_id": context_id,
        "account_id": ctx["account"]["id"],
        "outline_iterations": outline.get("iteration") or 1,
        "context_sufficiency": outline.get("context_sufficiency"),
        "tier_served": llm_out.get("tier"),
        "quota_downgraded": (quota_state or {}).get("downgraded", False),
        "created_at": iso(now()),
    })

    await write_audit(
        context_id, ctx["account"]["id"],
        "deck.generated", "deck", deck_id,
        {"slides": len(rec["slides"]), "tier": rec["tier"],
         "outline_iterations": outline.get("iteration") or 1},
    )

    # ------ Phase: complete -------
    await deck_generation_jobs.set_result(job_id, rec)
    return rec


@router.get("/api/contexts/{context_id}/decks/generation-status/{job_id}")
async def get_generation_status(
    context_id: str,
    job_id: str,
    ctx: Dict[str, Any] = Depends(require_context_membership()),
):
    """JC-DECK-GEN-ASYNC-KICKOFF-POLL (2026-07-05) — poll endpoint.

    Returns `{job_id, phase, progress, result?, error?}`. Idempotent — safe to
    poll repeatedly. Account-scoped: reading a job that belongs to a different
    account returns 404 (indistinguishable from non-existence to prevent
    enumeration).
    """
    account_id = ctx["account"]["id"]
    job = await deck_generation_jobs.get_job(job_id, account_id=account_id)
    if not job or job.get("context_id") != context_id:
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


# ---------------------------------------------------------------------------
# Quality check — FAST tier; scores deck against original intent + outline.
# Critical: this gives the user a soft refine path that costs ZERO deep
# budget. Without it, dissatisfied users would burn their daily slots
# regenerating.
# ---------------------------------------------------------------------------
def _quality_prompt(deck: Dict[str, Any]) -> str:
    slides = "\n\n".join(
        f"### Slide {s.get('n')}: {s.get('title','')}\n{s.get('body_md','')}"
        for s in (deck.get("slides") or [])
    )
    return (
        "You are AKKI's deck quality auditor. Score how well this deck answers "
        "the user's research question, and surface concrete refinements the user "
        "could make WITHOUT regenerating.\n\n"
        f"USER INTENT: {deck.get('intent')}\n"
        f"RESEARCH QUESTION: {deck.get('research_question')}\n"
        f"AUDIENCE: {deck.get('audience')}\n\n"
        "DECK CONTENT:\n" + slides + "\n\n"
        "Return STRICT JSON:\n"
        "{\n"
        '  "score": 0-100,\n'
        '  "answers_research_question": true|false,\n'
        '  "narrative_coherence": "strong|adequate|weak",\n'
        '  "evidence_density": "high|medium|low",\n'
        '  "audience_fit": "well-matched|partial|mismatched",\n'
        '  "strengths": ["<bullet>", "<bullet>"],\n'
        '  "weaknesses": ["<bullet>", "<bullet>"],\n'
        '  "free_refinements": ["<edit-not-regenerate guidance>", "..."],\n'
        '  "recommend_regenerate": true|false,\n'
        '  "regenerate_reason": "<one line if recommend_regenerate; else null>"\n'
        "}\n"
        "RULES: Recommend regeneration ONLY if score < 55 AND the issues "
        "cannot be fixed by the user editing slides directly."
    )


@router.post("/api/contexts/{context_id}/decks/{deck_id}/quality_check")
async def quality_check(
    context_id: str,
    deck_id: str,
    ctx: Dict[str, Any] = Depends(require_context_membership()),
):
    deck = await db.decks.find_one(
        {"id": deck_id, "context_id": context_id},
        {"_id": 0},
    )
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found.")

    from llm_service import call_llm
    llm_out = await call_llm(
        module="decks.quality_check",
        user_query=_quality_prompt(deck),
        response_format="json",
        tier="fast",   # ← Gemini Flash, free of deep budget
    )
    parsed = _safe_json(llm_out.get("response") or "{}")
    if not parsed or "score" not in parsed:
        raise HTTPException(status_code=502, detail="Quality auditor returned malformed response.")

    score = int(parsed.get("score") or 0)
    qc = {
        "score": score,
        "answers_research_question": bool(parsed.get("answers_research_question")),
        "narrative_coherence": parsed.get("narrative_coherence"),
        "evidence_density": parsed.get("evidence_density"),
        "audience_fit": parsed.get("audience_fit"),
        "strengths": parsed.get("strengths") or [],
        "weaknesses": parsed.get("weaknesses") or [],
        "free_refinements": parsed.get("free_refinements") or [],
        "recommend_regenerate": bool(parsed.get("recommend_regenerate")),
        "regenerate_reason": parsed.get("regenerate_reason"),
        "checked_at": iso(now()),
        "model": llm_out.get("model"),
    }
    await db.decks.update_one(
        {"id": deck_id, "context_id": context_id},
        {"$set": {"quality_check": qc}},
    )
    await db.deck_telemetry.update_one(
        {"deck_id": deck_id},
        {"$set": {"quality_score": score,
                  "quality_recommends_regen": qc["recommend_regenerate"]}},
    )
    return {"ok": True, "deck_id": deck_id, "quality_check": qc}


# ---------------------------------------------------------------------------
# Feedback — user signals satisfaction. Cheap, never spends deep budget.
# Drives the admin behaviour-monitoring panel.
# ---------------------------------------------------------------------------
@router.post("/api/contexts/{context_id}/decks/{deck_id}/feedback")
async def feedback(
    context_id: str,
    deck_id: str,
    body: FeedbackIn,
    ctx: Dict[str, Any] = Depends(require_context_membership()),
):
    deck = await db.decks.find_one(
        {"id": deck_id, "context_id": context_id},
        {"_id": 0, "id": 1},
    )
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found.")

    fb = {
        "rating": body.rating,
        "comment": body.comment,
        "will_regenerate": body.will_regenerate,
        "regen_reason": body.regen_reason,
        "submitted_at": iso(now()),
        "submitted_by": ctx["account"]["id"],
    }
    await db.decks.update_one(
        {"id": deck_id, "context_id": context_id},
        {"$set": {"user_feedback": fb}},
    )
    await db.deck_telemetry.update_one(
        {"deck_id": deck_id},
        {"$set": {"user_rating": body.rating,
                  "user_will_regenerate": body.will_regenerate,
                  "user_regen_reason": body.regen_reason}},
    )
    return {"ok": True, "deck_id": deck_id, "feedback": fb}


# ---------------------------------------------------------------------------
# List
# ---------------------------------------------------------------------------
@router.get("/api/contexts/{context_id}/decks")
async def list_decks(
    context_id: str,
    limit: int = 30,
    ctx: Dict[str, Any] = Depends(require_context_membership()),
):
    items = await db.decks.find(
        {"context_id": context_id},
        # Phase 11 ITEM B closeout — the list serializer must include
        # `validation` (the badge on `/app/decks` is rendered straight
        # from the list response, not the detail endpoint) and
        # `sensitivity` (the SensitivityChip on each row reads it from
        # here too). Both fields are full sub-documents — boto3-shape
        # projection inclusion lets Mongo return the entire nested
        # object without us having to enumerate sub-keys.
        {"_id": 0, "id": 1, "title": 1, "subtitle": 1, "research_question": 1,
         "audience": 1, "tier": 1, "model_id": 1,
         "created_at": 1, "quality_check.score": 1, "user_feedback.rating": 1,
         "validation": 1, "sensitivity": 1,
         # Phase C.3 — Solva-seeded decks carry a top-level brief_id so the
         # Decks listing row can render the Refine button (which opens
         # EnhanceModal in C.2 mode). Status surfaces the draft chip.
         "brief_id": 1, "status": 1},
    ).sort("created_at", -1).to_list(length=max(1, min(limit, 100)))
    return {"items": items, "count": len(items)}


@router.get("/api/contexts/{context_id}/decks/{deck_id}")
async def get_deck(
    context_id: str,
    deck_id: str,
    ctx: Dict[str, Any] = Depends(require_context_membership()),
):
    deck = await db.decks.find_one(
        {"id": deck_id, "context_id": context_id},
        {"_id": 0},
    )
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found.")
    return deck


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _safe_json(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    s = text.strip()
    # Strip code fences if the model returned them despite instructions.
    s = re.sub(r"^```(?:json)?\s*", "", s)
    s = re.sub(r"\s*```\s*$", "", s)
    try:
        return json.loads(s)
    except Exception:  # noqa: BLE001
        # Last-ditch — try to find the first JSON object.
        m = re.search(r"\{.*\}", s, re.DOTALL)
        if not m:
            return None
        try:
            return json.loads(m.group(0))
        except Exception:  # noqa: BLE001
            return None



# ---------------------------------------------------------------------------
# Context resolver — iter65 deep-link helper.
# Given just a deck_id, returns the context_id the deck belongs to (only if
# the calling user is a member of that context). Used by the frontend to
# auto-switch active context when a /app/decks/{deck_id} deep link points
# to a deck in a context different from the user's currently-active one.
# ---------------------------------------------------------------------------
@router.get("/api/decks/{deck_id}/context")
async def resolve_deck_context(
    deck_id: str,
    account: Dict[str, Any] = Depends(get_current_account),
):
    deck = await db.decks.find_one({"id": deck_id}, {"_id": 0, "id": 1, "context_id": 1})  # tenancy:allow-no-account-id — deep-link resolver: deck fetched by id THEN membership verified against deck.context_id (L666-671); resolver IS the tenancy contract
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found.")
    member = await db.memberships.find_one(
        {"context_id": deck["context_id"], "account_id": account["id"], "status": "active"},
        {"_id": 0, "role": 1},
    )
    if not member:
        raise HTTPException(status_code=403, detail="Not a member of this deck's context.")
    return {"deck_id": deck["id"], "context_id": deck["context_id"]}
