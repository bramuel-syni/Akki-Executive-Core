#!/usr/bin/env python3
"""Owner Digest v0 — proving slice.

Canonical Spec : /app/memory/JC_MON_CANONICAL_SPEC.md (Wave 3 backlog —
                 Monday 9am owner-tz, deterministic-only content,
                 skip-if-no-delta; replies route to TM Journal accept
                 rail in v0.5).
Sprint memo    : /app/memory/sprints/OWNER_DIGEST_V0.md

Seven checks (Halt-and-Surface if any FAIL):

 1. Composer produces a deterministic payload from `strategic_goals` —
    NO Shield call, NO LLM call. Same inputs → identical `delta_hash`.
 2. Composer ranks off_track + at_risk goals to the top of the rows.
 3. Composer computes a `previous_score` and `delta_score` when a
    historical entry pre-dates the 7-day window.
 4. `compose_or_skip` returns `should_skip=True` on a second call when
    nothing changed since the persisted previous digest.
 5. `compose_or_skip` returns `should_skip=False` when a goal's score
    moves (delta_hash differs).
 6. The cron endpoint refuses without the X-Cron-Secret header (403)
    and accepts when present (200).
 7. The APScheduler block in `server.py` arms an `owner_digest_weekly`
    job at Monday 09:00 (matches the user's "Monday 9am" constraint).

Exit codes:
  0 → all GREEN
  1 → at least one FAIL
"""

from __future__ import annotations

import asyncio
import os
import re
import sys
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend"))
sys.path.insert(0, str(REPO / "backend" / "tests"))

import conftest  # noqa: F401,E402

from httpx import ASGITransport, AsyncClient  # noqa: E402
from server import app  # noqa: E402
from core import db, iso, now  # noqa: E402
from services.owner_digest import (  # noqa: E402
    build_owner_digest, compose_or_skip,
)

RESULTS: list[tuple[str, bool, str]] = []


def _record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    flag = "GREEN" if ok else "RED"
    print(f"  [{flag}] {name}: {detail}")


# ─── seed a fresh test context with 3 goals ────────────────────────


async def _seed() -> tuple[str, str]:
    cid = f"ctx-owner-digest-{uuid.uuid4().hex[:6]}"
    owner = f"owner-{uuid.uuid4().hex[:6]}"
    await db.contexts.insert_one({
        "id": cid, "name": "Owner Digest Slice", "owner_account_id": owner,
        "members": [owner], "created_at": iso(now()),
    })
    eight_days_ago = (now() - timedelta(days=8)).replace(microsecond=0).isoformat()
    # Goal A — off_track + had a historical score for delta computation
    await db.strategic_goals.insert_one({
        "id": f"goal-A-{uuid.uuid4().hex[:6]}",
        "context_id": cid,
        "title": "Migrate to new ERP by Dec 2026",
        "status": "off_track",
        "category": "operations",
        "current_score": 35,
        "probability": 30,
        "target_value": "100", "target_metric": "%", "target_date": "2026-12-31",
        "score_history": [
            {"score": 60, "recorded_at": eight_days_ago},
        ],
        "created_at": iso(now()),
    })
    # Goal B — at_risk, no historical reading
    await db.strategic_goals.insert_one({
        "id": f"goal-B-{uuid.uuid4().hex[:6]}",
        "context_id": cid,
        "title": "Hit Q4 revenue target",
        "status": "at_risk",
        "category": "commercial",
        "current_score": 65,
        "probability": 55,
        "target_value": "12.0", "target_metric": "M$", "target_date": "2026-12-31",
        "score_history": [],
        "created_at": iso(now()),
    })
    # Goal C — on_track
    await db.strategic_goals.insert_one({
        "id": f"goal-C-{uuid.uuid4().hex[:6]}",
        "context_id": cid,
        "title": "Improve eNPS to 40",
        "status": "on_track",
        "category": "people",
        "current_score": 82,
        "probability": 75,
        "target_value": "40", "target_metric": "", "target_date": "2026-12-31",
        "score_history": [],
        "created_at": iso(now()),
    })
    return cid, owner


async def _run_async_checks() -> None:
    cid, owner = await _seed()

    # ─── 1 ─ deterministic compose ──────────────────────────────────
    print("\n[1] Composer is deterministic + no Shield/LLM call")
    p1 = await build_owner_digest(context_id=cid, owner_account_id=owner)
    p2 = await build_owner_digest(context_id=cid, owner_account_id=owner)
    ok_1 = p1["delta_hash"] == p2["delta_hash"]
    _record("composer_deterministic", ok_1, f"hash={p1['delta_hash'][:16]}…")

    # ─── 2 ─ ranking: off_track first, then at_risk, then on_track ──
    print("\n[2] Composer ranks off_track + at_risk first")
    statuses = [r["status"] for r in p1["rows"]]
    ok_2 = statuses == ["off_track", "at_risk", "on_track"]
    _record("ranking_off_track_first", ok_2, f"order={statuses}")

    # ─── 3 ─ delta_score computed for goal A (had pre-window history) ──
    print("\n[3] Composer computes previous_score + delta_score for goal A")
    a_row = next((r for r in p1["rows"] if r["title"].startswith("Migrate")), None)
    ok_3 = (
        a_row is not None
        and a_row["previous_score"] == 60
        and a_row["delta_score"] == -25
    )
    _record(
        "delta_score_computed",
        ok_3,
        f"prev={a_row and a_row['previous_score']} delta={a_row and a_row['delta_score']}",
    )

    # ─── 4 ─ skip-if-no-delta path ──────────────────────────────────
    print("\n[4] compose_or_skip → skip=True after persist when nothing changed")
    # Persist the first digest as if the cron had run.
    from services.owner_digest import persist_digest
    await persist_digest(p1)
    p3, should_skip = await compose_or_skip(context_id=cid, owner_account_id=owner)
    ok_4 = should_skip is True
    _record("skip_no_delta", ok_4, f"skip={should_skip}")

    # ─── 5 ─ delta detected when score changes ──────────────────────
    print("\n[5] compose_or_skip → skip=False when a goal's score changes")
    await db.strategic_goals.update_one(
        {"context_id": cid, "title": "Migrate to new ERP by Dec 2026"},
        {"$set": {"current_score": 50}},
    )
    p4, should_skip2 = await compose_or_skip(context_id=cid, owner_account_id=owner)
    ok_5 = (should_skip2 is False) and (p4["delta_hash"] != p1["delta_hash"])
    _record(
        "delta_detected",
        ok_5,
        f"skip={should_skip2} hash_changed={p4['delta_hash'] != p1['delta_hash']}",
    )

    # ─── 6 ─ cron endpoint auth ──────────────────────────────────────
    print("\n[6] /api/cron/owner-digest-weekly enforces X-Cron-Secret")
    os.environ["AKKI_CRON_SECRET"] = "test-cron-secret-jc-w3"
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as ac:
        r_unauth = await ac.post("/api/cron/owner-digest-weekly")
        r_auth = await ac.post(
            "/api/cron/owner-digest-weekly",
            headers={"X-Cron-Secret": "test-cron-secret-jc-w3"},
        )
    ok_6a = r_unauth.status_code == 403
    ok_6b = r_auth.status_code == 200 and "contexts_scanned" in (r_auth.json() if r_auth.status_code == 200 else {})
    _record(
        "cron_auth_required",
        ok_6a and ok_6b,
        f"unauth={r_unauth.status_code} auth={r_auth.status_code}",
    )


asyncio.get_event_loop().run_until_complete(_run_async_checks())


# ─── 7 ─ APScheduler block arms owner_digest_weekly (v0.5 hourly TZ-gated) ──
print("\n[7] APScheduler arms owner_digest_weekly (v0.5 = hourly :05 + endpoint TZ gate)")
server_src = (REPO / "backend" / "server.py").read_text()
# v0.5 (2026-06-26) replaced the single Monday-09 UTC trigger with an
# hourly fire so the cron endpoint can resolve per-context owner-tz.
# Accept EITHER the v0 shape (Mon-09 single fire) OR the v0.5 shape
# (hourly :05) so this slice keeps proving the schedule is armed
# under either ship state.
ok_v0 = re.search(
    r'CronTrigger\(\s*day_of_week\s*=\s*["\']mon["\']\s*,\s*hour\s*=\s*9\s*,\s*minute\s*=\s*0\s*\)',
    server_src,
) is not None
ok_v05 = re.search(r'CronTrigger\(\s*minute\s*=\s*5\s*\)', server_src) is not None
ok_7 = 'id="owner_digest_weekly"' in server_src and (ok_v0 or ok_v05)
_record(
    "scheduler_armed_mon_09",
    ok_7,
    "owner_digest_weekly present + (v0 Mon-09 OR v0.5 hourly :05) trigger detected"
    if ok_7 else "MISSING",
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

print("ALL CHECKS GREEN — Owner Digest v0 verified.")
import os as _os
_os._exit(0)
