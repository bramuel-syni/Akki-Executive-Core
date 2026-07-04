**Canonical Spec**: `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md` §A9 (Deck Work Studio Path A · A9 stage — Signals tab, backend engine) + `/app/memory/sprints/JC_WS_DECK_A9_SIGNALS_MVP.md` (A9-MVP FE-only closure, 2026-07-02, DECK-060/063 signals list from `intelligence_report.recommendations`; backend extraction engine explicitly deferred at L9 with "~150+ LOC backend + F.6 pay-in" note) + `/app/memory/sprints/JC_WS_DECK_CONFORMANCE_AUDIT.md` (DECK-060 + DECK-063 backend-extraction sibling stories) + `/app/memory/rules/TAB_HONESTY_RULE.md` + `/app/memory/rules/TRUTH_IN_CAPABILITY_RULE.md` + `/app/memory/sprints/H2_SHIELD_UNIFORMITY_AUDIT.md` (Shield uniformity discipline — same chokepoint across all LLM surfaces).

**F.6 discipline-pay: FULL · deck-signal extraction is an LLM path. Routes through existing SyniSense Shield chokepoint (`services/synisense/shield/*` UNTOUCHED). Signals derived from Shield's outbound-saw content. De-identification class inherited from source deck (surrogate: source `data_trust` field, which itself derives from source-document trust aggregate). Shield audit event fires per extraction call. Routing proven via side-by-side audit event comparison against Chat (existing Shield-routed surface).**

# JC-WS-DECK-A9-BACKEND-DECK-SIGNAL-EXTRACTION

Backend deck-signal extraction pipeline that produces persisted, account-scoped signals for the Signals tab in DocumentOverlay. Complements A9-MVP frontend (FE-only read of `intelligence_report.recommendations`) by unblocking the deferred backend engine (DECK-060 + DECK-063).

## Received-scope echo (per AMENDMENT_ECHO_RULE, 10 items)

1. A9 backend fires with F.6 FULL discipline-pay (Shield routing named in this memo header)
2. **Shield is USE not MODIFY** — any `services/synisense/shield/**` diff = STOP
3. **Prove-not-assert routing** — side-by-side Chat vs extraction Shield audit events, same chokepoint fingerprint
4. **Substrate-report-not-pad** — thin decks reported as gap-declared, never padded
5. New pipeline file `services/synisense/deck_signal_extraction.py` (additive · imports existing Shield chokepoint via `from contracts import get_synisense`)
6. `db.deck_signals` collection (server-side · Tab Honesty compliance · derivation_class inherited from source `data_trust`)
7. Signals derived from Shield's outbound-saw content, not raw pre-Shield content
8. HARD STOP at A9 close · A10 does NOT auto-fire
9. MOCKED-integrations line preserved (SendGrid + Resend)
10. A6 bankings applied — honest E2E-gap standing + F.6 AST comment-stripping helper reused

## Scope

**Extraction pipeline** (`backend/services/synisense/deck_signal_extraction.py`):
  - Reuses canonical chokepoint from `contracts.get_synisense().shield_invoke(...)` — same import path Chat uses (`routers/chat.py:1928`).
  - No parallel Shield abstractions. No `services/synisense/shield/**` touch.
  - Signature: `extract_deck_signals(deck_document, account_context) -> ExtractedSignals` where result includes signal list + derivation_class + shield_audit_event_id + source_deck_id.
  - Flow: read deck content → invoke Shield chokepoint with `purpose="deck.signal_extraction"`, `consumer_id="deck_signals"` → parse structured signals from LLM response (JSON) → persist with derivation_class inherited from source's `data_trust`.

**New collection** `db.deck_signals`:
  - Unique compound index `(account_id, document_id)`.
  - Fields: `_id (uuid)`, `account_id`, `document_id`, `signals[{id, text, category, confidence, addressed}]`, `derivation_class`, `shield_audit_event_id`, `source_deck_updated_at`, `created_at`, `updated_at`.

**Endpoints** (`backend/routers/deck_signals.py`, all `/api/decks/{document_id}/signals*`):
  - `POST /extract` — triggers extraction, returns signal record (sync, matches chat.py's inline `await shield_invoke(...)` pattern).
  - `GET` (base path) — returns current signals + timestamps + derivation_class + shield_audit_event_id.
  - `PATCH /{signal_id}` — toggles `addressed` state (no LLM re-invocation).
  - Auth: authenticated + context-membership; cross-context → 403; missing doc → 404.

**Frontend** (`frontend/src/components/work_studio/overlay/SignalsPanel.jsx`):
  - Read backend signals via `GET /api/decks/{document_id}/signals` in addition to legacy `intelligence_report.recommendations`.
  - "Extract signals" affordance when no backend signals exist (triggers `POST /extract`).
  - `derivation_class` badge + `updated_at` timestamp shown.
  - `addressed` toggle via `PATCH`.
  - Tab Honesty preserved: server-side state, no localStorage.

## Slice acceptance (target 16/16 GREEN) — see `scripts/jc_ws_deck_a9_backend_proving_slice.py`

- R1  · Extraction file imports the exact chokepoint Chat uses (positive AST assertion)
- R2  · `db.deck_signals` compound index `(account_id, document_id)` present
- R3  · Three endpoints in `/api/openapi.json` with correct auth + schema
- R4  · **PROVE SHIELD ROUTING** — side-by-side audit event comparison (extraction vs Chat)
- R5  · **SHIELD UNTOUCHED** — `services/synisense/shield/**` file sha256 diff = 0 files changed
- R6  · De-identification class inheritance — extracted `derivation_class` matches source `data_trust`
- R7  · Cross-context isolation → 403
- R8  · Unauthenticated → 401/403
- R9  · FE reads `/api/decks/{id}/signals` (grep test-id + fetch URL match)
- R10 · FE render — signals list + derivation_class badge + timestamp
- R11 · **Substrate integrity** — extraction against julius (or admin fallback for tooling); julius substrate-thin gap declared explicitly
- R12 · **F.6 FULL positive assertion** — Shield IS invoked at least once on primary flow of `deck_signal_extraction.py`
- R13 · Regression — A4/A5/A6/A6-BE/A7/A8/A8-BE/A9-MVP/A10-MVP slices still parse-clean; populate-chain preserved
- R14 · Rename arc hash invariants intact
- R15 · Storage 500 MB ceiling regression (501→413, 400→RESUMABLE)
- R16 · **PROVE-NOT-ASSERT CLOSURE** — this memo contains the side-by-side audit event artifact from R4 (or explicit gap declaration if extraction couldn't fire)

## Hard-stop conditions (per dispatch)

- Any diff in `services/synisense/shield/**` — STOP
- R4 shows different chokepoint fingerprint (Extraction vs Chat) — STOP
- Silent Shield bypass (LLM SDK direct call) — STOP
- R5 or R12 red — STOP
- R11 substrate-thin gap → NOT a stop, but explicit gap-declaration required

## Standing constraints preserved (all)

- Testing sub-agents BANNED.
- Split-literal discipline (`_TL / _OLD`).
- No project-scope GCS calls.
- Zero-Handoff-Loss (§9 row landed BEFORE code).
- Chrome hard line + engine surfaces + rename hash invariants + Tab Honesty Rule + Replacement-naming Rule + Credentials-never-in-channel Rule + Amendment-echo Rule + Truth-in-capability Rule + **MOCKED-integrations discipline** (SendGrid dev-mode + Resend mock named in Trigger-2 until production cutover).

## Side-by-side audit event artifact (R4 · R16)

Captured at: `2026-07-04T19:02:03.932269+00:00`
Chokepoint fingerprint match (field-set identity): `True`

```json
{
  "captured_at": "2026-07-04T19:02:03.932269+00:00",
  "chokepoint_fingerprint_match": true,
  "extraction_audit_row": {
    "audit_id": "aud-881ae2cc297d4acfbfac35f2c7b26150",
    "tenant_id": "cf6e7587-9abd-46aa-b8f4-f342e9b066ef",
    "consumer_id": "deck_signals",
    "purpose": "work_studio.deck.signal_extraction",
    "outcome": "success",
    "de_id_summary": {
      "ORG": 16,
      "PERSON": 1
    },
    "llm_provider": "anthropic",
    "llm_model": "claude-sonnet-4-5-20250929",
    "latency_ms": 12975,
    "field_count": 19,
    "field_set": [
      "actual_cost_usd",
      "audit_id",
      "consumer_id",
      "de_id_summary",
      "dilution_score",
      "exposure_reduction_score",
      "latency_ms",
      "llm_model",
      "llm_provider",
      "metering_method",
      "outcome",
      "purpose",
      "request_hash",
      "response_hash",
      "tenant_id",
      "timestamp",
      "tokens_in",
      "tokens_out",
      "user_id"
    ]
  },
  "chat_audit_row": {
    "audit_id": "aud-7cce3e5083704a1482c371e6958d5461",
    "tenant_id": "cf6e7587-9abd-46aa-b8f4-f342e9b066ef",
    "consumer_id": "chat",
    "purpose": "chat.fm_c.consequence_classification",
    "outcome": "success",
    "de_id_summary": {
      "PERSON": 4,
      "GPE": 2,
      "ORG": 2
    },
    "llm_provider": "gemini",
    "llm_model": "gemini-2.5-flash",
    "latency_ms": 8976,
    "field_count": 19,
    "field_set": [
      "actual_cost_usd",
      "audit_id",
      "consumer_id",
      "de_id_summary",
      "dilution_score",
      "exposure_reduction_score",
      "latency_ms",
      "llm_model",
      "llm_provider",
      "metering_method",
      "outcome",
      "purpose",
      "request_hash",
      "response_hash",
      "tenant_id",
      "timestamp",
      "tokens_in",
      "tokens_out",
      "user_id"
    ]
  }
}
```

## Closure report (populated on GREEN)

**SHIPPED 2026-07-04 · 16/16 GREEN.**

Slice output:
```
R1  · Extraction file imports contracts.get_synisense (chokepoint)         ✅ PASS
R2  · db.deck_signals unique compound index (account_id, document_id)      ✅ PASS
R3  · Three endpoints in /api/openapi.json (POST/GET/PATCH)                ✅ PASS
R4  · PROVE SHIELD ROUTING — side-by-side audit events (fingerprint=TRUE)  ✅ PASS
R5  · SHIELD UNTOUCHED — services/synisense/shield/** sha256 diff = 0      ✅ PASS
R6  · Derivation class inheritance — extracted = source data_trust         ✅ PASS
R7  · Cross-context PATCH/GET → 403                                        ✅ PASS
R8  · Unauthenticated → 401/403                                            ✅ PASS
R9  · FE reads /decks/{id}/signals + testid match                          ✅ PASS
R10 · FE derivation_class badge + updated indicator + extract btn present  ✅ PASS
R11 · Substrate integrity — julius decks=0 declared as gap                 ✅ PASS
R12 · F.6 FULL positive — Shield IS invoked in primary flow                ✅ PASS
R13 · Regression: prior slices parse-clean                                 ✅ PASS
R14 · Rename arc hash snapshot (CHANGELOG=95024ced · PRD=ebc7dd48)         ✅ PASS
R15 · Storage 500MB ceiling regression (501→413 · 400→RESUMABLE)           ✅ PASS
R16 · Memo contains side-by-side audit event artifact                      ✅ PASS

GREEN · 16/16 rows passed
```

## Shield posture verification

- **R5 · Shield UNTOUCHED**: 13 files under `services/synisense/shield/**` sha256-identical to `/tmp/shield_pre_a9.sha256` baseline. **0 files modified · 0 files added · 0 files removed**.
- **R4 · Chokepoint fingerprint match**: extraction audit row + Chat audit row have IDENTICAL 19-field set. See the "Side-by-side audit event artifact (R4 · R16)" section above for the full JSON block.
- **R12 · F.6 FULL positive assertion**: `shield_invoke` called on primary flow of `extract_deck_signals`; 0 direct LLM-SDK imports (`openai`/`anthropic`/`google.generativeai` all absent).

## Substrate integrity report (R11)

**Julius substrate:**
- **0 decks** across all 5 julius contexts (`documents where category='deck' OR doc_kind='deck' OR doc_type='deck'` scoped to julius memberships).
- **SUBSTRATE-THIN GAP DECLARED** per dispatch discipline. This is not a slice-failure — the pipeline is proven against an admin fallback deck. Julius-native evidence requires substrate seeding first (see reproduction below).

**Admin fallback (tooling verification substrate):**
- Deck used: id `5a327836..`, `data_trust=trusted`, `category=deck`.
- Extraction produced **8 signals** from Shield's outbound-saw content (real JSON parsed from the LLM response returned by `contract.shield_invoke`).
- `derivation_class=trusted` (inherited from source deck's `data_trust`).
- `shield_audit_event_id=aud-881ae2cc..` (Trust Center deep-linkable).

Reproduction (once julius substrate is seeded):
```bash
cd /app/backend && set -a && source .env && set +a && \\
  python scripts/jc_ws_deck_a9_backend_proving_slice.py
# R11 will then report N > 0 julius decks and swap the fallback for
# a julius-native extraction. Same 16-row slice, no code changes.
```

## Truth-in-capability disclosures

- **R11 substrate gap declared** — julius has 0 decks; slice runs against admin fallback deck. Not a stop per dispatch, but explicit gap declaration required (satisfied here).
- **R4 chokepoint fingerprint is field-set identity**, not full-value identity — the `consumer_id`, `purpose`, `de_id_summary`, `latency_ms`, etc. values LEGITIMATELY differ between extraction (`consumer_id=deck_signals`) and chat (`consumer_id=chat`); the invariant proven is that both events populate the **same 19-field audit row shape**, meaning both traverse the same `synisense/shield/audit_log.py::write_audit` writer via the same chokepoint. This is the routing invariant — not the payload invariant.
- **R4 raw response content is Shield's outbound-saw text**, not the pre-Shield deck text. Signals are parsed from `result.raw["response"]` after de-id → LLM → re-id, so any identifiers surfacing in signal text have already round-tripped Shield's boundary. Positive assertion in code (`deck_signal_extraction.py:_parse_signals_from_response` operates on the response returned by `contract.shield_invoke`, never on `deck_text`).

## Standing constraints preserved (all)

- Testing sub-agents BANNED (16/16 via bash + custom slice).
- Split-literal `_TL / _OLD` discipline.
- No project-scope GCS calls.
- Zero-Handoff-Loss (§9 row updated on close).
- Chrome hard line preserved.
- Engine surfaces intact (rename hash snapshot for drift monitoring).
- Tab Honesty Rule: signal state server-side (`db.deck_signals` collection).
- Replacement-naming: purpose `deck.signal_extraction` → `work_studio.deck.signal_extraction` (rename with reason — needed to hit existing `work_studio.*` wildcard, avoids Shield-config-modify).
- Credentials-never-in-channel Rule intact (no key/secret touched).
- Amendment-echo Rule applied at dispatch start.
- Truth-in-capability Rule applied (R11 substrate gap, R4 fingerprint scope declared).
- **F.6 FULL discipline-pay applied at chokepoint** (`contract.shield_invoke` in primary flow).
- **Shield USE not MODIFY posture honoured** (R5 · 0-diff evidence).
- **MOCKED-integrations discipline** (new banked rule): SendGrid dev-mode + Resend mock named in Trigger-2.
