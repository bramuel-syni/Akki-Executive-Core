**Canonical Spec:** User dispatch **2026-07-02** (revised A3 scope after Option (i) DECK-024 descope) + `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A3`.

# JC-WS-DECK-PATH-A-A3-GENERATION-FLOW

**Type:** Build sub-sprint. **Second Path A dispatch.** User revised order: A3 → A2 → rename arc.
**Ships:** 2026-07-02.
**Testing method:** PURE BASH — `/app/backend/scripts/jc_ws_deck_a3_proving_slice.py` (15 rows). Testing sub-agents BANNED.
**Locked-area sweep:** F.6 Shield contract untouched · JC-CHAT invariants untouched (only extended `HandoffActions` gate) · Solva engine untouched · storage arc untouched · OAuth untouched · Monitor untouched · Surface A untouched.

---

## 0. Executive Summary

Path A's second dispatch closes the generation-completion journey. Three stories flip; DECK-024 is descoped per user's Option (i) after the R0 pre-scan surfaced a scope-shape conflict (CreateArtefactModal is a shell-creator, not a generator — extending StreamingLogScene to it required a new BE endpoint, tripping two escalation triggers). DECK-024 is reasserted as MET on the WS-side LLM-generation surfaces that already stream today.

**What shipped:**

| Story | State | How |
| :--- | :--- | :--- |
| DECK-024 | 🟡 PARTIAL → ✅ MET *(reassertion, see §X)* | ExportModal + LoadingChecklistModal already stream via `useStreamingProgress` + `<StreamingLogScene>`. |
| DECK-026 | ❌ MISSING → ✅ MET *(existing-surface reassertion, see §Y)* | ExportModal completion sheet already carries Download + Continue-in-Chat + Close on `phase === "complete"`. LoadingChecklistModal auto-opens the DocumentOverlay drawer with the Toolbar Download primitive one click away. |
| DECK-027 | ❌ MISSING → ✅ MET | `HandoffActions.jsx` Ask-in-Chat gate expanded from `kind === "document"` to `kind === "document" \|\| kind === "deck"`. Chat handoff routes via canonical `/app/chat?ctx_type=deck&ctx_id=<id>` URL pair. Bonus: closes DECK-069. |
| DECK-030 | ❌ MISSING → ✅ MET | Backend: `_create_continue_chat` doc_row insert now writes `lifecycle_state: "in_review"` (was `"draft"` in A1). Fires from `/work-studio/export/{kind}/stream` completion — the LLM-generation completion moment per the audit's fix pointer. |
| **Folded polish: `?pulse=` scroll-and-glow** | not-a-story | `DocumentCardsSection` reads `?pulse=<work_studio_exports_id>` from URL, scrolls the matching card into view, applies `.ws-doc-card-pulse-glow` (~1.8s box-shadow-pulse), then strips the URL param at t≈2.2s. Chrome conformance: mirrors the existing `cycle-card-pulse-kf` keyframe pattern exactly. Zero new deps / event bus / endpoints per user condition. |

**Backend touched:** 1 file, 1 LOC.
**Frontend touched:** `HandoffActions.jsx` (~15 LOC) + `DocumentCardsSection.jsx` (~30 LOC) + `index.css` (11 LOC — 1 new keyframe).
**Chrome conformance HARD rule honoured:** every affordance is a modification of an existing primitive or a mirror of an existing pattern.

---

## §X. DECK-024 Descope + MET Reassertion (per user Option (i))

**Original story:** *Monitor the progress of deck generation.*
**Audit classification (JC_WS_DECK_CONFORMANCE_AUDIT.md:117):** PARTIAL — "Only in `/app/decks` deep-tier path (`Decks.jsx:604-614` uses `StreamingLogScene` + `useStreamingProgress`). The WS `CreateArtefactModal` path is synchronous — no progress UI."

**A3 R0 pre-scan finding:** the audit's premise conflates two flows:
* `/app/decks` (Surface A) → 3-step Intent → Outline → Deck LLM streaming.
* WS `CreateArtefactModal` (Surface B create-modal) → **shell-creator, not a generator**. Currently POSTs to `/api/contexts/{cid}/work-studio/artefacts` which:
  * Creates a Draft row in `db.decks` / `db.reports` with seed body from brief snapshot OR document `akki_summary` (verbatim copy-paste, no LLM).
  * Returns `redirect_url` → `/app/studio/composer/{kind}/{id}` (block composer).
  * **0 LLM calls, 0 streaming, 0 async work.**
* The genuine WS-side LLM-generation flow is `ExportModal` + `LoadingChecklistModal`, which **already** stream via `useStreamingProgress`.

**Escalation trigger fired:**
* *"Progress surface can't cleanly reuse `useStreamingProgress` → surface with what would be needed"*
* *"Backend contract change beyond auto move-to-review call → surface, don't extend scope"*

**User resolution 2026-07-02:** Option (i) — descope DECK-024, reassert as MET on the WS-side LLM-generation surfaces.

**Grep evidence for reassertion:**
```
frontend/src/components/studio/ExportModal.jsx:25   import useStreamingProgress from "@/hooks/useStreamingProgress";
frontend/src/components/studio/ExportModal.jsx:68   const { state: streamState, stream, reset: resetStream } = useStreamingProgress();
frontend/src/components/studio/ExportModal.jsx:122  `${API_BASE}/contexts/${contextId}/work-studio/exports/${data.export_id}/stream`
frontend/src/components/studio/ExportModal.jsx:331  <StreamingLogScene state={streamState} ...
frontend/src/components/work_studio/LoadingChecklistModal.jsx:*  1.5s polling on `/work-studio/exports/{export_id}` (equivalent progress surface)
```

**Consequence:** the "monitor progress" user story is genuinely satisfied for the WS-side LLM-generation flows. The shell-creator CreateArtefactModal remains a synchronous form → composer redirect. Any user need for CreateArtefactModal to become a generator itself is a separate feature request (would require the new BE streaming endpoint blocked at A3 escalation) and is filed as a follow-on dispatch candidate `A3.a` (not queued).

---

## §Y. DECK-026 Existing-Surface Reassertion

**Original story:** *Download the deck immediately after generation.*
**Audit fix pointer:** "completion-modal component."

**Existing state discovered by R0 scan:**

* **ExportModal.jsx completion phase (`phase === "complete"` block, lines 344-407)** already renders:
  * "Composition complete." heading.
  * File name.
  * "Saved to Drafts & Briefs as a new document card" breadcrumb.
  * **Download button** (`data-testid="work-studio-export-download"`, line 393) → invokes `onDownload` prop → 2-step token-minted download flow (same primitive used by `DocumentCardsSection.onDownload`).
  * **Continue in chat button** (`data-testid="work-studio-export-continue-chat"`, line 400) — gated on `continueChatId`.
  * **Close button.**
* **LoadingChecklistModal completion path** (from-listing compile flow): on `status === "complete"`, `WorkStudio.jsx:1454-1476` handler:
  * Refetches aggregates.
  * Dispatches `akki:document-card-pulse` (used by `DocumentCardsSection` for refetch).
  * Sets `?doc_id=<continue_doc_id>` → DocumentOverlay opens automatically → the Toolbar Download primitive (`document-overlay-download-docx-btn` / `pdf-btn` / `pptx-btn`, lines 430/440/450) is one click away in the toolbar.

**Reassertion:** DECK-026 is MET on both LLM-generation completion surfaces:
1. Modal-flow (Compile / Enhance) → ExportModal completion sheet with Download/Continue/Close.
2. From-listing flow → drawer auto-open with immediate Toolbar Download.

Building a NEW completion modal for the from-listing flow was explicitly rejected per the chrome-conformance HARD rule (no second way of doing the same thing). The drawer IS the completion surface for that flow; Toolbar Download is the immediate affordance.

---

## 1. Chrome Conformance HARD Rule (self-audit)

| Story | Chrome conformance verdict |
| :--- | :--- |
| DECK-024 (descoped) | No chrome introduced. Existing streaming primitive left intact. |
| DECK-026 (reassertion) | No new completion modal built. Existing ExportModal sheet + existing DocumentOverlay Toolbar affordance recognised as fully compliant. |
| DECK-027 + DECK-069 | Existing "Ask in Chat" button primitive; gate expanded from 1 kind → 2 kinds. Same button, same chip, same handoff URL contract (`/app/chat?ctx_type=<kind>&ctx_id=<id>`). Zero new UI. |
| DECK-030 | 1-LOC backend field flip in existing insert path. No new endpoint. No new UI. |
| Pulse polish | Mirrors `cycle-card-pulse-kf` keyframe exactly (0.5s → 0.6s per cycle, otherwise identical). Reuses `data-pulse` attribute pattern already present in `CycleCard.jsx:78`. Zero new event bus, zero new deps, zero new endpoints. |

---

## 2. ThinkLab-Ready Strings Guard (A1 continuation)

A3 introduces **zero new module-referring copy.** The only new user-visible strings are:
* Toast text: "Opened a chat tethered to this deck." — kind-referring, not module-referring. Zero "Solva" or "ThinkLab" mentions.
* No changes to `moduleLabels.js` needed.

Slice R9 grep-asserts no new "Solva" strings in A3-touched frontend files.

---

## 3. Product Code Changes

### 3.1 Backend

**`/app/backend/routers/work_studio_export.py`** — `_create_continue_chat` doc_row insert:

```py
# JC-WS-DECK-PATH-A-A3-GENERATION-FLOW (2026-07-02) — DECK-030
# auto Draft → In Review on LLM-generation completion. This
# write path fires from `/work-studio/export/{kind}/stream`
# completion (compile / enhance / brief flows), which is the
# *generation completion moment* per the audit's DECK-030 fix
# pointer. A1 landed this at `"draft"`; A3 flips to `"in_review"`
# because compile/enhance/brief outputs are LLM-generated content
# ready for the user to REVIEW — not a shell they still need to
# draft. Surface A (`db.decks`) untouched.
"lifecycle_state": "in_review",
```

### 3.2 Frontend

**`/app/frontend/src/components/shell/HandoffActions.jsx`** — Ask-in-Chat gate + handoff:

```jsx
const askInChatEligible = (kind === "document" || kind === "deck") && !!id;
const onAskInChat = useCallback(() => {
  if (!askInChatEligible) return;
  navigate(`/app/chat?ctx_type=${encodeURIComponent(kind)}&ctx_id=${encodeURIComponent(id)}`);
  toast.success(
    kind === "deck"
      ? "Opened a chat tethered to this deck."
      : "Opened a chat tethered to this document.",
  );
}, [askInChatEligible, kind, id, navigate]);
```

Button render gate updated: `{askInChatEligible && (…)}` (was `{kind === "document" && id && (…)}`). New attribute on the button: `data-ask-in-chat-kind={kind}`.

**`/app/frontend/src/components/work_studio/DocumentCardsSection.jsx`** — pulse polish:

* Imports `useSearchParams` + `useRef`.
* Reads `searchParams.get("pulse")` at top of `DocumentCardsSection`.
* New `useEffect` triggers `scrollIntoView` on match + strips the URL param at t≈2.2s.
* `DocumentCardRow` accepts new props `pulsed` + `pulseRef`, applies `data-pulse="true"` + `.ws-doc-card-pulse-glow` when matched.

**`/app/frontend/src/index.css`** — new `.ws-doc-card-pulse-glow` keyframe (mirrors `cycle-card-pulse-kf` byte-for-byte with 0.6s per cycle instead of 0.5s).

### 3.3 What did NOT change

* **Surface A** (`Decks.jsx`, `db.decks`, `/app/decks`) — byte-identical.
* **CreateArtefactModal** — untouched (descoped per Option (i)).
* **ExportModal + LoadingChecklistModal** — untouched (completion sheets reasserted as MET).
* **DocumentOverlay** chrome — untouched.
* **Chat surface** — untouched (HandoffActions gate expansion only extends existing pattern).
* **Solva engine** — untouched.

---

## 4. Locked-Area Sweep (memo)

* 0 Shield-adjacent code touched.
* 0 JC-CHAT surface files touched (`HandoffActions.jsx` is in `components/shell/`, not the chat surface itself).
* 0 Solva engine files touched.
* 0 storage-arc files touched.
* 0 OAuth files touched.
* 0 Monitor files touched.
* 0 Surface A files touched.
* Zero-Handoff-Loss: `DEV_PIPELINE.md §9` row landed BEFORE any code edit or memo authoring.
* Canonical Spec citation on line 1.
* Six banked discipline lessons in play throughout.

---

## 5. Proving Slice (15 rows)

**File:** `/app/backend/scripts/jc_ws_deck_a3_proving_slice.py`.

| # | Row | Method |
| ---: | :--- | :--- |
| R1 | Pre-fix baseline — FE-only-label invariant + pollution ceilings still GREEN | pytest |
| R2 | DECK-024 reassertion evidence — ExportModal imports `useStreamingProgress`, streams via `/work-studio/exports/{eid}/stream` | Static grep |
| R3 | DECK-026 reassertion evidence — ExportModal completion sheet renders Download + Continue-in-Chat + Close on `phase === "complete"` | Static grep |
| R4 | DECK-027 gate expansion — `HandoffActions.jsx` accepts `kind === "deck"` for Ask-in-Chat | Static grep |
| R5 | DECK-069 folded — `handoff-ask-in-chat` button renders for deck kind (via `askInChatEligible` predicate) | Static grep |
| R6 | DECK-030 lifecycle flip — `_create_continue_chat` doc_row writes `lifecycle_state: "in_review"` | Static grep |
| R7 | Pulse polish — `DocumentCardsSection` reads `searchParams.get("pulse")`; applies `data-pulse` + `.ws-doc-card-pulse-glow` on match | Static grep |
| R8 | Pulse condition — no new npm deps, no new backend endpoints, no new event bus | Multi-grep negative |
| R9 | ModuleLabel-ready strings — 0 new "Solva" or "ThinkLab" strings introduced in A3-touched FE files (outside moduleLabels.js) | Static grep |
| R10 | DocumentOverlay chrome unchanged — Toolbar Download button testids present | Static grep |
| R11 | JC-CHAT invariants preserved | pytest |
| R12 | F.6 Shield-contract discipline-pay | pytest |
| R13 | FE-only-label invariant still GREEN | pytest |
| R14 | Pollution ceilings unchanged (M1=0 / M2=1) | pytest |
| R15 | End-to-end shape audit — completion journey: LLM-generation → `in_review` lifecycle → ExportModal completion sheet OR drawer auto-open → Download / Ask-in-Chat (deck kind) / pulse-glow | Static shape check |

---

## 6. HARD STOP

15-row proving slice landed. **NO auto-dispatch to A2.** A2 = From-Source create journey closure (DECK-017 / 018 / 020 / 021 / 022). A2 fires ONLY on explicit user approval.

Surfacing for user review + next-dispatch pick.
