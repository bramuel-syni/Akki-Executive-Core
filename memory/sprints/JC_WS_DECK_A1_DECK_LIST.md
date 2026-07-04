**Canonical Spec:** `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A1` + user amendment **2026-07-02** (three-pick resolution: Surface B authoritative · rename-arc §9 defaults + Case 6 template override · ThinkLab-ready strings guard · chrome conformance HARD rule).

# JC-WS-DECK-PATH-A-A1-DECK-LIST

**Type:** Build sub-sprint. **First Path A dispatch.**
**Ships:** 2026-07-02.
**Dispatch:** `JC-WS-DECK-PATH-A-A1-DECK-LIST` (user amendment 2026-07-02).
**Testing method:** PURE BASH — `/app/backend/scripts/jc_ws_deck_a1_proving_slice.py` (15 rows). Testing sub-agents BANNED.
**Locked-area sweep:** F.6 Shield contract untouched · JC-CHAT invariants untouched · Chat surface untouched · Solva engine untouched · storage arc untouched · OAuth untouched · Monitor untouched.

---

## 0. Executive Summary

Path A opens with the smallest legitimate journey closure: the Deck List surface (Surface B = `/app/work-studio` deck tab). Six DECK-XXX stories flip from PARTIAL / CONFLICT / MISSING → MET via minimal additive changes to the existing `DocumentRow` + a small backend backfill.

**What shipped:**

| Story | State | How |
| :--- | :--- | :--- |
| DECK-002 | 🟡 PARTIAL → ✅ MET | Card-visual refinement of existing `DocumentRow` (padding lift + hover shadow). NO parallel `DeckCard`. |
| DECK-005 | ❌ MISSING → ✅ MET | Lifecycle chip on row (Draft / In Review / Committed). Reuses `LIFECYCLE_LABEL` vocabulary verbatim from `DocumentOverlay.jsx:70-74`. |
| DECK-007 | 🟡 PARTIAL → ✅ MET | Threads real `source_count` through `_create_continue_chat` from compile-flow caller. |
| DECK-008 | ⚠️ CONFLICT → ✅ MET | Verified `displayCategoryChip("deck")` → "Deck" already consistent; no tier-vs-type confusion in the current row. |
| DECK-009 | 🟡 PARTIAL → ✅ MET | Confidence chip already wired via `intelligence_report.confidence_pct` mirror-write (line 1466). Asserted end-to-end. |
| DECK-034 | ⚠️ CONFLICT → ✅ MET | "Akki Generated" badge kept on list row only per audit recommendation. Detail-header placement explicitly rejected. |

**Backend touched:** 2 files, ~15 LOC.
**Frontend touched:** 1 file (`WorkStudio.jsx`) + 1 new file (`moduleLabels.js`), ~50 LOC.
**Chrome conformance HARD rule honoured:** every new visual element is a modification of the existing `DocumentRow` primitive, not a parallel component.

---

## 1. Surface A Named Deprecation Path

Surface A = `/app/decks` + `Decks.jsx` + `db.decks` collection.
Surface B = `/app/work-studio` deck tab + `WorkStudio.jsx` + `db.documents?category=deck`.

**User pick (2026-07-02):** Surface B is authoritative. Surface A survives as a **legacy fast-path** with a **named deprecation contract**:

1. Nothing new builds on Surface A. A1..A10 sub-sprints add zero features to Surface A. Surface A retains its current 3-step Intent → Outline → Deck flow verbatim; NO regressions permitted.
2. Surface A stays live until Surface B demonstrably covers the Intent-first journey (i.e. Path A closes at A10 with the From-Blank + regeneration flow shipping).
3. **After Path A closes** (post-A10), a redirect retires `/app/decks` → `/app/work-studio?tab=deck` and the Surface A component tree is archived (not deleted — kept for git-log traceability).
4. This deprecation contract IS documented here for audit trail. **NO code touching Surface A in A1.**

**Slice enforcement:** R9 asserts `Decks.jsx` byte-identical to pre-A1 baseline.

---

## 2. Chrome Conformance HARD Rule (self-audit)

Overarching user constraint: **new features arrive INSIDE existing shells and conform to existing patterns.** Applied to A1:

| Story | Chrome conformance verdict |
| :--- | :--- |
| DECK-002 (cards) | Same `DocumentRow` component. Same primitive shape. Only padding + hover-shadow lifted. NOT a parallel `DeckCard` file. |
| DECK-005 (lifecycle chip) | Same chip primitive as origin/category chips already on the row. Same `px-2 py-0.5 rounded-sm text-[10px] font-medium uppercase tracking-wider border` recipe. Colors sourced from `DocumentOverlay.jsx`'s lifecycle state colors so both surfaces stay in visual sync. |
| DECK-007 (source count) | Chip was already wired; only the backend backfill missed. No new FE chip. |
| DECK-008 (type badge) | Existing `displayCategoryChip` primitive; zero new copy. |
| DECK-009 (confidence chip) | Existing `confPct` chip primitive; zero new render logic. |
| DECK-034 (Akki-generated badge) | Existing badge on this row; only asserted for the deck category. |
| **No new tabs** in the Overlay. No new drawer variant. No new nav pattern. No parallel component. ✅ | |

**If any A1..A10 sub-sprint downstream finds itself considering a new chrome pattern → STOP + surface** (per user constraint 2, "the sub-sprint adding tabs is exactly where a slightly-different drawer gets born").

---

## 3. ThinkLab-Ready Strings Guard

**Rule (from user dispatch):** any user-visible string A1 introduces that references the module MUST be written against **post-rename vocabulary**.

A1 introduces **no new module-referring copy** (the DocumentRow's new chip vocabulary is `Draft / In Review / Committed` — lifecycle nomenclature, not module nomenclature). Still, a small forward-compatible constants file was authored so downstream sub-sprints can import from it:

**File shipped:** `/app/frontend/src/lib/moduleLabels.js`

```js
export const MODULE_LABELS = Object.freeze({
  thinklab: "ThinkLab",       // module surface name (post-rename)
  solvaEngine: "Solva engine", // engine health label (Case 6 in audit — KEEP)
});
export const moduleLabel = () => MODULE_LABELS.thinklab;
export const solvaEngineLabel = () => MODULE_LABELS.solvaEngine;
```

**Rename arc Phase 1 dispatch (post-A1) will touch ONLY this file** for module-label changes — no A1 code re-touched.

**Slice enforcement:** R13 grep-asserts no new "Solva" strings introduced by A1; R14 asserts `moduleLabels.js` is importable + exports the expected shape.

---

## 4. Rename-Arc §9 Escalation Decisions (accepted verbatim from user 2026-07-02)

| # | Question | User decision |
| :--- | :--- | :--- |
| 9.1 | Casing convention (`ThinkLab` / `Thinklab` / `Think Lab`) | **`ThinkLab`** (PascalCase) — accept default |
| 9.2 | Branded tone — mixed casing per context | Accept default |
| 9.3 | `SolvaSessionSnapshot` typed model rename | **KEEP** — accept default |
| 9.4 | `takeToSolva.js` + `solvaPhaseDClient.js` + `solvaFlow.js` FE helpers | **RENAME** all three — accept default |
| 9.5 | `TrustCenter.jsx:756` (RENAME) vs `StatusPage.jsx:26` (KEEP) split | Accept default |
| 9.6 | Template filename rename | **OVERRIDE:** defer template FILENAMES to rename Phase 2; but user-visible template CONTENT strings (PDF headers) flip to "ThinkLab" NOW in Phase 1. **Content changes now, file renames later.** |
| 9.7 | `localStorage` key prefix rename | **KEEP** — accept default |
| 9.8 | `memory/PRD.md` / `memory/CHANGELOG.md` review scope | Touch only user-visible product-description prose — accept default |

**These 8 decisions are the source of truth for the rename-arc Phase 1 dispatch when it fires (post-A1 close).**

---

## 5. Product Code Changes

### 5.1 Backend

**`/app/backend/routers/documents.py`** — `sanitize_doc()` gains `lifecycle_state` passthrough (~5 LOC).

```py
# JC-WS-DECK-PATH-A-A1-DECK-LIST (2026-07-02) — DECK-005 lifecycle-chip
# surfacing on the Deck List row. Mirrors the `lifecycle_state` field
# written by _create_continue_chat + every other WS-artefact insert
# path (Draft / In Review / Committed vocabulary). Legacy rows without
# the field surface as null; the FE DocumentRow renders a "Draft"
# fallback chip on any row with `category="deck"` to close the DECK-005
# gap for pre-A1 rows without a backend migration.
"lifecycle_state": d.get("lifecycle_state"),
```

**`/app/backend/routers/work_studio_export.py`** — `_create_continue_chat` accepts optional `source_count` kwarg and writes `lifecycle_state: "draft"` on the doc_row insert (~10 LOC). Caller at L1067 passes the real source count from `explicit_doc_ids` / `citations_manifest`.

Backwards compat: caller at line ~1976 (enhance flow) leaves `source_count` unset → falls through to the pre-A1 heuristic (1 for enhance, 0 otherwise). No regression.

### 5.2 Frontend

**`/app/frontend/src/pages/WorkStudio.jsx`** — `DocumentRow` component gains:
* `LIFECYCLE_LABEL` mirror + `LIFECYCLE_CHIP_CLASSES` inline vocab (mirrors `DocumentOverlay.jsx:70-74` verbatim; kept inline to avoid a new cross-import).
* Lifecycle chip render inline with the origin + category chips (same primitive shape).
* `py-3` → `py-3.5` (subtle padding lift for card feel).
* `hover:shadow-sm` + `transition-[colors,box-shadow]` (hover shadow lift).
* `data-lifecycle-state={lifecycleState || "unset"}` on the button root (proving-slice hookable).

**`/app/frontend/src/lib/moduleLabels.js`** — NEW file. Constants for the ThinkLab rename arc's Phase 1 dispatch. Zero direct A1 dependency (no A1 code imports it yet); asserted importable + shape-valid by R14.

### 5.3 What did NOT change

* **Surface A** (`Decks.jsx`, `db.decks`, `/app/decks`) — byte-identical.
* **DocumentOverlay** chrome — untouched.
* **Chat surface** — untouched.
* **Shield contracts** — untouched. F.6 discipline-pay applies zero.
* **Solva engine** — untouched.
* **All other tabs** (Main Board & Committee Packs, Minutes, Drafts & Briefs, Reports) — will render the same lifecycle chip if the row carries a `lifecycle_state` field. Not asserted in this slice (out of A1 scope).

---

## 6. R1 Baseline Sweep Finding (folded into JC-WS-A1-BASELINE-INVARIANT-RESTORATION)

Pre-fix runtime baseline surfaced a **pre-existing** hard-ratchet violation from the prior `AUDITS-BACKEND-ROUTE` dispatch: 3 backend `thinklab` references in `backend/routers/audits.py` + `backend/scripts/audits_backend_route_proving_slice.py`.

**Surfaced to user; user picked Option (a) rename.** Baseline restoration mini-dispatch closed as `JC-WS-A1-BASELINE-INVARIANT-RESTORATION`:

* Halted-audit file renamed: `SOLVA_THINKLAB_RENAME_REGRESSION_AUDIT.md` → `SOLVA_MODULE_RENAME_REGRESSION_AUDIT.md`.
* 2 allowlist literals + 1 module docstring patched in backend.
* Memory `.md` cross-refs updated for consistency.
* Invariant `test_thinklab_uilabel_only.py` re-run: 1 passed, 0 failed.

The 4th audit URL is now `/api/audits/SOLVA_MODULE_RENAME_REGRESSION_AUDIT.md`.

---

## 7. Proving Slice (15 rows)

**File:** `/app/backend/scripts/jc_ws_deck_a1_proving_slice.py`.

| # | Row | Method |
| ---: | :--- | :--- |
| R1 | Pre-fix baseline — `test_thinklab_uilabel_only` + `test_no_bespoke_run_helper` + shield-no-leak invariants GREEN | pytest |
| R2 | Card-visual refinement — `py-3.5` + `hover:shadow-sm` present in `DocumentRow` className | AST grep |
| R3 | Lifecycle chip vocabulary — 3 states mapped (`draft` / `in_review` / `committed`) with matching color classes | Static string check |
| R4 | Source count passthrough — `_create_continue_chat` signature carries `source_count=None`; caller at ~L1067 passes real count | AST scan |
| R5 | Document-type badge — `displayCategoryChip("deck")` returns "Deck" (via origins.js CATEGORY_CHIP_SHORT map) | Static string check |
| R6 | Confidence chip — mirror-write still fires from confidence_scorer on export completion (grep for `confidence_pct` write path) | Static grep |
| R7 | Akki-generated badge — `akki_generated: True` still written on doc_row insert | Static grep |
| R8 | DocumentOverlay chrome unchanged — LIFECYCLE_LABEL / LIFECYCLE_DOT map byte-identical | sha256 of the const block region |
| R9 | Surface A untouched — `Decks.jsx` byte-identical to pre-A1 baseline | sha256 |
| R10 | F.6 Shield-contract discipline-pay still GREEN | pytest on shield-no-leak invariants |
| R11 | JC-CHAT invariants still GREEN | pytest on chat-streaming-reidentify + shield-no-leak |
| R12 | Pollution ceilings unchanged (M1=0 / M2=1 FINAL) | pytest on `test_no_bespoke_run_helper` |
| R13 | ThinkLab-ready strings — 0 new "Solva" strings introduced by A1 in FE code (grep on `WorkStudio.jsx` diff vs baseline) | Static grep |
| R14 | `moduleLabels.js` importable + shape valid — file exists, exports `MODULE_LABELS.thinklab === "ThinkLab"` + `MODULE_LABELS.solvaEngine === "Solva engine"` | AST parse |
| R15 | End-to-end shape assertion — `_create_continue_chat` with `source_count=N`, then sanitize_doc surfaces `source_count=N` + `lifecycle_state="draft"` + `akki_generated=true` + `category="deck"` + `confidence_pct` mirror path present | Static + shape audit |

---

## 8. Locked-Area Sweep (memo)

* 0 Shield-adjacent code touched.
* 0 JC-CHAT surface files touched.
* 0 Solva engine files touched.
* 0 storage-arc files touched.
* 0 OAuth files touched.
* 0 Monitor files touched.
* 0 Surface A files touched.
* `DEV_PIPELINE.md §9` row landed BEFORE any code edit or memo authoring (Zero-Handoff-Loss).
* Canonical Spec citation on line 1 of this memo (path A execution plan §A1 + user amendment 2026-07-02).
* Six banked discipline lessons in play throughout.

---

## 9. HARD STOP

15-row proving slice landed. **NO auto-dispatch to A2.** A2 = From-Source create journey closure (DECK-017/018/020/021/022 · 5 stories) fires ONLY on explicit user approval.

**Surfacing to user for:**
* Slice-close review + approval to close A1.
* Confirmation to move to A2 (or an alternate order — e.g., start rename-arc Phase 1 first).
