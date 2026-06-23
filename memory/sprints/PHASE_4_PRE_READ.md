# Phase 4 Pre-Read — Process Separation

**Mode:** READ-ONLY reconnaissance. No code changes.
**Predecessor:** Re-Arch Phase 3 ✅ FULLY CLOSED (3.0 + 3.1 + 3.2).
**Output classification:** **ESCALATE — Phase 1 contracts exist but are UNWIRED. Material discrepancy with approved plan, see §11.**
**Date:** 2026-06-23.

---

## 0 · Compliance & Debt Snapshot (Pre-Read close)

| 🟢 In compliance | 🟡 Carry-forward (acknowledged) | 🟠 Debt (active mitigation) | 🔴 Debt (escalation candidate) |
|---|---|---|---|
| Phase 0/1/2/3 lockdowns green | 15 pre-existing test failures (Phase 2.X side-lane) | 314 FE `api.X()` call sites still on raw axios | **Phase 1 contracts exist (21 methods, 3 protocols, 3 adapters) but ZERO production call sites consume them** — see §11 ESCALATE |
| Hot-path JSON-effective coverage 97.7% | 48 cross-context call sites in observe-mode JSON | 55 BE routes still on `Optional[Dict[str, Any]]` baseline | |
| 117 routes narrowed to shared models | 3 boundary imports (Phase 2.X side-lane) | | |
| Drift-catch system live (Phase 3) | | | |
| **No mid-build `ask_human`** — Anti-Forget Protocol §5 honoured throughout this Pre-Read | | | |

**Material finding:** the cross-context call substrate this Pre-Read needs to flip from "in-process" → "HTTP" is **NOT YET ROUTED THROUGH THE CONTRACT PROTOCOLS**. Phase 4 cannot ship without first wiring those call sites through `get_synisense()` / `get_solva()` / `get_akki()`. §11 ESCALATE proposes the resolution path.

---

## 1 · Current process & wiring landscape (Q1)

### 1.A · Entrypoint, app object, supervisor

| Aspect | Live value | Source |
|---|---|---|
| Entrypoint | `backend/server.py` (1462 LOC) | `/etc/supervisor/conf.d/supervisord.conf` |
| App object | `app = FastAPI(title=APP_NAME, docs_url="/api/docs", redoc_url=None, openapi_url="/api/openapi.json")` (server.py L175-180) | server.py |
| Dev launcher | `/root/.venv/bin/uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1 --reload` under supervisor | `supervisord.conf` |
| Prod launcher | `uvicorn server:app --host 0.0.0.0 --port 8001 --workers 1` (Dockerfile.backend `CMD`) | `Dockerfile.backend:120` |
| Worker count | **`--workers 1`** in both dev + prod (`Dockerfile.backend` comment: "APScheduler in-process. Single-replica deploys only") | `Dockerfile.backend:9-13` + `docker-compose.prod.yml:32 deploy.replicas: 1` |
| Healthcheck | `curl -fsS http://localhost:8001/api/health` (docker HEALTHCHECK) → `routers/misc.py:82-87` returns `{status, db}` from `db.command("ping")` | both Dockerfile + prod compose |

### 1.B · `app.include_router(...)` inventory

server.py mounts **136 routers** via `include_router` (grep count). All share the `/api` prefix internally (per the `# Register routers (all share /api prefix internally)` comment at server.py:182). Mounted in a flat list spanning L183-410.

**Natural-context grouping (manual map per Phase 1 boundary-imports baseline `/app/memory/invariants/boundary_imports.baseline.json`):**

| Future context | Routers | Sample files (representative) | Approx % of mounts |
|---|---:|---|---:|
| **SyniSense** (governance, shield, NER, audit, engine) | ~11 | `synisense.py`, `synisense_shield.py`, `synisense_engine.py`, `synisense_metrics.py`, `synisense_observability.py`, `signals_ask.py`, `signal_actions.py`, `admin_shield_backfill.py`, `admin_signal_kpi.py`, `healthz_shield.py`, `trust*.py` | ~8% |
| **Solva** (reasoning, narration, workbook v2) | ~8 | `solva_v2.py`, `solva_v2_artefact.py`, `solva_phase_d.py`, `solva_briefing.py`, `solva_telemetry_admin.py`, `workbook_analysis.py`, `lens.py`, `solva_phase_e_polish.py` | ~6% |
| **Akki** (everything else — auth, contexts, documents, work_studio, chats, tasks, cycle, billing, governance, admin, marketing, …) | ~117 | `auth*.py`, `contexts.py`, `documents.py`, `work_studio_*.py` (5 files), `tasks*.py` (3 files), `cycle*.py` (5 files), `chat.py`, `chat_audit_panel.py`, `billing.py`, `admin_*.py` (8 files), `cohort_*.py` (4 files), `home.py`, `events.py`, `decks.py`, `questions.py`, `pulse.py`, `prepare.py`, `monitor*.py` (3 files), `lens_*` etc. | ~86% |

The clean ~11 + ~8 + ~117 split means Phase 4.1 router-redistribution is mechanical: move ~19 SyniSense+Solva router files into their own FastAPI app modules; Akki keeps the rest.

### 1.C · Mongo connection pattern

Single canonical client in `backend/core.py:29-30`:

```python
client = AsyncIOMotorClient(MONGO_URL)
db = client[DB_NAME]
```

**496 files** across `routers/`, `services/`, `contracts/_adapters/`, `scripts/` import `from core import db`. Every router receives the same in-process motor client. No DI of `db`, no per-router pool, no transaction scope.

**Implication for Phase 4:** Q4 Options A/C (process separation with three independent uvicorn instances) each get their own `AsyncIOMotorClient(MONGO_URL)` automatically when each process starts — no behaviour change. The single-replica-only constraint comes from APScheduler, NOT Mongo.

### 1.D · Startup/shutdown lifecycle hooks

server.py defines **two `@app.on_event("startup")` blocks** (L1042-1383 + L1386-1442) and **one `@app.on_event("shutdown")`** (L1445-1462). The first startup block bootstraps:
- Initial logging
- Solva v2 admin flag flip (L1119-1125)
- `AKKI_CRON_SECRET`-gated APScheduler with **7 cron jobs** (L1127-1312)
- spaCy NER warm-up at startup (L1314-1339) — SyniSense-owned, ~1-3s
- SyniSense engine hourly cron with Mongo-lock leader election (L1341-1383)

The second startup block runs the demo seed (L1386-1442) — Akki-owned.

Shutdown hook closes both APSchedulers + the Motor client (skipped under PYTEST_CURRENT_TEST).

---

## 2 · Contract-call wiring audit (Q2)

### 2.A · Contract surface (Phase 1 — present in tree)

| File | LOC | Purpose |
|---|---:|---|
| `backend/contracts/__init__.py` | 107 | Protocol re-exports + DI accessors `get_synisense() / get_solva() / get_akki()` |
| `backend/contracts/synisense.py` | 79 | `SyniSenseContract` Protocol — 5 methods (`shield_invoke`, `get_audit_events`, `get_trust_receipt`, `get_shield_metrics`, `refresh_tenant_entities_cache`) |
| `backend/contracts/solva.py` | 76 | `SolvaContract` Protocol — 5 methods (`synthesize_workbook`, `run_solva_session`, `get_session_state`, `refuse_to_decide_check`, `list_solva_artefacts`) |
| `backend/contracts/akki.py` | 155 | `AkkiContract` Protocol — 11 methods (tenant profile / contexts / cycles / tenant entities / chat history / documents / signals / objectives / cycle_questions / briefings / audit_event) |
| `backend/contracts/types.py` | ~250 | Frozen-dataclass DTOs (TenantProfile, Context, Cycle, Document, Signal, …) |
| `backend/contracts/_adapters/synisense.py` | 159 | `InProcessSyniSenseAdapter` — pass-through to `services.synisense.shield.client.invoke` |
| `backend/contracts/_adapters/solva.py` | 178 | `InProcessSolvaAdapter` — pass-through to `services.solva_v2.*` |
| `backend/contracts/_adapters/akki.py` | 301 | `InProcessAkkiAdapter` — pass-through to direct `db.X` reads |

### 2.B · Contract consumer audit — **THE CRITICAL FINDING**

```bash
$ grep -rn "get_synisense\b\|get_solva\b\|get_akki\b" --include="*.py" \
       | grep -v "contracts/__init__\|tests/"
# (empty)
```

**ZERO production call sites consume `get_synisense() / get_solva() / get_akki()`.** The contracts package is currently a structural fixture — Protocols defined, adapters defined, Phase 1 invariant pinned (`test_invariant_contract_snapshots.py`), but NOT integrated into the runtime call graph.

```bash
$ grep -rn "SyniSenseContract\|SolvaContract\|AkkiContract" --include="*.py" \
       | grep -v "contracts/"
# Only test references in tests/invariants/test_invariant_contract_snapshots.py
```

Confirmation: the only files that name the Protocols outside `contracts/` are the test invariants. **All 48 cross-context call sites still call the underlying primitives DIRECTLY**, exactly as the observe-mode `/app/memory/invariants/cross_context_violations.json` documents.

### 2.C · The 48 cross-context call sites (observe-mode baseline, **still violations today**)

| Caller context | → Target context | Method | Count |
|---|---|---|---:|
| akki | synisense | `shield_invoke` | **24** |
| synisense | akki | `db.cycles.count_documents` | 4 |
| synisense | akki | `db.cycles.find` | 4 |
| synisense | akki | `db.chat_messages.count_documents` | 2 |
| synisense | akki | `db.objectives.count_documents` | 2 |
| synisense | akki | `db.documents.count_documents` | 1 |
| synisense | akki | `db.briefings.count_documents` | 1 |
| synisense | akki | `db.cycle_questions.count_documents` | 1 |
| synisense | akki | `db.documents.find` | 1 |
| synisense | akki | `db.memberships.find` | 1 |
| synisense | akki | `db.contexts.find_one` | 1 |
| synisense | akki | `db.contexts.find` | 1 |
| synisense | akki | `db.accounts.find_one` | 1 |
| akki | synisense | `find_audit` | 1 |
| akki | synisense | `find_receipt` | 1 |
| akki | solva | `narrate_analysis` | 1 |
| solva | synisense | `shield_invoke` | 1 |
| **Total** | | | **48** |

**Top offending files:**
- `services/synisense/engine/signal_derivation.py` — 15
- `routers/chat.py` — 7
- `services/documents/intelligence_service.py` — 3
- `services/synisense/shield/tenant_entities.py` — 3
- `routers/synisense_shield.py` — 2
- `services/synisense/engine/signal_seeder.py` — 2

### 2.D · Sample call-site shape (verbatim live code)

```python
# routers/chat.py:592-594 — Akki → SyniSense, direct primitive call
try:
    from services.synisense.shield.client import invoke as shield_invoke
    result = await shield_invoke(
        purpose="chat.tools.classify_turn",
        content=(...),
        ...
    )
```

```python
# routers/workbook_analysis.py:1089 — Akki → Solva, direct service import
from services.solva_v2.analyze_narration import narrate_analysis
narration = await narrate_analysis(...)
```

```python
# services/synisense/shield/tenant_entities.py — SyniSense → Akki, direct Mongo
async def harvest(account_id: str):
    rows = await db.accounts.find_one({"id": account_id}, {...})  # cross-context
```

**Implication for Phase 4:** the HTTP-transport swap (Q3) operates at the contract-adapter boundary. With zero call sites going through that boundary today, there's nothing for Phase 4.2 to swap. Either:
- (a) Phase 4 inserts a Phase 4.0 sub-dispatch that migrates the 48 call sites through `get_synisense() / get_solva() / get_akki()` first — this is Phase 2's "migrate call sites" work that was deferred. OR
- (b) Phase 4 ships the three FastAPI apps + dual-mount paths first, leaving the 48 in-process call sites alone, and Phase 4.x sub-dispatches migrate them later. The risk is that "process separation" delivers ZERO of its promised crash-isolation benefit until the migration completes — Akki crashing the SyniSense package via a direct import path still takes down SyniSense.

See §11 ESCALATE for the recommended path.

---

## 3 · HTTP transport choice (Q3)

### 3.A · Option A — `httpx` async client ← **RECOMMENDED**

| Aspect | Detail |
|---|---|
| Library | `httpx==0.28.1` (already in `backend/requirements.txt`; **already imported by 8 production files** — server.py, oauth_google.py, admin_health.py, auth_oauth.py, news_aggregator.py, etc.) |
| Bundle / dep cost | **Zero** — already shipped |
| Async surface | Native `httpx.AsyncClient` works with FastAPI's event loop; no thread-pool hop |
| Timeout / retry / circuit-breaker | Built-in `timeout=` param; retries via `httpx.Transport(retries=N)`; no built-in circuit breaker but `tenacity` is also already a transitive dep |
| Mocking in tests | `respx` is the standard mock library (small add); alternatively `httpx.MockTransport` (built-in) for unit tests |
| Latency on localhost loop | ~2-5ms RTT for TCP loopback; ~1-3ms for Unix socket (if used). Realistic per-call overhead: **5-15ms** including TLS handshake (one-time per connection) + serialization |
| Pattern already in tree | `server.py:1137-1142` uses `httpx.AsyncClient(timeout=180.0).post("http://localhost:8001/api/...")` for the in-process cron callbacks. Phase 4's cross-context calls follow this exact pattern just pointing at 8002/8003. |

### 3.B · Option B — Reuse `@zodios/core` generated client on backend

| Aspect | Detail |
|---|---|
| Library | Would require introducing a Python zodios analogue OR running the JS client under Node sidecar. Both bizarre. |
| Bundle / dep cost | Either ~2 GB Node runtime in the backend container OR re-implementing zodios in Python (~weeks of work). |
| Verdict | **Rejected outright.** Symmetric typing sounds clean but adds JS-runtime-shaped abstractions to Python. The OpenAPI spec is already the source of truth — Python clients can be generated from it with `openapi-python-client` if needed. |

### 3.C · Option C — Raw `requests` (sync)

| Aspect | Detail |
|---|---|
| Library | `requests==2.33.1` (already in requirements) |
| Sync vs async | Blocking. Would require `asyncio.run_in_executor(None, requests.X)` to use from FastAPI handlers — adds a thread-pool hop per call. |
| Hot-path cost | chat send-message currently calls `shield_invoke` up to 4× per request. Each `run_in_executor` is ~0.5-1ms overhead. Cumulative 2-4ms is small but UNNECESSARY when `httpx` is right there. |
| Verdict | **Rejected.** Wrong tool for an async FastAPI hot path. |

### 3.D · Recommendation: Option A (`httpx` async client)

Cited live evidence:
- `backend/requirements.txt:httpx==0.28.1` (already present).
- `backend/server.py:1135` already uses `import httpx; async with httpx.AsyncClient(...)` for internal cron callbacks — the EXACT pattern Phase 4 needs at scale.
- Zero new deps, zero new bundle weight, native async, fast.

---

## 4 · Container topology (Q4)

The plan §5 reads: *"all three still run in the same container initially."* Three candidates:

### 4.A · Option A — Supervisord multi-process ← **RECOMMENDED**

| Aspect | Detail |
|---|---|
| Process separation? | **Yes — real.** Three uvicorn instances under supervisord; each its own PID, its own AsyncIOMotorClient, its own spaCy load (or skipped per service) |
| Shared Mongo pool | Each process opens its own client → 3× the Mongo connection count. Mongo's default `maxPoolSize` is 100/client; Atlas tier handles this trivially. |
| Crash isolation | If SyniSense (PID 2) crashes, supervisord restarts ONLY that process. Akki (PID 1) keeps serving traffic. **The whole point of the phase.** |
| Per-service log streams | Each process logs to `/var/log/supervisor/<svc>.{err,out}.log`. Visually separable + searchable. |
| Operational complexity in Emergent | The CURRENT preview pod already uses supervisord (3 programs: backend, frontend, mongodb). Adding 2 more programs is a config edit, no new infra. Prod uses docker; need to switch CMD from raw uvicorn to `tini → supervisord → 3 uvicorns`. |
| Path to Phase 5 | Phase 5 splits the single docker container into three. The supervisord programs in Phase 4 become three docker services in Phase 5. Conversion is mechanical (each `[program:X]` block → one compose `services:` entry). |

### 4.B · Option B — Single uvicorn, three FastAPI apps mounted

| Aspect | Detail |
|---|---|
| Process separation? | **No.** One uvicorn process, three Apps in the same Python interpreter. Mounting tricks. |
| Crash isolation | None. A crash in SyniSense code takes down Akki. |
| Verdict | **Rejected.** The plan's explicit goal is process separation. This is "URL prefix separation" wearing the hat. Honest assessment per the dispatch ask. |

### 4.C · Option C — Three Python processes, single Dockerfile, entrypoint script

| Aspect | Detail |
|---|---|
| Process separation? | **Yes.** Three `subprocess.Popen` calls (or background `&` in shell) launching three uvicorns. |
| Crash isolation | A child crashes → entrypoint script must catch + restart. Re-implements ~20% of supervisord. |
| Path to Phase 5 | Same mechanics as A but the entrypoint script needs to be rewritten when splitting into three containers. A's supervisord-program-per-service maps 1:1 to compose-service-per-container; C's entrypoint script needs decomposition. |
| Verdict | **Worse than A.** Same capability, more bespoke. |

### 4.D · Recommendation: Option A (supervisord multi-process)

Cited live evidence:
- `/etc/supervisor/conf.d/supervisord.conf` already manages `backend`, `frontend`, `mongodb` in the preview pod.
- The Emergent pod runs supervisord natively — adding 2 more `[program:X]` blocks for SyniSense/Solva is the lowest-friction op.
- `docker-compose.prod.yml` currently runs the backend container with raw uvicorn. Phase 4 prod change: switch the `command:` to `/usr/bin/tini -- /usr/bin/supervisord -c /etc/supervisor/supervisord.conf` (in the akki-backend container) + ship the supervisord config in the image. One Dockerfile change.
- Phase 5 splits cleanly: each `[program:X]` block → its own service in `docker-compose.prod.yml`.

**Port allocation proposal:**
- Akki on **8001** (public-facing, the only one ingress forwards to — preserves the K8s `/api/*` routing).
- SyniSense on **8002** (loopback-only).
- Solva on **8003** (loopback-only).

---

## 5 · Healthcheck + observability per service (Q5)

### 5.A · Per-service `/healthz` endpoint shape

Each of the three services exposes its own `/healthz` (NOT `/api/health` — that's the Akki-specific one that already exists in `routers/misc.py:82`). Phase 4 standardises:

```python
# Akki:      GET http://localhost:8001/healthz
# SyniSense: GET http://localhost:8002/healthz
# Solva:     GET http://localhost:8003/healthz

# Response shape (each):
{
  "service": "akki",                       # | "synisense" | "solva"
  "version": "<git_sha7>",                 # from IMAGE_TAG env
  "started_at": "2026-02-..T..Z",          # process boot time
  "dependencies": {
    "mongo":  {"ok": true, "rtt_ms": 3},   # via db.command("ping")
    "shield": {"ok": true, "rtt_ms": 8},   # cross-service HTTP probe (Akki only — SyniSense's own /healthz answers shield=self)
    "solva":  {"ok": true, "rtt_ms": 9}    # cross-service HTTP probe (Akki only)
  }
}
```

### 5.B · Liveness vs readiness distinction (Phase 4 hardening)

| Probe | Endpoint | Behaviour | Caller |
|---|---|---|---|
| **Liveness** | `/healthz/live` | Cheap, no I/O. Returns 200 if the process is responding to HTTP. Used by supervisord auto-restart. | supervisord |
| **Readiness** | `/healthz/ready` | Pings Mongo + cross-service dependencies. 503 if any dep is down. Used by the load balancer / ingress to gate traffic. | docker HEALTHCHECK in prod; supervisord-startsecs probe in preview |
| **Full** | `/healthz` (above) | Aggregates both + version + dependency RTTs. Used by the admin Trust Panel + Sentry health check. | manual / admin UI |

This split prevents cascading restarts: a brief Mongo blip during deploy makes `/healthz/ready` return 503 (ingress drains traffic) but `/healthz/live` stays 200 (supervisord doesn't restart the process). Mongo recovers → `/healthz/ready` flips back to 200 → ingress resumes traffic. No process churn.

### 5.C · Log stream separation

Supervisord already writes per-program logs to `/var/log/supervisor/<program>.{err,out}.log`. Phase 4 reuses this pattern:
- `/var/log/supervisor/akki.{err,out}.log`
- `/var/log/supervisor/synisense.{err,out}.log`
- `/var/log/supervisor/solva.{err,out}.log`

Each Python logger gets a `service="<context>"` extra field bound at startup so log lines are machine-grep-friendly when aggregated.

### 5.D · `/metrics` (Prometheus) — out of Phase 4 scope

`docker-compose.prod.yml` doesn't ship Prometheus / Grafana sidecars. Logs flow through the docker `json-file` driver with `max-size: 50m` / `max-file: 5`. Phase 4 holds the line — `/metrics` is a Phase 5/6 follow-up if the deploy topology demands it.

---

## 6 · Versioned API paths (Q6)

### 6.A · Recommendation: **Option B — Dual-mount** (the only behaviour-preserving choice)

The dispatch ask is correct: Option A "big-bang rename" breaks 597 FE call sites (283 migrated + 314 unmigrated) plus every external integration partner that documented `/api/*` URLs.

### 6.B · Dual-mount mechanics

Each of the three FastAPI apps mounts its routers under TWO prefixes:

```python
# In akki_app.py:
app = FastAPI(title="Akki", openapi_url="/openapi.json")
for router in AKKI_ROUTERS:
    app.include_router(router, prefix="/api")       # legacy — preserved
    app.include_router(router, prefix="/v1/akki")   # new — Phase 4 versioned
```

The legacy `/api/*` paths keep working (FE call sites untouched). New code targets `/v1/<context>/*`. Phase 5 deprecation freezes `/api/*` 6-12 months after Phase 4 ships.

### 6.C · Cross-service public-API routing

Three FastAPI apps but ONE public entry point (Akki on 8001). The K8s ingress forwards `/api/*` to 8001 today; Phase 4 extends that pattern:

| Public URL prefix | Internal route |
|---|---|
| `/api/*` | → 8001 (Akki — back-compat preserved) |
| `/v1/akki/*` | → 8001 (Akki — new versioned shape) |
| `/v1/synisense/*` | → 8002 (SyniSense — new versioned shape) |
| `/v1/solva/*` | → 8003 (Solva — new versioned shape) |

For the preview pod where there's no ingress doing path-based routing, Akki on 8001 proxies `/v1/synisense/*` → `localhost:8002` and `/v1/solva/*` → `localhost:8003` (small `httpx` reverse-proxy layer, ~30 LOC).

For prod, the K8s ingress already does path-based forwarding — add 2 more rules.

---

## 7 · Shared state handling (Q7)

| Today's shared state | Future owner | Cross-service access in Phase 4 |
|---|---|---|
| Mongo connection pool (`core.py` singleton, 496 importers) | Each future process opens its own `AsyncIOMotorClient(MONGO_URL)` | No change to call shape — `from core import db` still works. Each process has its own pool. |
| LLM client / `shield_invoke` (`services/synisense/shield/client.py`) | SyniSense | HTTP via `SyniSenseContract.shield_invoke` → POST `/v1/synisense/shield/invoke` |
| Session / auth state (cookies + JWT issued by `routers/auth.py`) | Akki — single source of truth | SyniSense + Solva do NOT consult session. Every cross-service contract method receives `account_id: str` as required kwarg (already in Phase 1 surface). |
| APScheduler — 7 jobs in main + 1 in engine (see §1.D) | Mixed — see §9 detailed map | Each service runs its OWN scheduler with its OWN jobs. Cross-service triggers go via HTTP (already the pattern — server.py:1141 already calls `http://localhost:8001/api/...` for cron). |
| spaCy NER en_core_web_trf (~440 MB load, 1-3s warmup) | SyniSense only | Akki + Solva don't load it. **Saves ~880 MB RAM total + ~6s startup.** |
| Tenant-entity cache `_CACHE` in `tenant_entities.py:44-46` (5-min TTL) | SyniSense | Refresh-invalidation via `SyniSenseContract.refresh_tenant_entities_cache(account_id)` → POST `/v1/synisense/internal/cache/invalidate` |
| `_replica_id_cache` (`scheduler_lock.py:41`) | SyniSense engine | Process-local; replicated naturally per process. |
| `_doc_cache` (ideas_engine citation_resolver) | Akki (ideas_engine is Akki-owned) | Process-local; no cross-service access |
| In-memory rate limiters / token buckets | Each owns its own | No cross-service consultation |
| `process.env`-derived config (MONGO_URL, EMERGENT_LLM_KEY, etc.) | Each loads from its own `.env` at startup | All three services share `/app/backend/.env` initially; Phase 5 splits |

**No genuinely-shared mutable state crosses contexts today.** The 48 cross-context call sites are all data fetches, not state mutations — meaning the migration is uniformly "swap direct call for HTTP call", no transaction-boundary surprises.

---

## 8 · Sub-dispatch sequencing (Q8)

**Critical sequencing consequence of §2.B:** the plan's stated 4-5 dispatches doesn't account for the fact that **Phase 2's "migrate call sites" work was never done**. I recommend prefixing the sequence with a Phase 4.0 sub-dispatch that wires the 48 call sites through the existing Phase 1 adapters BEFORE any topology work. This is mechanical, behaviour-preserving (in-process adapters keep the same call shape), and is the prerequisite for Phase 4.2's HTTP transport swap to mean anything.

### 8.A · Proposed sequence — 5 sub-dispatches, ~12-15 build hours

| Sub-phase | Scope | Build hours | Goldens at risk |
|---|---|---:|---|
| **4.0** | **Phase 2.X recovery: wire the 48 cross-context call sites through `get_synisense()`/`get_solva()`/`get_akki()` adapters.** Behaviour-preserving (adapters are still in-process pass-through). Flip the `cross_context_violations.json` from observe-mode to enforce-mode at violation_count == 0. | 3-4 | Track A 4/6/7 lockdowns + chat fluency (Phase 14) + Solva v2 sessions. Sample paths: the 24× `shield_invoke` call sites in chat.py + the SyniSense direct-db reads in `signal_derivation.py`. |
| **4.1** | Three FastAPI app entrypoints + router redistribution by context (still ONE process initially). Akki keeps `server.py`-as-it-is; new `synisense_app.py` + `solva_app.py` import the ~11+8 routers; uvicorn-multiapp pattern OR a temporary "all three apps mount in `server.py` under prefixes" intermediate state. | 3 | All FastAPI introspection (`/api/openapi.json` shape — Phase 3 codegen depends on this) + the 117 narrowed routes' `response_model` declarations |
| **4.2** | HTTP transport for cross-context calls. Swap `InProcessSyniSenseAdapter` / `InProcessSolvaAdapter` / `InProcessAkkiAdapter` for HTTP-client variants (`HttpSyniSenseAdapter`, etc.) gated by env (`CONTRACT_TRANSPORT=in_process|http`). Default still in-process until 4.3 lands; preview-pod tier flips to http for soak. | 2-3 | Same as 4.0 + chat-send-message latency (4× shield calls). Need the 50ms-budget assertion. |
| **4.3** | Container topology shift — supervisord 3-process. Healthcheck endpoints (`/healthz`, `/healthz/live`, `/healthz/ready`). Per-service log streams. Akki proxies `/v1/synisense/*` + `/v1/solva/*` in the preview pod. Set `CONTRACT_TRANSPORT=http` by default. | 2-3 | All cross-service integration paths — needs cold-start ordering (Mongo first, then SyniSense, then Solva, then Akki) so cross-service probes don't churn. |
| **4.4** | Dual-mount versioned paths `/v1/akki/*` + `/v1/synisense/*` + `/v1/solva/*` alongside `/api/*` (legacy preserved). Re-generate `frontend/openapi.snapshot.json` + `yarn codegen` to surface the new paths in the FE codegen. Smoke test. | 1-2 | Phase 3 drift-catch invariants: `contractCompleteness` + `test_hot_path_routes_declare_response_model` |
| **Total** | | **11-15 hours** | |

### 8.B · Ordering rationale

- **4.0 first** because §2.B is fundamentally architectural — Phase 4's HTTP swap is meaningless without the call sites going through the contracts. Doing it as a Phase 4.0 sub-dispatch (rather than its own Phase 2.X dispatch) keeps the work inside the Phase 4 umbrella and avoids the rail-creating ambiguity of "Phase 2 closed but Phase 2.X is still in flight".
- **4.1 before 4.2** because the HTTP transport in 4.2 needs the three apps to actually exist on three ports. 4.1 creates the apps + redistributes routers; 4.2 then has somewhere to send HTTP requests.
- **4.3 before 4.4** because the supervisord topology in 4.3 is where the three apps actually run as three processes — 4.4's versioned paths need this to be visible to the FE codegen.
- **4.4 last** because dual-mount is additive and behaviour-preserving — safest landing zone for the phase.

### 8.C · Sub-dispatch most exposed to Phase 0 goldens

**Phase 4.0** is highest-risk for goldens. Sample exposure:
- The 24× `shield_invoke` call sites in chat.py — Phase 14 chat fluency lockdowns assert specific Shield-call shapes (`system_msg` plumbing, audit row structure). Migrating each call through `get_synisense().shield_invoke(...)` MUST preserve identical kwarg names and payload structure.
- The 15× direct-db reads in `signal_derivation.py` — Track A Phase 4 forecaster + Phase 6 BC-mirror lockdowns may indirectly observe Mongo state at specific timestamps. Migrating through `AkkiContract.list_*` methods preserves the data but may shift the read-timestamp semantics.

Mitigation: run the Phase 14 + Track A 4/6/7 full lockdown sweep AFTER each batch of 5-10 migrated call sites. The dispatch must allow 3-4 sweep iterations within its budget.

### 8.D · Rollback shape per sub-dispatch

- **4.0:** `git revert` the call-site migration + flip `cross_context_violations.json` back to `phase: 1_observe_mode`. Adapters and Phase 1 contract Protocols stay. Zero infra change.
- **4.1:** Revert the new app modules; restore the flat `app.include_router(...)` in `server.py`. Behaviour-preserving across the revert.
- **4.2:** Toggle `CONTRACT_TRANSPORT=in_process` in env; the adapter factory routes back through `InProcess*Adapter`. No supervisord change needed.
- **4.3:** `supervisorctl` updates the conf back to single-program. Restart backend program — back to single uvicorn on 8001.
- **4.4:** Drop the new `/v1/*` prefix from the dual-mount loop. `/api/*` still serves everything.

Each sub-dispatch is independently revertible.

---

## 9 · Discrepancies with approved plan (Q9)

### 9.1 · **MATERIAL — Phase 1 contracts cover the 48 call sites but ONE method signature mismatch**

The 21 contract methods cover all of the 48 cross-context primitives EXCEPT one:

| Primitive currently called | Contract method | Match? |
|---|---|---|
| `services.synisense.shield.client.invoke` | `SyniSenseContract.shield_invoke` | ✅ Direct match (adapter forwards kwargs) |
| `services.synisense.shield.audit.find_audit` | `SyniSenseContract.get_audit_events` | ⚠️ Naming differs but signature compatible (paginated audit lookup) — adapter maps |
| `services.synisense.shield.audit.find_receipt` | `SyniSenseContract.get_trust_receipt` | ✅ Direct match |
| `services.solva_v2.analyze_narration.narrate_analysis` | `SolvaContract.synthesize_workbook` | ❌ **Signature mismatch.** `narrate_analysis(rows, objective=...)` returns dict; `synthesize_workbook(analysis_id, account_id, objective)` returns `SynthesisResult` dataclass. The contract version is HIGHER-LEVEL than the underlying primitive. |
| 11 `db.X` reads from SyniSense (`accounts`, `contexts`, `cycles`, `chat_messages`, `documents`, `signals`, `objectives`, `briefings`, `cycle_questions`, `memberships`) | `AkkiContract.{get_tenant_profile, list_contexts, list_cycles, get_chat_history, list_documents, list_signals, list_objectives, list_briefings, list_cycle_questions}` | ✅ Direct matches except: `memberships.find` is not directly surfaced (closest is `list_contexts` which is indirect) |

**Two gaps to surface:**
1. **`SolvaContract.narrate_analysis` is not a contract method.** Phase 4.0 either (a) adds it to `SolvaContract` (widens the surface from 5 → 6 methods), OR (b) wraps the call site to use `SolvaContract.synthesize_workbook` (semantic shift; may not be behaviour-preserving). **Recommendation:** add `narrate_analysis` to `SolvaContract` — it's the low-level operation the one call site (`routers/workbook_analysis.py:1089`) needs. The Phase 1 invariant `test_invariant_contract_snapshots.py` re-snapshots the contract surface, so this is a clean widening.
2. **`db.memberships.find` is not surfaced via `AkkiContract`.** Single call site in `services/synisense/engine/signal_derivation.py`. Either (a) add `AkkiContract.list_memberships(account_id, context_id?)`, OR (b) prove the SyniSense call site can use `list_contexts` to derive the membership list. **Recommendation:** add `list_memberships`. Same clean widening as above.

Both gaps require widening `SolvaContract` + `AkkiContract` by ONE method each. Total contract surface becomes 23 methods (was 21). Not a dispatch blocker, but worth surfacing in §11 escalate.

### 9.2 · Connection-pool behaviour — confirmed safe

The current pattern (`AsyncIOMotorClient(MONGO_URL)` once in `core.py`) is compatible with per-service pools: each future process imports `core` independently, each opens its own client. Mongo on Atlas / standalone handles 3× the connection count trivially (single-replica + connection-pool defaults of 100 per client are well below the 32k limit on M0+ clusters).

### 9.3 · APScheduler ownership map (background tasks)

| Job ID | Owner | Today's location | Phase 4 home |
|---|---|---|---|
| `exco360_weekly` | Akki (blog) | `server.py:1153` | Akki |
| `influence_digest_weekly` | Akki (CRM / influence) | `server.py:1174` | Akki |
| `paragraph_anchors_daily` | Akki (documents) | `server.py:1198` | Akki |
| `solva_v2_stale_session_daily` | Solva | `server.py:1220` | **Solva (moves)** |
| `chat_retention_daily` | Akki (chat) | `server.py:1242` | Akki |
| `cohort_expiry_reminder_daily` | Akki (cohort) | `server.py:1265` | Akki |
| `ideas_weekly_sweep` | Akki (ideas_engine) | `server.py:1299` | Akki |
| `synisense_engine_hourly` | SyniSense | `server.py:1370` | **SyniSense (moves)** |

**Multi-context background tasks: NONE.** Each job belongs to exactly one future context. Migration is mechanical — move the `scheduler.add_job(...)` block from `server.py` to the new context's app startup.

**Critical: `synisense_engine_hourly` already uses Mongo-locked leader election** (`services/synisense/engine/scheduler_lock.py`). When SyniSense becomes a separate process, the existing lock pattern means multiple SyniSense replicas can race for the lock without harm — Phase 5 (deployment separation / HA) is already partially prepared.

### 9.4 · 314 unmigrated FE call sites — Phase 4 impact

Phase 4 ships dual-mount (`/api/*` + `/v1/<context>/*`), so the 314 raw-axios call sites keep working unchanged. **No urgency.** They become a candidate for Phase 5 cleanup (deprecate `/api/*` → require `/v1/*`).

### 9.5 · `/api/openapi.json` after Phase 4

Each FastAPI app exposes its own OpenAPI spec at its own port. Phase 4.4 dispatch needs Akki to PROXY-expose `/api/openapi.json` as a UNION of the three specs (or expose three separate specs at `/v1/akki/openapi.json`, `/v1/synisense/openapi.json`, `/v1/solva/openapi.json`). Phase 3 drift-catch (`yarn codegen:check`) needs ONE snapshot file to diff against — Phase 4.4 either picks the union approach OR generates three FE schema files. **Recommendation: union approach** to keep the FE codegen pipeline simple.

---

## 10 · Risk callouts (Q10)

### 10.1 · Chat-send-message latency budget (HIGH RISK)

`routers/chat.py` calls `shield_invoke` with **up to 4 distinct purposes per send-message request** (`chat.tools.classify_turn` + `chat.standard_response` + `chat.thin_input.evidence_list` + `chat.deliverable.pass1_reasoning` + `chat.deliverable.pass2_render` are the observed purpose strings — typically 1-3 fire per request, 4 in worst case for deliverable flows).

Each `shield_invoke` today is in-process — sub-millisecond marshalling. Post-Phase-4, each becomes a `POST /v1/synisense/shield/invoke` over localhost. Per §3.A, that's 5-15ms overhead per call.

**Cumulative budget:** 4 calls × 15ms = **60ms p99** on the chat send-message hot path.

The dispatch escalation trigger threshold is "**~50ms cumulative**." We are 10ms over in the worst case.

**Mitigations to surface in Phase 4.2:**
1. Persistent `httpx.AsyncClient` per process (avoids per-call TCP handshake — single connection-pool, keep-alive) — typical RTT 2-5ms on loopback vs 8-15ms fresh.
2. Batch the 4 shield calls into one `POST /v1/synisense/shield/batch` if the calls are independent (some are; the Phase 14 fluency `system_msg` thread couples 2 of them). Requires contract widening (a new `SyniSenseContract.shield_invoke_batch` method, OR `shield_invoke` accepting `List[ShieldRequest]`).
3. Accept the 10-20ms regression on the chat hot path — it's already a 2-30s end-to-end operation due to the LLM round-trip. 60ms is <0.2% of perceived latency.

**Recommendation:** ship Phase 4.2 with persistent `httpx.AsyncClient` + accept the regression. Re-measure post-deploy. If it bites, add the batch endpoint in Phase 4.x.

### 10.2 · Process-crash isolation (PHASE 4 BENEFIT)

Today, an unhandled exception in `services/synisense/shield/deidentifier.py` propagating to the event loop crashes the whole backend process. Post-Phase-4, it crashes ONLY SyniSense; supervisord auto-restarts it; Akki keeps serving (with shield calls returning `SyniSenseUnavailableError` → Phase 14 fluency lockdowns assert this surfaces gracefully).

**Flows that rely on synchronous-failure behaviour today:** chat send-message currently propagates `shield_invoke` exceptions up the stack so the FE gets a 500 with a typed flag (`chat_system_prompt_injection_failed`, `shield_unavailable`, etc.). Phase 4 preserves this — the HTTP-client adapter catches the network error and re-raises a typed exception identical to the in-process one. Phase 14 fluency tests assert this is unchanged.

### 10.3 · Healthcheck cascade-restart

Naive `/healthz` impl (single endpoint, fails if ANY dep is down) would cause: Mongo blip → Akki `/healthz` returns 503 → ingress restarts Akki → SyniSense `/healthz` also fails (because SyniSense calls Akki for tenant profile) → SyniSense restarts → cascade.

§5.B's liveness vs readiness split mitigates: `/healthz/live` never depends on cross-service or Mongo state. Only `/healthz/ready` does deep probes. Supervisord uses `/healthz/live`; the ingress uses `/healthz/ready`. Cascade impossible.

### 10.4 · Startup ordering (cold start)

Three uvicorn processes booting under supervisord. SyniSense + Solva must reach `READY` BEFORE Akki accepts traffic, otherwise Akki's first cross-service call fails. Supervisord supports `priority=N` for ordering + `startsecs=N` for readiness gating.

**Proposed cold-start order:**
1. `mongodb` (priority 100)
2. `synisense` + `solva` (priority 200, parallel)
3. `akki` (priority 300, depends on 2)

Each program's `startsecs` is set to "first successful HTTP 200 from `/healthz/ready` within 30s" — supervisord doesn't natively support HTTP readiness, but a `startsecs=15` heuristic + a `check_pre_start` script wrapping `curl --max-time 5 http://localhost:<port>/healthz/ready` works in practice. Same pattern used for ClamAV signature-DB pull in the existing prod compose.

---

## 11 · ESCALATE TO USER

**One material discrepancy, two decisions needed.**

### ESCALATE-A — Phase 1 contracts are UNWIRED

Per §2.B: the 21-method contract surface in `backend/contracts/{synisense,solva,akki}.py` + the in-process adapters in `backend/contracts/_adapters/` are present in the tree, the Phase 1 snapshot invariant pins them, but **zero production call sites consume them.** All 48 cross-context call sites still call the underlying primitives directly. The `cross_context_violations.json` is still in observe mode with `violation_count: 48`.

This means Phase 4.2 (HTTP transport swap) has no call sites to swap. The HTTP adapter would be a structural fixture identical in fate to the current InProcess adapter.

**Decision 1 — Phase 4 sequencing:**
- (a) **Insert Phase 4.0 as a "Phase 2.X recovery" sub-dispatch FIRST** — migrate the 48 call sites through `get_synisense() / get_solva() / get_akki()` in-process adapters, flip the `cross_context_violations.json` enforce-mode gate (= 0), THEN proceed with 4.1 → 4.4. Builds 12-15 hours total. **Recommended.**
- (b) Ship 4.1 + 4.3 + 4.4 (topology + healthchecks + dual-mount) WITHOUT 4.0 + 4.2 — gets the three-process container structure live but cross-context calls remain in-process imports. "Process separation" delivers ONLY the supervisord-restart-isolation benefit; the data-layer isolation promised by the plan is deferred. Honest framing required: this is Phase 4-as-skeleton, not Phase 4-as-completed.
- (c) Defer Phase 4 entirely until a dedicated Phase 2.X dispatch closes the cross-context call-site migration. Phase 2.X gets the work that should have happened during Phase 2; Phase 4 then ships clean on the back of a real contract-consumption baseline.

**Decision 2 — Contract widening:**
- (a) **Widen SolvaContract + AkkiContract by ONE method each** (`narrate_analysis` + `list_memberships`) so the Phase 4.0 migration covers all 48 call sites without bespoke workarounds. Re-snapshot via `test_invariant_contract_snapshots.py`. **Recommended.**
- (b) Wrap the two outlier call sites with bespoke pass-throughs that don't go via the contracts. Keeps the surface at 21 methods but creates 2 "second-class" call sites that won't get the HTTP swap.

**Recommended pair:** Decision 1.a + Decision 2.a. (Phase 4.0 backfills Phase 2.X migration + contract surface widens to 23 methods.)

---

## 12 · Recommended Phase 4.1 dispatch scope

**Conditional on §11 Decision 1.a (Phase 4.0 ships first).**

After Phase 4.0 closes (48 cross-context call sites going through contracts; enforce-mode invariant green), Phase 4.1 ships:

| Item | Scope |
|---|---|
| New file `backend/synisense_app.py` | `FastAPI(title="SyniSense")` instance + mount the ~11 SyniSense routers. Lifespan: spaCy warm-up, engine scheduler arm, `/healthz` + `/healthz/live` + `/healthz/ready` endpoints. |
| New file `backend/solva_app.py` | `FastAPI(title="Solva")` instance + mount the ~8 Solva routers. Lifespan: Solva v2 admin flag flip, stale-session scheduler arm, `/healthz` triad. |
| Refactor `backend/server.py` | Becomes `akki_app.py` (rename) OR keep `server.py` name but drop the SyniSense + Solva router includes. Akki keeps the ~117 routers + the remaining 6 cron jobs. |
| `supervisord` config | Add `[program:synisense]` (port 8002) + `[program:solva]` (port 8003); preserve existing `[program:backend]` (port 8001 = Akki). Priorities: 200/200/300. |
| Sprint memo | `/app/memory/sprints/PHASE_4_1_THREE_APPS.md` |

**Phase 4.1 acceptance criteria (proposed — subject to dispatch confirmation):**
- `supervisorctl status` shows 3 running uvicorn processes (akki, synisense, solva).
- `curl http://localhost:8001/healthz/ready` + `:8002/healthz/ready` + `:8003/healthz/ready` all return 200 with the §5.A shape.
- All Phase 14 + Track A 4/6/7 lockdowns green.
- Phase 3 invariants green — including `test_hot_path_routes_declare_response_model` and the `contractCompleteness` codegen completeness test.
- No change to `/api/*` paths (Phase 4.4 adds `/v1/<context>/*` dual-mount).
- Sprint memo + MASTER_STATE Section 6 updated.

**Out of Phase 4.1 scope (deferred to later sub-dispatches):**
- Cross-context HTTP transport (Phase 4.2).
- Dual-mount `/v1/<context>/*` (Phase 4.4).
- FE codegen regen against the new union spec (Phase 4.4).

---

**End of Phase 4 Pre-Read. Output: ESCALATE — §11 surfaces the Phase 1 contracts-unwired finding + the 2-method contract widening requirement. Stay paused.**
