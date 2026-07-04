**Canonical Spec:** `/app/memory/SPRINT_PLAN.md §5` (ThinkLab track) + `SPRINT_PLAN.md:99` architectural lock ("ThinkLab is UI label only; internal names stay solva (build-breaking invariant)") · **User dispatch:** `JC-USER-FOLLOWUP-3-TASKS` Task 2 · **Date:** 2026-07-02

# SOLVA-THINKLAB-RENAME-REGRESSION-AUDIT

**Type:** READ-ONLY grep-only regression audit.
**Ships:** 2026-07-02.
**Testing method:** N/A (documentation audit; no code touched).
**Locked-area sweep:** 0 product code touched · 0 tests touched · 0 planning memos touched · 0 sprint memos written outside this audit + the `DEV_PIPELINE.md §9` row entered BEFORE this file.

---

## 0. User Direction (verbatim)

> "Solva Module has not been renamed to ThinkLab — Need Solva model exclusively retaining the name."

**Interpretation:** Solva stays Solva. Block any pending "ThinkLab" rename on user-visible product surfaces. Internal sprint-identifier shorthand (`JC-TL`, `TL0`, `TL1.1`, `PHASE_TL0`) is OK to retain as internal aliases per user's escalation-trigger guidance ("internal sprint memos … OK to keep as internal identifiers").

---

## 1. Headline Finding

**The rename WAS NEVER EXECUTED on user-visible code.** All user-visible strings today say "Solva". The concern is not a regression revert — it is a **scope block on a pending future rename** described in planning memos but not yet implemented.

| Surface | User-visible "ThinkLab" occurrences | User-visible "Solva" occurrences | Notes |
| :--- | ---: | ---: | :--- |
| `frontend/src/**` (.jsx / .js / .ts / .tsx / .css / .json) | **0** | 1099 | Grep confirmed zero. |
| `frontend/public/`, `frontend/*.html`, `frontend/package.json` | **0** | (n/a) | Grep confirmed zero. |
| `backend/**` (.py / .txt / .md / .j2 / .html / .json, excluding `tests/` + `scripts/`) | **0** | (many — canonical engine name) | Existing invariant `tests/invariants/test_thinklab_uilabel_only.py` is a build-breaking guard at zero backend hits. |

**Consequence:** there is nothing user-visible to revert. The user's direction should be actioned by rescinding the planning-memo commitment to a future ThinkLab-on-FE rename, NOT by patching product code.

---

## 2. Where "ThinkLab" DOES Appear (memory-only, non-user-visible)

**Bucketed count: 12 files · ~30 lines total.** All are planning / audit / sprint memos or internal invariant filenames. None are shipped as user-visible copy.

### 2.1 Architectural-lock references (rescind-candidates)

| File | Line | Exact string (excerpt) | Nature | Recommendation |
| :--- | ---: | :--- | :--- | :--- |
| `memory/SPRINT_PLAN.md` | 20 | `"ThinkLab — guided multi-path reasoning experience over the existing Solva engine. Non-creator user completes any of four paths unaided…"` | Track definition — declares ThinkLab as the FE-visible surface | **REVERT** the framing to "Solva — guided multi-path reasoning experience". Retain the four-paths + reasoning semantics; drop the ThinkLab label. |
| `memory/SPRINT_PLAN.md` | 78 | `"Don't conflate tracks. Chat is not ThinkLab. ThinkLab is not Track A."` | Cross-track discipline note — mentions ThinkLab as if canonical | **REVERT** to "Chat is not Solva. Solva is not Track A." |
| `memory/SPRINT_PLAN.md` | 99 | `"ThinkLab is UI label only; internal names stay 'solva' (build-breaking invariant)."` | **The architectural lock itself** — this is the decision the user is rescinding | **RESCIND**. Replace with: "Solva is the surface AND the engine name; user-visible product copy MUST say Solva. Frontend rename to ThinkLab is DE-SCOPED per 2026-07-02 user direction." |
| `memory/SPRINT_PLAN.md` | 132 | `"…ThinkLab layer-order pulled back from 'SHARED' to 'logic shared, per-path order confirmed'…"` | Historical decision note | **KEEP** as historical record; add a marginal note that ThinkLab label is now de-scoped. |
| `memory/DEV_PIPELINE.md` | 203 | `"Engine vs surface name guard \| backend/ MUST NOT contain thinklab (case-insensitive); engine is Solva v2, ThinkLab is FE-only surface; hard ratchet at tests/invariants/test_thinklab_uilabel_only.py; Stage 1 close-out 2026-06-24"` | Invariant-ladder entry describing the split-name intent | **REPHRASE.** Keep the build-breaking invariant that backend has zero `thinklab` (still valuable defensively). But strip the "ThinkLab is FE-only surface" claim from the description; replace with "backend defensively locked against thinklab tokens; FE product copy uses Solva verbatim (no split-name model)". |
| `memory/DEV_PIPELINE.md` | 241 | `"TL Flag 3 (P0 right now): reference deck anchor — … (c) push back on framing → two-track ThinkLab + Decks-upgrade"` | External-blockers list — TL Flag 3 uses ThinkLab as label | **KEEP** as internal shorthand (`TL`, `Track TL`, `TL Flag 3` are all internal sprint identifiers per user's escalation-trigger note). Optionally rename to `Solva Flag 3` for consistency; user's call. |
| `memory/INVARIANT_HEALTH.md` | 37 | `"Engine vs surface name guard \| backend/ MUST NOT contain thinklab (case-insensitive) \| pytest tests/invariants/test_thinklab_uilabel_only.py -q \| 2026-06-24 \| ✅"` | Invariant health dashboard | **REPHRASE** same as DEV_PIPELINE.md:203. |

### 2.2 Historical-record references (KEEP)

These are historical planning artefacts. They record decisions that were made at a moment in time. Modifying them would rewrite history. Per zero-handoff-loss discipline they should stay as-is with a marginal note.

| File | Line | Exact string | Nature | Recommendation |
| :--- | ---: | :--- | :--- | :--- |
| `memory/PRD.md` | 297 | `"…escape allowlist + thinklab UI-label-only guard. Stage 2: clean-board…"` | PRD history — Stage 1 close-out record | **KEEP** as history. |
| `memory/PRD.md` | 321 | `"(Re-architecture · ThinkLab · Chat · Work Studio), invariant…"` | PRD history — track enumeration at a point in time | **KEEP** as history. Optional marginal note per §2.1. |
| `memory/CHANGELOG.md` | 675-676 | `"280b4549 — P2.4: test_thinklab_uilabel_only.py (case-insensitive thinklab scan of backend/; 0 hits today; hard-ratchet; FE-only surface allowed)"` | Changelog for a shipped commit | **KEEP** as history. |
| `memory/audit/JC_WS_ui_inventory.md` | 31 | `"The original '3 source origins (chat artefact · ThinkLab session · docs+signals+cycle)' model is [SUPERSEDED]"` | UI-inventory audit — already marked as SUPERSEDED | **KEEP** — self-supersedes correctly. Additional note optional but not required. |
| `memory/audit/JC_WS_ui_inventory.md` | 45 | Same context — `~~Source picker: ThinkLab session~~ ⛔ SUPERSEDED 2026-06-25` | Already SUPERSEDED with strikethrough | **KEEP** — already correctly closed. |
| `memory/audit/JC_WS_ui_inventory.md` | 108, 151 | `"Brief — ThinkLab session source (Journey 3)"` | Two additional mentions inside the same superseded section | **KEEP** — same superseded context. |
| `memory/JC_WS_CANONICAL_SPEC.md` | 254 | `"ThinkLab Gate A — comes AFTER JC-WS closes per user's ordering (Work Studio → ThinkLab → Chat)"` | JC-WS canonical spec — sequencing note referencing ThinkLab as track name | **AMBIGUOUS** — the reader intent is track-order. Recommend leaving as-is but adding a footnote: "Track name only; user-visible surface is Solva per 2026-07-02 direction." User to confirm. |

### 2.3 Sprint memos (KEEP — internal sprint identifiers)

The following sprint memos reference `ThinkLab` in their body prose as a track/label name. Per user's escalation-trigger guidance, sprint memo internal identifiers can stay:

| File | Occurrences | Recommendation |
| :--- | ---: | :--- |
| `memory/sprints/STAGE_4_WORK_STUDIO.md` | 1 (line 43) | KEEP (historical) |
| `memory/sprints/PHASE_WS0_CLASSIFY.md` | 3 (lines 134, 316, 319) | KEEP (historical) |
| `memory/sprints/STAGE_5_FE_SHELL_VERIFICATION.md` | 1 (line 141) | KEEP (historical) |
| `memory/sprints/PHASE_B1_CHAT_BUILD.md` | 1 (line 204) | KEEP (historical) |
| `memory/sprints/PHASE_WS1_REPAIR.md` | 1 (line 199) | KEEP (historical) |
| `memory/sprints/STAGE_1_SECURITY_RATCHET.md` | 6 (lines 15, 25, 134, 136, 138, 140, 143, 144, 159, 173) | KEEP — this memo IS the ThinkLab-UI-label-only lock's ship memo. Historical record. |
| `memory/sprints/PHASE_SPRINT_PLAN_INIT.md` | 3 (lines 14, 21, 45, 94) | KEEP (historical) |
| `memory/sprints/PHASE_AUDIT_P1.md` | 2 (lines 371, 373) | KEEP (historical) |

### 2.4 Invariant file (KEEP filename; consider inverting logic)

| File | Nature | Recommendation |
| :--- | :--- | :--- |
| `backend/tests/invariants/test_thinklab_uilabel_only.py` | Build-breaking guard: backend must contain zero `thinklab` tokens (case-insensitive). Currently GREEN at 0 hits. | **KEEP** the invariant itself (defensively useful — prevents accidental `thinklab` naming from leaking into engine code). Rename recommended: `test_no_thinklab_in_backend.py` to drop the "UI-label-only" implication. Optionally ADD companion invariant `test_no_thinklab_in_frontend.py` (mirror on `frontend/src/**`) to lock the user's 2026-07-02 direction into the CI pipeline. User's call on the companion. |

---

## 3. Bucketed Totals

| Bucket | Files | Lines | Recommendation |
| :--- | ---: | ---: | :--- |
| Rescind-candidates (planning locks) | 3 | 5 | REVERT / RESCIND / REPHRASE per user direction |
| Historical-record (keep as history) | 4 | ~10 | KEEP + optional marginal note |
| Sprint memo internal identifiers | 8 | ~19 | KEEP (per user's escalation guidance) |
| Invariant filename | 1 | 1 | KEEP (defensive); optional companion FE-invariant |
| **User-visible product code** | **0** | **0** | **NOTHING TO REVERT** |
| **Total user-visible "ThinkLab" leakage into shipped surfaces** | **0** | **0** | **Zero regression exposure.** |

---

## 4. Recommended Action (no code changes yet — awaiting user approval)

The user's direction is a **scope block**, not a revert. To honour it:

1. **Rescind** `SPRINT_PLAN.md:99` — replace the architectural lock line with a de-scoping note pointing at 2026-07-02 user direction. (~3 line edit.)
2. **Rephrase** `DEV_PIPELINE.md:203` + `INVARIANT_HEALTH.md:37` — keep the build-breaking invariant but drop the "ThinkLab is FE-only surface" framing. (~2 line edits per file.)
3. **Update** `SPRINT_PLAN.md:20 + :78` — swap "ThinkLab" for "Solva" in track description + cross-track discipline note. (~2 line edits.)
4. **Optionally add** `backend/tests/invariants/test_no_thinklab_in_frontend.py` mirroring the existing backend guard onto `frontend/src/**`. (~40 LOC new test file. Build-breaking. Would surface any accidental future ThinkLab leakage in FE.)

**Total lift if user approves:** ~1 hour of planning-memo edits + optionally 30 minutes for the FE-side invariant. No product-code changes needed.

**HARD STOP** — surfaced for user approval. Do NOT execute rescissions until user confirms.

---

## 5. Locked-Area Sweep

* 0 product code touched.
* 0 tests touched (`test_thinklab_uilabel_only.py` NOT edited).
* 0 planning memos touched (only READ; no rescissions executed pending user approval).
* 0 additional sprint memos authored beyond this audit.
* Zero-Handoff-Loss discipline honoured: `DEV_PIPELINE.md §9` row landed BEFORE this file.

## 6. HARD STOP

Read-only grep sweep complete. **No follow-up implementation without explicit user dispatch on §4.** Surfacing for user direction: approve §4 Steps 1-3 (rescission of ThinkLab-UI-label-only lock) and Step 4 (optional FE-invariant companion) — or reject and leave planning memos as-is.
