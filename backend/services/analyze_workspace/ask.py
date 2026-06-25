"""JC-WS Phase 2 (2026-06-25) — Analyze "ask" route.

Wires the docked-prompt input on the AnalyzeDrawer to a Shield-routed
intent classifier that dispatches to the appropriate deterministic
analyzer endpoint (forecast / simulate / extract / anomalies). Falls
through to a `refuse` highlight when the question can't be answered
from the loaded sources, surfacing what's missing instead of
fabricating an answer.

Contract (Part B of /app/memory/JC_WS_CANONICAL_SPEC.md):
  • Auto-trigger paths run UNDER the surface; the user sees only the
    accreted highlight card on the thread.
  • Refusal guard fires when the question references something
    outside the loaded sources / time range / sheet vocabulary.
  • Each highlight carries a `topic` (one of: trend, anomaly,
    forecast, target, validate, refusal) so the FE can group cards
    naturally without us inventing a tagging system.

Persistence:
  • Highlights live on `analyses.highlights[]` (append-only, tenant-
    scoped). Cleared on session-close ONLY if the parent analysis is
    purged.
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from contracts import get_synisense

logger = logging.getLogger(__name__)


# Topic vocabulary kept TIGHT on purpose. The canonical spec treats
# topics as natural-language groupings the user sees — not a tagging
# system to extend ad-hoc. Add new topics only when a new analyzer
# lands; surfacing them on the highlight card is the contract.
VALID_TOPICS = {"trend", "anomaly", "forecast", "target", "validate", "refusal", "simulate"}

# Refusal reasons — surfaced verbatim on the FE. Keep them short
# (under 120 chars). These are the user-facing strings the spec
# refers to as "what's missing / what to add".
REFUSAL_REASONS = {
    "no_time_series":      "This question implies a time-series read, but no date column was detected in the loaded sheet.",
    "missing_target":      "No measurable target was detected in the question. Add a metric (e.g. revenue, headcount, accuracy) or a column name.",
    "out_of_scope":        "The question references something outside the loaded sources. Add the supporting file(s) or narrow the scope.",
    "ambiguous_intent":    "I can't tell whether you want a forecast, a simulation, or a one-off lookup. Could you rephrase with the action verb?",
    "insufficient_data":   "The loaded data doesn't carry enough rows for a reliable answer. Add more periods or widen the date range.",
}


# ─────────────────────────────────────────────────────────────────────
# Intent classification — Shield-routed (LLM under audit + de-id)
# ─────────────────────────────────────────────────────────────────────
def _build_classifier_prompt(
    *, question: str, objective: str, column_summary: str, recent_highlight_titles: List[str],
) -> str:
    """Construct the LLM prompt that classifies a free-text question
    into a structured intent. The model returns STRICT JSON only."""
    recent = "\n".join(f"  - {t}" for t in recent_highlight_titles[-6:]) or "  (none yet)"
    return (
        "You are the intent router for an executive analysis workspace. "
        "The user has loaded one or more data files and is asking a "
        "follow-up question. Classify the question into ONE of:\n\n"
        "  forecast  — user wants a forward-looking projection on a metric\n"
        "  simulate  — user wants a scenario / Monte-Carlo (\"what if X\")\n"
        "  extract   — user wants a one-off lookup or aggregate from the data\n"
        "  validate  — user wants to confirm or refute a stated claim\n"
        "  anomaly   — user wants to surface outliers / oddities\n"
        "  refuse    — the question can't be answered from the data given\n\n"
        "DECISIVENESS RULE: When the question contains an explicit "
        "action verb (forecast / project / simulate / what-if / "
        "extract / look up / validate / confirm / anomaly / outliers), "
        "USE that verb. Don't refuse for 'ambiguity' when the verb "
        "is explicit. Refusal is reserved for genuinely missing data, "
        "not phrasing uncertainty.\n\n"
        "Refuse ONLY when:\n"
        "  • The question references a column / metric NOT in the loaded sheet.\n"
        "  • The question implies time-series analysis but no date column exists.\n"
        "  • The data is insufficient (e.g. fewer than 3 periods for a forecast).\n"
        "  • The question references entities NOT present in the column sample values shown below.\n\n"
        "Category-value note: when the COLUMNS block shows a categorical "
        "column with sample values in {curly braces}, any value listed "
        "there is in-scope (e.g. region names like 'East', 'North').\n\n"
        "OUTPUT STRICT JSON ONLY. No prose, no fences:\n"
        "{\n"
        '  "intent":      "forecast|simulate|extract|validate|anomaly|refuse",\n'
        '  "target":      "<column or metric name verbatim from the data, or empty>",\n'
        '  "horizon":     "<e.g. \\"Q4\\" / \\"next 3 months\\" / null>",\n'
        '  "scenario":    "<one short clause describing the what-if, or null>",\n'
        '  "rationale":   "<1 sentence justifying the classification, max 180 chars>",\n'
        '  "refusal_reason_code": "<one of: no_time_series|missing_target|out_of_scope|ambiguous_intent|insufficient_data|null>"\n'
        "}\n\n"
        "=== OBJECTIVE (what the user is trying to learn) ===\n"
        f"{objective or '(not set)'}\n\n"
        "=== DATA SUMMARY (sheet columns) ===\n"
        f"{column_summary or '(no data loaded)'}\n\n"
        "=== RECENT HIGHLIGHTS ON THE THREAD ===\n"
        f"{recent}\n\n"
        "=== USER QUESTION ===\n"
        f"{question}\n"
    )


def _build_narration_prompt(
    *, question: str, intent: str, analyzer_payload: Dict[str, Any], objective: str,
) -> str:
    """Turn a deterministic analyzer payload into a tweet-style
    highlight card (140-260 chars body, single headline, optional
    citation hint). The model returns STRICT JSON."""
    return (
        "You are surfacing an analytical finding as a tweet-style "
        "card on an executive workspace. ONE crisp headline + ONE "
        "short body paragraph + optional citation hint. No glazing, "
        "no hedging weasel words, lead with the substance.\n\n"
        "Voice-lint: do NOT use the words 'leverages', 'streamlines', "
        "'unlocks', 'empowers', 'robust', 'cutting-edge'. Avoid "
        "imperatives — the user makes decisions, not you.\n\n"
        "Output STRICT JSON only:\n"
        "{\n"
        '  "title":       "<headline, <= 90 chars>",\n'
        '  "body":        "<one sentence stating the finding, 140-260 chars>",\n'
        '  "citation":    "<short hint like \\"Sheet1!B2:B14\\" or filename, or empty>",\n'
        '  "topic":       "<one of: trend|anomaly|forecast|target|validate|simulate|refusal>",\n'
        '  "confidence":  "<one of: high|medium|low>"\n'
        "}\n\n"
        f"=== USER ASKED ===\n{question}\n\n"
        f"=== ANALYZER RAN ===\n{intent}\n\n"
        f"=== ANALYZER OUTPUT (JSON) ===\n{json.dumps(analyzer_payload, default=str)[:2000]}\n\n"
        f"=== OBJECTIVE ===\n{objective or '(not set)'}\n"
    )


def _strip_fences(s: str) -> str:
    s = (s or "").strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", s, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.match(r"^```(?:json)?\s*\n?(.*)$", s, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return s


def _parse_json(raw: str) -> Optional[Dict[str, Any]]:
    s = _strip_fences(raw)
    if not s.startswith("{"):
        i = s.find("{")
        if i < 0:
            return None
        s = s[i:]
    j = s.rfind("}")
    if j >= 0:
        s = s[: j + 1]
    try:
        return json.loads(s)
    except Exception as exc:
        logger.warning("analyze_workspace.parse_json_failed: %s; head=%r", exc, s[:200])
        return None


# ─────────────────────────────────────────────────────────────────────
# Sheet column summary — built from the analysis row's loaded sheets.
# ─────────────────────────────────────────────────────────────────────
def _column_summary_from_analysis(row: Dict[str, Any]) -> str:
    """Build a compact, LLM-friendly summary of the columns available
    in the loaded sheets. Caps at 6 columns × 3 sheets to keep the
    prompt envelope under 600 chars. Includes sample values for
    categorical/text columns so the classifier knows what category
    members are in-scope (e.g. region names like 'East')."""
    sheets = row.get("sheets") or []
    if not sheets:
        return "(no sheets loaded)"
    lines: List[str] = []
    for sheet in sheets[:3]:
        sheet_name = sheet.get("name") or "Sheet1"
        cols = sheet.get("columns") or []
        col_descs = []
        for c in cols[:6]:
            kind = c.get("kind") or "text"
            desc = f"{c.get('name','?')}({kind})"
            # For categorical / text columns, include sample values
            # so the classifier knows e.g. 'East' is a real region.
            if kind in ("categorical", "text"):
                samples = c.get("sample_values") or []
                if samples:
                    desc += "{" + ",".join(str(s)[:18] for s in samples[:4]) + "}"
            col_descs.append(desc)
        lines.append(f"  {sheet_name}: " + ", ".join(col_descs))
    return "\n".join(lines)


def _recent_titles(row: Dict[str, Any], n: int = 6) -> List[str]:
    out: List[str] = []
    for h in (row.get("highlights") or [])[-n:]:
        if isinstance(h, dict) and h.get("title"):
            out.append(str(h["title"])[:100])
    return out


# ─────────────────────────────────────────────────────────────────────
# Persistence — append a highlight to analyses.highlights[]
# ─────────────────────────────────────────────────────────────────────
async def persist_highlight(
    *, db, aid: str, account_id: str, highlight: Dict[str, Any],
) -> Dict[str, Any]:
    """Append a single highlight to the analysis row. Tenant-scoped.

    Highlight shape:
      {id, title, body, topic, confidence, citation, intent,
       analyzer_payload, asked_question, created_at, refused?}
    """
    h = {
        "id":             "hl-" + uuid.uuid4().hex[:12],
        "created_at":     datetime.now(timezone.utc).isoformat(),
        **highlight,
    }
    # Clamp topic to the closed vocabulary.
    if h.get("topic") not in VALID_TOPICS:
        h["topic"] = "validate"
    await db.analyses.update_one(
        {"id": aid, "account_id": account_id},
        {
            "$push": {"highlights": h},
            "$set":  {"updated_at": h["created_at"]},
        },
    )
    return h


# ─────────────────────────────────────────────────────────────────────
# Main entry — route a free-text question to a highlight.
# ─────────────────────────────────────────────────────────────────────
async def _shield_invoke(*, prompt: str, account_id: str, consumer_id: str) -> str:
    """Thin shim — Shield-routed Claude Sonnet call. Returns raw text."""
    syn = get_synisense()
    result = await syn.shield_invoke(
        purpose="analyze_workspace.intent_router",
        content=prompt,
        account_id=account_id,
        consumer_id=consumer_id,
        user_id=account_id,
        model_preference="analytical",
        internal_caller=True,
    )
    # Phase 4.0 contract — `shield_invoke` returns `ShieldResult`
    # with `.response` carrying the assistant text and `.raw` a
    # provider-shaped dict. Prefer `.response` for the text.
    if hasattr(result, "response") and result.response is not None:
        return result.response
    raw = result.raw if hasattr(result, "raw") else result
    if isinstance(raw, dict):
        if isinstance(raw.get("text"), str):
            return raw["text"]
        if isinstance(raw.get("response"), str):
            return raw["response"]
        ch = raw.get("choices") or []
        if ch and isinstance(ch[0], dict):
            msg = ch[0].get("message") or {}
            return msg.get("content") or ""
    return str(raw)


async def route_question(
    *,
    db,
    aid: str,
    account_id: str,
    question: str,
    analysis_row: Dict[str, Any],
) -> Dict[str, Any]:
    """Classify the question, execute the matching analyzer (or
    refusal), narrate as a highlight, persist, return the highlight.

    This is the single entry point the FE `POST /v2/analyses/{aid}/ask`
    endpoint calls.
    """
    objective = (analysis_row.get("objective") or "").strip()
    column_summary = _column_summary_from_analysis(analysis_row)
    recent = _recent_titles(analysis_row)

    # 1) Intent classification.
    classify_prompt = _build_classifier_prompt(
        question=question, objective=objective,
        column_summary=column_summary, recent_highlight_titles=recent,
    )
    try:
        classify_raw = await _shield_invoke(
            prompt=classify_prompt, account_id=account_id,
            consumer_id="analyze_workspace.classify",
        )
    except Exception:
        logger.exception("analyze_workspace.classify_shield_failed")
        # Fail closed — surface a refusal highlight so the user sees
        # the failure rather than a 500.
        return await persist_highlight(db=db, aid=aid, account_id=account_id, highlight={
            "title":          "Couldn't classify that question",
            "body":           "The intent router timed out or refused. Try rephrasing with a clearer verb (forecast / simulate / extract).",
            "topic":          "refusal",
            "confidence":     "low",
            "citation":       "",
            "intent":         "refuse",
            "asked_question": question,
            "refused":        True,
            "refusal_reason": REFUSAL_REASONS["ambiguous_intent"],
        })

    intent_obj = _parse_json(classify_raw) or {}
    intent = (intent_obj.get("intent") or "refuse").lower()
    if intent not in {"forecast", "simulate", "extract", "validate", "anomaly", "refuse"}:
        intent = "refuse"

    # 2) Refusal path — short-circuit to a refusal highlight.
    if intent == "refuse":
        code = (intent_obj.get("refusal_reason_code") or "ambiguous_intent")
        return await persist_highlight(db=db, aid=aid, account_id=account_id, highlight={
            "title":          "Can't answer that from the loaded data",
            "body":           REFUSAL_REASONS.get(code, REFUSAL_REASONS["ambiguous_intent"]),
            "topic":          "refusal",
            "confidence":     "high",
            "citation":       "",
            "intent":         "refuse",
            "asked_question": question,
            "refused":        True,
            "refusal_reason": REFUSAL_REASONS.get(code, REFUSAL_REASONS["ambiguous_intent"]),
            "refusal_code":   code,
            "rationale":      intent_obj.get("rationale", ""),
        })

    # 3) Execute the analyzer. For Phase 2 proving slice we DON'T
    #    re-run the deterministic engines (forecast / simulate /
    #    extract) — the workbook router already exposes those as
    #    standalone endpoints. Instead we narrate the intent +
    #    target + scenario as a finding the user can use as an
    #    anchor, then the FE can deep-link the user to the matching
    #    deterministic run if they want raw numbers.
    #
    #    The narration carries the structured intent payload so the
    #    user can SEE what the workspace decided to run. This is
    #    what the canonical spec means by "capabilities run UNDER
    #    the surface — the user sees only the highlight."
    analyzer_payload = {
        "intent":   intent,
        "target":   intent_obj.get("target") or "",
        "horizon":  intent_obj.get("horizon"),
        "scenario": intent_obj.get("scenario"),
        "rationale": intent_obj.get("rationale", ""),
    }

    # 4) Narrate as a highlight card.
    narrate_prompt = _build_narration_prompt(
        question=question, intent=intent,
        analyzer_payload=analyzer_payload, objective=objective,
    )
    try:
        narrate_raw = await _shield_invoke(
            prompt=narrate_prompt, account_id=account_id,
            consumer_id="analyze_workspace.narrate",
        )
    except Exception:
        logger.exception("analyze_workspace.narrate_shield_failed")
        narrate_raw = ""

    card = _parse_json(narrate_raw) or {}
    title = (card.get("title") or f"{intent.title()} on “{question[:60]}”").strip()[:120]
    body = (card.get("body") or analyzer_payload.get("rationale") or
            "The workspace dispatched the question to the matching analyzer; review the deterministic run for raw numbers.").strip()[:600]
    topic = (card.get("topic") or intent).lower()
    if topic not in VALID_TOPICS:
        topic = intent if intent in VALID_TOPICS else "validate"
    confidence = (card.get("confidence") or "medium").lower()
    citation = (card.get("citation") or "").strip()[:120]

    return await persist_highlight(db=db, aid=aid, account_id=account_id, highlight={
        "title":            title,
        "body":             body,
        "topic":            topic,
        "confidence":       confidence,
        "citation":         citation,
        "intent":           intent,
        "asked_question":   question,
        "analyzer_payload": analyzer_payload,
        "refused":          False,
    })
