"""JC-MON Stage 3.1 — Email-update progress extractor for Monitor tasks.

Source of truth: `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 3 ·
"TASK EMAIL-UPDATE LOOP: REUSE Task Manager's inbound-email mechanism
— owner emails an update → AI extracts progress → task auto-updates
→ update history records it. Do NOT build a second loop; wire Monitor
tasks onto the existing one, **additively**, without regressing TM.")

User resolution (2026-06-25):
> 3.1 Task drawer discriminator: additive on `tasks`; `objective_id`
> discriminates ONLY what attaches + what renders. ONE inbound email
> extraction path. Do not fork.

This module is the ONE additive extension on top of the existing
`_handle_task_contributor_reply` path in `routers/inbound_email.py`.
The discriminator is `task.objective_id`:

  • objective_id == None → task is a Task Manager task. The existing
    inbound-email handler's behaviour is UNCHANGED (contributor_comments
    push + team status flip + readiness recompute + audit row). This
    module is NOT invoked.

  • objective_id != None → task is a MONITOR task linked to a strategic
    objective. The existing TM-mode behaviour STILL RUNS unchanged
    (so the entity invariant "one task, one email loop" holds), and
    THEN this module is invoked ADDITIVELY to:
      1. Extract a progress signal (pct + rationale + optional metric)
         from the cleaned email body via a single Shield-routed call.
      2. Append the extracted signal to the task's `progress_updates`
         history (Monitor drawer renders this timeline).
      3. Set `task.progress_pct` to the latest extracted value if the
         signal is grounded (refusals leave it untouched).

Refusal short-circuits (honest):
  - empty cleaned body → no LLM call, return refused with reason
    `no_email_body_to_extract`.
  - LLM parse failure → audit trail preserved, reason
    `progress_extraction_parse_failed`, no `progress_updates` write.

Standing guarantees (canonical-spec contract):
  - Shield-routed (`solve_v2.monitor_email_update_extract`).
  - account/context-scoped via the existing inbound-email auth path.
  - additive-only on the shared `tasks` collection.
  - NO JC-TM regression: TM-mode tasks bypass this module entirely;
    Monitor-mode tasks still run the TM-mode behaviour, then layer
    progress extraction on top.
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from services.solva_v2.engines.llm_adapter_proxy import shielded_call


logger = logging.getLogger("akki.monitor.email_update_extractor")


_EXTRACT_SURFACE = "solve_v2.monitor_email_update_extract"
_EXTRACT_LAYER = "monitor.email_update_extract"


_EXTRACT_SYSTEM_PROMPT = (
    "You are AKKI Monitor's email-update progress extractor. The"
    " owner of a Monitor task (linked to a strategic objective) has"
    " emailed a progress update. Read the body and extract a single"
    " progress signal.\n\n"
    "Discipline:\n"
    " 1. `progress_pct` is 0-100. 0 = no movement; 100 = task done."
    " If the body doesn't state a clear progress signal, return"
    " progress_pct=null and explain in `_refusal_note`.\n"
    " 2. `rationale` is a one-sentence quote-or-paraphrase from the"
    " body (≤ 240 chars) — never invent content not in the email.\n"
    " 3. `target_metric` is OPTIONAL — populate ONLY if the body"
    " names a specific metric (\"revenue index 92\", \"DSO 58\","
    " etc); otherwise leave empty.\n"
    " 4. NEVER fabricate a progress number not stated/derivable"
    " from the body.\n\n"
    "Output JSON SHAPE ONLY:\n"
    "  {\n"
    "    \"progress_pct\": <int 0-100> | null,\n"
    "    \"rationale\": \"<one sentence>\",\n"
    "    \"target_metric\": \"<optional metric name>\" | \"\",\n"
    "    \"_refusal_note\": \"\"\n"
    "  }\n"
    "No prose around the JSON. No code fences."
)


_PROGRESS_JSON = re.compile(r"\{.*?\"progress_pct\".*?\}", re.DOTALL)


def _parse_extract(raw: str) -> Optional[Dict[str, Any]]:
    """Fence-strip + brace-balance parser (shared idiom across 2b)."""
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
        pct_raw = obj.get("progress_pct")
        rationale = (obj.get("rationale") or "").strip()
        target_metric = (obj.get("target_metric") or "").strip()
        if pct_raw is None:
            return {
                "progress_pct": None,
                "rationale": rationale[:240],
                "target_metric": target_metric[:120],
                "refusal_note": (obj.get("_refusal_note") or "").strip(),
            }
        if isinstance(pct_raw, (int, float)) and 0 <= pct_raw <= 100:
            return {
                "progress_pct": int(round(pct_raw)),
                "rationale": rationale[:240],
                "target_metric": target_metric[:120],
                "refusal_note": (obj.get("_refusal_note") or "").strip(),
            }
    return None


async def extract_email_progress_update(
    *,
    task: Dict[str, Any],
    cleaned_body: str,
    sender_email: str,
) -> Dict[str, Any]:
    """Public entry — extract a progress signal from a Monitor-task
    email reply. ADDITIVE on top of the existing TM-mode behaviour.

    Caller-contract:
      - The task MUST carry `objective_id` (the discriminator).
        TM-mode tasks bypass this function entirely; the caller
        guards on `objective_id is None`.

    Returns:
      {
        "refused":            bool,
        "refusal_reason":     Optional[str],
        "progress_pct":       Optional[int],
        "rationale":          Optional[str],
        "target_metric":      Optional[str],
        "refusal_note":       Optional[str],
        "audit_entry_ids":    List[str],
        "extracted_at":       ISO,
        "sender":             str,
      }
    """
    if not task.get("objective_id"):
        raise ValueError(
            "extract_email_progress_update: task.objective_id is required "
            "(this function is the Monitor-discriminator branch)"
        )

    now_iso = datetime.now(timezone.utc).isoformat()

    body = (cleaned_body or "").strip()
    if not body:
        return {
            "refused":         True,
            "refusal_reason":  "no_email_body_to_extract",
            "progress_pct":    None,
            "rationale":       None,
            "target_metric":   None,
            "refusal_note":    "Email arrived without a parseable text body.",
            "audit_entry_ids": [],
            "extracted_at":    now_iso,
            "sender":          sender_email,
        }

    session = {
        "id":         str(uuid.uuid4()),
        "account_id": task.get("account_id"),
        "context_id": task.get("context_id"),
    }

    prompt = (
        f"TASK:\n"
        f"  name:          {task.get('name', '(untitled)')}\n"
        f"  objective:     {task.get('objective', '(none)')}\n"
        f"  success_criteria: {task.get('success_criteria', '(none)')}\n"
        f"  due_date:      {task.get('due_date', '(no deadline)')}\n"
        f"  linked_objective_id: {task['objective_id']}\n\n"
        f"FROM: {sender_email}\n\n"
        f"EMAIL BODY:\n"
        f"---\n{body[:4000]}\n---\n\n"
        f"Extract the progress signal. Return the JSON now."
    )

    result = await shielded_call(
        engine="monitor_email_update_extract",
        layer=_EXTRACT_LAYER,
        turn_id=task["id"],
        prompt=prompt,
        system_override=_EXTRACT_SYSTEM_PROMPT,
        tier="standard",
        surface=_EXTRACT_SURFACE,
        account_id=session.get("account_id"),
        session_id=session["id"],
        context_id=session.get("context_id"),
        engine_version="monitor_email_update_extract@1.0",
        extra_output={"objective_id": task["objective_id"]},
    )
    audit = result.reasoning_audit_entry or {}
    audit_ids: List[str] = []
    if audit.get("id"):
        audit_ids.append(audit["id"])

    parsed = _parse_extract(result.text or "")
    if parsed is None:
        return {
            "refused":         True,
            "refusal_reason":  "progress_extraction_parse_failed",
            "progress_pct":    None,
            "rationale":       None,
            "target_metric":   None,
            "refusal_note":    (
                "Auto-calibrated: progress extractor failed to "
                "return a parseable JSON over the email body."
            ),
            "audit_entry_ids": audit_ids,
            "extracted_at":    now_iso,
            "sender":          sender_email,
        }

    return {
        "refused":         parsed["progress_pct"] is None,
        "refusal_reason":  (
            "no_progress_signal_in_body" if parsed["progress_pct"] is None
            else None
        ),
        "progress_pct":    parsed["progress_pct"],
        "rationale":       parsed["rationale"] or None,
        "target_metric":   parsed["target_metric"] or None,
        "refusal_note":    parsed.get("refusal_note") or None,
        "audit_entry_ids": audit_ids,
        "extracted_at":    now_iso,
        "sender":          sender_email,
    }


async def apply_monitor_progress_update(
    *,
    db: Any,
    task_id: str,
    extraction: Dict[str, Any],
) -> Dict[str, Any]:
    """Append the extraction to `tasks.progress_updates[]` and, if
    the extraction is grounded (refused=False), update `progress_pct`
    on the task row.

    Returns the persisted history entry (includes a stable `id`).
    """
    entry_id = str(uuid.uuid4())
    history_entry: Dict[str, Any] = {
        "id":              entry_id,
        "kind":            "email_extract",
        "extracted_at":    extraction.get("extracted_at"),
        "sender":          extraction.get("sender"),
        "progress_pct":    extraction.get("progress_pct"),
        "rationale":       extraction.get("rationale"),
        "target_metric":   extraction.get("target_metric"),
        "refused":         extraction.get("refused"),
        "refusal_reason":  extraction.get("refusal_reason"),
        "audit_entry_ids": extraction.get("audit_entry_ids") or [],
    }

    set_fields: Dict[str, Any] = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }
    if not extraction.get("refused"):
        set_fields["progress_pct"] = extraction.get("progress_pct")

    await db.tasks.update_one(  # tenancy:allow-no-account-id — Monitor email update: token validated upstream by F.5 token check
        {"id": task_id},
        {
            "$push": {"progress_updates": history_entry},
            "$set": set_fields,
        },
    )
    return history_entry


__all__ = [
    "extract_email_progress_update",
    "apply_monitor_progress_update",
]
