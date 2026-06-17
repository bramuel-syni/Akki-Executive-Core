# Phase 14 — Chat Fluency & Detection Hardening

**Shipped:** 2026-06-05 (iter-1 single-dispatch ship).
**Approver:** User direct dispatch following the read-only investigation that confirmed the dead-code system_msg + the token-shape drift between chat preamble and de-identifier.

---

## Goal

Make `/app/chat` conversationally indistinguishable from a raw Claude session at the prose level (no "redacted token" meta-language leaking into user-visible replies), while preserving every Shield wire-path guarantee and every existing audit surface.

---

## Files touched

**Modified:**
- `backend/services/synisense/shield/deidentifier.py` (+~65 LOC) — exported `SHIELD_TOKEN_FORMAT_DESCRIPTION` + `SHIELD_TOKEN_EXAMPLES` constants; added `_ORG_PROTECTOR_TERMS` frozenset (diseases / weekdays / months / generic capitalised nouns); wired the protector into the spaCy hit loop before append.
- `backend/services/synisense/shield/tenant_entities.py` (+~20 LOC) — length floor `_MIN_ENTITY_LEN = 4` applied at harvest time (every collection field) AND at lookup time (defensive belt against stale-cache entries that pre-date the deploy).
- `backend/services/synisense/shield/client.py` (+~10 LOC) — added optional `system_msg: Optional[str] = None` kwarg to `invoke()`; threads through to `invoke_with_metering`. Backwards-compatible (`None` default = pre-Phase-14 behaviour for the 90+ existing call sites).
- `backend/services/synisense/shield/llm_router.py` (+~10 LOC) — added optional `system_msg: Optional[str] = None` kwarg to `invoke_with_metering`; when provided, REPLACES the generic privacy-governed system prompt at the litellm `messages[0]` slot; when None, the pre-Phase-14 generic system prompt is used.
- `backend/routers/chat.py` (+~95 LOC, -~25 LOC) — added `_phase14_chat_fluency_system_msg()` helper at module top (single source of truth, references the de-id constants); replaced the dead L1833 `system_msg` block with a call to the helper; threaded `system_msg=system_msg` into the sync `shield_invoke` call at L1882; appended the same helper to the streaming path's `system_msg` at L2780 so the two endpoints don't diverge; added `chat_system_prompt_injection_failed` typed flag to the sync response (T1 step 5 — Honesty protocol).

**Created:**
- `backend/tests/test_chat_system_msg_prepended.py` — captures `shield_invoke` kwargs end-to-end via the sync send-message route; asserts the AKKI preamble was passed via `system_msg=`.
- `backend/tests/test_chat_token_shape_consistency.py` — 5 deterministic assertions pinning the chat preamble's token shape to the de-id emitter constants.
- `backend/tests/test_tenant_entities_length_floor.py` — 3 deterministic assertions: short-prefix bite suppression + "onrr"-fragment regression + 4-char boundary inclusive.
- `backend/tests/test_spacy_org_common_noun_protector.py` — 5 deterministic assertions: Malaria + Following NOT redacted, Apple Inc IS redacted, list constant exported with correct contents, list does not overreach onto real brand names.
- `backend/tests/test_chat_fluency_no_shield_leak.py` — `@pytest.mark.integration` real-LLM round-trip; asserts no `[[ENT_` / `redacted` / `\btoken\b` / `I can't parse` / `did you mean` leaks; asserts substantive marker present; asserts audit row written with `outcome=="success"`.

**Sprint memo:** this file (`/app/memory/sprints/PHASE_14_CHAT_FLUENCY.md`).

---

## Test results

**Deterministic (default sweep):** 14 new + 0 regressions across 160 tests in the targeted aggregate sweep (Phase 3-7 + Phase 14 + SyniSense baseline). **160/160 PASS.**

**Integration-marked (real LLM):** `test_chat_fluency_no_shield_leak.py` PASS in 23.37s against the live Anthropic endpoint via Shield. Real model produced fluent prose containing `Bramuel`, `Mary Anne`, `Nairobi`, `pre-read` etc. — no `[[ENT_` leak, no forbidden vocabulary, audit row written with `outcome=="success"`.

**Pre-existing collection errors NOT introduced by Phase 14:** `test_iter70_inbound_triage.py` and `test_iter70_inbound_edge.py` fail at collection with `KeyError: 'POSTMARK_SERVER_TOKEN'` — env var missing in the preview environment. Out of Phase 14 scope; logged here for completeness.

---

## Track-by-track compliance

### Track 1 — Chat fluency

| Step | Status | Evidence |
|---|---|---|
| 1.1 Export `SHIELD_TOKEN_FORMAT_DESCRIPTION` + `SHIELD_TOKEN_EXAMPLES` | ✅ | `deidentifier.py:159-180`. Pinned by `test_chat_token_shape_consistency.py`. |
| 1.2 Rewrite chat `system_msg` with token-shape contract + forbidden vocab + ambiguity-as-natural-followup rule | ✅ | `_phase14_chat_fluency_system_msg()` at `chat.py:~150`. Forbids `redacted`, `token(s)`, `I can't parse`, `did you mean`. Pinned by `test_chat_token_shape_consistency.py::test_chat_preamble_uses_real_token_shape_not_legacy`. |
| 1.3 Wire `system_msg` into the prompt that reaches `shield_invoke` (preferred: dedicated system param) | ✅ via dedicated `system_msg=` kwarg on `invoke()` + `invoke_with_metering()`. Backwards-compatible — None default preserves the 90+ existing call sites' behaviour. |
| 1.4 Apply same fix to streaming sibling | ✅ Streaming path at `chat.py:~2780` now appends the Phase 14 preamble to its `_tp.build_system_prompt()` result; the existing `stream_llm_direct(system_msg=...)` plumbing already passed it through. The two endpoints share the helper. |
| 1.5 Honesty protocol — typed flag on injection failure | ✅ `chat_system_prompt_injection_failed: bool` on the sync response. Set to `True` in the broad except path. `logger.exception(..., exc_info=True)` preserved. |

### Track 2 — Detection quality

| Step | Status | Evidence |
|---|---|---|
| 2.1 Length floor `≥ 4` chars on tenant entities (harvest + lookup) | ✅ `tenant_entities.py:_MIN_ENTITY_LEN = 4` enforced at every `rows.append(...)` site in `harvest()` (accounts.full_name + company_name + contexts.name + organization_name + cycles.title) and as a defensive belt at lookup-iteration time. Pinned by `test_tenant_entities_length_floor.py` (3 assertions). |
| 2.2 Narrow `_ORG_PROTECTOR_TERMS` frozenset + drop ORG hits matching it | ✅ Initial contents kept tight per the brief: 19 diseases + 6 weekdays + 12 months + 6 generic capitalised English words = 43 terms. Wired into the spaCy hit loop at `deidentifier.py:~609`. Pinned by `test_spacy_org_common_noun_protector.py` (5 assertions including real-spaCy round-trips for Malaria / Following / Apple Inc). |
| 2.3 Do NOT touch other parts of the de-id pipeline | ✅ Zero changes to regex layer, other spaCy types, substitution path, or anywhere outside the two strictly-scoped insertions. |

### Track 3 — Test pinning

| # | File | Marker | Status |
|---|---|---|---|
| 1 | `test_chat_system_msg_prepended.py` | default | ✅ PASS |
| 2 | `test_chat_token_shape_consistency.py` | default | ✅ PASS (5/5 assertions) |
| 3 | `test_tenant_entities_length_floor.py` | default | ✅ PASS (3/3 assertions) |
| 4 | `test_spacy_org_common_noun_protector.py` | default | ✅ PASS (5/5 assertions) |
| 5 | `test_chat_fluency_no_shield_leak.py` | `@pytest.mark.integration` | ✅ PASS — real LLM round-trip in 23.37s, no shield-mechanics leak, audit row outcome=="success" |

---

## Deviations from the brief

**None of substance.** Three minor implementation notes (no scope shift):

1. **Token-shape constant location.** The brief said to add `SHIELD_TOKEN_FORMAT_DESCRIPTION` to `deidentifier.py` — done. The chat helper imports it at the chat.py module top via a renamed alias to keep the local namespace tidy.

2. **Cache TTL type.** During the test pass I noticed `tenant_entities._CACHE_LOADED_AT` stores `time.monotonic()` floats, not `datetime` objects. The deterministic length-floor test patches the cache with the correct float type — not a code change, just a test-side note for future contributors.

3. **Chat seed shape.** Two test seeds needed `status: "active"` + `context_id: None` to satisfy the chat-fetch query in `chat.py`. Documented in the test files; no production code touched.

---

## What this dispatch did NOT touch (out-of-scope confirmed)

- Other Shield wire-path behaviour, hard-PII placeholders, deterministic token format, audit log schema, trust-receipt schema.
- POS check, WordNet, NER model swaps, embedding-based filters.
- Tenant catalogue cleanup of already-harvested short entries.
- New React surfaces — existing chip / AUDIT button / footer / per-message badges continue to render unchanged.
- Documents flow, Work Studio, Solva, Pulse, Tasks — untouched.

---

## Follow-ups (none auto-scoped)

- **Stale tenant-catalogue cleanup**: a one-time backfill that removes already-harvested `< 4` char entries from `synisense_tenant_entities`. Defensive `_MIN_ENTITY_LEN` belt at lookup time already shields production from these in the meantime. NOT auto-scoped per Phase 14 brief's explicit out-of-scope clause.
- **Postmark env var fix** (`test_iter70_inbound_triage.py` + `test_iter70_inbound_edge.py` collection errors) — unrelated to Phase 14; preview-env config issue.

---

## Status

**Phase 14 → ✅ COMPLETE 2026-06-05.**
- Total: 5 BE files modified + 5 new BE test files. Net ~200 LOC delta across product + tests.
- Iter budget: 1 of 1 used (no iter-2/3 needed).
- 14/14 default sweep PASS + 1/1 integration-marked PASS. 160/160 aggregate sweep PASS across Phase 3-7 + Phase 14 + SyniSense baseline.
