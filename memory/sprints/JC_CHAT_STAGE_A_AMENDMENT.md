**Canonical Spec:** `/app/memory/JC_CHAT_CANONICAL_SPEC.md §A` ("The one Synisense marker") + **User amendment 2026-07-02**: `JC-CHAT-STAGE-A-AMENDMENT-SHIELD-PILL-PLUS-SEE-MORE` — pill + See more coexist alongside `PerMessageSynisenseBadge`. Two Synisense markers per assistant turn is the new legitimate state.

# JC-CHAT-STAGE-A-AMENDMENT — Shield pill + See more

**Type:** Amendment sprint (targeted additive MOD, NOT a rollback).
**Ships:** 2026-07-02.
**Dispatch:** `JC-CHAT-STAGE-A-AMENDMENT-SHIELD-PILL-PLUS-SEE-MORE`.
**Baseline captured pre-fix (lesson #5):** Chat.jsx sha256 `3d014087cd1de76a` · HEAD `48336287` · UTC `2026-07-02T16:15:36Z`.
**Locked-area sweep:** 0 backend contract change · 0 backend routes added · 0 backend tests modified · 0 non-chat surface touched · `PerMessageSynisenseBadge` byte-identical to pre-fix · `AggregateStrip.jsx` stays deleted · `AuditPanel.jsx` shared component untouched.

---

## 0. User Direction (verbatim)

> "I need the content screen pill restored. inside it add 'see more' button that pops up the the details that were in 'auditor' button removed. Do not blindly roll back changes - this is not a roll back. do what i am requesting strictly without affecting current build."

**Interpretation:**

1. Restore the `"Content screened · N"` pill (removed in Stage A commit `1352e0d5`, 2026-06-25) as a live surface below each assistant chat response.
2. INSIDE that pill, add a "See more" button.
3. Clicking "See more" opens a modal showing the same details that the removed header **AUDIT button** (`AuditDialog`) surfaced — chat-level audit trail, Synisense metrics, export ZIP, Trust-Panel cross-link.
4. This is a strict additive amendment, not a Stage A rollback. The rest of Stage A stays in force.

---

## 1. Reconciliation With Canonical Spec §A ("One Synisense marker per turn")

**Stage A canonical statement (2026-06-25):** "The experience reads as the frontier LLM direct, with one clean marker that opens the full audit when asked."

**User amendment (2026-07-02):** The ambient redaction count is valuable enough to warrant its own marker — the count should read without a click. The per-turn badge (`PerMessageSynisenseBadge`) stays as the audit-access marker; the pill returns as the ambient-count marker.

**New two-marker semantic** (both surface BELOW each assistant message):

| Marker | What it shows | Interaction | Data source | Testid |
| :--- | :--- | :--- | :--- | :--- |
| **Pill** (reinstated) | `"Content screened · N"` — ambient count of spans redacted for this turn. | Hover tooltip = `by_type` breakdown (e.g., `email ×3, phone ×2`). Click "See more" → modal. | `m.synisense_stats.spans_redacted` + `m.synisense_stats.by_type` (same fields as pre-removal). Modal fetches `/api/chats/{cid}/audit` + `/api/chats/{cid}/synisense-metrics`. | `chat-synisense-icon` (unchanged from pre-removal) + `chat-synisense-see-more-btn` (new) + `chat-audit-dialog` (new modal). |
| **Badge** (unchanged) | `"N IDENTIFIERS PROTECTED · RESTORED ON YOUR VIEW"` — kicker label. | Click → expand inline audit-panel (`/api/chats/{cid}/audit-panel?message_id=…`) + Privacy-report PDF download. | `runs.identifiers_redacted` + `runs.layer_breakdown` (via `useMessagesSynisense` map). | `chat-msg-synisense-{msgId}` (unchanged). |

**Why both?** They surface different information:

* Pill = **per-message redaction count** (`spans_redacted` from the chat message payload).
* Badge = **per-message layer-broken breakdown** (`layer_breakdown` from the `useMessagesSynisense` aggregation).

The pill's "See more" button navigates to the **chat-level audit trail** (whole-conversation rows + metrics + export + Trust-Panel link). The badge's expander navigates to the **per-turn audit panel** (this single message's shielding_prose + scores + audit_id).

**Canonical spec §A is hereby amended** to acknowledge this two-marker pattern under user's 2026-07-02 direction. §A's original "one clean marker" language is preserved as historical context; the amendment adds: *"Amended 2026-07-02 — pill + badge coexist. Two markers per assistant turn is the current state, permitting ambient count read (pill) alongside per-turn audit access (badge)."*

---

## 2. What Stage A Changes Are Preserved vs. Amended

| Stage A change | Status after this amendment | Rationale |
| :--- | :--- | :--- |
| Title-adjacent `SynisenseInlineBadge` removed | **PRESERVED** (still removed) | Title-adjacent placement was the redundant one (badge and pill were showing the same signal at different positions). |
| Per-message `"Content screened · N"` pill removed | **AMENDED — REINSTATED** | User direction 2026-07-02. |
| Header AUDIT button + `AuditDialog` mount removed | **PARTIALLY AMENDED** — content re-surfaced via pill's "See more" modal (not the header button). | User asked for the *content* to return, not the header button. The pill → See more → modal path is the new access route. |
| Floating `<AggregateStrip>` banner + component file deleted | **PRESERVED** (still deleted) | Non-scope of this dispatch. Component file remains deleted. |
| Shared `AuditPanel` hidden on chat surface | **PRESERVED** (still hidden on chat) | Non-scope of this dispatch. `AuditPanel` remains an S0-R4 hide, not a delete. Solva surfaces still mount it. |
| `PerMessageSynisenseBadge` rewritten (~280 LOC) | **PRESERVED** (byte-identical to pre-fix) | User's "do not affect current build" instruction. Badge continues to expand to per-turn audit + Privacy report. |
| `formatSyniBreakdown` helper retained | **PRESERVED** (now finds a second caller in the reinstated pill) | Helper was kept during Stage A for potential reuse; pill uses it verbatim. |

---

## 3. Implementation Summary

### 3.1 New component — `/app/frontend/src/components/chat/ShieldedContentPill.jsx`

Self-contained. Renders nothing when `m.synisense_stats?.spans_redacted <= 0`. Otherwise renders:

* The pill: `<div data-testid="chat-synisense-icon">` wrapping a `<button>` with `FileLock2` icon + `"Content screened · N"` label + `title`/`aria-label` mirroring the pre-removal JSX verbatim.
* A trailing `"See more"` button inside the pill container: `<button data-testid="chat-synisense-see-more-btn">`.
* On click → `ChatAuditDialog` modal opens (also inside the same file).

The `ChatAuditDialog` reimplements the removed `AuditDialog` from `Chat.jsx:2284` (pre-removal). Content parity:

* Fetches `/api/chats/{cid}/audit` (rows) — `chat-audit-rows` data-testid preserved.
* Fetches `/api/chats/{cid}/synisense-metrics` (identifiers_redacted, model_calls, storyline) — `chat-audit-synisense-metrics` preserved.
* Export button hits `/api/chats/{cid}/audit/export.zip` — `chat-audit-export-btn` preserved.
* Trust-Panel cross-link via `akki:open-trust-panel` event — `chat-audit-trust-panel-link` preserved.
* Modal root `data-testid="chat-audit-dialog"` preserved.
* 404-friendly copy: `"Audit data isn't available yet — refresh once it has settled."`

**Component size:** ~180 LOC. Uses `@/components/ui/dialog` (Dialog / DialogContent / DialogHeader / DialogTitle / DialogDescription) — already available. Uses `@/lib/api/apiV2` (`api.get`) — already available. Imports `Download` from `lucide-react` (new import at the pill component level; Chat.jsx unaffected).

### 3.2 Chat.jsx MOD

Single search_replace replacing the Stage A comment block at lines 1857-1866 (the "class chip removed" + "AuditPanel auto-mount removed" comments) with:

```jsx
{/* JC-CHAT Stage A amendment (2026-07-02) — "Content screened · N" pill
    reinstated with a new "See more" affordance that opens a modal
    replicating the removed header AUDIT button's content. See
    /app/memory/sprints/JC_CHAT_STAGE_A_AMENDMENT.md. */}
<ShieldedContentPill m={m} chatId={chatId} />
```

Plus one new import at Chat.jsx top: `import ShieldedContentPill from "@/components/chat/ShieldedContentPill";`. Zero other Chat.jsx lines touched. `PerMessageSynisenseBadge` render at line 1757 preserved verbatim.

### 3.3 What is NOT touched

* `PerMessageSynisenseBadge.jsx` — untouched.
* `AuditPanel.jsx` — untouched.
* `AggregateStrip.jsx` — remains deleted.
* Backend routers — untouched.
* Backend tests — untouched.
* Any non-chat surface (Solva, Work Studio, Decks, Pulse, etc.) — untouched.

---

## 4. Standing-Rule Adherence (checked)

Six banked lessons:

1. **Zero-handoff-loss discipline.** ✅ `DEV_PIPELINE.md §9` row landed BEFORE this memo authoring.
2. **Canonical Spec on line 1.** ✅ `JC_CHAT_CANONICAL_SPEC.md §A` + user amendment 2026-07-02 cite on line 1.
3. **Additive not rollback.** ✅ No `git revert`. One new component + one Chat.jsx search_replace. All other Stage A changes preserved.
4. **F.6 Shield-contract discipline-pay.** ✅ Backend contract untouched; `test_synisense_security.py` + `test_synisense_shield.py` + `test_synisense_surface_validation.py` all unchanged. Verified GREEN post-mod.
5. **UNQUARANTINED runtime baseline.** ✅ Pre-fix baseline captured at `2026-07-02T16:15:36Z` (Chat.jsx sha `3d014087cd1de76a`).
6. **JC-CHAT invariants suite.** ✅ `test_invariant_chat_streaming_reidentify_present.py`, `test_invariant_shield_no_leak.py`, `test_invariant_audit_always.py` etc. unchanged and GREEN.

Pollution ceilings (M1 / M2):

* Chat.jsx: −0 LOC / +1 LOC (import added) / +5 LOC (comment + component mount) = net +6 LOC.
* New `ShieldedContentPill.jsx` file: +180 LOC (new component; doesn't affect existing files' pollution ceiling).
* `PerMessageSynisenseBadge.jsx`: 0 LOC delta.
* Chat surface Synisense marker count: 1 (badge) → 2 (badge + pill). Amended per §1.

M1 stays at 0. M2 stays at 1 (final). New component is a clean encapsulation and does not count against Chat.jsx pollution.

---

## 5. Proving Slice

Path: `/app/backend/scripts/jc_chat_stage_a_amendment_proving_slice.py`. 8 rows:

| Row | Assert | Method |
| ---: | :--- | :--- |
| 1 | Chat.jsx contains `ShieldedContentPill` mount AND `PerMessageSynisenseBadge` mount. | grep in `frontend/src/pages/Chat.jsx`. |
| 2 | New pill component exists at `frontend/src/components/chat/ShieldedContentPill.jsx` with `chat-synisense-icon` + `chat-synisense-see-more-btn` + `chat-audit-dialog` testids. | file exists + grep for the three testids. |
| 3 | Modal fetches parity — component references `/chats/${chatId}/audit`, `/chats/${chatId}/synisense-metrics`, `/chats/${chatId}/audit/export.zip`, and `akki:open-trust-panel` event. | grep. |
| 4 | `PerMessageSynisenseBadge.jsx` unchanged since pre-fix (byte-identical). | sha256 comparison. |
| 5 | `AggregateStrip.jsx` absent (Stage A regression preservation). | file existence check. |
| 6 | JC-CHAT invariant suite GREEN post-mod. | `pytest backend/tests/invariants -q` filter for JC-CHAT rows. |
| 7 | F.6 Shield-contract discipline-pay GREEN. | `pytest backend/tests/test_synisense_security.py backend/tests/test_synisense_shield.py backend/tests/test_synisense_surface_validation.py -q`. |
| 8 | Pollution ceilings — Chat.jsx net LOC delta ≤ +10; ShieldedContentPill.jsx new file only; PerMessageSynisenseBadge.jsx byte-identical; AggregateStrip.jsx absent. | file stat + LOC diff. |

---

## 6. Escalation Triggers

* **Blocked → surface, do NOT auto-handle:**
    * AuditPanel render logic reuse infeasible → NOT hit. Chose to NOT reuse `AuditPanel` (it's per-message; the See more modal is chat-level; different content surfaces entirely). New `ChatAuditDialog` inside the pill component fills the chat-level need directly.
    * Backend endpoint change required → NOT hit. All modal endpoints (`/chats/{cid}/audit`, `/chats/{cid}/synisense-metrics`, `/chats/{cid}/audit/export.zip`) are live and unchanged.
    * Pill + badge visual conflict → surfaced in §1 above. Verdict: pill sits at `mt-2` after message body; badge sits on the meta row (line 1749). Vertical separation makes double-marker density acceptable. If UX regression flagged, HARD STOP + surface for design review.
    * Test regression → NOT hit. Slice + existing invariants + F.6 all GREEN post-mod.

---

## 7. HARD STOP

Amendment shipped per user's strict scope. Slice 8/8 GREEN. Zero regression on existing Chat surfaces. Zero backend contract change. Amendment memo, §9 row, and proving slice all live. **Awaiting user acceptance before closing the dispatch.**

Two upstream open items (not touched by this dispatch, per user instruction):

* Task 1 deck audit sizing path (A / B / C) — still awaits user direction.
* Task 2 Solva/ThinkLab planning-memo rescission (5 lines, ~1h) — still awaits user direction.
