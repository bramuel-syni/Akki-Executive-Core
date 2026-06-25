# JC-CHAT — Experience & Completion Pass · Canonical Specification

> **Source:** User dispatch — 2026-06-25
> **Status:** ACTIVE
> **Supersedes:** Any prior Chat brief in handoffs / runway docs / sprint memos.
>
> **Handoff-durability contract.** This file + DEV_PIPELINE.md §2 + the
> most recent JC-CHAT sprint memo together MUST be sufficient to resume
> the build without re-asking the user any locked decision. Every
> JC-CHAT sprint memo MUST cite this file on line 1 as "Source of truth".

---

## Framing

Chat is the most complete surface in the platform — multi-model,
Shield-routed, grounded, audited, visibly working end-to-end. This is
**NOT a build phase**. It is an **EXPERIENCE pass plus a small
completion punch-list**. Do not rebuild, do not re-architect, do not
add scope.

**The promise to protect:** *everything you'd get from the frontier
model directly — smoothness, fluency, formatting, responsiveness — you
get here, just safely. Shielding stays invisible to the experience and
visible only when the user asks to see it.*

**GUIDING TEST** (apply to every change): *would this make Chat feel
less like talking to the frontier model directly? If yes, don't do it.*
Safety is the floor; it must not tax the experience.

---

## Part 0 — Standing rules

- Reuse and refine only. **No new engines, no new architecture.**
- **The Shield path is OUT OF BOUNDS for changes in this pass.** Every
  LLM call stays Shield-routed; audit, fail-closed, reidentification,
  grounding, tenancy — all unchanged. You may MEASURE the Shield path;
  you may not modify it. Any experience fix that would require
  touching reidentification, audit-write, or the routing path is a
  **STOP** — report it, don't do it.
- Classify by execution before touching anything. Static-read findings
  — confirm each at runtime before building, removing, or closing.
- "Done" = the experience demonstrated in a real conversation, shown
  — not a green test.
- Escalate only a genuine STOP or a real fork. Else it's yours.

## Discipline locks (registered from user reframings)

### R4 lock — assume-shared-until-proven-chat-only

Removing a shared audit component because it clutters chat is how you
silently break Monitor's or Work Studio's audit views. **Default is
assume-shared-until-proven-chat-only.** If a component is shared, the
change is **hide-on-chat-surface, never remove-the-component.**
**Default, not fallback.**

### F1 lock — Privacy-report scope check (additive-only-if-narrowing)

If the existing Privacy-report export is global-across-conversations
today, relocating it into the per-conversation audit panel narrows
scope — that's a **capability regression dressed as a tidy-up**.
Confirm scope first. If global today, the panel export is **ADDITIVE**
(adds per-conversation access); the global export **stays reachable**.

### R5 lock — Edit-prompt: report-verbatim-let-user-decide

For the edit-prompt punch-list item: **report the code comment
VERBATIM + file:line + surrounding logic context**. The user decides
intent, not the agent. Do not build until intent is decided.

---

## Stage 0 — GATE: Classify-before-remove (R4 / F1 / F2)

The A removals depend on these classifications. **STOP-and-surface
before A starts.**

### S0-R4 — Shared-component inventory

For each of the 4 markers proposed for removal:
- title `redacted` pill
- standalone class chip
- separate header `AUDIT` button
- floating exposure banner

Codebase inventory: which files import/render this component? Is it
used anywhere outside chat (Monitor audit views, Work Studio document
audit panels, AnalyzeDrawer, anywhere)?

- If chat-only → **REMOVE** from the page is the action.
- If shared → **HIDE-ON-CHAT-SURFACE**. Do NOT remove the component
  itself. **The default is hide-on-chat; removal requires explicit
  proof-of-chat-only.**

Output: `/app/memory/audit/JC_CHAT_marker_inventory.md` —
per-marker table (component file, import sites, render sites, verdict:
REMOVE / HIDE-ON-CHAT-SURFACE + reasoning).

### S0-F1 — Privacy-report scope check

Is the existing Privacy-report export global-across-conversations or
per-conversation today? Read the export endpoint + the call site that
triggers it; classify.

- If per-conversation today → relocation into audit panel is a clean
  move (same scope, different surface).
- If global today → the panel export is **ADDITIVE** (adds
  per-conversation access). The global export **STAYS REACHABLE** —
  do not narrow scope as a side-effect.

Output: scope verdict in the marker inventory memo + locked decision
on the relocation shape.

### S0-F2 — Accessibility hooks on the AUDIT button

Read the header `AUDIT` button component. Does it carry a keyboard
shortcut, ARIA hook, or accessibility binding that would break if the
button is removed/hidden? If yes, preserve the binding on the
surviving marker (the per-message badge).

Output: one-line a11y verdict in the marker inventory memo.

---

## A — The one Synisense marker (executes the classified removals)

Today ~5 redundant markers restate "stuff got shielded":
- title `redacted` pill
- green exposure banner + Privacy-report button
- per-message class chip
- `Synisense audit` expander
- header `AUDIT` button

**RETAIN EXACTLY ONE:** the **PER-MESSAGE shield badge**
(`PerMessageSynisenseBadge`) — two words until expanded, sits on the
turn it describes, opens that turn's full audit.

Surfacing changes only — the underlying shield/audit DATA and
capability are untouched:

- For the four markers proposed for removal: action per S0-R4 verdict
  (REMOVE if chat-only; HIDE-ON-CHAT-SURFACE if shared).
- The badge opens the audit (identified + masked + class-based
  rendering like `[PAYMENT_CARD_••••7689]` + trust receipt).
- **SMALL BUILD** (name it as such): relocate the exposure stats and
  the Privacy-report export INTO the audit panel per S0-F1 verdict
  (additive if currently global; clean move if currently
  per-conversation). This is a UI move, not a Shield change — the
  data already exists.
- Preserve a11y binding from S0-F2 on the surviving marker.

**KEEP DISTINCT:** Auto-shield is a CONTROL (sets shielding mode), not
a status marker — leave it.

---

## B — LLM experience parity (R1+R2+R3 methodology block)

Verify by real use that the shielded path delivers a native
frontier-LLM experience. The measurement methodology is part of B,
not a separate sidebar — surface the measurements as evidence, not
assertions. Fix only what can be fixed in the FRONTEND/presentation
layer. Anything that would require changing the Shield path is a
**STOP**, reported with the measurement — not actioned.

### R1 — Trace-and-classify rule (frontend-fixable vs Shield-path)

For each parity finding (formatting, follow-up fluency,
model-switching), trace the response payload from **Shield exit →
frontend render**.
- If Shield exit is correctly formatted but the frontend mangles it
  → **frontend-fixable** (in scope).
- If Shield exit is already mangled → **Shield-path finding**
  (STOP-and-report, do not modify Shield path).

The trace is the evidence; the verdict is reproducible.

### R2 — Streaming method

Determine whether responses stream token-by-token or buffer-then-dump
using one of:
- timestamped first-byte vs last-byte log, OR
- DevTools Network panel evidence showing SSE/chunk arrival pattern.

Report the method used + the evidence. *"Streams" / "buffers" claims
without one of these is not acceptable.*

### R3 — Latency baseline + decomposition

Measure time-to-first-token (TTFT) and time-to-completion (TTC) at 3
prompt sizes:
- **SHORT** (1-2 sentences)
- **MEDIUM** (1 paragraph + a context doc reference)
- **LONG** (multi-paragraph + 2 context docs + entity-rich PII payload)

For each prompt size, decompose the latency across the 6 stages:
1. network
2. backend handler
3. Shield prep
4. provider call
5. Shield post
6. frontend render

Report the numbers as a table. *That makes the "where's the cost"
question answerable, not just "it's slow / fast."*

### Specific findings to measure and report

- **STREAMING:** per R2 method. If buffering originates in the Shield
  path → STOP-and-report (per R1).
- **LATENCY:** per R3 method. Do not move reidentification or
  audit-write off the path in this pass — if that's where the cost
  is, that's a flagged finding for a separate, safety-reviewed
  decision.
- **FORMATTING FIDELITY:** confirm headings, bullets, bold, italics,
  code, tables render fully (MarkdownMessage). Classify each issue
  per R1.
- **FOLLOW-UP FLUENCY:** confirm multi-turn context, grounding
  (context_id + attached docs), and reidentified entities carry
  across turns and read naturally. Classify each gap per R1.
- **MODEL SWITCHING:** confirm mid-conversation switching is smooth
  and the current model is always clear. Classify per R1.

### Deliverable for B

A parity report — what's native already, what's frontend-fixable (and
fixed, with evidence), and what's a Shield-path finding escalated for
separate decision (with evidence).

Output: `/app/memory/audit/JC_CHAT_parity_report.md`.

*The value here is the honest measurement, not silent surgery.*

---

## C — Completion punch-list (verify-then-close; small, additive)

Static read shows these not present — **CONFIRM BY EXECUTION** each
is genuinely absent (may exist under other names), then close the
real gaps. Frontend/CRUD-level, no Shield involvement:

- **RENAME conversation** — close if absent.
- **RESTORE archived** (unarchive) — archive + view-archived +
  search-archived already exist; this is the back half. Close if
  absent.
- **PERMANENTLY DELETE archived** — close if absent.
- **EDIT a submitted prompt** (refine without a new conversation) —
  **R5 lock**: report the code comment VERBATIM + file:line +
  surrounding logic context. **The user decides intent, not the
  agent.** Do not build until intent is decided.

For each item: report the by-execution finding (PRESENT / ABSENT /
DELIBERATELY-SKIPPED with evidence), then close the real ABSENT ones.

---

## Proving slice (show the experience)

Two demonstrations, kept separate so neither presumes the other:

### 1. EXPERIENCE (A + B)

One real conversation:
- start a chat
- attach a document
- ask a question carrying PII → response streams, fully formatted,
  reads naturally with contextual entities rehydrated and hard-PII
  masked
- follow-up
- mid-conversation model switch
- open the single per-message badge to the full audit

*Show it feels like the frontier model direct, with one clean marker.*
Accompany with the B parity report.

### 2. PUNCH-LIST (C)

For each item CONFIRMED present-as-gap, show it closed (rename /
restore / permanent-delete) running real. Edit-prompt: show the
intent decision (from R5 verbatim-report), not a blind build.

---

## Acceptance

Chat feels like the frontier LLM direct — streaming, formatting,
follow-up, smooth model-switching — with shielding invisible in the
flow and surfaced by exactly one per-message marker that opens the
full audit. **Experience parity is MEASURED and reported**, with any
Shield-path cost escalated rather than silently changed. The
conversation-management gaps are verified and closed (or consciously
deferred). Nothing rebuilt, the Shield path untouched, the clutter
gone. *The promise holds: everything you get from the model out
there, here, safely.*

---

## Artefact manifest

**Stage 0 (classify-before-remove):**
- `/app/memory/audit/JC_CHAT_marker_inventory.md`
  (R4 per-marker table + F1 scope verdict + F2 a11y verdict)
- Sprint memo: `/app/memory/sprints/JC_CHAT_STAGE_0_CLASSIFY.md`

**A (single marker execution):**
- `/app/memory/jc_artifacts/JC-CHAT/A-marker/` (before/after
  screenshots — markers removed/hidden + surviving badge + relocated
  Privacy-report + preserved a11y)
- Sprint memo: `/app/memory/sprints/JC_CHAT_A_MARKER.md`

**B (parity report):**
- `/app/memory/audit/JC_CHAT_parity_report.md`
  (R1 trace evidence + R2 streaming method + R3 latency table +
  per-finding verdict: NATIVE / FRONTEND-FIXED / SHIELD-PATH-FLAGGED)
- Sprint memo: `/app/memory/sprints/JC_CHAT_B_PARITY.md`

**C (punch-list):**
- `/app/memory/audit/JC_CHAT_punchlist_verification.md`
- `/app/memory/jc_artifacts/JC-CHAT/C-punchlist/` (closed-item evidence)
- Sprint memo: `/app/memory/sprints/JC_CHAT_C_PUNCHLIST.md`

**Proving slice:**
- `/app/memory/jc_artifacts/JC-CHAT/proving-slice/experience-flow.jpg`
- `/app/memory/jc_artifacts/JC-CHAT/proving-slice/punchlist-closed.jpg`
