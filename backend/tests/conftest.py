"""Pytest fixtures shared by Solva v2 tests (and any future async test).

Phase 15.0 hardening pass: pytest-asyncio 0.23 with `auto` mode creates a
fresh event loop per async test by default. Motor's AsyncIO client latches
onto whichever loop first awaits it; once that loop is closed, subsequent
tests in fresh loops break with `RuntimeError: Event loop is closed`.

The fix is a session-scoped event_loop fixture so every async test in this
process shares a single loop. This is the documented pattern for sharing
Motor across tests under pytest-asyncio. The `scope='session'` event_loop
override is deprecated-but-functional in 0.23 (a clean replacement
`asyncio_default_loop_scope` ships in 0.25 which we have not pinned).

Sync tests (e.g. test_cycle_manager_actions_tab.py) are unaffected: they
use `asyncio.run()` and create their own short-lived loops, ignoring this
fixture entirely.
"""
from __future__ import annotations

import asyncio
import os
import sys

import pytest
from dotenv import load_dotenv

# Load backend env once for every collected test. Without this, any test
# whose imports reach `core.py` (which reads MONGO_URL at import time) fails
# at collection unless an earlier test file already called load_dotenv.
# Phase 15.1: services/solva_v2/__init__.py now re-exports the llm_adapter
# (which imports core), so the implicit-ordering hack the older tests relied
# on is no longer safe. Frontend env is loaded too because the
# request-driven smoke tests read REACT_APP_BACKEND_URL.
load_dotenv("/app/backend/.env")
load_dotenv("/app/frontend/.env")

# Phase P3.1 (2026-02) — CSRF middleware bypass for test runs.
# Existing tests drive endpoints directly via TestClient / AsyncClient
# and don't mint a CSRF cookie. Honour the in-process bypass switch so
# the suite keeps passing while production traffic still enforces CSRF.
os.environ.setdefault("CSRF_TEST_BYPASS_HEADER", "1")
# Phase P3 — disable rate-limit during tests. The suite drives ~50+
# login calls in <60s; without this, the per-IP login bucket trips
# and downstream MFA / B.4 / B.6 tests cascade-fail. Production
# never sets this env.
os.environ.setdefault("RATE_LIMIT_DISABLED", "1")
# Phase P5.11.2 (2026-02) — kill SendGrid notify sends during the
# pytest session. Three notify code paths read this flag:
#   - services.cohort_email._send_via_sendgrid
#   - routers.cohort_applications._notify_founder
#   - routers.website (early-access + contact form operator notify)
# Each short-circuits with a log line instead of opening a real
# SendGrid connection. Production never sets this env — it lives
# exclusively in test infra so bramuel / mugwe.marion / akki@syni.ai
# do not receive synthetic emails from CI runs or fork agents.
os.environ.setdefault("COHORT_NOTIFY_DISABLED", "true")
# C1-revised post-bundle (2026-02 fork-resume) — P4 cohort funnel
# test rot repair. P1-B flipped `COHORT_EMAILS_ENABLED=true` in
# preview `.env` so cohort approval/decline emails actually fire.
# The two pre-existing P4 tests
# (`test_p4_a_receipt_flag_off_logs_redacted`,
#  `test_p4_b_decline_writes_audit_and_skips_email_when_flag_off`)
# assert the legacy `flag_off` shape and now see
# `test_mode_disabled` instead. Force the flag off for the test
# session so the legacy assertions stay green while P1-B's own
# coverage (which monkeypatches the env to "true") is unaffected.
# Both shapes are SendGrid-safe under conftest's
# COHORT_NOTIFY_DISABLED=true guard above. Production never sets
# this env — preview's `.env` is the source of truth there.
os.environ["COHORT_EMAILS_ENABLED"] = "false"
import httpx as _httpx  # noqa: E402
_orig_request = _httpx.AsyncClient.request
async def _patched_request(self, method, url, *args, **kwargs):
    headers = kwargs.get("headers") or {}
    headers = dict(headers)
    headers.setdefault("X-CSRF-Test-Bypass", "1")
    kwargs["headers"] = headers
    return await _orig_request(self, method, url, *args, **kwargs)
_httpx.AsyncClient.request = _patched_request

# Phase P5.22 (2026-02) — symmetric bypass on the streaming path.
# `AsyncClient.stream(...)` builds its own request via `build_request`
# + `send` and bypasses the `request` monkey-patch above. The wire-
# level tests in `test_h2_5_shield_uniformity.py` exercise the
# streaming endpoint, so without this they regressed to 403
# `csrf_token_missing` on the production CSRFMiddleware. Mirror the
# header-injection on `stream` so both sync-style POST and streaming
# POST paths carry the test bypass token.
_orig_stream = _httpx.AsyncClient.stream
def _patched_stream(self, method, url, *args, **kwargs):
    headers = kwargs.get("headers") or {}
    headers = dict(headers)
    headers.setdefault("X-CSRF-Test-Bypass", "1")
    kwargs["headers"] = headers
    return _orig_stream(self, method, url, *args, **kwargs)
_httpx.AsyncClient.stream = _patched_stream

# Also patch the sync TestClient transport.
from starlette.testclient import TestClient as _StarletteTestClient  # noqa: E402
_orig_sync_request = _StarletteTestClient.request
def _patched_sync_request(self, method, url, **kwargs):
    headers = kwargs.get("headers") or {}
    headers = dict(headers)
    headers.setdefault("X-CSRF-Test-Bypass", "1")
    kwargs["headers"] = headers
    return _orig_sync_request(self, method, url, **kwargs)
_StarletteTestClient.request = _patched_sync_request

# Phase P5.6.1 (2026-06) — extend the bypass to the `requests` library.
# A long tail of legacy E2E tests (`test_phase_b_sandbox_upload.py`,
# `test_prepare_redirect_alias.py`, `test_governance_endpoint.py`,
# `test_cycle_manager_actions_tab.py`, `test_iter*.py`, …) hits the
# **live** FastAPI backend at `http://localhost:8001/api/...` via
# `requests.Session` rather than the in-process ASGITransport. The
# live backend runs production CSRFMiddleware which rejects every
# state-changing request with 403 `csrf_token_missing` unless the
# bypass header is present. The httpx + starlette TestClient
# monkey-patches above do NOT cover this code path, so these tests
# regressed silently when the CSRF middleware shipped in P3.1.
#
# IMPORTANT: the live backend (preview supervisor pod) does NOT have
# `CSRF_TEST_BYPASS_HEADER=1` in its env (and must NOT — that env
# would weaken security across the whole pod). So the bypass header
# is honoured only by the in-process ASGI tests where conftest sets
# the env at import time. For the `requests`-against-localhost
# tests, we instead do a real **double-submit round-trip**: mint a
# CSRF token via `GET /api/csrf` (which sets the cookie on the
# Session jar) and copy the same value into the `X-CSRF-Token`
# header on every state-changing request. The production
# CSRFMiddleware then HMAC-verifies the token and lets the request
# through — exercising the FULL middleware path (HMAC verify, cookie
# match, age check) rather than bypassing it.
#
# Idempotent methods (GET/HEAD/OPTIONS) and the mint endpoint itself
# skip the round-trip to avoid recursion. Sessions cache the cookie
# across requests so the mint cost is once-per-Session, not
# per-request.
import requests as _requests  # noqa: E402
from urllib.parse import urlparse as _urlparse  # noqa: E402

_orig_requests_session_request = _requests.Session.request
_CSRF_NON_IDEMPOTENT = {"POST", "PUT", "PATCH", "DELETE"}
# Mirror services/csrf.py:_ALLOWLIST_PREFIXES so we don't mint when
# the target is itself allowlisted (Stripe webhook receivers, etc.).
_CSRF_ALLOWLIST_SUBSTRINGS = (
    "/api/csrf",
    "/api/billing/webhook/",
    "/api/auth/oauth/google/callback",
    "/api/auth/oauth/microsoft/callback",
    "/api/inbound/sendgrid",
    "/api/cohort/email-events/sendgrid",
    "/api/internal/v1/",
    "/api/cron/",
    "/api/blog/cron/",
    "/api/solva/v2/cron/",
)


def _patched_requests_session_request(self, method, url, **kwargs):
    # Always announce the bypass header (cheap; honoured by in-proc
    # ASGI app only — live backend ignores it). The live-backend path
    # gets the real token round-trip below.
    headers = kwargs.get("headers") or {}
    headers = dict(headers) if headers else {}
    headers.setdefault("X-CSRF-Test-Bypass", "1")

    method_upper = (method or "").upper()
    if method_upper in _CSRF_NON_IDEMPOTENT and not any(s in url for s in _CSRF_ALLOWLIST_SUBSTRINGS):
        # Resolve the same-origin /api/csrf URL from the target.
        try:
            parsed = _urlparse(url)
            origin = f"{parsed.scheme}://{parsed.netloc}" if parsed.scheme else ""
        except Exception:
            origin = ""

        if origin:
            csrf_token_val = None
            # Try the existing session cookie jar first (avoid extra mint per request).
            jar_val = self.cookies.get("csrf_token", default=None)
            if jar_val:
                csrf_token_val = jar_val
            else:
                try:
                    mint = _orig_requests_session_request(
                        self, "GET", f"{origin}/api/csrf", timeout=10,
                    )
                    if mint.status_code == 200:
                        try:
                            csrf_token_val = mint.json().get("csrf_token")
                        except Exception:
                            csrf_token_val = None
                except Exception:
                    csrf_token_val = None

            if csrf_token_val:
                headers.setdefault("X-CSRF-Token", csrf_token_val)
                # Ensure the cookie is in the session for the next call too.
                if not self.cookies.get("csrf_token", default=None):
                    self.cookies.set("csrf_token", csrf_token_val)

    kwargs["headers"] = headers
    return _orig_requests_session_request(self, method, url, **kwargs)
_requests.Session.request = _patched_requests_session_request

BACKEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)


@pytest.fixture(scope="session")
def event_loop():
    """Single event loop for the entire test session.

    Phase 15.1: bumped pytest-asyncio to >=0.25 in requirements.txt and set
    `asyncio_default_fixture_loop_scope = session` in pytest.ini so this
    override is no longer deprecated. Motor's module-singleton client
    needs a stable loop for the lifetime of the suite.
    """
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def _isolate_dependency_overrides():
    """Snapshot + restore `app.dependency_overrides` per test.

    Phase C — Several legacy tests (test_cycle_feel_pass.py,
    test_cycle_assignment_handoff.py, test_cycles_v2.py, test_patch_*.py,
    etc.) set `app.dependency_overrides[get_current_account] = …` from
    inside the test body and never clean up. The pollution then bleeds
    into any test that runs *after* them, masking auth-gate assertions
    as 200 OK responses.

    This autouse fixture snapshots the override dict at test start and
    restores it at teardown, isolating each test without modifying the
    polluters. Tests that legitimately set overrides inside their own
    body keep working unchanged — only the cross-test leak is plugged.
    """
    # Import is local to avoid pulling FastAPI into collection-only runs.
    try:
        from server import app as _app  # type: ignore
    except Exception:
        # If `server` can't import here, the test will fail anyway with a
        # clearer error — don't mask import-level breakage.
        yield
        return
    snapshot = dict(_app.dependency_overrides)
    try:
        yield
    finally:
        _app.dependency_overrides.clear()
        _app.dependency_overrides.update(snapshot)

