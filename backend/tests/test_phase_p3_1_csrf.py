"""Phase P3.1 — CSRF middleware lockdown.

Cluster-F.3 (2026-06-27): converted from sync `_run`-helper pattern to
`@pytest.mark.asyncio + async def` so tests bind to the session-scoped
loop instead of creating local loops that bind Motor to the wrong loop
(same root cause as Cluster-E's FTT-023 closure). Risk verdict per
advance scan memo §5: LOW (CSRF round-trips are in-same-async-block;
2 pure-Python helper tests stay sync per Cluster-F.2 heuristic;
env-mutation try/finally preserved verbatim across 3 tests).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO / "backend"))

from dotenv import load_dotenv  # noqa: E402
load_dotenv(REPO / "backend" / ".env")

from httpx import ASGITransport, AsyncClient  # noqa: E402
from server import app  # noqa: E402


def _client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.mark.asyncio
async def test_p3_1_csrf_mint_endpoint_returns_token_and_sets_cookie():
    async with _client() as ac:
        r = await ac.get("/api/csrf")
        assert r.status_code == 200
        tok = r.json().get("csrf_token")
        assert tok and "." in tok
        # Cookie present.
        assert "csrf_token" in r.cookies or any(
            "csrf_token" in c for c in r.headers.get_list("set-cookie")
        )


@pytest.mark.asyncio
async def test_p3_1_post_without_csrf_returns_403_missing():
    """Strip the test-bypass header so we exercise the production path."""
    # Temporarily disable the autouse bypass for this single test.
    old = os.environ.get("CSRF_TEST_BYPASS_HEADER")
    os.environ["CSRF_TEST_BYPASS_HEADER"] = "0"
    try:
        async with _client() as ac:
            r = await ac.post(
                "/api/cohort/applications",
                json={
                    "name": "csrf-probe", "email": "csrf-probe@example.com",
                    "organisation": "Probe", "role": "Tester",
                    "use_case": "csrf", "referral_source": "test",
                },
                headers={"X-CSRF-Test-Bypass": "0"},  # explicit override the autoset bypass
            )
            assert r.status_code == 403
            detail = r.json()["detail"]
            assert detail["code"] == "csrf_token_missing"
    finally:
        if old is not None:
            os.environ["CSRF_TEST_BYPASS_HEADER"] = old
        else:
            os.environ.pop("CSRF_TEST_BYPASS_HEADER", None)


@pytest.mark.asyncio
async def test_p3_1_post_with_mismatched_csrf_returns_403_invalid():
    old = os.environ.get("CSRF_TEST_BYPASS_HEADER")
    os.environ["CSRF_TEST_BYPASS_HEADER"] = "0"
    try:
        async with _client() as ac:
            r1 = await ac.get("/api/csrf")
            cookie_val = r1.json()["csrf_token"]
            # Header carries a DIFFERENT (but valid-shaped) string.
            r = await ac.post(
                "/api/cohort/applications",
                json={
                    "name": "csrf-mismatch", "email": "csrf-mismatch@example.com",
                    "organisation": "Probe", "role": "Tester",
                    "use_case": "csrf", "referral_source": "test",
                },
                cookies={"csrf_token": cookie_val},
                headers={
                    "X-CSRF-Token": "tampered.value.123",
                    "X-CSRF-Test-Bypass": "0",
                },
            )
            assert r.status_code == 403
            detail = r.json()["detail"]
            assert detail["code"] == "csrf_token_invalid"
    finally:
        if old is not None:
            os.environ["CSRF_TEST_BYPASS_HEADER"] = old
        else:
            os.environ.pop("CSRF_TEST_BYPASS_HEADER", None)


@pytest.mark.asyncio
async def test_p3_1_post_with_matched_csrf_passes():
    old = os.environ.get("CSRF_TEST_BYPASS_HEADER")
    os.environ["CSRF_TEST_BYPASS_HEADER"] = "0"
    try:
        async with _client() as ac:
            r1 = await ac.get("/api/csrf")
            tok = r1.json()["csrf_token"]
            r = await ac.post(
                "/api/cohort/applications",
                json={
                    "name": "csrf-pass", "email": "csrf-pass@example.com",
                    "organisation": "Probe", "role": "Tester",
                    "use_case": "csrf", "referral_source": "test",
                },
                cookies={"csrf_token": tok},
                headers={
                    "X-CSRF-Token": tok,
                    "X-CSRF-Test-Bypass": "0",
                },
            )
            # Cohort apply may return 200/409 depending on dedupe state —
            # the only thing we're asserting is that CSRF did NOT block.
            assert r.status_code != 403
    finally:
        if old is not None:
            os.environ["CSRF_TEST_BYPASS_HEADER"] = old
        else:
            os.environ.pop("CSRF_TEST_BYPASS_HEADER", None)


@pytest.mark.asyncio
async def test_p3_1_get_requests_bypass_csrf():
    """GETs are idempotent; the middleware MUST NOT block them."""
    async with _client() as ac:
        r = await ac.get("/api/health/composite")
        assert r.status_code == 200


def test_p3_1_webhook_allowlisted():
    """Stripe webhook receiver is on the allowlist (Stripe HMAC-signs
    its events itself; CSRF on top would be redundant).

    Pure-Python set-membership contract — no asyncio surface, stays
    sync per Cluster-F.2 heuristic.
    """
    from services.csrf import _ALLOWLIST_PREFIXES
    assert "/api/billing/webhook/" in _ALLOWLIST_PREFIXES


def test_p3_1_verify_round_trip():
    """Pure-Python mint+verify round-trip — no asyncio surface, stays
    sync per Cluster-F.2 heuristic.
    """
    from services.csrf import mint_csrf_token, verify_csrf_token
    t = mint_csrf_token()
    assert verify_csrf_token(t)
    # Tampered HMAC fails.
    assert not verify_csrf_token(t[:-4] + "XXXX")
    # Empty string fails.
    assert not verify_csrf_token("")
