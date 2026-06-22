# Akki / Syni — Development Reference

> **Audience:** Senior engineer joining tomorrow OR a technical investor's CTO doing IP due-diligence.
> **Last updated:** Phase 15 dispatch — 2026-06-05.
> **Sister doc:** `/app/memory/PRODUCT.md` (product surface + journeys).

---

## 1 · Repo Map & Directory Structure

```
/app
├── backend/                     # FastAPI monolith
│   ├── server.py                # Single ASGI entrypoint (~1,458 lines, supervisor-managed)
│   ├── core/
│   │   └── db.py                # Motor (async MongoDB) singleton + collection accessors
│   ├── routers/                 # 131 router files, one per surface or capability
│   ├── services/                # 49 service modules (governance, reasoning, infra)
│   │   ├── synisense/           # SyniSense — data governance substrate
│   │   │   ├── shield/          # The Shield (de-id + re-id + audit + receipts)
│   │   │   ├── engine/          # Signal-derivation hourly cron
│   │   │   └── config.py        # Master secret resolution
│   │   ├── solva_v2/            # Solva v2 reasoning pipeline
│   │   ├── workbook_analyzer/   # XLSX/CSV parser + autopicker + forecaster + anomaly
│   │   ├── work_studio/         # Document lifecycle + confidence scorer
│   │   ├── crypto/              # JWT + token vault + HMAC helpers
│   │   └── …                    # Email, news, ideas-engine, intelligence, clamav, etc.
│   ├── models/                  # Pydantic typed payloads
│   ├── tests/                   # 160+ pytest files (deterministic + integration-marked)
│   └── requirements.txt
├── frontend/                    # React 19 SPA (CRA + craco, yarn-managed)
│   ├── src/
│   │   ├── pages/               # ~140 page-level components
│   │   ├── components/          # Reusable UI atoms + complex components
│   │   ├── hooks/               # Custom React hooks
│   │   ├── contexts/            # AuthContext, etc.
│   │   ├── lib/                 # API client, fetch wrappers
│   │   ├── website/             # Pre-login marketing pages
│   │   └── App.js               # React Router topology (lazy-loaded)
│   ├── package.json
│   └── craco.config.js
├── memory/                      # Single source of truth — agent state ledger
│   ├── MASTER_STATE.md          # The canonical phase/issue/scope ledger
│   ├── PRODUCT.md               # This doc's sister
│   ├── DEVELOPMENT.md           # This doc
│   ├── INVESTOR_QA.md           # Investor Q&A on SyniSense governance
│   ├── sprints/                 # Per-phase memos (Pre-Reads + close-outs)
│   ├── test_credentials.md      # Test credentials for QA agents
│   └── …
├── design_guidelines.md
├── PRD.md                       # Original product requirements doc
├── test_result.md
└── test_reports/                # Generic test reports (banned for SyniSense work)
```

---

## 2 · Tech Stack & Versions

### Backend
| Layer | Technology | Version | Notes |
|---|---|---|---|
| Language | Python | 3.11 | uvloop + ASGI |
| Framework | FastAPI | 0.118.0 | starlette underneath |
| ASGI server | uvicorn | latest | supervisor-managed |
| Async driver | Motor + PyMongo | motor 3.4 / pymongo 4.6 | MongoDB Atlas in prod, local in dev |
| NER | spaCy | 3.8.14 | `en_core_web_trf` preferred, `en_core_web_sm` fallback |
| PII detection | presidio-analyzer | latest | wraps spaCy + 24 regex recognisers |
| LLM SDK | emergentintegrations | proprietary | Multi-provider wrapper; Claude Sonnet 4.5 primary |
| Auth | python-jose | latest | JWT HS256 |
| Crypto | cryptography | latest | HKDF + HMAC + Fernet |
| Email | sendgrid + Postmark fallback | python-http-client | Inbound Parse webhook |
| Antivirus | clamd | clamav daemon | ClamAV escape-hatch enforced in prod |
| Excel | openpyxl + xlrd + pandas + numpy | pandas 2.2 / numpy 1.x | Workbook ingestion |
| Document gen | python-docx + python-pptx + reportlab | latest | DOCX/PPTX/PDF renderers |
| HTTP client | httpx | latest | async |
| Validation | pydantic | v2.x | model serialisation |
| Logging | structlog | latest | structured logging |
| Telemetry | sentry-sdk | latest | live mode in prod |

### Frontend
| Layer | Technology | Version | Notes |
|---|---|---|---|
| Language | JavaScript | ES2022 | TypeScript not used |
| Framework | React | 19.0.0 | CRA + craco |
| Router | react-router-dom | 6.x | lazy-loaded routes |
| Editor | Tiptap | 2.x | Phase 6 inline edit |
| UI primitives | shadcn/ui + lucide-react + sonner | latest | Tailwind underneath |
| State | React Context + hooks | — | No Redux/Zustand |
| HTTP | fetch + custom wrapper | — | `frontend/src/lib/api.js` (or similar) |
| Build | craco | — | hot reload via webpack dev server |

### Infra
| Layer | Technology | Notes |
|---|---|---|
| Container | Docker (k8s-managed) | Emergent platform |
| Process supervision | supervisord | One config for backend + frontend |
| MongoDB | Atlas (prod) / local (dev) | DB_NAME from env |
| File storage | local FS (`UPLOADS_DIR`) / S3 (when `STORAGE_BACKEND=s3`) | env-toggled |
| Background jobs | APScheduler + Mongo-locked cron | Single-replica scheduler safety |

---

## 3 · System Architecture

### 3.1 High-level diagram

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                              Client (React SPA)                              │
│   /app/* protected routes · /trust public · /signin · /first-session         │
└────────────────┬─────────────────────────────────────────────────────────────┘
                 │  HTTPS  (REACT_APP_BACKEND_URL prefixed → /api/*)
                 ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                          FastAPI (server.py)                                 │
│                                                                              │
│   ┌───── Middleware ─────────────────────────────────────────────────────┐   │
│   │  CORS · CSRF (allowlist) · Sentry · Brute-force · Auth/JWT          │   │
│   └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│   ┌───── 131 routers (each: /api/<prefix>) ──────────────────────────────┐   │
│   │  chat · solva_v2 · work_studio_export · documents · tasks · …       │   │
│   └────────────┬─────────────────────────────────────────────────────────┘   │
│                │                                                             │
│                ▼                                                             │
│   ┌───── 49 services ──────────────────────────────────────────────────────┐ │
│   │  synisense.shield · solva_v2.reasoner · workbook_analyzer ·            │ │
│   │  work_studio.confidence_scorer · documents.intelligence_service · …    │ │
│   └────────────┬──────────────────────────────────────────────────────────-┘ │
└────────────────┼─────────────────────────────────────────────────────────────┘
                 │
                 ├──────────┐
                 ▼          ▼
   ┌────────────────────┐  ┌──────────────────────────┐
   │  MongoDB (Motor)   │  │  SyniSense Shield        │
   │                    │  │  (services/synisense/    │
   │  130+ collections  │  │   shield/)               │
   └────────────────────┘  │                          │
                           │  ┌─ de-id ──────────┐    │
                           │  │  regex · tenant_ │    │
                           │  │  dict · spaCy    │    │
                           │  └────────┬─────────┘    │
                           │           ▼              │
                           │  ┌──────────────────┐    │
                           │  │  LLM router      │    │
                           │  │  (single point)  │    │
                           │  └────────┬─────────┘    │
                           │           ▼              │
                           │     Anthropic Claude     │
                           │     Sonnet 4.5           │
                           │       (no other         │
                           │        provider)         │
                           └──────────┬───────────────┘
                                      │
                       ┌──────────────┴──────────────┐
                       ▼                             ▼
        ┌──────────────────────────┐  ┌──────────────────────────┐
        │  re-identifier           │  │  audit_log +             │
        │  (asymmetric)            │  │  trust_receipt (HMAC)    │
        └──────────────────────────┘  └──────────────────────────┘
                       │
                       ▼
                user-visible reply
                + Trust chip + audit_id
```

### 3.2 Request lifecycle — a chat round-trip

```
1. POST /api/chats/{chat_id}/messages
   - Auth middleware extracts JWT → user_id, tenant_id (account_id)
   - CSRF middleware verifies header
   - chat.py route invoked

2. chat.py → builds prompt context
   - Loads prior messages (chats collection)
   - Builds system_msg with the Phase-14 fluency preamble
     (services/synisense/system_prompts/chat_system_prompt.py)

3. chat.py → calls shield_invoke(
       purpose="chat",
       content=<user prompt>,
       system_msg=<fluency preamble>,
       tenant_id, consumer_id, user_id,
       model_preference="balanced",
   )

4. shield.client.invoke()
   4a. purpose_validator.validate_purpose() — gates internal-only purposes
   4b. deidentifier.deidentify():
        - regex pass (24 patterns, EMAIL/CC/SSN/IBAN/PHONE/IP/URL/...)
        - tenant dictionary pass (per-tenant entity catalogue)
        - spaCy NER pass (PERSON/ORG/GPE/PRODUCT/NORP/FAC/EVENT/LAW)
        - overlap resolution: regex > tenant > spaCy
        - emit token_map {token: original}
        - emit redacted_text
   4c. llm_router.invoke_with_metering(
            de_id.redacted_text,
            model_preference,
            system_msg=<fluency preamble>,
        )
        - direct stream when CHAT_STREAMING_MODE=direct_stream
        - else buffered via emergentintegrations
        - returns (llm_text, provider, model, usage_dict)
   4d. reidentifier.reidentify(llm_text, token_map):
        - per-class strategy (rehydrate vs last4 vs redacted)
        - emit response_text
   4e. trust_receipt.build_trust_receipt(...):
        - HMAC-SHA256(canonical_json(receipt_minus_signature))
        - tenant-scoped via HKDF
   4f. audit_log.write_audit() → synisense_audit_log row
   4g. Returns {response, trust_receipt, audit_id}

5. chat.py → writes response to chats.messages
   - Appends synisense_audit_ids[]
   - Streams response to client (SSE)

6. Client renders response with Trust chip
```

### 3.3 Multi-tenancy model

Tenants are accounts, scoped by `account_id`. Every authenticated request carries the user's `account_id` in the JWT claim, and every collection that holds tenant data has `account_id` as a top-level field.

**Cross-tenant guarantees:**
- The Shield's tenant entity catalogue is `tenant_id`-scoped (`services/synisense/shield/tenant_entities.py:_CACHE` keyed by tenant).
- Trust receipts are signed with per-tenant HKDF-derived keys (`services/synisense/shield/trust_receipt.derive_tenant_key`).
- Every Mongo query in routers filters by `account_id` (manually enforced; not a framework-level interceptor).
- Active context resolution gates which `context_id` a tenant can access (`routers/active_context.py`).

**Multi-context model:** within a tenant, a user may switch between multiple contexts (e.g. "Q3 board" vs "Operating committee"). The active context is stored in the user profile and surfaces via `GET /api/active-context`.

---

## 4 · Backend

### 4.1 Router Inventory

> **Convention:** every router lives in `/app/backend/routers/<name>.py`, defines an APIRouter with `prefix=/api/<surface>`, and gets included via `app.include_router()` in `server.py`. 131 router files total.

| File | Mount | Responsibility | Notable routes |
|---|---|---|---|
| `account_deletion.py` | `/api/account` | Self-service account deletion | `DELETE /api/account` |
| `active_context.py` | `/api/active-context` | Multi-context switcher | `GET /POST /api/active-context` |
| `admin_audit_invariant.py` | `/api/admin/audit-invariants` | Shield invariant violations panel | `GET /api/admin/audit-invariants` |
| `admin_auth_events.py` | `/api/admin/auth-events` | Auth events superadmin view | `GET /api/admin/auth-events` |
| `admin_cohort.py` | `/api/admin/cohort` | Cohort approvals | various |
| `admin_cohort_applications.py` | `/api/admin/cohort-applications` | Cohort application list | `GET /api/admin/cohort-applications` |
| `admin_email_provider.py` | `/api/admin/email-provider` | Provider switch (SendGrid / Postmark) | various |
| `admin_extractions.py` | `/api/admin/extractions` | Extraction activity | `GET /api/admin/extractions` |
| `admin_health.py` | `/api/admin/health` | Composite health | `GET /api/admin/health` |
| `admin_inbox.py` | `/api/admin/inbox` | Admin inbox + unread count | various |
| `admin_journal.py` | `/api/admin/journal` | Admin journal entries | various |
| `admin_llm_spend.py` | `/api/admin/llm-spend` | LLM cost dashboard | `GET /api/admin/llm-spend` |
| `admin_qa_hooks.py` | `/api/admin/qa-hooks` | QA hook surface | various |
| `admin_sandbox_kpi.py` | `/api/admin/sandbox-kpi` | Sandbox KPI panel | various |
| `admin_shield_backfill.py` | `/api/admin/shield-backfill` | Shield backfill jobs | various |
| `admin_signal_kpi.py` | `/api/admin/signal-kpi` | Signal-engine KPI | various |
| `admin_tenants.py` | `/api/admin/tenants` | Multi-tenant org list | `GET /api/admin/tenants` |
| `admin_users.py` | `/api/admin/users` | User CRUD | full CRUD |
| `agenda.py` | `/api/agenda` | Agenda surfaces | various |
| `async_jobs.py` | `/api/jobs` | Async job orchestration | various |
| `audit.py` | `/api/audit` | Audit log read surface | `GET /api/audit` |
| `auth.py` | `/api/auth` | Email/password auth | `POST /login /signup /logout /me` |
| `auth_magic.py` | `/api/auth/magic` | Magic-link auth | `POST /api/auth/magic/request` |
| `auth_oauth.py` | `/api/auth/oauth` | OAuth probes (Google/Microsoft) | `GET /api/auth/oauth/*/start` |
| `auth_password_change.py` | `/api/auth/password` | Change password | `POST /api/auth/password/change` |
| `billing.py` | `/api/billing` | Stripe-gated billing routes | gated by `BILLING_ENABLED` |
| `blog.py` | `/api/blog` | Marketing blog | various |
| `briefings.py` | `/api/briefings` | Pre-meeting briefings | various |
| `chat.py` | `/api/chats` | **Chat sync + streaming** | `POST /api/chats/{id}/messages` + stream variant |
| `chat_audit_panel.py` | `/api/chats/audit-panel` | Per-message Shield audit panel | `GET /api/chats/{id}/messages/{mid}/audit` |
| `cohort_applications.py` | `/api/cohort-applications` | Cohort apply | `POST /api/cohort-applications` |
| `cohort_email_events.py` | `/api/cohort-email-events` | SendGrid event webhook | `POST /api/cohort-email-events` |
| `cohort_expiry_reminder.py` | `/api/cohort/expiry-reminder` | Cohort reminder cron trigger | various |
| `cohort_magic_link.py` | `/api/cohort/magic-link` | Cohort magic-link verification | various |
| `cohort_waitlist.py` | `/api/cohort/waitlist` | Cohort waitlist | various |
| `comments.py` | `/api/comments` | Generic comment CRUD | full CRUD |
| `committees.py` | `/api/committees` | Committees CRUD | full CRUD |
| `company_home.py` | `/api/company-home` | Tenant home surface | various |
| `compilations.py` | `/api/compilations` | Work Studio compilations registry | various |
| `contexts.py` | `/api/contexts` | Context CRUD | full CRUD |
| `csrf.py` | `/api/csrf` | CSRF token mint | `GET /api/csrf` |
| `cycle.py` | `/api/cycle` | Cycle Manager v1 | various |
| `cycle_assignments.py` | `/api/cycle/assignments` | Cycle contributor assignments | various |
| `cycle_manager.py` | `/api/cycle-manager` | Cycle Manager v2 | various |
| `cycles.py` | `/api/cycles` | Multi-cycle master | full CRUD |
| `daily_review.py` | `/api/daily-review` | Daily review surface | various |
| `decks.py` | `/api/decks` | Slide-deck composer | various |
| `depth.py` | `/api/depth` | Depth quota / upgrade modal | various |
| `document_engagement.py` | `/api/document-engagement` | Engagement tracking | various |
| `documents.py` | `/api/documents` | **Documents library + drawer** | full CRUD, multi-file upload |
| `documents_async_mirror.py` | `/api/documents/async-mirror` | Async mirror writer | various |
| `early_access.py` | `/api/early-access` | Early-access opt-in | various |
| `enterprise.py` | `/api/enterprise` | Enterprise lead capture | various |
| `events.py` | `/api/events` | Calendar events | various |
| `exco_teams.py` | `/api/exco-teams` | Exco team CRUD | various |
| `feedback.py` | `/api/feedback` | Feedback widget | `POST /api/feedback` |
| `first_session.py` | `/api/first-session` | First-session onboarding state | various |
| `governance.py` | `/api/governance` | Governance surface | various |
| `health_composite.py` | `/api/health` | Composite probe | `GET /api/health` |
| `healthz_clamav.py` | `/api/healthz/clamav` | ClamAV liveness | `GET /api/healthz/clamav` |
| `healthz_shield.py` | `/api/healthz/shield` | Shield warmup state | `GET /api/healthz/shield` |
| `help.py` | `/api/help` | Help / FAQ surface | various |
| `home.py` | `/api/home` | AppHome data | various |
| `ideas.py` | `/api/ideas` | Pulse Ideas | various |
| `inbound_email.py` | `/api/inbound` | **SendGrid Inbound Parse webhook** | `POST /api/inbound/sendgrid` |
| `inbound_queue.py` | `/api/inbound-queue` | Inbound queue surface | various |
| `inbox_message_preview.py` | `/api/inbox/preview` | Message preview | various |
| `influence_map.py` | `/api/influence-map` | Influence map | various |
| `learn.py` | `/api/learn` | Learn / wiki surface | various |
| `lens.py` | `/api/lens` | Lens Room | various |
| `llm_quota.py` | `/api/llm-quota` | Per-user LLM quota | various |
| `mfa.py` | `/api/mfa` | TOTP MFA | enrol/verify |
| `misc.py` | `/api/misc` | Catch-all utilities | various |
| `monitor.py` | `/api/monitor` | Monitor surface | various |
| `monitor_status_assessment.py` | `/api/monitor/status-assessment` | Status assessment | various |
| `monitor_v2.py` | `/api/monitor/v2` | Monitor v2 | various |
| `ned/` | `/api/ned/*` | NED-specific endpoints | sub-package |
| `ned_cycle.py` | `/api/ned-cycle` | NED Cycle Manager | various |
| `news.py` | `/api/news` | News aggregator surface | various |
| `oauth_google.py` | `/api/oauth/google` | Google OAuth handshake | `GET /api/oauth/google/start /callback` |
| `observability.py` | `/api/observability` | Trust Center mirror | public + internal |
| `onboarding_briefs.py` | `/api/onboarding/briefs` | Briefs modal | various |
| `onboarding_status.py` | `/api/onboarding/status` | Onboarding state | various |
| `password_reset.py` | `/api/password-reset` | Password reset | request + redeem |
| `pipeline.py` | `/api/pipeline` | Pipeline state | various |
| `portfolio.py` | `/api/portfolio` | Portfolio surface | various |
| `portfolio_data.py` | `/api/portfolio/data` | Portfolio data | various |
| `prepare.py` | `/api/prepare` | Prepare-mode helpers | various |
| `product_features.py` | `/api/product-features` | Product feature flags | various |
| `profile.py` | `/api/profile` | User profile | full CRUD |
| `pulse.py` | `/api/pulse` | Pulse Ideas + signals | various |
| `questions.py` | `/api/questions` | **Q4Y CRUD + status transitions** | full CRUD, link/unlink, reopen |
| `quick_actions.py` | `/api/quick-actions` | Quick actions | various |
| `sandbox.py` | `/api/sandbox` | Generative sandbox | various |
| `sandbox_generation.py` | `/api/sandbox/generation` | Sandbox generation | various |
| `search.py` | `/api/search` | Universal search | `GET /api/search` |
| `shares.py` | `/api/shares` | Document shares | various |
| `signal_actions.py` | `/api/signal-actions` | Signal action CRUD | various |
| `signals_ask.py` | `/api/signals/ask` | Signals query surface | various |
| `simulate.py` | `/api/simulate` | Simulation surface | various |
| `solva_briefing.py` | `/api/solva/briefing` | Solva briefing artefacts | various |
| `solva_phase_d.py` | `/api/solva/phase-d` | Solva dialectic | various |
| `solva_phase_e_polish.py` | `/api/solva/phase-e/polish` | Solva polish phase | various |
| `solva_telemetry_admin.py` | `/api/solva/telemetry/admin` | Solva telemetry | various |
| `solva_v2.py` | `/api/solva/v2` | **Solva v2 reasoning entrypoint** | session CRUD, run phases |
| `solva_v2_artefact.py` | `/api/solva/v2/artefact` | Solva v2 artefact export | various |
| `strategic_goal_assessment.py` | `/api/strategic-goals/assessment` | Strategic goal assessment | various |
| `strategic_goal_evolution.py` | `/api/strategic-goals/evolution` | Goal evolution | various |
| `strategic_goals.py` | `/api/strategic-goals` | Strategic goals CRUD | full CRUD |
| `streaming_v9.py` | `/api/work-studio/streaming-v9` | Work Studio compile streaming | SSE |
| `studio.py` | `/api/studio` | Studio composer | various |
| `studio_blocks.py` | `/api/studio/blocks` | Studio block CRUD | various |
| `synisense.py` | `/api/synisense` | Synisense aggregator surface | various |
| `synisense_engine.py` | `/api/synisense/engine` | Engine surface | various |
| `synisense_metrics.py` | `/api/synisense/metrics` | Metrics endpoint | `GET /api/synisense/metrics` |
| `synisense_observability.py` | `/api/synisense/observability` | Observability dashboard data | various |
| `synisense_shield.py` | `/api/synisense/shield` | Shield admin operations | various |
| `tasks.py` | `/api/tasks` | **Tasks CRUD + state machine** | `POST /api/tasks/{id}/commission /close /counts` |
| `tasks_initiatives.py` | `/api/tasks/initiatives` | Initiatives sub-surface | various |
| `team_catalogue.py` | `/api/team-catalogue` | Team catalogue | various |
| `trial_status.py` | `/api/me/trial-status` | Trial status | `GET /api/me/trial-status` |
| `trust_center.py` | `/api/trust-center` | Public Trust Center | various |
| `walkin.py` | `/api/walkin` | Walk-in feature | various |
| `website.py` | `/api/website` | Marketing site backend | various |
| `work_studio_export.py` | `/api/work-studio/exports` | **Work Studio compile/enhance** | `POST /start /complete` |
| `work_studio_from_source.py` | `/api/work-studio/from-source` | Compile-from-source | various |
| `work_studio_overlay.py` | `/api/work-studio/overlays` | **Document Review Drawer endpoints** | `POST /commit` etc. |
| `work_studio_phase_c.py` | `/api/work-studio/phase-c` | Phase C compile | various |
| `work_studio_phase_c2.py` | `/api/work-studio/phase-c2` | Phase C2 enhance | various |
| `work_studio_render.py` | `/api/work-studio/render` | Render downloadable artefact | DOCX/PDF/PPTX |
| `workbook_analysis.py` | `/api/workbook-analyze` | **Multi-workbook synthesize** | `POST /api/workbook-analyze/synthesize-v2` |

---

### 4.2 Service Layer

#### 4.2.1 SyniSense Shield — DEEP DIVE

The Shield is the centre of gravity of the codebase. Every LLM call from every product surface routes through it. No code outside `services/synisense/shield/` may import an LLM SDK directly; this is enforced by code review and by the fact that the Shield is the only module that calls `services/synisense/shield/llm_router.py`.

**Module structure:**

```
services/synisense/shield/
├── __init__.py
├── adapter.py            # External-facing shape adapters
├── audit_log.py          # Audit row writer + token-counting + cost math
├── boot_guard.py         # Boot-time invariants
├── client.py             # invoke() — the single entrypoint
├── config.py             # Master secret resolution
├── deidentifier.py       # 3-layer de-id pipeline (687 lines)
├── encryption.py         # At-rest token-map encryption helpers
├── engine/               # Signal-derivation cron (separate from de-id)
├── exceptions.py         # ServiceUnavailable, Rejected, RateLimit, etc.
├── llm_router.py         # Provider selection + metering
├── llm_streaming.py      # Direct-stream Anthropic adapter
├── observability_models.py
├── presidio_analyzer.py  # presidio-analyzer wrapper
├── purpose_validator.py  # Purpose allowlist + internal-only gating
├── reidentifier.py       # Asymmetric re-id (333 lines)
├── streaming.py          # Stream coordination
├── system_prompts/       # Caller-provided system prompts (e.g. chat fluency)
├── tenant_entities.py    # Per-tenant dictionary catalogue (247 lines)
└── trust_receipt.py      # HMAC + HKDF + canonical JSON (134 lines)
```

**Public API:**

```python
# services/synisense/shield/client.py:37
async def invoke(
    *,
    purpose: str,
    content: str,
    tenant_id: str,
    consumer_id: str,
    user_id: str,
    model_preference: Literal["analytical","generative","balanced"] = "balanced",
    internal_caller: bool = False,
    system_msg: Optional[str] = None,
) -> Dict[str, Any]:
    """Run the full Shield pipeline. Returns
    {response, trust_receipt, audit_id}. Raises one of four
    SynisenseError subclasses on failure."""
```

**Why this shape:** the function is a single canonical entrypoint. `purpose` drives purpose-gated exclusions (e.g. `documents.events_extract` skips the DATE_ISO regex). `internal_caller=True` exempts the caller from purpose-allowlist enforcement (callers like `confidence_scorer` and `intelligence_service` use this). `system_msg` (Phase 14) threads a caller-provided system prompt through to the provider — when None, llm_router uses a built-in generic prompt, preserving pre-Phase-14 behaviour at 90+ existing call sites.

**Pipeline (snippet from `client.invoke()`, lines 65-110):**

```python
# /app/backend/services/synisense/shield/client.py:65
started = time.perf_counter()
de_id = await deidentifier.deidentify(content, tenant_id=tenant_id, purpose=purpose)
llm_text, provider, model, usage = await llm_router.invoke_with_metering(
    de_id.redacted_text, model_preference=model_preference,
    system_msg=system_msg,
)
response_text = reidentifier.reidentify(llm_text, de_id.token_map)
latency_ms = int((time.perf_counter() - started) * 1000)

audit_id = "aud-" + uuid.uuid4().hex
receipt_id = "rcp-" + uuid.uuid4().hex
timestamp = datetime.now(timezone.utc).isoformat()
request_hash = trust_receipt.hash_payload(content)
response_hash = trust_receipt.hash_payload(response_text)
# ... metering math (exact vs estimated tokens) ...
await audit_log.write_audit(audit_id, tenant_id, …)
```

The shape is sequential by design: de-id MUST complete before the LLM call (fail-closed), and the audit row MUST be written even on partial success (the function uses a try/finally pattern to guarantee the audit-write call site is reached on every code path).

**Fail-closed contract:** every step that touches PII can raise `ServiceUnavailable`. The caller (any route) is expected to translate this to HTTP 503. Under no failure mode does raw `content` reach the LLM.

---

#### 4.2.2 Solva v2 — DEEP DIVE

Solva v2 is the structured reasoning engine. Where chat is conversational and ad-hoc, Solva is a directed pipeline.

**Module structure:**

```
services/solva_v2/
├── __init__.py
├── analyze_narration.py        # Phase 3 Solva v2 → AnalyzeJournal hook
├── citation_resolver.py        # Resolves paragraph anchors back to source docs
├── opinion_filter.py           # Removes weasel words / hedging
├── payload_builder.py          # Builds the Phase E export shape
├── probability_weighting.py    # Per-claim confidence scoring
├── refuse_to_decide.py         # Explicit "insufficient input" path
├── reasoner.py                 # Phase A→E orchestrator
└── …
```

**Phase progression:**

1. **Phase A** — input intake. Workbook + objective. Refused on missing input via `refuse_to_decide.should_refuse()`.
2. **Phase B** — extraction. Parses the workbook, surfaces structural artefacts.
3. **Phase C** — claim generation. Calls Shield with prompt asking for grounded claims; each claim gets per-claim probability via `probability_weighting`.
4. **Phase D** — dialectic. Engine generates counter-arguments, scores remaining claims.
5. **Phase E** — synthesis + polished artefact. `payload_builder` composes the export-ready JSON.

**Confidence aggregation (`payload_builder._input_confidence_pct`):** weighted average of per-claim probabilities → aggregate-level percentage. Surfaced on the Solva session view and on Analyze Drawer when Solva narration is the source.

**Refuse-to-Decide pattern:** Solva does not "always answer". When input is insufficient (no parseable date column, no objective text, fewer than 3 data points), the engine returns a typed Refusal with the reason rather than hallucinating. This is the only "graceful degradation" pattern in the product; everywhere else is fail-closed.

---

#### 4.2.3 Workbook Analyzer — DEEP DIVE

**Module structure:**

```
services/workbook_analyzer/
├── __init__.py
├── parser.py             # XLSX/CSV → typed sheet matrix + column inference
├── forecaster.py         # Linear-regression projection + 80% CI band
├── anomaly_detector.py   # Z-score outlier detection
├── refuse_to_decide.py   # Insufficient-input handling
├── schema.py             # Pydantic typed payloads
└── …
```

**Autopicker (column selection across multiple workbooks):**

```python
# /app/backend/services/workbook_analyzer/forecaster.py:189
def autopick_forecast_columns(*, sheets: List[Any]) -> Optional[Dict[str, Any]]:
    """Bug #30 fix (2026-06-04) — column-pair auto-picker.
    Returns {sheet, date_column, value_column, picker_reason}
    for the strongest signal pair OR None if no viable pair exists."""
    best: Optional[Dict[str, Any]] = None
    best_score: Tuple[int, float] = (0, 0.0)
    for sheet in sheets:
        cols = getattr(sheet, "columns", [])
        date_cols = [c for c in cols if c.kind == "date"]
        numeric_cols = [c for c in cols if c.kind == "numeric"]
        if not date_cols or not numeric_cols:
            continue
        total_rows = max(getattr(sheet, "n_rows", 0) or 0, 1)
        for date_col in date_cols:
            for num_col in numeric_cols:
                non_null = num_col.non_null_count or 0
                density = non_null / total_rows
                # density gate — rejects sparse columns
                if non_null < _AUTOPICK_MIN_NON_NULL_COUNT or density < _AUTOPICK_MIN_NON_NULL_RATIO:
                    continue
                # spread = max(values) - min(values); ties broken by
                # higher non-null count
                spread = float(num_col.maxv) - float(num_col.minv) \
                         if num_col.maxv is not None else 0.0
                score = (non_null, spread)
                if score > best_score:
                    best_score = score
                    best = {"sheet": sheet.name, "date_column": date_col.name,
                            "value_column": num_col.name,
                            "picker_reason": f"non_null_count={non_null}, value_spread={spread:.2f}"}
    return best
```

**Why this shape:** the autopicker has to make a decision across an arbitrary number of (sheet × column) candidates. The (non_null, spread) tuple is a lexicographic score: prefer the column with the most data points first, then break ties by the column with the larger value range. The density gate (added Track A Phase 4) prevents a 4-non-null-row column from beating a 200-non-null-row column just because the small one happens to have larger spread.

**Forecaster (linear regression + CI band):**

```python
# /app/backend/services/workbook_analyzer/forecaster.py:118 (extract)
xs = np.array([p[0] for p in pairs], dtype=float)
ys = np.array([p[1] for p in pairs], dtype=float)
slope, intercept = np.polyfit(xs, ys, 1)
fitted = slope * xs + intercept
residuals = ys - fitted
ss_res = float(np.sum(residuals ** 2))
ss_tot = float(np.sum((ys - ys.mean()) ** 2))
r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
residual_std = float(np.std(residuals, ddof=1)) if len(residuals) > 1 else 0.0
band_half = 1.282 * residual_std  # 80% CI under residual-normality
# project horizon_periods ahead with linear extrapolation
step_days = float(np.median(np.diff(xs))) if len(xs) > 1 else 30.0
```

**Why pure numpy:** SciPy / statsmodels add ~40MB of cold-start weight, all for a single linear regression. Pure numpy gives us the slope, intercept, R², and residual stddev in 8 lines. The 80% CI band uses the residual stddev × 1.282 (the z-score at the 90th percentile under a Gaussian residual assumption) — a deliberate choice over scipy's `t.ppf` because n is often small and we want a band that doesn't blow up to ±10× at n=3.

**Low-R² safety-net flag:** when `r2 < 0.30`, the synthesize endpoint surfaces a `low_signal` flag on the response so the UI can warn the user that the projection is weak. Threshold pinned at `_FORECAST_LOW_R2_THRESHOLD = 0.30` in `forecaster.py:29`.

---

#### 4.2.4 Work Studio — DEEP DIVE

**Module structure:**

```
services/work_studio/
├── __init__.py
├── confidence_scorer.py        # Phase 7 4-dim rubric (296 lines)
├── citation_resolver.py        # Citations manifest builder
├── enhance_runner.py           # Revise-with-AI orchestrator (Phase 6)
├── render_dispatcher.py        # report/brief/minutes/deck × docx/pdf/pptx
├── source_blob_resolver.py     # Resolves source documents for scoring
└── …
```

**Lifecycle status machine (`work_studio_exports.status`):**

```
created → compiling → ready → committed
              ↓
           failed (fail-closed; preserves error_kind)

ready ←→ enhancing (Phase 6 Revise)
ready → committed (idempotent via cache_key on Phase 7)
```

**Confidence scorer (Phase 7, the 4-dimension rubric):**

```python
# /app/backend/services/work_studio/confidence_scorer.py:54
_WEIGHTS = {
    "source_coverage":           0.40,
    "internal_consistency":      0.25,
    "gap_clarity":               0.20,
    "recommendation_grounding":  0.15,
}
_DIMENSIONS = list(_WEIGHTS.keys())
```

```python
# /app/backend/services/work_studio/confidence_scorer.py:200
async def score_confidence(
    *,
    document_title: str,
    document_kind: str,
    structured_content: Dict[str, Any],
    source_blobs: List[Dict[str, Any]],
    tenant_id: str,
    consumer_id: str = "work_studio_confidence",
) -> Optional[Dict[str, Any]]:
    """Returns dict with confidence_pct, rationale, scored_at,
    breakdown, cache_key, audit_id, OR None on skip/failure."""
    if not source_blobs:
        return None    # rubric refuses to score without sources
    prompt = _build_score_prompt(...)
    try:
        shield_result = await shield_invoke(
            purpose="work_studio.document.confidence_score",
            content=prompt, tenant_id=tenant_id,
            consumer_id=consumer_id, user_id=tenant_id,
            model_preference="analytical",
            internal_caller=True,
        )
    except Exception:
        logger.exception("confidence_score_shield_error")
        return None
    raw = shield_result.get("response") or ""
    parsed = json.loads(_strip_json_fence(raw))
    dims = {k: _clamp(parsed[k]) for k in _DIMENSIONS}
    pct = _aggregate(dims)
    return {
        "confidence_pct": pct,
        "rationale":      (parsed.get("rationale") or "").strip()[:240],
        "scored_at":      _now_iso(),
        "breakdown":      dims,
        "cache_key":      structured_content_hash(structured_content),
        "audit_id":       shield_result.get("audit_id"),
    }
```

**Why this shape:** the scorer returns `None` (not raises) on every failure mode so callers can degrade gracefully (the Phase 7 spec calls this "no scorer signal"). The cache_key is a SHA-256 of canonicalised structured_content — on commit-time recompute, if the structured_content hasn't changed since the last score, we skip the entire scorer call. This is Phase 7 Tightening 4 — a real $0.10/commit credit saver at scale.

**Why `internal_caller=True`:** the confidence scoring purpose is internal-only — it's not exposed as a user-callable surface. `purpose_validator.validate_purpose()` rejects it from external callers by default; setting `internal_caller=True` exempts the call site.

---

#### 4.2.5 Other services

| Service | Responsibility |
|---|---|
| `services/crypto/` | JWT issuance, token vault (Fernet), HMAC helpers |
| `services/email/` | SendGrid + Postmark wrappers with provider fallback |
| `services/clamav_service.py` | ClamAV daemon client + boot-time mode guard |
| `services/news_aggregator.py` | 15-source business news aggregator (hourly cron) |
| `services/ideas_engine/` | Pulse Ideas weekly synthesis |
| `services/documents/intelligence_service.py` | Document intelligence + signal extraction + Q4Y promotion |
| `services/synisense/engine/` | Signal derivation hourly cron (Mongo-locked, single-replica) |
| `services/sentry_setup.py` | Sentry init (live vs dev mode) |
| `services/auth/` | Brute-force protection, login attempts, password reset |
| `services/storage/` | Local FS / S3 abstraction |
| `services/exceptions/` | Typed exception hierarchy |
| `services/voice_lint.py` | Tone enforcement (no glazing, no hedging) |

---

### 4.3 Data Model — Mongo collections

> **Convention:** every collection name is lower_snake_case. Every tenant-scoped collection has `account_id` as a top-level field. Timestamps are stored as ISO-8601 strings in UTC.

#### 4.3.1 `accounts`
**Purpose:** tenant root. Every user belongs to one account.
**Schema:**
| Field | Type | Required | Notes |
|---|---|---|---|
| `_id` | ObjectId | yes | Mongo PK |
| `id` | str (UUID) | yes | app-side PK |
| `name` | str | yes | display name |
| `email` | str | yes | unique, indexed |
| `password_hash` | str | yes | bcrypt |
| `account_id` | str | yes | tenant scope |
| `role` | str | yes | `user` / `superadmin` |
| `mfa_enrolled` | bool | no | TOTP enrolled flag |
| `created_at` | str | yes | ISO-8601 UTC |

**Indexes:** `email` (unique), `account_id`.
**Lifecycle:** written on signup; updated on profile change; never archived (soft-delete via `deleted_at`).

#### 4.3.2 `contexts`
**Purpose:** workspace scope within a tenant. A user can have multiple contexts.
**Schema:** id, name, account_id, created_at.
**Indexes:** `account_id`.
**Lifecycle:** written on context creation; never deleted.

#### 4.3.3 `chats`
**Purpose:** chat session container.
**Schema:**
| Field | Type | Notes |
|---|---|---|
| `id` | str | session ID |
| `account_id` | str | tenant |
| `messages` | list[dict] | role/content/created_at/synisense_audit_ids[] |
| `created_at` | str | ISO |

**Indexes:** `account_id`, `id`.
**Lifecycle:** retention cron deletes >90-day idle chats (daily 03:30 UTC).

#### 4.3.4 `synisense_audit_log`
**Purpose:** every Shield call writes one row.
**Schema:** audit_id, tenant_id, consumer_id, user_id, purpose, timestamp, de_id_summary, dilution_score, exposure_reduction_score, llm_provider, llm_model, request_hash, response_hash, outcome, latency_ms, tokens_in, tokens_out, metering_method, actual_cost_usd.
**Indexes:** `tenant_id` + `timestamp`, `audit_id` (unique).
**Lifecycle:** append-only; never deleted (regulatory retention).

#### 4.3.5 `synisense_trust_receipts`
**Purpose:** HMAC-signed receipts (one per Shield call).
**Schema:** receipt_id, audit_id, version, tenant_id, consumer_id, purpose, timestamp, llm_provider, llm_model, de_id_summary, dilution_score, exposure_reduction_score, request_hash, response_hash, signature.
**Indexes:** `audit_id` (unique).
**Lifecycle:** append-only; never deleted.

#### 4.3.6 `work_studio_exports`
**Purpose:** Work Studio artefact rows. The lifecycle's source of truth.
**Schema:**
| Field | Type | Notes |
|---|---|---|
| `id` | str | export ID |
| `account_id` | str | tenant |
| `context_id` | str | scope |
| `kind` | str | report / brief / minutes / deck / blank |
| `format` | str | docx / pdf / pptx |
| `instructions` | str | user prompt |
| `source_document_ids` | list[str] | citations basis |
| `structured_content` | dict | LLM-emitted structured JSON |
| `citations_manifest` | list[dict] | resolved citations |
| `intelligence_report` | dict | confidence_pct, rationale, breakdown, scored_at |
| `notes` | str | reviewer notes |
| `notes_history` | list[dict] | append-only |
| `runs` | list[dict] | append-only version snapshots (Phase 4) |
| `status` | str | created / compiling / ready / committed / failed |
| `created_at` | str | ISO |
| `committed_at` | str | ISO (nullable) |

**Indexes:** `account_id` + `context_id`, `status`.
**Lifecycle:** runs[] grows; status flips deterministically; soft-delete via `archived_at`.

#### 4.3.7 `documents`
**Purpose:** user-uploaded files + Akki-generated artefacts mirror.
**Schema:** id, account_id, context_id, name, kind (pdf/docx/xlsx/csv/pptx), bytes_ref, akki_generated (bool), generated_from_export_id (when mirror), notes, notes_history, intelligence_report (mirror of Work Studio scorer), shared_with_email (BC), recipient_emails (list, max 10), confidence_pct (mirror), created_at.
**Indexes:** `account_id` + `context_id`, `created_at`.
**Lifecycle:** mirror writer (`documents_async_mirror.py`) keeps these in sync with `work_studio_exports`.

#### 4.3.8 `analyses`
**Purpose:** Analyze Journal rows (multi-workbook synthesis).
**Schema:** id, account_id, context_id, source_blob_refs, narration (Solva v2 output), notes, notes_history, runs[] (append-only versions), created_at.
**Indexes:** `account_id` + `context_id`.
**Lifecycle:** new run appends to `runs[]`; latest is read.

#### 4.3.9 `tasks`
**Purpose:** Task Manager rows.
**Schema:** id, account_id, context_id, title, description, state (draft/active/closed), commissioned_at, closed_at, audit (history), created_at.
**Indexes:** `account_id` + `state`.
**Lifecycle:** state machine with explicit transitions via `/api/tasks/{id}/commission /close`.

#### 4.3.10 `questions`
**Purpose:** Q4Y question records.
**Schema:** id, account_id, context_id, text, status (open/answered), source (document_id), response_links (list[dict]), history (audit), created_at.
**Indexes:** `account_id` + `status`.
**Lifecycle:** open → answered → can be reopened (preserves history).

#### 4.3.11 `cycles` + `cycle_assignments`
**Purpose:** Cycle Manager v2.
**Lifecycle:** cycle has assignments to contributors; assignments track response state.

#### 4.3.12 Other collections (130+ total in code)
- `compilations` — Work Studio compile job rows
- `inbound_queue` + `inbound_queue_raw` — TM3 SendGrid inbound parse rows
- `magic_links` + `magic_link_redemptions` — auth magic-link state
- `password_reset_tokens` — password reset state
- `login_attempts` — brute-force tracking
- `audit_invariant_violations` — Shield invariant violations
- `document_engagement` + `document_shares` — share/engagement tracking
- `events` + `event_invitations` — calendar
- `signal_actions` + `signal_events` + `signals` — signal feed
- `ideas_audit_log` + `ideas_digests` — Pulse Ideas
- `news_articles` + `news_sources` — news aggregator
- `synisense_engine_runs` — engine scheduler audit
- `user_calendar_credentials` — calendar credentials
- `feedback` + `early_access` — capture surfaces
- `cohort_applications` + `cohort_email_events` + `cohort_invites` — cohort
- `briefings`, `decks`, `studio_blocks`, `lens_sessions`, `daily_review_rows`, `influence_maps`, `monitor_status`, …

---

### 4.4 Background tasks / schedulers

Scheduled via APScheduler at boot (server.py:~610). All schedulers Mongo-locked to single-replica:

| Job | Cadence | Function | Lock collection |
|---|---|---|---|
| Exco360 brief | Tue 10:00 UTC | (briefings) | per-job |
| Influence Digest | Mon 08:00 UTC | (influence_map) | per-job |
| Paragraph Anchors | daily 03:00 UTC | (documents) | per-job |
| Chat Retention | daily 03:30 UTC | (chats) | per-job |
| Solva v2 Stale | daily 04:00 UTC | (solva_v2) | per-job |
| SyniSense Engine hourly | top-of-hour UTC | (synisense/engine) | `scheduler_locks` |
| News sweep | every 15 min | (news_aggregator) | per-job |

---

## 5 · Frontend

### 5.1 Routing & page tree

React Router 6 with lazy-loaded routes. Eager imports kept to first-paint surfaces (landing, signin, signup). All app routes lazy-loaded.

**Public marketing routes (eager top-level):**
- `/` → `WebsiteHome`
- `/signin` → `SignIn`
- `/signup` → `SignUp`

**Public marketing routes (lazy):**
- `/about`, `/features`, `/security`, `/plans`, `/enterprise`, `/blog`, `/blog/:slug`, `/cohort`, `/waitlist`, `/pricing`, `/trust`, `/privacy`, `/terms`, `/methodology`, `/exco360`, `/product/*`, `/for/*`.

**Protected app routes (lazy, gated by ProtectedRoute):**
- `/app` → `AppHome`
- `/app/chat`, `/app/chat/:id` → `Chat`
- `/app/solva`, `/app/solva/sessions`, `/app/solva/sessions/:id` → Solva pages
- `/app/work-studio`, `/app/work-studio/activity`, `/app/work-studio/analyze`, `/app/work-studio/documents/:id` → Work Studio pages
- `/app/analyze` → `AnalyzeJournal`
- `/app/documents`, `/app/documents/:id` → `DocumentsPage`
- `/app/questions` → `Questions`
- `/app/task-manager`, `/app/task-manager/activity` → Task Manager
- `/app/cycle`, `/app/cycle/drafts`, `/app/ned-cycle` → Cycle Managers
- `/app/inbound-queue` → `InboundQueue`
- `/app/pulse-ideas`, `/app/pulse` → Pulse
- `/app/events` → `Events`
- `/app/briefings`, `/app/decks`, `/app/studio`, `/app/lens`, `/app/daily-review`, `/app/influence-map`, `/app/news`, `/app/search` → various
- `/app/synisense-observability` → admin view
- `/app/admin/*` → SuperadminRoute (15+ surfaces)
- `/account/security`, `/account/profile`, `/account/recovery-codes`, `/tenant-settings` → account
- `/first-session` → `FirstSession`
- `/set-password` → `SetPasswordGuard`

### 5.2 Component inventory (key)

- `frontend/src/components/SetPasswordGuard.jsx` — first-login gate
- `frontend/src/components/SuperadminRoute.jsx` — admin gate
- `frontend/src/components/ProtectedRoute.jsx` — auth gate
- `frontend/src/components/depth/UpgradeModal.jsx` — quota / upgrade modal
- `frontend/src/components/feedback/FeedbackWidget.jsx` — feedback widget
- `frontend/src/components/cohort/Day16Banner.jsx`, `SpecialAskModal.jsx` — cohort UI
- `frontend/src/components/onboarding/OnboardingBriefsModal.jsx` — first-login briefs
- `frontend/src/components/work_studio/DocumentOverlay.jsx` — Document Review Drawer (Phase 6 host)
- `frontend/src/components/work_studio/DraftingDrawer.jsx` — Drafting drawer
- `frontend/src/components/work_studio/CreateArtefactModal.jsx`, `LoadingChecklistModal.jsx` — compile UX
- `frontend/src/components/analyze/AnalyzeDrawer.jsx` — Analyze drawer
- `frontend/src/components/documents/DocumentDrawer.jsx` — document multi-tab drawer
- `frontend/src/components/ui/*` — shadcn/ui primitives
- `frontend/src/components/chat/ChatAuditPanel.jsx` — Trust chip panel
- `frontend/src/components/OAuthButtons.jsx` — Google / Microsoft buttons
- `frontend/src/components/Toaster.jsx` (via sonner)

### 5.3 State management

No Redux / Zustand. React Context for cross-cutting state:
- `frontend/src/contexts/AuthContext.jsx` — auth state + user object + tenant ID
- Local component state (`useState` + `useReducer`) for most UI
- Server state via fetch + manual revalidation hooks
- `frontend/src/hooks/useTrialStatus.js` — trial-status hook

### 5.4 API client layer

Single fetch wrapper that:
1. Prefixes `REACT_APP_BACKEND_URL` from env
2. Attaches CSRF token from `/api/csrf` mint
3. Includes credentials (cookies)
4. Handles 401 → redirect to signin
5. Surfaces errors via sonner toasts

---

## 6 · LLM Integration

### 6.1 Shield invocation contract

EVERY LLM call MUST use:
```python
from services.synisense.shield.client import invoke as shield_invoke
result = await shield_invoke(
    purpose="<surface>.<action>",   # e.g. "chat", "work_studio.document.confidence_score"
    content="<user-bearing or assembled prompt>",
    tenant_id=<account_id>,
    consumer_id="<surface or sub-feature>",
    user_id=<user id or tenant id for internal>,
    model_preference="balanced",   # or "analytical" / "generative"
    internal_caller=False,          # True only for internal purposes
    system_msg=None,                # caller-provided system prompt
)
# result = {"response": str, "trust_receipt": dict, "audit_id": str}
```

### 6.2 Token shape & rehydration

**Token shape:** `[[ENT_<TYPE>_<NNN>]]` where TYPE matches `[A-Z0-9_]+` and NNN is 3+ digits. Anchored by regex in `reidentifier.py:48`:

```python
# /app/backend/services/synisense/shield/reidentifier.py:48
_TOKEN_RE = re.compile(r"\[\[ENT_([A-Z0-9_]+)_(\d{3,})\]\]")
```

**Why this shape:** the double-bracket prefix is rare in natural English (effectively zero false-positive matches in legitimate LLM output). The all-caps type label allows fast classification by the re-identifier without an extra lookup. The 3+ digit counter wraps cleanly under a per-request type sequence.

**Rehydration strategy:**

```python
# /app/backend/services/synisense/shield/reidentifier.py:118
def reidentify(text: str, token_map: Dict[str, str]) -> str:
    """Substitute every token in `text` with the appropriate user-
    visible form."""
    if not text or not token_map:
        return text
    def _sub(m: re.Match) -> str:
        tok = m.group(0)
        entity_type = m.group(1)
        original = token_map.get(tok)
        if original is None:
            return tok    # unknown token — defence-in-depth, kept as-is
        visible = _visible_placeholder(entity_type, original)
        if visible is not None:
            return visible    # hard PII — placeholder
        return original       # contextual class — rehydrate
    return _TOKEN_RE.sub(_sub, text)
```

**Per-class visibility strategy (`_VISIBLE_STRATEGY` at `reidentifier.py:69`):**

```python
_VISIBLE_STRATEGY: Dict[str, Tuple[str, str]] = {
    # Hard PII — keep redacted in user-visible reply
    "CREDIT_CARD":  ("last4",    "PAYMENT_CARD"),
    "ACCOUNT_NUM":  ("last4",    "ACCOUNT_NUM"),
    "SSN":          ("last4",    "SSN"),
    "IBAN":         ("last4",    "IBAN"),
    "PHONE_E164":   ("last4",    "PHONE"),
    "UK_NI_NUMBER": ("redacted", "UK_NI"),
    "API_KEY":      ("redacted", "API_KEY"),
    "EMAIL":        ("redacted", "EMAIL"),
    "IP":           ("redacted", "IP"),
    # Contextual classes (PERSON, ORG, GPE, etc.) → default rehydrate
}
```

**Streaming rehydration** — for SSE streams from Anthropic, tokens may split across deltas. `StreamingReidentifier` (reidentifier.py:178) buffers until a closing `]]` arrives or `_MAX_PENDING_TOKEN_LEN=64` chars accumulate without closure. No partial token ever reaches the user.

### 6.3 System-prompt patterns

| Surface | Purpose | System prompt source |
|---|---|---|
| Chat | `chat` | `services/synisense/system_prompts/chat_system_prompt.py` (Phase 14 fluency preamble) |
| Solva v2 | `solva.v2.*` | `services/solva_v2/system_prompts.py` |
| Work Studio compile | `work_studio.export.*` | `routers/work_studio_export.py` inline |
| Work Studio enhance | `work_studio.enhance` | `routers/work_studio_export.py` inline |
| Work Studio confidence | `work_studio.document.confidence_score` | `services/work_studio/confidence_scorer._build_score_prompt` |
| Documents intelligence | `documents.intelligence_extract` | `services/documents/intelligence_service.py` |
| Documents events | `documents.events_extract` | inline; DATE_ISO regex skipped via `_PURPOSE_REGEX_SKIPS` |

**Phase 14 fluency preamble (chat)** lives in `services/synisense/system_prompts/chat_system_prompt.py`. It instructs the model to:
- Use natural language for any token rehydration that survives (it shouldn't, but defence-in-depth).
- NOT mention "redacted tokens" or "did you mean" suggestions to the user.
- Treat `[[ENT_…]]` shapes as opaque references and assume the upstream rehydrator will resolve them.

### 6.4 Confidence scoring rubric

See §4.2.4 above for the full snippet. The prompt template lives at `confidence_scorer._build_score_prompt` (lines 107-170). Output is strict-JSON:

```json
{
  "source_coverage":           <int 0-100>,
  "internal_consistency":      <int 0-100>,
  "gap_clarity":               <int 0-100>,
  "recommendation_grounding":  <int 0-100>,
  "rationale": "<1-2 sentence prose, max 240 chars>"
}
```

Aggregation: weighted average per `_WEIGHTS`, clamped to [0, 100], rounded.

---

## 7 · Integrations

### 7.1 Anthropic Claude

- **Provider:** Anthropic Claude Sonnet 4.5
- **Access:** via Emergent LLM Key (`EMERGENT_LLM_KEY` env) routed through `emergentintegrations` library
- **Routing:** `services/synisense/shield/llm_router.py` selects provider + model based on `model_preference` ("analytical" / "generative" / "balanced")
- **Direct stream path:** when `CHAT_STREAMING_MODE=direct_stream` AND Anthropic API key is direct (not a routed key), `llm_streaming.py` bypasses emergentintegrations for lower latency
- **Metering:** `audit_log.estimate_tokens()` falls back to char/4 estimator when provider doesn't return usage payload; "exact" vs "estimated" provenance flag persisted on every audit row
- **Cost math:** `audit_log.compute_cost_usd()` uses provider-published pricing constants

### 7.2 SendGrid (outbound + inbound parse)

- **Outbound:** `services/email/sendgrid_email_service.py` — magic links, cohort emails, share emails, follow-up drafts
- **Inbound Parse webhook:** `/api/inbound/sendgrid` (router: `inbound_email.py`)
- **Auth:** Basic auth (`SENDGRID_INBOUND_AUTH_USERNAME` + `SENDGRID_INBOUND_AUTH_PASSWORD`) + optional HMAC signature
- **Domain:** `SENDGRID_INBOUND_DOMAIN` — DNS MX record routes to SendGrid
- **TM3 status:** ✅ Verified end-to-end (2026-06-04)
- **Sandbox flag:** `SENDGRID_SANDBOX_ONLY=true` in dev — emails accepted but not sent

### 7.3 Google OAuth (status: pending creds)

- **Code:** `routers/oauth_google.py` + `routers/auth_oauth.py`
- **Env vars needed:** `GOOGLE_OAUTH_CLIENT_ID` + `GOOGLE_OAUTH_CLIENT_SECRET` + `GOOGLE_OAUTH_REDIRECT_URI`
- **Status:** Code path live; user-blocked on GCP credentials provisioning

### 7.4 spaCy

- **Library:** spaCy 3.8.14 + presidio-analyzer wrapper
- **Models (in order of preference):**
  - `en_core_web_trf` — transformer (F1 ≈ 0.91) — requires `spacy-transformers` + `torch` (~2GB)
  - `en_core_web_sm` — small (F1 ≈ 0.86) — fallback
- **Loaded via:** `services/synisense/shield/deidentifier._ensure_spacy()` (lazy + cached)
- **Warmup:** boot-time via `deidentifier.warmup_or_warn()` (called from FastAPI startup event)
- **POS-tag check:** not yet shipped (Phase 14 followup)

### 7.5 Tiptap

- **Library:** Tiptap 2.x
- **Used in:** `DocumentOverlay.jsx` (Phase 6 inline edit)
- **Extensions:** StarterKit + Underline + Heading + Bold + Italic
- **Autosave:** 30s heartbeat + save-on-close belt + last-write-wins

### 7.6 Other live integrations

- **Sentry:** error reporting + traces, live mode in prod, `SENTRY_DSN` + `SENTRY_ENVIRONMENT`
- **ClamAV:** AV scan via clamd daemon (`CLAMAV_HOST` + `CLAMAV_PORT`)
- **S3 (optional):** `STORAGE_BACKEND=s3` toggle, AWS-compatible

---

## 8 · Key Algorithms — DEEP DIVE

### 8.1 Three-layer de-identification pipeline

The Shield's de-identification is three layers run in priority order: **regex > tenant_dict > spaCy**.

```python
# /app/backend/services/synisense/shield/deidentifier.py:521
async def deidentify(content: str, *, tenant_id: str, purpose: Optional[str] = None) -> DeIdResult:
    """Three-layer de-identification.
    Fail-closed: any unrecoverable failure raises ServiceUnavailable.
    Phase I.6 (2026-05-27) — purpose kwarg enables purpose-gated
    pattern exclusions."""
    if not content:
        return DeIdResult(redacted_text="", token_map={}, ...)
    original = content
    _PURPOSE_REGEX_SKIPS: Dict[str, set] = {
        "documents.events_extract": {"DATE_ISO"},
    }
    skip_labels = _PURPOSE_REGEX_SKIPS.get(purpose or "", set())

    # Collect every hit, then resolve overlaps preferring higher priority.
    hits: List[Dict[str, Any]] = []

    # Layer 1 — regex.
    for label, pat in _REGEX_PATTERNS:
        if label in skip_labels:
            continue
        validator = _REGEX_VALIDATORS.get(label)
        for m in pat.finditer(original):
            if validator is not None and not validator(m.group(0)):
                continue   # e.g. CREDIT_CARD shape matched but Luhn failed
            hits.append({"start": m.start(), "end": m.end(),
                         "type": label, "match": m.group(0), "priority": 1})

    # Layer 2 — tenant entity dictionary.
    try:
        from services.synisense.shield.tenant_entities import lookup_in_text
        tenant_hits = await lookup_in_text(original, tenant_id=tenant_id)
        for h in tenant_hits:
            hits.append({**h, "priority": 2})
    except Exception as exc:
        raise ServiceUnavailable(f"tenant_entities lookup failed: …") from exc

    # Layer 3 — local spaCy NER (run on a thread; spaCy is sync).
    nlp = _ensure_spacy()
    if nlp is None:
        raise ServiceUnavailable("spaCy model unavailable: ...")
    # … spaCy hits collected, overlap-resolved, token map built …
```

**Why three layers in this order:**
- **Regex** is deterministic and validator-gated. CREDIT_CARD + Luhn, EMAIL + RFC pattern, etc. Fastest path; highest confidence; runs first so it wins overlap resolution.
- **Tenant dictionary** catches per-tenant proper nouns (org names, employee names) that the LLM has no context for. Phase 14 added a 4-character length floor so tokens like "EY" don't false-positive across the catalogue.
- **spaCy** catches everything else — PERSON, ORG, GPE, PRODUCT, NORP, FAC, EVENT, LAW. Lowest confidence; runs last; protected by the Phase 14 ORG protector (43-term filter list to drop common false positives like disease names, weekdays, months).

**Purpose-gated exclusions** (`_PURPOSE_REGEX_SKIPS`): the only currently-allowed exclusion is `documents.events_extract` skipping `DATE_ISO`. Rationale: the events-extract LLM prompt asks the LLM to return ISO dates in its structured output; pre-tokenising them collapses extraction recall.

---

### 8.2 Asymmetric re-identification

See §6.2 above for the full snippet. The key insight: contextual classes (PERSON, ORG, …) rehydrate to the original; hard-PII classes (CREDIT_CARD, SSN, …) stay redacted in the user-visible reply.

**Why this matters for security:** if Claude ever leaks a token it received (it shouldn't, but defence-in-depth), the user-visible reply still shows `[PAYMENT_CARD_••••4242]`, not the original PAN. The audit trail records what Claude actually saw (the placeholder) and what the user saw (the placeholder), so a leak surfaces in the security log without surfacing on the user's screen.

---

### 8.3 HMAC trust-receipt signing

See §4.2.1 snippets from `trust_receipt.py`.

**HKDF per-tenant key:**

```python
# /app/backend/services/synisense/shield/trust_receipt.py:44
def derive_tenant_key(tenant_id: str) -> bytes:
    """HKDF-SHA256 → 32-byte key, salted, info=tenant_id."""
    if tenant_id in _TENANT_KEY_CACHE:
        return _TENANT_KEY_CACHE[tenant_id]
    kdf = HKDF(
        algorithm=hashes.SHA256(),
        length=_HKDF_LENGTH,           # 32
        salt=_HKDF_SALT,               # b"synisense/v1"
        info=tenant_id.encode("utf-8"),
    )
    key = kdf.derive(MASTER_SECRET)
    _TENANT_KEY_CACHE[tenant_id] = key
    return key
```

**Sign + verify:**

```python
# /app/backend/services/synisense/shield/trust_receipt.py:72
def sign(payload: Dict[str, Any], *, tenant_id: str) -> str:
    """HMAC-SHA256 hex over canonical JSON of payload minus signature."""
    body = {k: v for k, v in payload.items() if k != "signature"}
    key = derive_tenant_key(tenant_id)
    mac = hmac.new(key, _canonical_json(body), hashlib.sha256)
    return mac.hexdigest()

def verify(payload: Dict[str, Any], *, tenant_id: str) -> bool:
    """Constant-time verify via hmac.compare_digest."""
    sig = payload.get("signature")
    if not isinstance(sig, str) or not sig:
        return False
    recomputed = sign(payload, tenant_id=tenant_id)
    return hmac.compare_digest(sig, recomputed)
```

**Why HKDF + per-tenant key:** if the master secret leaks, every tenant's audit chain becomes forgeable. HKDF-derived per-tenant keys mean an attacker would need the master secret + the exact tenant ID + the canonical-JSON encoding to forge a single receipt. Different tenants get different keys; the same tenant always derives the same key (cache-safe).

**Why canonical JSON:** any byte tweak to the payload breaks the signature. Sorted keys + compact separators (`(",", ":")`) + UTF-8 ensures cross-language reproducibility (a downstream verifier in Go, Rust, or Node can recompute the same bytes).

---

### 8.4 Multi-workbook synthesis prompt assembly

The Analyze surface synthesises up to 5 workbooks into one Solva v2 narration. The prompt assembly happens in two layers:

1. **Per-workbook parsing** (`services/workbook_analyzer/parser.py`): each XLSX/CSV becomes a typed sheet matrix with column type inference (date / numeric / text). Sheets are renamed `<filename-stem>::<sheet>` so the citation resolver can disambiguate across the union.

2. **Multi-workbook autopicker** (`services/workbook_analyzer/forecaster.autopick_forecast_columns`): scores every (sheet × date_col × numeric_col) triple globally. Picks the highest-scoring triple. Density gate rejects sparse columns. (Full snippet in §4.2.3.)

3. **Forecast + anomaly + narration**: the selected triple feeds the forecaster (linear regression + 80% CI). The first sheet of each parsed workbook feeds the anomaly detector. Both outputs feed Solva v2 narration (`services/solva_v2/analyze_narration.py`) which produces the Bottom Line + per-tab drill-down (What changed / What's likely next / What's odd).

4. **SOURCE FILES roster**: the prompt includes a list of every source filename, its stem, and the autopicker reason, so the LLM understands the multi-file basis and the citation resolver can map back to source documents.

---

### 8.5 Confidence Scorer (4-dimensional rubric)

Full snippet in §4.2.4. The four dimensions are:

1. **source_coverage (40%)** — % of substantive claims with explicit citation back to source.
2. **internal_consistency (25%)** — does the doc contradict itself across sections?
3. **gap_clarity (20%)** — does the doc acknowledge what it doesn't know?
4. **recommendation_grounding (15%)** — are recommendations tied to evidence? (Defaults to 100 when no recs to avoid penalising rec-free docs.)

**Cache key (Tightening 4 — credit-saver):**

```python
def structured_content_hash(structured_content: Optional[Dict[str, Any]]) -> str:
    """SHA-256 over canonical-sorted JSON of structured_content."""
    canonical = json.dumps(structured_content, sort_keys=True,
                           separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(canonical).hexdigest()
```

On commit-time recompute, if the cache_key matches the previously-stored `intelligence_report.confidence_pct_cache_key`, the scorer call is skipped entirely. A real-world saving of ~$0.10/commit at scale.

---

### 8.6 Work Studio lifecycle state machine

```
created ──compile──▶ compiling
                          │  (LLM streams structured_content)
                          ▼
                       ready ──enhance──▶ enhancing
                          │                   │
                          │◀──────────────────┘ (back to ready on completion)
                          │
                          ▼
                      committed ──┐
                                  │ (idempotent — cache_key gate skips re-score)
                                  ▼
                          (downloadable / readable)

      Any state → failed (fail-closed; preserves error_kind)
```

State stored on `work_studio_exports.status`. Transitions are idempotent (`commit_document` checks current state before transitioning) and audit-logged. Failed states preserve `error_kind` so the UI can surface a recoverable message.

---

### 8.7 Forecaster density gate & low-R² flag

**Density gate** (autopicker): a column with <30% non-null density OR <6 absolute non-nulls is excluded entirely. Rationale: a 4-non-null-row column should never beat a 200-non-null-row column just because the small column happens to have large spread.

**Low-R² flag**: when the fitted regression's R² < 0.30, the synthesize endpoint sets `low_signal=true` on the response. The UI shows a warning so users don't over-rely on weak projections. Threshold pinned at `_FORECAST_LOW_R2_THRESHOLD = 0.30` in `forecaster.py:29`.

---

### 8.8 Append-only versioning pattern

Several surfaces use append-only versioning: each new "version" appends an entry to a `runs[]` array on the row rather than overwriting. Used by:
- `analyses.runs[]` (Analyze Journal, Phase 4)
- `work_studio_exports.runs[]` (Work Studio, Phase 4)
- `documents.notes_history[]` (Document notes, Track B Phase B5)

**Pattern:**

```python
new_run = {
    "run_id": "run-" + uuid.uuid4().hex[:12],
    "created_at": datetime.now(timezone.utc).isoformat(),
    "input_hash": <content_hash>,
    "narration": <output>,
    "citations": <manifest>,
    # ...other version-specific fields
}
await db.<collection>.update_one(
    {"id": <row_id>},
    {"$push": {"runs": new_run}},
)
```

**Idempotency**: every appender computes the `input_hash` (SHA-256 of canonical input) and skips the append when the last run's hash matches. This way refresh-with-no-change doesn't bloat the history.

**Why append-only**: regulatory traceability + reviewer audit. A user can scrub back to any historical state. Soft-delete via `archived_at` instead of physical row deletion.

---

## 9 · Build, Test, Deploy

### 9.1 Local dev

```bash
# Backend
cd /app/backend
pip install -r requirements.txt
sudo supervisorctl restart backend
# Backend runs on 0.0.0.0:8001 (supervisor-managed)

# Frontend
cd /app/frontend
yarn install
sudo supervisorctl restart frontend
# Frontend runs on 0.0.0.0:3000 (supervisor-managed; hot-reload enabled)

# All API URLs come from env:
#  - frontend: REACT_APP_BACKEND_URL
#  - backend: MONGO_URL, DB_NAME
# Never hardcode.
```

### 9.2 Test discipline

**Test categories:**
- **Default sweep (160+ tests):** deterministic. No real LLM. No network. Run on every commit.
- **`@pytest.mark.integration`:** real-LLM tests against the Anthropic API. Used to validate fluency, refusal behaviour, prompt compliance. Skipped by default; enable with `pytest -m integration`.

**Run sweep:**
```bash
cd /app/backend
pytest                       # default — deterministic only
pytest -m integration        # real-LLM tests (uses live API key)
pytest --co                  # collection (counts) without execution
```

**Test file layout:** `/app/backend/tests/test_<phase or surface>.py`. Per-phase lockdowns pin contracts (e.g. `test_chat_fluency_no_shield_leak.py` ensures no `[[ENT_…]]` survives in user-visible chat output).

**`@pytest.mark.integration` files (7):**
- `test_track_a_phase6_inline_edit_and_bc_removal.py`
- `test_track_a_phase5_lifecycle.py`
- `test_chat_fluency_no_shield_leak.py` (Phase 14)
- (4 others; grep `@pytest.mark.integration` to enumerate)

**Banned:** generic testing subagents. SyniSense work uses custom pytest + raw Playwright scripts in `/tmp` only.

### 9.3 Environment Variables

> Grouped by area. Criticality: **P0** = required for prod boot; **P1** = degrades safely; **P2** = optional/feature-flag.

#### Database
| Var | Purpose | Criticality | Default |
|---|---|---|---|
| `MONGO_URL` | Mongo connection string | P0 | none |
| `DB_NAME` | Mongo DB name | P0 | none |

#### LLM
| Var | Purpose | Criticality | Default |
|---|---|---|---|
| `EMERGENT_LLM_KEY` | Emergent universal LLM key | P0 | none |
| `ANTHROPIC_API_KEY` | Direct Anthropic key (optional, for direct-stream) | P1 | none |
| `OPENAI_API_KEY` | OpenAI key (unused in prod) | P2 | none |
| `GEMINI_API_KEY` | Gemini key (unused in prod) | P2 | none |
| `CHAT_STREAMING_MODE` | `direct_stream` vs `buffered` | P1 | `buffered` |
| `LLM_MODEL_DEEP` / `LLM_MODEL_STANDARD` / `LLM_MODEL_FAST` | Tier model names | P1 | default constants |

#### SyniSense
| Var | Purpose | Criticality | Default |
|---|---|---|---|
| `SYNISENSE_MASTER_SECRET` | HMAC master secret (HKDF root) | P0 in prod | transient (boot warning) |
| `SYNISENSE_MASTER_KEY` | Older alias for master_secret | P2 | none |
| `SYNISENSE_SHIELD_MAP_TTL_HOURS` | Tenant entity cache TTL | P1 | 24 |
| `SYNISENSE_SPACY_MODEL` | spaCy model name override | P1 | auto |
| `SYNISENSE_POOL_SIZE` | Worker pool size | P2 | default |
| `SYNISENSE_USE_POOL` | Toggle worker pool | P2 | true |
| `SYNISENSE_LLM_MODE` | `live` / `mock` | P1 | live |
| `SYNISENSE_LLM_FALLBACK_*` | Fallback timing/concurrency | P2 | default |
| `SYNISENSE_ALLOW_INSECURE` | Test-only escape hatch | P2 | false |
| `AKKI_SKIP_SHIELD_WARMUP` | Test bypass for warmup_or_warn | P2 | false |

#### SendGrid
| Var | Purpose | Criticality | Default |
|---|---|---|---|
| `SENDGRID_API_KEY` | API key for outbound | P0 in prod | none |
| `SENDGRID_FROM` / `SENDGRID_FROM_EMAIL` | From address | P0 in prod | none |
| `SENDGRID_INBOUND_DOMAIN` | Inbound Parse domain | P0 in prod | none |
| `SENDGRID_INBOUND_AUTH_USERNAME` / `SENDGRID_INBOUND_AUTH_PASSWORD` | Webhook basic auth | P0 in prod | none |
| `SENDGRID_WEBHOOK_PUBLIC_KEY` | HMAC verification | P1 | none |
| `SENDGRID_SANDBOX_ONLY` | Dev sandbox flag | P2 | false |
| `COHORT_EMAILS_ENABLED` | Gate cohort email sending | P0 in prod | false |
| `EMAIL_PROVIDER` | `sendgrid` / `postmark` / `resend` | P1 | sendgrid |
| `POSTMARK_SERVER_TOKEN` | Postmark fallback | P2 | none |
| `POSTMARK_WEBHOOK_SECRET` | Postmark webhook auth | P2 (or P0 if env-var path enforced) | none |
| `POSTMARK_INBOUND_DOMAIN` | Postmark inbound domain | P2 | none |
| `RESEND_API_KEY` / `RESEND_FROM_*` | Resend fallback | P2 | none |

#### OAuth
| Var | Purpose | Criticality | Default |
|---|---|---|---|
| `GOOGLE_OAUTH_CLIENT_ID` | Google OAuth | P0 (when enabling Google login) | none |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth | P0 | none |
| `GOOGLE_OAUTH_REDIRECT_URI` | Google OAuth | P0 | none |
| `MICROSOFT_OAUTH_CLIENT_ID` | Microsoft probe (mock) | P2 | none |
| `OAUTH_TOKEN_VAULT_KEY` | Fernet key for token vault | P0 in prod | per-process random |

#### Frontend / CORS
| Var | Purpose | Criticality | Default |
|---|---|---|---|
| `REACT_APP_BACKEND_URL` | FE → BE URL | P0 | none |
| `CORS_ORIGINS` | Allowlist or `*` | P1 | `*` |
| `FRONTEND_ORIGIN` / `FRONTEND_URL` | Various BE → FE links | P1 | none |
| `PUBLIC_APP_URL` / `PUBLIC_BASE_URL` | Public URL constants | P1 | none |
| `APP_PUBLIC_URL` / `APP_NAME` | App identity | P2 | none |

#### Auth + security
| Var | Purpose | Criticality | Default |
|---|---|---|---|
| `ADMIN_EMAIL` / `ADMIN_PASSWORD` | Initial superadmin seed | P0 on first boot | none |
| `AKKI_ADMIN_EMAIL` | Alternate admin alias | P2 | none |
| `AKKI_AUTH_OBSERVE_RATE` | Auth rate limit | P2 | default |
| `COOKIE_SECURE` | Cookie secure flag | P1 | `true` in prod |
| `CSRF_DISABLED` | Test-only | P2 | false |
| `CSRF_TEST_BYPASS_HEADER` | Test-only header | P2 | none |
| `FIRST_LOGIN_PASSWORD_GATE_DISABLED` | Test-only | P2 | false |
| `MFA_ADMIN_GRACE_EMAILS` | MFA admin grace | P2 | none |
| `RATE_LIMIT_DISABLED` | Test-only | P2 | false |
| `SECURITY_HEADERS_DISABLED` | Test-only | P2 | false |
| `SESSION_TIMEOUT_DISABLED` | Test-only | P2 | false |

#### File storage / uploads
| Var | Purpose | Criticality | Default |
|---|---|---|---|
| `STORAGE_BACKEND` | `local` / `s3` | P1 | local |
| `UPLOADS_DIR` | Local FS upload dir | P1 | `/app/uploads` |
| `S3_*` | S3 config | P2 | none |
| `ALLOW_UNSAFE_UPLOADS` | ClamAV escape hatch | P2 | false |
| `CLAMAV_HOST` / `CLAMAV_PORT` / `CLAMAV_TIMEOUT_SECONDS` / `CLAMAV_MAX_FILE_SIZE_MB` | ClamAV config | P1 | sensible defaults |
| `AKKI_ENV` | Environment label | P0 in prod | `(unset)` |
| `ENVIRONMENT` | Alternate env label | P2 | `(unset)` |

#### Misc
| Var | Purpose | Criticality | Default |
|---|---|---|---|
| `SENTRY_DSN` / `SENTRY_ENVIRONMENT` / `SENTRY_RELEASE` / `SENTRY_TRACES_SAMPLE_RATE` / `SENTRY_PROFILES_SAMPLE_RATE` | Sentry config | P1 | none / 0 |
| `STRIPE_*` | Stripe config (billing gated) | P2 | none |
| `BILLING_ENABLED` | Billing feature flag | P2 | false |
| `BACKEND_URL` / `AKKI_BACKEND_URL` | Backend self-URL | P2 | none |
| `AKKI_CRON_SECRET` | Cron auth header | P2 | none |
| `AKKI_CHAT_FIXTURES_ENABLED` | Chat fixtures (test) | P2 | false |
| `AKKI_DEEP_*` | Deep quota config | P2 | default |
| `IDEAS_LLM_ENABLED` / `IDEAS_SCHEDULER_DISABLED` | Ideas flags | P2 | true / false |
| `INBOX_ROUTING_LLM_ENABLED` | Inbox routing | P2 | true |
| `INBOUND_DOMAIN` / `INBOUND_PROVIDER` | Inbound config | P1 | none |
| `NEWS_FETCH_TIMEOUT_SECONDS` / `NEWS_REFRESH_MINUTES` / `NEWS_TTL_DAYS` | News config | P2 | default |
| `SOLVA_V2_ENABLED` | Solva v2 toggle | P2 | true |
| `SOLVA_V2_SMOKE_URL` / `APPSHELL_SMOKE_URL` / `E1_SMOKE_URL` | Smoke test URLs | P2 | none |
| `E2E_PASSWORD` | E2E test creds | P2 | none |
| `VALIDATOR_DAILY_SOFT_CAP` | Validator quota | P2 | default |
| `PULSE_SHIELD_TEXT` | Pulse Shield UI text | P2 | default |
| `CYCLE_FROM_EMAIL` / `CYCLE_REPLY_DOMAIN` | Cycle email | P1 | none |
| `DISABLE_DEMO_SEED` | Skip demo seed on boot | P2 | false |
| `CONTACT_NOTIFY_EMAIL` / `EARLY_ACCESS_NOTIFY_EMAIL` / `FOUNDER_NOTIFY_EMAIL` | Notify destinations | P2 | none |
| `HOSTNAME` | Pod hostname (k8s) | P2 | auto |
| `PYTEST_CURRENT_TEST` | Pytest marker (auto) | P2 | auto |

### 9.4 Deployment

**Emergent platform:** containerised + k8s-managed. Backend on port 8001 internally; frontend on port 3000; ingress routes `/api/*` to backend and everything else to frontend. ALL URLs / ports / secrets come from env vars.

**Boot guards (server.py:~573):**
- `AKKI_ENV=production` + `ALLOW_UNSAFE_UPLOADS=true` → REFUSE BOOT.
- `AKKI_ENV=production` + missing `POSTMARK_WEBHOOK_SECRET` (when EMAIL_PROVIDER=postmark) → REFUSE BOOT.
- `AKKI_ENV=production` + missing `SYNISENSE_MASTER_SECRET` → boot warning + transient secret (audit chain becomes per-process).

**Health endpoints (production probes):**
- `GET /api/health` — composite probe (DB connection + service liveness)
- `GET /api/healthz/shield` — Shield warmup state
- `GET /api/healthz/clamav` — ClamAV liveness

---

## 10 · Discipline Rails

The methodology that ships every phase. Documented in `MASTER_STATE.md` Section 14 (Operating contract). Reproduced here in summary form.

### R1 — Pre-Read
Every dispatch begins with a written Pre-Read at `/app/memory/sprints/<PHASE>.md` that documents:
- Scope (what we're shipping, in 1-3 sentences)
- Architecture (the seam, the new function signatures)
- Lockdown test set (≤10 deterministic tests; integration tests separately marked)
- Risks (what could break, mitigation)
- Rollback (one-line revert path)

### R2 — Approval Gate
**No code dispatch without written user approval.** The Pre-Read is shared; the user replies "approved" (often with tightenings). The agent does NOT proceed without that signal.

### R3 — Phase Done
A phase is "done" only when:
- Lockdown tests pass.
- Deterministic regression sweep passes (160+ tests green).
- Integration-marked tests pass when applicable.
- `MASTER_STATE.md` Section 8 updated.
- Sprint memo close-out written.

### R4 — Test Floor / Ceiling
- **Floor:** every phase has at least 5 lockdown tests.
- **Ceiling:** no more than 10 lockdown tests per phase. The lockdowns pin the contract; broader coverage is the deterministic regression sweep.

### R5 — Root-cause first
No surface patches on assumed problems. Reproduce the bug, trace the root cause through the failure chain, then fix. If the fix is in a different module than the symptom, document the route in the Pre-Read.

### R6 — No side quests
A phase ships exactly what was Pre-Read'd. Any discovery during the dispatch is logged as a backlog item in `MASTER_STATE.md`, not silently scoped in.

### R7 — Antiforget continuity
Every phase close-out memo answers: "What did this leave half-built?" and "What's the obvious next phase?" — so a fresh agent fork can pick up without re-discovery.

### Honesty Protocol
- No silent except-swallows. Every exception path logs with `exc_info=True`.
- No `# noqa` without an immediate cited reason.
- No "claim success" without a passing test.

### Testing Rules
- Generic testing subagents are BANNED for SyniSense work.
- Custom pytest + raw Playwright scripts in `/tmp` only.
- Real-LLM tests use `@pytest.mark.integration` and are excluded from the default sweep.

### MASTER_STATE.md
The canonical state ledger. Single source of truth. Section structure:
1. Overview / current phase
2. Operating contract (the Discipline Rails)
3. Persona / Voice rules
4. Architecture summary
5. Tech debt backlog (and 5b: declined items with rationale)
6. Last user direction
7. Continuity (pause/resume signals)
8. Phase ledger (the actual list of shipped phases with status)
9. Sprint memo references
10. Health-check probes
11. Operational risks
12. Reference doc registry
13. Glossary
14. Operating contract (canonical)

---

## 11 · Known Tech Debt (engineering-side, honest)

### 11.1 spaCy POS-tag check not yet shipped (P1)
Phase 14 added a 43-term protector list against the most observed ORG false positives (Malaria, Monday, August, etc.). A more principled fix is a POS-tag check: drop the spaCy ORG hit when the token's POS isn't PROPN. This was descoped to keep Phase 14 small. **Cost to ship:** ~20 LOC + 2 tests. **Risk:** low (additive guard).

### 11.2 Confidence chip on universal Documents page (P1, DECLINED)
Phase 7 writes `documents.confidence_pct` as a mirror but the universal `/app/documents/{doc_id}` page doesn't render the chip. The Work Studio overlay does. **Cost:** ~25 LOC FE-only delta + 1 lockdown test. **Status:** the user has DECLINED this as gold-plating (3 separate offers). Documented for posterity.

### 11.3 Lint rot in routers/documents.py (P2)
The Documents router has accumulated extension fields that don't always carry through the GET projection allow-list cleanly. Phase 5 iter-2 Fix A landed a one-line extension. Future Documents extensions need a careful read of the projection allow-list to avoid the same regression class. **Mitigation:** Phase 5 lockdowns pin the contract.

### 11.4 PPTX read-only in DocumentOverlay (P2)
`DocumentOverlay.jsx:680` locks PPTX to read-only. PPTX structural editing in-app is a substantial work item (likely 200+ LOC across FE + BE + a new PPTX merge strategy). **Mitigation:** users edit in PowerPoint and re-upload.

### 11.5 Real-time collaborative editing not shipped (P2)
Phase 6 ships single-user inline editing. Real-time collab (OT or CRDT — Yjs is the obvious choice) is parked. **Mitigation:** save-on-close belt + last-write-wins.

### 11.6 Tenant entity cache TTL-based, not push-invalidated (P2)
`SYNISENSE_SHIELD_MAP_TTL_HOURS` defaults to 24h. When a tenant adds a new entity, the catalogue isn't auto-invalidated; new entities are visible after TTL expiry. **Cost:** ~30 LOC for a `register()` push-invalidation hook + 2 tests. **Risk:** low.

### 11.7 `useFileInputResetOnInvoke` hook not yet shipped (P2, DECLINED)
BUG-ANL-002 fix applied the `finally`-block input.value clear to ONE call site. A cross-cutting hook would clean up the pattern across the codebase. **Status:** DECLINED by user as scope creep.

### 11.8 `data-testid` presence smoke test (P2, DECLINED)
A CI-level test that asserts every `<button>` / `<a>` / `<input>` carries a `data-testid` would harden E2E reliability. **Status:** DECLINED by user.

### 11.9 SyniSense Engine scheduler single-replica lock (P3)
Hourly cron locks `scheduler_locks.synisense_engine_hourly` to a single replica. If we scale to multi-region deployment, the lock collection needs distributed semantics. **Mitigation:** current load is single-region.

### 11.10 Microsoft OAuth is a mock (P2)
The `auth_oauth.py` Microsoft OAuth probe returns a 200 OK but doesn't complete an actual Identity Platform handshake. **Mitigation:** we don't claim Microsoft OAuth in product copy.

### 11.11 Boot-time warmup_or_warn coupling (P3)
H2.5 P0 hotfix downgraded `warmup_or_die` to `warmup_or_warn` after a prod outage. A failed warmup writes an `audit_invariant_violations` row and proceeds; per-request fail-closed still holds. The trade-off: a fully-broken Shield will still let the pod come up "ready" even though `/api/healthz/shield` returns 503. **Mitigation:** k8s readiness probe on `/api/healthz/shield` should fail the pod from receiving traffic.

### 11.12 Dedicated DOCX minutes template (P2)
Phase 5 iter-2 Fix C noted: minutes-kind compiles default to the report template. A dedicated minutes template (timestamps, attendee list, action items) would be more semantic. **Cost:** ~50 LOC new template + 1 test.

---

## 12 · Future / Parked / Declined Items

### Future (active P1)
- spaCy POS-tag check (Phase 14 followup) — additive ORG protector hardening.
- Confidence chip on universal Documents page — declined but worth surfacing again at the right time.
- Cohort waitlist email cadence — outbound notification when a waitlist member is invited.

### Parked (P2)
- Collaborative editing (Yjs / OT)
- PPTX structural editing
- Rich-media insertion in tiptap editor (images, charts)
- Pulse digest cadence + "why didn't this idea appear" diff view
- Dedicated DOCX minutes template
- Tenant entity cache push-invalidation
- `useFileInputResetOnInvoke` cross-cutting hook
- `data-testid` presence smoke test
- Multi-region SendGrid routing
- Distributed scheduler locking

### Declined (paper trail in MASTER_STATE.md Section 5b)
- Phase 6 "gold-plating" enhancements offered by agent and declined.
- Phase 7 universal-documents confidence chip.
- BUG-ANL-002 cross-cutting hook.

### Future Infra (P3)
- Multi-tenant Postgres adapter (currently MongoDB-only)
- Distributed cache (Redis) layer for tenant entity catalogue
- Edge-cached static assets
- Multi-region active-active deployment

---

## 13 · ASCII Diagrams

### 13.1 Shield pipeline

```
                           shield_invoke()
                                 │
        ┌────────────────────────┼────────────────────────┐
        ▼                        ▼                        ▼
  purpose_validator         deidentify()           audit_log.write_audit()
  (allowlist + internal)         │                  (after re-id)
        │                        │
        ▼                        ▼
  Rejected → 503         ┌───────────────────────┐
                         │  Layer 1: regex       │
                         │   (24 patterns,       │
                         │    Luhn-validated CC, │
                         │    purpose-skip set)  │
                         └──────────┬────────────┘
                                    ▼
                         ┌───────────────────────┐
                         │  Layer 2: tenant dict │
                         │   (per-tenant cache,  │
                         │    4-char floor)      │
                         └──────────┬────────────┘
                                    ▼
                         ┌───────────────────────┐
                         │  Layer 3: spaCy NER   │
                         │   (en_core_web_trf    │
                         │    or _sm fallback,   │
                         │    ORG protector 43)  │
                         └──────────┬────────────┘
                                    ▼
                            overlap resolution
                            (regex > tenant > spaCy)
                                    ▼
                            token_map + redacted_text
                                    ▼
                           llm_router.invoke_with_metering()
                                    ▼
                              raw LLM response
                                    ▼
                            reidentifier.reidentify()
                            (per-class strategy)
                                    ▼
                            user-visible response
                                    ▼
                       trust_receipt.build_trust_receipt()
                            (HMAC-SHA256 + HKDF)
                                    ▼
                          synisense_audit_log row +
                          synisense_trust_receipts row
```

### 13.2 Work Studio lifecycle (with Phase 7 cache)

```
        ┌───────────────────────────────────┐
        │  CreateArtefactModal              │
        │  (sources, kind, format, prompt)  │
        └────────────┬──────────────────────┘
                     ▼
        ┌───────────────────────────────────┐
        │  /api/work-studio/exports/start   │
        └────────────┬──────────────────────┘
                     ▼  status=created
        ┌───────────────────────────────────┐
        │  streaming_v9_router              │
        │  · shield_invoke (compile prompt) │
        │  · LLM streams structured_content │
        └────────────┬──────────────────────┘
                     ▼  status=compiling
        ┌───────────────────────────────────┐
        │  confidence_scorer.score_         │
        │   confidence(source_blobs)        │
        │  · 4-dim rubric                   │
        │  · cache_key = SHA-256(content)   │
        └────────────┬──────────────────────┘
                     ▼  status=ready
        ┌───────────────────────────────────┐
        │  DocumentOverlay (tiptap)         │
        │  · inline edit + autosave         │
        │  · Revise with AI                 │
        │  · save-on-close belt             │
        └────────────┬──────────────────────┘
                     ▼  on commit
        ┌───────────────────────────────────┐
        │  /api/work-studio/overlays/commit │
        │  · IF cache_key matches → SKIP    │
        │    rescore (Phase 7 T4)           │
        │  · ELSE → rescore + write         │
        │    intelligence_report fields     │
        └────────────┬──────────────────────┘
                     ▼  status=committed
        ┌───────────────────────────────────┐
        │  /app/documents/{doc_id}          │
        │  (downloadable artefact)          │
        └───────────────────────────────────┘
```

### 13.3 Analyze flow (multi-workbook synthesis)

```
        upload N workbooks (N ≤ 5)
                    │
                    ▼
        parser.py parses each → typed sheet matrix
        (sheets renamed <stem>::<sheet>)
                    │
                    ▼
        autopick_forecast_columns(sheets=union)
        · scores every (sheet × date_col × num_col)
        · density gate rejects sparse columns
        · picks highest (non_null, spread)
                    │
                    ▼
        run_forecast(selected triple)
        · linear regression slope+intercept
        · R² + residual stddev
        · 80% CI band (1.282 × stddev)
        · low_signal=true if R² < 0.30
                    │
                    ▼
        anomaly_detector(first sheet of each)
        · z-score outliers
                    │
                    ▼
        solva_v2.analyze_narration(forecast + anomalies + objective)
        · shield_invoke
        · Bottom Line + per-tab drill-down
                    │
                    ▼
        analyses.runs.push(new_run)
        (idempotent on input_hash match)
                    │
                    ▼
        AnalyzeDrawer renders What changed / What's likely next / What's odd / Sources / Export
```

### 13.4 Chat round-trip (with streaming reidentifier)

```
POST /api/chats/{id}/messages/stream
        │
        ▼
        chat.py builds:
        · prior context from chats.messages
        · system_msg (Phase-14 fluency preamble)
        · purpose = "chat"
        │
        ▼
        shield_invoke(content, system_msg, ...)
        ├──▶ deidentifier.deidentify()
        │    → token_map + redacted_text
        │
        ├──▶ llm_router (direct_stream when CHAT_STREAMING_MODE=direct_stream)
        │    │
        │    └──▶ Anthropic Claude Sonnet 4.5 (sees redacted_text + system_msg)
        │         │
        │         └─── delta-by-delta stream
        │              │
        │              ▼
        │         StreamingReidentifier.feed(delta)
        │         · buffers partial [[ENT_…]] across deltas
        │         · per-class re-id strategy
        │         · emits user-safe prefix
        │              │
        │              ▼
        │         SSE event → client
        │              │
        │              ▼
        │         Chat.jsx incrementally renders
        │
        └──▶ on stream complete:
             · audit_log.write_audit
             · trust_receipt.build_trust_receipt
             · chats.messages.push({role:"assistant", ..., synisense_audit_ids: [audit_id]})
             · client renders Trust chip
```

---

## 14 · Glossary

Engineering-focused supplement to PRODUCT.md §10 (full product glossary).

- **APScheduler** — Python scheduler library used for all cron jobs.
- **Async event loop coupling** — the constraint that any blocking call (spaCy NER, large numpy ops) must run on a worker thread to avoid blocking the asyncio loop.
- **Canonical JSON** — `json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)`. Used for HMAC signing.
- **CSRF middleware** — `routers/csrf.py` mint + a Starlette middleware that validates the `X-CSRF-Token` header against the cookie-bound token.
- **Direct stream** — `CHAT_STREAMING_MODE=direct_stream` bypasses the emergentintegrations adapter and streams directly from Anthropic SDK.
- **emergentintegrations** — proprietary multi-provider LLM SDK wrapper. Single SDK for OpenAI / Anthropic / Gemini.
- **Fail-closed** — pattern: any error in a security-critical path raises rather than returning a fallback. The Shield is fail-closed end-to-end.
- **Fernet** — symmetric encryption from `cryptography` library. Used for OAuth token vault (`OAUTH_TOKEN_VAULT_KEY`).
- **HKDF** — Key Derivation Function. Tenant-scoped HMAC keys derived from master secret.
- **HMAC-SHA256** — keyed-hash MAC. Trust Receipt signatures.
- **Luhn** — mod-10 checksum algorithm for credit cards. `_REGEX_VALIDATORS["CREDIT_CARD"]` uses Luhn to drop false-positive 16-digit numbers.
- **MASTER_SECRET** — root entropy for HKDF. Set via `SYNISENSE_MASTER_SECRET` env var.
- **Motor** — async MongoDB driver (wraps PyMongo).
- **Notes history** — append-only audit trail of notes edits. Lives on `documents`, `analyses`, etc.
- **Override hook** — pattern where a test sets a global flag (e.g. `AKKI_SKIP_SHIELD_WARMUP=1`) to bypass a boot-time invariant.
- **Per-request token map** — `Dict[str, str]` mapping `[[ENT_…]]` → original. Lives in memory only; never persisted. Discarded after the route returns.
- **Phase 14 fluency preamble** — system prompt threaded via `shield_invoke(system_msg=…)` that instructs Claude not to leak Shield meta-language.
- **Presidio analyzer** — Microsoft Presidio analyzer wrapping spaCy + 24 regex recognisers. Used internally by the Shield's regex layer.
- **Refuse to decide** — Solva v2 pattern (`services/workbook_analyzer/refuse_to_decide.py`). Engine returns a typed Refusal when input is insufficient.
- **Shield warmup** — boot-time spaCy load + a no-op deidentify to validate the pipeline. `deidentifier.warmup_or_warn`.
- **Single canonical entrypoint** — `services/synisense/shield/client.invoke()`. No other Shield API surface exists for callers.
- **SSE** — Server-Sent Events. The streaming mechanism for chat + Work Studio compile.
- **Supervisor** — `supervisord` process supervisor. Manages backend + frontend lifecycle.
- **Token vault** — `services/crypto/token_vault.py`. Fernet-encrypted OAuth refresh-token storage.
- **Trust receipt** — HMAC-signed proof-of-redaction. One per Shield call. Stored in `synisense_trust_receipts`.

---

*End of DEVELOPMENT.md.*
