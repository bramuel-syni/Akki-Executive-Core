"""Phase 3.1 — Fitness function: every hot-path FastAPI route in the Phase
3.0 inventory MUST declare `response_model=`.

This is the backend-side guard for FE/BE drift. If a hot-path route is
added without `response_model=`, the OpenAPI spec emits `{}` for the
response schema, the FE codegen produces `z.any()`, and drift catch is
lost on that route.

Build-breaking. Same shape as `test_invariant_tenancy.py`.

Phase 3.0 baseline = 217 hot-path routes (216 typed + 1 explicit
RedirectResponse). The 17 binary/streaming routes are exempted by
design — they don't emit JSON.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import List, Set, Tuple

import pytest
from fastapi.routing import APIRoute
from starlette.routing import Mount

# Hot-path substrings — MUST match Phase 3.0 dispatch §1.A inventory exactly.
# Uses substring `in path` check (not `startswith`) to mirror the Phase 3.0
# scanner. Routes outside this inventory (e.g. `/api/chats` exact list
# endpoint, `/api/cycles` plural) are Phase 3.x scope, NOT Phase 3.1.
_HOT_PATH_SUBSTRINGS: Tuple[str, ...] = (
    "/chats/", "/chat/",
    "/workbook/v2/", "/workbook/",
    "/work-studio/",
    "/contexts/{cid}/documents", "/contexts/{context_id}/documents",
    "/contexts/{cid}/cycle/", "/contexts/{context_id}/cycle/",
    "/tasks/",
    "/auth/",
    "/me/",
    "/contexts/{cid}/events", "/contexts/{context_id}/events",
)

# Routes that legitimately return non-JSON content (binary / streaming /
# RedirectResponse). They CANNOT have a JSON response_model — exempted.
_NON_JSON_PATH_PATTERNS: Tuple[str, ...] = (
    ".pdf", ".pptx", ".docx", ".xlsx", ".zip",
    "/download", "/stream",
    "/auth/magic/{token}",                                # RedirectResponse
    "/auth/oauth/microsoft/callback",                     # RedirectResponse
    "/chats/{chat_id}/messages",                          # StreamingResponse (SSE)
    "/work-studio/documents/{artefact_id}/render",        # Response (HTML)
    "/me/governance/audit/export",                        # Response (binary export)
)


def _is_hot_path(path: str) -> bool:
    return any(s in path for s in _HOT_PATH_SUBSTRINGS)


def _is_non_json(path: str) -> bool:
    return any(pattern in path for pattern in _NON_JSON_PATH_PATTERNS)


def _collect_routes(app) -> List[Tuple[str, str, APIRoute]]:
    """Walk all FastAPI routes (including those mounted via include_router)."""
    out: List[Tuple[str, str, APIRoute]] = []

    def walk(routes):
        for route in routes:
            if isinstance(route, APIRoute):
                for method in route.methods:
                    if method in ("GET", "POST", "PUT", "PATCH", "DELETE"):
                        out.append((method, route.path, route))
            elif isinstance(route, Mount):
                walk(route.routes)

    walk(app.routes)
    return out


def test_hot_path_routes_declare_response_model() -> None:
    """Every hot-path API route MUST declare `response_model=` so the
    OpenAPI spec carries a typed response shape for FE zod codegen.

    Build-breaking. New violations fail this test until either:
    - The route gets a `response_model=` (preferred — author or reuse a
      shared model from `contracts/responses.py`); OR
    - The route's path matches an entry in `_NON_JSON_PATH_PATTERNS`
      (e.g. binary download, SSE stream) — then add it there with a
      one-line rationale.
    """
    from server import app  # noqa: WPS433 — local app import for invariant

    untyped: List[Tuple[str, str]] = []
    for method, path, route in _collect_routes(app):
        if not _is_hot_path(path):
            continue
        if _is_non_json(path):
            continue
        if route.response_model is None:
            untyped.append((method, path))

    if untyped:
        formatted = "\n  ".join(f"{m:6s} {p}" for m, p in sorted(untyped))
        pytest.fail(
            "Hot-path routes missing `response_model=`:\n  "
            f"{formatted}\n\n"
            "Fix: add `response_model=<PydanticModel>` to the @router decorator. "
            "Reuse a model from `backend/contracts/responses.py` where the shape matches, "
            "or author a new shared model with `extra='allow'` for safety. "
            "If the route legitimately emits non-JSON, add its path to "
            "`_NON_JSON_PATH_PATTERNS` with a one-line rationale."
        )


def test_phase_3_2_marker_count_within_phase_3_2_target() -> None:
    """The Phase 3.0 baseline left `# phase-3.0:narrow-in-3.1` markers
    on routes using `Optional[Dict[str, Any]]`. Phase 3.1 narrowed 80 of
    those (172 → 92). Phase 3.2 narrowed a further 37 singletons
    (92 → 55).

    This invariant fails build if the marker count GROWS beyond the
    documented Phase 3.2 close baseline — preventing regression
    (any further phase must REDUCE markers, never increase).

    Baseline: Phase 3.2 close left 55 markers (92 Phase 3.1 close
    − 37 narrowed in Phase 3.2). Of these 55, the AST scanner
    classified them as polymorphic / cursor-returning / spread-only
    payloads where shape can't be statically recovered.
    """
    routers_dir = Path(__file__).resolve().parent.parent.parent / "routers"
    total = 0
    if not routers_dir.exists():
        pytest.skip(f"routers dir not found at {routers_dir}")
    for fp in routers_dir.rglob("*.py"):
        try:
            total += fp.read_text().count("phase-3.0:narrow-in-3.1")
        except Exception:
            pass
    # Also check the auth_magic + other backend/auth/* files
    auth_dir = Path(__file__).resolve().parent.parent.parent / "auth"
    if auth_dir.exists():
        for fp in auth_dir.rglob("*.py"):
            try:
                total += fp.read_text().count("phase-3.0:narrow-in-3.1")
            except Exception:
                pass

    PHASE_3_2_CLOSE_BASELINE = 55
    assert total <= PHASE_3_2_CLOSE_BASELINE, (
        f"phase-3.0:narrow-in-3.1 marker count grew to {total} — "
        f"Phase 3.2 close baseline was {PHASE_3_2_CLOSE_BASELINE}. "
        f"Future phases must REDUCE the count via narrowing, never increase. "
        f"If a new untyped hot-path route was added, narrow it directly "
        f"instead of carrying a Phase 3.0 marker."
    )
