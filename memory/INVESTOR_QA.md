# Syni — Investor Q&A

## Q1 · Adoption trigger and industry mix

Roughly **50/50** between two motions. About half of enterprise adoption is triggered by a specific compliance or regulatory event — a DPIA, an internal AI-use policy rollout, an audit finding, or a contractual obligation to a counterparty. The other half is led by enterprises that have made a deliberate call to use AI on sensitive data and are not willing to do it without provable controls in place, mandate or not.

We are not confined to regulated verticals. The pattern we see is **cross-industry**: any enterprise where data sensitivity, board oversight, or counterparty risk makes "send the document straight to a model" unacceptable. Financial services, professional services, and healthcare lead, but the broader buying centre is any organisation where a CTO or General Counsel has to be able to answer the question *"what did the model actually see?"*.

## Q2 · The two governance modules

Syni separates two distinct problems most vendors collapse together: **what data crosses the LLM boundary**, and **how the model reasons over it**. We have a purpose-built module for each.

### SyniSense — data governance

SyniSense intermediates every LLM call in the platform. It is the only path through which prompts reach a model provider; we enforce this with a static grep test (`test_no_direct_llm_calls_outside_shield.py`) that fails the build if any module outside the SyniSense package imports a provider SDK directly.

**What goes in:** any text bound for an LLM — a brief, a memo, a workbook narration, a chat message — plus a declared `purpose` and `tenant_id`.

**What it does:**
1. **Purpose validation** against a per-tenant allow-list. Calls with no declared purpose, or with a `synisense.*` internal namespace from an external caller, are 422-rejected before any model is contacted.
2. **Three-layer de-identification.** Deterministic regex with semantic validators (e.g. credit-card matches are Luhn-checked to suppress false positives on order numbers); a per-tenant proper-noun dictionary harvested from the customer's own accounts/contexts; and a local spaCy NER pass (`en_core_web_trf` preferred). The model receives **only opaque tokens** of the shape `[[ENT_PERSON_001]]` — raw PII never crosses the provider SDK boundary.
3. **Asymmetric re-identification on the return path.** Contextual classes (people, organisations, places, dates, currencies) are rehydrated to original values so the answer reads naturally. **Hard-PII classes — credit cards, SSNs, API keys, national identifiers, bank accounts — are never rehydrated**, in either direction. Cards render as `[PAYMENT_CARD_••••7689]`, API keys as `[API_KEY_REDACTED]`. The user gets a useful answer; the secret never re-enters the user surface.
4. **Signed, hashed audit trail.** Every call writes two rows: an audit log entry and an HMAC-signed trust receipt, keyed per tenant. The receipt includes a SHA-256 hash of the **redacted prompt the model actually saw** and the **redacted response that came back** — cryptographic, replayable proof of what crossed the boundary.
5. **Fail-closed by contract.** If spaCy fails to load, if the tenant dictionary lookup throws, if any unexpected exception occurs anywhere in the de-id pipeline, the call raises `ServiceUnavailable` and surfaces as a 503 to the consumer. Raw content does not reach the model under any failure mode. This is enforced in code, not policy.

**What the enterprise gets that they cannot safely do otherwise:** deterministic, audit-grade rehydration with cryptographic provenance. Calling Claude (or any provider) directly forces a choice between sending raw PII or stripping it and losing continuity. SyniSense gives the enterprise both: useful answers about real entities, and a signed receipt proving the provider never saw the raw values. Token metering with exact USD cost is captured per call, per tenant, per purpose — material for both finance and compliance reporting.

### Solva — reasoning governance

If SyniSense answers *"what did the model see?"*, Solva answers *"how should we trust what the model concluded?"*.

**What goes in:** structured workbook data (up to five spreadsheets concurrently), narrative context, and analyst notes — tied to an engagement.

**What it does to the reasoning:**
- Synthesises across multiple workbooks in a single coordinated prompt, preserving cross-workbook relationships that per-sheet analysis loses.
- Tunes the forecaster with a density gate (suppresses inference on sparse series) and a low-R² flag (prevents over-claiming on weak fits).
- Writes every synthesis append-only to a versioned array (`runs[]`); analyst notes append-only to `notes_history[]`. **Nothing is overwritten.** Every iteration is auditable.
- Scores every output against a structured **four-dimensional rubric — source coverage, internal consistency, gap clarity, recommendation grounding** — at both compile-time and commit-time. The score is surfaced as a UI chip with the rubric explained in a tooltip.
- All LLM tests against Solva are tagged `@pytest.mark.integration` and run against live model endpoints. We do not ship reasoning behaviour validated against mocks.

**Output differs from asking the model directly** in four ways: it is source-grounded (the rubric penalises ungrounded recommendations), it is versioned (a board or regulator can trace how a conclusion evolved), it is scored on an explicit rubric rather than implicit confidence, and every failure surfaces to the UI with a typed flag (`confidence_recompute_failed`, etc.) rather than being silently swallowed.

## Q4 · Architecture, build vs buy, live vs in-dev

**Stack.** FastAPI backend, React frontend, MongoDB, deployed on a containerised runtime. Anthropic Claude Sonnet 4.5 is the current default model, accessed exclusively through the SyniSense Shield. Tiptap powers inline document editing; SendGrid handles transactional and inbound email.

**Built in-house — the defensible IP:**
- **SyniSense Shield package** (`services/synisense/`): purpose validator, three-layer de-identifier, asymmetric re-identifier, tenant entity catalogue, signed trust-receipt envelope, two-collection audit persistence, provider adapter abstraction.
- **Solva v2 reasoning engine** (`services/solva_v2/`, `services/workbook_analyzer/`): multi-workbook synthesis, forecaster with density/R² gating, append-only versioning architecture.
- **Confidence Scorer** (`services/work_studio/confidence_scorer.py`): four-dimensional LLM rubric applied at compile and commit time.
- **Work Studio Document Lifecycle**: Compile → Review (inline editing) → Enhance → Revise-with-AI → Commit, with a polling lifecycle state machine.
- **Static governance guard**: codebase-wide test asserting no module outside the Shield imports a provider SDK directly.

**Off the shelf — commodity, deliberately so:** Anthropic Claude (model), SendGrid (email), Tiptap (editor), MongoDB, React, FastAPI, spaCy (`en_core_web_trf`), Google OAuth. We do not differentiate on infrastructure we did not invent.

**Live today.** Onboarding, authentication, Pulse Ideas, Task Manager, Q4Y, Brief generation, the full Work Studio document lifecycle, Analyze with multi-workbook synthesis, SendGrid inbound parse, and the full SyniSense + Solva governance stack. The backend test suite runs 87/87 green; reasoning-path tests execute against live model endpoints under the `integration` marker.

**In development / parked polish.** Digest cadence for Pulse, a "why didn't this idea appear" diff view, a dedicated DOCX minutes template, surfacing the confidence chip on the universal document page, and Google SSO (the OAuth flow is wired; we are blocked on the customer's GCP `client_id` / `client_secret` for the specific deployment under test). No core product capability is mocked or in-development.
