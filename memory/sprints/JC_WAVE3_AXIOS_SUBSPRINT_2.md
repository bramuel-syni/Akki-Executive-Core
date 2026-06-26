**Canonical Spec**: `/app/memory/JC_WS_CANONICAL_SPEC.md` (parent JC-WS lock — Wave 3 cleanup, pure FE refactor toward the shared client)

# JC-WAVE3 · axios → shared client migration — sub-sprint 2 · CLOSED 2026-06-26 · 6/6 GREEN

## Sub-sprint scope

Continuation of sub-sprint 1 (sandbox/v2 files). This sub-sprint
targets the **7 remaining files** in the SPA that still imported raw
`axios` (~20 call sites). Carries Wave 3 to **completion** — only
`src/lib/api.js` (the shared wrapper itself) and `_archived_legacy/`
artefacts still import axios.

## Files migrated

| File | Sites | Notes |
|---|---:|---|
| `pages/TrustCenter.jsx` | 9 | dropped `useAuthHeaders` (read wrong localStorage key `akki_token` — latent bug; cookie auth saved it) |
| `pages/WelcomePage.jsx` | 5 | dropped hand-rolled `ensureCsrf()` helper — interceptor now does the double-submit |
| `pages/SharedArtefact.jsx` | 2 | public-read viewer + best-effort auth detect |
| `website/pages/Waitlist.jsx` | 1 | removed leftover `axios.get(/csrf)` priming next to the existing `apiV2.post` |
| `website/pages/Cohort.jsx` | 1 | public POST applications |
| `website/components/PublicVelocityTile.jsx` | 1 | public observability tile |
| `components/chat/GovernanceSignals.jsx` | 1 | second site that read wrong key `akki_token` — same latent bug, same fix |

**~20 call sites migrated; 2 latent localStorage-key bugs fixed in passing.**

## Why the shared client is better

(Repeated from sub-sprint 1 for handoff continuity)

- **CSRF double-submit** — interceptor attaches `X-CSRF-Token` automatically; ~5 hand-rolled CSRF helpers across the SPA were either wrong (wrong key) or duplicated logic.
- **Same-origin guard** — `_resolveApiBase()` swaps to `/api` when the bundle was baked for a different host than the page (prevents the SameSite=Lax cookie-loss bug that bit prod in Q1).
- **Bearer + X-Active-Context** — always attached from the canonical `akki_access_token` key, not the misnamed `akki_token` two files were reading.
- **403 csrf-retry** — the response interceptor re-fetches the token + retries once on `csrf_token_missing` / `csrf_token_invalid`. Hand-rolled fetches gave up.
- **Error normalisation** — `apiErrorMessage()` / `apiErrorCode()` exported from the same module.

## Proving slice 6/6 GREEN

Run: `cd /app/backend && python scripts/jc_wave3_axios_migration_subsprint_2_slice.py`

| Row | Subject | Outcome |
|---|---|---|
| 1 | No `from "axios"` outside `src/lib/api.js` across all `src/*.jsx` + `src/*.js` | ✓ |
| 2 | Each migrated file imports `api` / `apiV2` | ✓ |
| 3 | No `${API}/api/...` template literals in migrated files | ✓ |
| 4 | `lib/api.js` interceptor stack intact (CSRF + Bearer + X-Active-Context + 403 retry) | ✓ |
| 5 | No `useAuthHeaders` hook leftover anywhere in `src/` | ✓ |
| 6 | No ad-hoc `axios.get(.../csrf)` priming calls anywhere | ✓ |

## Frontend prod build

`yarn build` → completed in 49.62 s, zero new warnings introduced.

## Net Wave 3 progress

| | Sub-sprint 1 | Sub-sprint 2 | Total |
|---|---:|---:|---:|
| Files migrated | 4 | 7 | **11** |
| Call sites migrated | 11 | ~20 | **~31** |
| Latent bugs fixed | 0 | 2 (wrong localStorage key) | 2 |

**Wave 3 axios migration is COMPLETE.** Only the shared wrapper at `src/lib/api.js` and explicitly archived files keep an axios import.

## What's NOT touched

- `src/lib/api.js` itself — the wrapper IS the abstraction; keeping the only axios import here is the goal of the migration.
- `src/_archived_legacy/` — frozen archive surfaces.
- Hooks that internally use the `fetch` API for streaming (e.g. `useSolvaReasoningStream.js`) — out of axios scope.

## Files

- 7 frontend files (see table above)
- `backend/scripts/jc_wave3_axios_migration_subsprint_2_slice.py` — new

— END —
