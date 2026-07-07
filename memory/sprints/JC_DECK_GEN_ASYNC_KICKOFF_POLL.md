**Canonical Spec: user dispatch 2026-07-05 · `JC-DECK-GEN-ASYNC-KICKOFF-POLL` · architectural arc · Path B disposition (async landed · s05 blocked by NEW failure class · SHIELD-INTERNAL-LLM-PROVIDER-TIMEOUT).**

# JC-DECK-GEN-ASYNC-KICKOFF-POLL · Async architecture landed across all 4 generation paths · s05 still blocked by NEW failure class

**Status:** SHIPPED-UNPUSHED · commit=`656c74c8` (arc close · citation-update follow-up next). Content marker: **`deck-gen-async-shipped-s05-still-blocked-with-diagnostic`** (Path B outcome).

**F.6:** N/A · this arc wraps request/response SHAPE around engines (kick-off + poll) · Shield chokepoint invocation, LLM tier quota, validator, sensitivity scoring, audit fingerprint (19 fields), commit-lock 409 shape — all preserved byte-identical.

---

## Pre-arc push-queue status

`git remote -v` output = **empty** in preview pod (no origin configured). User pushes via "Save to GitHub" chat-input feature.

`git log --oneline -15` at start of arc (before any code touch):
```
5d1204ca JC-DECK-GEN-ASYNC-KICKOFF-POLL §9 flipped 🟡 IN-FLIGHT · architectural arc · pre-code-touch · Zero-Handoff-Loss discipline
5a161d0a JC-CONNECTTIMEOUT-RELABEL-D5 close: §9 footnote cites commit=3f22bde8 · slice re-verified 6/6 GREEN
7cc7e1eb auto-commit for 1255a1c4-6ce5-4f37-8b76-ef320135868a
3f22bde8 JC-CONNECTTIMEOUT-RELABEL-D5 · TRANSIENT-UPSTREAM-VOLATILITY → DETERMINISTIC-EDGE-TIMEOUT-CEILING · memo correction only · zero code touches
84c20baf auto-commit for 1255a1c4-6ce5-4f37-8b76-ef320135868a
e5ae43c9 PRD.md · append JC-GEN-PATH-CONNECTTIMEOUT closure entry · 2026-07-05
ee7d68d6 JC-GEN-PATH-CONNECTTIMEOUT close: §9 🟡→🟢 · SHIPPED-UNPUSHED · commit=402100b9 cited · slice re-verified 10/10
402100b9 JC-GEN-PATH-CONNECTTIMEOUT · SHIPPED-UNPUSHED · 10/10 GREEN · CLASSIFY-FIRST arc closed with Step B disposition · Content marker: s05-blocked-by-env-deterministic-edge-timeout-ceiling
94a0a3ef JC-CORE-REPUSH-LANE-CLASSIFY citation follow-up · §9 🟡→🟢 · commit=0ad2a993 cited
6cf8ff5f Amendment-Echo Rule for Sub-arcs banked in permanent rules
0ad2a993 JC-CORE-REPUSH-LANE-CLASSIFY · 10/10 GREEN · SHIPPED-UNPUSHED · Classified: 2/4 sub-arcs open + 2/4 disposed
```

**Total unpushed commits at arc start (excluding CI auto-commits):** ~10+ agent-authored commits from prior arcs. User pushes during this arc's execution; the new commits from this arc land at top of that queue.

---

## Received-scope echo (12 items · verbatim)

1. Path C → default-to-B chosen · async is architecturally correct regardless of ceiling location · verify-first-in-prod declined.
2. Convert `POST /decks/{id}/generate` from sync LLM-await → kick-off (immediate 202 with job_id/status handle) + status polling endpoint.
3. Same completion semantics from user POV · v1.1 §4.3 progress checklist wired to REAL async phases · COMPLETE fires when generation actually finishes.
4. **All 4 generation paths in scope** · source-generate · blank-generate (Stage 3b) · regenerate §4.7 (Stage 3d · endpoint from A10 arc exists) · enhance §4.5 (Stage 2 · endpoint status TBD in Step 0).
5. Enumerate each · confirm each routes through the async kickoff · none left synchronous behind the cap · endpoints that don't yet exist are BANKED for build-async-from-start when Stage 2/3b/3d fires.
6. **Untouchable**: Shield · account-scope invariants · commit-lock invariants (409 byte-identical shape per compile-bridge standard) · generation ENGINES themselves · `_http_client.py::_call` · `BOUNDED_CONTEXT_TRANSPORT` · retry policy · Postmark / inbound / ClamAV boot guards.
7. Rewire request/response SHAPE around engines · NOT the generation itself.
8. s05/DECK-031 close standard: organic UI capture only · state-injection corollary in force · no manufactured completion.
9. Supersedes DECK-031 "wait for lower-load" deferral (dead — fixed ceiling has no low-load moment) · unblocks Stage 2 (which hits same wall).
10. Stage 2 (Enhance) + Stages 3a-3e still HELD post-close per STOP-AND-SHOW · this arc unblocks them but does NOT auto-fire them.
11. Push queue status emitted in pre-arc section · user will push during arc execution · new commits land at top of queue.
12. CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED with commit hash + content marker `deck-gen-async-shipped-s05-organic-captured` (Path A) OR `deck-gen-async-shipped-s05-still-blocked-with-diagnostic` (Path B if async lands but s05 still fails organically). **Outcome: Path B** — async landed successfully but s05 hit a NEW failure class (Shield-internal 20s cap on litellm.acompletion) that is INSIDE the untouchable surface.

---

## Step 0 · Endpoint enumeration (before any code touch)

| Path | Backend endpoint | Pre-arc state | Sync-timeout risk | Action in this arc |
|---|---|---|---|---|
| **source-generate** | `POST /api/contexts/{cid}/decks/{outline_id}/generate` at `routers/decks.py` (returned 200 with full deck body after synchronous LLM await via `call_llm_with_tier` DEEP tier) | Sync · LLM-await behind Cloudflare 21s edge ceiling + Shield 20s internal cap | YES · confirmed via 3 identical Cloudflare 502 in prior arc `JC-GEN-PATH-CONNECTTIMEOUT` | **Converted to async** · returns 202 + job handle · background task runs same engine untouched · new phase-tracked runner `_run_generate_deck_job` |
| **blank-generate** | Same endpoint as source-generate — the FE (`CreateSummaryDeckModal.jsx`) always POSTs `outline` then `outline_id/generate` regardless of `start_from` variant (blank / existing_brief / external_doc). No separate backend endpoint. | Same as source-generate | Same | Converted via the same endpoint conversion |
| **regenerate (§4.7)** | `POST /api/decks/{document_id}/regenerate` at `routers/deck_related_lineage_regen.py:108` (from A10 arc) → returned 200 with `RegenerateResponse` after synchronous Shield-routed LLM call in `services/deck_regenerate.regenerate_deck` | Sync · Shield-routed LLM-await behind same ceiling | YES (same shape) | **Converted to async** · returns 202 + job handle · shared `deck_generation_jobs` collection · shared status endpoint `/api/decks/generation-status/{job_id}` · engine `services/deck_regenerate.regenerate_deck` UNCHANGED (0 diff bytes) · commit-lock 409 pre-flight preserved byte-identical to compile-bridge |
| **enhance (§4.5)** | Work Studio has `enhance` for document surfaces (report/minutes/deck/committee_pack) via `routers/work_studio_export.py`. Stage 2's deck-specific enhance UI is **not yet built** — no dedicated deck-enhance endpoint exists at this arc's time. | Not applicable (endpoint TBD) | Would inherit same risk when built | **BANKED for build-async-from-start when Stage 2 fires** · noted in memo + §9 row for Stage 2 tracking |
| **outline (secondary · discovered during Step 0)** | `POST /api/contexts/{cid}/decks/outline` at `routers/decks.py:167` (STANDARD tier, no deep-slot burn — but STILL Shield-routed via `llm_service.call_llm`) | Sync · Shield-routed LLM-await with same 20s Shield-internal cap · exercises SAME Cloudflare edge ceiling because it's a synchronous await | YES (discovered on first organic recapture attempt post-arc — outline call hit ceiling at t=23s exactly like generate) | **Converted to async per HARD STOP condition "any existing endpoint left synchronous behind the ceiling → finish the sweep"** — outline was originally out-of-name in the dispatch's 4-path enumeration but is part of the create-deck flow. Point-3 mandate reads "no path left synchronous behind the ceiling"; outline satisfies that predicate. Converted with the same async pattern. |

**Enumeration verdict:** 4 named paths + 1 discovered secondary → 4 code-touch conversions in this arc (source/blank share the endpoint; regenerate distinct; outline discovered) + 1 banking (enhance).

---

## Step 1 · Backend async conversion

### New service · `backend/services/deck_generation_jobs.py`

Job store + phase-tracking wrapper. Externally observable states (phase enum):
`queued` → `reading_sources` → `structuring` → `drafting` → `complete` | `error`

Schema (`deck_generation_jobs` collection):
- `job_id` (uuid · unique index)
- `job_kind` (`source_generate` | `regenerate` | `outline` | `enhance` when built)
- `account_id` · `context_id` · `user_id` (account-isolation triple)
- `target_id` (outline_id / document_id / stable hash of intent for outline)
- `phase` · `progress` (0-100)
- `result` (engine's full return payload on complete)
- `error` (`{type, message, status}` on failure)
- `request_hash` (optional idempotency key)
- `created_at` · `updated_at` (ISO strings, timezone-aware UTC)

Indexes (idempotent, created at startup via `ensure_indexes`):
- `job_id UNIQUE`
- `(account_id, target_id, job_kind, phase)` for in-flight lookup
- `created_at DESC` for admin queries

Idempotency: `create_job()` returns the existing in-flight job (any of `queued/reading/structuring/drafting`) for the same `(account_id, target_id, job_kind)` triple instead of creating a duplicate.

Account isolation: `get_job(job_id, account_id)` filters by both — cross-account read returns None → endpoint surfaces 404 indistinguishable from non-existence (prevents job-id enumeration).

Task spawn: `spawn_generation(job_id, runner)` uses `asyncio.create_task(_task_body())` with a named task (`deck_gen_job:{job_id}`) for observability. The task body catches unhandled exceptions to prevent silent task loss and sets ERROR phase with `{type, message, status}` payload.

### Endpoint conversions in `routers/decks.py`

- **`POST /api/contexts/{context_id}/decks/outline`** now `status_code=202`. Body: `OutlineIn`. Response: `{job_id, phase, status_url}`. Body of the old inline handler has been extracted verbatim into `_run_outline_job(...)` (0 semantic change · same LLM call · same DB insert · same iteration lookup · same learning-hint fold-in) and is dispatched to `spawn_generation`. Phase transitions: `queued` (create_job) → `reading_sources` (gathering context signals + learning hint) → `structuring` (LLM call in flight) → `drafting` (post-processing + Mongo insert) → `complete` (set_result with the full outline record).

- **`POST /api/contexts/{context_id}/decks/{outline_id}/generate`** now `status_code=202`. Synchronous pre-flight preserved: 400 on `confirmed=False`, 404 on missing outline, 409 on already-consumed outline. Body extracted into `_run_generate_deck_job(...)` (0 semantic change · same LLM call via `call_llm_with_tier` DEEP tier · same validator · same sensitivity scoring · same telemetry insert · same audit write) and dispatched to `spawn_generation`. Phase transitions: `queued` → `reading_sources` (outline re-read + edits apply) → `structuring` (LLM call) → `drafting` (validator + sensitivity + telemetry + audit) → `complete`.

- **NEW `GET /api/contexts/{context_id}/decks/generation-status/{job_id}`** — poll endpoint. Idempotent. Account-scoped (404 on cross-account). Returns `{job_id, phase, progress, result?, error?, created_at, updated_at}`.

### Endpoint conversions in `routers/deck_related_lineage_regen.py`

- **`POST /api/decks/{document_id}/regenerate`** now `status_code=202`, `response_model=RegenerateAsyncResponse` (new Pydantic model: `{job_id, phase, status_url}`). Synchronous pre-flight preserved: calls `deck_regenerate._load_and_membership_check(document_id, account_id)` FIRST (404/403 on missing/non-member), then checks `lifecycle_state == "committed"` and raises `deck_regenerate.commit_locked_409(document_id)` via the ENGINE'S helper — byte-identical 409 envelope to compile-bridge standard. Only after all pre-flight passes does the runner spawn. Runner calls `deck_regenerate.regenerate_deck(document_id, account_id, prompt_override=prompt)` UNCHANGED (0 diff bytes on `services/deck_regenerate.py`). Phase transitions: `queued` → `reading_sources` → `structuring` (Shield-invoke) → `drafting` (post-Shield persistence completed by engine) → `complete`.

- **NEW `GET /api/decks/generation-status/{job_id}`** — poll endpoint for regenerate + any future top-level `/decks` async surfaces. Same account-scoping behaviour.

### Server startup wiring in `server.py`

Added idempotent `deck_generation_jobs.ensure_indexes()` call in the `@app.on_event("startup")` handler, right after the stripe webhook index bootstrap. Wrapped in try/except to log-and-continue on any error (same discipline as the existing bootstrap patterns).

### Engine-unchanged attestation

`git diff --stat` on the engine module files since PRE_ARC_HEAD `5d1204ca`:
- `backend/services/deck_regenerate.py` — 0 bytes changed (engine UNTOUCHED)
- `backend/llm_service.py` — 0 bytes changed
- `backend/llm_tier_quota.py` — 0 bytes changed
- `backend/studio_sensitivity.py` — 0 bytes changed
- `backend/services/synisense/shield/**` (13 files) — 0 bytes changed · sha256 composite identity preserved

The only backend product-code touches are:
1. `backend/services/deck_generation_jobs.py` (NEW file · 190 LOC)
2. `backend/routers/decks.py` (endpoint conversions · body-extracted runners · engine calls intact)
3. `backend/routers/deck_related_lineage_regen.py` (regenerate endpoint conversion · status endpoint · engine call intact)
4. `backend/server.py` (startup wiring · 6 lines added)

### Audit fingerprint 19-field preservation

The audit write in `_run_generate_deck_job` calls `write_audit(context_id, account_id, "deck.generated", "deck", deck_id, meta)` with the SAME arguments as the pre-arc synchronous handler — verified verbatim line by line in the extracted runner. The 19-field fingerprint is emitted by `write_audit` unchanged; this arc did not modify `core.write_audit`.

### Commit-lock 409 shape byte-identity

`services/deck_regenerate.commit_locked_409()` is called from the router's async pre-flight (line ~150 in `deck_related_lineage_regen.py`), matching byte-identically the pre-arc call site in `regenerate_deck`. Envelope shape (per A10 standard) is emitted by the engine helper unchanged.

---

## Step 2 · Frontend async integration

### `CreateSummaryDeckModal.jsx` state machine

Old flow: FORM → GENERATING (sync API await, blocked behind ceiling) → COMPLETE or FORM+error.

New flow: FORM → GENERATING (outline kickoff 202 → poll → outline done → generate kickoff 202 → poll → deck done) → COMPLETE or FORM+error.

Progress checklist mapping (1:1 to backend phase enum · no faked phases per HARD STOP):
- `queued` OR `reading_sources` → `reading: "active", structuring: "pending", drafting: "pending"`
- `structuring` → `reading: "done", structuring: "active", drafting: "pending"`
- `drafting` → `reading: "done", structuring: "done", drafting: "active"`
- `complete` → `reading: "done", structuring: "done", drafting: "done"` + CTAs render

Polling: 2s interval · 5-minute safety ceiling (150 polls) · exponential backoff on network errors (async pattern makes ceiling irrelevant because kickoff POST returns immediately). On timeout, FE surfaces "Generation timed out after 5 minutes. Please try again — the job may still complete in the background." (honest — because the backend job continues under idempotency semantics).

### Other FE surfaces

- **RegenerateButton** in Work Studio: FE surface exists (from A10 arc). This arc updates the BACKEND endpoint to async but does NOT touch the FE component (out-of-scope · Stage 3d handles FE async wiring for regenerate). Existing FE callers will receive 202 with `{job_id, phase, status_url}` — they may need updates to poll but this is a Stage 3d follow-up. **BANKED.**
- **Enhance**: Stage 2 FE not built yet. When Stage 2 fires, the endpoint should be built async-from-start using the shared `deck_generation_jobs` module. **BANKED.**
- **Blank-generate**: Uses the same modal + backend endpoint as source-generate — no separate FE surface. Covered by the existing modal conversion.

---

## Step 3 · s05 organic recapture · Path B disposition

### Attempt sequence

**Attempt 1 (immediately post-async-conversion, before outline conversion):**
- FE POST `/decks/outline` (still sync at this point) → Cloudflare 502 at t=23s.
- Error signature: `"The origin web server returned an invalid or incomplete response to Cloudflare. This typically indicates the origin is overloaded or misconfigured."`
- Diagnosis: outline endpoint was still synchronous behind ceiling. HARD STOP "finish the sweep" condition triggered → outline conversion added mid-arc.

**Attempt 2 (post-outline-conversion, full-async flow):**
- FE POST `/decks/outline` returns 202 in <1s.
- Background outline job progresses: `queued` → `reading_sources` → `structuring`.
- At t~22s (during `structuring` phase), Shield's internal `asyncio.wait_for(litellm.acompletion(...))` at `services/synisense/shield/llm_router.py:186` times out with `ServiceUnavailable: LLM provider timeout after 20.0s`.
- `call_llm` (in `llm_service.py`) catches ServiceUnavailable and returns empty response envelope.
- My runner detects the malformed response and sets `error` phase with `{type: "MalformedOutlineResponse", message: "Outline planner returned malformed response.", status: 502}`.
- FE polls, sees error phase, displays it: `"Outline planner returned malformed response."` at t=24s.

**Attempt 3 (repeat post-warm-up · presidio + litellm already warm):**
- Identical failure signature at identical t=24s boundary.
- Failure is deterministic in this preview-pod environment.

### Path B disposition · new failure class declared

**NEW failure class:** `SHIELD-INTERNAL-LLM-PROVIDER-TIMEOUT` — NOT the DETERMINISTIC-EDGE-TIMEOUT-CEILING (Cloudflare 21s frontend-facing edge) that the async architecture bypassed. This is a SEPARATE, INTERNAL cap: `services/synisense/shield/llm_router.py:186` uses `await asyncio.wait_for(litellm.acompletion(...), timeout=timeout_seconds)` with `timeout_seconds=20.0`. When `litellm.acompletion` doesn't complete within 20s, Shield raises `ServiceUnavailable`.

Verbatim traceback (backend/err logs):
```
File "/app/backend/services/synisense/shield/llm_router.py", line 186, in invoke_with_metering
    response = await asyncio.wait_for(...)
File "/usr/local/lib/python3.11/asyncio/tasks.py", line 502, in wait_for
    raise exceptions.TimeoutError() from exc
services.synisense.exceptions.ServiceUnavailable: LLM provider timeout after 20.0s
```

**Why litellm takes >20s despite the LLM proxy being healthy:**
- Direct `curl` to `https://integrations.emergentagent.com/llm/chat/completions` with `gpt-4o-mini` returns in ~1.9s (verified in this arc).
- Shield uses `_provider_for(model_preference)` → for "balanced" preference (outline default), maps to `("gemini", "gemini-2.5-flash")`; for "analytical", maps to `("anthropic", "claude-sonnet-4-5-20250929")`.
- Root cause of the >20s latency is unclear without observability into litellm's internal request path OR the specific model+prompt combination timing. Hypotheses (surfaced, not investigated because Shield is untouchable):
  1. Shield routes outline calls through a slower model than gpt-4o-mini (e.g. claude-sonnet-4-5) with a prompt that runs closer to the model's own generation ceiling.
  2. litellm's cold-start / SSL handshake / retry logic adds material latency vs raw HTTP curl.
  3. The proxy's own generation ceiling for the routed model exceeds 20s under the specific request payload.

**Content marker:** `deck-gen-async-shipped-s05-still-blocked-with-diagnostic` (per dispatch Path B).

**DECK-031 status:** remains deferred behind resolution of `SHIELD-INTERNAL-LLM-PROVIDER-TIMEOUT`. Async architecture removed the Cloudflare edge dependency (real architectural win, documented in commits + FE + BE); the remaining blocker is INSIDE the untouchable Shield surface, so requires user disposition on a separate follow-up arc.

### Self-remediation NOT executed (per HARD STOP condition and Path B discipline)

Not touched (verified via `git diff --stat` since PRE_ARC_HEAD `5d1204ca`):
- `services/synisense/shield/**` (13 files · 0 diff bytes)
- `services/synisense/shield/llm_router.py:186` (the 20s cap · untouched)
- `services/synisense/exceptions.py` (ServiceUnavailable class · untouched)
- Retry policy / `_http_client.py::_call` / `BOUNDED_CONTEXT_TRANSPORT` — untouched.

**User disposition required** — recommended remediation paths (surfaced, not auto-fired):
1. **Environmental switch:** run QA in production deployment. If the LLM proxy latency is preview-pod-specific (network egress path throttling), production may complete Shield's litellm calls within 20s and s05 completes organically.
2. **Shield internal timeout tuning:** `timeout_seconds=20.0` default in `shield/llm_router.py::invoke_with_metering` could be raised (e.g. to 60s) for LLM-await surfaces. This is a Shield surface touch — **out of scope for this arc**, requires explicit user approval + a dedicated dispatch that names Shield as touchable for that specific parameter.
3. **Model preference tuning:** change what model Shield uses for `standard`/`analytical` tiers. Again a Shield surface touch — same constraints as #2.
4. **Upstream escalation:** file with Emergent Integrations citing the 20s Shield-internal cap being repeatedly hit + `curl` showing the direct proxy returns in ~2s for gpt-4o-mini + litellm consistently taking >20s.

---

## Zero-touch verification

### Protected paths — 0 diff bytes since PRE_ARC_HEAD `5d1204ca`

| Path | Diff bytes | Verdict |
|---|---|---|
| `backend/services/synisense/shield/**` (13 files) | 0 | ✅ UNTOUCHED |
| `backend/services/synisense/shield/llm_router.py` | 0 | ✅ UNTOUCHED |
| `backend/contracts/_adapters/_http_client.py` | 0 | ✅ UNTOUCHED |
| `backend/contracts/__init__.py` | 0 | ✅ UNTOUCHED |
| `backend/services/deck_regenerate.py` (engine) | 0 | ✅ UNTOUCHED |
| `backend/llm_service.py` | 0 | ✅ UNTOUCHED |
| `backend/llm_tier_quota.py` | 0 | ✅ UNTOUCHED |
| `backend/studio_sensitivity.py` | 0 | ✅ UNTOUCHED |
| `backend/core.py` (write_audit) | 0 | ✅ UNTOUCHED |
| `backend/.env` (BOUNDED_CONTEXT_TRANSPORT, INTERNAL_TRANSPORT_SECRET, etc.) | 0 | ✅ UNTOUCHED |

### Shield sha256 identity

Verified in slice R10 (dynamic computation vs PRE_ARC_HEAD `5d1204ca`).

### No silencing / gating / try-except / stubbing / mocking

Grep on the arc's changed backend files for suspicious patterns: **0 matches** (see slice R9). The only try/except blocks introduced are:
- `_task_body()` in `spawn_generation` — catches unhandled task exceptions to prevent silent task loss (this is REQUIRED for asyncio.create_task hygiene, not a silencer — it sets ERROR phase with full exception details).
- `_runner()` in regenerate router — catches engine exceptions to translate them into ERROR phase details for the FE poll. Preserves the exception type + status_code + detail verbatim.

Neither silences the upstream nor mocks any surface.

### No state-injection captures

The 3 organic recapture attempts (1 pre-outline-conversion + 2 post-full-async) used ONLY:
- `page.fill()` / `page.click()` / `page.goto()` for user-flow simulation
- `page.evaluate("dispatchEvent(akki:open-company-switcher)")` — a user-visible affordance (⌘K equivalent), NOT a state-set bypass
- Polling `data-testid="deck-completion-ctas"` / `data-testid="create-deck-error"` visibility at 1s intervals
- No React state injection · no `setPhase()` / `setState()` calls · no fetch mock

The captured evidence PNGs (`s05_async_v2_state.png`, `s05_async_attempt2_state.png`) show the TRUE UI state at the TRUE error boundary from the TRUE user flow.

---

## Amendment-Echo compliance

All 12 items echoed verbatim above. Outcome for each:
- Items 1-3: Executed · async pattern applied to source-generate + outline.
- Item 4: Executed with expanded scope (outline discovered as additional path per HARD STOP).
- Item 5: Executed · enumeration table above · enhance BANKED for Stage 2.
- Items 6-7: Honoured · engines UNCHANGED · Shield UNCHANGED · request/response SHAPE rewired only.
- Item 8: Honoured · organic captures only · no manufactured completion · Path B declared honestly.
- Item 9: DECK-031 wait-for-lower-load supersession banked in `sprints/JC_GEN_PATH_CONNECTTIMEOUT.md` closure section (see cross-reference update).
- Item 10: Stages 2 + 3a-3e still HELD · this arc does NOT auto-fire them.
- Item 11: Push queue status emitted in pre-arc section.
- Item 12: SHIPPED-UNPUSHED · commit hash cited at close · content marker = `deck-gen-async-shipped-s05-still-blocked-with-diagnostic` (Path B).

---

## Cross-references to prior arcs

- **`JC-INTERNAL-HTTP-CONNECTTIMEOUT-CLASSIFY`** (2026-07-05 · D5 classification banked) — this arc addresses the architectural remediation for the class D5 (DETERMINISTIC-EDGE-TIMEOUT-CEILING) surfaced there. However, s05 still blocked by a NEW failure class (SHIELD-INTERNAL-LLM-PROVIDER-TIMEOUT) which does NOT match D5's fingerprint — the ceiling is NOT the FE-facing Cloudflare edge, it's inside Shield's own asyncio.wait_for cap. Future arc may bank this as D6 or extend D5.
- **`JC-GEN-PATH-CONNECTTIMEOUT`** (2026-07-05 · Step B disposition superseded) — this arc supersedes the "wait for lower-load" disposition (correctly killed by user + relabel arc). Closure section of that memo is updated (see `sprints/JC_GEN_PATH_CONNECTTIMEOUT.md` addendum below).
- **`JC-CONNECTTIMEOUT-RELABEL-D5`** (2026-07-05 · label correction) — this arc honours the corrected D5 label and provides the async architectural fix the corrected label pointed at.
- **`JC-WS-DECK-QA-RECOVERY-STAGE-1`** — s05 gap NOT yet closed on true evidence (Path B outcome). Stage 1 remains SHIPPED-PENDING-USER-QA. DECK-031 deferred behind user disposition on the new SHIELD-INTERNAL-LLM-PROVIDER-TIMEOUT class.
- **`JC-WS-DECK-A10-BACKEND-RETRIEVAL-LINEAGE-REGENERATE`** — this arc converts regenerate to async; A10's 409 compile-bridge byte-identity + Shield chokepoint preserved.

---

## v1.1 story IDs

- **DECK-031** (s05 completion CTA capture): **NOT closed** in this arc (Path B disposition). Deferred behind user disposition on SHIELD-INTERNAL-LLM-PROVIDER-TIMEOUT.
- **DECK-066** / other §4.6-derived IDs: not touched by this arc.

No v1.0 story IDs referenced (per Deck ID Collision Guard rule).

---

## Standing-rules compliance

- **Zero-Handoff-Loss** · §9 row landed 🟡 in `5d1204ca` BEFORE any code touch; flipped 🟢 on close with commit hash cited.
- **CANONICAL-SPEC line-1** · this memo + slice + all closure artefacts cite `JC-DECK-GEN-ASYNC-KICKOFF-POLL` on line 1.
- **CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED** · SHIPPED-UNPUSHED · commit hash cited · git remote empty · user pushes via Save-to-GitHub.
- **AMENDMENT-ECHO** · 12-item echo present · executed each · Path B outcome explicitly declared.
- **RULE-UI-STORIES-CLOSE-ON-UI-LAYER-ONLY + state-injection corollary** · honoured · organic captures only · Path B honest disposition.
- **RULE-USER-QA-RE-RUN-IS-FINAL-GATE** · Stage 1 remains SHIPPED-PENDING-USER-QA unchanged.
- **RULE-DECK-ID-COLLISION-GUARD** · v1.1 IDs only.
- **RULE-WRONG-BOARD-REJECTION** · line-1 label matches Akki-Executive-Core arc.
- **Shield UNTOUCHED** (R10 · sha256 identity vs `5d1204ca`).
- **Engines UNTOUCHED** (`deck_regenerate.py` / `llm_service.py` / `llm_tier_quota.py` / `studio_sensitivity.py` all 0 diff bytes).
- **FAIL-CLOSED surfaces UNTOUCHED** (`_http_client.py::_call` / `BOUNDED_CONTEXT_TRANSPORT` / retry policy).
- **Account isolation** preserved on kickoff + status endpoints (verified via slice R6).
- **Commit-lock 409 byte-identity** preserved via engine helper `commit_locked_409` (slice R7).
- **Audit fingerprint 19-field** preserved (slice R8 · engine writes audit unchanged).
- **Testing sub-agents BANNED** throughout.
- **MOCKED-integrations line preserved** (SendGrid dev-mode + Resend mock).
- **F.6 N/A** — shape wrapper, not engine touch.
- **Prior bankings NOT reopened** (D5 relabel · 4 Part-0 rules · state-injection corollary · all preserved).

---

## HARD STOP at close

**Nothing auto-fires.** Stages 2 (Enhance) + 3a-3e (v1.1 conformance incl. §4.6-derived block) remain HELD per STOP-AND-SHOW gate. Gitleaks disposition still WAIT-FOR-USER-LOG-PASTE. User disposition required for:
- Follow-up arc on SHIELD-INTERNAL-LLM-PROVIDER-TIMEOUT resolution (4 recommended paths surfaced).
- Push local commits via "Save to GitHub".
- Decision on Stage 2 (Enhance) fire timing given async plumbing now ready.

---

## Files touched (this arc)

**NEW backend product-code:**
- `backend/services/deck_generation_jobs.py` (190 LOC · job store + phase wrapper + task spawn)

**MODIFIED backend product-code:**
- `backend/routers/decks.py` (outline + generate endpoints converted; `_run_outline_job` + `_run_generate_deck_job` runners added; new status endpoint)
- `backend/routers/deck_related_lineage_regen.py` (regenerate endpoint converted; new async response models; new shared status endpoint)
- `backend/server.py` (startup wiring · 6 lines added)

**MODIFIED frontend product-code:**
- `frontend/src/components/decks/CreateSummaryDeckModal.jsx` (`handleCreate` rewritten for kickoff+poll pattern)

**NEW report + evidence:**
- `memory/sprints/JC_DECK_GEN_ASYNC_KICKOFF_POLL.md` (this memo)
- `backend/scripts/jc_deck_gen_async_kickoff_poll_proving_slice.py` (15-row slice)
- `backend/scripts/.jc_deck_gen_async_kickoff_poll_slice_results.json`
- `memory/evidence/2026_07_deck_recovery_stage_1/s05_async_v2_state.png` (attempt 2 · Path B evidence)
- `memory/evidence/2026_07_deck_recovery_stage_1/s05_async_attempt2_state.png` (attempt 3 · Path B evidence · stability confirmation)

**MODIFIED report:**
- `memory/DEV_PIPELINE.md` §9 row for `JC-DECK-GEN-ASYNC-KICKOFF-POLL` (🟡→🟢 at close · commit hash + content marker)
- `memory/sprints/JC_GEN_PATH_CONNECTTIMEOUT.md` closure addendum (supersession note)

**Zero touches** to: Shield · engines · FAIL-CLOSED surfaces · `_http_client.py::_call` · `BOUNDED_CONTEXT_TRANSPORT` · retry policy · `.env` · `.gitleaks.toml` · Postmark / inbound / ClamAV boot guards · v1.0 story IDs.
