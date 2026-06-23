# Phase 4.4 — Dual-Mount Versioned Surface

**Status:** ✅ DONE 2026-06-23
**Dispatch:** Phase 4.4 Build Dispatch (Dual-mount versioned `/v1/{context}/*` paths + integration smoke + invariant evolution + documentation seed)
**Author:** rearch-phase-4.4-dual-mount-dispatch
**Prereqs:** Phase 4.3 ✅ (Container topology fallback + healthcheck triad + final 5-hatch dissolution + transport flip)
**Closes:** Section 8 row "Phase 4.4" → ✅ DONE.

---

## 0. Compliance & Debt Snapshot

🟢 — Phase 4.3 closed (preserved): healthcheck triad live + `BOUNDED_CONTEXT_TRANSPORT=http` deployed default + signals fully on SyniSense API (32+6+30 = 68 typed methods) + `/api/*` slice hash held at `cdcb23322bb82895`.
🟢 — Phase 4.4 build complete:
  • **Dual-mount mechanism** (`routers/v1_dual_mount.py`) — single helper introspects each owning-context router's routes and clones them onto the master app at the parallel `/v1/<owning_context>/*` path. Same handler, same dependencies, same auth, same response model. Operation IDs are suffixed with the owning context AND a hash of the original path to stay globally unique even when multiple routers expose same-named handlers (e.g. `download_export`, `list_documents`, `record_view`, `consume_magic_link`, `register`).
  • **OpenAPI slice invariants** — three slice hashes now ratchet independently: `/api/*` (pinned `cdcb23322bb82895`), `/v1/*` (new baseline `acc51822aa8818ae`), and combined (`ca9429c64e44570c`).
  • **Integration smoke** — 30 representative routes tested for byte-equivalence between `/api/*` and `/v1/*` surfaces, plus 4 wrong-context 404 negatives plus 2 exclusion-list assertions plus 5 slice/count invariants = **38 tests, all green**.
  • **Documentation seed** — `/app/memory/API_VERSIONING.md` declares `/v1/{context}/*` as the stable versioned SDK surface; `/api/*` legacy-stable; no deprecation window until ≥12 months notice with parallel `Deprecation:` headers (NOT this phase).
🟡 — Carry-forward debt (unchanged):
  • 15 pre-existing Track A test failures (CSRF / E2E flake). User-acknowledged.
  • 314 FE raw-axios call sites (Phase 3 carry-forward).
  • 55 polymorphic BE routes on `Dict[str, Any]` baseline (Phase 3 carry-forward).
🟠 — None.
🔴 — None.

**Net-new failures attributable to Phase 4.4: 0.**

---

## 1. Dual-mount route map (truncated table; full enumeration is the running OpenAPI doc)

| Owning context | `/api/*` example | `/v1/{ctx}/*` parallel |
|---|---|---|
| akki | `/api/health` | `/v1/akki/health` |
| akki | `/api/contexts` | `/v1/akki/contexts` |
| akki | `/api/contexts/{cid}` | `/v1/akki/contexts/{cid}` |
| akki | `/api/chats/{chat_id}` | `/v1/akki/chats/{chat_id}` |
| akki | `/api/documents` | `/v1/akki/documents` |
| akki | `/api/decks` | `/v1/akki/decks` |
| akki | `/api/admin/audit-invariant-violations` | `/v1/akki/admin/audit-invariant-violations` |
| akki | `/api/observability/reasoning_velocity` | `/v1/akki/observability/reasoning_velocity` |
| synisense | `/api/synisense/health` | `/v1/synisense/health` |
| synisense | `/api/synisense/metrics/snapshot` | `/v1/synisense/metrics/snapshot` |
| synisense | `/api/trust-center/activity` | `/v1/synisense/trust-center/activity` |
| synisense | `/api/synisense/observability/snapshot` | `/v1/synisense/observability/snapshot` |
| synisense | `/api/synisense/dryrun` | `/v1/synisense/dryrun` |
| solva | `/api/solva/briefing/state` | `/v1/solva/briefing/state` |
| solva | `/api/solva/v2/health` | `/v1/solva/v2/health` |
| solva | `/api/workbook/analyses` | `/v1/solva/workbook/analyses` |
| solva | `/api/solva/v2-poc/status` | `/v1/solva/v2-poc/status` |

**Per-context route counts at clone time** (from startup log):
- synisense: **40** routes cloned
- solva: **62** routes cloned
- akki: **595** routes cloned
- **Total cloned: 697** (= every public `/api/*` operation across all 134 routers, minus the operational exclusions).

---

## 2. OpenAPI evolution proof

| Slice | Paths | Ops | `sha256[:16]` | Status |
|---|---:|---:|---|---|
| `/api/*` | 621 | 697 | `cdcb23322bb82895` | ✅ unchanged (Phase 4.1 ratchet held) |
| `/v1/*` | 619 | 695 | `acc51822aa8818ae` | 🆕 new baseline (Phase 4.4) |
| **combined** | **1240** | **1392** | **`ca9429c64e44570c`** | 🆕 new baseline (Phase 4.4) |

**Path count delta** = 621 − 619 = **2**, which equals the exclusion list size in the public OpenAPI:
- `/api/healthz/clamav` (Phase 10 ClamAV liveness probe)
- `/api/healthz/shield` (H2.5 Shield warmup probe)

Both are operational endpoints exposed under `/api/*` only; the per-context healthz probes added in Phase 4.3 are `include_in_schema=False` so they don't appear in either slice.

Slice-extraction helper lives in `tests/test_phase4_4_dual_mount_smoke.py::_slice_hash` (the `tests/invariants/` directory hosts the cross-context + tenancy invariants; the slice-hash invariant is co-located with the dual-mount integration smoke since the two share fixtures).

---

## 3. Integration smoke results

`tests/test_phase4_4_dual_mount_smoke.py` — **38 tests, all PASS**.

Breakdown:
- 5 slice/count/namespace invariants (sync).
- 30 byte-equivalence parametrized tests covering Akki (10), SyniSense (8), Solva (5), admin (4), tenancy-walled (4) routes — mix of public-readable, auth-walled, admin-walled, and tenancy-scoped surfaces. Each test issues two requests against the same fresh `httpx.AsyncClient(ASGITransport)` session — status must match, top-level JSON shape (key set / list length) must match, value-level equality asserted when no intrinsic freshness is involved.
- 2 wrong-context 404 negatives (`/v1/akki/trust-center/activity` → 404; `/v1/solva/contexts` → 404; `/v1/synisense/workbook/analyses` → 404; `/v1/wrongcontext/health` → 404).
- 1 exclusion-list assertion (healthcheck triad + internal transport are /api-only; `/v1/akki/healthz/akki` and `/v1/akki/internal/...` return 404).

Why shape-equality and not byte-equality everywhere: some handlers mint fresh state on every call (CSRF rotation, health-check probe timestamps, request_ids). Those are NOT route-divergence between `/api/*` and `/v1/*`; they're handler determinism artefacts. The wall we're guarding against is "wrong handler" / "wrong status code" / "lost dependency" — all of which manifest at the status/shape layer. The 30 cases cover that wall.

---

## 4. Test results

| Suite | Pass | Skip | Fail |
|---|---|---|---|
| `tests/invariants/` (default) | 34 | 10 (deliberate-smoke gates + LLM HUMAN_REQUIRED + upload schema drift) | 0 |
| `tests/invariants/test_invariant_cross_context_violations_smoke.py` (`AKKI_RUN_DELIBERATE_CROSS_CONTEXT_VIOLATION_SMOKE=1`) | 3/3 deliberate violations detected | — | 0 |
| `tests/invariants/test_invariant_violations_smoke.py` (`AKKI_RUN_DELIBERATE_VIOLATION_SMOKE=1`) | 4/4 deliberate violations detected | — | 0 |
| `tests/test_phase4_4_dual_mount_smoke.py` | **38** | 0 | 0 |
| `tests/test_phase4_2_http_transport_smoke.py` | **8** | 0 | 0 |
| `tests/test_p1_a_intel_to_pulse.py` + `test_patch_6_pulse_synisense.py` + `test_phase_p5_19_signal_cycle_adapter.py` + `test_phase_h1_portfolio_landing.py` + `test_phase_f_engine_signals.py` + `test_phase_i3_top_signals.py` + `test_iter41_signal_actions_in_process.py` | **73** | 0 | **1 (pre-existing, confirmed)** |

The single failure (`test_phase_f_engine_signals.py::test_monitor_update_status_objective`) was independently verified as pre-existing by re-running with all Phase 4.4 + Phase 4.3 changes stashed — it still fails on the original tree, so it is **not attributable to Phase 4.4**.

`/api/*` slice hash and route count verified unchanged on the live `/api/openapi.json` endpoint (`paths=621, hash=cdcb23322bb82895`).

---

## 5. MASTER_STATE diff

```
- Phase 4.3 — Container Topology + Healthcheck Triad + Final Hatch Dissolution: ✅ DONE 2026-06-23
+ Phase 4.3 — Container Topology + Healthcheck Triad + Final Hatch Dissolution: ✅ DONE 2026-06-23
+ Phase 4.4 — Dual-Mount Versioned Surface: ✅ DONE 2026-06-23
  Phase 5  — Deployment separation (sell-ready): 📋 NEXT
```

Public surface ratchet:
```
+ /api/* slice    sha256[:16] = cdcb23322bb82895   (unchanged since Phase 4.1)
+ /v1/*  slice    sha256[:16] = acc51822aa8818ae   (new baseline)
+ combined         sha256[:16] = ca9429c64e44570c   (new baseline)
```

---

## 6. Sprint memo pointer

* Master state: `/app/memory/MASTER_STATE.md` (Section 6 promoted Phase 4.4 → Active/✅; Phase 4.3 demoted to Section 6.x historical).
* Prior sprint memos:
  * `/app/memory/sprints/PHASE_4_1_THREE_APPS.md`
  * `/app/memory/sprints/PHASE_4_2_HTTP_TRANSPORT.md`
  * `/app/memory/sprints/PHASE_4_3_TOPOLOGY.md`
* API versioning policy: `/app/memory/API_VERSIONING.md` (NEW).
* New code paths:
  * `/app/backend/routers/v1_dual_mount.py` — the dual-mount mechanism + exclusion list.
  * `/app/backend/server.py` — three `dual_mount_v1(...)` calls (one per owning context) after the existing router mounts.
  * `/app/backend/tests/test_phase4_4_dual_mount_smoke.py` — 38-test gate.
* Edited test:
  * `tests/test_phase4_2_http_transport_smoke.py` — `test_internal_transport_openapi_hash_unchanged` now slices to `/api/*` before hashing (so the Phase 4.1 ratchet check works in the presence of the new `/v1/*` slice).

---

## 7. Deviations Log

### Deviation #1 — operation_id collisions across same-named handlers
**Symptom:** Several handler functions share names across routers — e.g. `download_export`, `list_documents`, `patch_document`, `record_view`, `get_engagement`, `register`, `consume_magic_link`. FastAPI's default operation_id is derived from the handler function name + path, so cloning created duplicate operation IDs in the OpenAPI document.
**Action taken:** Suffix every cloned route's `operation_id` with `_v1_<owning_context>_<sha1(original_path)[:8]>`. The path hash guarantees uniqueness because FastAPI itself disallows duplicate paths. Same suffix applied to the route's `name` so reverse-resolve helpers (e.g. `app.url_path_for`) work.
**Acceptance impact:** No FastAPI warnings about duplicate operation IDs on app boot.

### Deviation #2 — TestClient + Motor event-loop incompatibility
**Symptom:** First draft of `tests/test_phase4_4_dual_mount_smoke.py` used `starlette.testclient.TestClient`. TestClient spins its own event loop, which terminates at module exit, closing the loop that Motor's module-singleton `db` client was bound to. Subsequent async tests in OTHER files (e.g. `test_iter41_signal_actions_in_process.py`) then crashed with `RuntimeError: Event loop is closed`.
**Action taken:** Rewrote the smoke to use `httpx.AsyncClient(transport=httpx.ASGITransport(app=app))` + `async def test_...` so the session-scoped pytest-asyncio loop (configured in `pytest.ini`) is honoured. Motor stays bound to the session loop for the whole run; no event-loop churn across test modules.
**Acceptance impact:** `pytest tests/test_phase4_4_dual_mount_smoke.py tests/test_iter41_signal_actions_in_process.py` → 52/52 PASS with no cross-module interference.

### Deviation #3 — `/api/healthz/{clamav,shield}` excluded from `/v1/*`
**Symptom:** The Phase 4.4 dispatch convention says EVERY `/api/*` route is dual-mounted; but `/api/healthz/clamav` and `/api/healthz/shield` are operational liveness probes for the bundled process, not part of the per-context commercial surface.
**Action taken:** Added them to the `_EXCLUDED_PREFIXES = ("/api/internal/", "/api/healthz/")` exclusion list in `routers/v1_dual_mount.py`. Documented in `/app/memory/API_VERSIONING.md` under "What is NOT dual-mounted." Captured in the smoke test as `test_dual_mount_count_invariant` (expected delta = 2).
**Acceptance impact:** The 2-path delta between the `/api/*` and `/v1/*` slices is explicit, asserted, and documented.

---

## 8. Phase 5 handoff notes

Phase 4.4 leaves Phase 5 (deployment separation, sell-ready) ready to dispatch with the following pre-staged primitives:

**What's already in place for Phase 5:**
1. **Three independently runnable apps** (`akki_app:app`, `synisense_app:app`, `solva_app:app`) — each importable and serveable by a fresh uvicorn instance. Phase 4.3 verified standalone runnability.
2. **HTTP transport substrate** (`contracts/_adapters/_http_client.py`) — every cross-context call automatically routes via `/api/internal/v1/<context>/method/<name>` when `BOUNDED_CONTEXT_TRANSPORT=http`. Per-context base URL overrides (`INTERNAL_TRANSPORT_BASE_URL_{AKKI,SYNISENSE,SOLVA}`) are wired and read at call time.
3. **Healthcheck Triad** (`routers/healthz_context.py`) — per-context probe + composite proxy. Phase 5 K8s deployment can wire each context's `livenessProbe` and `readinessProbe` to its own probe + use the composite for top-level dashboards.
4. **Versioned surface** (`/v1/{context}/*`) — partner SDKs and external integrations can consume the stable contract independent of the legacy `/api/*` slice.
5. **Honesty contract** — `/api/*` slice hash `cdcb23322bb82895` is asserted on every `pytest tests/test_phase4_2_http_transport_smoke.py` run + every `pytest tests/test_phase4_4_dual_mount_smoke.py` run. Any drift fails the gate.

**What's left for Phase 5:**
1. **Supervisor unlock.** `/etc/supervisor/conf.d/supervisord.conf` is platform-`READONLY`. Phase 5 needs the deploy lane to lift this read-only mark or provide a writable supervisor sub-config so each `*_app` runs on its own port (`akki:8001`, `synisense:8011`, `solva:8012`).
2. **Per-context Dockerfile** — three Dockerfiles, one per context, each invoking `uvicorn <ctx>_app:app --port <port> --workers <n>`. Shared base image with the venv + requirements.
3. **Per-context env wiring.** Set `INTERNAL_TRANSPORT_BASE_URL_<CTX>` per pod so each sibling addresses the others over the cluster network; flip `AKKI_PROCESS_NAME=<context>_app` so healthz probes correctly identify the host.
4. **Commercial sell-ready package.** Pricing tiers, SDK build pipeline (consume the `/v1/*` slice of the OpenAPI doc), partner onboarding doc. The user has scoped this as part of the Phase 5 brief but explicitly deferred drafting to the Phase 5 dispatch.
5. **Cohort cron supervisor split.** A few cron jobs live in the bundled `server.py` startup hook; they will need to move into the owning-context's `<ctx>_app.py` lifespan so each cron runs in exactly one process.

Each of these is a config / deployment change — no code refactor required. The Phase 4.4 surface contract makes the cutover mechanical.

---

**End of Phase 4.4 sprint memo.**
