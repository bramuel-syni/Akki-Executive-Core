**Canonical Spec**: `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md` §A10 + `/app/memory/sprints/JC_WS_DECK_A10_RELATED_DOCS_MVP.md` (MVP FE-only, 2026-07-02, DECK-066 closed; DECK-064/065/067/084-087 explicitly deferred at L9-16 with "~200+ LOC backend + potential F.6" note) + `/app/memory/sprints/JC_WS_DECK_CONFORMANCE_AUDIT.md` (DECK-064/065/067/084-087 backend engine + regenerate sibling stories) + `/app/memory/rules/TAB_HONESTY_RULE.md` + `/app/memory/rules/TRUTH_IN_CAPABILITY_RULE.md` + `/app/memory/sprints/JC_WS_DECK_A9_BACKEND_DECK_SIGNAL_EXTRACTION.md` (A9 Shield-routing pattern reused for regenerate).

**F.6 discipline-pay: PARTIAL. Per-surface classifications named explicitly (banked per dispatch):**
- **`deck_retrieval.py`** · F.6 N/A · metadata queries only, no LLM path, no Shield routing required.
- **`deck_lineage.py`** · F.6 N/A · graph traversal only, no LLM path, no Shield routing required.
- **`deck_similarity`** (folded into `deck_retrieval.py`) · F.6 N/A · metadata scoring only (BM25-style over titles/tags/`source_document_ids` overlap); NO embedding computation at query time (would be an LLM path).
- **`deck_regenerate.py`** · **F.6 SHIELD-ROUTED** · regeneration invokes `contracts.get_synisense.shield_invoke` (same canonical chokepoint as Chat and A9 extraction). Shield audit event fires per regenerate call. `services/synisense/shield/**` UNTOUCHED (R10 asserts 0-diff). Regenerate audit fingerprint matches A9 extraction fingerprint (R9 side-by-side).

# JC-WS-DECK-A10-BACKEND-RETRIEVAL-LINEAGE-REGENERATE

Backend retrieval + lineage + regenerate engine that closes Deck Path A. Complements A10-MVP frontend (`RelatedDocuments.jsx` FE-only read of `source_document_ids` shipped 2026-07-02) by unblocking DECK-064/065/067/084-087.

## Received-scope echo (per AMENDMENT_ECHO_RULE, 10 items)

1. A10 backend fires with F.6 PARTIAL · per-surface classifications named (retrieval/lineage/similarity N/A · regenerate Shield-routed)
2. Regenerate honours commit-lock · same shape 409 as compile bridge (byte-identical envelope `{code, message}` + status 409)
3. Non-committed regenerate → new version in Draft state · prior versions PRESERVED (never mutated / never deleted)
4. Regenerate Shield-routed per A9 pattern · Shield UNTOUCHED (R10 · sha256 diff = 0) · audit fingerprint side-by-side with A9 extraction (R9)
5. Retrieval/lineage/similarity account-scoped · cross-account leak → STOP (R3/R4/R5 assert isolation)
6. New services: `deck_retrieval.py` (retrieval + similarity fold) · `deck_lineage.py` · `deck_regenerate.py`
7. Regenerate reuses A9's canonical Shield chokepoint (`contracts.get_synisense`) — no parallel abstraction
8. HARD STOP at A10 close · nothing auto-fires
9. MOCKED-integrations line preserved (SendGrid dev-mode + Resend mock)
10. A6+A9 bankings applied — honest E2E-gap standing + F.6 AST comment-stripping helper reused + prove-routing-not-assert extended

## Scope

**Endpoints** (all under `/api/decks/{document_id}/*`):
- `GET /related`   — account-scoped ranked related decks · F.6 N/A
- `GET /lineage`   — account-scoped ancestors + descendants + siblings graph · F.6 N/A
- `POST /regenerate` — account-scoped · **F.6 SHIELD-ROUTED** · body `{prompt?: str}` optional override. If committed → 409 `{code: "deck_already_committed", message: ...}` (compile-bridge-shape 409). Else → 200 with new document record (draft state, incremented `version_number`, `regenerated_from` link).

**Version-chain schema** (additive on `documents`):
- `version_number: int` (default 1 · backward-compat for existing rows).
- `regenerated_from: str | null` (previous version's doc_id · establishes the lineage backbone).
- `regenerate_shield_audit_id: str | null` (Trust Center deep-link).

**Frontend** (`RelatedDocuments.jsx`):
- Backend-first read of `/related` with legacy `source_document_ids` fallback for empty backend responses.
- Lineage/version chip in DocumentOverlay (small "vN of M" badge · additive).
- Regenerate affordance in overlay footer (disabled on committed state with tooltip).

## Slice acceptance (target 17/17 GREEN)

- R1  · `deck_retrieval.py` + `deck_lineage.py` + `deck_regenerate.py` exist; imports verified (retrieval/lineage: NO `contracts.get_synisense` · regenerate: HAS `contracts.get_synisense`)
- R2  · All 3 endpoints in `/api/openapi.json`
- R3  · Retrieval account isolation — Account A `/related` only returns Account A docs
- R4  · Cross-account similarity probe returns EMPTY for Account A vs known B-owned similar docs
- R5  · Lineage account isolation — same pattern
- R6  · **COMMIT-LOCK · REGENERATE 409** — committed doc → 409, envelope shape matches compile bridge 409 `{code, message}` structure. Side-by-side artifact captured.
- R7  · Regenerate on NON-committed → 200 · new version_number = prior+1 · `regenerated_from` set
- R8  · Prior versions preserved — original doc still retrievable + content intact
- R9  · **REGENERATE SHIELD ROUTING PROVED** — audit event fingerprint matches A9 extraction (19-field identity)
- R10 · **SHIELD UNTOUCHED** — 13 files sha256-identical to pre-A10 baseline (0 diffs)
- R11 · F.6 per-surface AST classification — retrieval/lineage: 0 refs · regenerate: shield_invoke on primary flow, 0 LLM-SDK direct imports
- R12 · Unauthenticated → 401/403 (CSRF+auth gate)
- R13 · FE `RelatedDocuments.jsx` reads `/related` backend + testids match
- R14 · FE lineage/version chip renders (structural)
- R15 · FE regenerate affordance renders + disabled on committed (structural + optional real render)
- R16 · Regression — 10 prior slices parse-clean · storage 500 MB · rename hashes
- R17 · Substrate integrity — regenerate creates its own lineage evidence in R7/R8; retrieval/lineage tested via those newly-created rows plus existing documents; substrate state reported honestly

## Hard-stop conditions

- Any diff in `services/synisense/shield/**` → STOP (R10)
- Regenerate 409 shape diverges from compile bridge → STOP (R6)
- Regenerate Shield audit fingerprint diverges from A9/Chat → STOP (R9)
- Prior version mutated/deleted → STOP (R8)
- Cross-account retrieval/lineage leaks → STOP (R3/R4/R5)
- Silent Shield bypass in regenerate → STOP (R11)

## Standing constraints preserved (all)

- Testing sub-agents BANNED.
- Split-literal `_TL / _OLD` discipline.
- No project-scope GCS calls.
- Zero-Handoff-Loss (§9 row landed BEFORE code).
- Chrome hard line + engine surfaces + rename hash invariants + Tab Honesty Rule + Replacement-naming Rule + Credentials-never-in-channel Rule + Amendment-echo Rule + Truth-in-capability Rule + **MOCKED-integrations discipline** (SendGrid + Resend named in Trigger-2).



## Side-by-side artifacts (R6 · R9 · R17)

Captured at: `2026-07-04T19:23:26.403019+00:00`

```json
{
  "captured_at": "2026-07-04T19:23:26.403019+00:00",
  "commit_lock_409_side_by_side": {
    "shape_identity": true,
    "regenerate_409": {
      "status_code": 409,
      "detail": {
        "code": "deck_already_committed",
        "message": "Document '431a1eda-d77b-40a4-a1e2-946c80a0d966' is committed and cannot be regenerated. Create a new draft to iterate."
      },
      "source": "services/deck_regenerate.py::commit_locked_409"
    },
    "compile_bridge_409_sample": {
      "code": "revision_empty",
      "message": "Revision has no snapshot.",
      "source": "routers/work_studio_phase_c.py:98"
    }
  },
  "shield_audit_fingerprint_side_by_side": {
    "chokepoint_fingerprint_match": true,
    "regenerate_audit": {
      "audit_id": "aud-d871a957955d49d8b9c17b1e83b51d1c",
      "consumer_id": "deck_regenerate",
      "purpose": "work_studio.deck.regenerate",
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
    "a9_extraction_audit": {
      "audit_id": "aud-881ae2cc297d4acfbfac35f2c7b26150",
      "consumer_id": "deck_signals",
      "purpose": "work_studio.deck.signal_extraction",
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
  },
  "substrate_report": {
    "r6_committed_probe_doc_id": "431a1eda-d77b-40a4-a1e2-946c80a0d966",
    "r7_draft_parent_doc_id": "9ca1001e-c2be-4142-a34d-a205d966d28b",
    "r7_regenerated_new_doc_id": "310cee2c-0ae6-44ba-a90b-81758b15ebe2",
    "note": "R7 created a fresh 2-version lineage (parent + regenerated child) which supplied the substrate for R8 (prior preserved) and R9 (Shield audit id capture). No julius-native substrate seeded \u2014 the pipeline is proven against admin-owned fresh probes."
  }
}
```

## Closure report (populated on GREEN)

**SHIPPED 2026-07-04 · 17/17 GREEN. Deck Path A A5-A10 fully complete.**

Slice output:
```
R1  · 3 A10 service files exist · import discipline verified                ✅ PASS
R2  · 3 endpoints in /api/openapi.json (related · lineage · regenerate)     ✅ PASS
R3  · Retrieval account isolation — only admin's docs returned              ✅ PASS
R4  · Cross-account similarity probe returns EMPTY                          ✅ PASS
R5  · Lineage account isolation — silent-truncate for foreign               ✅ PASS
R6  · REGENERATE COMMIT-LOCK → 409 compile-bridge-shape                     ✅ PASS
R7  · Regenerate NON-committed → new version_number + regenerated_from      ✅ PASS
R8  · Prior version preserved — original retrievable + content intact       ✅ PASS
R9  · REGENERATE SHIELD ROUTING · fingerprint matches A9 19-field set       ✅ PASS
R10 · SHIELD UNTOUCHED · sha256 diff = 0 across 13 files                    ✅ PASS
R11 · F.6 per-surface AST classification                                    ✅ PASS
R12 · Unauthenticated → 401/403 on all 3 endpoints                          ✅ PASS
R13 · FE reads /related endpoint + testids present                          ✅ PASS
R14 · FE lineage/version chip renders (structural)                          ✅ PASS
R15 · FE regenerate affordance + committed-disabled surface                 ✅ PASS
R16 · Regression: 10 prior slices + storage 500 MB + hashes                 ✅ PASS
R17 · Substrate report + memo side-by-side artifacts appended               ✅ PASS

GREEN · 17/17 rows passed
```

## Shield posture verification (R10 + R9)

- **R10 · Shield UNTOUCHED**: 13 files under `services/synisense/shield/**` sha256-identical to `/tmp/shield_pre_a10.sha256` baseline. **0 modified · 0 added · 0 removed**.
- **R9 · Chokepoint fingerprint identity**: regenerate audit row + A9 extraction audit row have IDENTICAL 19-field set — same audit-writer path in `services/synisense/shield/audit_log.py`. Regen: `consumer_id=deck_regenerate purpose=work_studio.deck.regenerate`; A9: `consumer_id=deck_signals purpose=work_studio.deck.signal_extraction`.
- **R11 · F.6 per-surface positive AST**: retrieval/lineage: 0 chokepoint refs (F.6 N/A invariant intact). Regenerate: `shield_invoke` on primary flow of `regenerate_deck`, 0 direct LLM-SDK imports.

## Commit-lock evidence (R6/R7/R8)

- **R6 · Commit-lock 409**: committed doc `<generated>` → 409 with `detail={code: 'deck_already_committed', message: <str>}`. Compile-bridge shape identity verified (both use `{code, message}` at `detail` per `routers/work_studio_phase_c.py:98/130/195`).
- **R7 · Non-committed regenerate**: parent draft `9ca1001e..` v1 → new draft `310cee2c..` v2. `regenerated_from` set. `regenerate_shield_audit_id` captured. New doc's `lifecycle_state="draft"`.
- **R8 · Prior preserved**: parent doc still retrievable via `db.documents.find_one({"id": parent_id})`. Content intact. `lifecycle_state="draft"` unchanged. **Never mutated · never deleted**.

## Account isolation evidence (R3/R4/R5)

- **R3 · Retrieval**: admin's `/related` returned 8 items, all in admin-context. 0 leaks.
- **R4 · Cross-account similarity**: fake account (random UUID, no memberships) → 0 items. Isolation upheld at source-doc-membership check in `deck_retrieval.get_related_decks`.
- **R5 · Lineage boundary**: admin's `/lineage` on foreign doc `eb99b392..` (ctx `000dd735..`) → `{document: None, ancestors: [], descendants: [], siblings: []}`. Silent-truncate at ctx-membership boundary in `deck_lineage._fetch_doc_scoped`.

## Truth-in-capability disclosures

- **R17 substrate**: R6 created a committed probe doc, R7 created a draft parent + regenerated child — the slice constructs its own 2-version lineage in-line (fresh admin-owned probes). Julius-native substrate NOT seeded; the pipeline is proven against admin fallback per A9 precedent. See R17 detail line and the memo's side-by-side artifact block.
- **R9 fingerprint scope**: chokepoint fingerprint proof is **field-set identity**, not full-value identity — legitimate differences in `consumer_id`, `purpose`, `de_id_summary`, `latency_ms`, etc. between regenerate and A9 audit rows are expected. Same-shape audit ↔ same chokepoint-writer. Full artifact in the memo.
- **R6 shape identity**: compile-bridge 409 samples (`revision_empty`, `synthesis_not_ready`) and regenerate 409 (`deck_already_committed`) all use `HTTPException(409, detail={code, message})`. Byte-identity impossible (codes differ by design), shape identity provable.

## Standing constraints preserved (all)

- Testing sub-agents BANNED (17/17 via bash + custom slice).
- Split-literal `_TL / _OLD` discipline.
- No project-scope GCS calls.
- Zero-Handoff-Loss (§9 row updated on close).
- Chrome hard line preserved.
- Engine surfaces intact (rename hash snapshot for drift monitoring).
- Tab Honesty Rule: retrieval/lineage/regenerate state authoritative server-side (documents collection).
- Replacement-naming: purpose `work_studio.deck.regenerate` covered by existing `work_studio.*` wildcard (no Shield-config-modify).
- Credentials-never-in-channel Rule intact (no key/secret touched).
- Amendment-echo Rule applied at dispatch start.
- Truth-in-capability Rule applied (R17 substrate report + R9 fingerprint scope + R6 shape identity declared).
- **F.6 PARTIAL discipline-pay** applied per surface (retrieval/lineage N/A · regenerate SHIELD-ROUTED).
- **Shield USE not MODIFY posture honoured** (R10 · 0-diff evidence).
- **MOCKED-integrations discipline** (banked rule): SendGrid dev-mode + Resend mock named in Trigger-2.
