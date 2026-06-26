"""Phase ZZ.2.x (2026-02 fork-resume v2) — deterministic chat fixtures
gating + Playwright probe correctness.
"""
from __future__ import annotations
import os
from pathlib import Path

import pytest
from httpx import AsyncClient, ASGITransport

REPO = Path(__file__).resolve().parent.parent.parent
FIXTURES_PY = REPO / "backend" / "services" / "solva_v2" / "chat_v2_fixtures.py"
CHAT_PY = REPO / "backend" / "routers" / "chat.py"


def test_zz2_x_fixture_module_carries_five_fixtures():
    src = FIXTURES_PY.read_text(encoding="utf-8")
    for k in ["unsourced_number", "bias_anchoring",
              "recommendation_with_counter", "escalation_trigger",
              "clean_response"]:
        assert f'"{k}"' in src, f"Missing fixture key {k!r}"
    # SSE shape: terminal `message` event carries `zz2_governance`
    assert '"zz2_governance": f["gov"]' in src


def test_zz2_x_chat_router_gates_fixture_mode():
    src = CHAT_PY.read_text(encoding="utf-8")
    # Env-var gate + admin check
    assert 'os.environ.get("AKKI_CHAT_FIXTURES_ENABLED") == "1"' in src
    assert "is_superadmin" in src and "is_admin" in src
    assert "from services.solva_v2.chat_v2_fixtures import stream_fixture" in src
    # Non-admin fixture request returns 404
    assert 'if fixture and not _is_admin:' in src


@pytest.fixture
def app():
    import importlib, server
    importlib.reload(server)
    return server.app


# ── Phase 5.6.2 (FTT-001) — real-assertion repair, 2026-06-26 ─────────
# Original body was `try: pass` (THIN-ASSERTION FLAGGED-FALSE-GREEN in
# PHASE_5_6_1_CSRF_RIG_AUDIT.md). The replacement below exercises BOTH
# rails of the gating expression at runtime through the in-process
# FastAPI app:
#
#   Rail 1 (NEGATIVE): env unset + `?fixture=…` → the gate MUST NOT
#       route into the fixture stream. We monkey-patch
#       `mint_chat_outcome` to raise `ShieldFailure` so the fall-
#       through deterministically lands on the 503 envelope (no real
#       LLM call). The body MUST contain zero fixture-only markers.
#
#   Rail 2 (POSITIVE CONTROL): env=1 + `?fixture=…` → the gate MUST
#       route into the fixture stream. We monkey-patch
#       `services.solva_v2.chat_v2_fixtures.stream_fixture` to emit a
#       sentinel string and assert the sentinel is present in the
#       response body. Without this rail the negative rail is half-
#       blind (CSRF-grade audit standard).
#
# The proving-slice equivalent lives at
# `/app/backend/scripts/jc_p562_ftt001_slice.py`.
_P562_SENTINEL = "__FIXTURE_BRANCH_INVOKED__"


async def _p562_sentinel_stream_fixture(name: str, chat_id: str):
    import json as _json
    yield (
        "data: "
        + _json.dumps({"type": "sentinel", "marker": _P562_SENTINEL,
                       "fixture": name, "chat_id": chat_id})
        + "\n\n"
    )


async def _p562_sentinel_mint_outcome(*_args, **_kwargs):
    from services.synisense.shield.exceptions import ShieldFailure
    raise ShieldFailure("synthetic_for_ftt001",
                        original=RuntimeError("synthetic"), surface="chat")


@pytest.mark.asyncio
async def test_zz2_x_fixture_404_when_env_disabled(app):
    """Phase 5.6.2 FTT-001 — env-disabled rail MUST NOT route into the
    deterministic fixture stream; positive control proves the fixture
    path itself is healthy."""
    import uuid as _uuid
    import services.solva_v2.chat_v2_fixtures as _fixtures_mod
    import services.synisense.shield.canonical as _shield_canonical
    from core import db, get_current_account

    saved_env = os.environ.pop("AKKI_CHAT_FIXTURES_ENABLED", None)
    saved_stream = _fixtures_mod.stream_fixture
    saved_mint = _shield_canonical.mint_chat_outcome
    _fixtures_mod.stream_fixture = _p562_sentinel_stream_fixture
    _shield_canonical.mint_chat_outcome = _p562_sentinel_mint_outcome

    acct_id = "ftt001-acct-" + _uuid.uuid4().hex[:12]
    chat_id = "ftt001-chat-" + _uuid.uuid4().hex[:12]
    admin_doc = {
        "id": acct_id, "email": f"{acct_id}@p562.local",
        "name": "FTT-001 admin", "is_superadmin": True, "is_admin": True,
        "created_at": "2026-06-26T00:00:00+00:00",
    }
    await db.chats.insert_one({
        "id": chat_id, "account_id": acct_id, "context_id": None,
        "model_id": "claude-sonnet-4-5", "title": "ftt001-zz2x",
        "shielding_policy": "auto", "status": "active",
        "created_at": "2026-06-26T00:00:00+00:00",
    })

    async def _override():
        return admin_doc

    app.dependency_overrides[get_current_account] = _override

    try:
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as c:
            # ── Rail 1: env disabled ──────────────────────────────
            os.environ.pop("AKKI_CHAT_FIXTURES_ENABLED", None)
            r1 = await c.post(
                f"/api/chats/{chat_id}/messages?fixture=bias_anchoring",
                json={"content": "ftt001 negative rail"},
                headers={"X-CSRF-Test-Bypass": "1"},
                timeout=30.0,
            )
            r1_body = r1.text or ""
            assert r1.status_code == 503, \
                f"rail1 expected 503 from shield-fallthrough, got {r1.status_code}: {r1_body[:200]}"
            assert "shield_unavailable" in r1_body, \
                f"rail1 expected shield_unavailable envelope, got: {r1_body[:200]}"
            for marker in (_P562_SENTINEL, '"zz2_governance"', "[anchoring"):
                assert marker not in r1_body, \
                    f"rail1 must NOT carry fixture marker {marker!r}; body={r1_body[:200]}"

            # ── Rail 2: env enabled (positive control) ───────────
            os.environ["AKKI_CHAT_FIXTURES_ENABLED"] = "1"
            r2 = await c.post(
                f"/api/chats/{chat_id}/messages?fixture=bias_anchoring",
                json={"content": "ftt001 positive rail"},
                headers={"X-CSRF-Test-Bypass": "1"},
                timeout=30.0,
            )
            r2_body = r2.text or ""
            assert r2.status_code == 200, \
                f"rail2 expected 200 from fixture stream, got {r2.status_code}: {r2_body[:200]}"
            assert _P562_SENTINEL in r2_body, \
                f"rail2 positive control: sentinel missing; body={r2_body[:200]}"
            assert "shield_unavailable" not in r2_body, \
                f"rail2 must NOT fall through to shield; body={r2_body[:200]}"
    finally:
        app.dependency_overrides.pop(get_current_account, None)
        try:
            await db.chats.delete_many({"id": chat_id})
            await db.chat_messages.delete_many({"chat_id": chat_id})
            await db.synisense_runs.delete_many({"chat_id": chat_id})
            await db.audit_invariant_violations.delete_many({"chat_id": chat_id})
            await db.chat_audit.delete_many({"chat_id": chat_id})
        except Exception:
            pass
        _fixtures_mod.stream_fixture = saved_stream
        _shield_canonical.mint_chat_outcome = saved_mint
        if saved_env is None:
            os.environ.pop("AKKI_CHAT_FIXTURES_ENABLED", None)
        else:
            os.environ["AKKI_CHAT_FIXTURES_ENABLED"] = saved_env


@pytest.mark.asyncio
async def test_zz2_x_fixture_stream_shape(app):
    """When fixtures are enabled + caller is admin, the stream serves
    the canned SSE script for each fixture. We exercise this against
    the in-process app with the env temporarily set."""
    os.environ["AKKI_CHAT_FIXTURES_ENABLED"] = "1"
    try:
        import importlib, server
        importlib.reload(server)
        app = server.app

        import requests
        base = "https://akki-executive.preview.emergentagent.com"
        rr = requests.post(f"{base}/api/auth/login",
                           json={"email": "admin@akki.ai", "password": "AkkiAdmin2026!"},
                           timeout=15)
        token = rr.json()["access_token"]
        cid = requests.get(f"{base}/api/auth/me",
                           headers={"Authorization": f"Bearer {token}"}).json()["account"]["default_context_id"]
        rc = requests.post(f"{base}/api/chats",
                           json={"context_id": cid, "model_id": "claude-sonnet-4-5",
                                 "title": "zz2x-stream-shape"},
                           headers={"Authorization": f"Bearer {token}", "X-Active-Context": cid})
        if rc.status_code >= 400:
            pytest.skip(f"chat create skipped: {rc.status_code}")
        chat_id = rc.json()["id"]

        try:
            transport = ASGITransport(app=app)
            async with AsyncClient(transport=transport, base_url="http://test") as c:
                h = {"Authorization": f"Bearer {token}", "X-Active-Context": cid}
                r = await c.post(
                    f"/api/chats/{chat_id}/messages?fixture=bias_anchoring",
                    headers=h, json={"content": "ping"},
                )
                assert r.status_code == 200, r.text
                body = r.text
                assert '"type": "start"' in body
                assert '"phase": "complete"' in body
                # zz2_governance attached on the terminal message
                assert '"zz2_governance"' in body
                # Fixture text rendered as delta (middle-dot is u00b7
                # in JSON-escaped SSE output)
                assert ("[anchoring · Q4 number]" in body
                        or "[anchoring \\u00b7 Q4 number]" in body)
                # Bias flag captured in the terminal governance object
                assert ("anchoring · Q4 number" in body
                        or "anchoring \\u00b7 Q4 number" in body)
        finally:
            requests.delete(f"{base}/api/chats/{chat_id}",
                            headers={"Authorization": f"Bearer {token}", "X-Active-Context": cid})
    finally:
        os.environ.pop("AKKI_CHAT_FIXTURES_ENABLED", None)
