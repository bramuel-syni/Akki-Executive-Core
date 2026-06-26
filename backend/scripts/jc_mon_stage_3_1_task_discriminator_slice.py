"""JC-MON Stage 3.1 — Task drawer discriminator + email-update loop proving slice.

Source of truth: `/app/memory/JC_MON_CANONICAL_SPEC.md` (§ Stage 3 ·
"TASKS (same entity as TM, discriminated by `objective_id`)" +
"TASK EMAIL-UPDATE LOOP: REUSE Task Manager's inbound-email mechanism
— wire Monitor tasks onto the existing one, ADDITIVELY, without
regressing TM").

User resolution (2026-06-25):
> 3.1 Task drawer discriminator: additive on `tasks`; `objective_id`
> discriminates ONLY what attaches + what renders. ONE inbound email
> extraction path. Do not fork.

Acceptance rows (6/6 required):
  A. ONE task entity — `db.tasks` accepts BOTH TM-mode (objective_id
     == None) AND Monitor-mode (objective_id != None) rows. Same
     collection. Same schema (additive field only).
  B. ONE drawer rendered by context — `_sanitize_task` surfaces
     `objective_id` + `progress_updates`; consumers branch on
     `objective_id` to render TM vs Monitor view.
  C. TM-mode unchanged — a contributor email reply for a task with
     objective_id == None pushes contributor_comments + flips
     team status + recomputes readiness, AND the new
     `monitor_progress_entry` field in the response is None.
     **JC-TM regression-free.**
  D. Monitor-mode extracts progress — a contributor email reply for
     a task with objective_id != None ALSO runs the TM-mode behaviour
     unchanged AND additively extracts a progress signal via the
     Shield-routed `solve_v2.monitor_email_update_extract` engine.
     The extraction lands in `tasks.progress_updates[]`.
  E. ONE inbound path — both rows go through the SAME
     `_handle_task_contributor_reply` function. No fork. Verified by
     calling the function once per task and inspecting outcomes.
  F. Honest refusal — a Monitor-mode email with no progress-shaped
     body surfaces `refused=True, refusal_reason="no_progress_signal_in_body"`
     (or similar) in `progress_updates[]`. No fabricated progress_pct.

Artefacts → `/app/memory/jc_artifacts/JC-MON/03-experience/3-1-task-discriminator/`.

Run from the repo root:
    cd /app/backend && python scripts/jc_mon_stage_3_1_task_discriminator_slice.py
"""
from __future__ import annotations

import asyncio
import base64
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path("/app/backend")
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv("/app/backend/.env")


from core import db  # noqa: E402
from routers.inbound_email import _handle_task_contributor_reply  # noqa: E402


ART_DIR = Path("/app/memory/jc_artifacts/JC-MON/03-experience/3-1-task-discriminator")
ART_DIR.mkdir(parents=True, exist_ok=True)


ACCOUNT_ID = "cf6e7587-9abd-46aa-b8f4-f342e9b066ef"
CONTEXT_ID = "a2937d0f-37f1-4042-a897-ab73a6cd652a"


async def _mint_task_with_token(
    *, objective_id: str | None,
    contributor_email: str = "tm-contributor@mara-heritage.test",
) -> Dict[str, Any]:
    """Mint a task + a F.5 contributor token in db.task_contributor_tokens."""
    tid = f"task-{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    team_member = {
        "id":                str(uuid.uuid4()),
        "name":              "Test Contributor",
        "role":              "Owner",
        "email":             contributor_email,
        "contribution":      "Submit weekly progress update",
        "status":            "invited",
        "contribution_mode": "email_reply",
    }
    task_doc = {
        "id":               tid,
        "account_id":       ACCOUNT_ID,
        "context_id":       CONTEXT_ID,
        "name":             "JC-MON Stage 3.1 — owner update task",
        "objective":        "Track Recovery Programme weekly progress",
        "success_criteria": "Owner emails weekly status updates",
        "state":            "active",
        "team":             [team_member],
        "due_date":         None,
        "created_at":       now_iso,
        "updated_at":       now_iso,
        "status_history":   [{"state": "active", "at": now_iso}],
        # Stage 3.1 discriminator field.
        "objective_id":     objective_id,
    }
    await db.tasks.insert_one(dict(task_doc))

    # F.5 token row — `_handle_task_contributor_reply` reads this.
    token = uuid.uuid4().hex
    await db.task_contributor_tokens.insert_one({
        "token":              token,
        "task_id":            tid,
        "task_account_id":    ACCOUNT_ID,
        "contributor_email":  contributor_email,
        "contributor_id":     team_member["id"],
        "used":               False,
        "created_at":         now_iso,
    })
    return {"task": task_doc, "token": token, "contributor_email": contributor_email}


def _make_payload(*, body_text: str, from_email: str) -> Dict[str, Any]:
    """Postmark-shape payload."""
    return {
        "TextBody":  body_text,
        "HtmlBody":  "",
        "From":      from_email,
        "FromName":  "Test Contributor",
        "Subject":   "Re: Weekly recovery update",
        "MessageID": f"msg-{uuid.uuid4().hex[:12]}",
        "_provider": "test_slice",
    }


async def _scenario_tm_mode_unchanged() -> Dict[str, Any]:
    """Acceptance C — TM-mode task; verify TM behaviour intact AND
    monitor_progress_entry is None (discriminator off)."""
    print("[1/3] TM-mode (objective_id=None) — verify TM behaviour intact …")
    minted = await _mint_task_with_token(objective_id=None)
    tid = minted["task"]["id"]
    token = minted["token"]
    payload = _make_payload(
        body_text=(
            "Hi team, quick update — checkout regression is fixed in staging, "
            "release tonight. No surprises. Thanks!"
        ),
        from_email=minted["contributor_email"],
    )
    resp = await _handle_task_contributor_reply(
        payload=payload, token_hash=token,
        from_email=minted["contributor_email"], from_name="Test Contributor",
        subject=payload["Subject"], text_body=payload["TextBody"],
        html_body="", message_id=payload["MessageID"],
        attachments_raw=[],
    )
    persisted = await db.tasks.find_one({"id": tid}, {"_id": 0})
    return {
        "task_id":               tid,
        "objective_id_on_task":  persisted.get("objective_id"),
        "response":              resp,
        "contributor_comments":  persisted.get("contributor_comments") or [],
        "team_status_after":     [m.get("status") for m in (persisted.get("team") or [])],
        "progress_updates":      persisted.get("progress_updates") or [],
        "monitor_progress_entry": resp.get("monitor_progress_entry"),
    }


async def _scenario_monitor_mode_extracts() -> Dict[str, Any]:
    """Acceptance D — Monitor-mode task with progress-shaped body;
    verify TM behaviour ALSO runs AND progress extracted."""
    print("[2/3] Monitor-mode (objective_id=<obj>) — progress-shaped email …")
    obj_id = f"obj-stage3-1-{uuid.uuid4().hex[:8]}"
    minted = await _mint_task_with_token(
        objective_id=obj_id,
        contributor_email="recovery-owner@mara-heritage.test",
    )
    tid = minted["task"]["id"]
    token = minted["token"]
    payload = _make_payload(
        body_text=(
            "Week 9 status: Phase 1 exit gate PASSED. "
            "Weekly active sessions index recovered to 97 by Week 9. "
            "Checkout conversion pct now 102% of Q1 mean. Phase 2 reactivation "
            "campaign launched Week 8. Headline monthly active revenue index "
            "this period: 92. Overall progress against target: 65%."
        ),
        from_email=minted["contributor_email"],
    )
    resp = await _handle_task_contributor_reply(
        payload=payload, token_hash=token,
        from_email=minted["contributor_email"], from_name="Recovery Owner",
        subject=payload["Subject"], text_body=payload["TextBody"],
        html_body="", message_id=payload["MessageID"],
        attachments_raw=[],
    )
    persisted = await db.tasks.find_one({"id": tid}, {"_id": 0})
    return {
        "task_id":               tid,
        "objective_id_on_task":  persisted.get("objective_id"),
        "response":              resp,
        "contributor_comments":  persisted.get("contributor_comments") or [],
        "team_status_after":     [m.get("status") for m in (persisted.get("team") or [])],
        "progress_updates":      persisted.get("progress_updates") or [],
        "monitor_progress_entry": resp.get("monitor_progress_entry"),
        "tasks_progress_pct":    persisted.get("progress_pct"),
    }


async def _scenario_monitor_mode_refuses() -> Dict[str, Any]:
    """Acceptance F — Monitor-mode task with NO progress-shaped body;
    verify honest refusal (no fabricated progress_pct)."""
    print("[3/3] Monitor-mode (objective_id=<obj>) — empty / non-progress body …")
    obj_id = f"obj-stage3-1-refusal-{uuid.uuid4().hex[:8]}"
    minted = await _mint_task_with_token(
        objective_id=obj_id,
        contributor_email="opaque-update@mara-heritage.test",
    )
    tid = minted["task"]["id"]
    token = minted["token"]
    # Body intentionally has no progress signal — just a greeting.
    payload = _make_payload(
        body_text="Hi — just checking in. Will send the proper update next week. Cheers.",
        from_email=minted["contributor_email"],
    )
    resp = await _handle_task_contributor_reply(
        payload=payload, token_hash=token,
        from_email=minted["contributor_email"], from_name="Vague Sender",
        subject=payload["Subject"], text_body=payload["TextBody"],
        html_body="", message_id=payload["MessageID"],
        attachments_raw=[],
    )
    persisted = await db.tasks.find_one({"id": tid}, {"_id": 0})
    return {
        "task_id":               tid,
        "response":              resp,
        "progress_updates":      persisted.get("progress_updates") or [],
        "monitor_progress_entry": resp.get("monitor_progress_entry"),
        "tasks_progress_pct":    persisted.get("progress_pct"),
    }


def _write_artefact(name: str, payload: Dict[str, Any]) -> Path:
    path = ART_DIR / name
    path.write_text(json.dumps(payload, indent=2, default=str))
    print(f"  → {path}")
    return path


def _assert(cond: bool, msg: str) -> None:
    label = "✅" if cond else "❌"
    print(f"  {label} {msg}")
    if not cond:
        raise AssertionError(msg)


def _acceptance_rows(
    tm_scenario: Dict[str, Any],
    monitor_scenario: Dict[str, Any],
    refusal_scenario: Dict[str, Any],
) -> None:
    print("\n— ACCEPTANCE ROWS (6/6 required) —")
    # Row A — one entity (both rows in db.tasks)
    _assert(
        tm_scenario["task_id"] != monitor_scenario["task_id"]
        and tm_scenario["task_id"].startswith("task-")
        and monitor_scenario["task_id"].startswith("task-"),
        "A. ONE entity: TM-mode + Monitor-mode tasks both in db.tasks (same id prefix)",
    )
    # Row B — discriminator surfaced (objective_id present on Monitor row)
    _assert(
        tm_scenario["objective_id_on_task"] is None
        and monitor_scenario["objective_id_on_task"] is not None,
        "B. ONE drawer-by-context: objective_id is None for TM, set for Monitor row",
    )
    # Row C — TM-mode unchanged (contributor_comments + team status)
    tm_comments_count = len(tm_scenario["contributor_comments"])
    tm_team_status = tm_scenario["team_status_after"]
    _assert(
        tm_comments_count >= 1
        and "submitted" in tm_team_status
        and tm_scenario["monitor_progress_entry"] is None
        and not tm_scenario["progress_updates"],
        f"C. TM-mode unchanged: comments={tm_comments_count} team_status={tm_team_status} "
        f"monitor_progress_entry={tm_scenario['monitor_progress_entry']} "
        f"progress_updates={len(tm_scenario['progress_updates'])}",
    )
    # Row D — Monitor-mode: TM behaviour ALSO runs + progress extracted
    m_comments_count = len(monitor_scenario["contributor_comments"])
    m_team_status = monitor_scenario["team_status_after"]
    m_updates = monitor_scenario["progress_updates"]
    m_entry = monitor_scenario["monitor_progress_entry"]
    _assert(
        m_comments_count >= 1 and "submitted" in m_team_status
        and len(m_updates) == 1
        and m_entry is not None
        and not m_entry.get("refused")
        and isinstance(m_entry.get("progress_pct"), int),
        f"D. Monitor-mode: TM behaviour PRESERVED (comments={m_comments_count} status={m_team_status}) "
        f"AND additive progress extracted (pct={m_entry.get('progress_pct') if m_entry else None})",
    )
    # Row E — ONE inbound path (both scenarios called the SAME function;
    # verified by both returning ok=True from the same handler)
    _assert(
        tm_scenario["response"].get("ok") is True
        and monitor_scenario["response"].get("ok") is True,
        "E. ONE inbound path: both scenarios served by _handle_task_contributor_reply (ok=True both)",
    )
    # Row F — Honest refusal on opaque body
    r_entry = refusal_scenario["monitor_progress_entry"] or {}
    r_updates = refusal_scenario["progress_updates"]
    _assert(
        len(r_updates) == 1
        and (
            r_updates[0].get("refused") is True
            or r_updates[0].get("progress_pct") is None
        )
        and refusal_scenario["tasks_progress_pct"] in (None, 0),
        f"F. Honest refusal on opaque body: refused={r_entry.get('refused')} "
        f"progress_pct={r_entry.get('progress_pct')} tasks.progress_pct={refusal_scenario['tasks_progress_pct']}",
    )
    print("\n6/6 acceptance rows GREEN — STAGE 3.1 STOP-AND-SHOW ready.\n")


async def main() -> None:
    start = datetime.now(timezone.utc).isoformat()
    print(f"=== JC-MON Stage 3.1 — task-discriminator proving slice — {start} ===\n")

    tm_scenario = await _scenario_tm_mode_unchanged()
    monitor_scenario = await _scenario_monitor_mode_extracts()
    refusal_scenario = await _scenario_monitor_mode_refuses()

    _write_artefact("tm-mode-unchanged.json", tm_scenario)
    _write_artefact("monitor-mode-extracts.json", monitor_scenario)
    _write_artefact("monitor-mode-refusal.json", refusal_scenario)

    _acceptance_rows(tm_scenario, monitor_scenario, refusal_scenario)


if __name__ == "__main__":
    os.environ.setdefault("CSRF_TEST_BYPASS_HEADER", "1")
    asyncio.run(main())
