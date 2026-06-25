"""JC-WS Phase 2 (2026-06-25) — data-aware question tips.

Generates 4-6 short tip strings that the AnalyzeDrawer shows under
the docked prompt input. Tips are derived from:
  • the actual sheet columns + their kinds (date / numeric / text)
  • the user's objective (if set)
  • the recent highlights on the thread (so we don't suggest a
    question that's already been answered)

Output is deterministic in shape (list of {text, intent}) so the
FE renders them as clickable chips that pre-fill the prompt input.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List

from contracts import get_synisense

logger = logging.getLogger(__name__)


def _column_lines(row: Dict[str, Any]) -> str:
    sheets = row.get("sheets") or []
    if not sheets:
        return "(no sheets loaded)"
    out: List[str] = []
    for sheet in sheets[:2]:
        sn = sheet.get("name") or "Sheet1"
        cols = sheet.get("columns") or []
        col_descs = []
        for c in cols[:8]:
            col_descs.append(f"{c.get('name','?')}({c.get('kind','text')})")
        out.append(f"  {sn}: " + ", ".join(col_descs))
    return "\n".join(out)


def _strip_fences(s: str) -> str:
    s = (s or "").strip()
    m = re.search(r"```(?:json)?\s*(.*?)```", s, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return s


def _shield_text(raw: Any) -> str:
    if isinstance(raw, dict):
        if isinstance(raw.get("text"), str):
            return raw["text"]
        ch = raw.get("choices") or []
        if ch and isinstance(ch[0], dict):
            msg = ch[0].get("message") or {}
            return msg.get("content") or ""
    return str(raw)


# Deterministic fallback when Shield is down — derived purely from
# column kinds. The spec says tips MUST be data-aware; this still
# qualifies because the suggestions reflect the actual loaded data.
def _deterministic_tips(row: Dict[str, Any]) -> List[Dict[str, str]]:
    sheets = row.get("sheets") or []
    if not sheets:
        return [
            {"text": "Load a workbook to get data-aware suggestions.", "intent": "extract"},
        ]
    cols = sheets[0].get("columns") or []
    dates = [c["name"] for c in cols if c.get("kind") == "date"][:1]
    numerics = [c["name"] for c in cols if c.get("kind") == "numeric"][:3]
    tips: List[Dict[str, str]] = []
    if dates and numerics:
        tips.append({"text": f"Forecast {numerics[0]} for the next 3 periods", "intent": "forecast"})
        tips.append({"text": f"Where did {numerics[0]} deviate the most from trend?", "intent": "anomaly"})
    if len(numerics) >= 2:
        tips.append({"text": f"What if {numerics[0]} stayed flat — how does {numerics[1]} respond?", "intent": "simulate"})
    if numerics:
        tips.append({"text": f"Total {numerics[0]} for the latest period", "intent": "extract"})
    if dates:
        tips.append({"text": f"Validate: did {numerics[0] if numerics else 'the headline metric'} grow YoY?", "intent": "validate"})
    return tips[:5]


async def generate_tips(
    *, account_id: str, analysis_row: Dict[str, Any], cap: int = 5,
) -> List[Dict[str, str]]:
    """Return up to `cap` data-aware question tips for the FE chip strip.

    Uses Shield-routed Claude Sonnet when available; falls back to
    a deterministic column-derived list when the LLM is unreachable
    (the spec says NO fabrication; the deterministic path is still
    grounded in the actual columns)."""
    objective = (analysis_row.get("objective") or "").strip()
    columns = _column_lines(analysis_row)
    recent_titles = [
        h.get("title", "")
        for h in (analysis_row.get("highlights") or [])[-6:]
        if isinstance(h, dict) and h.get("title")
    ]
    recent_block = "\n".join(f"  - {t}" for t in recent_titles[-4:]) or "  (none yet)"

    prompt = (
        "Suggest short, executive-grade follow-up questions for an "
        "analyst working through a data file. Output STRICT JSON only:\n"
        "{\n"
        '  "tips": [\n'
        '    {"text": "<question, <= 80 chars>", "intent": "forecast|simulate|extract|validate|anomaly"},\n'
        "    ...\n"
        "  ]\n"
        "}\n\n"
        f"Cap: {cap}. Match the question to ONE of the listed intents.\n"
        "AVOID generic prompts (\"what does the data say\"). Each tip "
        "MUST reference a column name or metric from the data summary. "
        "Don't suggest something covered by a recent highlight.\n\n"
        f"=== OBJECTIVE ===\n{objective or '(not set)'}\n\n"
        f"=== COLUMNS ===\n{columns}\n\n"
        f"=== RECENT HIGHLIGHTS ===\n{recent_block}\n"
    )
    try:
        syn = get_synisense()
        result = await syn.shield_invoke(
            purpose="analyze_workspace.tips",
            content=prompt,
            account_id=account_id,
            consumer_id="analyze_workspace.tips",
            user_id=account_id,
            model_preference="analytical",
            internal_caller=True,
        )
        # ShieldResult — .response is the assistant text.
        if hasattr(result, "response") and result.response is not None:
            text = result.response
        else:
            raw = result.raw if hasattr(result, "raw") else result
            text = _shield_text(raw)
        s = _strip_fences(text)
        # Find outermost {…}
        if not s.startswith("{"):
            i = s.find("{")
            if i >= 0:
                s = s[i:]
        j = s.rfind("}")
        if j >= 0:
            s = s[: j + 1]
        parsed = json.loads(s)
        tips_raw = parsed.get("tips") or []
        out: List[Dict[str, str]] = []
        for t in tips_raw[:cap]:
            if not isinstance(t, dict):
                continue
            txt = str(t.get("text", "")).strip()[:120]
            it = str(t.get("intent", "")).strip().lower()
            if it not in {"forecast", "simulate", "extract", "validate", "anomaly"}:
                it = "extract"
            if txt:
                out.append({"text": txt, "intent": it})
        if out:
            return out
    except Exception:
        logger.exception("analyze_workspace.tips_shield_failed")

    # Fallback: deterministic, column-derived tips.
    return _deterministic_tips(analysis_row)
