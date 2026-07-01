**Canonical Spec**: `/app/memory/sprints/LLM_MODELS_REFRESH_MATRIX.md` (Feb 2026 canonical matrix — .1 SHIPPED · .2 + .3 PENDING with subjective sign-off HALT clauses at lines 160 + 171-172) + `/app/memory/sprints/JC_LLM_MODELS_REFRESH_EVALUATION.md §4.1 + §4.2` (per-sub-task disposition audit) + `/app/memory/sprints/LLM_REFRESH_1.md` (predecessor .1 closure 2026-06-26 · 10/10 GREEN) + user directive: BOTH sign-off passes are the load-bearing gates blocking .2/.3 dispatch.

# LLM_MODELS_REFRESH .2 + .3 sign-off checklist

Two subjective quality-sign-off passes required from user. Neither is agent-executable. This doc is the exact instruction sheet: what to test, what "pass" looks like, where to record approval.

---

## Part A — .2 Work Studio drafting sign-off

### A.1 Surfaces the user tests

**Route**: `POST /work-studio/export/{kind}` — the same endpoint LLM-REFRESH.1 governance updated. Sub-kinds `board_brief` + `deep_dive` + `sensitivity_pack` + `bottom_line_pack` + `board_pack` all route through the same P1/P2 model pair currently at `claude-sonnet-4-5-20250929` (7 live sites per `JC_LLM_MODELS_REFRESH_EVALUATION.md §3.1`).

**Surface UI**: any origin that fires `Brief this` (Monitor Strategic Goals + Solva session + Task Manager task per `JC_WAVE3_ORIGIN_BRIEFS_*.md`). Also directly via Work Studio's Doc Journal.

### A.2 Concrete draft-scenario checklist (5 canonical drafts)

Recommend running all 5 back-to-back on the SAME account so tone drift is easier to spot.

| # | Scenario | Origin | Expected content shape | Draft type |
|---|---|---|---|---|
| 1 | Board pack for a Q4 audit committee (mix of on-track + at-risk + off-track objectives) | Monitor / Strategic Goals origin | 5-section board pack: Overview / Off-track / At-risk / On-track / Next-cycle asks | `board_pack` |
| 2 | Board brief on a single strategic objective marked at-risk (recent Shield-assessed rag_status flip) | Monitor / Signal origin | Single-objective 2-page brief with signal timeline + recommended interventions | `board_brief` |
| 3 | Sensitivity pack for a project with 3 GP perspectives showing high spread | Monitor / Objective with divergent GP perspectives | 2-column perspective diff + spread narrative + a hedge recommendation | `sensitivity_pack` |
| 4 | Deep dive on a Solva session that produced a Bottom Line | Solva session origin | 8-page structured dive: framing / evidence / Bottom Line / decision path / risks | `deep_dive` |
| 5 | Bottom Line pack on a Task Manager task with 4 sub-tasks completed | Task Manager task origin | 1-page task-outcome summary with owner + timeline + next-cycle placement | `bottom_line_pack` |

**How to trigger**: log in as `admin@akki.ai` (per `memory/test_credentials.md` line 2), navigate to the origin surface, click "Brief this", select the draft type, wait for the export to render.

### A.3 "Forward-to-a-board" acceptance rubric

Per matrix doc line 160 verbatim: **"Quality regression: HALT if user-perceived deck quality drops. 'Forward-to-a-board' subjective test required."**

**Concrete rubric** (unpacked from the matrix doc):

- [ ] **Would you send this to your actual board without edits?** If yes → PASS. If it needs > 3 material edits → FAIL. If minor stylistic edits only → PASS-with-note.
- [ ] **Tone**: executive register maintained throughout (no chatty-assistant patterns, no verbose disclaimers, no "here's a comprehensive analysis")
- [ ] **Factual grounding**: every claim traces to a data-point present in the origin payload (no hallucinated numbers, no invented committee names, no fabricated signal history)
- [ ] **Structure**: matches the canonical section shape for the draft type (see A.2 column 4)
- [ ] **Length**: within band. Board pack: 5-10 pages. Board brief: 2-3 pages. Sensitivity pack: 3-4 pages. Deep dive: 6-10 pages. Bottom Line: 1 page.
- [ ] **Recommendations**: land as actionable directives with owner + timeline, not vague "you may consider..." patterns.

### A.4 Byte-identity ratchet — what you're authorizing when you say "roll forward"

The JC-TL Stage 1 golden deck is currently pinned at **76555 bytes** (a deterministic composer output that's stable across identical inputs; regressions trip a build-breaking assertion). When we swap the P1/P2 model from `claude-sonnet-4-5-20250929` → `claude-sonnet-4-6`, the deterministic output byte-count WILL change (different tokens, different length, different structure microdetails).

**Rolling the ratchet forward means**:
1. Regenerate the JC-TL Stage 1 deck under `claude-sonnet-4-6`
2. Measure the new byte count (e.g., could land at anything from ~72000 to ~82000 bytes — depends on model prose length)
3. Pin the new byte count as the fresh ratchet
4. Any future regressions from THIS baseline trip the invariant

**What you're authorizing when you say "roll forward"**:
- You accept that the OLD 76555-byte golden is retired (no going back without re-swapping models)
- You accept the NEW byte count as the go-forward truth
- You've done the A.3 rubric pass on THIS output (i.e., the new output is board-quality)

Do NOT authorize roll-forward until A.3 passes.

### A.5 What a FAIL looks like (concrete classes)

- **Hallucination**: a fabricated fact that doesn't exist in the origin (e.g., inventing a committee that isn't in the account's context; citing a signal_id that doesn't exist)
- **Tone drift**: chatty assistant patterns (e.g., "I've prepared a comprehensive..."), first-person voice creeping in ("I think this suggests..."), rhetorical questions to the board
- **Factual error class**: wrong number, wrong owner name, misattributed quote, wrong date
- **Structural drift**: sections in wrong order, key section missing entirely, unrequested section added
- **Length blowout**: > 2× the expected band (5-10 page board pack becomes 22 pages) — usually indicates the model is padding

Any single fail → sub-sprint HALTS, revert to `claude-sonnet-4-5-20250929`, surface for re-model-selection.

### A.6 Estimated time investment

~2-3 hours end-to-end:
- 5 drafts × ~10 min each to trigger + wait for render = 50 min
- ~20 min per draft for the A.3 rubric pass = 100 min
- ~10 min for byte-ratchet + roll-forward authorization = 10 min
- **Total: ~2.5 hours** (assuming everything passes cleanly; more if any fail surfaces requiring re-generation)

---

## Part B — .3 Solva v2 4-surface per-surface sign-offs

### B.0 Scope-doc inaccuracy note (per lesson #6)

The matrix doc (`LLM_MODELS_REFRESH_MATRIX.md` lines 164-172) names `services/solva_v2/{llm_adapter, analyze_narration, payload_builder}.py`. **Disk cross-validation caught the inaccuracy**: those files contain 0 hardcoded model strings; they receive `model_id` as a parameter.

**Actual .3 scope** (per `JC_LLM_MODELS_REFRESH_EVALUATION.md §3.2`):
- `backend/llm_service.py` — `LLM_MODEL_FAST = "gemini-2.5-flash"` (STALE) + `LLM_MODEL_DEEP = "claude-opus-4-6"` (STALE) + `LLM_MODEL_STANDARD = "claude-sonnet-4-5-20250929"` (STALE) + 3× `validator_model: "gemini-2.5-flash"` (STALE)
- `backend/services/synisense/shield/llm_router.py` — `analytical` tier + `balanced` tier defaults (STALE)
- `backend/services/ideas_engine/synthesizer.py` — `model_id="claude-sonnet-4-5"` (STALE)

**Before .3 dispatches, user must resolve the scope-doc inaccuracy** (per `JC_LLM_MODELS_REFRESH_EVALUATION.md §4.2 sub-gate 1`):
- **Option A**: correct the matrix doc to name the actual sites above → then .3 dispatches against corrected scope
- **Option B**: reinterpret .3 as "all remaining stale-model defaults outside .1+.2 surfaces" → sprint name stays; scope broadens

The subjective sign-off requirement (4 per-surface passes) applies regardless of which scope-resolution option user picks. The subjective gate is on Solva v2 SURFACE quality, not on which file the model string lives in.

---

### B.1 Surface 1 — Chat

**Route**: `POST /api/chat/messages` + `POST /api/chat/threads/{thread_id}/messages`.

**Scenarios** (5 turns to stress the model coherence + memory + tool-use):
1. Send a fresh chat message: `"summarize my top 3 at-risk strategic objectives"` — expect a grounded response citing real objective names from the account
2. Follow up: `"which one is the highest priority"` — expect the model to remember turn 1 and pick one with reasoning
3. Ask a tool question: `"pull the latest signal for that objective"` — expect the model to call the signal tool + return actual signal contents
4. Non-sequitur: `"what's the weather"` — expect polite refusal + redirect to strategic work
5. Complex synthesis: `"draft me a paragraph for a board deck about the intervention path on that objective"` — expect prose that could be pasted into a board doc

**Pass rubric**: (a) 4/5 turns produce grounded, board-worthy responses; (b) tool-use turn (3) actually calls the tool and includes real data; (c) no hallucinated objectives / signals / owners; (d) tone is executive-register throughout.

**Estimated time**: ~30 min.

### B.2 Surface 2 — Briefings

**Route**: Owner Digest email deliveries (`POST /api/cron/owner-digest`) + the on-demand Briefings surface in Solva v2 POC.

**Scenarios** (3 briefings):
1. Weekly Monday briefing for a heavy-signal week (10+ signals across 5 objectives) — expect a delta-focused briefing that surfaces the top 3 movements
2. Weekly briefing for a quiet week (0-1 signals) — expect the skip-if-no-delta gate to fire (no send)
3. On-demand catch-up briefing after a 2-week gap — expect the model to sensibly compress 2 weeks into a single coherent narrative

**Pass rubric**: (a) delta detection is accurate (top-3 movements are actually the top 3 by material change); (b) skip-if-no-delta fires correctly on quiet weeks; (c) 2-week catch-up doesn't hallucinate or drop material events.

**Estimated time**: ~45 min (requires seeding real signal deltas).

### B.3 Surface 3 — Catch-up

**Route**: Solva v2 catch-up trigger from the POC.

**Scenarios** (2 catch-up sessions):
1. Catch-up after a 5-day gap on a specific objective — expect a chronological narrative of signal + doc events during the gap
2. Catch-up after a 14-day gap — expect intelligent chunking + prioritization (no dump-everything-verbose)

**Pass rubric**: (a) chronology is accurate (events in correct order); (b) prioritization is board-worthy (top events surface first); (c) 14-day catch-up compresses appropriately (no verbose recital of every signal).

**Estimated time**: ~30 min.

### B.4 Surface 4 — Solve-deep

**Route**: Solva v2 solve-deep session (5-cycle terminal quality).

**Scenarios** (1 full 5-cycle solve on a real objective):
1. Pick a genuinely-hard strategic objective from the test account (`juliusaopio@gmail.com` per `test_credentials.md` L14 — 5 contexts × 6 committees × 14 strategic docs = rich substrate)
2. Run the full 5-cycle solve
3. Evaluate the terminal Bottom Line quality

**Pass rubric**: (a) each cycle builds on prior cycles (no repetition or amnesia); (b) terminal Bottom Line is board-worthy per Part A A.3 rubric; (c) evidence chain is intact (Bottom Line traces to origin data, not fabrication); (d) 5 cycles feel like progress not spinning.

**Estimated time**: ~60 min per solve; recommend running 1 solve for sign-off.

### B.5 Total time investment for .3

- Chat: ~30 min
- Briefings: ~45 min
- Catch-up: ~30 min
- Solve-deep: ~60 min
- **Total: ~2.75 hours** for a single full pass. Multiply by any regression cycles.

---

## Part C — Where to record sign-off

**Recording protocol** (per user directive on clean audit trail):

1. **DEV_PIPELINE §9 verification row** — user adds a new row of form:
   ```
   | LLM-REFRESH.<N>-USER-SIGNOFF — <PASS / PASS-with-note / FAIL> — <timestamp> — <user-name>
   | 2026-XX-XX (user marked signoff · new byte-ratchet <NNNN> for .2 · surfaces: chat=PASS briefings=PASS catchup=PASS solve=PASS for .3)
   | Free-form note field. Any material observations, tone drift, hallucinations caught, etc.
   | Cross-refs: LLM_REFRESH_SIGNOFF_CHECKLIST.md + LLM_MODELS_REFRESH_MATRIX.md
   ```

2. **`memory/jc_artifacts/FAILING_TEST_TRACKER.md` trajectory marker** — user adds a note under the FTT registry section:
   ```
   LLM-REFRESH .2 signoff 2026-XX-XX PASS · byte-ratchet moved 76555 → NNNNN
   LLM-REFRESH .3 signoff 2026-XX-XX PASS across all 4 surfaces (chat, briefings, catchup, solve-deep)
   ```

3. **On any FAIL**: user adds a note in the same §9 row + tags `HALT` in the summary; agent auto-detects the HALT and pauses the sub-sprint until user provides re-model selection or re-generation authorization.

**Do NOT sign off via chat message alone.** The DEV_PIPELINE row is the audit trail.

---

## Cross-references

- Matrix doc canonical: `sprints/LLM_MODELS_REFRESH_MATRIX.md` lines 136-172
- Evaluation memo (per-sub-task disposition audit): `sprints/JC_LLM_MODELS_REFRESH_EVALUATION.md §4.1 + §4.2`
- Scope-doc inaccuracy finding: `JC_LLM_MODELS_REFRESH_EVALUATION.md §3.2`
- Predecessor .1 closure: `sprints/LLM_REFRESH_1.md`
- F.6 Shield-contract discipline-pay applicability: `sprints/CLUSTER_G_RETROSPECTIVE.md §6.2`
- Byte-ratchet mechanism: `sprints/JC_TL_STAGE_1_GOLDEN_DECK.md` (or wherever the 76555-byte pin lives; grep `76555` if unsure)
- Test creds for surfaces: `memory/test_credentials.md` (admin@akki.ai + juliusaopio@gmail.com + bramuel@syni.ai)
