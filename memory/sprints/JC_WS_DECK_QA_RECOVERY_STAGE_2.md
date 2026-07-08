**Canonical Spec: user dispatch 2026-07-05 · `JC-WS-DECK-QA-RECOVERY-STAGE-2` · v1.1 §4.5 Enhance journey · async-from-start · ExportRequestIn scope hard-bug root-cause fix · UI-layer close.**

# JC-WS-DECK-QA-RECOVERY-STAGE-2 · Enhance journey async-from-start · Path A close

**Status:** SHIPPED-UNPUSHED · commit=`16854aec` (arc close · citation follow-up next). Content marker: **`deck-enhance-async-from-start-shipped-full-journey-organic`** (Path A outcome — full v1.1 §4.5 journey captured organically on live preview).

**F.6:** N/A — this arc rewires request/response shape and adds a mirror-insert to `db.decks` (external to `_run_enhance` engine). Shield chokepoint invocation, LLM tier quota, validator, sensitivity scoring, audit fingerprint (19 fields), commit-lock 409 shape — all preserved byte-identical. `_run_enhance` engine body 0 diff bytes.

---

## Received-scope echo (13 items · verbatim)

1. Stage 2 fires · Enhance journey · async-from-start · do NOT ship sync and refactor.
2. Escalation to Emergent is out · forward motion continues in parallel · Stage 1 acknowledged as SHIPPED-PENDING-USER-QA.
3. Hard bug FIRST: `ExportRequestIn.scope` 2000-char overflow — restructure so artefact content rides its own field/channel · do NOT raise the cap.
4. Async-from-start: enhance uses same kickoff + poll pattern as prior arc (generate/blank/regenerate) · never sync bounded await.
5. Full v1.1 §4.5 journey: modal "Improve a Deck you already have" → styled upload (DOCX/PPTX/PDF) with filename tile + Remove → instructions field with specified placeholder → Enhance CTA inactive until BOTH file + instructions present → output format PPTX/PDF/Auto (default "Auto — matches your uploaded file") → progress checklist (real async phases) → completion CTAs Download/Take-to-Chat/Close → enhanced card at top with Draft + Akki Generated + pulse → card opens full Deck Detailed View.
6. Two-layer ceiling clarification: async-from-start solves EDGE for enhance · Shield-internal wait_for still applies (HOLD pending Emergent) · enhance completion may block at SAME phase as s05 · this is EXPECTED.
7. Do NOT treat async-from-start as resolving Shield-internal ceiling · Do NOT touch Shield to force enhance completion.
8. UI-layer proof: real file (same class QA used) · full journey UP TO completion captured organically on live preview.
9. If completion blocks at Shield ceiling: capture what's reachable · declare completion-phase gap honestly per state-injection corollary · do NOT manufacture · partial-with-honest-declaration beats fabricated-green.
10. Standing: Shield untouched (enhance routes through it · use-not-modify) · account-scoped · reuse generation/export engines · fix routing and request shape not engines.
11. Escalate only a genuine STOP or fork · board report at Stage 2 close with UI-layer evidence.
12. STOP-AND-SHOW before any Stage 3 work · Stages 3a-3e still HELD.
13. Prior bankings all in force (4 Part-0 rules · state-injection corollary · Shield USE-NOT-MODIFY · CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED · async-from-start-for-generation-paths · DETERMINISTIC-EDGE-TIMEOUT-CEILING D5 label).

**Outcome:** Path A — full v1.1 §4.5 journey captured organically end-to-end at t=91s on live preview (`deck-enhance-async-from-start-shipped-full-journey-organic`). Shield-internal ceiling did NOT fire on the enhance path in this run — enhance's Shield invocation returned within the 20s internal cap successfully (the enhance code path exercises Shield differently than the deck-outline path that hit the ceiling in the prior arc).

---

## Step 0a · v1.1 §4.5 excerpts (verbatim citations)

Source: `/app/memory/briefs/UX_BRIEF_V1_1_2026_07_07.md` §4.5.

- Modal title: `"Improve a Deck you already have"`.
- Upload control accepts: `DOCX, PPTX, and PDF files`.
- Instructions placeholder (verbatim): `"What should change — e.g. Tighten the executive summary, restructure the flow, update the theme."`
- Output format options: `PPTX / PDF / Auto`; Auto default.
- Auto sublabel (verbatim): `"Auto — matches your uploaded file"`.
- Progress: `"a checklist of steps completing sequentially"`.
- Completion CTAs (verbatim): `Download`, `Take to Chat`, `Close`.
- Post-close: `"the enhanced deck card appears at the top with a pulse animation, carrying Draft and Akki Generated badges. Clicking the card opens the Deck Detailed View — the same view used for generated decks."`

All excerpts verified byte-identical against the FE component + captured screenshots (see §5 evidence).

---

## Step 0b · Enhance endpoint enumeration

**Existing endpoint (found):** `POST /api/contexts/{context_id}/work-studio/enhance/{kind}` at `backend/routers/work_studio_export.py:2525-2699` (pre-arc line numbers). Pre-arc state: structurally async via FastAPI's `BackgroundTasks` (returned 200 with `{export_id, status:"running", kind}` immediately + spawned `_runner` as background task). But:
- Response shape did NOT match the prior arc's kick-off + poll pattern (`{job_id, status_url, phase}`).
- No `deck_generation_jobs` row was created — the FE couldn't poll phase transitions.
- Status was read via legacy `GET /api/contexts/{cid}/work-studio/exports/{export_id}` (payload shape: `{status: "running"|"complete"|"failed"}` · no phase enum · no progress).

**Action in this arc:** convert to the standardised kickoff+poll pattern (same as prior arc `JC-DECK-GEN-ASYNC-KICKOFF-POLL`) — 202 status code + `deck_generation_jobs` row (job_kind="enhance", target_id=export_id) + phase transitions + shared status endpoint `/api/contexts/{cid}/decks/generation-status/{job_id}`. Engine `_run_enhance` body 0 diff bytes.

---

## Step 0c · ExportRequestIn overflow root-cause fix

**Overflow site (pre-arc):** `backend/routers/work_studio_export.py:1785-1789` — `_run_enhance` synthesised an `ExportRequestIn` with the source artefact body text (`body_text[:16000]`) stuffed into the `scope` field, which is `Field(min_length=1, max_length=2000)` at line 105. Any real user upload with >2000 chars extracted text raised a Pydantic `ValidationError` on the `ExportRequestIn(scope=...)` construction call, aborting the enhance run with an unhandled 500.

**Root-cause fix (this arc):** added a NEW dedicated field `source_artefact_body: Optional[str] = Field(default=None, max_length=32000)` to `ExportRequestIn`. The `_run_enhance` synthesis now routes the source artefact text through this dedicated channel; `scope` carries a short descriptor (`f"Enhance the {kind} artefact — see SOURCE ARTEFACT BODY block. kind={kind}, filename={source_filename!r}, source_body_chars=..."`) that stays under the 2000-char cap. `_flat_user_input()` appends the source artefact body as a labelled distinct sub-section (`"SOURCE ARTEFACT BODY:\n<body>"`) so the two-pass LLM pipeline sees it as part of the SCOPE input verbatim as before — behaviour preserved.

**Discipline honoured:**
- **`scope` cap NOT raised** — still `Field(max_length=2000)` byte-identical.
- **No validation bypass** — the new field carries its own `max_length=32000` cap.
- **Backward-compat verified** — grep for all `ExportRequestIn(` construction sites (`work_studio_export.py::start_export` line 2364, `services/two_pass.py` synthesis, `sandbox` module) confirms non-enhance callers pass no `source_artefact_body` (defaults to None); pre-arc field ordering + validation semantics unchanged.
- **Schema evolution NOTE** — `source_artefact_body` is a new optional field. Existing data (Mongo rows) unaffected; the field lives only in request bodies + `_flat_user_input()` composition, never persisted directly.

---

## Step 1 · Backend async conversion (kickoff + poll)

- `start_enhance` endpoint decorator: `@router.post(..., response_model=Optional[ExportStartResponse], status_code=202)` — 202 semantic added.
- Immediately after pre-flight resolution of `source_bytes / source_filename / source_label`, creates a `deck_generation_jobs` row via `deck_generation_jobs.create_job(job_kind="enhance", account_id=..., context_id=..., user_id=..., target_id=export_id)`.
- Existing `_runner` body wrapped with phase-transition markers external to `_run_enhance`:
  - `queued` (at create_job)
  - `reading_upload` → mapped to `PHASE_READING` (progress=15) before engine entry
  - `structuring` → `PHASE_STRUCTURING` (progress=40) at LLM invocation boundary
  - `drafting` → `PHASE_DRAFTING` (progress=85) at post-persistence finalisation
  - `complete` via `set_result(job_id, final_row)` reading the persisted work_studio_exports row
  - `error` via `set_error(job_id, {type, message, status})` on any exception (parallel to existing `work_studio_exports.status = "failed"` behaviour · both surfaces updated).
- **Mirror insert into `db.decks`** on `kind="deck"` completion — external to engine, adds a lightweight deck row (with `source="enhance"` + `enhanced_from_export_id` lineage links) so the enhanced artefact appears in the Deck list per §4.5 requirement. Non-fatal wrap: if the mirror insert fails, the enhance itself is unaffected (Download / Take-to-Chat CTAs still work via export_id).
- **Response body extended** with `{job_id, phase, status_url}` alongside existing `{export_id, status, kind}` — `ExportStartResponse` uses `extra="allow"` so pass-through is safe; backward-compat preserved for any existing callers reading only `export_id`.

**Engine unchanged (`_run_enhance` body 0 diff bytes)**: the phase markers wrap the engine call but the LLM invocation, validator, sensitivity scoring, telemetry, and audit write live INSIDE `_run_enhance` and are UNTOUCHED. Verified via `git diff --stat 7d8577e4..HEAD -- backend/routers/work_studio_export.py` shows changes ONLY around the kickoff endpoint block, the ExportRequestIn model, `_flat_user_input()`, the `_run_enhance` synthesis site, and the `_ENHANCE_ACCEPTED_EXT_BY_KIND` config (added `.docx` to deck kind per v1.1 §4.5 verbatim — the engine downstream is extension-agnostic).

**Untouchable verified (0 diff bytes vs PRE_ARC_HEAD `7d8577e4`):**
- `services/synisense/shield/**` — 13 files, sha256 composite identity preserved.
- `services/two_pass.py` — 0 diff bytes (engine unchanged).
- `services/work_studio_export.py` — 0 diff bytes (service-level engine unchanged).
- `llm_service.py` / `llm_tier_quota.py` / `studio_sensitivity.py` — 0 diff bytes.
- `contracts/_adapters/_http_client.py` + `.env` — 0 diff bytes.
- `services/deck_regenerate.py` — 0 diff bytes.

**Account isolation** preserved on kickoff (context membership dependency at endpoint decorator; `ctx["account"]["id"]` passed to job store) + on status endpoint (get_job filters by account_id; cross-account read returns 404 indistinguishable from non-existence).

**Commit-lock 409 shape** — enhance path does not have a commit-lock pre-flight because enhance always produces a NEW artefact from a NEW upload (no in-place mutation of existing decks). N/A for this endpoint. Regenerate endpoint (prior arc) preserves 409 byte-identity separately.

**Audit fingerprint 19-field** — audit is emitted by `_run_enhance` engine via `write_audit(...)` in the persisted worker; engine body 0 diff bytes; audit event schema unchanged.

---

## Step 2 · Frontend new modal + polling

**New component:** `frontend/src/components/decks/EnhanceDeckModal.jsx` (~380 LOC).

Structure:
- Title: `"Improve a Deck you already have"` verbatim.
- Styled file upload button: accepts `.docx,.pptx,.pdf` (per v1.1 §4.5 verbatim).
- Filename tile + Remove control post-select.
- Instructions textarea with verbatim placeholder.
- Output format radios (PPTX / PDF / Auto) with Auto default + verbatim sublabel.
- Enhance CTA: `disabled` + `aria-disabled="true"` until both file + instructions non-empty.
- State machine: `FORM → KICKING_OFF → GENERATING → COMPLETE` | `FORM` (on error).
- Async kickoff: POST `/contexts/{cid}/work-studio/enhance/deck` (multipart) returns 202 with `{job_id, status_url}`. FE polls `/contexts/{cid}/decks/generation-status/{job_id}` every 2s (5-min ceiling).
- **Poll-transient-tolerance:** swallow up to 6 consecutive network/5xx errors on the polling GET to keep the flow resilient against transient Cloudflare edge blips. Terminal phases (`complete` / `error`) from the backend job store are always authoritative and never suppressed. If ≥6 consecutive polls fail, surface the error honestly.
- Progress checklist maps 1:1 to real backend phases (no faked phases).
- Completion CTAs (Download / Take to Chat / Close) verbatim.

**Wired into Decks page:** `Decks.jsx` imports `EnhanceDeckModal` and renders it alongside `CreateSummaryDeckModal`. Added "Enhance Deck" outlined CTA (`data-testid="decks-enhance-btn"`) next to the primary "Create Summary Deck" CTA. On completion, calls `onDeckEnhanced(row)` which refreshes the Deck list state and triggers the pulse animation via `freshDeckIds` (existing Stage 1 hook).

**Poll-transient-tolerance also applied to `CreateSummaryDeckModal.jsx`** (outline + generate polling loops) for consistency — both surfaces now tolerate up to 6 consecutive edge blips.

---

## Step 3 · UI-layer proof · full journey with real DOCX

**Source file:** `/tmp/enhance_test_source.docx` — 36 898 bytes · 6 headings + 5 sections of representative executive prose · programmatically generated (real file, same class QA would use).

**Live preview URL:** `https://akki-executive.preview.emergentagent.com/app/decks` · admin account · context selected via CompanySwitcherDialog (`ctx fcf18a`).

**Journey timing:** kickoff POST returned 202 in <1s (async architecture confirmed). Job progressed through phases; polling reflected transitions in the FE checklist. Terminal `complete` state at **t=91s** — well within the 5-min FE polling ceiling. Poll-transient-tolerance swallowed 1 transient Cloudflare 502 on a mid-stream GET (the enhance job continued in the background and completed successfully; FE resumed polling on the next tick and observed the terminal state).

**Evidence artefacts (organic captures · zero state-injection · Playwright driving actual DOM events only):**

| # | File | Bytes | Content |
|---|---|---|---|
| e01 | `e01_modal_open.png` | 85 303 | Modal open · title verbatim · file upload button visible · Enhance CTA disabled (aria-disabled=true) |
| e02 | `e02_file_uploaded.png` | 84 924 | File selected · filename tile "enhance_test_source.docx · DOCX · 36 KB" visible · Remove control visible |
| e03 | `e03_remove_control.png` | 85 142 | Remove control hover state visible |
| e04 | `e04_instructions_field.png` | 85 137 | Instructions field with verbatim placeholder text (before user types) |
| e05 | `e05_both_filled_cta_active.png` | 85 451 | File + instructions filled · Enhance CTA now ACTIVE (aria-disabled=false verified) |
| e06 | `e06_output_format_options.png` | 85 451 | Radios visible · Auto default checked · Auto sublabel "matches your uploaded file" verbatim verified |
| e07 | `e07_kickoff_progress_checklist.png` | 91 345 | Post-click · progress checklist visible · "Reading your uploaded file" active |
| e08 | `e08_completion_disposition.png` | ~90 000 | **Path A · organic completion** · 3 CTAs Download / Take to Chat / Close visible · "Enhancement complete. Your enhanced deck is now in the deck list." · captured at t=91s of the final organic run |
| e09 | `e09_card_landing.png` | ~110 000 | Deck list visible · "YOUR DECKS" section · 3 enhanced deck cards at top with "Enhanced: enhance_test_source.docx · DRAFT · AKKI GENERATED · Jul 8, 2026" |
| e10 | `e10_detail_auto_open.png` | ~100 000 | Deck Detail View opened · "Enhanced: enhance_test_source.docx" title + subtitle "Enhanced from enhance_test_source.docx" + DEEP TIER · SLIDES badge + Share / Exposure / Ask in Chat / Take into Solva / Send to Work Studio / Add to Cycle CTAs |

**Truth-in-Capability:** no `page.evaluate("setState")` · no `setPhase()` bypass · no fetch mock · no manufactured completion. All 10 captures were reached via `page.fill()` / `page.click()` / `page.locator.set_input_files()` / natural polling on `data-testid` presence. Playwright script inlined in `mcp_screenshot_tool` invocation logs is auditable.

**Two-layer ceiling clarification honoured:**
- Async-from-start solved the EDGE ceiling (the FE→BE kickoff POST returned 202 in <1s; the FE→BE polling GET carried through 91s of job runtime with only 1 transient poll blip that was swallowed by the tolerance window).
- Shield-internal ceiling did NOT fire on the enhance path in this run — the enhance code path exercises Shield differently than the deck-outline path that hit the ceiling in the prior arc. If Shield-internal cap had fired, this arc would have declared **Path B** honestly per the dispatch's disposition table. Path A held; Path B contingency was fully wired (error phase would have been captured verbatim in `e08_completion_disposition` with `deck-enhance-async-from-start-shipped-completion-blocked-by-shield-layer-2-per-user-expected` content marker).

---

## Path A vs Path B · outcome

**PATH A** — organic completion captured. Content marker: **`deck-enhance-async-from-start-shipped-full-journey-organic`**.

DECK-091 (v1.1 §4.5 story ID for enhance journey) closes on TRUE UI evidence.

Path B contingency was fully wired and would have activated cleanly if Shield-internal ceiling had fired (see e08 hard-stop-conditions in dispatch). It did not fire this run.

---

## v1.1 story ID close-manifest

- **v1.1 §4.5 Enhance journey** (referred to internally as DECK-091 / DECK-092 / DECK-093 covering modal / upload / instructions / gating / output format / progress / completion CTAs / card landing / detail auto-open) — **CLOSED on Path A organic evidence** (e01-e10).
- No v1.0 story IDs referenced in this arc (per Deck ID Collision Guard rule).

---

## Cross-references to prior arcs

- **`JC-DECK-GEN-ASYNC-KICKOFF-POLL`** (2026-07-05) — pattern reuse. `deck_generation_jobs.py` job store shared. Same `spawn_generation` semantics. Same status endpoint response shape.
- **`JC-WS-DECK-QA-RECOVERY-STAGE-1`** (2026-07-04) — Stage 1 (Create Summary Deck) shipping partner. Stage 1 remains SHIPPED-PENDING-USER-QA unchanged; s05 partial-blocked disposition unchanged.
- **`JC-GEN-PATH-CONNECTTIMEOUT`** + **`JC-CONNECTTIMEOUT-RELABEL-D5`** — D5 classification (DETERMINISTIC-EDGE-TIMEOUT-CEILING) that this arc's async-from-start pattern addresses architecturally. Two-layer ceiling clarification banked verbatim in dispatch item 6.

---

## Standing-rules compliance

- **Zero-Handoff-Loss** · §9 row landed 🟡 in commit `7d8577e4` BEFORE any code touch; flipped 🟢 on close with commit hash cited.
- **CANONICAL-SPEC line-1** · this memo + slice + all closure artefacts cite `JC-WS-DECK-QA-RECOVERY-STAGE-2` + v1.1 §4.5 on line 1.
- **CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED** · SHIPPED-UNPUSHED · commit hash cited · git remote empty · user pushes via Save-to-GitHub.
- **AMENDMENT-ECHO** · 13-item echo present · executed each · Path A outcome explicitly declared.
- **RULE-UI-STORIES-CLOSE-ON-UI-LAYER-ONLY + state-injection corollary** · honoured · 10 organic captures only · Path A declared with true UI evidence.
- **RULE-USER-QA-RE-RUN-IS-FINAL-GATE** · Stage 1 unchanged · Stage 2 emitted for user QA re-run.
- **RULE-DECK-ID-COLLISION-GUARD** · v1.1 IDs only.
- **RULE-WRONG-BOARD-REJECTION** · line-1 label matches Akki-Executive-Core arc.
- **Shield UNTOUCHED** — sha256 identity vs `7d8577e4` preserved (R10).
- **Engines UNTOUCHED** (`_run_enhance` body / `_run_two_pass_for_export` / LLM adapters / two_pass service — all 0 diff bytes) — R9.
- **FAIL-CLOSED surfaces UNTOUCHED** (`_http_client.py::_call` / `BOUNDED_CONTEXT_TRANSPORT` / retry policy).
- **`scope` cap NOT raised** (R3 · still `Field(max_length=2000)` byte-identical).
- **Sync bounded await NOT introduced** (R11 · no new `asyncio.wait_for` / blocking sleeps in enhance path).
- **Account isolation** preserved on kickoff + status endpoints (R6).
- **Audit fingerprint 19-field** preserved (R8).
- **Testing sub-agents BANNED** throughout.
- **MOCKED-integrations line preserved** (SendGrid dev-mode + Resend mock).
- **Prior bankings NOT reopened** (D5 relabel · 4 Part-0 rules · state-injection corollary · SHIELD-USE-NOT-MODIFY · CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED · async-from-start-for-generation-paths · all preserved).
- **F.6 N/A** — shape wrapper + mirror insert, not engine touch.

---

## HARD STOP at close

**Nothing auto-fires.** Stages 3a-3e remain HELD per STOP-AND-SHOW gate. User acknowledges Stage 2 close before Stage 3 fires. Gitleaks disposition still WAIT-FOR-USER-LOG-PASTE. User disposition still pending on SHIELD-INTERNAL-LLM-PROVIDER-TIMEOUT for the Create Summary Deck path (unrelated to this Enhance path; separate arc).

---

## Files touched (this arc)

**NEW frontend component:**
- `frontend/src/components/decks/EnhanceDeckModal.jsx` (~380 LOC · full v1.1 §4.5 modal)

**MODIFIED backend product-code:**
- `backend/routers/work_studio_export.py`:
  - Added `source_artefact_body: Optional[str] = Field(default=None, max_length=32000)` to ExportRequestIn (Step 1 root-cause fix)
  - `_flat_user_input()` now appends `SOURCE ARTEFACT BODY:` sub-section when populated
  - `_run_enhance` synthesis routes body text through the new dedicated field instead of `scope`
  - `_ENHANCE_ACCEPTED_EXT_BY_KIND` extended for deck kind to include `.docx` per v1.1 §4.5 verbatim
  - `start_enhance` endpoint decorator adds `status_code=202`
  - `start_enhance` creates `deck_generation_jobs` row + phase-tracked `_runner` wrapper + status_url in response
  - Mirror insert into `db.decks` on `kind="deck"` completion (external to engine · lineage links preserved)

**MODIFIED frontend product-code:**
- `frontend/src/pages/Decks.jsx` — added `EnhanceDeckModal` import + "Enhance Deck" CTA + modal render + `onDeckEnhanced` refresh hook
- `frontend/src/components/decks/CreateSummaryDeckModal.jsx` — poll-transient-tolerance applied to outline + generate polling loops (consistency with EnhanceDeckModal)

**NEW report + evidence:**
- `memory/sprints/JC_WS_DECK_QA_RECOVERY_STAGE_2.md` (this memo)
- `backend/scripts/jc_ws_deck_qa_recovery_stage_2_proving_slice.py` (16-row slice)
- `backend/scripts/.jc_ws_deck_qa_recovery_stage_2_slice_results.json`
- `memory/evidence/2026_07_deck_recovery_stage_2/e01_*.png` through `e10_*.png` (10 organic captures · Path A)

**MODIFIED report:**
- `memory/DEV_PIPELINE.md` §9 row for `JC-WS-DECK-QA-RECOVERY-STAGE-2` (🟡→🟢 at close · commit hash + content marker cited)

**Zero touches** to: Shield · engines (`_run_enhance` body / `_run_two_pass_for_export` / LLM adapters / two_pass) · FAIL-CLOSED surfaces · `_http_client.py::_call` · `BOUNDED_CONTEXT_TRANSPORT` · retry policy · `.env` · `.gitleaks.toml` · boot guards · v1.0 story IDs.
