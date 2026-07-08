Canonical rationale: Governance parity between metering and streaming adapters · gates A1/A2 choice on ceiling asymmetry follow-on. User dispatch 2026-07-08 · `JC-SHIELD-ADAPTER-METERING-PARITY-DIAGNOSE` (bounded CLASSIFY-ONLY · P1 · zero code · Shield READ-ONLY · A2 defensible ONLY IF ∆ = ∅ · A2 NEVER chosen on diff size alone · HARD STOP at classification).

# JC-SHIELD-ADAPTER-METERING-PARITY-DIAGNOSE

**Status:** CLASSIFY-ONLY · Trigger-2 close pending  
**Priority:** P1 (gates A1/A2 disposition on `JC-SHIELD-CEILING-ASYMMETRY-DIAGNOSE` follow-on)  
**Arc pattern:** report-only (memo + proving slice + §9 row 🟡→🟢)  
**Verdict (recommendation posture):** **NEITHER-STRAIGHT-SWAP** — A1 (chunked `shield_invoke`) preserves current governance in full; A2 as currently structured (bare `stream_llm_direct` / `collect_llm_text` as Enhance uses) LOSES ~13 governance items; A2-refined (route through `client.py::prepare_for_streaming` + `finalize`) CAN achieve parity but is a strictly larger scope than "reroute to streaming adapter".  
**F.6 classification:** N/A  
**PRE_ARC_HEAD:** `4d1d0f80` (§9 row 🟡 IN-FLIGHT flip, pre-code-touch, pre-memo-draft)  
**Shield composite sha256 (13 files, PRE_ARC_HEAD):** `c6902d324ed90734cd815f63eaee8ebb66d776ef89f1797c1f7f50cbae10d5a8`

---

## Received-scope echo (6 items)

1. Parity-diagnose fires · classify-only · zero code · Shield READ-ONLY · no build proposal built · ✅ HONOURED.
2. Read BOTH adapters: `services/synisense/shield/llm_router.py::invoke_with_metering` (:118-221) AND `services/synisense/shield/streaming.py::stream_llm_direct` (:331-447) · ✅ TRACED file:line.
3. Report exactly what governance each emits: metering data · audit fingerprint · fail-closed timing · rate-limit/cost accounting · request/response fingerprint · tenant isolation enforcement · ✅ ENUMERATED per adapter (STEP 1 · STEP 2 tables).
4. Delta report: verbatim ∆ both directions · ✅ COMPUTED (STEP 3).
5. Recommendation posture (do NOT build): A2 defensible ONLY if ∆ = ∅; otherwise A1 is default; NEVER on diff size alone · ✅ RENDERED with framing discipline (STEP 4).
6. HARD STOP at classification · A1/A2 build fires ONLY on user's explicit approval AFTER this report · ✅ ENFORCED.

---

## STEP 0 · Scoping recon

**Both adapters located (READ-ONLY):**

| Adapter | Path | Public entry | Line range |
|---|---|---|---|
| Metering (non-streaming) | `backend/services/synisense/shield/llm_router.py` | `invoke_with_metering(de_id_content, *, model_preference, timeout_seconds, system_msg)` | `:118-221` |
| Metering wrapper (governed) | `backend/services/synisense/shield/client.py` | `invoke(*, purpose, content, tenant_id, consumer_id, user_id, model_preference, internal_caller, system_msg)` | `:37-128` |
| Streaming | `backend/services/synisense/shield/streaming.py` | `stream_llm_direct(*, provider, model_id, system_msg, user_text, session_id, max_tokens)` | `:331-447` |
| Streaming non-generator companion | `backend/services/synisense/shield/streaming.py` | `collect_llm_text(*, provider, model_id, system_msg, user_text, session_id, max_tokens)` | `:456-481` |
| Streaming governed gateway (H2.5) | `backend/services/synisense/shield/client.py` | `prepare_for_streaming(*, purpose, content, tenant_id, consumer_id, user_id, internal_caller) → (redacted_text, token_map, finalize)` | `:149-249` |

**Critical distinction surfaced early:** `stream_llm_direct` and `collect_llm_text` are the STREAMING TRANSPORT primitives; they are NOT the full governance envelope. The governance envelope for streaming is `client.py::prepare_for_streaming` + `finalize`, which wraps `stream_llm_direct` in the same purpose-validation + de-id + audit + trust-receipt pipeline that `client.py::invoke` wraps around `invoke_with_metering`. **The `stream_llm_direct` primitive alone is not the governance-equivalent of `invoke_with_metering`.** The parity comparison must be careful about which layer we compare.

**Terminology used in this memo:**
- **METERING-ADAPTER** = `client.py::invoke` (governance wrapper) + `llm_router.invoke_with_metering` (transport). Full-round-trip Shield gateway. Used by `shield_invoke` → `llm_service.call_llm`.
- **STREAMING-ADAPTER-BARE** = `streaming.py::collect_llm_text` (or `stream_llm_direct` directly). Transport only. **Used by Enhance path** (`work_studio_export.py:619+767`) — bypasses `prepare_for_streaming`.
- **STREAMING-ADAPTER-GOVERNED** = `client.py::prepare_for_streaming` + `stream_llm_direct` + `finalize`. Full-round-trip Shield gateway with streaming transport. **Used today only by the chat router** (`routers/chat.py:2390` per docstring at `client.py:137`).

The parity question the dispatch asks — "should Generate switch from metering-adapter to streaming-adapter?" — has THREE candidate answers depending on which streaming layer is meant:
- A2a — bare streaming (matches Enhance today) → **large governance loss** (per STEP 3 delta).
- A2b — governed streaming (`prepare_for_streaming` + `finalize`) → **governance-equivalent BUT distinct scope** (not "just reroute the adapter"; also plumb tenant_id / consumer_id / user_id / purpose through the Generate runner).

Both A2 variants are reported in STEP 3-4 to keep the ∆ evaluation honest.

---

## STEP 1 · Governance emissions of METERING-ADAPTER

Traced from `client.py::invoke` at `:37-128` (governance wrapper) around `llm_router.invoke_with_metering` at `:118-221` (transport). Every emission item is cited to file:line.

| # | Emission | File:line | Notes |
|---|---|---|---|
| M1 | Purpose validation | `client.py:63` (`purpose_validator.validate_purpose(purpose, internal_caller)`) | Rejects with `PurposeUnauthorized` if purpose not in whitelist. |
| M2 | Tenant-scoped de-identification | `client.py:66` (`deidentifier.deidentify(content, tenant_id=tenant_id, purpose=purpose)`) | Returns `redacted_text` + `token_map` + `de_id_summary` + `dilution_score` + `exposure_reduction_score`. **This is the tenant isolation enforcement mechanism**: tenant PII is redacted BEFORE the LLM sees it. |
| M3 | Fail-closed LLM call | `llm_router.py:186-189` (`asyncio.wait_for(litellm.acompletion(**params), timeout=timeout_seconds)` where `timeout_seconds=20.0`) | Raises `ServiceUnavailable("LLM provider timeout after {timeout_seconds}s")` on timeout. Ceiling from `JC-SHIELD-CEILING-ASYMMETRY-DIAGNOSE`. |
| M4 | Re-identification | `client.py:71` (`reidentifier.reidentify(llm_text, de_id.token_map)`) | Swaps opaque tokens `[[ENT_XXX_NNN]]` back to originals in the response. |
| M5 | Latency measurement | `client.py:65, 72` (perf_counter start/end → `latency_ms`) | Integer ms; written into audit row. |
| M6 | Request hash (SHA-256 of INPUT) | `client.py:77` (`trust_receipt.hash_payload(content)`) | Fingerprint of pre-de-id user content. |
| M7 | Response hash (SHA-256 of OUTPUT) | `client.py:78` (`trust_receipt.hash_payload(response_text)`) | Fingerprint of post-re-id response. |
| M8 | Token metering — exact | `client.py:88-91` (`usage.get("method") == "exact"` from `llm_router.invoke_with_metering` return `_usage` dict; sourced from `response.usage.prompt_tokens/completion_tokens` at `llm_router.py:197-206`) | `{input_tokens, output_tokens, method: "exact"}`. |
| M9 | Token metering — estimated fallback | `client.py:92-95` (`audit_log.estimate_tokens(content)` + `audit_log.estimate_tokens(response_text)`) | char/4 estimator when SDK usage payload absent (mock mode / fallback). |
| M10 | Metering-method provenance | `client.py:88-95` (`metering_method: "exact" \| "estimated"`) | Written into audit row; downstream billing filters on this. |
| M11 | Cost accounting (USD) | `client.py:96-99` (`audit_log.compute_cost_usd(provider, model, tokens_in, tokens_out)`) | Per-model rate table at `audit_log.py:96+`; USD per 1M tokens. |
| M12 | Audit row write (Mongo `synisense_audit_log`) — 19 fields | `client.py:101-113` → `audit_log.write_audit` at `audit_log.py:27-93` | Fields: `audit_id, tenant_id, consumer_id, user_id, purpose, timestamp, de_id_summary, dilution_score, exposure_reduction_score, llm_provider, llm_model, request_hash, response_hash, outcome, latency_ms, tokens_in, tokens_out, metering_method, actual_cost_usd` (19). |
| M13 | Trust receipt build | `client.py:114-122` → `trust_receipt.build_trust_receipt` at `trust_receipt.py:99+` | 13 fields: `receipt_id, audit_id, tenant_id, consumer_id, purpose, timestamp, llm_provider, llm_model, de_id_summary, dilution_score, exposure_reduction_score, request_hash, response_hash`. |
| M14 | Trust receipt write (Mongo) | `client.py:123` (`audit_log.write_receipt(receipt)`) | Persisted for Trust Center rendering + downstream audit. |
| M15 | Outcome tag on failure | Implicit at `llm_router.py:213-221` (raises `ServiceUnavailable`; wrapper propagates); success path writes `outcome="success"` at `client.py:109` | Failure path does NOT reach audit_write in current code; failure rows are absent. **This is a corroborating asymmetry finding** — see STEP 4. |
| M16 | Tenant isolation enforcement (call-path level) | `client.py:66` `tenant_id=tenant_id` threaded into de-id + audit row + trust receipt | Not just a data label — the de-id map is tenant-partitioned; audit row is tenant-partitioned. |

**Metering-adapter emits 15 governance items (M1-M14 + M16); M15 is asymmetric on failure and surfaced separately.**

---

## STEP 2 · Governance emissions of STREAMING-ADAPTER-BARE

Traced from `streaming.py::collect_llm_text` at `:456-481` (called by Enhance path at `work_studio_export.py:619` + `:767`). `collect_llm_text` internally consumes `stream_llm_direct` at `:331-447`.

**Function signature (bare):** `collect_llm_text(*, provider: str, model_id: str, system_msg: str, user_text: str, session_id: Optional[str], max_tokens: int = 4096) → (text, provider_used, fallback_triggered, error)`.

**Enumeration (what is emitted):**

| # | Emission | File:line | Notes |
|---|---|---|---|
| S1 | Streaming delta yield (real-time) | `streaming.py:388, 424, 439-440` (`yield c` per `LlmStreamChunk`) | Per-chunk `text`; enables SSE surfaces. |
| S2 | Provider-used label | `streaming.py:340-343 + 366, 388-389, 407, 439` (`provider_used ∈ {anthropic_direct, gemini_direct, openai_direct, proxy_buffered}`) | Documented which transport served the request. |
| S3 | Fallback-triggered provenance | `streaming.py:439-440` (`c.fallback_triggered = True` on proxy fallback) | Surfaces to caller whether direct-SDK failed. |
| S4 | Per-chunk usage (best-effort) | `LlmStreamChunk.usage` dataclass field at `streaming.py:47` | Populated per-chunk when SDK returns usage; not consistently across providers. |
| S5 | Error surface (mid-stream) | `streaming.py:404-410, 442-447` (`kind="error"` chunk) | Caller decides how to handle. |

**Enumeration (what is NOT emitted — governance items present in metering but absent here):**

| Missing | Bare-streaming behaviour |
|---|---|
| Purpose validation | ⨯ NOT enforced — `collect_llm_text` has no `purpose` kwarg. |
| Tenant-scoped de-identification | ⨯ NOT enforced — no `tenant_id` kwarg. `user_text` is passed through raw. |
| Re-identification | ⨯ NOT applied — no `token_map` returned; caller sees whatever the model produced against raw PII. |
| Fail-closed timing (20s wait_for) | ⨯ ABSENT — no `asyncio.wait_for` wrapper anywhere in `streaming.py` (grep-verified: `grep -c "wait_for\|asyncio.wait_for" streaming.py` = 0). |
| Latency measurement | ⨯ NOT measured by adapter. Caller may do it externally but adapter emits none. |
| Request hash | ⨯ NOT computed. |
| Response hash | ⨯ NOT computed. |
| Token metering — exact | Partial — `LlmStreamChunk.usage` field exists but is best-effort; NOT persisted to DB. |
| Token metering — estimated | ⨯ NOT computed by adapter. |
| Metering-method provenance | ⨯ NOT emitted. |
| Cost accounting (USD) | ⨯ NOT computed. |
| Audit row write | ⨯ NOT written. `synisense_audit_log` gets NO row for a bare-streaming call. |
| Trust receipt build | ⨯ NOT built. |
| Trust receipt write | ⨯ NOT written. `synisense_trust_receipts` gets NO row. |
| Outcome tag | ⨯ NOT written (there is no audit row to tag). |
| Tenant isolation enforcement | ⨯ NOT enforced at call-path level. Bare adapter is tenant-agnostic. |

**Streaming-adapter-bare emits 5 governance/telemetry items (S1-S5) and OMITS 13 items relative to the metering adapter.**

---

## STEP 2b · Governance emissions of STREAMING-ADAPTER-GOVERNED (for completeness)

Traced from `client.py::prepare_for_streaming` at `:149-249` — the H2.5 Shield-adjacent streaming gateway (2026-05-24). Currently consumed only by the chat router per the docstring at `client.py:137`.

**Function signature:** `prepare_for_streaming(*, purpose, content, tenant_id, consumer_id, user_id, internal_caller) → (redacted_text, token_map, finalize)`. The `finalize` closure at `:197-247` writes the audit row + trust receipt.

**Governance parity with metering-adapter:**

| Metering item | Governed-streaming equivalent | File:line |
|---|---|---|
| M1 purpose validation | ✅ Present | `client.py:188` |
| M2 de-identification | ✅ Present | `client.py:191` |
| M3 fail-closed timing (20s wait_for) | ⨯ ABSENT — streaming does not use `invoke_with_metering`; caller drives the LLM via `stream_llm_direct`. No `wait_for(20.0)` wrapper. **This is the entire reason this arc's parent (`JC-SHIELD-CEILING-ASYMMETRY-DIAGNOSE`) surfaced the ceiling asymmetry.** | — |
| M4 re-identification | Delegated to caller via `token_map` return; the caller runs `StreamingReidentifier(token_map)` per-delta. Not run inside the adapter itself but the mechanism is provided. | `client.py:249` |
| M5 latency measurement | ✅ Present (perf_counter at `:190` + `:208`) | `client.py:190, 208` |
| M6 request hash | ✅ Present | `client.py:195` |
| M7 response hash | ✅ Present (computed in finalize) | `client.py:209` |
| M8-M11 token metering + cost | ✅ Present (finalize computes tokens_in/tokens_out + metering_method + cost_usd) | `client.py:211-222` |
| M12 audit row write (19 fields) | ✅ Present | `client.py:224-236` |
| M13-M14 trust receipt build + write | ✅ Present | `client.py:237-246` |
| M16 tenant isolation enforcement | ✅ Present (tenant_id threaded through de-id + audit + receipt) | `client.py:191, 225, 238` |

**Governed-streaming emits 14 governance items (M1-M2, M4-M14, M16); OMITS only M3 (the 20s wait_for cap).**

The absence of M3 in governed-streaming is **the exact mechanism** by which Enhance-via-`prepare_for_streaming` would bypass the ceiling. But — again — **Enhance today does NOT use `prepare_for_streaming`**. Enhance uses bare `collect_llm_text` (`work_studio_export.py:619+767`), which is `streaming-adapter-bare` and therefore governance-degraded.

---

## STEP 3 · Delta computation (verbatim, both directions)

### ∆(metering \ streaming-bare) — governance emitted by metering-adapter that streaming-adapter-bare does NOT

**13 items:**

1. **Purpose validation** (`purpose_validator.validate_purpose`)
2. **Tenant-scoped de-identification** (`deidentifier.deidentify(content, tenant_id, purpose)`)
3. **Re-identification** (`reidentifier.reidentify(llm_text, token_map)`)
4. **Fail-closed 20s timing** (`asyncio.wait_for(litellm.acompletion(...), 20.0)`)
5. **Latency measurement + audit-row `latency_ms`**
6. **Request hash (SHA-256 of INPUT)**
7. **Response hash (SHA-256 of OUTPUT)**
8. **Token metering persistence** (`tokens_in`, `tokens_out` written to `synisense_audit_log`)
9. **Metering-method provenance** (`"exact" \| "estimated"`)
10. **Actual cost USD accounting** (`actual_cost_usd`)
11. **Audit row write** (19-field row into `synisense_audit_log`)
12. **Trust receipt build + write** (13-field receipt into `synisense_trust_receipts`)
13. **Tenant isolation enforcement at call-path level** (tenant_id threaded through de-id + audit + receipt)

### ∆(streaming-bare \ metering) — governance/telemetry emitted by streaming-adapter-bare that metering-adapter does NOT

**4 items:**

1. **Per-chunk streaming deltas** (real-time SSE-compatible transport)
2. **Provider-used label** (`anthropic_direct | gemini_direct | openai_direct | proxy_buffered`)
3. **Fallback-triggered provenance** (direct-SDK → litellm proxy → proxy_buffered chain visibility)
4. **Per-chunk `usage` field** (best-effort; not persisted to DB)

### ∆(metering \ streaming-governed) — governance emitted by metering that governed-streaming does NOT

**1 item:**

1. **Fail-closed 20s timing** (`asyncio.wait_for(litellm.acompletion(...), 20.0)`) — governed-streaming lacks this wrapper because the caller drives the LLM via `stream_llm_direct` and streaming does not use `invoke_with_metering`.

### ∆(streaming-governed \ metering) — governance/telemetry emitted by governed-streaming that metering does NOT

**3 items:**

1. Per-chunk streaming deltas
2. Provider-used label + fallback-triggered provenance (surfaced via stream chunks; not into audit row schema)
3. Streaming-specific outcome semantics (`outcome="stream_error"` mid-stream vs `outcome="success"`)

---

## STEP 4 · Recommendation posture (framing discipline enforced)

**Verdict: NEITHER-STRAIGHT-SWAP.**

Rule map (from dispatch):
- If ∆ = ∅ → A2 defensible, both A1 and A2 governance-equivalent.
- If ∆ ≠ ∅ (streaming loses governance metering has) → A1 default; A2 requires explicit governance-trade acknowledgment.
- If ∆ has both directions → neither is a straight swap; A1 (preserves current governance) is safest; A2 requires adding-back-what-streaming-lacks.

**Applied to this arc:**

- ∆(metering \ streaming-bare) = **13 items** (large one-way governance loss).
- ∆(streaming-bare \ metering) = **4 items** (streaming-only capabilities: real-time deltas + provider labels + fallback provenance + per-chunk usage).
- **∆ has both directions.** By the dispatch's own rule: **neither is a straight swap.**

**A1 recommendation (default):** Chunked `shield_invoke` — refactor `_run_generate_deck_job` at `routers/decks.py:464` to invoke `shield_invoke` (via `call_llm_with_tier`) **N+2 times per user request** instead of once (1 meta + N per-slide body + 1 optional coherence tidy). Each sub-call fits under the 20s cap. **Preserves all 13 governance items** because every sub-call goes through `client.py::invoke → invoke_with_metering` exactly like today's single call — only the count changes.
- Governance trade-off: none (100% preservation).
- Metering trade-off: N+2 audit rows per deck (vs 1 today) — surfaces at Trust Center as a burst; downstream billing filters need to aggregate by `session_id` or by a new `generation_job_id` field to reconstruct per-request cost. Small billing-side query change.
- Latency trade-off: N+2 × ~5-8s serial vs 1 × ~25-30s today. Same order of magnitude in the worst case; better than today because it fits under the async runner without hitting the cap.
- Coherence risk: LOW (outline pre-locks narrative arc per `JC-SHIELD-CEILING-ASYMMETRY-DIAGNOSE` STEP 2).

**A2a (bare adapter reroute — NOT RECOMMENDED):** Reroute `_run_generate_deck_job` to call `collect_llm_text` directly (matches Enhance today). **Sheds 13 governance items.** Per user's rule ("A2 defensible ONLY IF ∆ = ∅"), A2a is NOT defensible for Generate. Additionally, this option corroborates a latent finding — **Enhance itself is currently governance-degraded** by using bare `collect_llm_text` instead of `prepare_for_streaming` (Real Signal iv below).

**A2b (governed-streaming reroute — DEFENSIBLE but distinct scope):** Reroute `_run_generate_deck_job` to `client.py::prepare_for_streaming` + `stream_llm_direct` + `finalize`. **Sheds 1 governance item (M3 fail-closed timing)** — but that shed item IS the whole point of the reroute (it's the ceiling being bypassed). Governance parity on the other 13 items: preserved.
- Scope trade-off: this is NOT "reroute the adapter" — it's "plumb Shield governance kwargs (`tenant_id`, `consumer_id`, `user_id`, `purpose`, `internal_caller`) through the Generate runner + wire the streaming finalize handshake + integrate `StreamingReidentifier` per-delta". Larger surface than A1.
- Coherence trade-off: streaming a full deck JSON is tricky — partial JSON deltas are not directly usable until complete; caller must accumulate + parse at end. So streaming adds no functional value to Generate (unlike Chat where deltas are user-visible). This makes A2b's streaming "bypass the cap" feel like a workaround more than a design win.
- If A2b is chosen, the fail-closed timing (M3) is intentionally shed as the bypass mechanism — this is the explicit trade-off the user must acknowledge.

**Framing verbatim (do NOT build):**
> "Neither A1 nor A2 is a straight swap. A1 (chunked `shield_invoke`) preserves all 13 governance items and is the recommended default. A2a (bare adapter reroute) is NOT defensible — sheds 13 governance items; violates user's explicit rule. A2b (governed-streaming reroute via `prepare_for_streaming`) is defensible IF the user acknowledges shedding the fail-closed 20s cap (M3) as the bypass mechanism, and IF the user accepts the larger plumbing surface. Propose scoped follow-on arcs `JC-DECK-GENERATE-CHUNKED-INVOCATION` (A1) or `JC-DECK-GENERATE-GOVERNED-STREAMING-REROUTE` (A2b) for explicit user approval · do NOT build in this arc · rough scope + risk assessment above."

---

## STEP 5 · Real Signals surfaced

- **(iv) Enhance path is currently governance-degraded.** `work_studio_export.py:619` and `:767` call `collect_llm_text` directly (`streaming-adapter-bare`) instead of `client.py::prepare_for_streaming` (`streaming-adapter-governed`). This means Enhance runs today emit ZERO Shield audit rows, ZERO trust receipts, ZERO tenant-scoped de-identification, ZERO purpose validation, ZERO cost accounting into `synisense_audit_log`. **This is a latent governance defect independent of the Generate/Enhance ceiling asymmetry.** Surfacing for user disposition — separate arc may be warranted (`JC-WS-ENHANCE-GOVERNANCE-REPAIR`). It is NOT within this arc's scope to fix.
- **(v) Metering-adapter failure rows are absent.** On timeout / SDK failure at `llm_router.py:213-221`, the exception propagates through `client.py::invoke` before `audit_log.write_audit` is called — so `synisense_audit_log` has NO row for a failed Shield call. Failure telemetry is only in supervisor error logs. **Consider adding a `outcome="timeout" | "provider_error"` audit path** — but this is a separate improvement, not this arc.
- **(vi) Streaming vs metering audit-row schema unification.** Both paths (governed) write to the same `synisense_audit_log` collection with the same 19-field row shape. This is a POSITIVE finding: the Trust Center panel does not need to distinguish streaming vs sync at query time.

---

## STEP 6 · Closure — Zero-touch verification

`git diff --stat 4d1d0f80 -- <protected paths>` must yield 0 bytes on close.

Protected paths (identical to `JC-SHIELD-CEILING-ASYMMETRY-DIAGNOSE` R6 list, plus explicit expansion):
1. `backend/services/synisense/shield/**` (13 files)
2. `backend/services/synisense/shield/streaming.py`
3. `backend/services/synisense/shield/llm_router.py`
4. `backend/services/synisense/shield/client.py`
5. `backend/services/synisense/shield/audit_log.py`
6. `backend/services/synisense/shield/trust_receipt.py`
7. `backend/services/synisense/shield/deidentifier.py`
8. `backend/services/synisense/shield/reidentifier.py`
9. `backend/services/synisense/shield/purpose_validator.py`
10. `backend/routers/work_studio_export.py`
11. `backend/routers/decks.py`
12. `backend/llm_service.py`
13. `backend/llm_tier_quota.py`
14. `backend/.env`

Composite Shield sha256 identity `c6902d324ed90734cd815f63eaee8ebb66d776ef89f1797c1f7f50cbae10d5a8` (13 files) preserved on close.

Files touched in this arc (report-only, per proving slice R6):
- NEW `memory/sprints/JC_SHIELD_ADAPTER_METERING_PARITY_DIAGNOSE.md` (this memo)
- NEW `backend/scripts/jc_shield_adapter_metering_parity_diagnose_proving_slice.py`
- NEW `memory/jc_artifacts/shield_adapter_metering_parity/slice_results.json`
- MOD `memory/DEV_PIPELINE.md` §9 row (this arc, 🟡 IN-FLIGHT flipped BEFORE memo/slice draft; 🟢 on close with content marker `shield-adapter-metering-parity-classified-neither-straight-swap`)

Zero product-code / config / env / Shield touches.

---

## STEP 7 · Close-status

Push status: **SHIPPED-UNPUSHED** on close · commit hash cited in Trigger-2 · `git remote -v` empty in preview pod · user pushes via "Save to GitHub". Per `RULE-CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED`.

**HARD STOP at classification. Nothing auto-fires past this memo.** A1/A2b build fires ONLY on user's explicit approval AFTER this report. Track 2 (`JC-WS-DRAFTS-BRIEFS-QA-RECOVERY-STAGE-1`) is dispatched but queued strictly after this arc closes.

**Content marker:** `shield-adapter-metering-parity-classified-neither-straight-swap`
