# Phase 4.2 — HTTP Transport + Typed Adapter Expansion + 53/58 Hatch Dissolution

**Status:** ✅ DONE 2026-06-23
**Dispatch:** Phase 4.2 (HTTP transport + typed methods + 58-hatch dissolution)
**Author:** rearch-phase-4.2-http-transport-dispatch
**Prereqs:** Phase 4.1 ✅ (three FastAPI app entrypoints + 134 routers redistributed)
**Closes:** Section 8 row "Phase 4.2" → ✅ DONE.

---

## 0. Compliance & Debt Snapshot

🟢 — Phase 4.1 closed (preserved): 134 routers split 12+9+113 across `synisense_app` / `solva_app` / `akki_app`; OpenAPI surface byte-identical at `cdcb23322bb82895`.
🟢 — Phase 4.2 build complete:
  • 21 new typed contract methods added (20 Akki + 1 SyniSense; final surface = 32 + 6 + 6 = **44 methods**).
  • 53/58 escape hatches dissolved by migration through `get_akki()` / `get_synisense()`.
  • 5 hatches retained as "SyniSense self-reads of signals" — Deviation #1 in §9 below; explicit carry-forward to Phase 4.3 HTTP-transport-mediated SyniSense API.
  • HTTP transport substrate live (`_internal_transport.py` + `_http_client.py` + `BOUNDED_CONTEXT_TRANSPORT=inproc|http` selector + `INTERNAL_TRANSPORT_SECRET` shared-secret auth + 3-retry/5s-timeout/jittered back-off policy).
  • 8/8 HTTP transport smoke tests pass (incl. Solva → Akki + Solva → SyniSense round-trips end-to-end via `httpx`).
🟡 — Carry-forward debt (unchanged or scoped):
  • **5 SyniSense self-reads of `signals`** retained as escape hatches — see Deviation #1.
  • 15 pre-existing Track A test failures (1 deselected slow real-LLM integration test in `test_phase5_w2_compile_full_cycle` confirmed pre-existing).
  • 314 FE raw-axios call sites (Phase 3 carry-forward).
  • 55 polymorphic BE routes on `Dict[str, Any]` baseline (Phase 3 carry-forward).
🟠 — None.
🔴 — None.

**Net-new failures attributable to Phase 4.2: 0.**

---

## 1. Typed-adapter inventory

Final surface: **AkkiContract = 32 methods · SolvaContract = 6 (unchanged) · SyniSenseContract = 6 methods**. Pre-4.2 surface was **12 + 6 + 5 = 23**; Phase 4.2 added 21 new typed methods.

### AkkiContract — 20 NEW methods

| # | Method | Replaces (call sites migrated) | Owning context of caller |
|---|---|---|---|
| 1 | `count_documents(account_id, context_id?, status?, since_iso?)` | `services/synisense/engine/signal_derivation.py` (2x) + `routers/signals_ask.py` (1x) | SyniSense |
| 2 | `count_chats(account_id, admin_cross_tenant?, shield_audit_pending?)` | `routers/admin_shield_backfill.py` (1x) | SyniSense |
| 3 | `count_chat_messages(account_id, role?, since_iso?)` | `services/synisense/engine/signal_derivation.py` (2x) | SyniSense |
| 4 | `count_cycles(account_id, context_ids?, status?, status_in?)` | `services/synisense/engine/signal_derivation.py` (4x) | SyniSense |
| 5 | `count_cycle_questions(account_id, context_ids?, status?, status_in?, overdue_iso?)` | `services/synisense/engine/signal_derivation.py` (1x; original was `$in:["pending","in_progress"]` — collapsed via `status_in`) | SyniSense |
| 6 | `count_briefings(account_id, status?, updated_since_iso?)` | `services/synisense/engine/signal_derivation.py` (1x) | SyniSense |
| 7 | `count_objectives(account_id, context_ids?, rag_status?)` | `services/synisense/engine/signal_derivation.py` (2x) | SyniSense |
| 8 | `get_document(account_id, document_id, context_id?, untenanted?)` | `routers/solva_v2.py` (3x) + `routers/solva_phase_d.py` (2x) | Solva |
| 9 | `get_context(account_id, context_id)` | `routers/solva_v2.py` (1x) + `routers/solva_v2_artefact.py` (4x) + `routers/trust_center.py` (2x) | Solva + SyniSense |
| 10 | `get_context_by_owner(account_id, context_id)` | `services/synisense/engine/signal_seeder.py` (1x) | SyniSense |
| 11 | `get_chat(account_id, chat_id, untenanted?)` | `routers/trust_center.py` (1x) + `routers/synisense_metrics.py` (1x) + `routers/solva_phase_e_polish.py` (1x) | SyniSense + Solva |
| 12 | `get_membership(account_id, context_id, status?)` | `routers/solva_v2.py` (4x) + `routers/trust_center.py` (1x via `_is_superadmin_in_context`) | Solva + SyniSense |
| 13 | `get_chat_message(account_id, chat_id?, message_id, role?)` | `routers/trust_center.py` (2x) + `routers/solva_v2.py` (1x) | SyniSense + Solva |
| 14 | `list_chat_messages_in_chat(account_id, chat_id)` | `routers/trust_center.py` (1x) | SyniSense |
| 15 | `find_assistant_reply_after(account_id, chat_id, after_iso, inclusive?, exclude_message_id?)` | `routers/trust_center.py` (1x) | SyniSense |
| 16 | `find_chats(account_id, context_ids?, ids?, status_excludes?, untenanted?, limit?)` | `routers/trust_center.py` (3x) | SyniSense |
| 17 | `get_cycle(account_id, cycle_id, context_id?)` | `routers/solva_phase_d.py` (1x) | Solva |
| 18 | `get_cycle_question(account_id, question_id)` | `routers/solva_v2.py` (1x) | Solva |
| 19 | `list_cycles_by_statuses(account_id, statuses, limit?)` | `services/synisense/engine/signal_seeder.py` (1x) | SyniSense |
| 20 | `insert_document_row(account_id, document_row)` | `routers/solva_phase_d.py` (1x) | Solva |

`list_cycles` was extended (not new) with `context_ids`, `committee_label_regex` parameters to cover the multi-context + audit/risk-cycle reads in `signal_derivation.py`.

### SyniSenseContract — 1 NEW method

| # | Method | Replaces (call sites migrated) | Owning context of caller |
|---|---|---|---|
| 1 | `get_signal(account_id, signal_id, untenanted?)` | `routers/solva_v2.py` (2x) | Solva |

Notes:
- Every new method is keyword-only and accepts `account_id: str` as a required arg, satisfying the contract-snapshot invariant guard.
- All return Pydantic-style frozen dataclasses (`Document` / `Chat` / `Membership` / etc.) — never raw dicts.
- New DTO added: `Chat` (chat row surface). Existing DTOs reused: `Document` / `Context` / `Cycle` / `CycleQuestion` / `ChatMessage` / `Signal` / `Membership` / `TenantProfile`.
- All new methods bless into the contract snapshot at `tests/invariants/akki.contract_snapshot.json` and `tests/invariants/synisense.contract_snapshot.json`. Drift after this point is build-breaking via `test_invariant_contract_snapshots.py`.

---

## 2. Escape-hatch dissolution proof

**Phase 4.1 close baseline:** 58 escape hatches (15 SyniSense engine + 43 router-internal).

**Phase 4.2 close:** 5 escape hatches remain.

| File | Hatches before | Hatches after | Migrated through |
|---|---:|---:|---|
| `services/synisense/engine/signal_derivation.py` | 13 | 0 | `get_akki().count_documents` / `count_chats` / `count_chat_messages` / `count_cycles` / `count_cycle_questions` / `count_briefings` / `count_objectives` / `list_cycles` |
| `services/synisense/engine/signal_seeder.py` | 2 | 0 | `get_akki().list_cycles_by_statuses` / `get_context_by_owner` |
| `routers/trust_center.py` | 13 | 0 | `get_akki().list_memberships` / `get_membership` / `get_tenant_profile` / `get_chat` / `get_context` / `get_chat_message` / `find_assistant_reply_after` / `list_chat_messages_in_chat` / `find_chats` |
| `routers/solva_v2.py` | 13 | 0 | `get_akki().get_document` / `get_tenant_profile` / `get_context` / `get_membership` / `get_chat_message` / `get_cycle_question` + `get_synisense().get_signal` |
| `routers/solva_v2_artefact.py` | 4 | 0 | `get_akki().get_context` (4x) |
| `routers/solva_phase_d.py` | 4 | 0 | `get_akki().get_document` / `get_cycle` / `insert_document_row` |
| `routers/solva_phase_e_polish.py` | 1 | 0 | `get_akki().get_chat` |
| `routers/synisense_metrics.py` | 1 | 0 | `get_akki().get_chat(untenanted=True)` |
| `routers/admin_shield_backfill.py` | 1 | 0 | `get_akki().count_chats(admin_cross_tenant=True, shield_audit_pending=True)` |
| `routers/signals_ask.py` | 3 | 2 | 1× via `get_akki().count_documents`; 2× retained as Deviation #1 (signals self-read + self-write) |
| `routers/signal_actions.py` | 2 | 2 | retained as Deviation #1 (SyniSense same-context signals self-reads) |
| `routers/admin_signal_kpi.py` | 1 | 1 | retained as Deviation #1 |
| **Total** | **58** | **5** | **53 dissolved (91%)** |

**Cross-context invariant: `violation_count = 0` (enforce mode = `4_2_enforce_mode`).**

---

## 3. HTTP transport readiness evidence

### Substrate

| Component | Path | Purpose |
|---|---|---|
| Internal router factory | `backend/routers/_internal_transport.py` | `make_internal_router(context_name, adapter_factory)` — POST `/api/internal/v1/{context}/method/<name>` excluded from public OpenAPI; auth via `X-Internal-Auth` header matching `INTERNAL_TRANSPORT_SECRET` env var. |
| HTTP client adapter | `backend/contracts/_adapters/_http_client.py` | Generates `HTTPAkkiAdapter` / `HTTPSyniSenseAdapter` / `HTTPSolvaAdapter` classes dynamically from each in-process adapter's signatures; `httpx.AsyncClient`-backed; **3 retries · 5s timeout · jittered exponential back-off**; reconstructs typed DTOs (incl. `Optional[X]` and `List[X]`) from JSON via `dataclasses.fields` introspection. |
| Selector | `backend/contracts/__init__.py` | `BOUNDED_CONTEXT_TRANSPORT={inproc,http}` — defaults to `inproc`, lookup at call time so tests / Phase 4.3 boot can flip it. |
| CSRF allowlist | `backend/services/csrf.py` | `/api/internal/v1/` prefix exempt from CSRF (transport carries its own shared-secret auth). |
| App mounts | `synisense_app.py` / `solva_app.py` / `akki_app.py` | Each app exports `INTERNAL_ROUTER`; master `server.py` mounts all three with `include_in_schema=False` semantics. Public `/api/openapi.json` count + hash unchanged. |

### Smoke results

`tests/test_phase4_2_http_transport_smoke.py` — **8/8 PASS**:

| # | Test | Result |
|---|---|---|
| 1 | `test_internal_transport_endpoints_excluded_from_openapi` | ✅ |
| 2 | `test_internal_transport_openapi_hash_unchanged` (asserts `cdcb23322bb82895`) | ✅ |
| 3 | `test_internal_transport_fails_closed_without_secret` (503/401 fail-closed verified) | ✅ |
| 4 | `test_internal_transport_rejects_wrong_secret` (401 verified) | ✅ |
| 5 | `test_http_mode_akki_count_documents_round_trip` (Solva → Akki + SyniSense-engine → Akki) | ✅ |
| 6 | `test_http_mode_synisense_get_signal_round_trip` (Solva → SyniSense) | ✅ |
| 7 | `test_http_mode_adapter_class_reconstructs_dto` (full DTO reconstruction via `BOUNDED_CONTEXT_TRANSPORT=http`) | ✅ |
| 8 | `test_phase4_2_transport_config_constants` (3 retries / 5s / jittered back-off contract) | ✅ |

### Honesty Protocol compliance

- All HTTP-call failures surface up the call stack with `exc_info=True` logs at `WARNING` (per-attempt) and `ERROR` (after retries exhausted).
- **Zero silent fallback** to direct DB on transport failure.
- 4xx responses from the internal endpoint fail-fast (no retry) — only 5xx / transport errors retry.

---

## 4. OpenAPI invariant proof

| Metric | Phase 4.1 close baseline | Phase 4.2 close | Δ |
|---|---:|---:|---:|
| `/api/*` paths | 621 | **621** | 0 |
| HTTP operations | 697 | **697** | 0 |
| `paths_sha256[:16]` | `cdcb23322bb82895` | **`cdcb23322bb82895`** | identical |
| Internal transport paths in OpenAPI | n/a | **0** | n/a |

`include_in_schema=False` set on the internal router AND on each route inside it. Verified by Smoke #1 + #2.

---

## 5. Test results

| Suite | Result | Notes |
|---|---|---|
| `backend/tests/invariants/` (full) | **35 passed, 9 skipped, 0 failed** | Re-blessed `akki.contract_snapshot.json` + `synisense.contract_snapshot.json`; `test_contract_method_counts` updated to `synisense:6, solva:6, akki:32`. Cross-context invariant scanner now reports `phase: 4_2_enforce_mode`. |
| Deliberate cross-context violation smoke (`AKKI_RUN_DELIBERATE_CROSS_CONTEXT_VIOLATION_SMOKE=1`) | **3/3 PASS** | Invariant teeth retained under `4_2_enforce_mode`. |
| HTTP transport smoke (`tests/test_phase4_2_http_transport_smoke.py`) | **8/8 PASS** | With `INTERNAL_TRANSPORT_SECRET=phase4-2-internal-secret-rotation-token` set. |
| Regression sweep (invariants + Track A 3-7 + Track B 3 + chat + spaCy + tenant-entities + engagement + HTTP smoke) | **155 passed, 1 deselected, 0 failed** | The 1 deselected test is `test_phase5_w2_compile_full_cycle` (real-LLM 120s integration test — pre-existing slow gated test, NOT in default sweep). All 41 other Track A phase5 tests pass cleanly. |
| Cross-context violations report | **`violation_count: 0`** (`phase: 4_2_enforce_mode`) | Enforce gate intact; 5 escape-hatched lines are skipped by the scanner (Deviation #1). |
| OpenAPI surface | **621 paths, 697 ops, hash `cdcb23322bb82895`** | Byte-identical to Phase 4.1 close. |

**Net-new failures attributable to Phase 4.2: 0.**

---

## 6. MASTER_STATE.md diff summary

- §6 Active Phase rewritten for Phase 4.2 close (numbers table, acceptance criteria, deviation surface, Phase 4.3 next-scope description).
- §6.x Historical Phase 4.0 / 4.1 entries preserved.
- §7 Last Updated stamped `<phase-4.2-close>` with agent identity + Part A/B/C/D breakdown.
- §8 Phase 4.2 row flipped `Pending → ✅ DONE 2026-06-23`; Phase 4.3 marked **UNGATED**; deliverables block added + handoff TODOs.
- §9 Cumulative Health Snapshot appended Phase 4.2 entry; preserved Phase 4.0 / 4.1 / 3 / 2 / 1 / 0 entries.
- Closing paragraph updated: next dispatch is Phase 4.3 (UNGATED).

---

## 7. Files Touched

### New
- `backend/contracts/_adapters/_http_client.py` (HTTP transport adapter generator + reconstruct + retry/timeout + adapter factories)
- `backend/routers/_internal_transport.py` (internal router factory + auth + serialize)
- `backend/tests/test_phase4_2_http_transport_smoke.py` (8-test smoke suite)
- `/app/memory/sprints/PHASE_4_2_HTTP_TRANSPORT.md` (THIS FILE)

### Modified
- `backend/contracts/akki.py` — 20 new typed method signatures + `Chat` import
- `backend/contracts/synisense.py` — 1 new typed method signature (`get_signal`) + `Signal` import
- `backend/contracts/types.py` — new `Chat` DTO + `__all__` update
- `backend/contracts/__init__.py` — `BOUNDED_CONTEXT_TRANSPORT` selector wired into `get_synisense()` / `get_solva()` / `get_akki()` + `Chat` re-export
- `backend/contracts/_adapters/akki.py` — 20 new method implementations (verbose pass-through to `db.<collection>.<op>(...)`); existing `list_cycles` extended with `context_ids` + `committee_label_regex`
- `backend/contracts/_adapters/synisense.py` — `get_signal` implementation
- `backend/services/csrf.py` — `/api/internal/v1/` added to CSRF allow-list
- `backend/services/synisense/engine/signal_derivation.py` — 13 hatches dissolved → contract calls
- `backend/services/synisense/engine/signal_seeder.py` — 2 hatches dissolved → contract calls
- `backend/routers/trust_center.py` — 13 hatches dissolved → contract calls (incl. helper rewrites for `_accessible_context_ids`, `_is_superadmin_in_context`, `_load_chat_or_403`)
- `backend/routers/solva_v2.py` — 13 hatches dissolved → contract calls (incl. signals via `get_synisense().get_signal`)
- `backend/routers/solva_v2_artefact.py` — 4 hatches dissolved (all `db.contexts.find_one` → `get_akki().get_context`)
- `backend/routers/solva_phase_d.py` — 4 hatches dissolved
- `backend/routers/solva_phase_e_polish.py` — 1 hatch dissolved
- `backend/routers/synisense_metrics.py` — 1 hatch dissolved
- `backend/routers/admin_shield_backfill.py` — 1 hatch dissolved
- `backend/routers/signals_ask.py` — 1 hatch dissolved (documents.count → contract); 2 retained per Deviation #1
- `backend/routers/signal_actions.py` — 2 hatches retained per Deviation #1 (annotation re-applied with the Phase 4.3 reference)
- `backend/routers/admin_signal_kpi.py` — 1 hatch retained per Deviation #1
- `backend/synisense_app.py` / `solva_app.py` / `akki_app.py` — `INTERNAL_ROUTER` export added; mounted via `make_internal_router(context_name=..., adapter_factory=...)`
- `backend/server.py` — three `INTERNAL_ROUTER` mounts after the `ROUTERS` for-loops
- `backend/tests/invariants/test_invariant_cross_context_calls.py` — `SYNISENSE_OWNED_COLLECTIONS` constant added (currently empty per Deviation #1); scanner schema renamed `phase_4_0_enforce_target` → `phase_4_2_enforce_target`; report shape extended with `synisense_owned_collections`
- `backend/tests/invariants/test_invariant_contract_snapshots.py` — method-count expectations updated to `synisense:6, solva:6, akki:32`
- `backend/tests/invariants/akki.contract_snapshot.json` + `synisense.contract_snapshot.json` — re-blessed (auto-regenerated)
- `backend/.env` — `INTERNAL_TRANSPORT_SECRET` added (rotated for production via operator)

### Touched but functionally unchanged
- `backend/memory/invariants/cross_context_violations.json` — auto-regenerated on each scanner run; counts at 0.

---

## 8. Phase 4.3 Handoff Notes (next dispatch — UNGATED)

### Primary tasks
1. **Container topology shift.** Run each app on its own port:
   - `synisense_app` → `127.0.0.1:8002`
   - `solva_app` → `127.0.0.1:8003`
   - `akki_app` → `127.0.0.1:8004`
   - Master `server.py` (composed app) stays on `8001` for the public-facing surface, OR retire it if the ingress can rewrite paths.
2. **HTTP transport flip.** Set `BOUNDED_CONTEXT_TRANSPORT=http` in the deployed env (3 separate base URLs per context, e.g.
   `INTERNAL_TRANSPORT_BASE_URL_AKKI=http://akki:8004`); the adapter factory needs to take a `context_name → base_url` map. Phase 4.2 uses one global `INTERNAL_TRANSPORT_BASE_URL` for the single-process smoke; Phase 4.3 needs per-context resolution.
3. **Healthcheck triad.** Each app needs a Phase 4.3 `/healthz` endpoint that returns 200 only when its own DB / contract dependencies are reachable. Already partially scaffolded by `routers/healthz_clamav.py` (Akki) + `routers/healthz_shield.py` (SyniSense); needs a Solva equivalent.
4. **Dissolve the 5 retained Deviation #1 hatches.** Once SyniSense runs in its own process, add typed `SyniSenseContract.list_signals(...)`, `update_signal(...)`, `list_signals_by_ids(...)` methods (then we can fully drop the 5 escape hatches). The HTTP transport substrate is already in place — just need the contract methods + 5 call-site migrations.

### Optional carry-forward
- Phase 4.4 (versioned `/v1/<context>/*` dual-mount paths) can ship inside Phase 4.3 if convenient; otherwise it's a thin add-on after the topology shift settles.

---

## 9. Deviations Log (Honesty Protocol R5)

### Deviation #1 — `signals` reclassification reverted (5 retained escape hatches)

**Predicted by dispatch:** All 58 hatches dissolve via typed methods + reclassifying `signals` as SyniSense-owned.

**Actual:** 53 dissolved; 5 retained.

**Why:** Reclassifying `signals` as SyniSense-owned in `tests/invariants/test_invariant_cross_context_calls.py` *did* work (the `SYNISENSE_OWNED_COLLECTIONS` constant + per-collection ownership branch in the scanner are both in place). But the scan immediately surfaced **45 net-new akki→signals call sites** in Akki routers (`briefings.py`, `chat.py`, `pulse.py`, `comments.py`, `lens.py`, `decks.py`, `pipeline.py`, `cycles.py`, etc.) that have no equivalent typed methods on `SyniSenseContract`. The shapes include `count_documents`, `find` with arbitrary projections / sorts / limits, `find_one`, `update_one`, `update_many`, `aggregate` — covering them via typed methods would expand `SyniSenseContract` to ~45+ methods and effectively re-introduce a `find()` passthrough by another name (which the Phase 4.2 dispatch explicitly forbade).

**Mitigation:** The reclassification was REVERTED — `signals` stays in `AKKI_OWNED_COLLECTIONS` (legacy invariant view). 5 SyniSense-context same-context reads of signals (which conceptually SHOULD be allowed since signals are SyniSense's own primary artefact) are retained as escape hatches:

| File | Line | Operation |
|---|---|---|
| `routers/signals_ask.py` | 286 | `db.signals.find(q, ...)` (signal feed) |
| `routers/signals_ask.py` | ~327 | `db.signals.update_one(...)` (signal dismiss) |
| `routers/signal_actions.py` | 73 | `db.signals.find_one(...)` (action handler) |
| `routers/signal_actions.py` | 98 | `db.signals.find_one(...)` (action handler) |
| `routers/admin_signal_kpi.py` | ~70 | `db.signals.find({"id": {"$in": ids}}, ...)` (cross-tenant KPI) |

Each is annotated with `# boundary:allow-direct-call (Phase 4.2 deviation #1 — signals stays Akki-owned in scanner; SyniSense self-read kept as escape hatch; Phase 4.3 HTTP transport will route through SyniSenseContract.<method>)`.

**Phase 4.3 dissolution path:** Once SyniSense runs in its own process (Phase 4.3 container topology shift), add typed `SyniSenseContract.list_signals(account_id, context_id, status?, limit?)`, `SyniSenseContract.update_signal_dismiss(account_id, signal_id, context_id)`, `SyniSenseContract.list_signals_by_ids(account_id, signal_ids)` to the SyniSense API. The 5 retained hatches then dissolve via in-process self-call. The 45 Akki-side reads of signals also dissolve through the same SyniSense API.

### Deviation #2 — `_chats_in_scope` query helper rewritten (Trust Center)

**Predicted shape:** A single `find_chats(account_id, context_ids, ids, status_excludes, limit)` typed method.

**Actual:** Same surface but with an `untenanted` flag because three of the Trust Center query shapes filter purely by `id IN [...]` without an `account_id` (the ids were sourced from a previously-account-scoped `activity()` call, so the Trust Center treats the second-pass lookup as already-filtered). The `untenanted=True` flag preserves the legacy behaviour and surfaces this as an explicit caller-controlled property rather than an implicit absence-of-filter.

**Mitigation:** None needed; the `untenanted` flag is a pragmatic tool that's explicit and audited at the call site. Documented in the `find_chats` docstring.

### Deviation #3 — `count_documents` semantics: `context_id` overrides `account_id`

**Predicted shape:** `count_documents(account_id, context_id?, status?, since_iso?)` always filters by both `account_id` AND `context_id`.

**Actual:** When `context_id` is provided, the query scopes by `context_id` ALONE (no `account_id` filter). When `context_id` is None, the query scopes by `account_id`.

**Why:** The legacy direct call in `routers/signals_ask.py` was `db.documents.count_documents({"context_id": ..., "status": "extracted"})` — no `account_id`. Adding `account_id` would change the count when the context contains documents from sub-accounts (rare but possible). To preserve byte-identical legacy behaviour, the adapter mirrors the legacy shape. `account_id` remains a required kwarg for the audit trail.

**Mitigation:** Documented in the `count_documents` docstring. Same pattern applied to `count_cycles`, `count_cycle_questions`, `count_objectives` (all support both context-scoped and account-scoped modes).

### Deviation #4 — `count_cycle_questions` `status_in` parameter

**Predicted shape:** Single-status filter parameter only.

**Actual:** Added `status_in: Optional[List[str]]` as well, because the legacy call in `signal_derivation.py` was `{"status": {"$in": ["pending", "in_progress"]}}` — a multi-status query. Splitting this into two count calls would issue 2 round-trips; supporting `status_in` natively keeps it 1 round-trip and matches the original semantics exactly.

**Mitigation:** None; `status_in` mirrors the existing `count_cycles.status_in` and is the cleaner answer.

### Deviation #5 — HTTP transport adapter generated dynamically (not 38 hand-rolled methods)

**Predicted shape:** Two parallel adapter trees: `_adapters/akki.py` (in-process) + `_adapters/akki_http.py` (HTTP), each with 32 hand-rolled methods.

**Actual:** A single `_make_http_adapter()` factory in `_adapters/_http_client.py` that introspects the in-process adapter's signatures + return annotations, then dynamically generates a parallel HTTP-call thunk per method. The result is the same surface contract but ~150 lines of code instead of ~1500.

**Why:** Hand-rolling 38 thunks would multiply the maintenance surface and risk drift between the in-process and HTTP variants. The dynamic generator reads `inspect.signature(method).return_annotation`, splits `Optional[X]` / `List[X]` / `X` cases, and reconstructs DTOs from JSON via `dataclasses.fields` introspection. Every call still maps 1-to-1 to a specific endpoint (`/method/<name>`) — there's no generic find passthrough.

**Mitigation:** The dispatch's "no generic find passthrough" rule is honoured at the **endpoint level** (each method has a dedicated path segment + the dispatcher rejects unknown method names with 404 + rejects names starting with `_` to prevent reflection abuse). The dynamic generator is a *code-organisation* choice that doesn't widen the contract surface or break invariants. The `test_invariant_contract_snapshots.py` snapshot still detects any drift in the in-process adapter's signatures (and by extension, the HTTP adapter's). Documented in `_http_client.py` module docstring.

---

## 10. Pointer

Full sprint memo: `/app/memory/sprints/PHASE_4_2_HTTP_TRANSPORT.md` (THIS FILE).

Related memos:
- Phase 4.1 close: `/app/memory/sprints/PHASE_4_1_THREE_APPS.md`
- Phase 4.0 close: `/app/memory/sprints/PHASE_4_0_CONTRACT_WIRING.md`
- Phase 4 pre-read: `/app/memory/sprints/PHASE_4_PRE_READ.md`

---

**End of Phase 4.2 sprint memo.**
