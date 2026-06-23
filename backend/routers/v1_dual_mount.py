"""Phase 4.4 — Dual-mount versioned surface.

Mounts every existing ``/api/*`` route a second time under
``/v1/{owning_context}/*`` where the owning context is the one defined
by the Phase 4.1 router-to-app classification (12 SyniSense + 9 Solva +
113 Akki routers). Both surfaces route to the **same** underlying
endpoint function — no logic duplication, no behaviour drift.

Convention
==========

For each route currently mounted under ``/api/<rest>``, the parallel
``/v1/<owning_context>/<derived>`` path is derived as follows:

  • If ``<rest>`` already starts with ``<owning_context>/``, drop the
    duplicate context segment so the path doesn't double up.
      ``/api/synisense/foo``        →  ``/v1/synisense/foo``
      ``/api/solva/v2/foo``         →  ``/v1/solva/v2/foo``

  • Otherwise, the owning_context is prepended verbatim.
      ``/api/contexts/{cid}``  (akki)      →  ``/v1/akki/contexts/{cid}``
      ``/api/chats/{cid}``     (akki)      →  ``/v1/akki/chats/{cid}``
      ``/api/trust-center/...``(synisense) →  ``/v1/synisense/trust-center/...``

Exclusion list
==============

Routes that are deliberately NOT dual-mounted:

  • ``/api/openapi.json`` — singleton OpenAPI document; FastAPI manages it.
  • ``/api/docs`` and ``/docs/oauth2-redirect`` — Swagger UI singletons.
  • ``/api/healthz/*`` — per-context probes are already context-namespaced
    via the Healthcheck Triad (Phase 4.3). Re-mounting under ``/v1/*``
    would double-publish the unindexed probes without adding value.
  • ``/api/internal/v1/*`` — Phase 4.2 internal transport endpoints; not
    part of the public commercial surface.

operation_id stability
======================

Each cloned route gets ``operation_id=<original>_v1_<owning_context>``.
This keeps the public OpenAPI document free of operation_id collisions
once the ``/v1/*`` slice is included in the schema, and lets SDK
generators produce non-clashing method names for the two surfaces.
"""
from __future__ import annotations

from typing import Iterable

from fastapi import FastAPI
from fastapi.routing import APIRoute, APIRouter


_EXCLUDED_PREFIXES = (
    "/api/internal/",
    "/api/healthz/",
)


_EXCLUDED_EXACT = {
    "/api/openapi.json",
    "/api/docs",
}


def _v1_path_for(owning_context: str, api_path: str) -> str:
    """Map an ``/api/*`` route to its parallel ``/v1/<owning_context>/*`` path."""
    if not api_path.startswith("/api/"):
        return ""  # caller checks the empty-string sentinel and skips
    if api_path in _EXCLUDED_EXACT:
        return ""
    for excluded in _EXCLUDED_PREFIXES:
        if api_path.startswith(excluded):
            return ""
    rest = api_path[len("/api"):]  # leading "/<segment>/..." (always begins with "/")
    # If the next segment already equals the owning context, don't double-prefix.
    head, _, tail = rest.lstrip("/").partition("/")
    if head == owning_context:
        # /api/synisense/foo → /v1/synisense/foo
        return f"/v1/{owning_context}/{tail}" if tail else f"/v1/{owning_context}"
    # /api/contexts/{cid} → /v1/akki/contexts/{cid}
    return f"/v1/{owning_context}{rest}"


def _clone_route(app: FastAPI, route: APIRoute, new_path: str, owning_context: str) -> None:
    """Register `route` as a parallel route on `app` under `new_path`.

    Preserves every meaningful kwarg so the cloned route is functionally
    identical (auth, response model, status code, dependencies, etc.).
    Operation IDs / names are suffixed with both the owning context AND
    the original path so they remain globally unique even when multiple
    routers expose a same-named handler (e.g. `download_export`,
    `list_documents`).
    """
    import hashlib
    # `operation_id` must be globally unique. We avoid collisions by
    # building the suffix from a hash of the original /api/* path; that
    # path is unique by FastAPI guarantee, so the suffix is unique too.
    path_tag = hashlib.sha1(route.path.encode()).hexdigest()[:8]
    original_op_id = route.operation_id or route.name
    new_op_id = (
        f"{original_op_id}_v1_{owning_context}_{path_tag}"
        if original_op_id
        else None
    )
    new_name = (
        f"{route.name}_v1_{owning_context}_{path_tag}"
        if route.name
        else None
    )
    app.add_api_route(
        new_path,
        route.endpoint,
        response_model=route.response_model,
        status_code=route.status_code,
        tags=route.tags,
        dependencies=route.dependencies,
        summary=route.summary,
        description=route.description,
        response_description=route.response_description,
        responses=route.responses,
        deprecated=route.deprecated,
        operation_id=new_op_id,
        methods=list(route.methods),
        response_model_include=route.response_model_include,
        response_model_exclude=route.response_model_exclude,
        response_model_by_alias=route.response_model_by_alias,
        response_model_exclude_unset=route.response_model_exclude_unset,
        response_model_exclude_defaults=route.response_model_exclude_defaults,
        response_model_exclude_none=route.response_model_exclude_none,
        include_in_schema=route.include_in_schema,
        response_class=route.response_class,
        name=new_name,
        openapi_extra=route.openapi_extra,
    )


def dual_mount_v1(
    app: FastAPI,
    routers: Iterable[APIRouter],
    owning_context: str,
) -> int:
    """Re-mount every route on each router under ``/v1/<owning_context>/*``.

    Returns the count of cloned routes for logging / assertion.
    """
    cloned = 0
    for router in routers:
        for route in router.routes:
            if not isinstance(route, APIRoute):
                continue
            v1_path = _v1_path_for(owning_context, route.path)
            if not v1_path:
                continue
            _clone_route(app, route, v1_path, owning_context)
            cloned += 1
    return cloned


__all__ = ["dual_mount_v1", "_v1_path_for", "_EXCLUDED_PREFIXES", "_EXCLUDED_EXACT"]
