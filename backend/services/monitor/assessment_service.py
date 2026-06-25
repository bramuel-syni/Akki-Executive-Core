"""JC-MON achievement engine — Stage 2a thin slice.

Source of truth: `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 2a).

The Q4 fit-verification already classified the path as **THIN ADAPTER**:
`probability_weighting` accepts the inputs a Monitor objective + tracked
evidence would hand it after a well-defined "objective → single grounded
claim" transformation. The full reproducible derivation lives at
`/app/memory/audit/JC_MON_solva_fit_verification.md`.

This service ships the thin adapter as a real, run-once-per-call assessor.
Two signals come back per objective:

  • **probability_pct** — via Solva's `probability_weighting` engine.
    The engine handles refusal discipline on its own (auto-calibrated
    fallback on twice-failed parse; tier-invariant 35-75 corridor for
    `corpus`-tier claims).
  • **progress_pct** — via a dedicated Shield-routed extractor that
    reads the BASE doc summaries + TRACKING doc summaries against the
    objective's `target_value` and returns a 0-100 progress estimate
    with a one-sentence rationale.

  Both signals carry their Shield trust-receipt audit ids. The caller
  persists those into `objective_assessments`.

The on-demand reassess trigger is honoured: this service is the entry
point for both (a) "user clicked reassess" AND (b) "a new tracking doc
was accepted in the Journal." No background tracker — the canonical
spec says background tracking layers on LATER once on-demand proves
trustworthy.

Refusal short-circuit (above-engine) per the canonical spec's
"REFUSE-when-thin" rule:
  - No tracking docs at all → refuse with reason "no_tracking_evidence_yet".

Engine refusal (below this adapter):
  - probability_weighting twice-failed parse → engine emits
    `pct=50, band="Possible", rationale="Auto-calibrated: ..."`.

Returns a dict of shape:
    {
      "objective_id":            "...",
      "refused":                 bool,
      "refusal_reason":          Optional[str],
      "progress_pct":            Optional[int],
      "progress_rationale":      Optional[str],
      "probability_pct":         Optional[int],
      "probability_band":        Optional[str],
      "probability_rationale":   Optional[str],
      "base_doc_ids":            List[str],
      "tracking_doc_ids":        List[str],
      "audit_entry_ids":         List[str],     # progress + probability
      "assessed_at":             "<ISO>",
    }
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.solva_v2.engines import probability_weighting as pw
from services.solva_v2.engines.llm_adapter_proxy import shielded_call


logger = logging.getLogger("akki.monitor.assessment")


_PROGRESS_SURFACE = "solve_v2.monitor_progress"
_PROGRESS_LAYER = "monitor.progress"
_PROBABILITY_LAYER = "monitor.probability"


_PROGRESS_SYSTEM_PROMPT = (
    "You are an AKKI Monitor assessor. Read the objective + target,"
    " plus the BASE doc evidence (the strategic plan or performance"
    " agreement that defines what's being tracked) and the TRACKING"
    " doc evidence (the progress updates and operational data). Then"
    " produce a SINGLE JSON object stating the progress against target"
    " today.\n\n"
    "Discipline:\n"
    " 1. The pct is 0-100. 0 = no movement against target; 100 = target"
    " met. If evidence is thin or ambiguous, anchor near 50 and say so"
    " in the rationale.\n"
    " 2. Cite which document each number comes from in the rationale"
    " (\"per tracking doc 2: …\").\n"
    " 3. NEVER invent a number with no source.\n"
    " 4. The rationale is one sentence (≤ 240 chars).\n\n"
    "Output JSON SHAPE ONLY:\n"
    "  {\"progress_pct\": <int 0-100>, \"rationale\": \"<one sentence>\"}\n"
    "No prose around the JSON. No code fences."
)


def _summarise_doc(doc: Dict[str, Any], char_cap: int = 600) -> str:
    """Compact one-line summary string for prompt assembly. We pull
    `name` + the first `char_cap` chars of `extracted_text` so the LLM
    has REAL content rather than a stub. If `extracted_text` is missing
    we fall back to whatever short description fields exist on the doc."""
    name = (doc.get("name") or doc.get("title") or "(untitled)").strip()
    text = (doc.get("extracted_text") or doc.get("summary") or doc.get("description") or "")
    text = (text or "").strip()
    if len(text) > char_cap:
        text = text[:char_cap].rstrip() + " …"
    return f"- {name}: {text}" if text else f"- {name}"


def _build_progress_prompt(
    *,
    objective: Dict[str, Any],
    base_docs: List[Dict[str, Any]],
    tracking_docs: List[Dict[str, Any]],
) -> str:
    base_block = "\n".join(_summarise_doc(d) for d in base_docs) or "  (none)"
    tracking_block = "\n".join(_summarise_doc(d) for d in tracking_docs) or "  (none)"
    return (
        f"OBJECTIVE:\n"
        f"  title:        {objective.get('title', '(untitled)')}\n"
        f"  description:  {objective.get('description', '(none)')}\n"
        f"  target_metric:{objective.get('target_metric', '(not set)')}\n"
        f"  target_value: {objective.get('target_value', '(not set)')}\n"
        f"  due_date:     {objective.get('due_date', '(no deadline)')}\n\n"
        f"BASE DOCS:\n{base_block}\n\n"
        f"TRACKING DOCS:\n{tracking_block}\n\n"
        f"Return the progress JSON now."
    )


_JSON_BLOB = re.compile(r"\{[^{}]*\"progress_pct\"\s*:\s*-?\d+[^{}]*\}", re.DOTALL)


def _parse_progress(raw: str) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    candidates = [raw.strip()]
    m = _JSON_BLOB.search(raw)
    if m:
        candidates.append(m.group(0))
    for c in candidates:
        try:
            obj = json.loads(c)
        except Exception:
            continue
        pct = obj.get("progress_pct")
        rationale = (obj.get("rationale") or "").strip()
        if isinstance(pct, (int, float)) and 0 <= pct <= 100:
            return {
                "progress_pct": int(round(pct)),
                "rationale": rationale[:240],
            }
    return None


async def _assess_progress(
    *,
    objective: Dict[str, Any],
    base_docs: List[Dict[str, Any]],
    tracking_docs: List[Dict[str, Any]],
    session: Dict[str, Any],
) -> Dict[str, Any]:
    """Single Shield-routed call producing the progress signal."""
    prompt = _build_progress_prompt(
        objective=objective, base_docs=base_docs, tracking_docs=tracking_docs,
    )
    result = await shielded_call(
        engine="monitor_progress",
        layer=_PROGRESS_LAYER,
        turn_id=objective["id"],
        prompt=prompt,
        system_override=_PROGRESS_SYSTEM_PROMPT,
        tier="standard",
        surface=_PROGRESS_SURFACE,
        account_id=session.get("account_id"),
        session_id=session["id"],
        context_id=session.get("context_id"),
        engine_version="monitor_progress@1.0",
        extra_output={
            "base_doc_count": len(base_docs),
            "tracking_doc_count": len(tracking_docs),
        },
    )
    parsed = _parse_progress(result.text)
    audit = result.reasoning_audit_entry
    if parsed is None:
        # Honest refusal — engine couldn't extract a number from the
        # evidence. Mid-band fallback with explicit rationale.
        return {
            "progress_pct": 50,
            "rationale": (
                "Auto-calibrated: progress extractor failed to return a "
                "parseable JSON over the supplied evidence."
            ),
            "audit_entry": audit,
            "parse_failed": True,
        }
    return {
        "progress_pct": parsed["progress_pct"],
        "rationale": parsed["rationale"] or "(no rationale returned)",
        "audit_entry": audit,
        "parse_failed": False,
    }


def _build_probability_claim(
    *,
    objective: Dict[str, Any],
    base_docs: List[Dict[str, Any]],
    tracking_docs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Single corpus-tier claim representing the objective's achievement
    likelihood given current trajectory. The single-claim adapter design
    is documented in the Q4 fit verification (`audit/JC_MON_solva_fit_verification.md`).
    """
    base_titles = ", ".join((d.get("name") or "?").strip() for d in base_docs) or "(none)"
    tracking_titles = ", ".join((d.get("name") or "?").strip() for d in tracking_docs) or "(none)"
    text = (
        f"{objective.get('title', '(untitled objective)')} "
        f"— target: {objective.get('target_value', '<not set>')}. "
        f"Will be achieved by {objective.get('due_date', '<no deadline>')} "
        f"given current trajectory across the BASE evidence "
        f"({base_titles}) and TRACKING evidence ({tracking_titles})."
    )
    return {
        "tier": "corpus",
        "text": text,
        # Free-form passthrough fields the engine preserves verbatim.
        "objective_id":     objective["id"],
        "base_doc_ids":     [d["id"] for d in base_docs],
        "tracking_doc_ids": [d["id"] for d in tracking_docs],
    }


async def assess_objective(
    *,
    objective: Dict[str, Any],
    base_docs: List[Dict[str, Any]],
    tracking_docs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Public entry — run the on-demand assessment for a single objective.

    Refusal short-circuit per canonical spec:
      - No tracking docs → refuse with reason 'no_tracking_evidence_yet'.

    Two real signals on success:
      - progress_pct (+ rationale + audit id) via Shield-routed extractor.
      - probability_pct (+ band + rationale + audit id) via
        Solva `probability_weighting` engine, single-claim adapter.
    """
    if not objective.get("id"):
        raise ValueError("assess_objective: objective.id is required")

    now_iso = datetime.now(timezone.utc).isoformat()
    base_doc_ids = [d["id"] for d in base_docs]
    tracking_doc_ids = [d["id"] for d in tracking_docs]

    if not tracking_docs:
        return {
            "objective_id":          objective["id"],
            "refused":                True,
            "refusal_reason":         "no_tracking_evidence_yet",
            "progress_pct":           None,
            "progress_rationale":     None,
            "probability_pct":        None,
            "probability_band":       None,
            "probability_rationale":  None,
            "base_doc_ids":           base_doc_ids,
            "tracking_doc_ids":       tracking_doc_ids,
            "audit_entry_ids":        [],
            "assessed_at":            now_iso,
        }

    session = {
        "id":         str(uuid.uuid4()),
        "account_id": objective.get("account_id"),
        "context_id": objective.get("context_id"),
    }

    # Run both signals. Sequential for clarity; both Shield-routed.
    progress_signal = await _assess_progress(
        objective=objective,
        base_docs=base_docs,
        tracking_docs=tracking_docs,
        session=session,
    )

    claim = _build_probability_claim(
        objective=objective,
        base_docs=base_docs,
        tracking_docs=tracking_docs,
    )
    pw_result = await pw.run(
        session=session,
        turn_id=objective["id"],
        layer=_PROBABILITY_LAYER,
        claims=[claim],
        comparables=None,
    )
    rated = (pw_result.get("output") or {}).get("claims") or []
    if not rated:
        return {
            "objective_id":          objective["id"],
            "refused":                True,
            "refusal_reason":         "engine_returned_no_ratings",
            "progress_pct":           progress_signal.get("progress_pct"),
            "progress_rationale":     progress_signal.get("rationale"),
            "probability_pct":        None,
            "probability_band":       None,
            "probability_rationale":  None,
            "base_doc_ids":           base_doc_ids,
            "tracking_doc_ids":       tracking_doc_ids,
            "audit_entry_ids":        _collect_audit_ids(progress_signal, pw_result),
            "assessed_at":            now_iso,
        }

    weighted = rated[0]
    return {
        "objective_id":           objective["id"],
        "refused":                False,
        "refusal_reason":         None,
        "progress_pct":           progress_signal.get("progress_pct"),
        "progress_rationale":     progress_signal.get("rationale"),
        "probability_pct":        int(weighted.get("confidence_pct", 0)),
        "probability_band":       weighted.get("confidence_band"),
        "probability_rationale":  weighted.get("confidence_rationale") or "",
        "base_doc_ids":           base_doc_ids,
        "tracking_doc_ids":       tracking_doc_ids,
        "audit_entry_ids":        _collect_audit_ids(progress_signal, pw_result),
        "assessed_at":            now_iso,
    }


def _collect_audit_ids(
    progress_signal: Dict[str, Any],
    pw_result: Dict[str, Any],
) -> List[str]:
    out: List[str] = []
    progress_entry = progress_signal.get("audit_entry") or {}
    if progress_entry.get("id"):
        out.append(progress_entry["id"])
    for ae in pw_result.get("audit_entries") or []:
        if ae.get("id"):
            out.append(ae["id"])
    return out


# ---------------------------------------------------------------------------
# JC-MON Stage 2b.1 — AI recommendations / interventions widen
# ---------------------------------------------------------------------------
# Canonical spec section: `/app/memory/JC_MON_CANONICAL_SPEC.md` § Stage 2b.
# "Each its own quality bar … 1. AI recommendations / interventions". Builds
# ADDITIVELY on top of a successful `assess_objective` run. Caller passes the
# already-produced signals (progress + probability + rationales) so this
# function does NOT re-run the assessment. One LLM call per invocation.
# Shield-routed under sub-surface `solve_v2.monitor_recommendations`.

_RECOMMENDATIONS_SURFACE = "solve_v2.monitor_recommendations"
_RECOMMENDATIONS_LAYER = "monitor.recommendations"

_RECOMMENDATIONS_SYSTEM_PROMPT = (
    "You are AKKI Monitor's interventions assistant. The objective"
    " has already been assessed (progress + probability are below)."
    " Propose 2-4 SPECIFIC, SEQUENCED recommendations the owner could"
    " execute to close the gap to target.\n\n"
    "Discipline:\n"
    " 1. Each recommendation is a verb-led, executable action — not"
    " a platitude. (\"Tighten the reactivation-email cadence to"
    " weekly\" not \"Improve marketing.\")\n"
    " 2. Cite the evidence (BASE or TRACKING doc name) the"
    " recommendation responds to in `evidence_citation`.\n"
    " 3. `sequence` is 1-based: rec 1 must land before rec 2 starts."
    " Order matters — the first rec is the load-bearing one.\n"
    " 4. `confidence_band` is one of: \"Likely-helpful\","
    " \"Possible-helpful\", \"Worth-trying\". No false-precision"
    " percentages here.\n"
    " 5. NEVER fabricate a recommendation that has no support in"
    " the supplied evidence. If the evidence is thin, RETURN AN"
    " EMPTY LIST and explain why in `_refusal_note`.\n\n"
    "Output JSON SHAPE ONLY:\n"
    "  {\n"
    "    \"recommendations\": [\n"
    "      {\n"
    "        \"sequence\": 1,\n"
    "        \"title\": \"<verb-led action>\",\n"
    "        \"rationale\": \"<one or two sentences>\",\n"
    "        \"evidence_citation\": \"<doc name or quote>\",\n"
    "        \"confidence_band\": \"Likely-helpful\"\n"
    "      }\n"
    "    ],\n"
    "    \"_refusal_note\": \"\"\n"
    "  }\n"
    "No prose around the JSON. No code fences."
)


_RECOMMENDATIONS_BLOB = re.compile(
    r"\{.*?\"recommendations\"\s*:\s*\[.*?\].*?\}",
    re.DOTALL,
)


def _build_recommendations_prompt(
    *,
    objective: Dict[str, Any],
    assessment: Dict[str, Any],
    base_docs: List[Dict[str, Any]],
    tracking_docs: List[Dict[str, Any]],
) -> str:
    base_block = "\n".join(_summarise_doc(d) for d in base_docs) or "  (none)"
    tracking_block = "\n".join(_summarise_doc(d) for d in tracking_docs) or "  (none)"
    progress_pct = assessment.get("progress_pct")
    progress_rat = assessment.get("progress_rationale") or "(no rationale)"
    prob_pct = assessment.get("probability_pct")
    prob_band = assessment.get("probability_band") or "(no band)"
    prob_rat = assessment.get("probability_rationale") or "(no rationale)"
    return (
        f"OBJECTIVE:\n"
        f"  title:        {objective.get('title', '(untitled)')}\n"
        f"  description:  {objective.get('description', '(none)')}\n"
        f"  target_metric:{objective.get('target_metric', '(not set)')}\n"
        f"  target_value: {objective.get('target_value', '(not set)')}\n"
        f"  due_date:     {objective.get('due_date', '(no deadline)')}\n\n"
        f"ASSESSMENT (already computed):\n"
        f"  progress_pct:    {progress_pct}\n"
        f"  progress_basis:  {progress_rat}\n"
        f"  probability_pct: {prob_pct} ({prob_band})\n"
        f"  probability_basis: {prob_rat}\n\n"
        f"BASE DOCS:\n{base_block}\n\n"
        f"TRACKING DOCS:\n{tracking_block}\n\n"
        f"Return the recommendations JSON now. 2-4 items, sequenced."
    )


def _parse_recommendations(raw: str) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    txt = raw.strip()
    for fence in ("```json", "```JSON", "```"):
        if txt.startswith(fence):
            txt = txt[len(fence):].lstrip("\n").strip()
        if txt.endswith("```"):
            txt = txt[:-3].rstrip()
    candidates = [txt]
    if "{" in txt:
        first = txt.find("{")
        last = txt.rfind("}")
        if first >= 0 and last > first:
            candidates.append(txt[first:last + 1])
    for c in candidates:
        try:
            obj = json.loads(c)
        except Exception:
            continue
        recs = obj.get("recommendations")
        if not isinstance(recs, list):
            continue
        cleaned: List[Dict[str, Any]] = []
        for rec in recs:
            if not isinstance(rec, dict):
                continue
            title = (rec.get("title") or "").strip()
            if not title:
                continue
            cleaned.append({
                "sequence": int(rec.get("sequence") or len(cleaned) + 1),
                "title": title[:200],
                "rationale": (rec.get("rationale") or "").strip()[:480],
                "evidence_citation": (rec.get("evidence_citation") or "").strip()[:200],
                "confidence_band": (rec.get("confidence_band") or "Worth-trying").strip(),
            })
        return {
            "recommendations": cleaned,
            "refusal_note": (obj.get("_refusal_note") or "").strip(),
        }
    return None


async def recommend_interventions(
    *,
    objective: Dict[str, Any],
    assessment: Dict[str, Any],
    base_docs: List[Dict[str, Any]],
    tracking_docs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Stage 2b.1 — propose interventions for one assessed objective.

    Caller-supplied refusal short-circuits (per canonical spec's
    "STOP and show before widening" discipline — interventions only
    make sense on top of a successful assessment):

    - If the assessment refused (no tracking evidence) → refuse with
      the upstream refusal reason. No LLM call.
    - If probability_band == "High-conviction" AND progress_pct ≥ 90
      → refuse with reason `objective_on_track_no_intervention`.
      Recommendations are for closing gaps, not celebrating wins.

    Successful path: single Shield-routed LLM call returns 2-4
    sequenced recommendations with evidence_citation. Empty-list
    return path (evidence thin) is honest refusal too — `refusal_note`
    is preserved.
    """
    if not objective.get("id"):
        raise ValueError("recommend_interventions: objective.id is required")

    now_iso = datetime.now(timezone.utc).isoformat()

    # Upstream refusal carried through (no LLM call).
    if assessment.get("refused"):
        return {
            "objective_id":     objective["id"],
            "refused":           True,
            "refusal_reason":    assessment.get("refusal_reason"),
            "recommendations":  [],
            "audit_entry_ids":  [],
            "assessed_at":       now_iso,
        }

    progress_pct = assessment.get("progress_pct") or 0
    prob_band = assessment.get("probability_band")
    if prob_band == "High-conviction" and progress_pct >= 90:
        return {
            "objective_id":     objective["id"],
            "refused":           True,
            "refusal_reason":    "objective_on_track_no_intervention",
            "recommendations":  [],
            "audit_entry_ids":  [],
            "assessed_at":       now_iso,
        }

    session = {
        "id":         str(uuid.uuid4()),
        "account_id": objective.get("account_id"),
        "context_id": objective.get("context_id"),
    }

    prompt = _build_recommendations_prompt(
        objective=objective,
        assessment=assessment,
        base_docs=base_docs,
        tracking_docs=tracking_docs,
    )
    result = await shielded_call(
        engine="monitor_recommendations",
        layer=_RECOMMENDATIONS_LAYER,
        turn_id=objective["id"],
        prompt=prompt,
        system_override=_RECOMMENDATIONS_SYSTEM_PROMPT,
        tier="standard",
        surface=_RECOMMENDATIONS_SURFACE,
        account_id=session.get("account_id"),
        session_id=session["id"],
        context_id=session.get("context_id"),
        engine_version="monitor_recommendations@1.0",
        extra_output={
            "base_doc_count": len(base_docs),
            "tracking_doc_count": len(tracking_docs),
            "assessment_progress_pct": progress_pct,
            "assessment_probability_pct": assessment.get("probability_pct"),
        },
    )

    audit = result.reasoning_audit_entry or {}
    audit_ids: List[str] = []
    if audit.get("id"):
        audit_ids.append(audit["id"])

    parsed = _parse_recommendations(result.text or "")
    if parsed is None:
        # Engine parse-failure: honest mid-band refusal — empty list +
        # explicit note, mirrors the progress extractor's auto-calibrated
        # fallback.
        return {
            "objective_id":     objective["id"],
            "refused":           True,
            "refusal_reason":    "recommendations_parse_failed",
            "recommendations":  [],
            "refusal_note":      (
                "Auto-calibrated: interventions extractor failed to "
                "return a parseable JSON over the supplied evidence."
            ),
            "audit_entry_ids":  audit_ids,
            "assessed_at":       now_iso,
        }

    recs = parsed["recommendations"]
    # Cap at 4 (per canonical spec — 2-4 specific, sequenced).
    recs = sorted(recs, key=lambda r: r["sequence"])[:4]
    return {
        "objective_id":     objective["id"],
        "refused":           False,
        "refusal_reason":    None,
        "recommendations":   recs,
        "refusal_note":      parsed.get("refusal_note") or None,
        "audit_entry_ids":   audit_ids,
        "assessed_at":       now_iso,
    }


__all__ = [
    "assess_objective",
    "recommend_interventions",
    "explain_performance",
    "extended_health",
]


# ---------------------------------------------------------------------------
# JC-MON Stage 2b.2 — AI explanation of performance widen
# ---------------------------------------------------------------------------
# Canonical spec section: `/app/memory/JC_MON_CANONICAL_SPEC.md` § Stage 2b.
# "Each its own quality bar … 2. AI explanation of performance". Reads the
# assessment + evidence and narrates WHY the objective is tracking the way
# it is. ADDITIVELY composes with 2a + 2b.1; does not re-run them. One
# Shield-routed LLM call per invocation.

_EXPLANATION_SURFACE = "solve_v2.monitor_explanation"
_EXPLANATION_LAYER = "monitor.explanation"

_EXPLANATION_SYSTEM_PROMPT = (
    "You are AKKI Monitor's performance-explanation assistant. The "
    "objective has already been assessed; your job is to NARRATE the "
    "reasons behind the read, not propose actions.\n\n"
    "Discipline:\n"
    " 1. Causes must be evidence-grounded — every cause cites a doc "
    "name (BASE or TRACKING). No speculation beyond the evidence.\n"
    " 2. NEVER prescribe actions here (that is 2b.1's job). Stay "
    "narrative.\n"
    " 3. Headline is ONE sentence (≤ 220 chars) that an owner could "
    "read first and trust to be true given the evidence.\n"
    " 4. Causes are 2-4 items, each a single observation with its "
    "supporting doc cited.\n"
    " 5. If evidence is thin, return causes=[] and explain in "
    "`_refusal_note` why a narrative cannot be supported.\n\n"
    "Output JSON SHAPE ONLY:\n"
    "  {\n"
    "    \"headline\": \"<one-sentence overall read>\",\n"
    "    \"causes\": [\n"
    "      {\n"
    "        \"observation\": \"<one-sentence cause statement>\",\n"
    "        \"evidence_citation\": \"<doc name or quote>\"\n"
    "      }\n"
    "    ],\n"
    "    \"summary_prose\": \"<2-3 sentence narrative>\",\n"
    "    \"_refusal_note\": \"\"\n"
    "  }\n"
    "No prose around the JSON. No code fences."
)


_EXPLANATION_BLOB = re.compile(
    r"\{.*?\"headline\"\s*:\s*\"[^\"]*\".*?\"causes\"\s*:\s*\[.*?\].*?\}",
    re.DOTALL,
)


def _build_explanation_prompt(
    *,
    objective: Dict[str, Any],
    assessment: Dict[str, Any],
    base_docs: List[Dict[str, Any]],
    tracking_docs: List[Dict[str, Any]],
) -> str:
    base_block = "\n".join(_summarise_doc(d) for d in base_docs) or "  (none)"
    tracking_block = "\n".join(_summarise_doc(d) for d in tracking_docs) or "  (none)"
    progress_pct = assessment.get("progress_pct")
    progress_rat = assessment.get("progress_rationale") or "(no rationale)"
    prob_pct = assessment.get("probability_pct")
    prob_band = assessment.get("probability_band") or "(no band)"
    prob_rat = assessment.get("probability_rationale") or "(no rationale)"
    return (
        f"OBJECTIVE:\n"
        f"  title:        {objective.get('title', '(untitled)')}\n"
        f"  description:  {objective.get('description', '(none)')}\n"
        f"  target_value: {objective.get('target_value', '(not set)')}\n"
        f"  due_date:     {objective.get('due_date', '(no deadline)')}\n\n"
        f"ASSESSMENT (already computed):\n"
        f"  progress_pct:    {progress_pct}\n"
        f"  progress_basis:  {progress_rat}\n"
        f"  probability_pct: {prob_pct} ({prob_band})\n"
        f"  probability_basis: {prob_rat}\n\n"
        f"BASE DOCS:\n{base_block}\n\n"
        f"TRACKING DOCS:\n{tracking_block}\n\n"
        f"Return the explanation JSON now. 2-4 causes, each cited."
    )


def _parse_explanation(raw: str) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    candidates = [raw.strip()]
    m = _EXPLANATION_BLOB.search(raw)
    if m:
        candidates.append(m.group(0))
    for c in candidates:
        try:
            obj = json.loads(c)
        except Exception:
            continue
        headline = (obj.get("headline") or "").strip()
        causes = obj.get("causes")
        summary = (obj.get("summary_prose") or "").strip()
        if not headline:
            continue
        if not isinstance(causes, list):
            continue
        cleaned_causes: List[Dict[str, Any]] = []
        for cause in causes:
            if not isinstance(cause, dict):
                continue
            obs = (cause.get("observation") or "").strip()
            cite = (cause.get("evidence_citation") or "").strip()
            if not obs:
                continue
            cleaned_causes.append({
                "observation": obs[:300],
                "evidence_citation": cite[:200],
            })
        return {
            "headline": headline[:240],
            "causes": cleaned_causes[:4],
            "summary_prose": summary[:600],
            "refusal_note": (obj.get("_refusal_note") or "").strip(),
        }
    return None


async def explain_performance(
    *,
    objective: Dict[str, Any],
    assessment: Dict[str, Any],
    base_docs: List[Dict[str, Any]],
    tracking_docs: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Stage 2b.2 — narrate why the objective is tracking this way.

    Caller-supplied refusal short-circuits (per canonical spec):
      - Upstream assessment refused → carry through. No LLM call.

    Successful path: Shield-routed LLM call producing headline +
    2-4 evidence-cited causes + 2-3 sentence narrative.
    """
    if not objective.get("id"):
        raise ValueError("explain_performance: objective.id is required")

    now_iso = datetime.now(timezone.utc).isoformat()

    if assessment.get("refused"):
        return {
            "objective_id":    objective["id"],
            "refused":          True,
            "refusal_reason":   assessment.get("refusal_reason"),
            "headline":         None,
            "causes":           [],
            "summary_prose":    None,
            "audit_entry_ids": [],
            "assessed_at":      now_iso,
        }

    session = {
        "id":         str(uuid.uuid4()),
        "account_id": objective.get("account_id"),
        "context_id": objective.get("context_id"),
    }

    prompt = _build_explanation_prompt(
        objective=objective,
        assessment=assessment,
        base_docs=base_docs,
        tracking_docs=tracking_docs,
    )
    result = await shielded_call(
        engine="monitor_explanation",
        layer=_EXPLANATION_LAYER,
        turn_id=objective["id"],
        prompt=prompt,
        system_override=_EXPLANATION_SYSTEM_PROMPT,
        tier="standard",
        surface=_EXPLANATION_SURFACE,
        account_id=session.get("account_id"),
        session_id=session["id"],
        context_id=session.get("context_id"),
        engine_version="monitor_explanation@1.0",
    )

    audit = result.reasoning_audit_entry or {}
    audit_ids: List[str] = []
    if audit.get("id"):
        audit_ids.append(audit["id"])

    parsed = _parse_explanation(result.text or "")
    if parsed is None:
        return {
            "objective_id":    objective["id"],
            "refused":          True,
            "refusal_reason":   "explanation_parse_failed",
            "headline":         None,
            "causes":           [],
            "summary_prose":    None,
            "refusal_note": (
                "Auto-calibrated: explanation extractor failed to "
                "return a parseable JSON over the supplied evidence."
            ),
            "audit_entry_ids": audit_ids,
            "assessed_at":      now_iso,
        }

    return {
        "objective_id":    objective["id"],
        "refused":          False,
        "refusal_reason":   None,
        "headline":         parsed["headline"],
        "causes":           parsed["causes"],
        "summary_prose":    parsed["summary_prose"],
        "refusal_note":     parsed.get("refusal_note") or None,
        "audit_entry_ids": audit_ids,
        "assessed_at":      now_iso,
    }


# ---------------------------------------------------------------------------
# JC-MON Stage 2b.3 — Extended health / status widen (beyond RAG)
# ---------------------------------------------------------------------------
# Canonical spec section: `/app/memory/JC_MON_CANONICAL_SPEC.md` § Stage 2b.
# "3. Extended health/status (beyond the current RAG)." Beyond the canonical
# red/amber/green color: plan compliance + risk surface + confidence trend.
# Deterministic where possible (no LLM where math suffices); Shield-routed
# only for the risk_surface narrative.

_RAG_THRESHOLDS = (
    # (band, min_probability_pct)
    ("green",  70),
    ("amber",  40),
    ("red",     0),
)


def _derive_rag(probability_pct: Optional[int]) -> str:
    if probability_pct is None:
        return "unassessed"
    for band, threshold in _RAG_THRESHOLDS:
        if probability_pct >= threshold:
            return band
    return "red"


def _derive_plan_compliance(
    progress_pct: Optional[int],
    probability_pct: Optional[int],
) -> Dict[str, Any]:
    """Deterministic — compare progress to an implicit linear-plan
    expectation (50% mid-period default) and use probability to weight
    the verdict."""
    if progress_pct is None:
        return {"status": "unassessed", "rationale": "No progress signal."}
    if progress_pct >= 85 and (probability_pct or 0) >= 60:
        return {
            "status": "ahead-of-plan",
            "rationale": (
                f"Progress {progress_pct}% with probability "
                f"{probability_pct}% — ahead of a 50%-mid-period linear "
                f"baseline and high-conviction trajectory."
            ),
        }
    if progress_pct >= 50:
        return {
            "status": "on-plan",
            "rationale": (
                f"Progress {progress_pct}% — at or above linear "
                f"baseline. Probability {probability_pct}% supports the "
                f"trajectory."
            ),
        }
    return {
        "status": "behind-plan",
        "rationale": (
            f"Progress {progress_pct}% — below linear baseline. "
            f"Probability {probability_pct}% reflects the gap."
        ),
    }


def _derive_confidence_trend(
    current_probability_pct: Optional[int],
    prior_probability_pct: Optional[int],
) -> Dict[str, Any]:
    """Deterministic. Five states based on delta vs prior assessment:
       first_assessment_baseline / improving / stable / degrading.
       Threshold for change: ±8 percentage points (above sampling noise)."""
    if current_probability_pct is None:
        return {"status": "unassessed", "delta_pp": None}
    if prior_probability_pct is None:
        return {
            "status": "first_assessment_baseline",
            "delta_pp": None,
            "rationale": "No prior assessment on record; this is the baseline.",
        }
    delta = current_probability_pct - prior_probability_pct
    if delta >= 8:
        status = "improving"
    elif delta <= -8:
        status = "degrading"
    else:
        status = "stable"
    return {
        "status": status,
        "delta_pp": delta,
        "rationale": (
            f"Δ {delta:+d}pp vs prior assessment "
            f"(current {current_probability_pct}% / prior "
            f"{prior_probability_pct}%)."
        ),
    }


_RISK_SURFACE_SURFACE = "solve_v2.monitor_risk_surface"
_RISK_SURFACE_LAYER = "monitor.risk_surface"

_RISK_SURFACE_SYSTEM_PROMPT = (
    "You are AKKI Monitor's risk-surface assistant. Read the objective + "
    "assessment + evidence and surface 1-3 NAMED RISKS that could shift "
    "the read negatively in the next period.\n\n"
    "Discipline:\n"
    " 1. Each risk is a SHORT NAME (3-6 words) + a 1-sentence "
    "narrative + an evidence citation.\n"
    " 2. NEVER invent a risk with no support in the evidence. If "
    "evidence is thin, return risks=[] with a `_refusal_note`.\n"
    " 3. Order by `severity` descending (high → low).\n\n"
    "Output JSON SHAPE ONLY:\n"
    "  {\n"
    "    \"risks\": [\n"
    "      {\n"
    "        \"name\": \"<3-6 words>\",\n"
    "        \"narrative\": \"<one sentence>\",\n"
    "        \"evidence_citation\": \"<doc name or quote>\",\n"
    "        \"severity\": \"high\"|\"medium\"|\"low\"\n"
    "      }\n"
    "    ],\n"
    "    \"_refusal_note\": \"\"\n"
    "  }\n"
    "No prose around the JSON. No code fences."
)


_RISK_SURFACE_BLOB = re.compile(
    r"\{.*?\"risks\"\s*:\s*\[.*?\].*?\}",
    re.DOTALL,
)


def _build_risk_surface_prompt(
    *,
    objective: Dict[str, Any],
    assessment: Dict[str, Any],
    base_docs: List[Dict[str, Any]],
    tracking_docs: List[Dict[str, Any]],
) -> str:
    base_block = "\n".join(_summarise_doc(d) for d in base_docs) or "  (none)"
    tracking_block = "\n".join(_summarise_doc(d) for d in tracking_docs) or "  (none)"
    return (
        f"OBJECTIVE: {objective.get('title', '(untitled)')}\n"
        f"  target_value: {objective.get('target_value', '(not set)')}\n"
        f"  due_date:     {objective.get('due_date', '(no deadline)')}\n\n"
        f"ASSESSMENT:\n"
        f"  progress_pct:    {assessment.get('progress_pct')}\n"
        f"  probability_pct: {assessment.get('probability_pct')} ({assessment.get('probability_band')})\n\n"
        f"BASE DOCS:\n{base_block}\n\n"
        f"TRACKING DOCS:\n{tracking_block}\n\n"
        f"Surface 1-3 risks now."
    )


def _parse_risk_surface(raw: str) -> Optional[Dict[str, Any]]:
    if not raw:
        return None
    txt = raw.strip()
    for fence in ("```json", "```JSON", "```"):
        if txt.startswith(fence):
            txt = txt[len(fence):].lstrip("\n").strip()
        if txt.endswith("```"):
            txt = txt[:-3].rstrip()
    candidates = [txt]
    if "{" in txt:
        first = txt.find("{")
        last = txt.rfind("}")
        if first >= 0 and last > first:
            candidates.append(txt[first:last + 1])
    for c in candidates:
        try:
            obj = json.loads(c)
        except Exception:
            continue
        risks = obj.get("risks")
        if not isinstance(risks, list):
            continue
        cleaned: List[Dict[str, Any]] = []
        for risk in risks:
            if not isinstance(risk, dict):
                continue
            name = (risk.get("name") or "").strip()
            narr = (risk.get("narrative") or "").strip()
            if not name or not narr:
                continue
            sev = (risk.get("severity") or "medium").lower()
            if sev not in ("high", "medium", "low"):
                sev = "medium"
            cleaned.append({
                "name": name[:80],
                "narrative": narr[:280],
                "evidence_citation": (risk.get("evidence_citation") or "").strip()[:200],
                "severity": sev,
            })
        sev_rank = {"high": 0, "medium": 1, "low": 2}
        cleaned.sort(key=lambda r: sev_rank.get(r["severity"], 1))
        return {
            "risks": cleaned[:3],
            "refusal_note": (obj.get("_refusal_note") or "").strip(),
        }
    return None


async def extended_health(
    *,
    objective: Dict[str, Any],
    assessment: Dict[str, Any],
    base_docs: List[Dict[str, Any]],
    tracking_docs: List[Dict[str, Any]],
    prior_assessment: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Stage 2b.3 — extended health/status beyond the canonical R/A/G.

    Three signals composed:
      • `rag_status`: deterministic from probability_pct.
      • `plan_compliance`: deterministic from progress + probability.
      • `confidence_trend`: deterministic from current vs prior
        probability (or `first_assessment_baseline` if no prior).
      • `risk_surface`: Shield-routed narrative — 1-3 named risks.

    Caller-supplied refusal short-circuit: upstream-refused assessment
    carries through; deterministic signals still emit `unassessed`
    where applicable; risk_surface skipped (no LLM call).
    """
    if not objective.get("id"):
        raise ValueError("extended_health: objective.id is required")

    now_iso = datetime.now(timezone.utc).isoformat()
    rag_status = _derive_rag(assessment.get("probability_pct"))
    plan_compliance = _derive_plan_compliance(
        assessment.get("progress_pct"),
        assessment.get("probability_pct"),
    )
    confidence_trend = _derive_confidence_trend(
        assessment.get("probability_pct"),
        (prior_assessment or {}).get("probability_pct"),
    )

    # If upstream refused, deterministic signals still emit honestly
    # (`unassessed`/baseline) — but no LLM call for risk_surface.
    if assessment.get("refused"):
        return {
            "objective_id":      objective["id"],
            "refused":           True,
            "refusal_reason":    assessment.get("refusal_reason"),
            "rag_status":        rag_status,
            "plan_compliance":   plan_compliance,
            "confidence_trend":  confidence_trend,
            "risk_surface":      {"risks": [], "refusal_note": "upstream-refused; risk surface not computed."},
            "audit_entry_ids":   [],
            "assessed_at":       now_iso,
        }

    session = {
        "id":         str(uuid.uuid4()),
        "account_id": objective.get("account_id"),
        "context_id": objective.get("context_id"),
    }

    prompt = _build_risk_surface_prompt(
        objective=objective,
        assessment=assessment,
        base_docs=base_docs,
        tracking_docs=tracking_docs,
    )
    result = await shielded_call(
        engine="monitor_risk_surface",
        layer=_RISK_SURFACE_LAYER,
        turn_id=objective["id"],
        prompt=prompt,
        system_override=_RISK_SURFACE_SYSTEM_PROMPT,
        tier="standard",
        surface=_RISK_SURFACE_SURFACE,
        account_id=session.get("account_id"),
        session_id=session["id"],
        context_id=session.get("context_id"),
        engine_version="monitor_risk_surface@1.0",
    )
    audit = result.reasoning_audit_entry or {}
    audit_ids: List[str] = []
    if audit.get("id"):
        audit_ids.append(audit["id"])
    parsed = _parse_risk_surface(result.text or "")
    risk_surface = parsed or {"risks": [], "refusal_note": "risk_surface_parse_failed"}
    return {
        "objective_id":      objective["id"],
        "refused":           False,
        "refusal_reason":    None,
        "rag_status":        rag_status,
        "plan_compliance":   plan_compliance,
        "confidence_trend":  confidence_trend,
        "risk_surface":      risk_surface,
        "audit_entry_ids":   audit_ids,
        "assessed_at":       now_iso,
    }
