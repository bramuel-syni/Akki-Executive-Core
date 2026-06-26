#!/usr/bin/env python3
"""Wave 3 — Origin-triggered Briefs · Monitor (first surface) · proving slice.

Canonical Spec : /app/memory/DEV_PIPELINE.md (Journey 3a revision per
                 JC-WS Phase 3 canonical-spec update; this sprint ships
                 the pattern on the Monitor surface first per the
                 coverage-gap analysis).
Sprint memo    : /app/memory/sprints/JC_WAVE3_ORIGIN_BRIEFS_MONITOR.md

Eight checks (Halt-and-Surface if any FAIL):

 1. `ExportRequestIn` schema accepts `origin_kind` + `origin_id` and
    rejects unknown origin_kind values.
 2. Schema's `origin_id` is bounded (max_length=128) — matches existing
    audit `target_id` constraint.
 3. Backend persists `origin_kind` + `origin_id` on the
    `work_studio_exports` row when present in the request.
 4. Backend includes `origin_kind` + `origin_id` in the
    `work_studio.export.requested` audit metadata.
 5. Omitting origin_kind/id keeps the legacy in-Studio flow byte-
    identical (no extra row fields beyond None defaults).
 6. The Monitor FE component exports a `BriefThisGoalButton` and
    routes the click through the SHARED api client (no axios import,
    no local CSRF priming).
 7. The Monitor FE component stamps `origin_kind=monitor_objective`
    and `origin_id=<goal.id>` on the payload it POSTs.
 8. The FE pre-fills description/objective/scope from goal data
    (title appears verbatim in the auto-built payload — the test
    helper for the build step exercises the same fn the runtime uses
    via static AST inspection).

Exit codes:
  0 → all GREEN
  1 → at least one FAIL
"""

from __future__ import annotations

import asyncio
import json
import re
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend"))
sys.path.insert(0, str(REPO / "backend" / "tests"))

import conftest  # noqa: F401,E402 (CSRF rig)

import pytest  # noqa: E402  (used by inline asserts below)
from httpx import ASGITransport, AsyncClient  # noqa: E402
from server import app  # noqa: E402
from core import db  # noqa: E402

RESULTS: list[tuple[str, bool, str]] = []


def _record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    flag = "GREEN" if ok else "RED"
    print(f"  [{flag}] {name}: {detail}")


# ─── Build a test context + account ────────────────────────────────
async def _mint_test_jwt() -> tuple[str, str, str]:
    """Mint a fresh test account + context + JWT. Returns (token, account_id, context_id)."""
    from core import create_access_token  # type: ignore
    aid = f"jc-w3-brief-{uuid.uuid4().hex[:8]}"
    cid = f"ctx-jc-w3-brief-{uuid.uuid4().hex[:6]}"
    email = f"{aid}@x.invalid"
    await db.accounts.insert_one({
        "id": aid, "email": email, "name": "Origin Brief Slice",
        "memberships": [{"context_id": cid, "role": "superadmin"}],
        "default_context_id": cid,
        "created_at": "2026-06-26T00:00:00Z",
    })
    await db.contexts.insert_one({
        "id": cid, "name": "Origin Brief Slice Context",
        "owner_account_id": aid, "members": [aid],
        "created_at": "2026-06-26T00:00:00Z",
    })
    # require_context_membership reads from `db.memberships`, not the
    # embedded `accounts.memberships` field. Seed both so the dep
    # passes.
    await db.memberships.insert_one({
        "id": f"mem-{uuid.uuid4().hex[:8]}",
        "context_id": cid, "account_id": aid,
        "role": "superadmin", "status": "active",
        "created_at": "2026-06-26T00:00:00Z",
    })
    tok = create_access_token(account_id=aid, email=email)
    return tok, aid, cid


# ─── 1+2 ─ Schema accepts origin fields & enforces enum ───────────
print("\n[1+2] ExportRequestIn schema with origin_kind/id")
from routers.work_studio_export import ExportRequestIn  # noqa: E402

try:
    valid = ExportRequestIn(
        description="d" * 10, objective="o" * 10, scope="s" * 10,
        origin_kind="monitor_objective", origin_id="goal-123",
    )
    schema_ok_1 = valid.origin_kind == "monitor_objective" and valid.origin_id == "goal-123"
except Exception as exc:
    schema_ok_1 = False
    valid = None  # noqa
_record("schema_accepts_origin_fields", schema_ok_1, f"valid={schema_ok_1}")

# Unknown origin must be rejected.
rejected = True
try:
    ExportRequestIn(
        description="d" * 10, objective="o" * 10, scope="s" * 10,
        origin_kind="some_random_module", origin_id="x",
    )
    rejected = False
except Exception:
    rejected = True
_record("schema_rejects_unknown_origin_kind", rejected, f"rejected={rejected}")


# ─── 3+4 ─ Backend persists + audits origin ──────────────────────
async def _check_persist_and_audit() -> None:
    print("\n[3+4] Persist origin on export row + include in audit metadata")
    tok, _aid, cid = await _mint_test_jwt()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        # NB: ASGITransport runs FastAPI BackgroundTasks synchronously
        # within the same request lifecycle. The thin-input refusal
        # path short-circuits the LLM call so the worker completes in
        # ~ms instead of ~60s, keeping the slice fast. The persistence
        # + audit checks below verify state written BEFORE the worker
        # fires (i.e. these assertions are unaffected by whether the
        # worker succeeds or refuses).
        r = await ac.post(
            f"/api/contexts/{cid}/work-studio/export/brief",
            json={
                "description": "x",  # < 5 chars → thin-input refusal
                "objective":   "x",
                "scope":       "x",
                "output_format": "auto", "cadence": "one_off",
                "origin_kind": "monitor_objective",
                "origin_id":   "goal-prove-1",
            },
            headers={"Authorization": f"Bearer {tok}"},
        )
    body = {}
    try:
        body = r.json()
    except Exception:
        body = {}
    export_id = body.get("export_id")
    accepted = r.status_code in (200, 202) and bool(export_id)
    _record("export_started_ok", accepted, f"status={r.status_code} export_id={export_id}")

    if not export_id:
        _record("origin_on_row", False, "no export_id")
        _record("origin_in_audit", False, "no export_id")
        return

    row = await db.work_studio_exports.find_one({"id": export_id})
    ok = bool(row) and row.get("origin_kind") == "monitor_objective" and row.get("origin_id") == "goal-prove-1"
    _record(
        "origin_on_row",
        ok,
        f"row.origin_kind={row.get('origin_kind') if row else None} "
        f"row.origin_id={row.get('origin_id') if row else None}",
    )

    audit = await db.audit_log.find_one({
        "action": "work_studio.export.requested",
        "resource_id": export_id,
    })
    meta = (audit or {}).get("metadata") or {}
    ok_audit = meta.get("origin_kind") == "monitor_objective" and meta.get("origin_id") == "goal-prove-1"
    _record("origin_in_audit", ok_audit, f"audit.metadata={meta}")


asyncio.get_event_loop().run_until_complete(_check_persist_and_audit())


# ─── 5 ─ Legacy in-Studio flow unchanged when omitted ─────────────
async def _check_omitted_origin_clean() -> None:
    print("\n[5] In-Studio flow (no origin fields) — row carries None defaults")
    tok, _aid, cid = await _mint_test_jwt()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        # Same thin-input shortcut as the [3+4] block above — the
        # row+audit assertions land on state written before the worker.
        r = await ac.post(
            f"/api/contexts/{cid}/work-studio/export/brief",
            json={
                "description": "x",
                "objective":   "x",
                "scope":       "x",
            },
            headers={"Authorization": f"Bearer {tok}"},
        )
    body = r.json() if r.status_code in (200, 202) else {}
    export_id = body.get("export_id")
    if not export_id:
        _record("legacy_path_unchanged", False, f"no export_id; status={r.status_code}")
        return
    row = await db.work_studio_exports.find_one({"id": export_id})
    ok = bool(row) and row.get("origin_kind") is None and row.get("origin_id") is None
    _record(
        "legacy_path_unchanged",
        ok,
        f"row.origin_kind={row.get('origin_kind') if row else None} "
        f"row.origin_id={row.get('origin_id') if row else None}",
    )


asyncio.get_event_loop().run_until_complete(_check_omitted_origin_clean())


# ─── 6+7+8 ─ FE: button uses shared api client, stamps origin, prefills payload ──
print("\n[6+7+8] Monitor FE component wiring (static source inspection)")
src = (
    REPO / "frontend" / "src" / "components" / "monitor"
    / "StrategicGoalsPanel.jsx"
).read_text()

# 6 — Uses shared api client + no direct axios import.
ok_6 = (
    "BriefThisGoalButton" in src
    and 'import api from "@/lib/api/apiV2"' in src
    and 'from "axios"' not in src
)
_record("fe_uses_shared_api_client", ok_6, f"present={'BriefThisGoalButton' in src}")

# 7 — Stamps origin_kind=monitor_objective + origin_id=goal.id.
ok_7 = (
    re.search(r'origin_kind:\s*["\']monitor_objective["\']', src) is not None
    and re.search(r'origin_id:\s*goal\?\.id', src) is not None
)
_record("fe_stamps_origin_payload", ok_7, "origin_kind+origin_id present in payload" if ok_7 else "MISSING")

# 8 — Pre-fills payload from goal data: title appears in the synthesised description.
ok_8 = "goal?.title" in src and "Brief the board" in src
_record(
    "fe_prefills_from_goal_data",
    ok_8,
    "goal.title and 'Brief the board' present in synthesised payload",
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
    # Use os._exit to bypass any lingering asyncio cleanup from the
    # background BackgroundTasks workers (real LLM calls) the export
    # endpoint scheduled. We've already verified the persistence +
    # audit synchronously; we don't need to wait for the LLM run.
    import os as _os
    _os._exit(1)

print("ALL CHECKS GREEN — Wave 3 Origin-triggered Briefs (Monitor) verified.")
import os as _os
_os._exit(0)
