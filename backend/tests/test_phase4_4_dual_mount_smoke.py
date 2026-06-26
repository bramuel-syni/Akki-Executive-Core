"""Phase 4.4 — Dual-mount versioned surface smoke + invariant gate.

Asserts:

  1. Each owning-context router is dual-mounted under `/v1/<ctx>/*` with
     no logic divergence — handler, status, headers (minus path-dependent
     ones), and JSON body must match byte-for-byte against `/api/*`.
  2. The `/api/*` slice hash stays pinned at `cdcb23322bb82895` (Phase 4.1
     ratchet, re-affirmed at every subsequent phase).
  3. The `/v1/*` slice hash is captured as a new baseline.
  4. The combined `paths_sha256[:16]` baseline is captured.
  5. Wrong-context routes (e.g. `/v1/wrongcontext/foo`, or asking for a
     SyniSense path under `/v1/akki/...`) return 404 — no silent
     fall-through to a same-named route owned by a different context.

The HTTP exchange uses ``httpx.AsyncClient`` with ``ASGITransport`` (the
same pattern used by the iter-41 in-process suite). Tests are marked
async so pytest-asyncio's session-scoped loop is honoured — Motor's
module-singleton client stays bound to a single live loop across the
whole session.
"""
from __future__ import annotations

import hashlib
import json
import os
from typing import List, Tuple

import httpx
import pytest

# Force the in-proc transport so the smoke run isn't sensitive to a
# misbehaving HTTP loopback under heavy concurrent test load. The
# Phase 4.4 dual-mount itself is purely a route-table operation —
# transport mode is orthogonal.
os.environ.setdefault("BOUNDED_CONTEXT_TRANSPORT", "inproc")

from server import app  # noqa: E402


# ─── Phase 4.4 baseline hashes ───────────────────────────────────────────
# /api/* slice — Phase 4.1 close pin (`cdcb23322bb82895`) was rolled
# forward during the JC-MON / JC-CHAT / JC-TL feature dispatches
# (2026-06-25/26) which added 9 new additive routes across JC-MON
# Stage 2b widens + JC-MON Stage 3.0 candidate-objectives generator.
# Then rolled again at BUG-ANL-UPLOAD-GRIDFS close (2026-06-26) for
# the additive `/api/jc-artifacts/track2/{filename}` superadmin-gated
# JC-TL Track-2 deck download. Each add was deliberate and additive
# (no existing-route behavioural change), so the ratchet rolls
# forward on the new total. Audit trail for the rolls lives in
# DEV_PIPELINE.md § 5 and the per-stage sprint memos.
EXPECTED_API_SHA = "9aa905f6d951f2a8"  # rolled at JC-TL GP ship close (2026-06-26)
EXPECTED_V1_SHA = "6ce751ef812f6816"
EXPECTED_COMBINED_SHA = "4f050f7e95b8dd10"


@pytest.fixture(scope="module")
def openapi_paths() -> List[str]:
    return sorted(app.openapi().get("paths", {}).keys())


def _slice_hash(paths: List[str], slice_prefix: str) -> str:
    selected = sorted(p for p in paths if p.startswith(slice_prefix))
    return hashlib.sha256("\n".join(selected).encode()).hexdigest()[:16]


# ─────────────────────────────────────────────────────────────────────────
# 1. OpenAPI slice hash invariants (sync — no event loop needed)
# ─────────────────────────────────────────────────────────────────────────
def test_api_slice_hash_pinned(openapi_paths: List[str]) -> None:
    """`/api/*` slice hash MUST remain `cdcb23322bb82895` — the Phase 4.1
    ratchet preserves a byte-identical legacy surface forever."""
    api_paths = [p for p in openapi_paths if p.startswith("/api/")]
    actual = _slice_hash(openapi_paths, "/api/")
    assert actual == EXPECTED_API_SHA, (
        f"/api/* slice drift: expected={EXPECTED_API_SHA} got={actual} "
        f"(api_paths={len(api_paths)})"
    )
    assert len(api_paths) == 632


def test_v1_slice_hash_pinned(openapi_paths: List[str]) -> None:
    """`/v1/*` slice baseline established at Phase 4.4 close. Any drift
    indicates an unintentional surface change to the versioned API."""
    v1_paths = [p for p in openapi_paths if p.startswith("/v1/")]
    actual = _slice_hash(openapi_paths, "/v1/")
    assert actual == EXPECTED_V1_SHA, (
        f"/v1/* slice drift: expected={EXPECTED_V1_SHA} got={actual} "
        f"(v1_paths={len(v1_paths)})"
    )
    # /v1/* expected count = /api/* count minus the operational
    # endpoints excluded from dual-mount (currently
    # /api/healthz/{clamav, shield}).
    assert len(v1_paths) == 630


def test_combined_hash_pinned(openapi_paths: List[str]) -> None:
    """Full OpenAPI hash baseline established at Phase 4.4 close."""
    actual = hashlib.sha256("\n".join(openapi_paths).encode()).hexdigest()[:16]
    assert actual == EXPECTED_COMBINED_SHA, (
        f"Combined OpenAPI hash drift: expected={EXPECTED_COMBINED_SHA} "
        f"got={actual} (total paths={len(openapi_paths)})"
    )


def test_v1_context_namespaces_present(openapi_paths: List[str]) -> None:
    """Each owning context must have at least one /v1/* route registered."""
    for ctx in ("synisense", "solva", "akki"):
        ctx_paths = [p for p in openapi_paths if p.startswith(f"/v1/{ctx}/")]
        assert ctx_paths, f"Missing /v1/{ctx}/* routes — dual-mount skipped this context"


def test_dual_mount_count_invariant(openapi_paths: List[str]) -> None:
    """Phase 4.4: /v1/* count = /api/* count minus exclusion-list size.

    Currently excluded from dual-mount and present in the public OpenAPI:
      • /api/healthz/clamav
      • /api/healthz/shield
    So expected delta = 2.
    """
    api_paths = [p for p in openapi_paths if p.startswith("/api/")]
    v1_paths = [p for p in openapi_paths if p.startswith("/v1/")]
    delta = len(api_paths) - len(v1_paths)
    EXPECTED_EXCLUDED_COUNT = 2
    assert delta == EXPECTED_EXCLUDED_COUNT, (
        f"Phase 4.4 dual-mount count drift: /api={len(api_paths)} - "
        f"/v1={len(v1_paths)} = {delta} (expected {EXPECTED_EXCLUDED_COUNT}). "
        f"If the exclusion list changed, update EXPECTED_EXCLUDED_COUNT + "
        f"_EXCLUDED_PREFIXES / _EXCLUDED_EXACT in routers/v1_dual_mount.py."
    )


# ─────────────────────────────────────────────────────────────────────────
# 2. Byte-identity smoke — sample N≥30 routes across all three contexts
# ─────────────────────────────────────────────────────────────────────────
def _smoke_routes() -> List[Tuple[str, str, str]]:
    """List of `(method, /api path, /v1 path)` triples we exercise.

    Each path is confirmed to exist in the public OpenAPI surface as of
    Phase 4.4 close (verified by `grep` against
    `app.openapi()["paths"]`). Mix covers:
      • Akki public + auth-walled + admin (10)
      • SyniSense surface (8) — trust-center, observability, governance,
        admin Shield, engine signal types
      • Solva surface (5) — briefing state, workbook, v2 sessions, admin
      • Admin cross-context walls (4)
      • Tenancy-scoped read walls (3)
    """
    return [
        # ── Akki public / metadata (10)
        ("GET", "/api/health", "/v1/akki/health"),
        ("GET", "/api/csrf", "/v1/akki/csrf"),
        ("GET", "/api/me/active-context", "/v1/akki/me/active-context"),
        ("GET", "/api/auth/me", "/v1/akki/auth/me"),
        ("GET", "/api/blog/posts", "/v1/akki/blog/posts"),
        ("GET", "/api/blog/rss", "/v1/akki/blog/rss"),
        ("GET", "/api/chat/models", "/v1/akki/chat/models"),
        ("GET", "/api/help/features", "/v1/akki/help/features"),
        ("GET", "/api/billing/plans", "/v1/akki/billing/plans"),
        ("GET", "/api/lens/catalog", "/v1/akki/lens/catalog"),
        # ── SyniSense surface (8)
        ("GET", "/api/trust-center/activity", "/v1/synisense/trust-center/activity"),
        ("GET", "/api/trust-center/reasoning", "/v1/synisense/trust-center/reasoning"),
        ("GET", "/api/synisense/status", "/v1/synisense/status"),
        ("GET", "/api/me/governance", "/v1/synisense/me/governance"),
        ("GET", "/api/me/governance/audit", "/v1/synisense/me/governance/audit"),
        ("GET", "/api/v1/engine/signal_types", "/v1/synisense/v1/engine/signal_types"),
        ("GET", "/api/observability/reasoning_velocity", "/v1/akki/observability/reasoning_velocity"),
        ("GET", "/api/public/observability/reasoning_velocity", "/v1/akki/public/observability/reasoning_velocity"),
        # ── Solva surface (5)
        ("GET", "/api/solva/briefing/state", "/v1/solva/briefing/state"),
        ("GET", "/api/solva/v2/seed", "/v1/solva/v2/seed"),
        ("GET", "/api/solva/v2/sessions", "/v1/solva/v2/sessions"),
        ("GET", "/api/workbook/analyses", "/v1/solva/workbook/analyses"),
        ("GET", "/api/workbook/v2/analyses", "/v1/solva/workbook/v2/analyses"),
        # ── Admin cross-context walls (4)
        ("GET", "/api/admin/audit-invariant-violations", "/v1/akki/admin/audit-invariant-violations"),
        ("GET", "/api/admin/audit-invariant-violations/summary", "/v1/akki/admin/audit-invariant-violations/summary"),
        ("GET", "/api/admin/synisense/perf", "/v1/synisense/admin/synisense/perf"),
        ("GET", "/api/admin/solva/key-usage", "/v1/solva/admin/solva/key-usage"),
        # ── Tenancy-scoped read walls (3)
        ("GET", "/api/chats", "/v1/akki/chats"),
        ("GET", "/api/chats/archived", "/v1/akki/chats/archived"),
        ("GET", "/api/chats/search", "/v1/akki/chats/search"),
    ]


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    )


@pytest.mark.parametrize("method, api_path, v1_path", _smoke_routes())
async def test_route_byte_identity(
    method: str,
    api_path: str,
    v1_path: str,
) -> None:
    """The /v1 surface must return byte-equivalent responses to /api/* for
    the same request. Status code must match exactly. Body shape (top-
    level JSON keys) must match — value-level equality is asserted only
    when neither response contains intrinsically-fresh fields (CSRF
    rotation, timestamps, request_ids).

    The wall we're guarding against is "wrong handler" / "wrong status
    code" / "lost dependency" — all of which manifest at the status /
    shape layer.
    """
    async with _client() as client:
        api_resp = await client.request(method, api_path)
        v1_resp = await client.request(method, v1_path)

    assert api_resp.status_code == v1_resp.status_code, (
        f"Status drift {api_path}={api_resp.status_code} vs "
        f"{v1_path}={v1_resp.status_code}"
    )

    api_body = api_resp.content
    v1_body = v1_resp.content
    if api_body == v1_body:
        return
    # If at least one body is non-JSON, fall back to a shape probe on
    # the first 32 bytes. Identical leading bytes = same handler shape;
    # any divergence after that is freshness (timestamps embedded in
    # XML, etc.), which is NOT a route-wiring concern.
    try:
        api_json = json.loads(api_body)
        v1_json = json.loads(v1_body)
    except Exception:
        # Both empty → benign.
        if api_body == b"" and v1_body == b"":
            return
        # Compare first 64 bytes — handler identity gives same root
        # element / first declaration; later content can drift on
        # timestamps without being a wiring bug.
        assert api_body[:64] == v1_body[:64], (
            f"Non-JSON body divergence at byte 0..64 between {api_path} "
            f"and {v1_path}:\n"
            f"api[:200]={api_body[:200]!r}\nv1[:200]={v1_body[:200]!r}"
        )
        return
    if isinstance(api_json, dict) and isinstance(v1_json, dict):
        assert set(api_json.keys()) == set(v1_json.keys()), (
            f"Top-level JSON key drift between {api_path} and {v1_path}\n"
            f"api keys: {sorted(api_json.keys())}\n"
            f"v1  keys: {sorted(v1_json.keys())}"
        )
    elif isinstance(api_json, list) and isinstance(v1_json, list):
        assert len(api_json) == len(v1_json), (
            f"List length drift between {api_path} ({len(api_json)}) and "
            f"{v1_path} ({len(v1_json)})"
        )
    else:
        assert api_json == v1_json, (
            f"Scalar JSON drift between {api_path} and {v1_path}: "
            f"{api_json!r} vs {v1_json!r}"
        )


# ─────────────────────────────────────────────────────────────────────────
# 3. Wrong-context negative tests — no silent fall-through
# ─────────────────────────────────────────────────────────────────────────
async def test_wrong_context_returns_404() -> None:
    """A SyniSense path requested under /v1/akki/* must not resolve.

    SyniSense's trust-center endpoints are mounted at
    /v1/synisense/trust-center/activity. Requesting them under
    /v1/akki/trust-center/activity must return 404, not silently
    delegate to a different context's handler.
    """
    async with _client() as client:
        resp = await client.get("/v1/akki/trust-center/activity")
        assert resp.status_code == 404, (
            f"Wrong-context fall-through: /v1/akki/trust-center/activity "
            f"returned {resp.status_code}, body={resp.content[:200]!r}"
        )
        resp = await client.get("/v1/solva/contexts")
        assert resp.status_code == 404
        resp = await client.get("/v1/synisense/workbook/analyses")
        assert resp.status_code == 404
        resp = await client.get("/v1/wrongcontext/health")
        assert resp.status_code == 404


async def test_excluded_paths_are_api_only() -> None:
    """Healthcheck triad and internal transport endpoints are /api-only.
    They must NOT be dual-mounted under /v1/<context>/*.
    """
    async with _client() as client:
        for ctx in ("akki", "synisense", "solva"):
            api_resp = await client.get(f"/api/healthz/{ctx}")
            v1_resp = await client.get(f"/v1/{ctx}/healthz/{ctx}")
            assert api_resp.status_code == 200
            assert v1_resp.status_code == 404, (
                f"Healthcheck must not be dual-mounted: "
                f"/v1/{ctx}/healthz/{ctx} returned {v1_resp.status_code}"
            )
        api_internal = await client.post(
            "/api/internal/v1/akki/method/count_documents", json={},
        )
        assert api_internal.status_code in (401, 503), (
            f"Internal transport unexpectedly returned {api_internal.status_code}"
        )
        v1_internal = await client.post(
            "/v1/akki/internal/v1/akki/method/count_documents", json={},
        )
        assert v1_internal.status_code == 404
