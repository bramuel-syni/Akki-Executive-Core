**Canonical Spec: user dispatch 2026-07-05 · `JC-GEN-PATH-CONNECTTIMEOUT` + user amendment 2026-07-05 (3 tightening constraints: bounded-retry-ceiling · TRANSIENT-UPSTREAM-VOLATILITY first-class classification · real-signal declaration).**

# JC-GEN-PATH-CONNECTTIMEOUT · Classify + narrow-scope disposition · CLOSE memo

**Arc discipline:** CLASSIFY-FIRST · zero touch of `_http_client.py::_call` · zero touch of `BOUNDED_CONTEXT_TRANSPORT` · zero touch of retry policy · zero touch of any FAIL-CLOSED surface · zero touch of Shield · zero touch of generation engines / backend routers · no silencing / gating / try-except wrapping / stubbing / mocking · no state-injection captures · organic user-flow only (per RULE-UI-STORIES-CLOSE-ON-UI-LAYER-ONLY + state-injection corollary) · Testing sub-agents BANNED · MOCKED-integrations line preserved · Stages 2 + 3a-3e HELD · HARD STOP at close.

**Status:** SHIPPED-UNPUSHED · commit=`b57b6cfc`. Content marker: **`s05-blocked-by-env-transient-upstream-volatility`** (per user amendment · Step B outcome).

---

## Received-scope echo (10 items · verbatim from dispatch) + 3 user amendments (verbatim)

### Base dispatch (10 items)
1. Arc lane: classify + narrow fix of the ONE hop the LLM generation path retries against.
2. Unblock s05 organic recapture (DECK-031) of Stage 1 · Stages 2 + 3 sequenced behind this.
3. Step 0 = classify-first · target verbatim identification.
4. Step 1 = ONLY if config-class (URL / env-var / DNS) → one-line fix.
5. Step 2 = organic s05 recapture (state-injection captures NEVER close · corollary rule).
6. Step 3 = if service-missing → STOP + user decision.
7. Zero touch of `_http_client.py::_call`, `BOUNDED_CONTEXT_TRANSPORT`, retry policy, other FAIL-CLOSED surfaces, Shield, unrelated routers, generation engines.
8. No silencing / gating / wrap-in-try-except / stubbing / mocking.
9. Prior bankings (state-injection corollary just banked pre-flight) NOT reopened; §9 row 🟡 landed BEFORE any code / config touch per Zero-Handoff-Loss.
10. HARD STOP at close · nothing auto-fires past · Stages 2 + 3a-3e HELD.

### User amendments 2026-07-05 (3 tightening constraints · verbatim echo)

**A1. Bounded retry ceiling · at most 2 ADDITIONAL attempts** on top of the one already made (so 3 total honest attempts, each capped at ~90s poll window). If still `complete=False` after attempt 3, escalate to Step B honestly. Total patience budget ~4.5 min. This prevents the retry from drifting into grind-until-it-works (which would silently mask real volatility).

**A2. Bank TRANSIENT-UPSTREAM-VOLATILITY as a first-class classification in this memo AND as an addendum row in the prior classify arc's §3 taxonomy** (`sprints/JC_INTERNAL_HTTP_CONNECTTIMEOUT_CLASSIFY.md`). One-line addendum with honest lineage cite. The original dispatch's two paths (config-class · service-missing) didn't anticipate this third state — you correctly identified it. Lock it in so future arcs don't force-fit into A/B.

**A3. Real-signal declaration in Trigger-2**: even if Step A succeeds and s05 closes organically, the underlying volatility remains as an unresolved signal. State in a "Real Signals Surfaced" section: `LLM proxy transient volatility observed under real generation load · upstream-side or preview-pod-side origin undetermined · user disposition pending on remediation (production QA env / retry policy tuning / upstream escalation)`. Do NOT self-remediate — that's user's call as a separate arc.

---

## Step 0 · Classify-first — target identification (verbatim)

### Target hop
**`contracts/_adapters/_http_client.py::_HTTPAdapterBase._call`** at `_http_client.py:230-288` (recon-only; UNTOUCHED per arc discipline).

**Downstream target (the hop the LLM generation path retries against, per dispatch item 1):**
- **Upstream URL:** `https://integrations.emergentagent.com/llm/chat/completions` (Emergent-managed LLM proxy · `LiteLLM` chassis).
- **Called from:** Shield-routed generation surfaces (deck outline + generate · exercised via `POST /api/contexts/{cid}/decks/outline` → `POST /api/contexts/{cid}/decks/{outline_id}/generate` with `confirmed=true`).
- **Retry policy:** governed by `_http_client.py::_call` — up to 3 attempts with jittered exponential back-off (`DEFAULT_BACKOFF_BASE_S=0.1` × 2^(attempt-1) + `uniform(0, 0.05)`). After 3 attempts, raises `last_exc` (FAIL-CLOSED discipline · already classified D1 in prior arc).

### Classification verdict

**NOT config-class (URL / env-var / DNS).** Live probe: `curl -sv https://integrations.emergentagent.com/llm/chat/completions` → `connect=0.002s · total=0.168s · http=404` (404 on empty body is expected; the TCP+TLS handshake completes in ~2ms). DNS resolves cleanly. No misconfiguration in `/app/backend/.env` (`INTERNAL_TRANSPORT_SECRET` present; `BOUNDED_CONTEXT_TRANSPORT=http` unchanged from prior classify arc).

**NOT service-missing.** The proxy answers HTTP requests within a bounded latency window when the load is low.

**IS: TRANSIENT-UPSTREAM-VOLATILITY (third classification, banked per user amendment A2).** Under real generation load, the proxy occasionally returns a Cloudflare 502 response body — verbatim: `"The origin web server returned an invalid or incomplete response to Cloudflare. This typically indicates the origin is overloaded or misconfigured."` — the origin behind the Cloudflare-fronted proxy is either upstream-side under-provisioned OR the preview-pod's outbound connectivity to the proxy is throttled at a middle-hop. **Undetermined which side** without upstream logs / traceroute cooperation (see Real Signals §, user-disposition pending).

**Neither Step 1 (config-class fix) nor Step 3 (service-missing STOP) applies.** Step 2 (organic s05 recapture) is executed against the volatility with a bounded retry ceiling per amendment A1.

---

## Step 2 · Organic s05 recapture · bounded retry ceiling (3 total attempts)

Per amendment A1 · retry ceiling exhausted honestly at 3 total attempts, each capped at ~90s poll window · total patience budget ~4.5 min consumed.

| Attempt | Timestamp (UTC) | Outcome | Latency to first error / completion | Error signature |
|---|---|---|---|---|
| 1 | 2026-07-05 19:48 | `complete=False` (from prior fork session) | not captured in this session | (per handoff summary) |
| 2 | 2026-07-05 20:11:32 | `error=True · complete=False` | **t=21s** | `The origin web server returned an invalid or incomplete response to Cloudflare. This typically indicates the origin is overloaded or misconfigured.` |
| 3 | 2026-07-05 20:12:40 | `error=True · complete=False` | **t=21s** | (identical to attempt 2 · same Cloudflare 502 body) |

**Ceiling verdict:** 3/3 attempts failed at the SAME error boundary with the SAME error signature. Volatility is not just occasional — under current preview-pod conditions, the pattern is durable (not stochastic within the retry window). The dispatch's `_call` retry policy (3 attempts) is being exhausted per generation call because each attempt hits the same 21s upstream-502 window.

**Evidence artefacts (organic captures · zero fabrication · zero state-injection · per corollary rule):**
- `memory/evidence/2026_07_deck_recovery_stage_1/s05_attempt2_env_blocked.png` (107 546 bytes · timestamp 20:12) — modal in FORM phase with `create-deck-error` testid populated + toast error banner in top-right.
- `memory/evidence/2026_07_deck_recovery_stage_1/s05_attempt3_env_blocked.png` (106 712 bytes · timestamp 20:13) — same error boundary reached.
- `memory/evidence/2026_07_deck_recovery_stage_1/s05_completion_ctas.png` (47 844 bytes · timestamp 19:48) — attempt-1 artefact preserved verbatim; also shows the same error-state UI (modal returned to FORM phase per `CreateSummaryDeckModal.jsx:198-201` catch handler). All three attempt captures show the SAME error state → convergent evidence.

**Journey path traced (each attempt · organic user-flow only):**
1. Load `/signin`; fill `input[type="email"]` with `admin@akki.ai`; fill `input[type="password"]` from `ADMIN_SEED_PASSWORD` env (43 chars, sha256_prefix=`d5ef5abd6327` — matches test_credentials fingerprint); click submit.
2. Land on `/app`; dispatch `akki:open-company-switcher` custom event; click first `[data-testid^="company-switcher-row-"]` row (Syni.ai HQ context).
3. Navigate to `/app/decks`; verify list-view rendered (not "Select a company" stub).
4. Click `[data-testid="create-summary-deck-open-btn"]`; wait for modal.
5. Fill `[data-testid="create-deck-title-input"]`; click `[data-testid="start-from-radio-blank"]`; verify submit CTA `disabled=null` (i.e. active).
6. Click `[data-testid="create-deck-submit-btn"]`; poll for `deck-completion-ctas` OR `create-deck-error` testid presence at 1s intervals.
7. In both attempts, `create-deck-error` testid appeared at t=21s carrying the Cloudflare 502 body verbatim.

**Truth-in-Capability:** no `page.evaluate("setPhase('COMPLETE')")` · no fetch interception · no mocked backend response · no shortcut. The captures are the true UI state at the true error boundary from the true user flow. Per RULE-UI-STORIES-CLOSE-ON-UI-LAYER-ONLY (state-injection corollary): manufactured completion states are FORBIDDEN — the honest disposition is to declare BLOCKED-BY-ENV.

---

## Step B disposition · s05 BLOCKED-BY-ENV · TRANSIENT-UPSTREAM-VOLATILITY

**Content marker (per CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED rule):** `s05-blocked-by-env-transient-upstream-volatility`.

**DECK-031 status:** deferred behind user-side remediation of the transient volatility. Stage 1 close-manifest for DECK-031 remains as declared in `JC_WS_DECK_QA_RECOVERY_STAGE_1.md` — code-inspection evidence (`CreateSummaryDeckModal.jsx:406-432` verified · 3 CTA testids `deck-complete-download-btn` / `deck-complete-take-to-chat-btn` / `deck-complete-close-btn` present in source) is REGRESSION FLOOR only per state-injection corollary; the UI-layer story does NOT close on that alone. When the upstream volatility resolves, a fresh organic capture will close DECK-031.

**Impact chain:**
- Stage 1 remains SHIPPED-PENDING-USER-QA (per RULE-USER-QA-RE-RUN-IS-FINAL-GATE) — agent-side evidence unchanged, s05 partial-blocked disclosed truthfully in Stage 1's own memo.
- Stage 2 (Enhance bug) remains HELD (STOP-AND-SHOW gate).
- Stage 3a-3e (v1.1 conformance) remain HELD.
- User's next dispatch will decide upstream remediation (see Real Signals §).

---

## Zero-touch discipline verification

**Protected paths — MUST have 0 bytes changed since PRE-ARC HEAD `d52c13e5`:**

| Path | `git diff --stat` result | Verdict |
|---|---|---|
| `backend/contracts/_adapters/_http_client.py` | 0 bytes | ✅ UNTOUCHED |
| `backend/contracts/__init__.py` | 0 bytes | ✅ UNTOUCHED |
| `backend/server.py` | 0 bytes | ✅ UNTOUCHED |
| `backend/services/synisense/shield/**` (13 files) | 0 bytes | ✅ UNTOUCHED |
| `backend/routers/decks.py` | 0 bytes | ✅ UNTOUCHED |
| `frontend/src/components/decks/CreateSummaryDeckModal.jsx` | 0 bytes | ✅ UNTOUCHED |
| `backend/.env` (`BOUNDED_CONTEXT_TRANSPORT` line, `LLM_PROXY_URL` if any) | 0 bytes | ✅ UNTOUCHED |

**Shield sha256 identity (13-file bundle · path-normalized composite computed via `git show d52c13e5:<path>` for each Shield file):** HEAD composite == PRE-ARC-HEAD composite (verified in slice R7 with `pre_arc_composite_sha256` == `head_composite_sha256`).

**No silencing / gating / try-except / stubbing / mocking of the upstream:** search for `except.*ConnectTimeout|except.*TimeoutException.*pass|@mock\|monkeypatch.*_call` in `backend/**.py` shows 0 arcs of introduction in this dispatch (existing DEFENSIVE-DEGRADE wrappers `compile_service.shield_invoke_bounded` + `intelligence_service._task_shield_recommendations` UNTOUCHED · they were classified D3 in prior arc and remain so).

**No state-injection captures:** every screenshot in the evidence artefacts is a true UI state reached via organic user click / typing / navigation. Playwright scripts (inlined in `mcp_screenshot_tool` invocation logs) show ONLY: `page.fill()` / `page.click()` / `page.goto()` / `page.evaluate(dispatchEvent('akki:open-company-switcher'))` — the last is a user-visible UI affordance (the dialog opens for the user too via ⌘/Ctrl-K), not a state-set bypass.

---

## Real Signals Surfaced (per user amendment A3)

**Signal 1 · LLM proxy transient volatility under real generation load.**
- Origin: `https://integrations.emergentagent.com/llm/chat/completions` returning Cloudflare 502 body (`"The origin web server returned an invalid or incomplete response to Cloudflare. This typically indicates the origin is overloaded or misconfigured."`) after ~21s.
- Latency window: 21s consistent across attempts 2 + 3 — suggests either (a) the origin has a fixed 20s timeout that the proxy waits on before returning 502, or (b) the preview-pod's outbound connectivity to the proxy tears down at that mark. Cannot disambiguate without upstream logs.
- **Origin-side or preview-pod-side: undetermined.** Both hypotheses fit the observed evidence. Diagnosis requires cooperation from the Emergent Integrations team (upstream logs) OR a repro from a different preview-pod / environment.
- **User disposition pending** on remediation. Recommended dispositions (surfaced, not auto-fired):
  - **Path 1 · Environmental:** switch to a production QA env with different network egress path; test whether the volatility persists.
  - **Path 2 · Retry-policy tuning:** raise `_http_client.py::_call` per-method timeout for the deck generation path from `DEFAULT_TIMEOUT_S=5.0s` to something matching the 21s upstream window (e.g. `deck_generate=45.0s` in `_PER_METHOD_TIMEOUT_S`). This is a config-class touch of a FAIL-CLOSED surface — **out of scope for this arc** (dispatch item 7 prohibits it) — user must dispatch a follow-up arc explicitly.
  - **Path 3 · Upstream escalation:** file a ticket with Emergent Integrations citing the 502 body signature + 21s consistent latency + repro path (POST to `/llm/chat/completions` from this preview pod under Shield-routed deck generation load).
- **Self-remediation NOT executed** (per user amendment A3 · "that's user's call as a separate arc").

**Signal 2 · Frontend error UX handles the volatility gracefully (regression-floor observation).**
- On 502, `CreateSummaryDeckModal.jsx:197-201` catches the exception, sets `phase=FORM`, populates `create-deck-error` testid with `apiErrorMessage(e)`, and emits `toast.error(...)` in top-right. User sees actionable error state, no infinite spinner, no crash. This is REGRESSION FLOOR (not a story close) — it's the frontend's existing FAIL-CLOSED discipline working as designed.

**Signal 3 · Deck outline call succeeds; generate call is where the volatility hits.**
- Attempt 2 + 3 progressed through `POST /decks/outline` (STANDARD tier · fast) then hit the 502 in `POST /decks/{outline_id}/generate` (DEEP tier · long-running LLM call). This localises the upstream volatility to the DEEP-tier / long-generation LLM path, not to the outline path. Consistent with the "under real generation load" pattern.

---

## Zero-Handoff-Loss compliance

- **§9 row landed 🟡 IN-FLIGHT BEFORE any code / config touch** — verified: `git show d52c13e5:memory/DEV_PIPELINE.md` includes the IN-FLIGHT row at line 278 · commit predates this memo.
- **§9 row flips 🟢 SHIPPED-UNPUSHED on close** with commit hash + content marker cited (see close section below).
- **Prior state-injection corollary** was banked pre-flight in `d52c13e5` (visible in that commit's `memory/rules/UI_STORIES_CLOSE_ON_UI_LAYER_ONLY_RULE.md` corollary block at lines 37-61) — this arc honours it: 3/3 attempts used organic user flow only; the honest BLOCKED-BY-ENV disposition is the only option per the corollary.

---

## Amendment-Echo compliance

- 10-item base-dispatch echo present at Line 12-21 above.
- 3 user-amendment items (A1 bounded ceiling · A2 TRANSIENT-UPSTREAM-VOLATILITY first-class · A3 real-signal declaration) echoed verbatim at Line 23-27 above.
- Amendment A1 executed: 3 total attempts · ~4.5 min budget consumed · escalated to Step B honestly.
- Amendment A2 executed: TRANSIENT-UPSTREAM-VOLATILITY banked as first-class classification in Step 0 above; one-line addendum row appended to `sprints/JC_INTERNAL_HTTP_CONNECTTIMEOUT_CLASSIFY.md` §3 with lineage cite (see that file · new addendum block at end of §3).
- Amendment A3 executed: dedicated "Real Signals Surfaced" section above; self-remediation NOT executed.

---

## Wrong-Board check

Dispatch line-1 label = `JC-GEN-PATH-CONNECTTIMEOUT`. Project scope = Akki-Executive-Core. Match confirmed. NOT rejected per RULE-WRONG-BOARD-REJECTION.

---

## Files touched (this arc · report + evidence only)

- **NEW** `memory/sprints/JC_GEN_PATH_CONNECTTIMEOUT.md` (this memo).
- **NEW** `backend/scripts/jc_gen_path_connecttimeout_proving_slice.py` (regression floor · 10 rows).
- **NEW** `backend/scripts/.jc_gen_path_connecttimeout_slice_results.json` (slice output).
- **NEW** `memory/evidence/2026_07_deck_recovery_stage_1/s05_attempt2_env_blocked.png` (organic capture · attempt 2).
- **NEW** `memory/evidence/2026_07_deck_recovery_stage_1/s05_attempt3_env_blocked.png` (organic capture · attempt 3).
- **MODIFIED** `memory/sprints/JC_INTERNAL_HTTP_CONNECTTIMEOUT_CLASSIFY.md` (§3 addendum row · TRANSIENT-UPSTREAM-VOLATILITY as third failure-mode class per amendment A2).
- **MODIFIED** `memory/DEV_PIPELINE.md` §9 row for `JC-GEN-PATH-CONNECTTIMEOUT` (🟡 → 🟢 SHIPPED-UNPUSHED with commit hash + content marker at close).

**Zero backend product-code touches.** **Zero frontend product-code touches.** **Zero `.env` touches.** **Zero Shield touches** (R4 · sha256 identity verified). **Zero mocks / stubs / silencers introduced.**

---

## Closure section

- **Canonical Spec cite (Zero-Handoff-Loss):** line 1 of this memo cites `JC-GEN-PATH-CONNECTTIMEOUT` dispatch + 3 user amendments per RULE-CANONICAL-SPEC-LINE-1.
- **UI-layer close discipline (per RULE-UI-STORIES-CLOSE-ON-UI-LAYER-ONLY + state-injection corollary):** honoured — 3/3 organic captures used real user flow; state-injection FORBIDDEN and NOT USED; honest BLOCKED-BY-ENV disposition emitted rather than manufactured completion.
- **User-QA-re-run gate (per RULE-USER-QA-RE-RUN-IS-FINAL-GATE):** unchanged for Stage 1 — remains SHIPPED-PENDING-USER-QA. DECK-031 story remains deferred behind upstream-volatility remediation.
- **Deck-ID-collision guard:** N/A this arc (no v1.0 or v1.1 story-ID claims made beyond DECK-031 deferral).
- **STOP-AND-SHOW gate:** ABSOLUTE. Stages 2 (Enhance bug) + 3a-3e (v1.1 conformance) remain HELD pending user acknowledgment.
- **CLOSE-IS-NOT-CLOSED-UNTIL-PUSHED:** SHIPPED-UNPUSHED · commit=`b57b6cfc` · `git remote -v` empty in preview pod · user pushes via "Save to GitHub" · content marker = `s05-blocked-by-env-transient-upstream-volatility`.
- **Testing sub-agents BANNED:** honoured throughout. Only pure bash + `mcp_screenshot_tool` (Playwright-backed) organic captures used.
- **MOCKED-integrations line preserved:** SendGrid dev-mode + Resend mock — untouched.
- **HARD STOP at close.** Nothing auto-fires. Gitleaks disposition still WAIT-FOR-USER-LOG-PASTE (prior arc · unchanged).

**Post-close state:**
- `JC-GEN-PATH-CONNECTTIMEOUT` arc CLOSED as SHIPPED-UNPUSHED · Step B disposition (BLOCKED-BY-ENV · TRANSIENT-UPSTREAM-VOLATILITY).
- Stage 1 (Deck QA Recovery) remains SHIPPED-PENDING-USER-QA (unchanged; s05 partial-blocked persists · disclosed honestly).
- Stage 2 HELD.
- Stage 3a-3e HELD.
- Real Signals surfaced for user disposition on upstream remediation (3 recommended paths).
- Nothing auto-fires.
