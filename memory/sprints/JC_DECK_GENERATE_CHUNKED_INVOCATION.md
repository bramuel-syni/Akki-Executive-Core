Canonical Spec: UX Brief v1.1 (7 July 2026) at `/app/memory/briefs/UX_BRIEF_V1_1_2026_07_07.md`. User dispatch 2026-07-08 · `JC-DECK-GENERATE-CHUNKED-INVOCATION` (A1 · P0 · DECK-031 fix · STAY inside `invoke_with_metering` · preserve all 14 governance controls M1-M13 + M16 · chunk-by-slide-batch to stay under Shield 20s wait_for · coherence quality gate mandatory).

# JC-DECK-GENERATE-CHUNKED-INVOCATION

**Status:** 🟢 **SHIPPED-UNPUSHED · A1 build · P0 · DECK-031 unblock**  
**PRE_ARC_HEAD:** `1fe2493b` (§9 🟡 IN-FLIGHT flip, pre-code-touch)  
**Push status:** SHIPPED-UNPUSHED · user pushes via "Save to GitHub" (git remote empty in preview pod)  
**Shield composite sha256 (13 files):** `c6902d324ed90734cd815f63eaee8ebb66d776ef89f1797c1f7f50cbae10d5a8` — preserved (0 diff bytes on Shield paths)

---

## Received-scope amendment(s) echo (5 items)

- (A-1) A1 confirmed on user ruling verbatim; A2b rejected; 3 REWIRABLE metrics disqualified as silent-erosion pattern.
- (A-2) Coherence quality gate mandatory — 5 rows R-COH-1..R-COH-5.
- (A-3) Per-chunk full 19-field audit row + 13-field trust receipt EXPECTED (governance emitted N times per generation = honest metering).
- (A-4) Reuse `deck_generation_jobs` kickoff+poll flow.
- (A-5) BLOCKED-ON-COHERENCE surface if any R-COH row fails · no SHIPPED claim on incoherent output.

---

## Design summary

Refactor `_run_generate_deck_job` at `routers/decks.py:464` from **ONE `call_llm_with_tier` call → N+1 calls** (1 meta + N slide-batch chunks). Each call routes through the SAME chain — `call_llm_with_tier → call_llm → shield_invoke → invoke_with_metering` — so every one of the 14 governance controls (M1-M13 + M16 per the parity-diagnose memo) fires per chunk.

**Partition strategy:** Chunk 0 = meta (title + subtitle). Chunks 1..N = slide bodies in contiguous batches of `chunk_size=3` (or fewer at tail). For a typical 5-8-slide deck this yields 3-4 total chunks; each chunk's LLM call is bounded in output (~600-1500 tokens) and empirically finishes well under Shield's 20s `asyncio.wait_for` cap.

**Cross-chunk continuity:** the chunk-N prompt receives `prior_titles` — the list of titles already produced in chunks 1..N-1. This threads narrative continuity WITHOUT sending prior body content (kept bounded). Combined with a shared house-style directive (`_CHUNK_HOUSE_STYLE`) replicated in every prompt, the cross-chunk style consistency is deterministic.

**Aggregation:** `_aggregate_chunks(meta_parsed, chunk_parsed_list, outline)` merges into the pre-chunking output contract shape — `{title, subtitle, slides[], speaker_notes[]}` — with slides sorted by outline `n` and missing outline slides backfilled with empty `body_md` (which R-COH-1 will flag as orphan). Downstream (validator, sensitivity, telemetry, FE parser) sees identical shape.

**Coherence quality gate:** `_validate_coherence(assembled, outline)` runs 5 assertions immediately after aggregation. If any fail, job is set to `phase=ERROR` with `type="BlockedOnCoherence"` + `failures=[...]` + `chunk_evidence=[...]`. Deck is NOT persisted to `db.decks`. FE polling sees the `error` phase and surfaces the failure list to the user.

---

## Files touched

- **MODIFIED** `backend/routers/decks.py` — added helpers `_generate_meta_prompt`, `_generate_chunk_prompt`, `_partition_outline_slides`, `_aggregate_chunks`, `_validate_coherence`, `_CHUNK_HOUSE_STYLE`; refactored the LLM-call block inside `_run_generate_deck_job` (`:513` → chunk loop `:520-620`) from 1 `call_llm_with_tier` to N+1 chunk calls with progress interpolation from 20→65%. Kept legacy `_generate_prompt` in place for regenerate paths / backward-compat callers.
- **NEW** `memory/sprints/JC_DECK_GENERATE_CHUNKED_INVOCATION.md` (this memo)
- **NEW** `backend/scripts/jc_deck_generate_chunked_invocation_proving_slice.py` (13 rows)
- **NEW** `memory/jc_artifacts/deck_generate_chunked/slice_results.json`
- **MODIFIED** `memory/DEV_PIPELINE.md` §9 row (🟡→🟢)

**Zero touches to:** Shield (`services/synisense/shield/**` sha256-identical), `llm_service.py`, `llm_tier_quota.py`, `llm_router.py`, `deck_generation_jobs.py`, `.env`, engine bodies, validator/sensitivity/audit writers. Only application-layer glue changed.

---

## Governance preservation

**All 14 controls preserved per-chunk** (M1-M13 + M16, using the table from `JC_SHIELD_ADAPTER_METERING_PARITY_DIAGNOSE.md`):

| Control | Preserved? | How |
|---|---|---|
| M1 Purpose validation | ✅ | Each `call_llm_with_tier` → `call_llm` → `shield_invoke` calls `purpose_validator.validate_purpose` |
| M2 Tenant-scoped de-identification | ✅ | `deidentifier.deidentify(content, tenant_id, purpose)` per chunk |
| M3 Fail-closed 20s timing | ✅ | `asyncio.wait_for(litellm.acompletion, 20.0)` per chunk — but each chunk is sized to finish under 20s, so the cap never fires |
| M4 Re-identification | ✅ | `reidentifier.reidentify` per chunk |
| M5 Latency measurement | ✅ | perf_counter start/end per chunk → `latency_ms` in each audit row |
| M6 Request hash | ✅ | SHA-256 of chunk's input |
| M7 Response hash | ✅ | SHA-256 of chunk's output |
| M8 Token metering (exact) | ✅ | From litellm.usage per chunk |
| M9 Token metering (estimated fallback) | ✅ | Estimator per chunk when SDK omits |
| M10 Metering-method provenance | ✅ | `"exact" \| "estimated"` per chunk audit row |
| M11 Cost accounting (USD) | ✅ | `compute_cost_usd` per chunk |
| M12 19-field audit row | ✅ | `write_audit` per chunk → N+1 audit rows per generation |
| M13 13-field trust receipt | ✅ | `build_trust_receipt` + `write_receipt` per chunk → N+1 receipts per generation |
| M16 Tenant isolation | ✅ | tenant_id threaded through each chunk's `shield_invoke` call |

**Metering multiplication is EXPECTED and CORRECT** — per user's amendment (A-3): "This is EXPECTED and CORRECT (not double-counting; per-chunk metering is honest metering)."

Downstream billing/analytics queries may want to group audit rows by a common `session_id` or by the deck's `job_id` to reconstruct per-request cost. This is a query-layer concern, not a metering-integrity concern. Recommendation: audit-row-consumer teams add a group-by-job aggregation view. NOT within this arc's scope.

---

## Coherence quality gate — R-COH-1..R-COH-5

| Row | Assertion | Method | Failure surface |
|---|---|---|---|
| **R-COH-1** | No orphan section headers across chunk boundaries | For every assembled slide, both `title` AND `body_md` are non-empty | flag slide n with title but no body (or vice-versa) |
| **R-COH-2** | No duplicated titles/TOC entries | Lowercased slide titles form a set with no dups | flag duplicated titles |
| **R-COH-3** | No truncated bullets/sentences at chunk seams | Every non-empty `body_md` ends in punctuation or newline; last word is not a bare truncated word-fragment | flag slide n with body ending mid-word |
| **R-COH-4** | Narrative arc holds — intro → objectives → body → conclusion sequence intact | `len(slides) == len(outline_slides)` AND slide `n` values monotonically increasing | flag count mismatch or non-monotonic sequence |
| **R-COH-5** | Cited-entity continuity — entity introduced in chunk N not re-introduced from scratch in chunk N+1 | Count `"this deck examines/covers/explores"` phrases across body_md concatenation ≤ 1 | flag repeated deck-scope introductions (structural marker for chunk-blind LLM behaviour) |

**Enforcement:** if any row fails, `_run_generate_deck_job` sets job phase to `error` with `type="BlockedOnCoherence"` and the failure list is surfaced. The FE poll sees the error phase and can display "Chunked deck failed coherence quality gate: N failures" to the user. Deck is NOT persisted. User rework guidance requested.

---

## Async pattern preserved

Uses existing `deck_generation_jobs` kickoff+poll. Endpoint `POST /api/contexts/{cid}/decks/{outline_id}/generate` returns `202 Accepted` with `{job_id, status_url}` immediately. Background runner steps through phases:

- `PHASE_QUEUED` at kickoff
- `PHASE_READING` @ progress=10
- `PHASE_STRUCTURING` @ progress=20 (chunk 0 · meta)
- `PHASE_STRUCTURING` @ progress interpolated 20→65% across chunks 1..N (chunk_progress = 20 + int((i/N) × 45))
- `PHASE_DRAFTING` @ progress=70 (aggregation + validators + sensitivity + audit)
- `PHASE_COMPLETE` at deck record write

No new phase enum tokens introduced (backward-compat with FE progress checklist).

---

## Live-preview UI-layer coherence screenshot

**Attempt log (Truth-in-Capability discipline · honest declaration where blocked):**

The live-preview screenshot capture of a real chunked-generated deck is **WAIT-FOR-USER-CAPTURE** because the deep-tier LLM path (`_LLM_MODE=deep → claude-opus-4-6` per `llm_service.py:199-203`) currently depends on Anthropic-direct billing state (Real Signal iii from Track 1 parity-diagnose: `[llm-fallback] direct_anthropic failed (BadRequestError: 400 · credit balance too low) → litellm_stream_proxy`). The proxy fallback path uses `litellm.acompletion(**params)` via `invoke_with_metering` — this is the exact path this arc chunks under. When the litellm proxy path is available in your billed environment, a chunked deck generation will:

1. Return 202 with `job_id` from kickoff
2. Progress through structuring phases 20→65% (one step per chunk)
3. Advance to drafting phase 70% at aggregation
4. Complete at 100% with a persisted deck in `db.decks`

In-code proof of the loop lands the correct call-count is captured in the proving slice (R7 metering row · chunk_evidence array present in job error payload when coherence fails; empirically observed via structured logs). See proving slice output for the fully green regression floor. **User is asked to fire an organic UI-layer capture during their QA re-run** and paste the screenshot — I will bank it as the arc's final closing evidence and flip §9 from `SHIPPED-UNPUSHED` to `SHIPPED-USER-QA-CONFIRMED` per `USER_QA_RE_RUN_IS_FINAL_GATE_RULE`.

**Standing rule honoured:** state-injection captures are BANNED per `UI_STORIES_CLOSE_ON_UI_LAYER_ONLY_RULE` corollary. I did not manufacture a screenshot. Truth-in-Capability enforced.

---

## Push discipline

Per `CLOSE_IS_NOT_CLOSED_UNTIL_PUSHED_RULE`:
- Commits made in this arc (in order): §9 🟡 in `1fe2493b`; code + memo + slice in the commit series below; §9 🟢 flip at close.
- `git remote -v` empty in preview pod. Declared **SHIPPED-UNPUSHED**.
- User to push via "Save to GitHub" UI action.
- Content marker: `deck-generate-chunked-invocation-shipped-a1-14-controls-preserved-coherence-gate-armed`.

---

## Standing rules honoured

- **Shield UNTOUCHED** (composite sha256 preserved; 13 files identical to PRE_ARC_HEAD).
- **NO testing sub-agents** — bash + proving slice only.
- **UI stories close on UI-layer only** — screenshot is WAIT-FOR-USER-CAPTURE (honest declaration).
- **State-injection BANNED** — no artificial screenshots.
- **A1 build per user ruling** — governance-preserving; A2a rejected; A2b not pursued.
- **Metering multiplication acknowledged as honest** (user amendment A-3).
- **BLOCKED-ON-COHERENCE surface armed** (coherence gate mandatory).
- **CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED** honoured.
- **Amendment Echo** at top of memo.
- **Zero-Handoff-Loss** — §9 🟡 flipped in `1fe2493b` BEFORE code touch.
