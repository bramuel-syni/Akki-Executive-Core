**Canonical Spec: user dispatch 2026-07-05 · `JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY` (CLASSIFY-ONLY arc, R7 zero-touch)**

# JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY · Classification Memo

**Arc discipline:** CLASSIFY-ONLY. Zero code / config / env / silencing / gating touches to `contracts/_adapters/_http_client.py`, its callers, `BOUNDED_CONTEXT_TRANSPORT`, or any try/except surface. Shield UNTOUCHED. Testing sub-agents BANNED. MOCKED-integrations line preserved. HARD STOP at report close.

**Received-scope echo (per Amendment-Echo rule):**
1. Target identification of `_call` under `contracts/_adapters/_http_client.py`.
2. Surface enumeration of static callers via `get_akki` / `get_synisense` / `get_solva` (dynamic-resolution edge declared where indeterminate).
3. Per-surface failure-mode classification (fail-closed / silent-degrade / defensive-degrade).
4. Environment scope (preview pod vs prod posture; `BOUNDED_CONTEXT_TRANSPORT` resolution).
5. Evidence-bundle priority audit (5 bundles under `/app/memory/evidence/2026_07_02/`) → review-sitting verdict.

**Two reinforcements received (echoed):**
- **§5 is the gating deliverable.** Where §2 is dynamically-resolved, declare `dynamically-resolved · exact caller set indeterminate at static-analysis time` and audit each bundle honestly against BOTH static-enumerated callers AND the dynamic-resolution edge.
- **Zero-touch reinforcement.** Fixing the shell-loop bug in our own tooling is fine. Any tempting fix inside `_http_client.py`, its callers, `BOUNDED_CONTEXT_TRANSPORT`, or try/except surfaces = STOP + revert. If something egregious is surfaced mid-recon (e.g., bare `except: pass` swallowing timeout), record it in §3 as a SILENT-DEGRADE finding + flag for user disposition. Do NOT fix it.

---

## §1 · Target identification

**File:** `backend/contracts/_adapters/_http_client.py`
**Method:** `_HTTPAdapterBase._call(self, method_name, **kwargs)` at lines 230-288.

**Behaviour (as-shipped, unmodified):**

1. Composes URL `f"{self._base_url}/api/internal/v1/{self.context_name}/method/{method_name}"` (L231).
2. Adds `X-Internal-Auth: <INTERNAL_TRANSPORT_SECRET>` header (L232).
3. Resolves per-method timeout via `_PER_METHOD_TIMEOUT_S` map (L77-79) — currently only `shield_invoke=120.0s`; everything else defaults to `DEFAULT_TIMEOUT_S=5.0s` (L60).
4. Sanitizes kwargs via `_sanitize_kwargs_for_json` (L140-170) — Pydantic → `.model_dump(mode='json')`; dataclass → `dataclasses.asdict`.
5. `httpx.AsyncClient(timeout=method_timeout).post(url, json=json_kwargs, headers=headers)` (L245-246).
6. On `200` → JSON parse → DTO reconstruct (L247-251).
7. On `4xx` → **fail-fast** raise `httpx.HTTPStatusError` (L253-263).
8. On `httpx.TransportError` / `httpx.TimeoutException` → retry with jittered exponential back-off (`DEFAULT_BACKOFF_BASE_S=0.1` × 2^(attempt-1) + `uniform(0, 0.05)`) up to `DEFAULT_RETRIES=3` attempts (L269-279).
9. After retries exhausted → `raise last_exc` with `.error("HTTP transport %s.%s exhausted %d retries")` log (L281-288).

**Transport resolution (dynamic):**
- `contracts.__init__._transport_mode()` reads `BOUNDED_CONTEXT_TRANSPORT` env at call time (L65-67).
- `get_akki()` / `get_synisense()` / `get_solva()` route to HTTP adapter iff `_transport_mode() == "http"` (L70-94).
- HTTP adapter classes are **built dynamically** at first use via `_make_http_adapter` (L294-333) using `inspect.getmembers(inproc_adapter)` — the exact method surface is discovered at class-load time, not enumerable statically without importing the in-process adapter.
- **`_thunk`** closure at L321-327 dispatches every public method call through `_call(method_name, **kwargs)`.

**Confirmed in-pod state (recon-only):**
- `backend/.env` L104: `BOUNDED_CONTEXT_TRANSPORT=http` (preview pod runs in HTTP transport mode).
- Base URLs: `INTERNAL_TRANSPORT_BASE_URL_AKKI` / `_SYNISENSE` / `_SOLVA` empty (L107-109) → fallback `DEFAULT_BASE_URL=http://127.0.0.1:8001` (L56-59). Loopback to same uvicorn.
- Backend logs `/var/log/supervisor/backend.err.log` grep confirms live `httpx.ConnectTimeout` stack frames at `_http_client.py:246` (post-`client.post`) and `_http_client.py:286` (post-retry raise).

---

## §2 · Surface enumeration

**Static-analysis caller set (grep `get_akki|get_synisense|get_solva` on `backend/**.py`, excluding tests):**

| Layer | File | Sites |
|---|---|---:|
| Routers | `routers/chat.py` | 10 (streaming + non-streaming Shield hops) |
| Routers | `routers/solva_v2.py` | 12 (context / signal / doc / membership reads) |
| Routers | `routers/sandbox.py` | 6 (signal insert / delete / list) |
| Routers | `routers/documents.py` | 3 (signal list · Shield-invoke) |
| Routers | `routers/solva_phase_d.py` | 5 (doc / cycle reads · Shield-invoke · doc insert) |
| Routers | `routers/trust_center.py` | 10 (chat / context / membership / message reads) |
| Routers | `routers/work_studio_overlay.py` | 1 (Shield-invoke thin wrapper) |
| Routers | `routers/portfolio.py` | 2 (signal count aggregations) |
| Routers | `routers/home.py` | 2 (signal counts / lists) |
| Routers | `routers/company_home.py` | 3 (signal aggregations / counts / lists) |
| Routers | `routers/signals_ask.py` | 1 (doc count) |
| Routers | `routers/committees.py` | 1 (signal unset) |
| Routers | `routers/comments.py` | 1 (signal get) |
| Routers | `routers/cycle.py` | 1 (signal get) |
| Routers | `routers/lens.py` | 1 (signal get) |
| Routers | `routers/simulate.py` | 1 (signal list) |
| Routers | `routers/synisense_metrics.py` | 1 (chat get) |
| Routers | `routers/admin_shield_backfill.py` | 1 (chat count) |
| Services | `services/synisense/engine/signal_derivation.py` | 12 (cycle / message / doc / objective / membership reads) |
| Services | `services/synisense/engine/signal_seeder.py` | 2 (cycle / context reads) |
| Services | `services/synisense/shield/tenant_entities.py` | 1 (Akki accessor) |
| Services | `services/synisense/deck_signal_extraction.py` | 2 (Shield-invoke) |
| Services | `services/tasks/compile_service.py` | 1 (Shield-invoke — wrapped, see §3 D3) |
| Services | `services/tasks/intelligence_service.py` | 1 (Shield-invoke — wrapped, see §3 D3) |
| Services | `services/solva_v2/analyze_narration.py` | 1 (Shield-invoke thin wrapper) |
| Services | `services/work_studio/confidence_scorer.py` | 1 (Shield-invoke thin wrapper) |
| Services | `services/sandbox_generation.py` | 1 (Shield-invoke) |
| Services | `services/inbox_routing/backfill.py` | 1 (signal find) |
| Services | `services/analyze_workspace/tips.py` | 1 (SyniSense accessor) |
| Services | `services/analyze_workspace/ask.py` | 1 (SyniSense accessor) |
| Services | `services/signal_dedup.py` | 1 (SyniSense accessor) |
| Services | `services/universal_search.py` | 1 (signal search) |
| Boot | `backend/server.py` | 1 (engine derivation backfill task — see §3 D2) |

**Static-analysis total:** ~85 call sites across 32 files (approximate — grep is over-inclusive for import-only lines).

**Dynamic-resolution edge — declared explicitly:** `dynamically-resolved · exact caller set indeterminate at static-analysis time`.

Reasons the exact `_call` invocation set is NOT statically enumerable:
1. **Runtime env-var switch.** `contracts.__init__._transport_mode()` re-reads `BOUNDED_CONTEXT_TRANSPORT` on **every** `get_akki()` / `get_synisense()` / `get_solva()` invocation (L65-67 of `contracts/__init__.py`). Which route hits `_call` depends entirely on env at that instant.
2. **Registry-built adapter classes.** `_make_http_adapter` (L294-333 of `_http_client.py`) uses `inspect.getmembers(inproc_adapter)` to discover the method surface at class-load time. The exact set of method names routed through `_call` is a function of the in-process adapter's public method surface — not enumerable without importing the adapter module.
3. **Closure-captured method name.** Every method on the generated HTTP adapter is a `_thunk` closure that captures `_method_name` via default-arg (L321). Static grep for `_call(` finds the base method definition only; the actual call sites are `_thunk` invocations that appear as attribute access (`adapter.list_signals(...)`), not `_call` calls.

**In-pod truth (recon-only):** With `BOUNDED_CONTEXT_TRANSPORT=http` set in `/app/backend/.env` (L104), **every one** of the ~85 static call sites routes through `_call` in this preview pod. In prod, the same env value would produce the same routing (Phase 4.3 http-default flip per §4 §4 of `_HTTPAdapterBase` docstring at L15).

---

## §3 · Per-surface failure-mode classification

Four caller postures observed. Each is classified against the three canonical modes: **FAIL-CLOSED** (exception surfaces to caller / client), **SILENT-DEGRADE** (exception swallowed without log emission), **DEFENSIVE-DEGRADE** (exception swallowed WITH log emission + intentional fallback per docstring / design).

### D1 · Base adapter layer — `_HTTPAdapterBase._call` itself

**Classification: FAIL-CLOSED.** Correct discipline.

- Retries `TransportError`/`TimeoutException` up to 3 attempts with back-off (L269-279).
- After exhaustion emits `.error("HTTP transport %s.%s exhausted %d retries — surfacing failure", exc_info=True)` (L281-284).
- Raises `last_exc` (L286-288). No swallow.
- 4xx short-circuits with `.error("HTTP transport %s.%s 4xx (status=%d) — fail-fast")` + raise `HTTPStatusError` (L255-263).

**Evidence:** `_http_client.py:281-288` (surface + raise). Backend log line 390133 confirms real emission: `2026-07-05 07:48:34,982 - akki - WARNING - [engine] derivation backfill failed: ConnectTimeout: …` — the `.warning` there is the CALLER of `_call` (see D2); `_call` itself logged `.error` upstream with stack trace at `_http_client.py:246` and `_http_client.py:286` per grep (100+ occurrences in log).

### D2 · Server startup engine backfill (`backend/server.py:540-565`)

**Classification: DEFENSIVE-DEGRADE.** Log-visible. Intentional per inline docstring citing the 2026-06-26 startup-race fix.

- Wraps `_engine_backfill()` in a boot-grace-window sleep (`ENGINE_BACKFILL_BOOT_GRACE_S`, default 20.0s) so uvicorn listener is up before HTTP-transport loopback fires.
- `try/except Exception:` around backfill body emits `logger.warning("[engine] derivation backfill failed: %s: %s", type(exc).__name__, str(exc)[:200])` (L559-561).
- Outer try/except around scheduling emits `logger.warning("[engine] derivation backfill scheduling failed: %s", e)` (L564-565).
- Comment (L539) explicitly notes the hourly cron is the durable scheduler — the boot backfill is a "convenience refresh" only.

**Evidence:** Backend logs confirm both failure (390133) and successful recovery (`2026-07-05 14:16:38.407` onward — 24 tenants successfully derived signals via hourly cron re-run). Failure IS log-visible; degradation IS intentional.

### D3 · Best-effort Shield wrappers (`services/tasks/compile_service.py`, `services/tasks/intelligence_service.py`)

**Classification: DEFENSIVE-DEGRADE.** Log-visible. Documented in docstring.

- `compile_service.shield_invoke_bounded` (L75-103): 3.0/120.0s `asyncio.wait_for` around `get_synisense().shield_invoke(...)`; `except asyncio.TimeoutError` returns `{"__timeout__": True, "purpose": purpose}` + emits `log.warning("shield timeout: purpose=%s timeout=%.1fs")`; `except Exception as e` returns `None` + emits `log.warning("shield failed: purpose=%s err=%s")`.
- Docstring explicit: *"Returns None on timeout or any failure so callers can fall back to deterministic behaviour without distinguishing the failure mode."*
- `intelligence_service._task_shield_recommendations` (L225-265): 3.0s `wait_for` + same pattern; docstring: *"Best-effort Shield call ... Returns None on any failure — caller substitutes the rule-based fallback."*
- Both call sites wrap `from contracts import get_synisense` in `try/except Exception: return None` — imports rarely fail; belt-and-braces.

**Not silent-degrade because:** every path emits a log line describing the failure. Callers substitute rule-based deterministic output.

### D4 · Direct call sites in routers/services (no wrapper)

**Classification: FAIL-CLOSED.**

- Sites like `routers/sandbox.py:283 await get_synisense().insert_signals_for_context(...)`, `routers/portfolio.py:94 return await get_synisense().count_goals_at_risk(...)`, `services/synisense/engine/signal_derivation.py:90 await get_akki().list_cycles(...)`, `routers/chat.py:588 result = (await get_synisense().shield_invoke(...))` — no local `try/except` wrapper.
- Exception propagates up through FastAPI's request handler → 500 response (or the wrapping caller's own exception discipline).
- User-visible failure. NOT silent.

### Silent-degrade findings (surfaced per reinforcement 2 — NOT fixed per R7)

**Grep-scan across the primary caller surfaces** (`routers/chat.py`, `routers/documents.py`, `services/tasks/compile_service.py`, `services/tasks/intelligence_service.py`, `services/synisense/deck_signal_extraction.py`, `routers/work_studio_overlay.py`, `services/solva_v2/analyze_narration.py`, `services/work_studio/confidence_scorer.py`) for `except:` bare-except or `except Exception:` blocks wrapping contract-layer calls:

- **`routers/documents.py:584,630,642,884,952`** — `except Exception:` / `except Exception: pass`. Each inspected against surrounding code:
  - L584: wraps `services.metadata_signatures.derive_and_persist(...)` (Mongo/Motor writes only, no `get_akki`/`get_synisense`/`get_solva` inside) — comment `# pragma: no cover — non-fatal`. **NOT silent-degrade of `_call`.**
  - L630: wraps `background_tasks.add_task(auto_extract_after_upload, ...)` — enqueue-only; the task body itself has its own try/except. **NOT silent-degrade of `_call`.**
  - L642: wraps `db.accounts.update_one(...)` — Mongo write only. **NOT silent-degrade of `_call`.**
  - L884: wraps `write_audit(...)` — Mongo audit-log write only. **NOT silent-degrade of `_call`.**
  - L952: wraps `write_audit(...)` — Mongo audit-log write only. **NOT silent-degrade of `_call`.**
- **`routers/chat.py:2812,2826,3737,3900`** — `except Exception:` blocks. Spot-inspected (see file view in recon):
  - L2812/2826 wrap streaming SSE cleanup logic (client disconnect / task cancellation).
  - L3737/3900 wrap audit / analytics side-effects around already-completed request paths.
  - None wrap direct `_call` invocations at the contract layer without a preceding log emission.
- **`services/tasks/compile_service.py:85`** and **`services/tasks/intelligence_service.py:234`** — these are `except Exception: return None` around `from contracts import get_synisense` (import guard, not call guard). The actual `_call` failure path is caught SEPARATELY at L101-103 / L264-266 with `.warning` emission → DEFENSIVE-DEGRADE (D3).

**Verdict:** Zero silent-degrade findings in the primary contract-caller surface. All Shield-wrapping code paths audited emit log lines; all direct call sites fail-close. Findings are recorded here for user disposition; **no code change made** per R7 zero-touch discipline.

### §3 · Addendum · 2026-07-05 · TRANSIENT-UPSTREAM-VOLATILITY (banked as third failure-mode class)

**Lineage cite:** `JC-GEN-PATH-CONNECTTIMEOUT` arc (2026-07-05) — user amendment A2 requested this classification be banked as first-class, since the original dispatch's two paths (config-class · service-missing) did not anticipate this third state. See `sprints/JC_GEN_PATH_CONNECTTIMEOUT.md` Step 0 verdict.

**D5 · TRANSIENT-UPSTREAM-VOLATILITY** (third class · added 2026-07-05): applies when an upstream target (e.g. `https://integrations.emergentagent.com/llm/chat/completions`) is **reachable at TCP+TLS handshake** (connect < 5ms · DNS clean · no env misconfig) BUT **intermittently returns Cloudflare-fronted 502 / origin-timeout responses** under real workload conditions. Signature body: `"The origin web server returned an invalid or incomplete response to Cloudflare. This typically indicates the origin is overloaded or misconfigured."`. Origin-side or preview-pod-side attribution undetermined without upstream cooperation. Distinct from D1-D4 because the base `_call` retry policy (3 attempts) can be exhausted deterministically per generation call when the failure window is durable rather than stochastic. **Disposition path:** honest BLOCKED-BY-ENV declaration for UI stories (per state-injection corollary of RULE-UI-STORIES-CLOSE-ON-UI-LAYER-ONLY) + user-side remediation via one of: environmental switch, retry-policy tuning of `_PER_METHOD_TIMEOUT_S` for the affected surface, or upstream escalation. **Not fixable within CLASSIFY-ONLY discipline** (retry-policy tuning would touch FAIL-CLOSED surface).

---

## §4 · Environment scope

**Preview pod (this environment):**
- `/app/backend/.env` L104: `BOUNDED_CONTEXT_TRANSPORT=http`
- `/app/backend/.env` L107-109: per-context base URLs empty → fallback to `DEFAULT_BASE_URL=http://127.0.0.1:8001` (`_http_client.py:56-59`).
- `INTERNAL_TRANSPORT_SECRET` present (L93).
- Every `get_akki` / `get_synisense` / `get_solva` invocation routes through `_call` → HTTP POST to `127.0.0.1:8001/api/internal/v1/…`.
- Backend log evidence: `httpx.ConnectTimeout` at `_http_client.py:246` (post-`client.post`) — approximately 100+ frames captured in `/var/log/supervisor/backend.err.log`. The pattern clusters around cold-start windows (before uvicorn socket binds) and occasional transient loopback saturation.
- **Cold-start mitigation already in place:** `server.py:540-565` boot-grace-window (`ENGINE_BACKFILL_BOOT_GRACE_S=20.0`) defers the engine backfill task, and the hourly cron is the durable scheduler. Backend log at 14:16 shows 24 tenants successfully derived signals — recovery works.

**Production posture (unmodified inference from repo state):**
- Same `BOUNDED_CONTEXT_TRANSPORT=http` default is expected in prod (Phase 4.3 http-default flip per `_http_client.py:15` docstring).
- Prod pods run uvicorn on the same 8001 loopback. Same routing shape as preview.
- Prod-vs-preview delta:
  - Cold-start frequency: prod likely has warmer, longer-lived pods → cold-start ConnectTimeout window narrower.
  - Loopback saturation: prod resource limits may differ; preview pod resource ceiling may induce transient loopback stalls.
- **No evidence in this arc of prod incidents** — this scope is a preview-pod recon only.

**Scope of failure mode:** LOCAL loopback (not public-internet). Cause is one of:
- Cold-start race (uvicorn not yet listening) — mitigated by boot-grace-window.
- Loopback socket saturation / workqueue backpressure.
- `httpx.AsyncClient` per-call instantiation (L245) — every `_call` invocation creates a fresh client; connection-pool reuse not in play.

**Reader-scope reminder:** classifying only. No hypotheses beyond what backend logs substantiate.

---

## §5 · Evidence-bundle priority audit (gating deliverable)

**Bundle set:** 5 bundles at `/app/memory/evidence/2026_07_02/`. Manifest at `MANIFEST_2026_07_02.json`.

For each bundle, the capture path is audited against the `_call` transport (static caller enumeration + dynamic-resolution edge). Verdict is per-bundle then rolled up to the review-sitting verdict.

### B4 · Owner Digest (`bundle_v0_5_owner_digest/`)

- **Status per manifest:** `CAPTURED-devmode`.
- **Capture script:** `backend/scripts/jc_bundle_capture_2026_07_02.py::capture_b4_owner_digest`.
- **Capture path:** `AsyncIOMotorClient(MONGO_URL)` → direct Mongo reads. Composer: `from services.owner_digest import build_owner_digest, _build_subject, _build_plain_body, _build_html_body`.
- **Static grep of `services/owner_digest.py`:** ZERO references to `get_akki` / `get_synisense` / `get_solva` / `_call`. All reads via direct Motor client.
- **Dynamic-resolution edge for B4:** N/A — capture path does not touch the contract layer.
- **`_call` invoked in this bundle's capture?** **NO.**
- **Content quality:** `owner_digest_payload.json` shows `rows: []` + `rows_count: 0`. README declares honestly: *"Julius NED Seat context has 0 `strategic_goals` rows at capture time"* — this is a **substrate gap**, not a transport failure.
- **Bundle verdict:** CLEAN. Empty rows reflect declared substrate scarcity, not silent-degrade from ConnectTimeout.

### B3 · Monitor Reassessment (`bundle_v0_5_monitor_reassessment/`)

- **Status per manifest:** `GAP-DECLARED`.
- **Capture script:** substrate probe via direct Mongo (`db.monitor_background_items.count_documents({...})`).
- **Static grep of the probe:** ZERO contract-layer references. Direct Motor client only.
- **`_call` invoked?** **NO.**
- **Substrate finding:** `monitor_items_all_julius_ctxs: 0`. Bundle declares fallback-vector infeasibility honestly and closes GAP-DECLARED per dispatch discipline (force-fire forbidden).
- **Bundle verdict:** CLEAN. Gap-declared status is substrate-driven, not transport-driven.

### B1 · Work Studio LLM refresh (`bundle_llm_refresh_2_work_studio/`)

- **Status per manifest:** `PARTIAL`.
- **Capture script:** direct Mongo (`db.documents.count_documents(...)` + `db.work_studio_exports.find(...)`) to probe substrate + roster.
- **Static grep:** ZERO contract-layer references.
- **`_call` invoked?** **NO.**
- **Content:** `substrate_probe.json` (NED=3 docs, Govt Exec=3 docs) + `existing_export_rosters.json` (2 exports, `model_roster: null` for both — legacy pre-LLM-refresh rows). README declares honestly: substrate thin; fresh generation would demonstrate LLM degrade on sparse input, not roster refresh quality.
- **Bundle verdict:** CLEAN. Partial status is substrate/quality-driven, not transport-driven.

### B2 · Solva v2 LLM refresh (`bundle_llm_refresh_3_solva_v2/`)

- **Status per manifest:** `GAP-DECLARED (paths verified)`.
- **Capture script:** AST-level import of `services/solva_v2/submodules.py::SUBMODULE_NAMES` + direct Mongo query on `solva_v2_sessions`.
- **Static grep:** ZERO contract-layer references. AST + Motor only.
- **`_call` invoked?** **NO.**
- **Content:** `path_verification.json` shows all 4 dispatch paths present in shipped code with zero drift (`missing_from_ship=[], extras=[]`); `julius_existing_solva_sessions=0`.
- **Bundle verdict:** CLEAN. Gap declared honestly on session-substrate + LLM-streaming budget.

### B5 · Origin Briefs (`bundle_v0_5_origin_briefs/`)

- **Status per manifest:** `PARTIAL (contract verified)`.
- **Capture script:** Pydantic model introspection of `_TL_BriefExportIn.origin_kind` field annotation + direct Mongo `work_studio_exports.find({"origin_kind": {"$ne": null}})`.
- **Static grep:** ZERO `get_akki`/`get_synisense`/`get_solva`. Pydantic reflection + Motor only.
- **`_call` invoked?** **NO.**
- **Content:** `contract_verification.json` shows 4 accepted literals (`monitor_objective / monitor_signal / solva_session / task_manager_task`) + 4 existing exports with origin stamps. Live emit for julius deferred (0 solva sessions on julius; LLM budget out-of-scope).
- **Bundle verdict:** CLEAN. Partial status is deferred-live-emit, not transport-driven.

### Rollup table

| Bundle | Capture path invokes `_call`? | Bundle content contaminated by ConnectTimeout? | Bundle verdict |
|---|---|---|---|
| B4 owner_digest | NO (Motor + services.owner_digest direct-Mongo) | NO — empty rows = substrate gap (`strategic_goals=0`) | CLEAN |
| B3 monitor_reassessment | NO (Motor `count_documents` only) | NO — 0 items = substrate gap | CLEAN |
| B1 work_studio | NO (Motor find/count only) | NO — 3 docs = substrate thin | CLEAN |
| B2 solva_v2 | NO (AST import + Motor count only) | NO — 0 sessions = substrate absent | CLEAN |
| B5 origin_briefs | NO (Pydantic introspection + Motor find only) | NO — deferred live emit = budget scoped-out | CLEAN |

### Static-analysis vs dynamic-resolution audit (per reinforcement 1)

The **static caller set** for these capture scripts contains: `AsyncIOMotorClient`, `services.owner_digest.build_owner_digest`, `services.solva_v2.submodules.SUBMODULE_NAMES`. Zero of these route through `get_akki` / `get_synisense` / `get_solva`, therefore zero route through `_call`.

The **dynamic-resolution edge** is honest here: because none of the capture scripts touch the contract layer at all, the runtime env-var switch inside `contracts.__init__._transport_mode()` is never reached from these scripts. The dynamic-resolution question does not apply.

### Review-sitting verdict

**CLEAR-TO-PROCEED.**

**Rationale:**
- Zero of the 5 evidence bundles invoked `_call` in their capture paths (all use direct Motor client or Python-level AST/type introspection).
- Zero of the 5 bundles have contaminated content attributable to ConnectTimeout. All gaps / partials / empty-row states are substrate-declared honestly in the bundle READMEs.
- The dynamic-resolution edge is inapplicable to the bundle capture surface because the capture surface does not use the contract layer.

**No caveats material to the bundle review.** The environment issue (§4) is real and log-visible, and D2/D3 caller-side degradation is real; but none of it contaminated the 5 bundle artefacts under review.

**Findings surfaced for user disposition (per reinforcement 2 · NOT auto-fixed under R7):**
- No bare `except: pass` swallowing `_call` failures found in the audited surfaces. The `except Exception:` blocks in `routers/documents.py` and `routers/chat.py` wrap unrelated side-effects (audit inserts, background-task enqueue, metadata derivation) and do not silence contract-layer exceptions.
- The environment issue itself (loopback ConnectTimeout in this preview pod, most-visible on cold-start engine backfill) remains open for user disposition (fix / gate / silence). Not in scope for this arc.

---

## Closure section

- **Zero-touch discipline (R7) verified:** `git diff --stat` on `contracts/_adapters/_http_client.py`, `contracts/__init__.py`, `contracts/_adapters/synisense.py`, `contracts/_adapters/solva.py`, `contracts/_adapters/akki.py`, `services/synisense/shield/**`, `backend/server.py` — none touched during this arc. Only files modified: this memo, the proving slice, and DEV_PIPELINE.md §9 row (report-only surface).
- **Push status:** SHIPPED-UNPUSHED with commit hash cited at close (per RULE-CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED · `git remote -v` empty in this preview pod · user pushes from their side).
- **MOCKED-integrations line preserved:** SendGrid dev-mode + Resend mock — untouched (this arc did not touch integration surfaces).
- **Testing sub-agents BANNED:** honoured. Slice-verification via pure bash execution of the proving slice only.
- **Amendment Echo:** both reinforcements from the user's Trigger-2 fire message echoed in the "Two reinforcements received (echoed)" block above.
- **Wrong-Board check:** dispatch line-1 label = `JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY`; matches Akki-Executive-Core arc project scope. Not rejected.

**Nothing auto-fires.** HARD STOP at report close. Awaiting user disposition on the environment issue (fix / gate / silence) and any follow-up dispatch.
