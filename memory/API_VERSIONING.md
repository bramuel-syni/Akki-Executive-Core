# API Versioning

> Effective from **Phase 4.4 (2026-06-23)**.

The AKKI/SyniSense/Solva backend exposes two surfaces that resolve to the **same handlers, the same auth, the same shield wraps, and the same tenancy guards**:

| Surface | Status | Intended consumer |
|---|---|---|
| `/api/*` | **Legacy-stable.** Supported indefinitely. | Existing FE app, internal tooling, anyone integrated before 2026-06-23. |
| `/v1/{context}/*` | **Stable, versioned SDK surface.** | New SDKs, partner integrations, anyone building against the commercial separability contract going forward. |

Both surfaces stay in lock-step. A route under `/api/<rest>` always has a parallel route under `/v1/<owning_context>/<derived>`, byte-for-byte identical at the handler layer.

---

## What `v1` represents

`v1` is the **commercial separability contract** — the version of the API in which SyniSense, Solva, and Akki are exposed as three context-bound surfaces that can each be:

- Deployed as an independent uvicorn process (`<context>_app:app`).
- Versioned independently in future (Solva can ship `/v2/solva/*` without forcing Akki).
- Sold or licensed independently.

The `{context}` segment in the path declares ownership. Per the Phase 4.1 router classification:

| Context | Surface examples |
|---|---|
| `synisense` | `/v1/synisense/trust-center/*`, `/v1/synisense/synisense/*`, `/v1/synisense/observability/*` (Shield+observability) |
| `solva` | `/v1/solva/v2/*`, `/v1/solva/briefing/*`, `/v1/solva/workbook/*` |
| `akki` | `/v1/akki/contexts/*`, `/v1/akki/chats/*`, `/v1/akki/documents/*`, every Akki-owned product surface |

---

## Path mapping convention

Given an `/api/<rest>` path and its owning context `<ctx>`:

- **If `<rest>` starts with `<ctx>/`** (the legacy path already led with the context), the v1 path drops the duplicate context segment:
  ```
  /api/synisense/health  →  /v1/synisense/health
  /api/solva/v2/render   →  /v1/solva/v2/render
  ```
- **Otherwise** (context-implicit legacy path), the owning context is prepended verbatim:
  ```
  /api/contexts/{cid}  (akki)      →  /v1/akki/contexts/{cid}
  /api/trust-center/*  (synisense) →  /v1/synisense/trust-center/*
  /api/workbook/*      (solva)     →  /v1/solva/workbook/*
  ```

---

## What is NOT dual-mounted

Operational endpoints stay on `/api/*` only and are NOT exposed under `/v1/*`:

- `/api/openapi.json`, `/api/docs` — singleton OpenAPI / Swagger documents.
- `/api/healthz/*` — per-context readiness probes (already namespaced by the Healthcheck Triad).
- `/api/internal/v1/*` — Phase 4.2 internal cross-context HTTP transport. NOT part of the public commercial surface.

---

## Deprecation policy

`/api/*` is **legacy-stable**, not deprecated. There is **no sunset date**. We will:

- Continue to ship bug fixes to `/api/*`.
- Continue to maintain byte-identical surface ratchets (`paths_sha256[:16] = cdcb23322bb82895` for `/api/*` is the Phase 4.1 commitment).
- Announce any future deprecation window with **at least 12 months notice** plus a parallel `Deprecation:` HTTP header on the affected routes.

`v2` (or context-specific `v2/<context>/*`) will only ship when a context's API shape changes in a way that cannot be expressed additively under `v1`. Until that day, all surfaces remain on `v1`.

---

## SDK hint

If you are generating an SDK:

- Use the `/v1/{context}/*` slice of the OpenAPI document.
- Filter the document with the helper in `tests/invariants/` (slice hash extraction) so your SDK only ships the versioned surface.
- The `operation_id` of each `/v1/*` route is suffixed with `_v1_<owning_context>_<path_hash>` to guarantee uniqueness across the contract surface. Strip the suffix for human-readable SDK method names.

---

## See also

- `/app/memory/sprints/PHASE_4_4_DUAL_MOUNT.md` — Phase 4.4 dispatch close-out.
- `/app/backend/routers/v1_dual_mount.py` — the dual-mount mechanism.
- `/app/backend/tests/test_phase4_4_dual_mount_smoke.py` — surface invariant + byte-identity gate.
