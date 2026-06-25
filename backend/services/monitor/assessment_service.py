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


__all__ = ["assess_objective"]
