# Akki / Syni — Product Reference

> **Audience:** Technical investor / acquirer due-diligence, non-engineering stakeholder onboarding.
> **Last updated:** Phase 15 dispatch — 2026-06-05.
> **Cross-references:**
> - `/app/memory/MASTER_STATE.md` — canonical state ledger (this doc paraphrases nothing from it; status is taken verbatim).
> - `/app/memory/INVESTOR_QA.md` — investor Q&A on SyniSense governance.
> - `/app/memory/DEVELOPMENT.md` — engineering deep dive (sister doc to this one).

---

## 1 · Executive Summary

Akki (operating brand: Syni) is a **decision-support platform for senior executives and boards**. It combines four capabilities most teams can only get by stitching together three or four vendors:

1. **Akki Chat** — a Claude Sonnet 4.5 conversational assistant that any executive can use in the open, because every prompt and every reply passes through a deterministic data-governance layer (SyniSense Shield) before touching the LLM.
2. **Solva v2 reasoning engine** — multi-stage workbook analysis and structured argumentation, with claim-level confidence weighting and audit trails. Solva is not a "chat the spreadsheet" wrapper; it is a directed reasoning pipeline with explicit refusal paths.
3. **Work Studio document lifecycle** — a closed loop from open question → cited brief / report / deck / minutes → reviewer drawer → committed artefact. Every artefact carries a four-dimension confidence score and a citation manifest tied to its source documents.
4. **SyniSense** — the data-governance and tenant-isolation substrate. Three-layer de-identification (regex → tenant dictionary → spaCy NER), asymmetric re-identification (hard PII never reaches the user-visible reply even after the LLM round-trip), and HMAC-signed trust receipts for every Shield call.

Akki is wire-path-honest: the LLM never sees raw tenant PII, and the user never sees raw payment cards / SSNs / API keys regardless of what the LLM emits. Every call is logged with a cryptographic receipt. This is the difference between Akki and a typical "secure ChatGPT" wrapper: those wrappers run de-identification, but they rehydrate everything on the way back. Akki classifies PII into *contextual* (PERSON, ORG, GPE) — rehydrated for continuity — and *hard* (CREDIT_CARD, SSN, API_KEY, EMAIL, PHONE, IP, IBAN, UK_NI) — which stay redacted in the user-visible reply with type-aware placeholders (e.g. `[PAYMENT_CARD_••••7689]`, `[API_KEY_REDACTED]`).

The product is built around the **Discipline Rails** development methodology: every code dispatch runs through a written Pre-Read, requires explicit user approval, ships with a ≤10-test lockdown, and updates a single source-of-truth state file (`MASTER_STATE.md`) at phase close. Fourteen phases have shipped under this methodology to date, with zero open bugs and one user-side blocker (Google OAuth credentials).

---

## 2 · Positioning & Value Proposition

**What Akki is:** the operational system of record for a chief executive or board's decision-making cadence. It captures the inputs (signals, news, attached documents, contributor responses), runs the reasoning (Solva v2 + Work Studio + chat), produces the artefacts (briefs, reports, decks, minutes), tracks the resolutions (tasks, questions, agendas), and proves the data trail (trust receipts, audit log, citation manifests).

**Why not just use Claude / ChatGPT directly:** for a regulated executive, the cost of a single PII leak (a board paper containing salary data, or a customer email forwarded to an LLM, or a payment card number copied in by mistake) exceeds the cost of subscribing to a year of governance tooling. Akki removes the policy enforcement burden — the user can paste anything; the Shield handles classification, redaction, audit, and asymmetric rehydration without the user thinking about it.

**Why not just use Notion / Microsoft 365 / Google Workspace:** those platforms surface documents; they don't reason over them. Akki's value sits in the gap between document storage and decision: a Work Studio brief is not just a Word file; it is a structured artefact with a confidence score, a citation manifest, a lifecycle state machine (draft → compile → enhance → review → commit), and a reopen path that auto-flips status from "answered" back to "open" when a contributor's response invalidates the artefact's basis.

**Differentiator headline:**

> **Akki is the only LLM-powered executive workspace where the LLM is the contractor, not the owner.** The Shield contractually constrains what the LLM sees, what it can return, and how the user perceives its output.

**Buying centre:** Chief Executives (decision-makers), Chiefs of Staff (operators), Board Secretaries / Company Secretaries (custodians of the record), Risk / Compliance officers (validators of the governance story).

---

## 3 · Personas & Buying Centre

### 3.1 Primary persona — "The Executive"
**Who:** A C-suite operator (CEO, COO, MD) running a 50-1,000-person organisation with a structured decision cadence (weekly leadership, monthly P&L, quarterly board).
**Pain:** Lives in inboxes, slide decks, and document tabs. Has 9 things to decide this week and 6 of them depend on data scattered across 4 systems. Can't trust generic LLM tools with the inputs.
**Job-to-be-done:** "Give me a brief on the [topic] by [time], grounded in the documents I uploaded, with the bits I can cite and the bits I can't clearly marked."
**Akki surface used most:** Work Studio (compile → review → commit), Akki Chat (ad-hoc reasoning), Pulse Ideas (weekly synthesis).

### 3.2 Secondary persona — "The Chief of Staff"
**Who:** Right hand to the Executive. Owns the cadence (meetings, agendas, follow-ups).
**Pain:** Three weeks behind on follow-ups, can't see which contributor responses are still outstanding, manually drafting reminder emails.
**Job-to-be-done:** "Run the cycle: distribute the contribution prompts, track responses, draft the chairperson notes, and surface what's outstanding."
**Akki surface used most:** Task Manager + Cycle Manager (Phase B2 / Phase E), Inbox routing.

### 3.3 Tertiary persona — "The Board Secretary"
**Who:** Custodian of the board record. Concerned with audit trails, signed-off minutes, evidence chains.
**Pain:** When the regulator or a journalist asks "what did the board know in Q2?", needs to produce a defensible answer fast.
**Job-to-be-done:** "Show me every document the board read this quarter, who reviewed it, who annotated it, and the cryptographic receipt that proves no third party saw the underlying PII."
**Akki surface used most:** Trust Center, Audit Panel, Document Engagement.

### 3.4 Compliance persona — "The Risk Officer"
**Who:** Owns regulatory exposure. The decision-maker on "can we use an LLM at all?"
**Pain:** Vendor due-diligence on AI is a nightmare. "Does this share data with the model provider?" "How do we know?" "What's the residual risk if your governance layer fails?"
**Job-to-be-done:** "Validate that Akki's data flow matches what the sales deck claimed."
**Akki surface used most:** Trust Center (public + internal), Investor Q&A document, Shield observability dashboard.

---

## 4 · Differentiators — SyniSense + Solva

### 4.1 SyniSense — data governance

SyniSense is the substrate. Every LLM call from every product surface (chat, Solva, Work Studio, confidence scoring, briefings) routes through `shield_invoke()`. There are zero direct LLM SDK imports in the product code outside the Shield module; this is enforced by lint convention and code review.

**What the Shield does, in plain English:**

1. **Classifies sensitive content** in the prompt across three layers:
   - **Regex layer** — deterministic patterns: EMAIL, PHONE_E164, IBAN, ACCOUNT_NUM, CREDIT_CARD (Luhn-validated), SSN, UK_NI_NUMBER, MONEY, DATE_ISO, IP, URL, API_KEY families.
   - **Tenant dictionary** — case-insensitive longest-match against the per-tenant entity catalogue harvested from existing Mongo collections (`accounts`, `contexts`, `cycles`). This is what catches "Lemasy Limited" or "Bramuel Mwangi" — proper nouns the LLM otherwise wouldn't recognise as PII.
   - **spaCy NER** (`en_core_web_trf` preferred, `en_core_web_sm` fallback) — PERSON, ORG, GPE, PRODUCT, NORP, FAC, EVENT, LAW. Phase 14 added a 43-term **ORG protector** that drops false positives on disease names (Malaria), weekdays, months, and common capitalised words.

2. **Substitutes detected entities** with opaque tokens of the shape `[[ENT_<TYPE>_<NNN>]]` (e.g. `[[ENT_PERSON_001]]`, `[[ENT_CREDIT_CARD_001]]`).

3. **Calls the LLM** with the redacted prompt only. The provider sees no raw PII.

4. **Re-identifies the response** using an **asymmetric** strategy:
   - **Contextual classes** (PERSON, ORG, GPE, PRODUCT, NORP, FAC, EVENT, LAW, DATE_ISO, MONEY, URL) → substitute back the original value. Continuity matters for conversational coherence.
   - **Hard-PII classes** (CREDIT_CARD, ACCOUNT_NUM, SSN, IBAN, PHONE_E164 → last-4 placeholder; UK_NI_NUMBER, API_KEY, EMAIL, IP → fully-redacted placeholder). Even if the LLM tries to echo back what it received, the user sees `[PAYMENT_CARD_••••7689]`, not the original PAN.

5. **Writes a Trust Receipt** — HMAC-SHA256 signature over the de-id summary, dilution score, exposure-reduction score, request hash, and response hash. Tenant-scoped via HKDF-derived key. The receipt is canonical-JSON-signed so any byte tweak invalidates the signature.

**Fail-closed semantics:** if any step of the pipeline raises (spaCy load failure, tenant lookup failure, Shield rejection), the request 503s. Raw content NEVER reaches the LLM under any failure mode. This is the security promise.

### 4.2 Solva v2 — reasoning governance

Solva is the structured-reasoning engine. Where chat is conversational and ad-hoc, Solva is a directed pipeline with explicit phases:

- **Phase A** — input intake (workbook + objective).
- **Phase B** — extraction / parsing.
- **Phase C** — claim generation with per-claim confidence weighting.
- **Phase D** — challenge / dialectic (the engine pressure-tests its own claims).
- **Phase E** — synthesis + polished artefact (export-ready).

Each phase emits typed artefacts. The engine refuses to proceed when input is insufficient (the "Refuse to Decide" pattern in `services/workbook_analyzer/refuse_to_decide.py`). Solva's outputs feed Work Studio compilation but are also surfaceable on their own.

### 4.3 The product moat
The IP defensibility lives in two places:
1. **Asymmetric re-identification + per-class visibility strategy.** Most "secure LLM" vendors are symmetric — they redact on the way out and rehydrate on the way back, giving the user the illusion of continuity but no actual protection if the LLM ever leaks. Akki's asymmetric design means an LLM leak surfaces in the audit log but never on the user's screen.
2. **The Discipline Rails methodology + the MASTER_STATE.md ledger.** Every phase ships with a Pre-Read, an approval gate, a lockdown test set, and a memo. The codebase has fourteen phases of evidence that this works under real product pressure — it's not a slide deck pattern, it's the actual git history.

---

## 5 · Feature Catalogue

### 5.1 Onboarding

**Purpose:** First-time user lands at `/first-session`, picks an entry path (Create your first cycle / Upload a Document / Try the Demo), and is routed to the matching app surface with the right context primed.

**User journey:**
1. User signs up via `/signup` or magic link.
2. Email magic link arrives (TM3 / SendGrid Inbound Parse stack).
3. First login forces a password set (`SetPasswordGuard` gate at `frontend/src/components/SetPasswordGuard.jsx`).
4. Lands at `/first-session` (page: `frontend/src/pages/FirstSession.jsx`).
5. Picks an option:
   - **Create your first cycle** → `/app/task-manager` (Track B Phase B1b).
   - **Upload a Document** → `/app/documents?upload=1`.
   - **Try the Demo** → `/app` (AppHome).
6. From there, contextual onboarding briefs surface via `OnboardingBriefsModal`.

**Key UI surfaces:** `/first-session` (`FirstSession.jsx`), `OnboardingBriefsModal`, `Day16Banner`.

**Underlying capability:** Persona-routing onboarding that respects the explicit user intent rather than forcing a tutorial. Each entry path lands the user on a primed surface ready to accept their work.

**Current state:** Live. Tester PASS on Journeys 4-v2 + 6 + 7 + 8 (Track B Phase B1b).

**Dependencies:** Email provider (SendGrid), Magic link router (`auth_magic`), Password reset gate (`first_login_password_set`).

---

### 5.2 Authentication & Identity

**Purpose:** Account creation, login, MFA, password reset, OAuth (Google/Microsoft), magic links, session management.

**User journey (login):**
1. User hits `/signin` (`SignIn.jsx`).
2. Email + password OR magic link OR Google OAuth.
3. JWT issued (HS256 via `services/crypto/`), CSRF token minted (`/api/csrf`).
4. Session persisted; cookie set with `COOKIE_SECURE` from env.
5. MFA challenge if enrolled (TOTP via `/api/mfa/*`).
6. First-login forces password set (`SetPasswordGuard`).

**Key UI surfaces:** `/signin` (`SignIn.jsx`), `/signup` (`SignUp.jsx`), `/forgot-password` (`ForgotPassword.jsx`), `/reset-password/:token` (`ResetPassword.jsx`), `/account/security` (`AccountSecurity.jsx`).

**Underlying capability:** Multi-factor identity stack with magic-link recovery and OAuth federation. Six distinct error codes for password reset (C1-revised Phase B). Brute-force protection via `login_attempts` collection.

**Current state:**
- ✅ Live: email/password, magic link, password reset, MFA, JWT, CSRF.
- 🚧 USER-BLOCKED: Google OAuth (G2) — awaiting GCP credentials.
- ⚠️ Microsoft OAuth — registered as mock (`auth_oauth.py` Phase U).

**Dependencies:** SendGrid (magic link delivery), Crypto module (`services/crypto/`), CSRF middleware (`routers/csrf.py`).

---

### 5.3 Chat (AKKI Chat)

**Purpose:** A long-running conversational surface where any executive can paste anything (board minutes, draft emails, customer data) and reason with Claude Sonnet 4.5, knowing the Shield handles redaction and the audit trail.

**User journey:**
1. User opens `/app/chat` (page: `frontend/src/pages/Chat.jsx`).
2. Picks or creates a chat session (`chats` collection).
3. Types a prompt, optionally attaches files (PDF / DOCX / images / workbook).
4. SyniSense Shield de-identifies the prompt + attachments.
5. Claude Sonnet 4.5 responds via direct streaming (`services/llm_streaming.py`) when `CHAT_STREAMING_MODE=direct_stream` and the Anthropic key is direct, else buffered via emergentintegrations.
6. The `StreamingReidentifier` rehydrates contextual tokens delta-by-delta as they arrive (with cross-delta token-boundary protection).
7. The user sees the final reply with hard-PII placeholders + a "Trust" chip linking to the audit panel.

**Key UI surfaces:** `/app/chat` (`Chat.jsx`), `ChatAuditPanel` (`routers/chat_audit_panel.py`), `SynisenseObservability.jsx` (admin view).

**Underlying capability:** Full conversational chat with attachment ingestion, per-message Shield audit, fluency-preserving system prompt (Phase 14), and consistent token shape `[[ENT_<TYPE>_<NNN>]]`. Phase 14 closed a UX failure where Claude was leaking Shield meta-language ("redacted tokens", "did you mean").

**Current state:** ✅ Live. Phase 14 ✅ shipped 2026-06-05 — chat fluency hardened, 14/14 default + 1/1 integration-marked real-LLM test PASS in 23.37s.

**Dependencies:** SyniSense Shield, Anthropic Claude (via Emergent LLM Key), spaCy NER, tenant entity catalogue.

---

### 5.4 Solva v2 — Workbook Analysis & Reasoning

**Purpose:** Structured multi-phase reasoning over a workbook + objective. Produces a polished artefact (Phase E export) with claim-level confidence and explicit refusal paths when input is insufficient.

**User journey:**
1. User opens `/app/solva` (`SolvaApp.jsx`).
2. Creates a new session (`SolvaSession.jsx`), uploads workbook + types objective.
3. Phase A → Phase B → Phase C → Phase D → Phase E pipeline runs.
4. Each phase emits typed artefacts visible in the session view.
5. Solva refuses to decide when the input is insufficient (`services/workbook_analyzer/refuse_to_decide.py`).
6. Final artefact exportable as DOCX/PDF/PPTX.

**Key UI surfaces:** `/app/solva` (`SolvaApp.jsx`), `/app/solva/sessions` (`SolvaSessions.jsx`), `/app/solva/sessions/:id` (`SolvaSession.jsx`), `/app/solva/sessions/:id/phase-d` (`SolvaPhaseDSession.jsx`).

**Underlying capability:** Per-claim probability weighting (`services/solva_v2/probability_weighting.py`), aggregate-level confidence (`services/solva_v2/payload_builder.py:_input_confidence_pct`), opinion filter (`services/solva_v2/opinion_filter.py`), and an explicit state machine.

**Current state:** ✅ Live. Solva v2 is the only Solva surface (v1 archived M.4 2026-05-26).

**Dependencies:** SyniSense Shield, Workbook Analyzer (`services/workbook_analyzer/`), Anthropic Claude.

---

### 5.5 Work Studio — Document Lifecycle

**Purpose:** The closed-loop document lifecycle: source documents → compile / enhance → review drawer → commit. Every artefact carries a four-dimension confidence score (Phase 7), a citation manifest, and a lifecycle status.

**User journey (compile a brief):**
1. User opens `/app/work-studio` (`WorkStudio.jsx`).
2. Picks a source document or set of sources.
3. Picks the artefact kind: report / brief / minutes / deck / blank draft.
4. `CreateArtefactModal` collects instructions.
5. `LoadingChecklistModal` shows step-by-step progression (Compile → Enhance → Score → Complete).
6. Compile endpoint streams progress events (`streaming_v9_router`).
7. On completion, the artefact lands in the Document Review Drawer (`DocumentOverlay.jsx`).
8. User edits inline (Phase 6 ✅) — tiptap editor with autosave + save-on-close belt.
9. Optionally invokes "Revise with AI" (uses the existing enhance infrastructure).
10. Commit-time recompute: if structured_content changed, confidence is rescored (Phase 7 ✅, with idempotency-gated cache via SHA-256 of structured_content).
11. Committed artefact surfaces on the universal Documents page and is downloadable as DOCX / PDF / PPTX.

**Key UI surfaces:** `/app/work-studio` (`WorkStudio.jsx`), `WorkStudioDocumentPage.jsx`, `WorkStudioActivity.jsx`, `WorkStudioAnalyze.jsx`, `DocumentOverlay.jsx`, `DraftingDrawer.jsx`, `CreateArtefactModal`, `LoadingChecklistModal`.

**Underlying capability:** Append-only versioning (`work_studio_exports.runs[]`), notes_history with empty-body deletion semantics, source-doc resolution via citations_manifest, multi-renderer dispatch (report/brief/minutes/deck × docx/pdf/pptx), inline rich-text editing with PDF carve-out, Revise-with-AI with diff view.

**Current state:** ✅ Live. Phase 6 ✅ inline edit + Revise + BC mirror removal. Phase 7 ✅ Confidence Scoring Runtime Compute Path with 4-dim rubric. Both with 100% lockdown PASS.

**Dependencies:** SyniSense Shield (all LLM passes), tiptap editor, Confidence Scorer (`services/work_studio/confidence_scorer.py`), Citation Resolver (`services/solva_v2/citation_resolver.py`), DOCX/PDF/PPTX renderers (`services/work_studio_export.py`).

---

### 5.6 Analyze (multi-workbook synthesis)

**Purpose:** Cross-file synthesis of up to 5 workbooks per analysis, with autopicked forecast columns, anomaly detection, and McKinsey-tone narration via Solva v2.

**User journey:**
1. User opens `/app/analyze` (`AnalyzeJournal.jsx`).
2. Picks a context (defaults to active context; backfills URL via mount-time guard — see BUG-ANL-001).
3. Uploads one or more workbooks (CSV / XLSX / DOCX).
4. The file picker uses the BUG-ANL-002 fix: input.value cleared in `finally` block to avoid silent-retry loops.
5. Optionally types an objective.
6. Synthesize endpoint parses up to 5 source blobs, runs autopicker → forecast → anomaly detection.
7. Solva v2 narration generates Bottom Line + drill-down tabs (What changed / What's likely next / What's odd / Sources / Export).
8. Result lands in the Analyze Drawer (`AnalyzeDrawer.jsx`).
9. Notes can be added (autosave, history preserved).
10. Refresh creates a new version in the `runs[]` array (append-only, idempotent on unchanged input).

**Key UI surfaces:** `/app/analyze` (`AnalyzeJournal.jsx`), `AnalyzeDrawer.jsx`.

**Underlying capability:** Multi-workbook autopicker selects the strongest (date, numeric) pair globally across the file union. Density gate rejects sparse columns (<30% non-null OR <6 absolute non-nulls). Low-R² safety-net flag fires when R² < 0.30. Anomaly detector runs on the first sheet of each parsed source. Sheets renamed to `<filename-stem>::<sheet>` so the citation resolver works across the union. Excel binaries are deleted on session close (D4 decision).

**Current state:** ✅ Live. Phase 4 ✅ (versioning + multi-workbook), Phase 3 ✅ (Solva v2 synthesis), BUG-ANL-001 ✅ (route guard), BUG-ANL-002 ✅ (silent file-picker fix).

**Dependencies:** Workbook Analyzer (`services/workbook_analyzer/`), Solva v2 narration (`services/solva_v2/analyze_narration.py`), SyniSense Shield, Citation Resolver.

---

### 5.7 Generate Brief

**Purpose:** From any document, generate a board-ready brief with explicit signal extraction and intelligence report.

**User journey:**
1. User opens any document in the Document Reader (`DocumentDrawer`).
2. Clicks "Generate Brief".
3. If intelligence + signals are already generated, the brief is composed; otherwise, the pipeline runs them first (P0-A fix — G4 / G5).
4. The brief lands as a `work_studio_exports` row.
5. The artefact is reviewable in the Document Review Drawer.

**Key UI surfaces:** Document Reader (`DocumentDrawer`), Work Studio drawer.

**Underlying capability:** Brief generation is a special case of Work Studio compilation, with the document being its own source. Includes signal extraction (`services/documents/intelligence_service.py`), intelligence report generation, and citation-back-to-source.

**Current state:** ✅ Live. P0-A ✅ shipped (G4 + G5 closed).

**Dependencies:** Work Studio compilation pipeline, SyniSense Shield, Documents intelligence service.

---

### 5.8 Task Manager

**Purpose:** Tracks tasks with state machine (Draft → Active → Closed), commission/close actions, filter tab badges, and Follow-Up Drafts surface.

**User journey:**
1. User opens `/app/task-manager` (`TaskManager.jsx`).
2. Sees tasks grouped by filter tabs: All / Drafts / Active / Closed.
3. Each tab shows a live count badge via `GET /api/tasks/counts` (TM1 fix).
4. Picks a Draft task → clicks "Commission" → idempotent state transition.
5. Picks an Active task → clicks "Close" → confirmation modal with verbatim spec text → idempotent close.
6. Closed tasks become read-only (cannot be reopened per QA spec).
7. Follow-Up Drafts surface ("View more" → `/app/cycle/drafts`) shows Akki-drafted follow-ups to contributors with pending submissions.

**Key UI surfaces:** `/app/task-manager` (`TaskManager.jsx`), `TaskManagerActivity.jsx`, `CycleDraftJournal`.

**Underlying capability:** Idempotent state machine via `POST /api/tasks/{id}/commission` + `/close`. Audit-logged as `task.commissioned` / `task.closed`. State guards return 400 on illegal transitions. Closed-at timestamp recorded.

**Current state:** ✅ Live. Track B Phase B2 — tester PASS Journeys 14-17.

**Dependencies:** Tasks routers (`routers/tasks.py`, `tasks_initiatives.py`), Audit log, Cycle Manager.

---

### 5.9 Pulse Ideas

**Purpose:** Weekly cited synthesis across four lenses (operational, financial, customer, market). Ideas-Engine surface that proposes things the executive might not have thought of yet.

**User journey:**
1. User opens `/app/pulse-ideas` (`PulseIdeas.jsx`).
2. Sees current week's synthesis OR the most recent digest if not refreshed.
3. Each idea card carries the lens label and citation-back-to-source.
4. User can drill into the underlying signals.

**Key UI surfaces:** `/app/pulse-ideas` (`PulseIdeas.jsx`), `Pulse.jsx`.

**Underlying capability:** Four-lens weekly synthesis driven by `services/ideas_engine/`. Signals from `signal_actions`, `signal_events`, `signals` collections. Doc-extracted signals propagate from the doc reader (G9 fix).

**Current state:** ✅ Live.

**Dependencies:** Ideas Engine service, Signal collections, SyniSense Shield.

---

### 5.10 Q4Y (Questions for You)

**Purpose:** Surfaces questions extracted from documents OR raised in chat, with a side drawer showing the question, status, related document, and response history.

**User journey:**
1. User opens `/app/questions` (`Questions.jsx`).
2. Sees question cards with status badges (Open / Answered).
3. Filters by status (All / Open / Answered), sorts by recency.
4. Clicks a card → side drawer opens with full question, status badge, related document as attachment, and four CTAs:
   - **Use in Solva** → opens Solva with question pre-populated.
   - **Use in Chat** → opens chat session with question pre-populated.
   - **Share** → opens Share Question modal (recipients + optional message).
   - **Mark as Answered** → flips status.
5. Empty state: "You have not generated any questions yet. Go to a document to generate questions." + Go to Document CTA.

**Key UI surfaces:** `/app/questions` (`Questions.jsx`), Question side drawer (in `Questions.jsx`).

**Underlying capability:** Question-extraction promoter `services/documents/intelligence_service.promote_intelligence_questions_to_q4y`. Stable IDs `q4y:from_intel:{doc_id}:{idx}`. Orphan close-out on re-extraction (audit-preserved). Manual link-from-drawer to associate a response document. Reopen flow flips Answered → Open and preserves history.

**Current state:** ✅ Live. Track B Phase B3 + B4 complete — tester PASS Journeys 21-24.

**Dependencies:** Documents intelligence service, Solva v2 entry points, Chat, Share modal.

---

### 5.11 Documents Library

**Purpose:** The universal documents page. Lists every document the user can access in the current context, with filters (category / kind / shared with me / generated by Akki).

**User journey:**
1. User opens `/app/documents` (`DocumentsPage.jsx`).
2. Lists documents in the active context.
3. Clicks a row → DocumentDrawer opens with intelligence tabs (overview, signals, intelligence report, share, notes, engagement).
4. Notes autosave every 1.0s with debounced flush + beforeunload hook (G6 fix).
5. Share modal accepts up to 10 recipient_emails (G7 fix).
6. Generate Brief / Generate Signals / Open in Work Studio CTAs.

**Key UI surfaces:** `/app/documents` (`DocumentsPage.jsx`), `DocumentDrawer` (multi-tab side drawer).

**Underlying capability:** Multi-file upload via chunked POST. 250MB cap. Drag-and-drop. Akki-generated artefacts auto-mirror to documents collection with `akki_generated=true` flag.

**Current state:** ✅ Live. Track B Phase B5 G6 + G7 complete.

**Dependencies:** Documents routers (`documents.py`, `documents_async_mirror.py`), Work Studio integration, ClamAV virus scan.

---

### 5.12 Calendar

**Purpose:** Events surface showing decision calendar, board meetings, contributor deadlines.

**User journey:**
1. User opens `/app/events` (`Events.jsx`).
2. Picks a date → modal shows events for that date.
3. No "Selected — commits on Save changes" reassurance scaffolding (G10 fix removed 18 LOC of all-caps leakage text).

**Key UI surfaces:** `/app/events` (`Events.jsx`).

**Underlying capability:** Events router (`routers/events.py`). Date-extraction from documents bypassed by Shield (purpose-gated DATE_ISO skip — see deidentifier `_PURPOSE_REGEX_SKIPS`).

**Current state:** ✅ Live. Track B Phase B5 G10 ✅.

**Dependencies:** Documents intelligence extraction, Calendar Credentials (`user_calendar_credentials` collection).

---

### 5.13 Share / Send

**Purpose:** Share a document (or question, or artefact) with one or more recipients by email.

**User journey:**
1. From any document drawer → "Share document" CTA.
2. Modal accepts recipient emails (min 1, max 10), optional message.
3. SendGrid delivers; engagement is logged in `document_engagement` and `document_shares`.

**Key UI surfaces:** Share modal in `DocumentDrawer`, `Questions.jsx` (G17), `pages/SharedArtefact.jsx`.

**Underlying capability:** Recipients stored as array (`recipient_emails`) + BC singular (`shared_with_email`). Email send via SendGrid (`SENDGRID_API_KEY` from env). Inbound replies route via SendGrid Inbound Parse to `/api/inbound/sendgrid` (TM3 ✅).

**Current state:** ✅ Live. G7 ✅ (multi-recipient share), G17 ✅ (Share modal on Questions).

**Dependencies:** SendGrid, Document shares schema, Engagement tracking.

---

### 5.14 Trust Center

**Purpose:** Public-facing transparency page + internal observability dashboard for SyniSense.

**User journey (public):**
1. Any visitor opens `/trust` (`pages/TrustCenter.jsx` + `routers/observability.public_router`).
2. Sees rolling 30-day Shield call volume, success rate, percentile latencies, classes of PII redacted.

**User journey (internal):**
1. Admin opens `/app/synisense-observability` (`SynisenseObservability.jsx`).
2. Sees per-tenant metrics, audit row drill-down, failed-call inspection.

**Key UI surfaces:** `/trust` (`TrustCenter.jsx`), `/app/synisense-observability` (`SynisenseObservability.jsx`).

**Underlying capability:** `synisense_audit_log` + `synisense_trust_receipts` collections. Public mirror via `observability_router.public_router`. M.3 + ZZ.4 phases.

**Current state:** ✅ Live.

**Dependencies:** Shield audit infrastructure, M.3 public mirror, ZZ.4 reasoning velocity panel.

---

### 5.15 Admin

**Purpose:** Superadmin surfaces for tenant management, cohort approvals, user CRUD, LLM spend monitoring, extraction activity, shield back-fill, etc.

**Surfaces:**
- `/app/admin/users` — User CRUD (`AdminUsers.jsx`).
- `/app/admin/tenants` — Multi-tenant org view (`AdminTenants.jsx`).
- `/app/admin/cohort` — Cohort console (`CohortConsole.jsx`).
- `/app/admin/cohort/applications` — Cohort application approvals.
- `/app/admin/inbox` — Admin inbox + unread count.
- `/app/admin/extractions` — Extractions activity.
- `/app/admin/llm-spend` — LLM cost monitoring per tenant.
- `/app/admin/shield-backfill` — Shield backfill admin (H4 phase).

**Underlying capability:** SuperadminRoute gate on every admin route (`SuperadminRoute.jsx`). Server-side superadmin enforcement on every data endpoint. Audit-logged actions.

**Current state:** ✅ Live across all surfaces.

**Dependencies:** Auth (superadmin claim in JWT), Admin routers (15+ files), Audit log.

---

### 5.16 Other Live Surfaces

- **Cycle Manager** (`/app/cycle`) — Multi-cycle master with state transitions. Cycle v2.
- **NED Cycle Manager** (`/app/ned-cycle`) — Non-Executive Director cycle workflow. Phase E.
- **Inbound Queue** (`/app/inbound-queue`) — Routes inbound contributor emails to the right context.
- **Briefings** — Pre-meeting briefings with cited intelligence.
- **Decks** — Slide-deck composer (`Decks.jsx` + `Decks` router).
- **Studio Composer** — Modular content blocks (`StudioComposerPage.jsx`).
- **Lens Room** — Coaching / discovery sessions (`LensRoom.jsx`).
- **Daily Review** — Daily summary digest (`DailyReview.jsx`).
- **InfluenceMap** — Org influence map (`InfluenceMap.jsx`).
- **Wiki / Learn / Help / News / Search** — knowledge + universal search.
- **Sandbox** — Generative sandbox for prompt experiments (Phase J).
- **Activity / Archived Chats** — User history surfaces.
- **Account Security** — Password change, MFA enrol, recovery codes.
- **Tenant Settings** — Per-tenant configuration.
- **Contributor Portal** — External contributor entry surface.
- **Pre-login Website** — `WebsiteHome.jsx` + marketing pages (Phase I1).
- **Status Page** — Composite health probe (`StatusPage.jsx`).
- **Throw Diagnostic** — Crash report surface.
- **Welcome Page** — Post-signup landing.
- **Invite Accept** — Invitation acceptance flow.

Every live surface has a `data-testid` discipline; every interactive element carries a unique kebab-case test ID for E2E reliability.

---

## 6 · User Journeys (end-to-end, narrative)

### 6.1 First-time user → first analyzed workbook

> **Persona:** Sarah, COO at a 200-person growth-stage retailer. Just signed up. Has a Q3 sales workbook on her desktop.

1. Lands at `/signup`, types email + name + org → submits.
2. Receives magic link email (SendGrid via TM3 pipeline). Clicks it.
3. Backend mints a session token; redirects to `/set-password` (SetPasswordGuard).
4. Sets a password → JWT issued, CSRF token minted → redirected to `/first-session`.
5. Sees three onboarding cards: "Create your first cycle", "Upload a Document", "Try the Demo".
6. Picks "Upload a Document" → routed to `/app/documents?upload=1` with the upload modal pre-opened.
7. Drags her Q3 sales workbook in → uploads → ClamAV scan passes → document lands.
8. Clicks the document → DocumentDrawer opens with intelligence-extraction running.
9. Notices the "Analyze" surface in the left nav → opens `/app/analyze`.
10. Mount-time guard backfills URL with `?context_id=` from her active context (BUG-ANL-001 fix).
11. Uploads the same workbook to Analyze.
12. File picker uses the BUG-ANL-002 fix (finally-block input clear) — no silent failure.
13. Workbook parses → autopicker selects (Month, Sales) as the strongest pair → forecast runs.
14. Solva v2 narration generates Bottom Line in McKinsey tone.
15. Sarah sees the Analyze Drawer with What changed / What's likely next / What's odd tabs, all cited.
16. Adds a note ("Need to follow up with marketing on the August dip") — autosaves with 1.0s debounce.
17. Result row appears in the Analyze Journal listing.

**Time elapsed:** ~3-5 minutes from signup to first cited insight.

**Shield interactions:** at least 3 Shield calls (intelligence extraction on the doc upload, signal extraction, Solva narration). Every call is audit-logged with a Trust Receipt.

---

### 6.2 Compile a Work Studio document end-to-end

> **Persona:** Marcus, Chief of Staff to a mid-cap CEO. Needs to compile the Q3 board paper from three source documents.

1. Marcus opens `/app/work-studio`.
2. Sees the Document Lifecycle empty-state copy: "Pick a source document or set of sources above" (W1 fix — was "below").
3. Clicks "Compile from sources" → picks three documents.
4. Picks artefact kind: **report**.
5. Picks output format: **DOCX**.
6. Adds instructions: "Q3 board paper. Bottom-line up front. Three substantive sections + risks + recommendation."
7. Clicks "Compile" → `LoadingChecklistModal` opens.
8. Modal shows step-by-step progression: "Reading sources… Drafting outline… Composing sections… Finalising…" with HOLD on Finalising while the LLM streams.
9. Behind the scenes:
   - `/work-studio/compilations/{id}/start` endpoint kicks off (W2 — idempotent).
   - SyniSense Shield de-identifies all three source documents + instructions.
   - Claude Sonnet 4.5 streams structured content.
   - Confidence Scorer runs (Phase 7) — 4-dim rubric, weighted average.
   - DOCX renderer composes the file (`services/work_studio_export.py`).
10. On completion, Marcus is auto-routed to `/app/documents?doc_id={continueDocId}` and the Document Review Drawer opens.
11. He sees the artefact in tiptap with `Edit` toggle live (Phase 6 ✅).
12. Toggles edit mode → "Inline edit on — autosaving every 30s" indicator (emerald).
13. Makes a few corrections — autosave belt fires every 30s.
14. Clicks "Revise with AI" → modal collects revise instructions → calls the existing enhance infrastructure.
15. Closes the drawer → save-on-close belt fires silently (Phase 6 Tightening 2).
16. Goes back to `/app/documents` → his new artefact is there with `Akki Generated` chip + confidence chip (Phase 7).
17. Confidence chip hover surfaces rationale: "Strong source coverage; gaps in market sizing acknowledged. recommendation_grounding = 88."
18. Commits the artefact → cache_key match means no re-score (Phase 7 Tightening 4 — saves ~$0.10).

**Time elapsed:** ~10-12 minutes including LLM wall-clock + reviewer time.

**Shield interactions:** 3 calls (compile + revise + commit-recompute, the last short-circuited by cache).

---

### 6.3 Send a shielded chat message and audit it

> **Persona:** Aisha, Risk Officer. Wants to validate Shield behaviour for her board.

1. Aisha opens `/app/chat`.
2. Types: "Customer Mary Anne with email mary.anne@example.com and card 4242 4242 4242 4242 is asking about the Lemasy Limited contract. Draft a reply."
3. Hits Send → SyniSense Shield runs:
   - Regex: detects email + credit card (Luhn-valid).
   - Tenant dictionary: detects "Lemasy Limited" (her tenant's org name).
   - spaCy NER: detects "Mary Anne" → PERSON.
   - Token map: `[[ENT_EMAIL_001]]`, `[[ENT_CREDIT_CARD_001]]`, `[[ENT_ORG_001]]`, `[[ENT_PERSON_001]]`.
4. Redacted prompt + Phase-14 fluency preamble sent to Claude.
5. Claude streams a reply mentioning `[[ENT_PERSON_001]]`, `[[ENT_ORG_001]]` — the StreamingReidentifier rehydrates these contextual tokens delta-by-delta as "Mary Anne" and "Lemasy Limited".
6. The credit card and email tokens are NOT rehydrated — the user sees `[PAYMENT_CARD_••••4242]` and `[EMAIL_REDACTED]` in the final reply.
7. Aisha clicks the "Trust" chip → audit panel opens.
8. Audit panel shows: tokens detected per class, exposure-reduction score (% of original chars replaced), dilution score (% of words tokenised), HMAC signature of the trust receipt.
9. Aisha verifies the signature: `synisense_trust_receipts` row → reconstructs canonical JSON → HMAC matches.
10. She exports a CSV of the last 30 days of audit rows from `/app/synisense-observability`.

**Time elapsed:** ~1 minute including the LLM round-trip.

**Shield interactions:** 1 call. Audit row + Trust Receipt persisted.

---

### 6.4 Convert a Q4Y question into a committed answer (≥3 surfaces)

> **Persona:** Tom, CEO. Reviewing his board pack last week, a question surfaced from the Project Lighthouse Q3 Brief: "What's the customer-acquisition assumption for the Madrid market?"

1. Tom opens `/app/questions` → sees the question as an Open card.
2. Clicks the card → side drawer opens with full question, status badge `Open`, related document as attachment (G13).
3. Clicks "Use in Solva" (G14) → routed to `/app/solva` with the question pre-populated.
4. Picks "Workbook + objective" Solva option → uploads his market-sizing workbook.
5. Solva runs Phases A-E → produces a polished claim chain with per-claim confidence weighting.
6. Each claim cites the source workbook cells.
7. Back in `/app/questions`, he opens the drawer again → clicks "Link response" → picks the Solva session he just ran → the drawer now shows the Solva session as a response link with date/time (G19).
8. Status stays `Open` (G20) — he hasn't confirmed it yet.
9. Reviews the response → satisfied → clicks "Mark as Answered" → status flips to `Answered`.
10. A week later he gets contradictory data from a contributor → opens the question → clicks "Reopen" (G21).
11. Status flips back to `Open`. The Solva session response link is preserved in history (G22).
12. Now he wants to commit the answer into his next board paper → opens `/app/work-studio` → "Compile from sources" → picks the Project Lighthouse brief + the Solva session export → compiles a minutes-style summary.
13. The new Work Studio artefact lands with citations back to both sources (Phase 5 ✅).

**Surfaces touched:** Q4Y, Solva, Work Studio, Documents, Trust Center (audit log).

**Time elapsed:** ~20-30 minutes over a week.

---

## 7 · Current State Snapshot (Live · In-Dev · Declined)

Status reflected verbatim from `/app/memory/MASTER_STATE.md` Section 8 (2026-06-05 02:15Z Phase 14 close).

### ✅ Live (14 phases + 3 bugs)
- **Track A:** Phase 1 (Foundation) · Phase 2 (Chrome) · Phase 3 (Solva v2 narration) · Phase 4 (Multi-workbook + Versioning) · Phase 5 (Work Studio Lifecycle) · Phase 6 (Inline edit + Revise + BC removal) · Phase 7 (Confidence Scoring Runtime) · **Phase 14 (Chat Fluency & Detection Hardening — closed 2026-06-05)**.
- **Track B:** Phase B1 (incl. B1b small mechanicals) · Phase B2 (Task Manager lifecycle) · Phase B3 (Questions feature wiring) · Phase B4 (cross-feature surfacing) · Phase B5 (Document workflow + Calendar polish).
- **Standalone bugs closed:** BUG-ANL-001 (Analyze route guard) · BUG-ANL-002 (Analyze upload silent-failure) · BUG-WS-001 (rag_band test spec).
- **TM3 ✅ unblocked 2026-06-04:** SendGrid Inbound Parse fully verified end-to-end.

### 🟡 In-progress / Pending verification
- **None active.** Agent is paused per orchestrator instruction pending the next user dispatch.

### ❌ Open
- Four ❌ items remain across the original 37 QA items (carried forward; no code change attempted).

### 🚧 User-blocked
- **G2 — Google OAuth credentials.** Waiting for user to provide GCP OAuth Client ID + Secret. Code path is wired (`routers/oauth_google.py` + `auth_oauth.py`), only credentials missing.
- **Prod env var: `COHORT_EMAILS_ENABLED=true`** — without this, cohort approval emails won't send in prod.
- **Prod env var: `POSTMARK_WEBHOOK_SECRET` decision** — keep env var OR remove boot-guard at `server.py:573`.

### 🛌 Declined / Backlog (paper trail only)
- `useFileInputResetOnInvoke` cross-cutting hook (BUG-ANL-002 follow-up).
- `data-testid` presence smoke test (Phase 6 close-out).
- Confidence chip on universal `/app/documents/{doc_id}` page (Phase 7 close-out).

All declined items have a paper trail in `MASTER_STATE.md` Section 5b and a "gold-plating" rationale (the user explicitly declined them as scope creep).

---

## 8 · Known Limitations & Honest Tech Debt (product-side)

### 8.1 Google OAuth not live
The Google OAuth code path is shipped (`routers/oauth_google.py`, `routers/auth_oauth.py`, `frontend/src/components/OAuthButtons.jsx`), but production cannot use it because the GCP credentials are not yet provisioned. **Mitigation:** email + password and magic-link login work. **Impact:** users expecting one-click Google sign-on currently land on the email form.

### 8.2 Microsoft OAuth is a mock
`auth_oauth.py` includes a Microsoft OAuth probe endpoint that returns a 200 OK for the probe but does not complete an actual Microsoft Identity Platform handshake. **Mitigation:** none. **Impact:** any marketing claim of "Microsoft OAuth" is unsupported. (We do not currently make this claim.)

### 8.3 Confidence chip not surfaced on universal Documents page
Phase 7 ships the confidence scorer + writes `documents.confidence_pct` as a mirror, but the universal `/app/documents/{doc_id}` page does not currently render the chip. The Work Studio overlay does. **Mitigation:** users see the chip when reviewing an artefact. **Impact:** users browsing the Documents library don't see at-a-glance confidence; they must open the drawer.

### 8.4 spaCy fallback model has lower NER F1
The Shield prefers `en_core_web_trf` (transformer model, ~F1 0.91) but falls back to `en_core_web_sm` (~F1 0.86) when spacy-transformers isn't installed. **Mitigation:** the regex layer + tenant dictionary catch the highest-stakes PII regardless of NER quality. Phase 14 added an ORG protector for the most common spaCy false positives (disease names, weekdays, months). **Impact:** ~5-percentage-point drop in PERSON / ORG recall vs. the transformer model. Not a security failure (regex + dictionary still cover hard PII); a quality smell.

### 8.5 Email magic link gated on prod env var
Magic link delivery requires `COHORT_EMAILS_ENABLED=true` in production. Without it, the platform creates the magic link record but does not send the email. **Mitigation:** documented in MASTER_STATE.md Section 5. **Impact:** prod env-var checklist needs to be set on deploy.

### 8.6 Collaborative editing not yet shipped
Phase 6 ships inline single-user editing. Real-time collaborative editing (OT / CRDT) is parked as P2 future work. **Mitigation:** save-on-close belt + last-write-wins. **Impact:** two reviewers editing the same artefact will trample each other.

### 8.7 PPTX structural editing limited
Phase 6's inline edit works on DOCX. PPTX is currently locked to read-only in the Document Review Drawer (`DocumentOverlay.jsx:680`). **Mitigation:** PPTX edits happen in PowerPoint and re-uploaded. **Impact:** in-app PPTX editing not available.

### 8.8 Inbound email mailbox-resolution rate-limited
The TM3 webhook resolves contributor mailboxes per hash. The current implementation is single-tenant-scoped and would need a more efficient lookup if Akki scales to >1000 tenants per region. **Mitigation:** current load is well within capacity. **Impact:** future infra work.

### 8.9 Tenant entity catalogue cache TTL
The Shield's tenant dictionary cache (`services/synisense/shield/tenant_entities.py`) reloads from Mongo on cache miss or after `SYNISENSE_SHIELD_MAP_TTL_HOURS` expiry. Phase 14 added a defensive belt against stale-cache survival, but a tenant adding a new entity may see up to TTL-duration delay before it's redacted. **Mitigation:** cache invalidation hook on `register()`. **Impact:** small lag window for new entities.

### 8.10 spaCy ORG part-of-speech check not yet shipped
Phase 14 added a 43-term protector list against common spaCy ORG false positives. A future POS-tag check (drop ORG when the token's POS is not PROPN) would be more principled but was descoped to keep Phase 14 small. **Mitigation:** protector list covers the observed leak classes. **Impact:** unobserved false positives may still get redacted.

### 8.11 Lint rot in routers/documents.py
The Documents router has accumulated mixed conventions (some Phase 5 fields don't carry through to the GET allow-list cleanly). Phase 5 iter-2 Fix A landed an extension. **Mitigation:** Phase 5 lockdowns pin the contract. **Impact:** future Documents extensions need a careful read of the projection allow-list to avoid the same regression class.

---

## 9 · Roadmap & Parked Items

### 9.1 P0 — must ship next (none currently active)
- Phase 14 user verification (chat fluency on `/app/chat`).
- Google OAuth (G2) — pending GCP creds.

### 9.2 P1 — high-confidence next phases
- Confidence chip on universal Documents page (~25 LOC FE-only delta, currently DECLINED as gold-plating).
- spaCy ORG POS-tag check (Phase 14 follow-up).
- Cohort waitlist email cadence.

### 9.3 P2 — backlog / parked
- Collaborative editing (OT / CRDT) for DOCX.
- PPTX structural editing in `DocumentOverlay.jsx`.
- Rich-media insertion (images / charts inline) in the editor.
- Pulse digest cadence + "why didn't this idea appear" diff view.
- Dedicated DOCX minutes template (current uses report template by default — Phase 5 iter-2 Fix C).
- `useFileInputResetOnInvoke` cross-cutting hook (BUG-ANL-002 follow-up).
- `data-testid` presence smoke test (CI-level discipline gate).

### 9.4 P3 — future infrastructure
- Multi-region SendGrid routing.
- Tenant entity catalogue real-time invalidation (vs. TTL polling).
- Distributed locking on Synisense Engine scheduler beyond single-replica.
- Stripe billing live (currently gated behind `BILLING_ENABLED`).

---

## 10 · Glossary

- **Akki / Syni** — operating brand of the platform. "Akki" is the conversational/product persona; "Syni" is the parent platform brand (SyniSense being the governance layer).
- **AKKI_ENV** — environment label. Recognised values: `production` (locks down boot guards), `preview` (default).
- **Anomaly Flag** — Synisense Engine signal class for unusual workbook patterns.
- **Audit Log** — `synisense_audit_log` collection. Every Shield call writes a row.
- **AutoPicker** — workbook column auto-selection logic in `services/workbook_analyzer/forecaster.autopick_forecast_columns`. Selects strongest (date, numeric) pair globally.
- **Bottom Line** — Solva v2 narration field surfaced on the Analyze Drawer.
- **BUG-ANL-001 / BUG-ANL-002 / BUG-WS-001** — closed bug identifiers from the user-surfaced bug log.
- **Brief / Report / Minutes / Deck** — Work Studio artefact kinds.
- **Citation Manifest** — list of source-document cell ranges or paragraph anchors that ground a generated artefact.
- **ClamAV** — antivirus daemon used for file-upload scanning. Production refuses to bypass.
- **Cohort** — the early-access user cohort. Cohort applications + invites + magic links.
- **Commission** — Task Manager state transition Draft → Active.
- **Confidence Pct** — 0-100 weighted average of the 4-dim rubric (Phase 7).
- **Context** — multi-tenant workspace scope. Every read/write is `account_id`-scoped; every `account_id` belongs to one `context_id`.
- **Continue Doc Id** — Work Studio lifecycle hop-4 identifier that points to the `documents` collection row of a compiled artefact.
- **CSRF** — Cross-Site Request Forgery. Mint endpoint `/api/csrf`. Allowlist excludes a few routes by design.
- **Cycle Manager** — multi-cycle workflow for board / leadership cadence. Cycle v2.
- **De-Id** — de-identification (the Shield pipeline).
- **Density Gate** — autopicker filter rejecting sparse columns (<30% non-null OR <6 absolute non-nulls).
- **Dilution Score** — % of words in the prompt that got tokenised. Trust receipt field.
- **Discipline Rails** — the methodology: R1 (Pre-Read) → R2 (Approval) → R3 (Phase Done) → R4 (≤10 tests) → R5 (Root-cause) → R6 (No side quests) → R7 (Antiforget continuity).
- **DOCX / PDF / PPTX** — output formats Work Studio supports.
- **Enhance** — Work Studio AI-driven artefact improvement pass.
- **Exposure Reduction Score** — % of chars in the prompt that got replaced. Trust receipt field.
- **First Session** — onboarding-card surface at `/first-session`.
- **Follow-Up Drafts** — Akki-drafted follow-up emails to contributors with pending submissions.
- **G1..G23 / O1..O9 / TM1..TM5** — QA-doc item identifiers (Onboarding / Task Manager / Google login / Doc reader / Calendar QA docs).
- **Grounding Contract** — Solva v2 constraint that LLM responses must cite source paragraphs.
- **Hard PII** — PII classes that stay redacted in the user-visible reply: CREDIT_CARD, ACCOUNT_NUM, SSN, IBAN, PHONE_E164, UK_NI_NUMBER, API_KEY, EMAIL, IP.
- **HMAC** — keyed-hash authentication used for Trust Receipt signatures.
- **HKDF** — Key Derivation Function used to derive tenant-scoped HMAC keys from `SYNISENSE_MASTER_SECRET`.
- **Idempotency Gate** — Phase 7 cache_key (SHA-256 of structured_content) used to skip duplicate confidence recomputes.
- **Inbound Email** — SendGrid Inbound Parse webhook for contributor email replies.
- **Intelligence Report** — `work_studio_exports.intelligence_report` JSON shape holding `confidence_pct`, `rationale`, `breakdown`.
- **Lockdown Test Set** — ≤10 deterministic tests per phase. Real-LLM tests are `@pytest.mark.integration`.
- **MASTER_STATE.md** — the canonical state ledger. Read first every dispatch.
- **Notes History** — append-only notes log on Analyses + Documents.
- **Notes Updated At** — ISO timestamp set on the notes-bearing PATCH only (not on category PATCH).
- **Pulse Ideas / Pulse Signals** — weekly ideas-engine synthesis vs. raw signal feed.
- **Purpose** — Shield call classification: `chat`, `documents.events_extract`, `work_studio.document.confidence_score`, etc. Drives purpose-gated exclusions.
- **Q4Y** — Questions For You. Question-extraction surface.
- **R²** — coefficient of determination in the forecaster. Below 0.30 → low-signal flag.
- **Recipient Emails** — share recipients list (max 10) on a document share.
- **Re-Identify** — token → original substitution on the response path.
- **RAG Band** — confidence-pct bucket: green ≥75, amber 50-74, red <50 (Phase 5 spec; Phase 4 used 80-spec).
- **Refuse to Decide** — Solva v2 pattern where the engine surfaces "insufficient input" rather than fabricating an answer.
- **Revise with AI** — Work Studio Phase 6 enhance-on-demand panel.
- **Run Snapshot** — Append-only entry in `analyses.runs[]` (Phase 4).
- **Save-on-Close Belt** — Phase 6 Tightening 2 — async save fires when the drawer closes, even silently.
- **Shield** — SyniSense's redaction + audit pipeline. `services/synisense/shield/`.
- **shield_invoke** — the single canonical Shield call entrypoint. Every LLM call uses it.
- **Solva v2** — the reasoning engine. `services/solva_v2/`.
- **SOURCE FILES roster** — multi-workbook prompt block listing every source by stem.
- **Stale-Cache Survival** — Phase 14 defensive belt against pre-Phase-14 cache entries.
- **Streaming Reidentifier** — stateful per-stream token rehydrator (`reidentifier.StreamingReidentifier`).
- **SyniSense Engine** — the signal-derivation cron (`services/synisense/engine/`). Hourly Mongo-locked.
- **Synisense Observability** — admin dashboard for Shield metrics.
- **System Msg** — caller-provided LLM system prompt (Phase 14 — added as optional `shield_invoke` kwarg).
- **Tenant Dictionary** — per-tenant entity catalogue harvested from Mongo collections.
- **Three-Layer De-Id** — regex → tenant_dict → spaCy NER.
- **Tightening** — user-approved hardening of a Pre-Read scope. Numbered per phase (e.g. "Phase 7 T4").
- **Token Map** — per-request `{token: original_value}` map. Lives only in memory.
- **Trust Center** — `/trust` public transparency page.
- **Trust Receipt** — HMAC-signed proof-of-redaction per Shield call.
- **Universal Document Page** — `/app/documents/{doc_id}` surface.
- **Voice Lint** — copy/tone enforcement layer (no glazing, no hedging, no weasel words).
- **W1..W6** — Phase 5 scope deliverables.
- **Work Studio** — the document-lifecycle surface.

---

## 11 · Appendix — ASCII journey diagrams

### 11.1 Onboarding → first analyzed workbook

```
  ┌──────────┐  signup     ┌──────────┐  magic link   ┌──────────────┐
  │  signup  │ ───────────▶│ email out│ ─────────────▶│ set password │
  └──────────┘             └──────────┘               └──────┬───────┘
                                                             │
                                                             ▼
                                                   ┌───────────────────┐
                                                   │  /first-session   │
                                                   └──────┬────────────┘
                                                          │
                          ┌───────────────────────────────┼───────────────────────────┐
                          │                               │                           │
                          ▼                               ▼                           ▼
              ┌──────────────────┐         ┌──────────────────────┐       ┌────────────────────┐
              │ /app/task-manager│         │/app/documents?upload=1│       │  /app  (AppHome)   │
              └──────────────────┘         └────────────┬─────────┘       └────────────────────┘
                                                        │
                                                        ▼
                                                ┌─────────────────┐
                                                │  upload file    │
                                                └────────┬────────┘
                                                         ▼
                                                ┌─────────────────┐
                                                │  /app/analyze   │  ─── BUG-ANL-001 guard ─▶ backfill ?context_id=
                                                └────────┬────────┘
                                                         ▼
                                                ┌─────────────────┐
                                                │ synthesize_v2   │
                                                └────────┬────────┘
                                                         ▼
                                                ┌─────────────────┐
                                                │  AnalyzeDrawer  │
                                                └─────────────────┘
```

### 11.2 Shield round-trip (chat)

```
user prompt
    │
    ▼
┌─────────────────────────────────────────────┐
│ services/synisense/shield/client.invoke()   │
│                                             │
│   ┌────────────┐   ┌────────────┐   ┌─────┐ │
│   │  regex     │ → │ tenant_dict│ → │spaCy│ │   ← three-layer deidentify
│   └────────────┘   └────────────┘   └─────┘ │
│              │                              │
│              ▼ token map                    │
│   ┌────────────────────────┐                │
│   │  redacted_text         │                │
│   └─────────┬──────────────┘                │
└─────────────┼───────────────────────────────┘
              │
              ▼
       Claude Sonnet 4.5
              │  (sees only redacted_text + system_msg)
              ▼
     ┌────────────────────────┐
     │ raw LLM response       │
     └─────────┬──────────────┘
               │
               ▼
┌─────────────────────────────────────────────┐
│ reidentifier.reidentify() / Streaming       │
│                                             │
│   contextual classes   → rehydrate          │
│   hard PII classes     → keep redacted      │
│                          (e.g. [PAYMENT_CARD_••••4242])
└─────────────────────────────────────────────┘
               │
               ▼
   ┌──────────────────────────┐
   │ user-visible reply       │
   │ + trust receipt (HMAC)   │
   │ + audit row              │
   └──────────────────────────┘
```

### 11.3 Work Studio lifecycle (Phase 5 + 6 + 7)

```
   sources
      │
      ▼
┌─────────────┐
│ CreateModal │ ─── kind: report/brief/minutes/deck/blank
└──────┬──────┘
       ▼
┌──────────────────┐
│ LoadingChecklist │ ── status: pending → in_progress → complete
└──────┬───────────┘
       ▼
┌─────────────────────┐     ┌───────────────────────┐
│ shield_invoke()     │  →  │ structured_content    │
│  (compile)          │     │ + citations_manifest  │
└─────────────────────┘     └──────┬────────────────┘
                                   ▼
                          ┌──────────────────────┐
                          │ Confidence Scorer    │  ── 4 dim × weighted
                          │ (Phase 7)            │
                          └──────┬───────────────┘
                                 ▼
                          ┌──────────────────┐
                          │ intelligence_    │
                          │ report.          │
                          │ confidence_pct   │
                          └──────┬───────────┘
                                 ▼
                          ┌──────────────────┐
                          │ status=complete  │
                          └──────┬───────────┘
                                 ▼
                ┌───────────────────────────────┐
                │ DocumentOverlay (Phase 6)     │
                │  · tiptap inline edit         │
                │  · Revise with AI             │
                │  · save-on-close belt         │
                └────────┬──────────────────────┘
                         ▼
                ┌──────────────────┐
                │ commit_document  │
                │  · cache_key gate│  ── (Phase 7 T4)
                │  · recompute pct │
                │  · status=       │
                │    committed     │
                └────────┬─────────┘
                         ▼
                ┌─────────────────┐
                │ /app/documents/ │
                │ {doc_id}        │
                └─────────────────┘
```

---

*End of PRODUCT.md.*
