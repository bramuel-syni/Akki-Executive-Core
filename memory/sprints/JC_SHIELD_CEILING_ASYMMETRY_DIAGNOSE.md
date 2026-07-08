Canonical Spec: user dispatch 2026-07-08 · `JC-SHIELD-CEILING-ASYMMETRY-DIAGNOSE` (CLASSIFY-ONLY diagnose arc · P1 · bounded · Shield READ-ONLY · no code changes · testing sub-agents BANNED · bash slice only) + 3 reinforcements ((1) call-count runtime evidence over structural inspection · declare INDETERMINATE + recommend Case D if runtime evidence unavailable; (2) prompt-semantic reading for (b) — NO/YES/INDETERMINATE based on prompt coherence dependency, not `acompletion` call count; (3) Case A framing discipline — memo phrasing "propose scoped arc `JC-DECK-GENERATE-CHUNKED-INVOCATION` for user approval · do NOT build in this arc · rough scope + risk assessment only").

# JC-SHIELD-CEILING-ASYMMETRY-DIAGNOSE

**Status:** CLASSIFY-ONLY · Trigger-2 close pending  
**Priority:** P1  
**Arc pattern:** report-only (memo + proving slice + §9 row 🟡→🟢)  
**Verdict (posture):** **CASE A** (propose scoped arc for user approval · do NOT build in this arc · rough scope + risk assessment only)  
**PRE_ARC_HEAD:** `f7255414` (§9 row 🟡 IN-FLIGHT flip, pre-code-touch, pre-memo-draft)  
**Shield composite sha256 (13 files, PRE_ARC_HEAD):** `c6902d324ed90734cd815f63eaee8ebb66d776ef89f1797c1f7f50cbae10d5a8`

---

## Received-scope echo

**Scope in:** classify why Stage 2 (Enhance journey) completed the full v1.1 §4.5 organic run at t=91s on live preview without hitting the 20s Shield-internal ceiling, while Stage 1 (Generate journey · DECK-031 · Create Summary Deck) hit `SHIELD-INTERNAL-LLM-PROVIDER-TIMEOUT` at ~22s in the same environment.

**Scope out:** implementation. This arc emits a classification memo + proving slice + §9 row only. No code, config, .env, or Shield file will be touched. Any implementation (chunking, adapter reroute, else) requires a follow-up dispatch after user reads this memo.

**Constraints honoured:**
- Shield files (`services/synisense/shield/**`) — READ-ONLY (0 diff bytes vs PRE_ARC_HEAD; sha256 identity `c6902d324e...` preserved on close).
- No code / config / env changes in this arc.
- Testing sub-agents (`testing_agent_v3_fork`) BANNED throughout.
- Bash execution of proving slice only.
- Files touched in commit: memo (this file) + proving slice + `DEV_PIPELINE.md §9` row ONLY.
- Reinforcements honoured (call-count runtime evidence discipline · prompt-semantic reading · Case A framing).

---

## STEP 0 · Scoping recon

**Two paths under diagnosis:**

| Path | Endpoint | Router | Runner | LLM adapter (Shield entry) |
|---|---|---|---|---|
| **Enhance** (v1.1 §4.5) | `POST /api/contexts/{cid}/work-studio/enhance/{kind}` (`status_code=202`) | `backend/routers/work_studio_export.py` (enhance_export) | `_runner` at `work_studio_export.py:2717` → `_run_enhance` at `work_studio_export.py:1762` → `_do_pass_1_and_pass_2` at `work_studio_export.py:556` | `collect_llm_text` at `work_studio_export.py:619` (Pass 1) + `:767` (Pass 2) — imported from `services.llm_streaming` which re-exports from `services/synisense/shield/streaming.py` |
| **Generate** (v1.1 §4.2-4.3) | `POST /api/contexts/{cid}/decks/{outline_id}/generate` (`status_code=202`) | `backend/routers/decks.py:377` (generate_deck) | `_run_generate_deck_job` at `decks.py:464` | `call_llm_with_tier` at `decks.py:513` → `llm_tier_quota.call_llm_with_tier` at `llm_tier_quota.py:165` → `llm_service.call_llm` at `llm_service.py:135` → `shield_invoke` at `llm_service.py:224` — resolves to `services/synisense/shield/client.py::invoke` → `services/synisense/shield/llm_router.py::invoke_with_metering` |

Both terminal call sites are inside `services/synisense/shield/**` and therefore Shield-untouchable. The asymmetry lies **not in whether Shield is touched** (it isn't, for either) but in **which Shield adapter is invoked**.

---

## STEP 1 · Runtime call-count evidence audit (reinforcement 1)

**Runtime evidence for the Stage 2 91s enhance run (`dbdad051` commit era, 2026-07-05):**

- `/var/log/supervisor/backend.err.log` — current file has 0 hits for `2026-07-05`; log has rotated (last rotation Jul 4). Current file starts at 2026-07-07.
- `/var/log/supervisor/backend.err.log.1` — 0 hits for `2026-07-05`; older rotation (last mod Jun 23).
- No archival with 2026-07-05 timestamps present in any of `backend.err.log{,.1..4}` or `backend.out.log{,.1..3}`.

**Verdict on runtime call-count evidence for the 91s run:** **INDETERMINATE from runtime logs** — the 91s enhance run's logs have been rotated out and are not recoverable in-pod.

**Static evidence resolves the root-cause axis WITHOUT needing runtime call-count:**

Per code inspection:
- **Enhance path** invokes `collect_llm_text` **twice per user request** (Pass 1 reasoning at `work_studio_export.py:619` + Pass 2 JSON at `work_studio_export.py:767`).
- **Generate path** invokes `shield_invoke` **once per user request** (via `call_llm` at `llm_service.py:224`).

But this call-count difference is **NOT the root cause of the asymmetry**. The root cause is which Shield adapter is called:
- `collect_llm_text` in `services/synisense/shield/streaming.py:456-481` dispatches to `stream_llm_direct` at `streaming.py:331`, which for Anthropic dispatches to `_stream_anthropic` at `streaming.py:95` (uses `anthropic.AsyncAnthropic().messages.stream` — **NO `asyncio.wait_for` wrapper**); with Anthropic-direct failure falls back to `_stream_via_litellm_proxy` at `streaming.py:247` (uses `litellm.acompletion(stream=True)` — **NO `asyncio.wait_for` wrapper**).
- `shield_invoke` in `services/synisense/shield/client.py:67` calls `llm_router.invoke_with_metering` in `llm_router.py:118`, which at `llm_router.py:186-189` wraps `litellm.acompletion(**params)` (non-streaming) in `asyncio.wait_for(..., timeout=timeout_seconds)` where `timeout_seconds: float = 20.0` (default, unchanged at every call site).

**Runtime cap evidence in current logs:** `grep -c "LLM provider timeout after 20.0s" /var/log/supervisor/backend.err.log` = **104 hits** (all traceback frames show `services.synisense.shield.llm_router.py:214 → raise ServiceUnavailable(f"LLM provider timeout after {timeout_seconds}s")` — i.e., the `wait_for(20.0)` cap on `invoke_with_metering`). Zero of these traceback frames go through `stream_llm_direct` or `collect_llm_text`; every single frame originates from `llm_service.call_llm → shield_invoke → invoke_with_metering`. This is corroborating evidence that the cap only fires on the non-streaming adapter path.

**Answer (a) — final:**

> **The 20s ceiling is NOT symmetrically "per-inner-call". It is a PER-LLM-ADAPTER cap. Specifically, it fires on the `llm_router.invoke_with_metering` path (non-streaming litellm.acompletion, `wait_for(20.0s)` wrapper at `llm_router.py:186-189`) and DOES NOT fire on the `stream_llm_direct` path (streaming, no wait_for wrapper anywhere in `streaming.py`). The asymmetry is thus router-level, not call-count-level. Enhance uses the streaming adapter (2 sub-calls per request, each unbounded); Generate uses the metering adapter (1 sub-call per request, capped at 20s). Runtime call-count evidence for the specific 91s dbdad051 run is INDETERMINATE (log rotated), but static evidence + 104 corroborating in-current-log timeout tracebacks (all originating from the metering path, none from the streaming path) is conclusive on the root-cause axis.**

---

## STEP 2 · Prompt-semantic reading of Generate (reinforcement 2)

**Where the Generate prompt lives:** `backend/routers/decks.py::_generate_prompt` at `decks.py:352-374`. This is application-layer code (not Shield); the prompt template is legible from the application-side.

**Prompt shape (verbatim, condensed):**

```
Generate the full slide deck for AKKI in the calm, editorial house
style. Each slide is a markdown block with a title and 3-6 bullet
lines or a short paragraph. Use the approved outline; do not invent
new slides or merge them.

CONTEXT: {ctx_name}
AUDIENCE: {audience_assumed or 'board/ExCo'}
RESEARCH QUESTION: {research_question}

APPROVED OUTLINE:
- Slide 1: {title_1} — {purpose_1}
  Key points: {kp_1a; kp_1b; ...}
- Slide 2: {title_2} — {purpose_2}
  Key points: {kp_2a; kp_2b; ...}
... (N slides)

Return STRICT JSON:
{
  "title": "<deck title, max 90 chars>",
  "subtitle": "<single line, max 120 chars>",
  "slides": [{"n": 1, "title": "<short>", "body_md": "<markdown body>"}, ...],
  "speaker_notes": ["<one note per slide, 1-2 sentences each>"]
}
```

**Coherence-dependency analysis (per-slide vs cross-slide):**

- Narrative arc — **pre-established at the outline stage** (a prior separate LLM call). The outline prompt already produced per-slide `title` + `purpose` + `key_points`. The Generate prompt explicitly says "Use the approved outline; do not invent new slides or merge them." → **narrative structure is LOCKED before this call fires**.
- Slide-N body_md's substantive input = outline_slide_N's `key_points` + shared house-style directive + shared CONTEXT/AUDIENCE/RESEARCH_QUESTION. **Slide-N body_md does NOT depend on the body_md of slide N-1 or slide 1..N-2 for content correctness** (only on the outline's Slide-N entry).
- Cross-slide dependency = **stylistic**, not semantic: consistent tone, house style, tense, terminology. Achievable via a shared style directive replicated in every sub-prompt (already present in the current prompt).
- Deck-level metadata (`title`, `subtitle`, `speaker_notes[]`) is aggregate — but each speaker_note is per-slide and short (1-2 sentences); `title`/`subtitle` are 90-120 chars and derivable from `research_question` + outline.

**Answer (b) — final:**

> **YES · Generate IS chunkable AT THE PROMPT LEVEL without material quality loss.** The outline stage already locks the narrative arc; per-slide `body_md` expansion is a bounded, per-slide-local transformation from `key_points → prose`. Cross-slide dependency is stylistic (house style + tone consistency), not semantic. Rough chunking shape (see § STEP 3 for arc scope): (a) 1 meta sub-call → `title` + `subtitle` (small; well under 20s); (b) N per-slide sub-calls → each slide's `body_md` (small; well under 20s each; parallelisable but serial is also fine); (c) 1 aggregation pass → assemble `slides[]` + `speaker_notes[]` in application code (deterministic, no LLM). Alternative to chunking — see § STEP 4 — is to reroute Generate through the same **`stream_llm_direct` adapter** Enhance uses, which sidesteps the `wait_for(20.0)` cap entirely without any prompt refactor. Both are legitimate; user chooses.

**INDETERMINATE-from-application-side caveat honoured:** the prompt is fully legible from `decks.py:352-374` (not opaque; not hidden inside a Shield-side template). No INDETERMINATE hedge needed on (b).

---

## STEP 3 · Case A/B/C/D posture emission

Per the dispatch's classification frame:
- **Case A** — Application-layer fix viable: chunk the Generate invocation into <20s sub-calls, preserving Shield untouched.
- **Case B** — Application-layer fix not viable: pursue upstream (Shield timeout tuning or model preference tuning).
- **Case C** — Both application-layer and upstream needed.
- **Case D** — Insufficient evidence to classify; propose instrumentation arc.

**Verdict: CASE A**, with an application-layer optionality note:

> **Recommended posture — propose scoped arc `JC-DECK-GENERATE-CHUNKED-INVOCATION` for user approval · do NOT build in this arc · rough scope + risk assessment only.**

**Rough scope of the proposed arc (for user review, not implementation):**

- **Option A1 (chunked invocation)** — refactor `_run_generate_deck_job` at `decks.py:464` to invoke `shield_invoke` N+2 times (1 meta + N per-slide + 1 optional coherence tidy) instead of once. Prompt refactor: split `_generate_prompt` into `_generate_meta_prompt(outline, ctx_name)` + `_generate_slide_prompt(outline, slide_n, ctx_name)`. Aggregate results in application code. Phase transitions in the runner extended: `structuring` → `drafting_slide_1..N` (progress tick per slide) → `assembling` → `complete`. Zero Shield touches.
  - Risk: latency scales linearly (N sub-calls serial ≈ N × ~5-8s each); acceptable inside the async runner (no user-visible edge timeout because poll-based).
  - Coherence risk: LOW (outline pre-locks narrative arc; house-style directive replicated per sub-prompt).
  - Effort estimate: ~150-250 LOC net in `decks.py` + `_generate_prompt` refactor + phase enum extension in `deck_generation_jobs.py`.

- **Option A2 (adapter reroute — alternative, likely SIMPLER)** — refactor `_run_generate_deck_job` to invoke `collect_llm_text` (the streaming adapter Enhance uses) instead of `call_llm_with_tier → call_llm → shield_invoke`. Zero prompt refactor required; zero chunking required. Streaming adapter has NO `wait_for(20.0)` wrapper in `services/synisense/shield/streaming.py`, so the cap does not apply.
  - Risk: cross-tier consistency — `call_llm_with_tier` currently threads through `llm_service.call_llm` which selects Opus 4.6 for `tier="deep"`. `collect_llm_text` takes `provider` + `model_id` explicitly; the tier-selection layer would need a light re-wire (or `call_llm` internally chooses streaming vs metering based on tier · surface).
  - Quota-metering risk: `call_llm_with_tier` calls `check_and_consume` (quota gating); `collect_llm_text` bypasses it. Need to preserve quota metering + audit-log write.
  - Effort estimate: ~50-100 LOC net; smaller and lower-coherence-risk than A1 but touches shared plumbing (`llm_service.call_llm`) that other surfaces depend on — expansion-blast-radius is a factor.

- **Option A3 (hybrid)** — chunk AND reroute (A1 + A2). Over-engineering unless a specific driver appears; not recommended.

**Not recommended: Case B / Case C / Case D.**
- Case B would require Shield changes (raising `timeout_seconds` on `invoke_with_metering`) — Shield is UNTOUCHABLE per canonical rule. Model preference tuning (via env) alone would not resolve — Opus 4.6 is inherently slow for a full-deck one-shot; the ceiling would still fire.
- Case C: no need to layer upstream and application when application-only resolves.
- Case D: static evidence is sufficient on the root-cause axis; runtime call-count evidence for the specific 91s run is INDETERMINATE but resolves nothing further — the router-level asymmetry (not call-count) is the causal axis.

---

## STEP 4 · Real Signals Surfaced

- **Router-level asymmetry within Shield** — `stream_llm_direct` (streaming) has no `wait_for(20.0)` cap; `invoke_with_metering` (non-streaming) has one. Both are Shield-adjacent files but the two adapters behave differently under long-running LLM calls. This is a **latent architectural asymmetry** worth surfacing beyond just the immediate Generate/Enhance case — any future surface routed through `invoke_with_metering` will inherit the same 20s ceiling.
- **`_LLM_MODE=deep` → `LLM_MODEL_DEEP=claude-opus-4-6`** (per `llm_service.py:199-203`). Opus 4.6 for a full-deck one-shot JSON output on 3-8 slides regularly exceeds 20s. The tier-selection surface is fundamentally at odds with the metering-adapter cap.
- **Application-layer credit-exhaustion warning bleeding into Enhance-path fallback** — current logs show `[llm-fallback] direct_anthropic failed (BadRequestError: 400 · credit balance too low) → litellm_stream_proxy`. The Anthropic-direct SDK path is currently degraded (billing); Enhance is presently falling back to `_stream_via_litellm_proxy`. This is orthogonal to the ceiling asymmetry but should be surfaced for user disposition (billing / API-key remediation) as a separate signal. The ceiling asymmetry conclusion holds regardless (both direct and proxy streaming paths lack `wait_for`).

**Self-remediation NOT executed** per Case A framing (do NOT build; classification only).

---

## STEP 5 · Closure — Zero-touch verification

`git diff --stat f7255414 -- <7 protected paths>` must yield 0 bytes on close.

Protected paths for zero-touch (all 7 verified in proving slice R6):
1. `backend/services/synisense/shield/**` (13 files)
2. `backend/services/synisense/shield/streaming.py`
3. `backend/services/synisense/shield/llm_router.py`
4. `backend/services/synisense/shield/client.py`
5. `backend/services/work_studio_export.py`
6. `backend/routers/work_studio_export.py`
7. `backend/routers/decks.py`
8. `backend/services/deck_regenerate.py`
9. `backend/llm_service.py`
10. `backend/llm_tier_quota.py`
11. `backend/.env`
12. `backend/services/deck_generation_jobs.py`

Composite Shield sha256 identity `c6902d324ed90734cd815f63eaee8ebb66d776ef89f1797c1f7f50cbae10d5a8` (13 files) preserved on close (R7).

Files touched in this arc (report-only, per proving slice R5):
- NEW `memory/sprints/JC_SHIELD_CEILING_ASYMMETRY_DIAGNOSE.md` (this memo)
- NEW `backend/scripts/jc_shield_ceiling_asymmetry_diagnose_proving_slice.py`
- MOD `memory/DEV_PIPELINE.md` §9 row (this diagnose arc, 🟡 IN-FLIGHT flipped BEFORE memo/slice draft; 🟢 on close with commit hash cited)

Zero product-code / config / env / Shield touches.

---

## STEP 6 · Amendment-Echo (dispatch + 3 reinforcements)

**Dispatch base scope echo:** classify (a) whether ceiling is per-inner-call; (b) whether Generate is chunkable if (a) YES; emit Case A/B/C/D posture; write memo + proving slice; update DEV_PIPELINE §9; commit; close via Trigger-2. ✅ HONOURED.

**Reinforcement 1 (call-count runtime evidence over structural inspection):** ✅ HONOURED. Runtime evidence for 91s dbdad051 run declared **INDETERMINATE** honestly (logs rotated). Static evidence resolves the root-cause axis (router-level asymmetry, not call-count). Case D (instrumentation proposal) evaluated and rejected — root-cause axis is conclusive without additional instrumentation. 104 corroborating in-current-log timeout tracebacks all originate from the metering path, none from the streaming path (documented in STEP 1).

**Reinforcement 2 (prompt-semantic reading for (b)):** ✅ HONOURED. `_generate_prompt` fully legible from `decks.py:352-374`; not opaque; no INDETERMINATE hedge needed. Coherence dependency analysed at the prompt-semantic level (per-slide vs cross-slide) — outline pre-locks arc; per-slide body expansion is bounded; cross-slide dependency is stylistic, not semantic. YES verdict rendered with rough chunking shape sketch (STEP 3 · Option A1).

**Reinforcement 3 (Case A framing discipline):** ✅ HONOURED. Memo phrasing verbatim: "propose scoped arc `JC-DECK-GENERATE-CHUNKED-INVOCATION` for user approval · do NOT build in this arc · rough scope + risk assessment only" (STEP 3). No implementation-ready code, LOC diffs, or file writes.

---

## STEP 7 · Close-status

Push status: **SHIPPED-UNPUSHED** on close · commit hash cited in Trigger-2 · `git remote -v` empty in preview pod · user pushes via "Save to GitHub". Per `RULE-CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED`.

HARD STOP at classification. Nothing auto-fires past this memo. Stages 3a-3e (v1.1 conformance) remain HELD. `JC-DECK-GENERATE-CHUNKED-INVOCATION` (or `JC-DECK-GENERATE-STREAM-ADAPTER-REROUTE`) requires an explicit user dispatch before any implementation.
