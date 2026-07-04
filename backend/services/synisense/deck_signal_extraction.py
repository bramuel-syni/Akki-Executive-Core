"""JC-WS-DECK-A9-BACKEND-DECK-SIGNAL-EXTRACTION (2026-07-04) — deck-signal extraction pipeline.

Canonical spec: /app/memory/sprints/JC_WS_DECK_A9_BACKEND_DECK_SIGNAL_EXTRACTION.md
             + /app/memory/sprints/H2_SHIELD_UNIFORMITY_AUDIT.md (Shield uniformity discipline)

F.6 discipline-pay: FULL. Deck-signal extraction is an LLM path. Routes
through the existing SyniSense Shield chokepoint (`services/synisense/shield/*`
UNTOUCHED). Signals are derived from Shield's outbound-saw content
(the `sr.raw["response"]` string returned by `shield_invoke`), never
from raw pre-Shield deck text.

De-identification class inherited from source: the persisted record
carries `derivation_class = source_deck["data_trust"]`. The source
deck's `data_trust` is itself computed from the trust aggregate of the
underlying source documents (via `docs_overall_trust()` in `core.py`),
so the inheritance chain is preserved end-to-end.

Chokepoint (identical to `routers/chat.py:1928` — same import path,
same call signature, same audit-event fingerprint):

    from contracts import get_synisense
    result = await get_synisense().shield_invoke(
        purpose="deck.signal_extraction",
        content=deck_text,
        account_id=account_id,
        consumer_id="deck_signals",
        user_id=account_id,
        model_preference="analytical",
        internal_caller=True,
        system_msg=SYSTEM_PROMPT,
    )

No `services/synisense/shield/**` file is imported here. No LLM SDK
(openai / anthropic / google.generativeai) is imported. R12 of the
A9-backend proving slice enforces this positively.
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from contracts import get_synisense  # canonical Shield chokepoint

logger = logging.getLogger("work_studio.deck_signal_extraction")


SYSTEM_PROMPT = (
    "You are a signals-extraction assistant. Given the contents of a Deck "
    "document, identify the top actionable signals: risks, opportunities, "
    "priorities, or open questions the reader should act on. Return STRICT "
    "JSON in the following shape, with 3-8 signal entries:\n"
    "{\n"
    '  "signals": [\n'
    '    {"text": "<one-sentence signal>", "category": "risk|opportunity|priority|open_question", "confidence": 0.0-1.0}\n'
    "  ]\n"
    "}\n"
    "No prose, no code fences, JSON only."
)


PURPOSE = "work_studio.deck.signal_extraction"
CONSUMER_ID = "deck_signals"


@dataclass
class ExtractedSignal:
    id: str
    text: str
    category: str
    confidence: float
    addressed: bool = False


@dataclass
class ExtractedSignals:
    document_id: str
    account_id: str
    signals: List[ExtractedSignal]
    derivation_class: str  # inherited from source deck's data_trust
    shield_audit_event_id: Optional[str]
    source_deck_updated_at: Optional[str]
    raw_response: str = ""
    raw: Dict[str, Any] = field(default_factory=dict)


def _extract_deck_text(deck_document: Dict[str, Any]) -> str:
    """Compose the deck content string fed to Shield. Uses the
    document's `extracted_text` (already post-ingest) — same content
    surface Chat's grounding path uses when a deck is attached."""
    text = deck_document.get("extracted_text") or ""
    if not text:
        # Fall back to preview or name — an honest empty-substrate signal
        # for the extraction call rather than a fabricated body.
        text = deck_document.get("preview") or deck_document.get("name") or ""
    # Guard against runaway prompts — cap at 24000 chars (mirrors
    # MAX_DOC_CHARS_PER_PROMPT-ish sizing).
    return text[:24000]


def _parse_signals_from_response(response_text: str) -> List[Dict[str, Any]]:
    """Parse JSON-shaped signals from Shield's outbound-saw response.

    Uses defensive parsing: strip optional code fences, extract the
    outermost JSON object. Truth-in-capability: if the LLM violates the
    JSON contract, we return an empty list rather than fabricating
    signals from the raw text (the extraction is best-effort against
    the LLM's compliance with the STRICT-JSON directive)."""
    if not response_text:
        return []
    text = response_text.strip()
    # Strip common code-fence wrappers if present.
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    # Extract outermost JSON object.
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return []
    try:
        obj = json.loads(m.group(0))
    except Exception:  # noqa: BLE001
        return []
    signals = obj.get("signals") if isinstance(obj, dict) else None
    if not isinstance(signals, list):
        return []
    out: List[Dict[str, Any]] = []
    for s in signals:
        if not isinstance(s, dict):
            continue
        text_val = str(s.get("text") or "").strip()
        if not text_val:
            continue
        cat = str(s.get("category") or "priority").strip().lower()
        if cat not in ("risk", "opportunity", "priority", "open_question"):
            cat = "priority"
        try:
            conf = float(s.get("confidence") or 0.5)
        except Exception:  # noqa: BLE001
            conf = 0.5
        conf = max(0.0, min(1.0, conf))
        out.append({"text": text_val, "category": cat, "confidence": conf})
    return out


async def extract_deck_signals(
    deck_document: Dict[str, Any],
    account_context: Dict[str, Any],
) -> ExtractedSignals:
    """Extract signals from a Deck document, routing through Shield.

    Args:
      deck_document: a `db.documents` row (dict, `_id` excluded is fine).
      account_context: `{"account_id": str}` — Shield tenant scope.

    Returns:
      ExtractedSignals with:
        - `signals` list (may be empty on thin-substrate / non-JSON responses).
        - `derivation_class` inherited from `deck_document["data_trust"]`.
        - `shield_audit_event_id` from `result.audit_id` — used by R4 side-by-side.
        - `source_deck_updated_at` from `deck_document["updated_at"]` for staleness detection.
    """
    account_id = account_context["account_id"]
    document_id = deck_document.get("id") or ""
    deck_text = _extract_deck_text(deck_document)

    # Shield invocation — this is the F.6 discipline-pay point.
    # Fail-closed: if Shield raises, we propagate (caller returns 500).
    contract = get_synisense()
    result = await contract.shield_invoke(
        purpose=PURPOSE,
        content=deck_text,
        account_id=account_id,
        consumer_id=CONSUMER_ID,
        user_id=account_id,
        model_preference="analytical",
        internal_caller=True,
        system_msg=SYSTEM_PROMPT,
    )
    # `ShieldResult` is a frozen dataclass — use .raw for the wire dict
    # + typed .audit_id for the id we persist.
    outbound_response = result.raw.get("response") or ""
    shield_audit_id: Optional[str] = result.audit_id

    parsed = _parse_signals_from_response(outbound_response)
    signals = [
        ExtractedSignal(
            id=str(uuid.uuid4()),
            text=p["text"],
            category=p["category"],
            confidence=p["confidence"],
            addressed=False,
        )
        for p in parsed
    ]

    return ExtractedSignals(
        document_id=document_id,
        account_id=account_id,
        signals=signals,
        # Derivation class inherited from source deck's data_trust
        # (source-inheritance chain preserved end-to-end).
        derivation_class=str(deck_document.get("data_trust") or "unrated"),
        shield_audit_event_id=shield_audit_id,
        source_deck_updated_at=str(deck_document.get("updated_at") or ""),
        raw_response=outbound_response,
        raw={"purpose": PURPOSE, "consumer_id": CONSUMER_ID},
    )


def signals_to_dict(extracted: ExtractedSignals) -> Dict[str, Any]:
    """Serialise for Mongo / API response."""
    return {
        "document_id": extracted.document_id,
        "account_id": extracted.account_id,
        "signals": [
            {
                "id": s.id, "text": s.text, "category": s.category,
                "confidence": s.confidence, "addressed": s.addressed,
            }
            for s in extracted.signals
        ],
        "derivation_class": extracted.derivation_class,
        "shield_audit_event_id": extracted.shield_audit_event_id,
        "source_deck_updated_at": extracted.source_deck_updated_at,
    }
