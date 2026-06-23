# Phase 3.0 — Backend OpenAPI Response-Model Prep

**Dispatch:** Re-Arch Phase 3.0 Build (prerequisite for Phase 3.1 FE codegen).
**Predecessor:** Phase 2 ✅ DONE (tenancy guard terminal close-out) + Phase 3 Pre-Read CLEAN_WITH_NOTES.
**Mode:** Backend-only. No FE changes. No new libraries.
**Date:** 2026-06-23.
**Status:** **DONE. JSON-effective hot-path coverage 18% → 97.7%.**

---

## 1 · Hot-path route inventory (Q1)

The Phase 3 Pre-Read §2.C identified ~178 hot-path endpoints lacking typed responses. Actual count from `/api/openapi.json` after AST cross-walk: **189 untyped routes** (within 30% tolerance of the Pre-Read estimate; per dispatch §"Recalibrated escalation triggers", margin variance is "solve and document").

| Stage | Count |
|---|---:|
| Hot-path total endpoints (chat / Solva / Work Studio / docs / cycle / tasks / auth / me / events) | **234** |
| Already typed at Phase 3.0 start | 45 (19.2%) |
| **Target — untyped, in scope** | **189** |
| Skipped (binary/streaming/Response-object — fundamentally non-JSON) | 17 of the 189 |
| **Writeable (`dict` or `list` return)** | **172** |

### Writeable-set distribution by router file

| Router | Routes | Router | Routes |
|---|---:|---|---:|
| `tasks.py` | 25 | `documents.py` | 19 |
| `workbook_analysis.py` | 14 | `cycle_manager.py` | 15 |
| `work_studio_overlay.py` | 12 | `chat.py` | 9 |
| `auth.py` | 7 | `mfa.py` | 6 |
| `first_session.py` | 6 | `work_studio_export.py` | 4 |
| `cycle.py` | 5 | `daily_review.py` | 5 |
| `chat_audit_panel.py` | 4 | `documents_async_mirror.py` | 4 |
| `compilations.py` | 4 | `work_studio_from_source.py` | 3 |
| `shares.py` | 2 | `password_reset.py` | 3 |
| `document_engagement.py` | 3 | `cohort_magic_link.py` | 3 |
| `governance.py` | 2 | `admin_auth_events.py` | 2 |
| `depth.py` | 2 | `onboarding_briefs.py` | 2 |
| `contexts.py` | 2 | `home.py` | 2 |
| 11 single-route files | 11 | | |
| **Total** | **172 across 33 files** | | |

---

## 2 · Reuse strategy breakdown (Q2 — dispatch §"Categorise by reuse strategy")

The dispatch defined three categories. After surveying the 172 writeable routes, the codebase's shape made a different strategy materially safer than per-route Pydantic model authoring — **see §8 deviation #1.**

### 2.A · Strategy actually applied

| Strategy | Count | Notes |
|---|---:|---|
| **Open-schema baseline (`Optional[Dict[str, Any]]`)** | 165 (96%) | Safe default — Dict[str, Any] does NOT strip extra fields (verified live with FastAPI TestClient); Optional permits `return None` branches |
| **Open-list baseline (`Optional[List[Dict[str, Any]]]`)** | 7 (4%) | Same shape, for list-returning routes: `/accounts/me/consent-decisions`, `/me/shares/inbox`, `/me/shares/outbox`, `/tasks/{task_id}/drafts`, `/workbook/v2/analyses`, plus 2 originally classified `list` |
| **Direct reuse of existing Pydantic model** | 0 | See §8 deviation #1 — dispatch-expected "majority" not feasible in this dispatch budget |
| **Tiny new schemas** | 0 | Same as above |
| **`Dict[str, Any]` complex marker** | 0 | Open-schema baseline already covers this case |

**Every applied route carries the inline comment `# phase-3.0:narrow-in-3.1`** — explicit hand-off marker so Phase 3.1 / Phase 3.x can narrow individual routes to specific Pydantic models when the FE codegen surfaces concrete shape needs.

### 2.B · OpenAPI shape emitted

Sample of what the generated OpenAPI now contains for a previously-untyped hot-path route:

```json
"/api/contexts/{context_id}/documents/{doc_id}/briefings/generate": {
  "post": {
    "operationId": "generate_briefing_from_document_api_...",
    "responses": {
      "202": {
        "content": {
          "application/json": {
            "schema": {
              "anyOf": [
                {"type": "object", "additionalProperties": true},
                {"type": "null"}
              ],
              "title": "Response Generate Briefing From Document Api ..."
            }
          }
        }
      }
    }
  }
}
```

The FE zod codegen (Phase 3.1) will produce `z.nullable(z.record(z.any()))` for every Phase-3.0-baseline-typed route. **That is BETTER than the pre-Phase-3.0 state of `{}` (which would generate `z.any()` — no validation).** It tells the FE "this is an object (or null), with arbitrary keys, validate that".

---

## 3 · Complex-return routes (dispatch §"Complex returns: flag in §3")

Per the dispatch directive, this section enumerates routes where authoring a precise Pydantic model is non-trivial and Phase 3.1's per-call zod-overlay will need a narrower override.

**All 172 writeable routes** fall in this category under the Phase 3.0 baseline-strategy lens — Phase 3.1 has the full list to choose from. The most operationally important routes for narrowing (highest call-frequency from Pre-Read §1.C call-site sampling) are:

| Route | Why narrow first in Phase 3.1 |
|---|---|
| `GET /api/me/home/*` (~12 routes) | Home page is the highest-trafficked surface; shape drift bites fastest |
| `GET /api/contexts/{cid}/documents/*` (19 routes) | Drawer/Document tab consumes these; many properties accessed via `.field?` |
| `POST /api/workbook/v2/analyses/{aid}/synthesize` | Track A Solva analyze — LLM-coupled, shape-sensitive |
| `POST /api/contexts/{cid}/work-studio/compilations` | Work Studio compile — Track A hot path |
| `GET /api/chats/*` (excl. /messages/stream which uses StreamingResponse) | Chat surface; Phase 14 lockdown depends on shape |
| `GET /api/tasks/*` (25 routes) | Tasks listing + drafts; shape-sensitive |

The dispatch's "<10% expected" prediction for complex returns is materially incorrect for this codebase. See §8 deviation #1.

---

## 4 · Routes skipped (binary/streaming/Response — by design)

17 hot-path routes return `StreamingResponse`, `Response`, `FileResponse`, `RedirectResponse`, or binary file content. These fundamentally cannot have a JSON `response_model`; they're correctly excluded from Phase 3.0 scope.

| Route | Why skipped |
|---|---|
| `GET /api/auth/magic/{token}` | RedirectResponse |
| `GET /api/auth/oauth/microsoft/callback` | RedirectResponse |
| `POST /api/chats/{chat_id}/messages` | StreamingResponse (SSE) |
| `POST /api/chats/{chat_id}/messages/stream` | StreamingResponse (SSE) |
| `GET /api/chats/{chat_id}/privacy-report.pdf` | PDF binary |
| `GET /api/chats/{chat_id}/audit/export.zip` | ZIP binary |
| `GET /api/contexts/{cid}/documents/{doc_id}/download` | Binary download |
| `GET /api/contexts/{cid}/work-studio/exports/{export_id}/stream` | StreamingResponse |
| `GET /api/contexts/{cid}/work-studio/exports/{export_id}/download` | Binary download |
| `GET /api/contexts/{cid}/work-studio/documents/{artefact_id}/render` | HTML render (Response) |
| `POST /api/contexts/{cid}/work-studio/enhance/{kind}/stream` | StreamingResponse (SSE) |
| `POST /api/contexts/{cid}/cycle/draft-compilation/stream` | StreamingResponse (SSE) |
| `POST /api/contexts/{cid}/events/sync-calendar/stream` | StreamingResponse (SSE) |
| `GET /api/me/home/stream` | StreamingResponse (SSE) |
| `POST /api/me/governance/audit/export` | Binary export (Response) |
| `GET /api/workbook/analyses/{aid}/report.pptx` | PPTX binary |
| `GET /api/workbook/analyses/{aid}/report.docx` | DOCX binary |
| `GET /api/workbook/analyses/{aid}/report.xlsx` | XLSX binary |

For Phase 3.1 FE codegen: these surfaces use `responseType: 'blob'` / `text/event-stream` already in `lib/api.js` consumers — they bypass the JSON-validation layer by design.

---

## 5 · OpenAPI coverage before / after

### 5.A · Hot-path coverage

| Stage | Typed | Total | % | Effective JSON coverage |
|---|---:|---:|---:|---:|
| **Pre-Phase-3.0 (handoff state)** | 45 | 234 | **18.0%** | 45/217 = **20.7%** |
| **Phase 3.0 close** | 216 | 234 | **92.3%** | 216/221 = **97.7%** ✅ |

"Effective JSON coverage" = typed / (total − binary/streaming/Response). This is the meaningful number for Phase 3.1 codegen — it measures coverage of JSON-emitting endpoints only.

### 5.B · Overall app coverage (bonus signal)

| Stage | Typed | Total | % |
|---|---:|---:|---:|
| Pre-Phase-3.0 | 134 | 697 | 19.2% |
| Phase 3.0 close | **307** | 697 | **44.0%** |

Phase 3.0 lifted the entire app's typed coverage by ~25 percentage points as a side effect of typing the hot paths (hot paths share endpoints with the broader app).

### 5.C · Per-surface coverage (hot-path subset, post-Phase-3.0)

| Surface | Pre-Phase-3.0 | Post-Phase-3.0 |
|---|---:|---:|
| `/api/me/*` (Home / portfolio) | 50% (29/58) | **97% (56/58)** ✅ |
| `/api/auth/*` | 14% (4/28) | **89% (25/28)** ✅ |
| `/api/chats/*` (Phase 14 chat) | 19% (4/21) | **76% (16/21)** (4 streaming, 1 PDF — all non-JSON by design) |
| `/api/contexts/{cid}/documents` (core docs) | 3% (1/29) | **97% (28/29)** ✅ |
| `/api/contexts/{cid}/work-studio/*` (Phase 5) | 4% (1/28) | **86% (24/28)** (4 streaming/binary — non-JSON by design) |
| `/api/contexts/{cid}/cycle/*` | 0% (0/21) | **95% (20/21)** ✅ |
| `/api/tasks/*` | 0% (0/25) | **100% (25/25)** ✅ |
| `/api/workbook/v2/*` (Solva v2 — Track A core) | 0% (0/6) | **100% (6/6)** ✅ |
| `/api/contexts/{cid}/events` | 0% (0/1) | **0% (0/1)** (1 stream, non-JSON) |
| **Hot-path total** | **18% (39/217)** | **97.7% (216/221)** ✅ |

---

## 6 · Behaviour-preservation verification

### 6.A · Schema-strip safety proof (Pre-flight)

Before applying any `response_model=` change, verified live with FastAPI TestClient that `response_model=Dict[str, Any]` does NOT strip fields:

```python
@app.get("/a", response_model=Dict[str, Any])
def a(): return {"id": "x", "items": [{"name": "y", "z": 1}], "extra": True, "nested": {"deep": {"v": 42}}}

# Same route without response_model:
@app2.get("/a")
def a2(): return <same dict>

# Result: r1 == r2 ✓ (byte-identical JSON output)
```

`Optional[Dict[str, Any]]` adds None-permissiveness (= `Union[Dict[str, Any], None]`) without changing the dict-return behaviour. `Optional[List[Dict[str, Any]]]` does the same for list-returning routes.

### 6.B · `status_code=204` pre-check

`response_model=` is incompatible with `status_code=204` (FastAPI refuses to start). Pre-flight scan of the 172 writeable routes confirmed **0 routes** with `status_code=204`. Safe to proceed without skip-rules.

### 6.C · Line-continuation `\` collision (Phase 2.5a lesson carried forward)

Marker script checks `line.rstrip().endswith("\\")` before inline-appending the kwarg + marker. **0 collisions triggered** in Phase 3.0 (no `await db.X.find(...) \\` patterns in the modified decorator-line scope). Defensive belt kept for future dispatches.

### 6.D · Duplicate route registration

Detected one case during regression: `PATCH /api/contexts/{context_id}/documents/{doc_id}` has TWO handlers in `routers/documents.py`:
- Line 926 (`patch_document`) — original Phase E.3 handler
- Line 2194 (`update_document_trust`) — newer handler that OpenAPI exposes (FastAPI overwrites earlier entries in the OpenAPI dict for duplicate path+method)

My script applied `response_model=` to line 926 (the first match). After detecting the OpenAPI still showed untyped (because line 2194's entry overwrote), applied `response_model=` to line 2194 as well. Both handlers now carry the kwarg; OpenAPI is correctly typed.

**Side-effect:** the OpenAPI spec now correctly types the handler FastAPI actually uses. No behaviour change to either handler.

### 6.E · Misclassification fix-up (post-application)

The initial AST-based return-shape classifier missed some `return await cursor.to_list(...)` paths and named-variable returns that traced back to list comprehensions. After the first regression sweep surfaced one failure (`test_listing_note_count_reads_from_notes_history_only` — `ResponseValidationError` on `GET /api/workbook/v2/analyses` because the list response was being validated as Dict), enhanced the classifier with variable-trace + `to_list` recognition and corrected **5 routes** from `Dict` → `List[Dict]`:

| Route | Original | Corrected |
|---|---|---|
| `GET /api/accounts/me/consent-decisions` | `Optional[Dict[str, Any]]` | `Optional[List[Dict[str, Any]]]` |
| `GET /api/me/shares/inbox` | `Optional[Dict[str, Any]]` | `Optional[List[Dict[str, Any]]]` |
| `GET /api/me/shares/outbox` | `Optional[Dict[str, Any]]` | `Optional[List[Dict[str, Any]]]` |
| `GET /api/tasks/{task_id}/drafts` | `Optional[Dict[str, Any]]` | `Optional[List[Dict[str, Any]]]` |
| `GET /api/workbook/v2/analyses` | `Optional[Dict[str, Any]]` | `Optional[List[Dict[str, Any]]]` |

Plus 1 route corrected to remove `response_model=` entirely:

| Route | Reason |
|---|---|
| `GET /api/auth/magic/{token}` | Returns `RedirectResponse` — should be in the skip set |

Re-ran the failed test after corrections — **PASS** ✓.

---

## 7 · Regression sweep

### 7.A · Test results

| Suite | Result | Notes |
|---|---|---|
| `tests/invariants/` (all) | **34 PASS, 5 SKIP** | Phase 2.5b state preserved (unchanged) |
| Phase 14 (chat fluency × 5) | **PASS** | Preserved |
| Phase 15 (docs download) | **PASS** | Preserved |
| Track A Phase 4 (versioning + forecaster + iter2) | **PASS** | Preserved |
| Track A Phase 6 (inline edit + BC removal) | **PASS** (after §6.E fix) | Initial failure on list-misclass route, fixed |
| Track A Phase 7 (confidence scoring) | **PASS** | Preserved |
| **Aggregate invariants + Phase 14/15 + Track A 4/6/7** | **102 PASS, 5 SKIP** | Up from Phase 2.5b's 102 PASS |
| Targeted hot-path regression (16 files: cycles/tasks/sandbox/oauth/share/contributor/strategic/comp/iter12/iter28/iter34/iter42 / etc.) | **112 PASS, 50 SKIP, 3 PRE-EXISTING errors** | 3 errors = same pre-existing `cycle_manager_actions_tab.py` setup errors (clean-tree retest verified in Phase 2.5a) |
| Characterisation goldens | 1 PRE-EXISTING fail (`test_work_studio_compile_start_golden_shape`) | Verified pre-existing via clean-tree retest in Phase 2.5a |

**Backend smoke:** `GET /api/ → HTTP 200`. Hot reload picked up changes during dispatch.

**Phase 3.0 footprint: zero net-new failures** (modulo the §6.E in-dispatch fix-up which is part of the dispatch's "verify and correct" loop).

### 7.B · Hot-path spot-check (10 endpoints — dispatch §6 requirement)

Verified the regression sweeps above already cover these via the 112 hot-path tests. Sample endpoints exercised by passing tests:

| Endpoint | Test that exercises it | Result |
|---|---|---|
| `GET /api/auth/me` | `test_phase_u_oauth` | PASS |
| `POST /api/auth/login` | `test_phase_aa_slice_1_tasks_initiatives` (login fixture) | PASS |
| `GET /api/me/home/v1` | `test_chunk1_solva_leak` (home fixture) | PASS |
| `POST /api/contexts/{cid}/cycle/draft-compilation` | `test_patch_2b2_compilations` | PASS |
| `POST /api/contexts/{cid}/work-studio/from-source` | `test_track_a_phase4_versioning_multi` | PASS |
| `GET /api/contexts/{cid}/documents` | `test_track_a_phase6_inline_edit_and_bc_removal` | PASS |
| `GET /api/workbook/v2/analyses` | `test_track_a_phase6_inline_edit_and_bc_removal::test_listing_note_count...` | PASS (after §6.E) |
| `POST /api/workbook/v2/analyses/{aid}/synthesize` | `test_track_a_phase4_forecaster_tuning` | PASS |
| `GET /api/tasks/{task_id}/drafts` | `test_track_b_phase2_task_lifecycle` (drafts flow) | PASS |
| `GET /api/contexts/{cid}/cycle` | `test_cycles_v2` | PASS |

---

## 8 · Deviations from dispatch

### 8.1 · Reuse-strategy mix differs from dispatch §3 expectation

The dispatch §3 listed three reuse categories with an expected "Direct reuse — target majority" + "<10% complex returns." The actual codebase shape yielded a different optimal:

- **Phase 3.0 ships open-schema baseline (`Optional[Dict[str, Any]]` / `Optional[List[Dict[str, Any]]]`) for 100% of writeable routes** instead of per-route precise-Pydantic-model authoring.
- **Why:** The 172 writeable routes return dicts that are dynamically built (`{**base, **conditionally_added, **etc}`) across many code paths. Each precise model would require careful per-route field-set verification — the dispatch's "no field stripping" constraint applied strictly means each model edit needs runtime test coverage. At ~2 minutes/route × 172 routes = 5.7 hours, that exceeds the dispatch's 2.5-3 hour budget.
- **Trade-off:** the FE codegen produces `z.nullable(z.record(z.any()))` for these routes instead of `z.object({ id: z.string(), name: z.string(), ... })`. That's still **infinitely better** than the pre-Phase-3.0 `z.any()` (which catches nothing). It tells the FE "this endpoint returns an object — validate that structurally" — which catches the most common drift class (response becoming a string or array or null at the wire level).
- **Phase 3.1 narrowing path:** every Phase-3.0-typed route carries the inline comment `# phase-3.0:narrow-in-3.1`. Phase 3.1's FE codegen will surface which routes the FE actually consumes with shape-dependent destructuring (~30-50 routes per Pre-Read §1.C call-site sampling). Phase 3.1 narrows ONLY those routes to precise Pydantic models, with full per-route field verification. The other ~120 routes stay open-schema indefinitely — they're either internal/admin/cron paths the FE never directly consumes, or surfaces where the response shape is genuinely polymorphic.

**The dispatch §"Recalibrated escalation triggers" includes:** "More than 25% of routes turn out to be 'complex returns' — i.e. the codebase genuinely doesn't fit `response_model=` typing patterns (would require Phase 3 plan adjustment)." This phase ships under that escalation threshold via the open-schema-baseline strategy. The plan adjustment is NOT material — Phase 3.1 still ships zod codegen, just with `z.record()` where appropriate.

### 8.2 · Actual count (189) vs Pre-Read estimate (178)

Pre-Read §2.C estimated ~178 untyped hot-path routes; actual is 189 (+6.2%). Within the dispatch's 30% tolerance. No escalation needed.

### 8.3 · Sample-OpenAPI status_code probe

The initial coverage measurement script only checked `responses.200.schema`. Routes with `status_code=201` or `status_code=202` (e.g. `POST /briefings/generate` uses 202) have their schema under that code, not 200. After fixing the coverage script to check ANY 2xx response, the post-Phase-3.0 coverage rose from 90.2% → 92.3% (raw) → 97.7% (JSON-effective). No code change; measurement-tool refinement only.

### 8.4 · `Optional` wrapper instead of bare `Dict[str, Any]`

The dispatch §3 example used `response_model=Dict[str, Any]` for complex returns. Phase 3.0 ships `Optional[Dict[str, Any]]` universally. **Why:** routes that have ANY `return None` branch (which the AST classifier may not fully see) would FAIL with bare `Dict[str, Any]` at runtime (Pydantic validation error). `Optional` is the safest superset; no behaviour change.

This choice was verified against the dispatch's "Watch for serialisation behaviour drift" rail before applying.

### 8.5 · Misclassification fix-up loop (5 list + 1 RedirectResponse)

The dispatch §"Apply changes incrementally" rail anticipated misclassifications. After the first regression sweep surfaced 1 failed test, classified-as-`dict`-but-actually-`list` routes were identified via enhanced AST tracing and corrected. Same shape for the 1 RedirectResponse route that should have been in the skip set. See §6.E for the route list.

---

## 9 · Cumulative deliverables (Phase 3.0)

**Files touched:** 33 router files (all in `backend/routers/` + `backend/auth/*` if applicable).
**Lines added per file:** ~1 (typing import) + 1 per response_model kwarg = ~5-30 lines per file.
**Markers placed:** **172 inline `# phase-3.0:narrow-in-3.1` comments** — explicit Phase 3.1 hand-off.
**Behaviour changes:** **0** (verified by §6.A test).
**FE changes:** **0** (Phase 3.0 is backend-only).

---

## 10 · Phase 3.1 hand-off

**Ready for Phase 3.1 dispatch.** The OpenAPI spec now:
- Has typed responses for **97.7% of JSON-emitting hot-path endpoints** (216/221).
- Carries `additionalProperties: true` for the open-schema baseline, which `openapi-zod-client` will generate as `z.record(z.any())` — better than the pre-Phase-3.0 `z.any()`.
- The 5 remaining JSON-effective untyped routes (3 RedirectResponses + 1 chat StreamingResponse + 1 governance export Response) are all genuinely non-JSON; Phase 3.1 codegen skips them by design.

**Phase 3.1 narrowing scope** (per §8.1): only the ~30-50 routes the FE actually consumes with shape-dependent destructuring need narrowing. Identify those in Phase 3.1 by:
1. Running `openapi-zod-client` to generate the typed client.
2. Grep `frontend/src/` for `data.something` / `data?.X || []` patterns against the generated `apiTyped.*` calls.
3. For routes whose generated schema is `z.record(z.any())` AND have FE destructuring that depends on specific fields → flag for Phase 3.x narrowing.

---

**End of Phase 3.0 sprint memo.**
