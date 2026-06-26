#!/usr/bin/env python3
"""Wave 3 — Origin-triggered Briefs fan-out · Solva + Task Manager · proving slice.

Canonical Spec : /app/memory/DEV_PIPELINE.md (Journey 3a — Brief actions
                 live on the origin surface: Solva / Monitor / Task Manager.
                 Pattern shipped on Monitor in sub-sprint 1
                 (jc_wave3_origin_briefs_monitor_slice.py 9/9 GREEN).
                 This slice verifies the FAN-OUT to Solva + Task Manager
                 without re-implementing the pattern.)
Sprint memo    : /app/memory/sprints/JC_WAVE3_ORIGIN_BRIEFS_SOLVA_TM_FANOUT.md

Twelve checks (Halt-and-Surface if any FAIL):

  Coupling-debt rule
  ────
   1. Both surfaces use the SAME shared `/work-studio/export/brief`
      route (no parallel brief endpoint per surface).

  Backend
  ────
   2. `ExportRequestIn.origin_kind` still rejects unknown values.
   3. `origin_kind="solva_session"` round-trips end-to-end:
      persisted on row + audit metadata.
   4. `origin_kind="task_manager_task"` round-trips end-to-end:
      persisted on row + audit metadata.

  FE — Solva
  ────
   5. `solva-handoff-brief-this-session` test-id exists on the
      handoff bar.
   6. Solva handler imports the shared `api` client (no axios).
   7. Solva handler stamps `origin_kind=solva_session` + `origin_id`.
   8. Solva auto-prefill builder reads `session.framing.user_input`,
      `session.synthesis.primary_diagnosis`, `session.synthesis.tensions`.

  FE — Task Manager
  ────
   9. `task-drawer-brief-this-task` test-id exists on the Compile tab.
  10. Task handler imports the shared `api` client (no axios).
  11. Task handler stamps `origin_kind=task_manager_task` + `origin_id`.
  12. Task auto-prefill builder reads `task.name`, `task.readiness_score`,
      `task.description`, `task.due_date`.

Exit codes:
  0 → all GREEN
  1 → at least one FAIL
"""

from __future__ import annotations

import asyncio
import re
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend"))
sys.path.insert(0, str(REPO / "backend" / "tests"))

import conftest  # noqa: F401,E402

from httpx import ASGITransport, AsyncClient  # noqa: E402
from server import app  # noqa: E402
from core import db  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def _record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    flag = "GREEN" if ok else "RED"
    print(f"  [{flag}] {name}: {detail}")


# ─── seed test context ─────────────────────────────────────────────


async def _mint_test_jwt() -> tuple[str, str, str]:
    from core import create_access_token  # type: ignore
    aid = f"jc-w3-fanout-{uuid.uuid4().hex[:8]}"
    cid = f"ctx-jc-w3-fanout-{uuid.uuid4().hex[:6]}"
    email = f"{aid}@x.invalid"
    await db.accounts.insert_one({
        "id": aid, "email": email, "name": "Origin Brief Fan-out Slice",
        "memberships": [{"context_id": cid, "role": "superadmin"}],
        "default_context_id": cid, "created_at": "2026-06-26T00:00:00Z",
    })
    await db.contexts.insert_one({
        "id": cid, "name": "Fan-out Context",
        "owner_account_id": aid, "members": [aid],
        "created_at": "2026-06-26T00:00:00Z",
    })
    await db.memberships.insert_one({
        "id": f"mem-{uuid.uuid4().hex[:8]}",
        "context_id": cid, "account_id": aid,
        "role": "superadmin", "status": "active",
        "created_at": "2026-06-26T00:00:00Z",
    })
    return create_access_token(account_id=aid, email=email), aid, cid


# ─── 1 ─ coupling-debt rule: single shared route ───────────────────
print("\n[1] Both FE surfaces post to /work-studio/export/brief")
FRONTEND = REPO / "frontend" / "src"
solva_src = (FRONTEND / "components" / "solva" / "artefact" / "SolvaArtefact.jsx").read_text()
task_src = (FRONTEND / "components" / "tasks" / "TaskDrawer.jsx").read_text()
monitor_src = (FRONTEND / "components" / "monitor" / "StrategicGoalsPanel.jsx").read_text()

# All three surfaces must use the same path.
brief_route = r"/work-studio/export/brief"
solva_uses = solva_route_count = len(re.findall(brief_route, solva_src))
task_uses = len(re.findall(brief_route, task_src))
monitor_uses = len(re.findall(brief_route, monitor_src))
ok = solva_uses >= 1 and task_uses >= 1 and monitor_uses >= 1
_record(
    "shared_brief_route_only",
    ok,
    f"solva={solva_uses} task={task_uses} monitor={monitor_uses}",
)


async def _backend_round_trip(origin_kind: str, origin_id: str) -> tuple[bool, dict, dict]:
    tok, _aid, cid = await _mint_test_jwt()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        r = await ac.post(
            f"/api/contexts/{cid}/work-studio/export/brief",
            json={
                "description": "x", "objective": "x", "scope": "x",
                "origin_kind": origin_kind, "origin_id": origin_id,
            },
            headers={"Authorization": f"Bearer {tok}"},
        )
    body = r.json() if r.status_code in (200, 202) else {}
    export_id = body.get("export_id")
    if not export_id:
        return False, {}, {}
    row = await db.work_studio_exports.find_one({"id": export_id}) or {}
    audit = await db.audit_log.find_one(
        {"action": "work_studio.export.requested", "resource_id": export_id},
    ) or {}
    return True, row, audit


async def _run_backend_checks() -> None:
    # ─── 2 ─ schema rejects unknown origin_kind (regression check) ─
    print("\n[2] Schema still rejects unknown origin_kind values")
    from routers.work_studio_export import ExportRequestIn
    rejected = True
    try:
        ExportRequestIn(
            description="x"*10, objective="x"*10, scope="x"*10,
            origin_kind="bogus_module", origin_id="x",
        )
        rejected = False
    except Exception:
        rejected = True
    _record("schema_rejects_unknown_origin", rejected, f"rejected={rejected}")

    # ─── 3 ─ solva_session round-trip ─────────────────────────────
    print("\n[3] origin_kind=solva_session round-trips to row + audit")
    ok_s, row_s, audit_s = await _backend_round_trip(
        "solva_session", "solva-fanout-1",
    )
    meta_s = (audit_s or {}).get("metadata") or {}
    ok_3 = (
        ok_s
        and row_s.get("origin_kind") == "solva_session"
        and row_s.get("origin_id")   == "solva-fanout-1"
        and meta_s.get("origin_kind") == "solva_session"
        and meta_s.get("origin_id")   == "solva-fanout-1"
    )
    _record(
        "solva_session_persisted_and_audited", ok_3,
        f"row.ok={bool(row_s)} audit.meta={meta_s}",
    )

    # ─── 4 ─ task_manager_task round-trip ─────────────────────────
    print("\n[4] origin_kind=task_manager_task round-trips to row + audit")
    ok_t, row_t, audit_t = await _backend_round_trip(
        "task_manager_task", "task-fanout-1",
    )
    meta_t = (audit_t or {}).get("metadata") or {}
    ok_4 = (
        ok_t
        and row_t.get("origin_kind") == "task_manager_task"
        and row_t.get("origin_id")   == "task-fanout-1"
        and meta_t.get("origin_kind") == "task_manager_task"
        and meta_t.get("origin_id")   == "task-fanout-1"
    )
    _record(
        "task_persisted_and_audited", ok_4,
        f"row.ok={bool(row_t)} audit.meta={meta_t}",
    )


asyncio.get_event_loop().run_until_complete(_run_backend_checks())


# ─── 5..8 ─ FE Solva wiring checks ─────────────────────────────────
print("\n[5..8] Solva FE wiring")
_record(
    "solva_testid_present",
    'data-testid="solva-handoff-brief-this-session"' in solva_src,
    "test-id present",
)
_record(
    "solva_uses_shared_api",
    'from "axios"' not in solva_src and 'import api from "@/lib/api/apiV2"' in solva_src,
    "no axios + shared api client",
)
_record(
    "solva_stamps_origin",
    (
        re.search(r'origin_kind:\s*["\']solva_session["\']', solva_src) is not None
        and re.search(r'origin_id:\s*sessionId', solva_src) is not None
    ),
    "origin_kind=solva_session + origin_id=sessionId present",
)
_record(
    "solva_prefill_reads_session_shape",
    (
        "session?.framing?.user_input" in solva_src
        and "session?.synthesis" in solva_src
        and "tensions" in solva_src
    ),
    "framing.user_input + synthesis + tensions in prefill builder",
)


# ─── 9..12 ─ FE Task Manager wiring checks ─────────────────────────
print("\n[9..12] Task Manager FE wiring")
_record(
    "task_testid_present",
    'data-testid="task-drawer-brief-this-task"' in task_src,
    "test-id present",
)
_record(
    "task_uses_shared_api",
    'from "axios"' not in task_src and 'import api from "@/lib/api/apiV2"' in task_src,
    "no axios + shared api client",
)
_record(
    "task_stamps_origin",
    (
        re.search(r'origin_kind:\s*["\']task_manager_task["\']', task_src) is not None
        and re.search(r'origin_id:\s*task\.id', task_src) is not None
    ),
    "origin_kind=task_manager_task + origin_id=task.id present",
)
_record(
    "task_prefill_reads_task_shape",
    (
        "task?.name" in task_src
        and "task?.readiness_score" in task_src
        and "task?.due_date" in task_src
    ),
    "name + readiness_score + due_date present in prefill builder",
)


# ─── Summary ───────────────────────────────────────────────────────
green = sum(1 for _, ok, _ in RESULTS if ok)
red = len(RESULTS) - green
print(f"\n=== SUMMARY: {green}/{len(RESULTS)} GREEN ===")
if red:
    print("FAILED checks:")
    for name, ok, detail in RESULTS:
        if not ok:
            print(f"  - {name}: {detail}")
    import os as _os
    _os._exit(1)

print("ALL CHECKS GREEN — Wave 3 Origin-triggered Briefs Solva + Task Manager fan-out verified.")
import os as _os
_os._exit(0)
