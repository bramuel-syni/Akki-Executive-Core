#!/usr/bin/env python3
"""Phase 5.6.2 — FTT-001 real-assertion proving slice.

Canonical Spec : /app/memory/sprints/P5_22_csrf_wire_test_refresh.md
                 (Phase 5.6.x ledger; FTT-001 = THIN-ASSERTION repair)
Audit standard : /app/memory/audit/PHASE_5_6_1_CSRF_RIG_AUDIT.md
                 (CSRF-grade rig audit — both rails MUST exercise real
                 behaviour; positive control proves the fixture path is
                 not silently broken)
Sprint memo    : /app/memory/sprints/P5_6_2_ftt001_real_assertion.md

Replaces the original `try: pass` no-op in
`tests/test_phase_zz2_x.py::test_zz2_x_fixture_404_when_env_disabled`
with a real behavioural assertion driven through the actual chat-router
gating expression (line ~1695 of routers/chat.py):

    if fixture and os.environ.get("AKKI_CHAT_FIXTURES_ENABLED") == "1"
       and _is_admin:
        from services.solva_v2.chat_v2_fixtures import stream_fixture
        return StreamingResponse(stream_fixture(...), media_type=...)

Both rails are exercised through the in-process FastAPI app (no preview-
URL hop, no real LLM call). The fixture import is lazy (inside the if
block) so monkey-patching the module attribute on
`services.solva_v2.chat_v2_fixtures.stream_fixture` BEFORE the request
hits is sufficient — and reaching for that patched attribute is itself
proof the gate took the fixture branch.

For the env-disabled rail, the request falls through past the gating
into the Shield/LLM pipeline. To keep the slice deterministic (no
Anthropic call) we monkey-patch `mint_chat_outcome` to raise
`ShieldFailure`, which the router maps to a 503 envelope. The crucial
assertion is that the 503 body lacks every fixture-only marker
(`zz2_governance`, `__FIXTURE_BRANCH_INVOKED__`, fixture text) — i.e.
the gating BLOCKED the fixture branch.

The four checks:

  Rail 1 — NEGATIVE (env disabled)
  ────
   1. With `AKKI_CHAT_FIXTURES_ENABLED` unset and `?fixture=bias_anchoring`,
      the response is the synthetic 503 envelope from the LLM-fallthrough
      patch (NOT the sentinel-bearing fixture stream).
   2. The response body contains ZERO fixture-only markers
      (`__FIXTURE_BRANCH_INVOKED__`, `zz2_governance`, fixture text
      fragment).

  Rail 2 — POSITIVE control (env enabled)
  ────
   3. With `AKKI_CHAT_FIXTURES_ENABLED=1` and the same `?fixture=…`,
      the patched `stream_fixture` IS invoked and the response body
      contains the sentinel `__FIXTURE_BRANCH_INVOKED__`.
   4. Without (3) passing, rail 1 is half-blind — slice fails red so
      the audit caller knows the fixture path itself is not broken.

Exit codes:
  0 → all GREEN
  1 → at least one FAIL (Halt-and-Surface)
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "backend"))
sys.path.insert(0, str(REPO / "backend" / "tests"))

import conftest  # noqa: F401,E402  — loads .env + CSRF bypass shims

import httpx  # noqa: E402
from httpx import ASGITransport  # noqa: E402

import server  # noqa: E402
from core import db  # noqa: E402
from services.synisense.shield.exceptions import ShieldFailure  # noqa: E402
import services.solva_v2.chat_v2_fixtures as fixtures_mod  # noqa: E402
import services.synisense.shield.canonical as shield_canonical  # noqa: E402

ACTIVE_CONTEXT_HEADER = "X-Active-Context"
SENTINEL = "__FIXTURE_BRANCH_INVOKED__"
FIXTURE_NAME = "bias_anchoring"
FIXTURE_TEXT_FRAGMENT = "[anchoring"  # canonical marker inside fixture text

RESULTS: list[tuple[str, bool, str]] = []


def _record(name: str, ok: bool, detail: str = "") -> None:
    RESULTS.append((name, ok, detail))
    flag = "GREEN" if ok else "RED"
    print(f"  [{flag}] {name}: {detail}")


# ── Sentinel stand-ins ──────────────────────────────────────────────
async def _sentinel_stream_fixture(name: str, chat_id: str):
    """Replaces services.solva_v2.chat_v2_fixtures.stream_fixture for
    the duration of the slice. Yields a single SSE frame carrying the
    sentinel so a response-body grep proves the gate took this branch.
    """
    yield (
        "data: "
        + json.dumps({"type": "sentinel", "marker": SENTINEL, "fixture": name, "chat_id": chat_id})
        + "\n\n"
    )


async def _sentinel_mint_outcome(*args, **kwargs):
    """Replaces services.synisense.shield.canonical.mint_chat_outcome
    so the env-disabled rail terminates with a deterministic 503 body
    (`shield_unavailable`) instead of reaching the real LLM client.
    The router catches this and emits the 503 envelope — proving the
    request DID fall past the fixture gate.
    """
    raise ShieldFailure("synthetic_for_p562_slice", original=RuntimeError("synthetic"), surface="chat")


# ── Seed helpers ────────────────────────────────────────────────────
async def _seed_admin_account_and_chat() -> tuple[dict, dict]:
    """Inserts a throwaway superadmin account + chat row directly into
    Mongo (bypassing the HTTP signup/chat-create dance). Returns
    (account_doc, chat_doc); caller cleans both up at teardown.
    """
    acct_id = "p562-acct-" + uuid.uuid4().hex[:12]
    account_doc = {
        "id": acct_id,
        "email": f"{acct_id}@p562.local",
        "name": "P5.6.2 FTT-001 slice admin",
        "is_superadmin": True,
        "is_admin": True,
        "created_at": "2026-06-26T00:00:00+00:00",
    }
    chat_doc = {
        "id": "p562-chat-" + uuid.uuid4().hex[:12],
        "account_id": acct_id,
        "context_id": None,   # general chat — no X-Active-Context required
        "model_id": "claude-sonnet-4-5",
        "title": "p562-ftt001-slice",
        "shielding_policy": "auto",
        "status": "active",
        "created_at": "2026-06-26T00:00:00+00:00",
    }
    await db.chats.insert_one(dict(chat_doc))
    return account_doc, chat_doc


async def _purge(account_doc: dict, chat_doc: dict) -> None:
    try:
        await db.chats.delete_many({"id": chat_doc["id"]})
        await db.chat_messages.delete_many({"chat_id": chat_doc["id"]})
        await db.synisense_runs.delete_many({"chat_id": chat_doc["id"]})
        await db.audit_invariant_violations.delete_many({"chat_id": chat_doc["id"]})
        await db.chat_audit.delete_many({"chat_id": chat_doc["id"]})
    except Exception:
        pass


# ── Rail executors ──────────────────────────────────────────────────
async def _post_message(app, account_doc: dict, chat_doc: dict) -> httpx.Response:
    from core import get_current_account

    async def _override():
        return account_doc

    app.dependency_overrides[get_current_account] = _override
    try:
        transport = ASGITransport(app=app)
        async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
            return await client.post(
                f"/api/chats/{chat_doc['id']}/messages?fixture={FIXTURE_NAME}",
                json={"content": "ping from p562 slice"},
                headers={
                    "X-CSRF-Test-Bypass": "1",
                    # General chat — no X-Active-Context.
                },
                timeout=30.0,
            )
    finally:
        app.dependency_overrides.pop(get_current_account, None)


# ── Slice main ──────────────────────────────────────────────────────
async def main() -> int:
    # Snapshot env so we restore caller's state at teardown.
    saved_env = os.environ.pop("AKKI_CHAT_FIXTURES_ENABLED", None)
    saved_stream_fixture = fixtures_mod.stream_fixture
    saved_mint = shield_canonical.mint_chat_outcome

    fixtures_mod.stream_fixture = _sentinel_stream_fixture
    shield_canonical.mint_chat_outcome = _sentinel_mint_outcome

    account_doc, chat_doc = await _seed_admin_account_and_chat()
    app = server.app

    try:
        # ── Rail 1: env DISABLED ────────────────────────────────────
        os.environ.pop("AKKI_CHAT_FIXTURES_ENABLED", None)
        r1 = await _post_message(app, account_doc, chat_doc)
        r1_body = r1.text or ""

        # Check 1 — gate BLOCKED fixture branch (status NOT 200 with sentinel).
        check1_ok = (r1.status_code == 503) and ("shield_unavailable" in r1_body)
        _record(
            "rail1_gating_blocked_fixture_branch",
            check1_ok,
            f"status={r1.status_code} body_head={r1_body[:120]!r}",
        )

        # Check 2 — zero fixture-only markers in the response body.
        markers_present = [
            m for m in (SENTINEL, '"zz2_governance"', FIXTURE_TEXT_FRAGMENT)
            if m in r1_body
        ]
        check2_ok = len(markers_present) == 0
        _record(
            "rail1_no_fixture_markers_present",
            check2_ok,
            f"unexpected_markers={markers_present!r}",
        )

        # ── Rail 2: env ENABLED (positive control) ──────────────────
        os.environ["AKKI_CHAT_FIXTURES_ENABLED"] = "1"
        r2 = await _post_message(app, account_doc, chat_doc)
        r2_body = r2.text or ""

        # Check 3 — fixture branch DID fire (sentinel present, 200).
        check3_ok = (r2.status_code == 200) and (SENTINEL in r2_body)
        _record(
            "rail2_positive_control_fixture_invoked",
            check3_ok,
            f"status={r2.status_code} sentinel_present={SENTINEL in r2_body} body_head={r2_body[:120]!r}",
        )

        # Check 4 — Shield-fallthrough did NOT run (no `shield_unavailable`
        # in r2). Confirms the env flag is the actual discriminator.
        check4_ok = "shield_unavailable" not in r2_body
        _record(
            "rail2_did_not_fall_through_to_shield",
            check4_ok,
            f"shield_unavailable_in_body={('shield_unavailable' in r2_body)}",
        )

    finally:
        await _purge(account_doc, chat_doc)
        # Restore patches + env.
        fixtures_mod.stream_fixture = saved_stream_fixture
        shield_canonical.mint_chat_outcome = saved_mint
        if saved_env is None:
            os.environ.pop("AKKI_CHAT_FIXTURES_ENABLED", None)
        else:
            os.environ["AKKI_CHAT_FIXTURES_ENABLED"] = saved_env

    print()
    failed = [n for n, ok, _ in RESULTS if not ok]
    if failed:
        print(f"FAIL: {len(failed)} check(s) failed: {failed}")
        return 1
    print(f"OK: {len(RESULTS)}/{len(RESULTS)} checks GREEN")
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
