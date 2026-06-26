"""JC-MON Stage 3.0 — Candidate-objectives generator (REASSESS action).

Source of truth: `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 3 ·
"OBJECTIVES: generate from a strategy doc as a CANDIDATE LIST the user
reviews/edits/confirms").

User resolution (2026-06-25):
> 3.0 Reassess: LLM **generates candidate objectives** from baseline
> doc; user edits/removes/confirms BEFORE creation. No objective
> exists until confirmed. Generation call, not classifier.

This service produces a CANDIDATE LIST only — it does NOT persist
anything. The Monitor surface renders the list, the user edits /
removes / confirms each candidate, and confirmed candidates are
persisted via the existing `POST /api/contexts/{cid}/monitor/objective`
endpoint. The architectural guarantee: **no objective exists until the
user confirms it**.

Behavioural contract:
  • Single Shield-routed LLM call per invocation
    (`solve_v2.monitor_candidate_objectives`).
  • Reads BASE doc content (the strategy / performance agreement) +
    optional supplementary baseline docs; returns 2-6 candidates each
    carrying `title`, `description`, `target_metric`, `target_value`,
    `due_date`, `rationale`, `evidence_citation`, `confidence_band`.
  • Honest refusal short-circuits:
      - empty `base_docs` → refuse with reason `no_baseline_evidence`
      - parse failure on LLM output → refuse with reason
        `candidate_parse_failed` + audit trail preserved
  • Every successful candidate cites the BASE doc by name in
    `evidence_citation`. If the LLM cannot ground a candidate in the
    supplied evidence, the LLM is instructed to RETURN AN EMPTY LIST
    (per the canonical spec's REFUSE-when-thin rule).

The shape mirrors Stage 2b.1's recommendations service so the FE
reviewer can render it with the same idioms.
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.solva_v2.engines.llm_adapter_proxy import shielded_call


logger = logging.getLogger("akki.monitor.candidate_objectives")


_CANDIDATES_SURFACE = "solve_v2.monitor_candidate_objectives"
_CANDIDATES_LAYER = "monitor.candidate_objectives"


_CANDIDATES_SYSTEM_PROMPT = (
    "You are AKKI Monitor's candidate-objective generator. Read the"
    " BASE doc evidence (a strategic plan, performance agreement, or"
    " equivalent baseline) and propose 2-6 candidate strategic"
    " OBJECTIVES the user could track against this baseline.\n\n"
    "Discipline:\n"
    " 1. Each objective is a GROUNDED, SPECIFIC, MEASURABLE goal —"
    " not a slogan. (\"Recover monthly active revenue index to ≥ 100\""
    " not \"Improve revenue.\")\n"
    " 2. Each objective MUST cite the BASE doc by name in"
    " `evidence_citation` — verbatim quote or doc reference.\n"
    " 3. NEVER fabricate an objective that has no support in the"
    " supplied evidence. If the BASE docs are thin or ambiguous,"
    " RETURN AN EMPTY LIST and explain why in `_refusal_note`.\n"
    " 4. `target_value` is concrete (\"Index ≥ 100 within 180 days\","
    " \"Reduce DSO from 65 to ≤ 50 days by Q4\") — not aspirational.\n"
    " 5. `due_date` is YYYY-MM-DD if the BASE doc names a horizon;"
    " otherwise leave empty (the user will choose).\n"
    " 6. `confidence_band` ∈ {\"Strongly-grounded\","
    " \"Reasonably-grounded\", \"Speculative\"} — graded by how"
    " directly the BASE doc supports the candidate.\n"
    " 7. The user will review/edit/confirm each candidate BEFORE"
    " anything is persisted. Your output is a SUGGESTION SET, not"
    " a commitment.\n\n"
    "Output JSON SHAPE ONLY:\n"
    "  {\n"
    "    \"candidates\": [\n"
    "      {\n"
    "        \"title\": \"<noun-phrase goal name, ≤ 200 chars>\",\n"
    "        \"description\": \"<one-paragraph context, ≤ 480 chars>\",\n"
    "        \"target_metric\": \"<metric name, e.g. 'monthly_active_revenue_index'>\",\n"
    "        \"target_value\": \"<concrete target with horizon>\",\n"
    "        \"due_date\": \"YYYY-MM-DD\" | \"\",\n"
    "        \"rationale\": \"<one sentence why this comes from the BASE doc>\",\n"
    "        \"evidence_citation\": \"<doc name or quote from BASE>\",\n"
    "        \"confidence_band\": \"Strongly-grounded\"\n"
    "      }\n"
    "    ],\n"
    "    \"_refusal_note\": \"\"\n"
    "  }\n"
    "No prose around the JSON. No code fences."
)


def _summarise_doc(doc: Dict[str, Any], char_cap: int = 1200) -> str:
    """Compact one-line summary for prompt assembly — mirrors the
    Stage 2a/2b helper but with a larger cap because the BASE doc IS
    the load-bearing input here (vs. tracking evidence in 2a/2b)."""
    name = (doc.get("name") or doc.get("title") or "(untitled)").strip()
    text = (doc.get("extracted_text") or doc.get("summary") or doc.get("description") or "")
    text = (text or "").strip()
    if len(text) > char_cap:
        text = text[:char_cap].rstrip() + " …"
    return f"- {name}: {text}" if text else f"- {name}"


def _build_candidates_prompt(
    *,
    base_docs: List[Dict[str, Any]],
    context_label: Optional[str] = None,
    divergent_blind_spots: Optional[List[str]] = None,
) -> str:
    """Assemble the prompt for the candidate-objectives generator.

    JC-TL AUTO-TUNE (2026-06-26) — added the `divergent_blind_spots`
    keyword argument so persona-spread blind-spots from a
    Get-Perspectives session can fold in as fresh signal alongside
    the BASE docs. When supplied, each blind-spot becomes a
    "consider also" line in the prompt; when omitted (the default),
    behaviour is byte-identical to the pre-auto-tune prompt body.

    Path-discipline: blind-spots are EVIDENCE, not COMMANDS. The
    extractor still grounds candidates in BASE docs first; the
    blind-spots only widen the lens.
    """
    base_block = "\n".join(_summarise_doc(d) for d in base_docs) or "  (none)"
    ctx = (context_label or "(unnamed context)").strip()
    base_prompt = (
        f"CONTEXT: {ctx}\n\n"
        f"BASE DOCS (baseline / strategic plan / performance agreement):\n"
        f"{base_block}\n\n"
    )
    if divergent_blind_spots:
        # Deterministic ordering — sorted set; preserves prompt
        # byte-identity for repeated runs with same inputs.
        bs_items = sorted({(s or "").strip() for s in divergent_blind_spots if (s or "").strip()})
        if bs_items:
            bs_block = "\n".join(f"  - {s}" for s in bs_items)
            base_prompt += (
                "BLIND-SPOTS SURFACED BY A RECENT GET-PERSPECTIVES SESSION\n"
                "(treat as widening signal; do NOT generate objectives\n"
                "that are ONLY anchored on blind-spots — every objective\n"
                "still grounds in a BASE doc):\n"
                f"{bs_block}\n\n"
            )
    return (
        base_prompt
        + "Generate 2-6 candidate objectives grounded in these BASE"
          " docs. Return the candidates JSON now."
    )


def _parse_candidates(raw: str) -> Optional[Dict[str, Any]]:
    """Defensive parser — fence-strip + brace-balance + per-candidate
    validation. Mirrors the 2b.1 / 2b.2 hardened parser pattern."""
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
    valid_bands = {"Strongly-grounded", "Reasonably-grounded", "Speculative"}
    for c in candidates:
        try:
            obj = json.loads(c)
        except Exception:
            continue
        items = obj.get("candidates")
        if not isinstance(items, list):
            continue
        cleaned: List[Dict[str, Any]] = []
        for cand in items:
            if not isinstance(cand, dict):
                continue
            title = (cand.get("title") or "").strip()
            if not title:
                continue
            band = (cand.get("confidence_band") or "Reasonably-grounded").strip()
            if band not in valid_bands:
                band = "Reasonably-grounded"
            due = (cand.get("due_date") or "").strip()
            # Reject malformed due_date — leave empty so the user picks.
            if due and not re.match(r"^\d{4}-\d{2}-\d{2}$", due):
                due = ""
            cleaned.append({
                "title":             title[:200],
                "description":       (cand.get("description") or "").strip()[:480],
                "target_metric":     (cand.get("target_metric") or "").strip()[:120],
                "target_value":      (cand.get("target_value") or "").strip()[:200],
                "due_date":          due,
                "rationale":         (cand.get("rationale") or "").strip()[:280],
                "evidence_citation": (cand.get("evidence_citation") or "").strip()[:200],
                "confidence_band":   band,
            })
        # Cap at 6 (per spec — 2-6 candidates).
        return {
            "candidates": cleaned[:6],
            "refusal_note": (obj.get("_refusal_note") or "").strip(),
        }
    return None


async def generate_candidate_objectives(
    *,
    base_docs: List[Dict[str, Any]],
    account_id: Optional[str] = None,
    context_id: Optional[str] = None,
    context_label: Optional[str] = None,
    divergent_blind_spots: Optional[List[str]] = None,
) -> Dict[str, Any]:
    """Public entry — generate candidates from BASE doc evidence.

    JC-TL AUTO-TUNE (2026-06-26) — accepts an optional
    `divergent_blind_spots` list of blind-spot descriptions
    surfaced by a Get-Perspectives session. When supplied, the
    extractor folds them into the prompt as widening signal
    alongside the BASE docs (NOT as a replacement for grounding).
    When omitted, behaviour is byte-identical to the pre-auto-tune
    path (proven by JC-MON Stage 3.0 close evidence).

    Shape returned (intentionally parallel to Stage 2b.1):
        {
          "refused":             bool,
          "refusal_reason":      Optional[str],
          "candidates":          List[Dict] (empty on refusal),
          "refusal_note":        Optional[str],
          "audit_entry_ids":     List[str],
          "generated_at":        ISO,
        }

    Refusal short-circuits:
      - empty `base_docs` → no LLM call, reason `no_baseline_evidence`.
      - LLM parse failure → audit trail preserved, reason
        `candidate_parse_failed`.

    The caller (FE) renders the list, the user edits / removes /
    confirms each candidate, and **only confirmed candidates** are
    persisted via the existing `POST /monitor/objective` endpoint.
    """
    now_iso = datetime.now(timezone.utc).isoformat()

    if not base_docs:
        return {
            "refused":         True,
            "refusal_reason":  "no_baseline_evidence",
            "candidates":      [],
            "refusal_note":    (
                "No BASE doc evidence supplied. Upload a strategic plan"
                " or performance agreement and mark it as the BASE doc"
                " on this Monitor surface, then re-generate."
            ),
            "audit_entry_ids": [],
            "generated_at":    now_iso,
        }

    session = {
        "id":         str(uuid.uuid4()),
        "account_id": account_id,
        "context_id": context_id,
    }
    prompt = _build_candidates_prompt(
        base_docs=base_docs,
        context_label=context_label,
        divergent_blind_spots=divergent_blind_spots,
    )
    result = await shielded_call(
        engine="monitor_candidate_objectives",
        layer=_CANDIDATES_LAYER,
        turn_id=session["id"],
        prompt=prompt,
        system_override=_CANDIDATES_SYSTEM_PROMPT,
        tier="standard",
        surface=_CANDIDATES_SURFACE,
        account_id=account_id,
        session_id=session["id"],
        context_id=context_id,
        engine_version="monitor_candidate_objectives@1.0",
        extra_output={
            "base_doc_count":            len(base_docs),
            "divergent_blind_spot_count": len(divergent_blind_spots or []),
        },
    )
    audit = result.reasoning_audit_entry or {}
    audit_ids: List[str] = []
    if audit.get("id"):
        audit_ids.append(audit["id"])

    parsed = _parse_candidates(result.text or "")
    if parsed is None:
        return {
            "refused":          True,
            "refusal_reason":   "candidate_parse_failed",
            "candidates":       [],
            "refusal_note":     (
                "Auto-calibrated: candidate-objective extractor"
                " failed to return a parseable JSON over the supplied"
                " evidence."
            ),
            "audit_entry_ids":  audit_ids,
            "generated_at":     now_iso,
        }

    return {
        "refused":         False,
        "refusal_reason":  None,
        "candidates":      parsed["candidates"],
        "refusal_note":    parsed.get("refusal_note") or None,
        "audit_entry_ids": audit_ids,
        "generated_at":    now_iso,
    }


__all__ = ["generate_candidate_objectives"]
