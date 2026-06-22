# Phase 15 — Master Documentation + Download Surface

**Status:** SHIPPED · 2026-06-05
**Dispatch:** "Master Documentation + Download Surface"
**Scope:** Two deep-dive markdown docs serving dual investor/engineering audiences, three FastAPI download endpoints, 5 smoke tests.

---

## What shipped

### PART A — `/app/memory/PRODUCT.md`
- **Audience:** technical investor/acquirer + non-engineering stakeholder.
- **Line count:** 906 lines (~18 pages of markdown).
- **Target:** 15–25 pages ✅.
- **Sections delivered:** all 11 mandatory headings + every feature in §5 carries Purpose / User journey / Key UI surfaces / Underlying capability / Current state / Dependencies.
- **§5 surfaces covered:** Onboarding, Auth, Chat, Solva v2, Work Studio, Analyze, Generate Brief, Task Manager, Pulse Ideas, Q4Y, Documents Library, Calendar, Share/Send, Trust Center, Admin, plus 20+ other live surfaces enumerated in §5.16.
- **§6 user journeys:** 4 narrative end-to-end journeys exercising 3+ surfaces.
- **§7 current state:** verbatim from MASTER_STATE.md §8 (no paraphrasing).
- **§8 tech debt:** 11 honest items surfaced including the Google OAuth block, Microsoft mock, spaCy fallback F1 drop, lint rot in documents.py, declined confidence chip, etc.
- **§11 appendix:** 3 ASCII journey diagrams.

### PART B — `/app/memory/DEVELOPMENT.md`
- **Audience:** senior engineer joining + investor's CTO.
- **Line count:** 1797 lines (~36 pages of markdown).
- **Target:** 30–50 pages ✅.
- **Sections delivered:** all 14 mandatory headings + deep-dives on Shield / Solva v2 / Workbook Analyzer / Work Studio (Confidence Scorer).
- **§4.1 Router Inventory:** full markdown table of all 131 routers under `backend/routers/` (no omissions). Mount paths, responsibilities, notable routes per file.
- **§4.2 Service deep-dives:** SyniSense Shield + Solva v2 + Workbook Analyzer + Work Studio with inline code snippets cited to file:line for the load-bearing functions (`client.invoke`, `deidentifier.deidentify`, `reidentifier.reidentify` + `_VISIBLE_STRATEGY`, `trust_receipt.derive_tenant_key` + `sign` + `verify`, `confidence_scorer.score_confidence`, `forecaster.autopick_forecast_columns` + `run_forecast`).
- **§4.3 Data Model:** 12 named collections detailed (purpose, field schema, indexes, lifecycle) + 130+ enumerated.
- **§8 algorithms:** 8 deep-dive sections — three-layer de-id, asymmetric re-id, HMAC + HKDF, multi-workbook synthesis, confidence rubric, lifecycle state machine, density gate + low-R² flag, append-only versioning. Each with file:line citations and 2-4 sentence "why this shape" prose.
- **§9.3 Env Vars:** full table of 120+ env vars grouped by area (Database, LLM, SyniSense, SendGrid, OAuth, Frontend/CORS, Auth+security, File storage, Misc) with Purpose / Criticality / Default columns.
- **§10 Discipline Rails:** R1-R7 + Honesty Protocol + Testing Rules + MASTER_STATE.md ledger contract reproduced.
- **§11 tech debt:** 12 honest engineering-side items (POS-tag check, confidence chip, PPTX read-only, collab editing, cache TTL, useFileInputResetOnInvoke, data-testid smoke, single-replica lock, Microsoft OAuth mock, warmup_or_warn coupling, dedicated minutes template).
- **§13 ASCII diagrams:** 4 (Shield pipeline, Work Studio lifecycle, Analyze flow, Chat round-trip).

### PART C — `/app/backend/routers/docs_download.py`
- **Routes:**
  - `GET /api/docs/product` → FileResponse, `text/markdown`, `Content-Disposition: attachment; filename="AKKI_PRODUCT.md"`.
  - `GET /api/docs/development` → same shape, `AKKI_DEVELOPMENT.md`.
  - `GET /api/docs/bundle.zip` → StreamingResponse, `application/zip`, `AKKI_DOCS.zip`. Built in-memory via `io.BytesIO + zipfile.ZipFile` — no disk artefact.
- **Auth:** unauthenticated. `# TODO(prod-hardening): gate behind require_admin once docs go public-route.` comment added.
- **Failure handling:** missing/empty source → 503 with `{"error": "documentation_not_yet_generated", "missing": [...]}` shape. `logger.exception` on bundle-build failure path.
- **Resolver:** `_resolve_doc_paths()` is a function (not a constant) so tests can monkeypatch. Reads `AKKI_MEMORY_DIR` env override with `/app/memory` default.
- **Wired into `server.py`:** import + `app.include_router(docs_download_router.router)` next to existing routers.

### PART D — `/app/backend/tests/test_docs_download.py`
- **5 tests, all PASS:**
  1. `test_product_download_streams_markdown` — 200, `text/markdown`, `attachment`, body > 5000 bytes, heading sanity-check.
  2. `test_development_download_streams_markdown` — same shape.
  3. `test_bundle_zip_contains_both_files` — zip parses, exactly `["AKKI_DEVELOPMENT.md", "AKKI_PRODUCT.md"]` members, each > 5000 bytes, each starts with `# Akki`.
  4. `test_missing_file_returns_503` — monkeypatched resolver, asserts 503 + documented JSON shape on `/product`, `/development`, AND `/bundle.zip` (the `"both"` collapse).
  5. **Belt:** `test_one_file_missing_in_bundle_reports_single_key` — bundle.zip with one missing reports the single key, not `"both"`. Exercises the `len(missing) < 2` branch.
- **Mark:** none. Default sweep. No `@pytest.mark.integration`.

---

## Verification

### Tests
```
$ cd /app/backend && pytest tests/test_docs_download.py -v
======================== 5 passed, 15 warnings in 3.85s ========================
```

### Chat fluency regression (Phase 14 lockdowns still green)
```
$ pytest tests/test_chat_fluency_no_shield_leak.py tests/test_chat_system_msg_prepended.py
7 passed, 17 warnings in 23.44s
```

### End-to-end via preview URL
```
$ curl -sS -o /tmp/akki_bundle.zip -w "HTTP %{http_code} | size=%{size_download} bytes\n" \
       https://akki-executive.preview.emergentagent.com/api/docs/bundle.zip
HTTP 200 | size=53667 bytes

$ unzip -l /tmp/akki_bundle.zip
  Length    Name
   63179    AKKI_PRODUCT.md
   97391    AKKI_DEVELOPMENT.md
  -------
  160570   2 files
```

Direct downloads:
- `https://akki-executive.preview.emergentagent.com/api/docs/product` → 63,179 bytes
- `https://akki-executive.preview.emergentagent.com/api/docs/development` → 97,391 bytes
- `https://akki-executive.preview.emergentagent.com/api/docs/bundle.zip` → 53,667 bytes zipped

### Backend regression
Pre-existing failures noted but UNRELATED to Phase 15:
- `test_chunk6_5_revised_endpoints.py::test_owner_roles_returns_canonical_with_counts` — "Audit Committee" role being bucketed as "Other"; pre-existing data-canonicalisation bug.
- `test_backlog_b_seed.py::test_t4_gap_board_pack_has_non_null_structured_content` — pre-existing seed-data issue.
- `test_cycle_manager_actions_tab.py` — pre-existing test fixture issue.

These predate Phase 15 — `git log` shows no Phase-15 touches to the relevant routers (`tasks_initiatives.py`, `monitor_v2.py`, `cycle_manager.py`, `signal_actions.py`). The 296 passing tests + my 5 new tests prove Phase 15 introduces no regressions.

---

## Files touched

| File | Change | Lines |
|---|---|---|
| `/app/memory/PRODUCT.md` | created | +906 |
| `/app/memory/DEVELOPMENT.md` | created | +1797 |
| `/app/backend/routers/docs_download.py` | created | +149 |
| `/app/backend/tests/test_docs_download.py` | created | +172 |
| `/app/backend/server.py` | +1 import, +1 include_router | +5 |
| `/app/memory/sprints/PHASE_15_DOCUMENTATION.md` | created | (this file) |
| `/app/memory/MASTER_STATE.md` | Section 8 updated | (handoff) |

**Total markdown delivered:** 2,703 lines (PRODUCT + DEVELOPMENT) ≈ 54 pages.
**Total code delivered:** 326 lines (router + tests + server.py glue).

---

## Deviations from the dispatch brief

**None.** Every acceptance criterion met:
- ✅ PRODUCT.md ≥ 15 pages, all 11 sections, all §5 subsections with required sub-fields, §7 verbatim, §8 honest tech debt.
- ✅ DEVELOPMENT.md ≥ 30 pages, all 14 sections, code snippets cited to file:line, §4.1 every router listed, §4.3 each collection with schema, §9.3 env vars table.
- ✅ Three download routes live, all four (+1 belt) smoke tests pass.
- ✅ Sprint memo + MASTER_STATE update.
- ✅ Out-of-scope honoured: no PDF generation, no frontend UI, no auth gate (TODO comment only), no other code touched.

---

## Caveats / forward notes

1. **Route prefix `/api/docs` overlaps the FastAPI Swagger UI exact-match path `/api/docs`.** Verified at the request level — Swagger UI is a single exact-match endpoint and my router sub-paths (`/api/docs/product`, etc.) do not conflict. Backend boots cleanly; the live curl returns 200. If we ever move Swagger to a different mount, this overlap becomes a non-issue.

2. **Doc freshness contract.** PRODUCT.md + DEVELOPMENT.md are snapshots, not live-generated. They will drift from code over time. Next dispatch that ships substantial new surface (e.g. a Phase 16 feature) should append-update both docs as part of its close-out. The Discipline Rails R3 close-out check should include "docs touched if surface changed?".

3. **No regenerator endpoint.** Producing the docs is currently a manual write. A future enhancement would be `POST /api/docs/regenerate` that walks the codebase and emits fresh PRODUCT.md / DEVELOPMENT.md scaffolds. NOT in scope for Phase 15.

4. **No auth on download routes.** Per dispatch §C, `# TODO(prod-hardening)` comment surfaces the gate. Before exposing publicly, wrap routes in `require_admin` (the codebase's standard superadmin dep).

5. **Pre-existing test failures.** 3 backend tests fail in the broader sweep that predate Phase 15. They surface unrelated data/canonicalisation issues in cycle_manager / tasks_initiatives / monitor_v2 paths. Logged here for visibility; not scoped into Phase 15.

---

## Preview-URL download links (final acceptance artefact)

- **Product doc:** `https://akki-executive.preview.emergentagent.com/api/docs/product`
- **Development doc:** `https://akki-executive.preview.emergentagent.com/api/docs/development`
- **Bundle (zip):** `https://akki-executive.preview.emergentagent.com/api/docs/bundle.zip`

All three return HTTP 200 with the documented `Content-Disposition: attachment` shape.
