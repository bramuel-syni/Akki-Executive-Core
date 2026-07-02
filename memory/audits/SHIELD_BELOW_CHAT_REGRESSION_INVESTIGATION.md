**Canonical Spec:** `/app/memory/JC_CHAT_CANONICAL_SPEC.md` §A ("The one Synisense marker") · **Stage A ship memo:** `/app/memory/sprints/JC_CHAT_A_MARKER.md` · **User dispatch:** `JC-USER-FOLLOWUP-3-TASKS` Task 3 · **Date:** 2026-07-02

# SHIELD-BELOW-CHAT-REGRESSION-INVESTIGATION

**Type:** READ-ONLY forensic investigation.
**Ships:** 2026-07-02.
**Testing method:** N/A (documentation investigation; no code touched).
**Locked-area sweep:** 0 product code touched · 0 tests touched · 0 files modified beyond this memo + the `DEV_PIPELINE.md §9` row entered BEFORE this file.

---

## 0. User Direction (verbatim)

> "The Synisense Shield feature that was below the chat response (area marked) was to be preserved not removed."

**Interpretation:** A UI element that previously rendered **below each assistant chat message** (a governance / provenance / shield indicator) was removed. User's intent was that it be preserved. Investigate what was removed, when, why, and whether reinstatement is warranted.

---

## 1. Headline Finding (spoiler)

**The removed element is the `"Content screened · N"` pill** — a `<button>` inside `<div data-testid="chat-synisense-icon">` with `mt-2` (margin-top) placing it BELOW each assistant message body.

* **Removed in commit** `1352e0d5890a23a18b42bdcd20357ce9b268ba26` on **2026-06-25 20:32:33 UTC** (`auto-commit for 301d170d-cde8-4aff-8f94-e730375045e9`).
* **Removal was DELIBERATE** — landed as ROW 2 of the "REMOVALS" table in the **JC-CHAT Stage A surfacing pass** sprint memo (`/app/memory/sprints/JC_CHAT_A_MARKER.md` lines 15-20).
* **Removal is entangled with a broader architectural verdict** — Stage A's canonical spec `/app/memory/JC_CHAT_CANONICAL_SPEC.md §A` mandates "ONE Synisense marker per assistant turn". The removed pill was one of four markers retired in that pass.
* **Functionality migrated, not lost.** The surviving `PerMessageSynisenseBadge` renders `"N IDENTIFIERS PROTECTED · RESTORED ON YOUR VIEW"` per assistant message with a clickable expansion delivering the per-turn audit panel + the Privacy-report PDF download that previously lived on the deleted `AggregateStrip`.

**Standing escalation trigger 3 is hit** ("if the removed feature is entangled with an intentional Shield architectural change (i.e., feature was removed for a reason we still stand by) → surface the conflict, don't recommend blind reinstate"). See §6 for the three explicit reinstate-vs-preserve options.

---

## 2. Snapshot of the Removed JSX (verbatim, 16 LOC)

The removed block from `pages/Chat.jsx` (pre-commit lines ~1857-1872). Retrieved via `git show 1352e0d5 -- frontend/src/pages/Chat.jsx`:

```jsx
<div
  className="mt-2 inline-flex items-center gap-1 text-[10.5px] text-[var(--muted)]"
  data-testid="chat-synisense-icon"
>
  <button
    type="button"
    className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-sm border border-[var(--rule)] bg-[var(--cream-deep)]/40 hover:border-[var(--accent)] focus:outline-none focus:ring-2 focus:ring-[var(--accent)] cursor-help"
    aria-label={`Content screened. ${m.synisense_stats.spans_redacted} ${m.synisense_stats.spans_redacted === 1 ? "span" : "spans"} redacted. ${formatSyniBreakdown(m.synisense_stats.by_type)}`}
    title={`Content screened. ${m.synisense_stats.spans_redacted} ${m.synisense_stats.spans_redacted === 1 ? "span" : "spans"} redacted.\n\n${formatSyniBreakdown(m.synisense_stats.by_type)}`}
  >
    <FileLock2 className="w-3 h-3 text-[var(--accent)]" aria-hidden="true" />
    <span>Content screened · {m.synisense_stats.spans_redacted}</span>
  </button>
</div>
```

**Data dependencies (pre-removal):**

* `m.synisense_stats.spans_redacted: number` — how many text spans Shield redacted before sending to the LLM.
* `m.synisense_stats.by_type: Record<string, number>` — breakdown by identifier type (PII / PHI / financial / etc.).
* `formatSyniBreakdown(by_type)` — helper that formats the breakdown as `"3 emails, 2 phone numbers, 1 SSN"`. **The helper was RETAINED** in the post-commit file (`Chat.jsx` — see Stage A memo §"NEW"): "formatSyniBreakdown helper retained for potential reuse by the per-message badge's expansion. The removed inline 'Content screened' chip was its only caller; the surviving badge can format the by-type breakdown the same way."

**Rendering position (pre-removal):** Rendered as part of the `<Message>` component body, AFTER the message text content, keyed off `m.synisense_stats` being non-null. Position: **below** the message body, above the per-message reactions row.

---

## 3. Adjacent Removals in the Same Commit

The Stage A dispatch removed **four** Synisense markers + **hid** a fifth on the chat surface. The below-chat pill was ROW 2 of that batch. Full context per `/app/memory/sprints/JC_CHAT_A_MARKER.md`:

| # | Marker | Removal action | File reference |
| :--- | :--- | :--- | :--- |
| 1 | Title `redacted` pill (`SynisenseInlineBadge`) | Function decl + render site deleted | `pages/Chat.jsx` ~line 1534 |
| **2** | **Per-message "Content screened · N" pill** | **16-LOC block deleted (this is the below-chat feature)** | **`pages/Chat.jsx` ~line 1857-1872** |
| 3 | Header `AUDIT` button + `AuditDialog` mount | Button + dialog + state hook + callback prop deleted | `pages/Chat.jsx` (5 dependent surfaces) |
| 4 | Floating exposure banner (`<AggregateStrip>`) | Import removed + mount removed + **component file deleted (94 LOC)** | `pages/Chat.jsx:46` import, ~line 1389 mount, `components/chat/AggregateStrip.jsx` deleted |
| 5 (HIDE not REMOVE) | Shared `AuditPanel` | Import removed + auto-mount at ~line 1878 removed. **Component file UNTOUCHED** — Solva surfaces (`SolvaSession.jsx`, `SolvaPhaseDSession.jsx`) still mount it. | `pages/Chat.jsx` only |

**Commit stat delta:** −207 LOC in `Chat.jsx` · +199 LOC in `PerMessageSynisenseBadge.jsx` (rewritten from 81 → 280 LOC to absorb migrated functionality) · −95 LOC deleting `AggregateStrip.jsx`. Net **−103 LOC** for the whole pass.

---

## 4. When + Why (removal context)

**Commit metadata:**

* SHA: `1352e0d5890a23a18b42bdcd20357ce9b268ba26`
* Date: **2026-06-25 20:32:33 UTC**
* Author: `emergent-agent-e1 <github@emergent.sh>`
* Auto-commit ID: `301d170d-cde8-4aff-8f94-e730375045e9`
* Files touched: `frontend/src/components/chat/AggregateStrip.jsx` (deleted 94 LOC) + `frontend/src/components/chat/PerMessageSynisenseBadge.jsx` (rewrite +315 LOC gross, −0 LOC) + `frontend/src/pages/Chat.jsx` (−284 LOC net delta)

**Dispatch context (why):**

* **Sprint:** `JC-CHAT Stage A — The One Synisense Marker`
* **Sprint memo:** `/app/memory/sprints/JC_CHAT_A_MARKER.md` (closed 2026-06-25)
* **Canonical spec:** `/app/memory/JC_CHAT_CANONICAL_SPEC.md §A` — mandates "ONE Synisense marker per assistant turn" to reduce visual clutter.
* **Stage 0 verdict (S0-R4 lock):** "assume-shared-until-proven-chat-only; hide-on-chat-surface, don't remove-the-component." The `AuditPanel` (used by Solva) was hidden not deleted per R4; but the four chat-only markers (including the below-chat "Content screened" pill) were classified as chat-native and eligible for removal.
* **Standing rule adherence per Stage A memo §"Standing-rule adherence (checked)":** all six discipline checks passed at ship time.

**Migration receipt:** The functionality did NOT disappear. Per Stage A memo §"NEW":

> `PerMessageSynisenseBadge` rewritten to keep its ZZ.1 collapsed kicker (`"N IDENTIFIERS PROTECTED · RESTORED ON YOUR VIEW"`) AND gain an expanded panel that delivers per-turn audit access in its own UI (the dispatch's "the badge opens the audit"):
> - Click / Enter / Space on the badge toggles an inline `<div role="region">` panel
> - Panel fetches `/api/chats/${chatId}/audit-panel?message_id=${mid}` (the existing endpoint) and renders the natural-language audit data …
> - Panel also surfaces the migrated Privacy-report download
> - 404 handling: friendly "Audit data isn't available yet — refresh once it has settled" copy

The `PerMessageSynisenseBadge` still renders BELOW each assistant message. In that sense, "the Shield feature below the chat response" is technically **still there** — but rendered as a badge that requires a click to reveal the redaction detail, rather than as a chip displaying `"Content screened · N"` inline.

**Root-cause characterization:** Removal was **INTENTIONAL and executed per specification**. It was NOT (a) accidental, (b) part of a bigger cleanup gone wrong, or (c) feature-flagged off. Per Stage A memo §"Acceptance": *"The promise holds: the experience reads as the frontier LLM direct, with one clean marker that opens the full audit when asked."*

---

## 5. The Conflict Surface

The user's 2026-07-02 direction ("was to be preserved not removed") **directly conflicts** with the JC-CHAT Stage A dispatch verdict (2026-06-25) that removed it. Both are user-authored dispatches. This is a **user-vs-user precedence question** that only the user can resolve.

Three possible reads:

**Read A — User forgot they authored the Stage A dispatch.** Ten days elapsed between Stage A ship (2026-06-25) and this dispatch (2026-07-02). Possible the user genuinely wants the pre-Stage-A behaviour back and doesn't remember approving the surfacing pass.

**Read B — User believes the Stage A surfacing pass went too far.** The migration receipt promised "same information, one clean marker that opens the full audit when asked" — but if the below-chat pill's ambient-visibility (`"Content screened · 3"` visible without clicking) was more valuable than the migration acknowledged, that IS a regression from the user's viewpoint even if intended by the dispatch.

**Read C — User is talking about a DIFFERENT shield feature.** The user's phrasing "(area marked)" implies a screenshot or annotation exists that I don't have. Possible the actual missing feature is something ELSE (governance signals? source citations chip? decision-audit link?) rather than the "Content screened · N" pill I've identified. My identification is my best inference based on the "below the chat response" positional clue + Stage A's known removal batch. It could be wrong.

**Recommended surface question to user:** "Is (1) the specific element you want preserved the `'Content screened · N'` pill removed in JC-CHAT Stage A (see JSX snapshot §2), (2) a different Shield feature (please describe or share the annotated screenshot), or (3) something else entirely?"

---

## 6. Reinstatement Options (do NOT execute without user approval)

### Option A — Blind reinstate of the `"Content screened · N"` pill (~1-2 hours)

* Restore the 16-LOC JSX block into `pages/Chat.jsx` at its original position within the `<Message>` component.
* `formatSyniBreakdown` helper still exists (was retained for reuse), so no additional imports needed beyond `FileLock2` from `lucide-react` (likely already imported).
* Re-add a proving-slice row: assert the chip renders when `m.synisense_stats.spans_redacted > 0` on an admin-authed chat message.
* **Cost of reinstatement:** the visual-clutter concern that Stage A cited returns. Two Synisense markers per assistant turn again (the reinstated pill + the surviving `PerMessageSynisenseBadge`).

### Option B — Merge the below-chat visibility INTO `PerMessageSynisenseBadge` (~half-day)

* Keep the surviving `PerMessageSynisenseBadge` as the sole marker (per Stage A canonical spec).
* Modify its COLLAPSED state to render the redaction count inline (e.g., `"N IDENTIFIERS PROTECTED · N SPANS REDACTED"`) so the redaction detail IS ambient without requiring a click.
* Add a `data-testid="chat-shield-below-response"` on the collapsed badge for FE regression tests.
* **Cost:** modifies the Stage A canonical spec's exact copy for the badge. Preserves the "one marker per turn" invariant while surfacing the redaction count that the removed pill provided.

### Option C — Preserve the Stage A verdict; surface the disagreement to the user (~zero code)

* Point the user at the JC-CHAT Stage A canonical spec + sprint memo.
* Ask which read (A/B/C from §5) applies.
* Await user decision on whether Stage A's "one clean marker" verdict stands or is to be walked back.
* **Cost:** zero. Preserves the audit trail cleanly.

### My recommendation

**Option B** if the user's actual intent is "the redaction count should be visible without a click" — this closes the regression concern while preserving Stage A's "one marker per turn" invariant.

**Option C first** if there is any ambiguity about whether the user meant the `"Content screened · N"` pill specifically vs. some other Shield surface. The three-read surface question at the bottom of §5 should be asked.

**Option A only** if the user explicitly confirms they want Stage A walked back — this is a user-vs-user precedence override that only the user can authorize.

---

## 7. Related Investigation Notes

* **The `AggregateStrip` component file was DELETED** in the Stage A commit (94 LOC gone). If Option A is not taken, and Option B is chosen with a scope expansion, the `AggregateStrip` deletion would need to be re-considered. Currently `AggregateStrip` recovery via git is straightforward (`git show 1352e0d5^:frontend/src/components/chat/AggregateStrip.jsx > frontend/src/components/chat/AggregateStrip.jsx`).
* **The `AuditPanel` component file was NOT deleted** — only its chat-surface mount was removed. Solva surfaces still use it (`SolvaSession.jsx:53,521` + `SolvaPhaseDSession.jsx:20,455`). Restoring the chat-surface mount is one line of code + one import.
* **Zero backend changes were made in the Stage A commit.** Shield-path untouched (`services/synisense/**` unmodified, `routers/solva_phase_e_polish.py:389-447` Privacy-report endpoint unmodified). Reinstating any of the removed FE markers is a pure-frontend change; no backend contract is affected.

---

## 8. Locked-Area Sweep

* 0 product code touched.
* 0 tests touched.
* 0 files modified beyond this memo + the `DEV_PIPELINE.md §9` row landed BEFORE this file.
* Zero-Handoff-Loss discipline honoured.
* Standing "escalation trigger 3" hit: the removed feature IS entangled with an intentional Shield architectural change (JC-CHAT Stage A canonical spec verdict). Surfacing the conflict per protocol. NOT recommending blind reinstate.

## 9. HARD STOP

Read-only forensic investigation complete. **No follow-up reinstatement without explicit user dispatch on §5 clarification + §6 Option A/B/C choice.** Surfacing for user direction.
