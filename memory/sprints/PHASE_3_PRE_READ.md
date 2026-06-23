# Phase 3 Pre-Read — Frontend API-Boundary Contract

**Mode:** READ-ONLY reconnaissance. No code changes.
**Predecessor:** Re-Arch Phase 2 ✅ DONE (685 → 0 tenancy violations across 47 collections).
**Output classification:** **CLEAN_WITH_NOTES — backend prerequisite uncovered, ESCALATE in §9.**
**Date:** 2026-06-23.

---

## 1 · Current FE API client landscape (Q1)

### 1.A · Single canonical client + minor escape hatches

The FE has **one** canonical API client at `frontend/src/lib/api.js` (279 LOC). It wraps `axios.create({ baseURL: API_BASE, withCredentials: true })` and installs four interceptor layers:

1. **`_resolveApiBase()`** — same-origin / cross-origin guard (P5.6). Returns `/api` when the page origin doesn't match `REACT_APP_BACKEND_URL` (the bundle-vs-deploy host case).
2. **CSRF double-submit-cookie wrapper (P3.1)** — `ensureCsrfToken()` + request interceptor that injects `X-CSRF-Token` on POST/PUT/PATCH/DELETE. Auto-retry once on `csrf_token_missing` / `csrf_token_invalid`.
3. **Bearer + `X-Active-Context` headers** — per-tab membership selector (Phase A).
4. **Response error funnel** — dispatches `akki:rbac-error` / `akki:session-event` `CustomEvent`s for `MEMBERSHIP_REVOKED`, `ACTIVE_CONTEXT_REQUIRED`, `session_idle_timeout`, `session_absolute_timeout`. Includes `apiErrorMessage(err)` + `apiErrorCode(err)` helpers for downstream destructuring of `detail.code` / `detail.message`.

### 1.B · Call-site inventory (grep snapshot, 2026-06-23)

| Call shape | Count | Notes |
|---|---:|---|
| `api.{get,post,put,patch,delete}(...)` | **611** | canonical |
| Raw `fetch(...)` (excl. tests + `_archived`) | 23 | mostly `beforeunload` keepalive (DocumentDrawer L484) + public-marketing endpoints + sandbox flow |
| Direct `axios.X(...)` (excl. `lib/api.js`) | 24 | mostly the public CSRF mint path + sandbox seed flow |
| `resolveApiUrl(...)` helper | 2 | minimal use (mostly marketing surfaces still build their own URLs) |
| **TOTAL distinct API call sites** | **~660** | |

**FE page count:** 91 pages under `frontend/src/pages/` (down from the plan's "~140 untyped FE pages" estimate). **250 components** under `frontend/src/components/`. **Zero TypeScript files** under `frontend/src` (`*.ts` / `*.tsx` count = 0).

### 1.C · Typical call-site pattern (10 representative samples)

All ten samples follow the same shape: `const { data } = await api.X(path, body?)`. Response handling is **always destructure-with-defensive-fallback**, never validated. Errors propagate to surrounding try/catch and reach `toast.error()` via `apiErrorMessage(err)`.

```jsx
// pages/ArchivedChats.jsx:28
const { data } = await api.get("/chats/archived");
setItems(data.items || []);

// pages/WorkStudioAnalyze.jsx:41
const { data } = await api.post("/workbook/upload", fd, {
  headers: { "Content-Type": "multipart/form-data" },
});
const { data: full } = await api.get(`/workbook/analyses/${data.id}`);
setAnalysis(full);

// pages/cycle/CycleList.jsx:168
const { data: created } = await api.post(`/contexts/${activeContextId}/cycles`, { title: t });
navigate(created?.redirect_url || `/app/cycle/${created.id}?tab=agenda`);

// pages/TenantSettings.jsx:146
const { data } = await api.get("/accounts/me/consent-decisions");
setConsentLog(data);

// components/ask/AskPanel.jsx:145
const { data } = await api.get(`/contexts/${contextId}/ask`);

// components/monitor/ObjectivesProjectsPanel.jsx:140-144
if (r.data?.no_data) { ... }
setAssessment(r.data?.assessment || null);

// components/monitor/StrategicGoalsPanel.jsx:556
setEvolution({ events: data?.events || [], loading: false });

// components/work_studio/overlay/DocumentOverlay.jsx:987
const { data } = await api.post(...);

// pages/LensRoom.jsx:221
await api.delete(`/contexts/${cid}/lens/coach/sessions/${s.id}`);

// pages/ned/NedInbox.jsx:181
await api.post(`/ned/assignments/${it.assignment_id}/accept`);
```

**Characterisation per sample:**

| Sample | URL construction | Request body | Response handling | Error handling |
|---|---|---|---|---|
| ArchivedChats | literal | (none) | `data.items \|\| []` | try/catch → setErr(message slice) |
| WorkStudioAnalyze | literal + chained | FormData (multipart) | direct prop assignment | (none surfaced) |
| CycleList | template-string ctx_id | inline `{ title }` | `created?.redirect_url \|\| created.id` | try/catch → toast.error |
| TenantSettings | literal | (none) | direct assignment | silent (empty-state fallback) |
| AskPanel | template-string ctx_id | (none) | destructure | (downstream) |
| ObjectivesProjectsPanel | template-string ctx_id | inline | `r.data?.no_data` / `r.data?.assessment \|\| null` | (downstream) |
| StrategicGoalsPanel | template-string ctx_id | (none) | `data?.events \|\| []` | try/catch |
| DocumentOverlay | (in scope of helper) | (varies) | destructure | (downstream) |
| LensRoom | template-string ctx_id | (none) | (delete — no body) | try/catch → toast |
| NedInbox | template-string assignment_id | (none) | (action — no body) | try/catch → toast |

**Key observation:** the destructure-with-fallback pattern is universal. Response shapes are TRUSTED by convention — there's no runtime check that `data.items` is an array, no check that `created.id` exists, no check that the response is even JSON. This is the exact drift surface Phase 3 must close.

### 1.D · Existing schema validation: ZERO

- `PropTypes`: **0 imports** across `frontend/src`.
- `zod`: **declared in package.json (`zod: ^3.24.4`) but UNUSED** (0 imports anywhere in `frontend/src`). Critical finding — see §3.
- `ajv` / `yup` / `joi`: **0 dependencies**.
- Defensive optional chaining (`data?.foo`) is the de-facto validation today — it suppresses error symptoms but doesn't catch drift.

---

## 2 · OpenAPI spec availability + quality (Q2)

### 2.A · Spec served at `/api/openapi.json` (NOT `/openapi.json`)

```bash
$ curl localhost:8001/openapi.json          → 404
$ curl localhost:8001/api/openapi.json      → 200 (673177 bytes)
$ curl localhost:8001/api/docs              → 200 (Swagger UI)
$ curl localhost:8001/docs                  → 404
```

This is because FastAPI is mounted with `prefix="/api"` on the global app. **Phase 3 codegen pipeline must use the `/api`-prefixed URL.**

### 2.B · Spec scale

- **OpenAPI version:** 3.1.0
- **Total endpoints:** **697** (HTTP method × path combinations)
- **Components.schemas:** **266 typed models** (Pydantic models that ARE surfaced via `request_body` / 422 validation envelopes)
- **Spec size:** ~673 KB JSON

### 2.C · Response-typing coverage gap — MATERIAL

This is the critical Phase 3 prerequisite finding. Only 32 router handlers use `response_model=…` directive across the entire backend (`grep -rEn "response_model=" backend/routers | wc -l = 32`). The other ~660 handlers return raw `dict` / `Dict[str, Any]`, so FastAPI emits an **empty schema `{}`** for their `responses.200.content.application/json.schema`.

**Aggregate coverage:**

| Metric | Count | % |
|---|---:|---:|
| Endpoints with typed (non-empty) response 200 schema | **134 / 697** | **19.2%** ❌ |
| Endpoints with typed request body | 224 / 697 | 32.1% |
| Endpoints with EMPTY (`{}`) response 200 schema | **549 / 697** | **78.8%** |

**Hot-path coverage (the Tier 3 candidate surface):**

| Surface | Typed responses | Total endpoints | % |
|---|---:|---:|---:|
| `/api/me/*` (Home / portfolio) | 29 | 58 | 50% ✅ |
| `/api/auth/*` | 4 | 28 | 14% ❌ |
| `/api/chats/*` (Phase 14 chat) | 4 | 21 | 19% ❌ |
| `/api/contexts/{cid}/documents` (core docs) | 1 | 29 | 3% ❌ |
| `/api/contexts/{cid}/work-studio/*` (Phase 5) | 1 | 28 | 4% ❌ |
| `/api/contexts/{cid}/cycle/*` | 0 | 21 | **0%** ❌ |
| `/api/tasks/*` | 0 | 25 | **0%** ❌ |
| `/api/workbook/v2/*` (Solva v2 — Track A core) | 0 | 6 | **0%** ❌ |
| `/api/contexts/{cid}/events` | 0 | 1 | **0%** ❌ |
| **Hot-path TOTAL** | **39** | **217** | **18%** ❌ |

### 2.D · Sample endpoint inspection (5 endpoints per dispatch §Q2)

| Endpoint | Request body | Response 200 |
|---|---|---|
| `POST /api/contexts/{context_id}/work-studio/compilations` | `#/components/schemas/CompilationCreate` ✅ typed | `{}` ❌ UNTYPED |
| `GET /api/chats/{chat_id}/audit-panel` | (no body) | `{}` ❌ UNTYPED |
| `GET /api/workbook/v2/analyses/{aid}` | (no body) | `{}` ❌ UNTYPED |
| `GET /api/admin/synisense/perf` | (no body) | inline schema ✅ typed |
| `POST /api/auth/login` | `#/components/schemas/...LoginIn` ✅ typed | `{}` ❌ UNTYPED |

**Pattern:** requests are typed (FastAPI naturally requires a Pydantic body model to parse), but responses are NOT — handlers return ad-hoc dicts.

### 2.E · Phase 1 contracts → OpenAPI exposure

`backend/contracts/{synisense.py, solva.py, akki.py, types.py}` define **Python Protocols + frozen-dataclass DTOs** (679 LOC total). They are **INTERNAL typing surfaces**, not HTTP-exposed routes. There are zero paths under `/api/contracts/*` in the OpenAPI spec. The "21 contract methods" from Phase 1 live inside backend services, accessed by HTTP wrapper handlers — but those wrapper handlers (e.g. `routers/synisense.py`, `routers/workbook_analysis.py`) generally DON'T declare `response_model=` and so don't surface the DTO shape in OpenAPI.

The Phase 1 fitness function `test_invariant_contract_snapshots.py` pins the Protocol surface via `inspect.signature` snapshots (next to the test as `{contract}.contract_snapshot.json`). This protects the Python contract identity, NOT the HTTP boundary shape. Phase 3 is the HTTP-boundary equivalent.

---

## 3 · Validator library + codegen strategy (Q3)

### 3.A · Option A — Runtime-only JSON Schema validation (ajv)

| Aspect | Detail |
|---|---|
| Library | `ajv` (~120KB minified+gzip) |
| New FE code | ~80-120 LOC: wrapper `apiSchema.js` reads the committed `openapi.json` snapshot, compiles schemas per endpoint, wraps `api.X` |
| Build pipeline | Pull `/api/openapi.json` at build time (or commit a snapshot); compile once at app boot |
| Per-request overhead | ~0.5ms on a 5KB JSON; ~3-5ms on a 100KB JSON (Work Studio compile) |
| Error UX | JSON-Schema-flavoured: `"data.items[3].name: should be string, got null"` — readable but not friendly |
| Drift detection in CI | Yes — a CI step compares the deployed `openapi.json` against the committed snapshot; mismatch fails the build |
| New dependency | **+1 (ajv)** |

### 3.B · Option B — Zod with OpenAPI codegen ← **RECOMMENDED**

| Aspect | Detail |
|---|---|
| Library | `zod` (already declared in package.json `^3.24.4`, currently **UNUSED**) |
| Codegen tool | `openapi-zod-client` (~3MB devDependency, build-time only — not shipped) |
| New FE code | ~50-80 LOC for the schema-wrapping helper; the rest is generated |
| Generated code | One zod schema per `components.schemas.*` entry + one typed client method per endpoint that has either a `response_model` or a `requestBody` ref. Estimate: ~6000 LOC generated, committed to `frontend/src/lib/apiGenerated/` (regenerated by `yarn codegen`) |
| Build pipeline | `yarn codegen` runs `openapi-zod-client → frontend/src/lib/apiGenerated/`. CI compares fresh codegen against committed; mismatch fails the build. |
| Per-request overhead | ~0.3-1ms on 5KB JSON; ~2-4ms on 100KB JSON — slightly faster than ajv |
| Error UX | Fluent: `data.items[3].name expected string, received null at path: items.3.name`. Composable with custom `errorMap`. |
| Drift detection in CI | Yes — same shape as A, plus `yarn codegen --check` step fails if generated drift |
| New dependency | **0 runtime** (zod already present); **+1 devDependency** (`openapi-zod-client`) |

**Why B wins:**
1. Zod is **already a declared dependency** — no new runtime bundle weight.
2. JSDoc consumers (the few places JS files have JSDoc typings) get inferable types via `z.infer<typeof Schema>` — same effort as ajv, better tooling.
3. The codegen creates a typed `api*` client we can incrementally adopt, while keeping the existing `api.js` as the underlying axios layer. **Zero forced refactor of the 611 call sites.**
4. `openapi-zod-client` (Astahmer/openapi-zod-client on GitHub) is mature — battle-tested by other React apps consuming FastAPI backends.

### 3.C · Option C — Custom lightweight runtime validator

| Aspect | Detail |
|---|---|
| Library | None (hand-rolled) |
| New FE code | ~400-600 LOC: JSON-Schema mini-interpreter; per-endpoint registration table |
| Build pipeline | Hand-maintain schema definitions OR write a custom OpenAPI → schema converter |
| Per-request overhead | depends on impl, likely ~1-2ms (no compile optimisation) |
| Error UX | bespoke — whatever we write |
| Drift detection in CI | Possible but bespoke |
| New dependency | **0** |
| Maintenance liability | **HIGH** — every JSON Schema feature (`oneOf`, `discriminator`, `nullable`, `format`) is a new code path to implement. The 266 schemas in our spec exercise many of these. |

**Rejected.** The maintenance liability outweighs the zero-new-dep benefit. We'd be re-implementing zod badly.

### 3.D · Recommendation: Option B (zod + openapi-zod-client codegen)

Cited live evidence:
- `package.json:dependencies.zod = "^3.24.4"` (already declared).
- 91 pages + 250 components × 611 call sites = a surface too large to retrofit with hand-written validators (C) but small enough to wrap incrementally via a generated typed client (B).
- The existing `api.js` interceptor stack stays intact; the generated client is a typed layer ON TOP of it.

---

## 4 · Coverage scope tier recommendation (Q4)

### 4.A · Tier evaluation against the §2.C OpenAPI coverage gap

| Tier | Scope | Static drift catchable today (without backend prep) |
|---|---|---|
| Tier 1 — every endpoint | 697 endpoints | Only 134 (19.2%) — backend prep adds the other 80% |
| Tier 2 — Phase 1 contract-backed HTTP wrappers | ~21 endpoints | The Phase 1 contracts are Python Protocols, NOT HTTP routes. Tier 2 as defined doesn't have a direct HTTP surface — see §2.E. |
| Tier 3 — hot-path subset (chat / Solva / Work Studio / + top-trafficked) | ~217 endpoints | Only 39 (18%) typed today — backend prep adds the other 178 |

### 4.B · Recommendation: **Tier 3 (hot-path subset, ~217 endpoints)**, with Phase 3.0 backend prep

Tier 3 aligns with the user's "stop the correction spiral" objective:
- Chat / Solva / Work Studio are the LLM-coupled surfaces where shape drift bites hardest (a missing field surfaces as a silent-empty toast or a render crash).
- Hot paths are where users feel drift. Cold paths (admin / cohort / pre-account) carry less drift risk because they're touched by ~5 surfaces total.
- 217 endpoints is small enough to ship in one Phase 3 dispatch (after backend prep); 697 is not.

Tier 1 widening is reserved for **Phase 3.x follow-up** if drift surfaces in the cold paths once Tier 3 lands.

Tier 2 as currently defined isn't actionable (the contracts surface is Python, not HTTP). A near-equivalent — "all endpoints exposing a Phase 1 contract DTO via their HTTP wrapper" — needs the backend prep (§9 escalate) to make sense.

---

## 5 · Failure-mode policy recommendation (Q5)

### 5.A · Recommended: **Hybrid (fail-closed dev/staging, fail-open prod)**

| Environment | Behaviour | Why |
|---|---|---|
| `NODE_ENV=development` (local) | **Fail-closed** — throw `ApiContractViolationError`, error boundary catches | Devs see drift immediately during the change PR |
| Preview / staging deploy | **Fail-closed** — same as dev | Pre-prod catches drift before it reaches users |
| Production (`NODE_ENV=production`) | **Fail-open + log** — return the unvalidated payload as-is + emit `akki:contract-violation` `CustomEvent` for Sentry capture | Users don't see a broken page from a backend change that's already deployed; the team gets the signal via Sentry's "contract violations" channel |

### 5.B · Justification against "no diversions, no rework"

- **Fail-closed in prod** would convert backend deploys with response-shape changes into hard user-visible outages. That creates new diversions: hotfix PR + redeploy + rollback panic.
- **Fail-open in prod with Sentry capture** preserves user trust (graceful degradation) while routing the drift signal to the team via the existing observability channel (`akki:contract-violation` mirrors the existing `akki:rbac-error` / `akki:session-event` pattern in `lib/api.js:224-246`).
- **Fail-closed in dev/staging** means drift is caught at PR-review time (when the engineer is paying attention) — not at deploy time (when nobody is).

### 5.C · Implementation sketch (informational; not Phase 3 Pre-Read scope)

```js
// frontend/src/lib/apiContract.js
function _failurePolicy() {
  if (process.env.NODE_ENV !== "production") return "throw";
  if (process.env.REACT_APP_BACKEND_URL?.includes("preview.emergentagent.com")) return "throw";
  return "log";
}

export async function validatedCall(schema, axiosCall) {
  const resp = await axiosCall();
  const result = schema.safeParse(resp.data);
  if (!result.success) {
    if (_failurePolicy() === "throw") {
      throw new ApiContractViolationError(result.error, resp);
    }
    window.dispatchEvent(new CustomEvent("akki:contract-violation", {
      detail: { schema: schema._def.typeName, error: result.error, url: resp.config.url },
    }));
    return resp;  // forward raw payload
  }
  return { ...resp, data: result.data };
}
```

---

## 6 · Fitness function shape (Q6)

### 6.A · FE-side: every API client method has a schema

```js
// frontend/src/lib/__tests__/contractCompleteness.test.js
test("every endpoint in the OpenAPI snapshot has a zod schema", () => {
  const spec = require("../../../openapi.snapshot.json");
  const generated = require("../apiGenerated/schemas.gen.js");
  const expected = Object.keys(spec.paths).flatMap(p =>
    Object.keys(spec.paths[p]).filter(m => HTTP_METHODS.includes(m))
      .map(m => `${m.toUpperCase()} ${p}`)
  );
  const actual = Object.keys(generated);
  expect(expected.sort()).toEqual(actual.sort());
});
```

**Estimated LOC:** ~30. Runs as part of `yarn test` + a CI step.

### 6.B · Backend-side: every Phase 1 contract method's HTTP wrapper has a `response_model`

```python
# backend/tests/invariants/test_invariant_http_response_model.py
def test_every_hot_path_route_declares_response_model():
    """Hot-path routes (chat / solva / work-studio / cycle / tasks / docs /
    events) MUST declare response_model=... so the OpenAPI spec carries
    a typed response shape. This drives the FE zod codegen."""
    HOT_PATH_PREFIXES = (
        "/api/chats", "/api/contexts/{cid}/work-studio",
        "/api/workbook/v2", "/api/tasks", "/api/contexts/{cid}/cycle",
        "/api/contexts/{cid}/documents", "/api/contexts/{cid}/events",
        "/api/auth", "/api/me",
    )
    untyped = []
    for route in app.routes:
        if not isinstance(route, APIRoute): continue
        if not any(route.path.startswith(p.replace("{cid}", "{context_id}") or p)
                   for p in HOT_PATH_PREFIXES): continue
        if route.response_model is None:
            untyped.append((list(route.methods)[0], route.path))
    assert untyped == [], (
        f"Hot-path routes missing response_model=: {untyped}\n"
        f"Add response_model=<PydanticModel> so OpenAPI emits the shape."
    )
```

**Estimated LOC:** ~60. **Build-breaking** (sibling of `test_invariant_tenancy.py`).

### 6.C · CI step: OpenAPI snapshot drift

```yaml
# .github/workflows/openapi-drift.yml (or equivalent)
- name: Generate FE schemas from backend OpenAPI
  run: yarn codegen
- name: Fail if generated schemas drift from committed
  run: git diff --exit-code frontend/src/lib/apiGenerated/
```

**Estimated LOC:** ~15 in the workflow + a `yarn codegen` script in `package.json`.

### 6.D · Total fitness function delta

| Fitness function | Layer | LOC | Build-breaking? |
|---|---|---:|---|
| `contractCompleteness.test.js` | FE | ~30 | Yes |
| `test_invariant_http_response_model.py` | BE | ~60 | Yes |
| `yarn codegen --check` in CI | CI | ~15 | Yes |
| **Total** | | **~105** | |

**Minimal set delivering static-catch on drift: all three.** FE-side catches FE drift; BE-side catches missing `response_model`; CI catches schema-version drift between backend and frontend.

---

## 7 · Sub-dispatch sequencing (Q7)

### 7.A · Three sub-dispatches

| Sub-phase | Scope | Build hours | Goldens at risk |
|---|---|---:|---|
| **Phase 3.0 — Backend prep: response_model on hot-path routes** | Add `response_model=...` to ~178 hot-path routes that currently emit `{}` response schemas. Use existing Pydantic models where present; add new `*Out` models where the route returns a freshly-built dict. Ship `test_invariant_http_response_model.py` (Q6.B). | 2.5-3 | Track A 4/5/6/7 lockdowns (any FastAPI response_model coercion that changes the wire shape — mitigated by adding model that EXACTLY matches existing dict shape). Chat / Solva real-LLM rounds. |
| **Phase 3.1 — FE codegen pipeline + zod runtime wrapper** | `yarn add -D openapi-zod-client`; commit `yarn codegen` script + generated `lib/apiGenerated/`; write `lib/apiContract.js` (validatedCall helper + fail-open/closed policy); commit `openapi.snapshot.json`; ship Q6.A contractCompleteness test + Q6.C CI step. | 2-2.5 | None (additive layer; existing call sites untouched). |
| **Phase 3.2 — Hot-path migration to typed client** | Migrate the 39 already-typed + 178 newly-typed = 217 hot-path call sites to the generated typed client. Each migration replaces `const { data } = await api.X(path)` with `const data = await apiTyped.X.something()`. Behaviour-preserving — wire shape unchanged. | 1-1.5 | Track A 4/5/6/7 lockdowns + Phase 14/15 lockdowns (any drift between the generated schema and runtime payload surfaces as a failed assertion). |
| **Total** | | **5.5-7 hours** | |

Aligns with the plan's "2-3 dispatches, 5-7 build hours" estimate.

### 7.B · Acceptance criteria per sub-phase

**Phase 3.0 acceptance:**
- ~178 hot-path routes carry `response_model=...`.
- `/api/openapi.json` shows typed responses for 217/217 hot-path endpoints (100%).
- `test_invariant_http_response_model.py` green and build-breaking.
- All existing Track A + Phase 14/15 lockdowns + Phase 2 invariants green.
- Zero behaviour change (response_model is filter-only; if backend returns dict matching the model, runtime payload is identical).
- Sprint memo `PHASE_3_0_RESPONSE_MODEL_PREP.md`.

**Phase 3.1 acceptance:**
- `yarn codegen` runs cleanly and produces deterministic output.
- Generated `lib/apiGenerated/schemas.gen.js` + `apiTyped.gen.js` committed.
- `openapi.snapshot.json` committed (used by `contractCompleteness` test).
- `validatedCall(schema, axiosCall)` helper in `lib/apiContract.js`.
- Hybrid fail-policy active (`process.env.NODE_ENV` gate).
- `contractCompleteness.test.js` green in CI.
- `git diff --exit-code` check active in CI.
- All existing FE smoke tests pass.
- Sprint memo `PHASE_3_1_CODEGEN_AND_WRAPPER.md`.

**Phase 3.2 acceptance:**
- 217/217 hot-path call sites migrated to `apiTyped.*`.
- Zero `api.{get,post,put,patch,delete}(...)` calls remain inside hot-path components for these endpoints.
- Existing `api.js` interceptor stack still in use (axios underneath).
- All Track A 4/5/6/7 + Phase 14/15 lockdowns green.
- No new error toasts surfaced under hybrid policy in preview/staging during a 24-hour soak.
- Sprint memo `PHASE_3_2_HOT_PATH_MIGRATION.md`.

### 7.C · Phase 3 ⊕ side-lane Phase 2.X items

Phase 2.X side-lane (48 cross-context calls + 15 pre-existing test failures + 3 boundary imports) remains parallel/independent. Phase 3 does NOT block it; Phase 2.X does NOT block Phase 3.

---

## 8 · Discrepancies with approved plan (Q8)

### 8.A · "~140 untyped FE pages" → actual 91 pages + 250 components

The plan §5 estimate of "~140 untyped FE pages" is **an under-count of the broader FE surface**:
- 91 page files
- 250 component files
- 611 `api.X(...)` call sites total
- The "page" count is now 91 (likely shrunk via Phase 14/15 consolidation + Phase B5 deletions). Component count is 250 — these ALSO contain API calls that need migrating.

**Impact:** Phase 3.2's "migrate hot-path call sites" scope is ~217 call sites spread across pages AND components, not just pages. Estimate (1-1.5 build hours) accommodates this. No plan revision needed.

### 8.B · Phase 1 backend contracts are Python-only, NOT HTTP-exposed

The plan §5 reads: "Generate typed response contracts / runtime schema validation at the API client layer from the backend contracts (OpenAPI)." This implies the backend contracts (`backend/contracts/*.py`) drive the OpenAPI shape. In reality:
- `backend/contracts/{akki,solva,synisense}.py` are **Python Protocols + frozen dataclasses** — INTERNAL service-layer types.
- The HTTP wrappers in `backend/routers/` that surface these protocols mostly DON'T declare `response_model=` — so the OpenAPI spec carries `{}` for their response shapes.

**Impact:** Phase 3 cannot directly bind FE schemas to Phase 1 contract DTOs without first making the HTTP wrappers declare typed response models. This is the Phase 3.0 backend prep — see §9 ESCALATE.

### 8.C · OpenAPI completeness is the blocker

| Surface | Typed responses | Total | % |
|---|---:|---:|---:|
| All endpoints | 134 | 697 | 19.2% |
| Hot-path (Tier 3) | 39 | 217 | 18% |

**Impact:** Phase 3.1 + 3.2 are NOT viable in isolation. Without Phase 3.0 backend prep, the FE zod codegen would generate validators for only 18% of hot-path calls; the other 82% would have NOTHING to validate against. This contradicts the "stop the correction spiral" objective.

### 8.D · No TypeScript migration required

All three validator strategies (A, B, C) can run on `.js` / `.jsx` files. Zod schemas produce type info via `z.infer<>` ONLY when consumed in TypeScript; in JS files, they remain pure runtime validators with JSDoc-friendly inferred shapes. **No `.ts` / `.tsx` introduction needed for Phase 3.** This aligns with the plan's "NOT a TS rewrite of the ~140 pages."

### 8.E · Latency

Validator overhead on hot paths (zod safeParse over 5-100KB JSON): 0.3-5ms per call. Chat send / Solva analyze / Work Studio compile take 2-30 seconds end-to-end (LLM round-trip). Validator overhead is **<0.1% of perceived latency** on hot paths. Below the 50ms escalation threshold.

---

## 9 · ESCALATE TO USER

**One material discrepancy, one decision needed:**

### ESCALATE — OpenAPI response-typing coverage is 18% on hot paths

The plan §5 assumes the OpenAPI spec is the FE codegen source. The current spec carries typed response schemas for only **19.2% of all endpoints (134/697)** and **18% of hot-path endpoints (39/217)**. The other 82% of hot paths emit `responses.200.content.application/json.schema = {}` because their FastAPI handlers don't declare `response_model=...`.

**Implication for Phase 3 scope:** the zod codegen (Phase 3.1) and the hot-path migration (Phase 3.2) cannot ship in isolation. Without typed responses to bind to, the generated schemas would be empty `z.any()` for 82% of hot-path calls — equivalent to no validation, and trivially passes any drift.

**Two decisions:**

**Decision 1 — Backend prep dispatch (Phase 3.0):**
- (a) **Ship Phase 3.0 first** as a focused backend-side dispatch: add `response_model=...` to the ~178 untyped hot-path routes using existing Pydantic models where present (most of the 266 schemas are already declared as request bodies — reusable) + add minimal `*Out` models where the route builds a fresh dict. Build-breaking invariant `test_invariant_http_response_model.py`. Same shape as Phase 2 sub-phases (mechanical, behaviour-preserving). Estimated 2.5-3 build hours. **Then** Phase 3.1 + 3.2.
- (b) Defer Phase 3 entirely until a backend prep can be funded separately (slows the "stop the correction spiral" objective).
- (c) Ship Phase 3.1/3.2 only against the existing 18% — accept that 82% of hot-path calls have no drift catch. Re-scope as "Phase 3 Tier 3-narrow" with explicit ⚠️ that the coverage gap persists.

**Decision 2 — Tier confirmation:**
- (a) Tier 3 (hot-path subset, ~217 endpoints) — recommended in §4.
- (b) Tier 1 (all 697 endpoints) — requires 549 `response_model` adds in Phase 3.0, ~4× the backend prep cost.
- (c) Tier 3-narrow per §9 Decision 1.c — ship against existing 18% only.

**Recommended pair:** Decision 1.a + Decision 2.a. (Phase 3.0 backend prep + Tier 3 scope.)

---

## 10 · Recommended Phase 3.1 dispatch scope

**Conditional on §9 Decision 1.a (Phase 3.0 backend prep ships first).**

After Phase 3.0 closes (hot-path response_model coverage = 100%), Phase 3.1 ships:

| Item | Scope |
|---|---|
| `yarn add -D openapi-zod-client` (~3MB devDependency) | New tooling |
| `package.json` scripts: `"codegen": "openapi-zod-client -i http://localhost:8001/api/openapi.json -o src/lib/apiGenerated/ ..."` | Build wiring |
| `frontend/src/lib/apiGenerated/{schemas.gen.js, apiTyped.gen.js}` | Generated artefacts (committed) |
| `frontend/openapi.snapshot.json` | Committed OpenAPI snapshot (driving the codegen + the FE completeness test) |
| `frontend/src/lib/apiContract.js` | ~80 LOC: `validatedCall()` + `ApiContractViolationError` + hybrid fail-policy |
| `frontend/src/lib/__tests__/contractCompleteness.test.js` | ~30 LOC: every endpoint has a schema |
| CI step: `yarn codegen --check` | ~15 LOC |
| Phase 3.1 sprint memo | `/app/memory/sprints/PHASE_3_1_CODEGEN_AND_WRAPPER.md` |

**Phase 3.1 acceptance criteria (verbatim from §7.B):**
- `yarn codegen` runs cleanly and produces deterministic output.
- Generated artefacts committed.
- `openapi.snapshot.json` committed.
- `validatedCall(schema, axiosCall)` helper live in `lib/apiContract.js`.
- Hybrid fail-policy active (`process.env.NODE_ENV` gate).
- `contractCompleteness.test.js` green in CI.
- `git diff --exit-code` check active in CI.
- All existing FE smoke tests pass.

**Out of Phase 3.1 scope (deferred to Phase 3.2):**
- Migration of existing 217 hot-path call sites to `apiTyped.*` — Phase 3.1 ships the typed client AS AN ADDITIVE LAYER. The existing 611 `api.X(...)` calls keep working unchanged. Phase 3.2 migrates the hot-path subset.

---

**End of Phase 3 Pre-Read. Output: CLEAN_WITH_NOTES — §9 ESCALATE on OpenAPI coverage gap requires user decision before Phase 3 build dispatch.**
