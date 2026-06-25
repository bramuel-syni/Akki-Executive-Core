# JC-CHAT Stage A — The One Synisense Marker (executes the classified removals)

> **Source of truth:** `/app/memory/JC_CHAT_CANONICAL_SPEC.md` (§ A — The one Synisense marker).

**Closed 2026-06-25** — Stage A surfacing pass complete. Zero
backend changes; Shield-path UNTOUCHED. Sole surviving Synisense
marker: `PerMessageSynisenseBadge`.

---

## What shipped (executing the Stage 0 verdicts verbatim)

### REMOVALS (4 chat-only markers per S0-R4 verdict)

| # | Marker | Removal action | File reference |
|---|---|---|---|
| 1 | Title `redacted` pill | Removed `SynisenseInlineBadge` function declaration AND its render site beside the chat title | `pages/Chat.jsx` (function deleted; render site at `~line 1534` replaced with comment block) |
| 2 | Per-message "Content screened · N" pill | Removed the 16-line inline JSX block including its `chat-synisense-icon` test-id wrapper | `pages/Chat.jsx` (~line 1857-1872 deleted; replaced with comment block) |
| 3 | Header `AUDIT` button | Removed the `<button data-testid="chat-audit-btn">` block AND the `<AuditDialog>` mount AND the dialog function declaration AND the `auditOpen` / `setAuditOpen` state hook AND the `onAudit` prop on `ChatHeader` (defn + call-site) | `pages/Chat.jsx` (all 5 dependent surfaces) |
| 4 | Floating exposure banner | Removed `<AggregateStrip>` import + mount + **deleted the component file** | `pages/Chat.jsx:46` import removed; `~line 1389` mount removed; `components/chat/AggregateStrip.jsx` deleted (zero remaining imports) |

### HIDE-ON-CHAT-SURFACE (per S0-R4 lock — shared `AuditPanel`)

| # | Marker | Action | Why |
|---|---|---|---|
| 5 | `AuditPanel` shared component | Removed the import + the auto-mount at `~line 1878`. **Component file UNTOUCHED.** | Shared component — imported by `pages/SolvaSession.jsx:53,521` and `pages/SolvaPhaseDSession.jsx:20,455`. Those surfaces continue to mount it (verified by `grep`). The component itself stays defined at `components/chat/AuditPanel.jsx`; chat just no longer renders it. R4 lock satisfied: hide-on-chat-surface, never remove-the-component. |

### RELOCATIONS / MIGRATIONS

| What | From | To |
|---|---|---|
| Privacy-report PDF download (S0-F1: clean move, not narrowing — endpoint is per-conversation today) | `AggregateStrip.jsx:42-62` (deleted) | `PerMessageSynisenseBadge.jsx` expansion panel · button labelled "Privacy report (this conversation) · PDF" · same `/api/chats/${chatId}/privacy-report.pdf` endpoint · same chat scope · byte-identical PDF |
| A11y binding (S0-F2: only `title="View audit log"` to carry) | header AUDIT button (removed) | `PerMessageSynisenseBadge` expand affordance · now carries `title="Open this turn's audit log"` + `aria-label="Identifiers protected: N. Open this turn's audit log."` |

### NEW (the surviving marker gets fuller surface)

`PerMessageSynisenseBadge` rewritten to keep its ZZ.1 collapsed
kicker (`"N IDENTIFIERS PROTECTED · RESTORED ON YOUR VIEW"`) AND
gain an expanded panel that delivers per-turn audit access in its
own UI (the dispatch's "the badge opens the audit"):

- Click / Enter / Space on the badge toggles an inline `<div role="region">` panel
- Panel fetches `/api/chats/${chatId}/audit-panel?message_id=${mid}`
  (the existing endpoint) and renders the natural-language audit
  data (headline prose + up to 4 sections with prose + bulleted items)
  — same data shape `AuditPanel.jsx` reads, rendered here in a
  chat-local condensed view
- Panel also surfaces the migrated Privacy-report download
- 404 handling: friendly "Audit data isn't available yet — refresh
  once it has settled" copy (preserves Chat.jsx:1857-bugfix UX)

The component file is `/app/frontend/src/components/chat/PerMessageSynisenseBadge.jsx`
(~280 LOC after rewrite from the 81-LOC prior version).

---

## Auto-shield CONTROL (kept distinct per dispatch)

The Auto-Shield (i) tooltip in the header — the CONTROL that sets
shielding mode (Auto / Always / Off) — is intentionally **NOT** a
status marker and was **NOT** touched. Stays at its original
position in `ChatHeader`.

---

## Standing-rule adherence (checked)

- **Reuse / refine only — no new engines, no new architecture** ✅
  · zero new backend; zero schema changes; existing endpoints reused
- **Shield path OUT OF BOUNDS for changes** ✅
  · `services/synisense/**` not touched; `routers/solva_phase_e_polish.py:389-447` (Privacy-report endpoint) not touched; chat audit endpoints not touched
- **Classify by execution before touching** ✅
  · Stage 0 done first (`/app/memory/audit/JC_CHAT_marker_inventory.md`); Stage A executes those verdicts only
- **R4 lock: assume-shared-until-proven-chat-only** ✅
  · `AuditPanel` (used by Solva) was HIDE-ON-CHAT-SURFACE, NOT removed; component file untouched; Solva surfaces unaffected
- **F1 lock: privacy-report scope check** ✅
  · Verified per-conversation today; relocation is CLEAN MOVE not narrowing; same scope, different surface
- **F2 lock: a11y binding preserved** ✅
  · `title="View audit log"` migrated as `title="Open this turn's audit log"` + `aria-label` filling the previously missing aria binding

---

## Files touched

| File | Change | Net LOC delta |
|---|---|---|
| `frontend/src/pages/Chat.jsx` | Removed `AuditPanel` + `AggregateStrip` imports; removed `auditOpen` state; removed `SynisenseInlineBadge` function (29 LOC); removed `AuditDialog` function (135 LOC); removed inline "Content screened" pill (16 LOC); removed header AUDIT button (8 LOC); removed `<AggregateStrip>` mount (6 LOC); removed `<AuditDialog>` mount (5 LOC); passed `chatId` + `messageId` props to `PerMessageSynisenseBadge`; cleaned unused `Eye` + `Download` imports | **−207** (2450 → 2243) |
| `frontend/src/components/chat/PerMessageSynisenseBadge.jsx` | Rewritten: keeps ZZ.1 kicker + tooltip; gains expanded panel (per-turn audit data fetch + Privacy-report download); a11y migrations carried | **+199** (81 → 280) |
| `frontend/src/components/chat/AggregateStrip.jsx` | **Deleted** (zero remaining imports) | **−95** |

**Net delta:** −103 LOC. The surfacing pass is honestly subtractive.

---

## Smoke

`grep -nE "AggregateStrip\|AuditDialog\|SynisenseInlineBadge\|setAuditOpen\|auditOpen\|AuditPanel" frontend/src/pages/Chat.jsx`
returns ONLY comment-block references (the JC-CHAT Stage A commit
notes) — no live code references remain. `eslint` on the rewritten
badge: ✅ no issues. FE preview compiles cleanly (sign-in surface
renders without console errors).

Before/after screenshot evidence at
`/app/memory/jc_artifacts/JC-CHAT/A-marker/chat-after-stage-A.jpg`.
A full login-and-conversation walk-through is the user-side QA
step.

---

## What's NOT in this stage

Stage A is a pure surfacing pass. The next stages (per canonical
spec):

- **B — LLM experience parity** (R1 trace + R2 streaming method + R3
  latency table; produce `audit/JC_CHAT_parity_report.md`; measure
  the Shield path, do not modify it)
- **C — Completion punch-list** (rename · restore · permanent-delete
  · edit-prompt R5 verbatim-report)

---

## Acceptance

A user enters a conversation, sees one Synisense marker per
assistant turn (the per-message badge), and clicks it to access
that turn's audit + the per-conversation Privacy-report PDF. The
chat surface is visibly less cluttered (4 markers removed,
1 shared component hidden); the Shield path is untouched; Solva
surfaces continue to mount `AuditPanel` exactly as before. *The
promise holds: the experience reads as the frontier LLM direct,
with one clean marker that opens the full audit when asked.*
