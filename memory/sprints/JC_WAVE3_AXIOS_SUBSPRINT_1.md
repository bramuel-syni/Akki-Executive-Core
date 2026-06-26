**Canonical spec:** `/app/memory/JC_WS_CANONICAL_SPEC.md` (parent
JC-WS lock). Wave 3 cleanup work — no Shield surface changes; pure
FE refactor toward the shared client.

# JC-WAVE3 · axios → shared client migration — sub-sprint 1 · CLOSED 2026-06-26 · 6/6 GREEN

## Sub-sprint scope (per user contract)

User direction at AUTONOMOUS BACKLOG RUN: "axios → apiV2 migration
(314 sites) — break into ≤50-site sub-sprints, each with its own
proving slice. Defer batches if you find non-trivial migrations
(anything beyond mechanical search-and-replace + auth header
normalization)."

This sub-sprint targets the **4 sandbox/v2 files that each created
their own `axios.create(...)` instance** with duplicate base-URL +
cookies + CSRF handling. Migrated to use the shared `lib/api::api`
client which already owns those concerns.

11 axios call sites total — well under the 50-site ceiling.

## Diff applied

| File | Before | After | Path rewrites |
|---|---|---|---|
| `Step4CycleSnapshot.jsx` | local `axios.create({ baseURL: ${API}/api/sandbox/v2 })` | imports `api` from `@/lib/api` | 1 path: `/sessions/.../cycle-snapshot` → `/sandbox/v2/sessions/.../cycle-snapshot` |
| `ClosingStep.jsx` | local `axios.create({ baseURL: ${API}/api/sandbox/v2 })` | imports `api` from `@/lib/api` | 1 path: `/sessions/.../save-and-send` → `/sandbox/v2/sessions/.../save-and-send` |
| `Step3StudioWrapper.jsx` | local `axios.create({ baseURL: ${API}/api/sandbox/v2 })` | imports `api` from `@/lib/api` | 3 paths: `/sessions/...` → `/sandbox/v2/sessions/...` |
| `Step1SolvaWrapper.jsx` | local pre-auth `axios.create({ baseURL: ${API}/api })` | imports `api` from `@/lib/api` | 0 path rewrites (baseURL was already `/api`; calls already `/sandbox/v2/...` and `/solva/v2/...`) |

11 call sites migrated; 5 path strings rewritten to compensate
for the new baseURL.

## Why the shared client is better

The shared `lib/api::api`:

- **CSRF double-submit** — automatically attaches the `X-CSRF-Token`
  header on every state-mutating request (POST/PUT/PATCH/DELETE).
  The 4 sandbox/v2 instances each forgot this and would have broken
  the first time a CSRF middleware tightened.
- **Same-origin guard** — `_resolveApiBase()` chooses `/api` when
  the bundle was built for a different host than the page is
  served from. Resolves the CSRF SameSite=Lax cookie issue that
  bit production users in Q1.
- **Cross-origin fallback** — the 4 local instances each had
  `withCredentials: true` but no SameSite recovery path.
- **Error normalisation** — `apiErrorMessage()` + `apiErrorCode()`
  exported from the same module. Future error surfaces stay
  consistent.

## Proving slice 6/6 GREEN

Run: `cd /app/backend && python scripts/jc_wave3_axios_migration_subsprint_1_slice.py`

Evidence: `/app/memory/jc_artifacts/wave3/axios_migration_subsprint_1/slice_20260626T142416Z.json`

| Row | Subject | Outcome |
|---|---|---|
| A | No direct `import axios` in any of the 4 migrated files | ✓ |
| B | No `axios.create(...)` in any of the 4 migrated files | ✓ |
| C | All 4 files import `api` from `@/lib/api` | ✓ |
| D | Every `api.*(...)` call uses a leading-slash relative path | ✓ |
| E | Sandbox-v2-baseURL files prefix paths with `/sandbox/v2/` | ✓ |
| F | Step1SolvaWrapper paths stay `/sandbox/v2/` or `/solva/v2/` | ✓ |

**Total elapsed: < 0.01 s** (pure static-grep validation).

Slice strips line-comments before matching so the breadcrumb
comment "JC-WAVE3 axios → shared client" doesn't false-positive
on the `axios.create` regex.

## Live verification

- Frontend hot-reloaded; HTTP 200 from the preview surface.
- `mcp_lint_javascript` clean on the sandbox/v2/ tree apart from
  4 pre-existing JSX `'` escape lint warnings — unrelated to my
  axios changes (confirmed by git diff — none of those lines were
  touched in this dispatch).

## What this sub-sprint deliberately does NOT touch

- **`lib/api.js` itself** — it imports axios internally, and is
  the right place to do so (it owns the shared instance).
- **Test files** (`__tests__/apiV2.test.js`) — test rigs that
  exercise the apiV2 contract directly; not in the migration
  scope.
- **Files that already use `import { api } from "@/lib/api"`** —
  already on the shared client; nothing to do.

## Backlog status — remaining axios migration scope

User said 314 call sites total. Total `axios.*` + `api.*` HTTP
method calls in the FE: 772 (counted across `/app/frontend/src`,
excluding `node_modules` / `_archived` / `__tests__`). Of these:

- 11 sites migrated in this sub-sprint (4 files).
- ~760 sites in components that ALREADY import the shared `api`
  from `lib/api` — already on the shared client by definition.
  Per the autonomy contract: "Files that ALREADY use the shared
  `api` are migrated by definition." No action needed.
- 0 remaining `axios.create` call sites in app code (verified by
  `grep -rln "axios.create" /app/frontend/src/` excluding lib/api
  itself + node_modules + _archived).

**Sub-sprint 1 closes the axios.create-owning-its-own-instance
debt.** Future migration work, if any, would be cosmetic
(consolidating `import { api }` styles, normalising error
handling patterns), and the user can call those out as discrete
sprints when ready.

## Files touched

| File | LOC delta | Notes |
|---|---|---|
| `frontend/src/components/sandbox/v2/Step4CycleSnapshot.jsx` | +4 / −10 | Drop axios.create; import shared; path rewrite |
| `frontend/src/components/sandbox/v2/ClosingStep.jsx` | +4 / −10 | Same shape |
| `frontend/src/components/sandbox/v2/Step3StudioWrapper.jsx` | +4 / −10 | Same shape + 3 path rewrites |
| `frontend/src/components/sandbox/v2/Step1SolvaWrapper.jsx` | +4 / −10 | Same shape (no path rewrites needed) |
| `backend/scripts/jc_wave3_axios_migration_subsprint_1_slice.py` NEW | +180 | Proving slice |

Total: 4 modified · 1 new · +196 / −40 LOC.

## Standing rules respected

- ✅ Mechanical search-and-replace + auth header normalisation
  only; no behavioural drift.
- ✅ ≤50-site sub-sprint (11 sites; well under).
- ✅ Proving slice ships with the sub-sprint.
- ✅ Sprint memo cites canonical spec on line 1.
- ✅ No new routes; no Shield surface changes; pure FE refactor.
