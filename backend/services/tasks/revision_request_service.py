"""JC-TM (2026-06-25) — AI-drafted revision request service.

The JC-TM canonical spec Part 0 calls out: "the AI drafts suggested
revision requests". This is the orchestration value of the Task
Manager — when the user spots a thin or off-target contribution, the
AI offers a respectful, specific revision request the user can edit
and send.

Shield-routed (purpose `task_manager.contributions.revision_request_draft`),
tenant-scoped, audit-logged. Falls through to a deterministic template
when Shield is unavailable so the user is never blocked.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

from services.tasks.compile_service import shield_invoke_bounded  # reuses same bounded helper

logger = logging.getLogger("akki.tasks.revision_draft")


def _strip_fences(s: str) -> str:
    s = (s or "").strip()
    m = re.search(r"```(?:markdown|text)?\s*(.*?)```", s, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return s


def _deterministic_revision_draft(
    *, contributor_name: str, contribution_desc: str, gap_hint: str,
) -> str:
    """Falls back when Shield is unavailable. Still gives the user a
    decent starting point — they can edit before sending."""
    name = contributor_name.split(" ")[0] or "there"
    return (
        f"Hi {name},\n\n"
        f"Thanks for the draft on \"{contribution_desc or 'your section'}\". "
        "Two specific asks before this can land in the pack:\n\n"
        f"• {gap_hint or 'Could you tighten the section into a single page with the headline read up top, and add one supporting datapoint per claim?'}\n"
        "• Could you cite the source for the numbers you reference? "
        "The board likes to see the underlying paper.\n\n"
        "If anything is unclear or you can't get to this by the due "
        "date, ping me and we'll figure out the lighter version.\n\n"
        "Thanks,"
    )


async def draft_revision_request(
    *, task: Dict[str, Any], contributor: Dict[str, Any],
    account_id: str, gap_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate a respectful, specific revision-request draft for ONE
    contributor on a task. Returns `{draft_text, source}` where `source`
    is `'shield'` (LLM-drafted) or `'fallback'` (template-derived)."""
    contributor_name = (contributor.get("name") or "").strip()
    contribution_desc = (contributor.get("contribution") or "").strip()
    objective = (task.get("objective") or "").strip()
    success_criteria = (task.get("success_criteria") or "").strip()
    task_name = (task.get("name") or "").strip()

    prompt = (
        "You are drafting a respectful, SPECIFIC revision-request note from "
        "an executive to one of their contributors on a task. The contribution "
        "isn't there yet; the executive wants to nudge it without micromanaging.\n\n"
        "Voice constraints:\n"
        "  • Plain, direct register. Not corporate.\n"
        "  • Lead with thanks for what arrived. Then 1-2 specific asks.\n"
        "  • If a gap is named, name it concretely (numbers, citations, "
        "the missing section). Don't be vague.\n"
        "  • Offer a fallback path if the contributor is stuck.\n"
        "  • 80-160 words. One paragraph plus 1-2 bullet asks. Close with "
        "the executive's name placeholder (\"Thanks,\").\n"
        "  • DO NOT include \"Subject:\" — just the body.\n"
        "  • NO em-dashes; use commas or full stops.\n\n"
        f"=== TASK ===\n{task_name}\n\n"
        f"=== OBJECTIVE ===\n{objective or '(not set)'}\n\n"
        f"=== SUCCESS CRITERIA ===\n{success_criteria or '(not set)'}\n\n"
        f"=== CONTRIBUTOR ===\n{contributor_name} (role: {contributor.get('role','')})\n"
        f"Assigned: {contribution_desc or '(not set)'}\n\n"
        f"=== GAP HINT ===\n{gap_hint or 'The contribution feels thin against the success criteria.'}\n\n"
        "Write the body of the revision request now. No prose around it."
    )

    result = await shield_invoke_bounded(
        purpose="task_manager.contributions.revision_request_draft",
        content=prompt,
        tenant_id=account_id, user_id=account_id, consumer_id="tasks",
    )
    if result and result.get("__timeout__"):
        logger.warning("revision_request_draft: shield timeout — using fallback")
        return {
            "draft_text": _deterministic_revision_draft(
                contributor_name=contributor_name,
                contribution_desc=contribution_desc,
                gap_hint=gap_hint or "",
            ),
            "source": "fallback",
            "reason": "shield_timeout",
        }
    if result and result.get("response"):
        text = _strip_fences(result["response"]).strip()
        if text:
            return {"draft_text": text, "source": "shield"}
    # Shield returned empty / errored — fall through.
    return {
        "draft_text": _deterministic_revision_draft(
            contributor_name=contributor_name,
            contribution_desc=contribution_desc,
            gap_hint=gap_hint or "",
        ),
        "source": "fallback",
        "reason": "shield_empty",
    }
