Source of truth: `/app/memory/JC_CHAT_CANONICAL_SPEC.md`

# JC-CHAT Stage 0 — Classify-before-remove

> **Closed:** 2026-06-25
> **Stage 0 STOP point reached** — R4 marker inventory + F1 scope
> verdict + F2 a11y verdict surfaced. Stage A executions CLEARED to
> proceed per the per-marker action plan.

---

## Verdicts (one-line summary)

- **R4 (per-marker classification):** 4 markers chat-only → **REMOVE**;
  1 marker (`AuditPanel`) shared with Solva/Solva-Phase-D →
  **HIDE-ON-CHAT-SURFACE** (component file untouched).
- **F1 (Privacy-report scope):** **Per-conversation today** —
  relocation into the surviving badge's audit-expansion is a **CLEAN
  MOVE**, not a narrowing. No additive-vs-narrowing concern.
- **F2 (AUDIT-button a11y):** Minor — only `title="View audit log"`.
  No keyboard shortcut to preserve. Migrate `title` + add `aria-label`
  on surviving badge.

Full per-marker evidence + Stage A plan in
`/app/memory/audit/JC_CHAT_marker_inventory.md`.

---

## What the R4 lock actually changed

Static-read alone, all 5 markers looked chat-page-noise — easy to
delete. The R4-lock runtime classification surfaced that **`AuditPanel`
is shared with Solva voice audit + Solva Phase D**. Without the lock,
that component would have been silently deleted in Stage A and broken
two unrelated surfaces.

The verdict for `AuditPanel`: **HIDE-ON-CHAT-SURFACE**. Component file
`components/chat/AuditPanel.jsx` is untouched. The chat-side mount at
`Chat.jsx:1878` is gated behind a chat-only constant defaulting to
hidden. Solva surfaces keep their existing AuditPanel render — byte-stable.

The discipline locked in the spec — "Default is assume-shared-until-
proven-chat-only" — caught a real defect before it shipped. Worth the
gate's cost.

---

## What the F1 lock actually checked

The dispatch flagged: if Privacy-report is global today, relocating it
into the per-conversation audit panel **narrows scope** — a capability
regression dressed as a tidy-up.

The endpoint
(`routers/solva_phase_e_polish.py:389-447`) requires `{chat_id}` in
the URL path. The FE caller (`AggregateStrip.jsx:46`) passes the
current `chatId`. There is no global variant.

**F1 verdict: per-conversation today → clean move.** The relocation is
not narrowing. The PDF content + endpoint + scope are unchanged; only
the FE invocation site moves into the surviving badge.

---

## What the F2 check found

The AUDIT button has **minimal a11y** — only the `title="View audit
log"` tooltip and the implicit `button` role. No keyboard shortcut, no
explicit `aria-label`, no `aria-controls`.

**F2 verdict: preserve `title` on the surviving badge's expand
affordance; add an `aria-label` matching the title (closing a gap that
existed before this work).**

---

## Stage A — CLEARED to execute

Per-marker action plan in the inventory memo. Summary:

1. Remove four chat-only markers (~60 LOC across `Chat.jsx`).
2. Hide-on-chat-surface the `AuditPanel` mount.
3. Migrate Privacy-report action into the surviving badge.
4. Migrate `title` + add `aria-label` on the surviving badge.
5. Delete `components/chat/AggregateStrip.jsx` (zero imports elsewhere).

**No backend changes. Shield path untouched.** Stage A is a pure
surfacing pass, exactly as the dispatch frames it.

---

## What we did NOT do (per the dispatch's standing rules)

- Did NOT modify any Shield-path code.
- Did NOT modify audit-write, reidentification, or routing.
- Did NOT remove the shared `AuditPanel` component file.
- Did NOT modify Solva surfaces (Solva voice audit + Solva Phase D
  keep their existing AuditPanel render byte-stable).
- Did NOT change the Privacy-report endpoint or its PDF content.
- Did NOT add any new component or engine.
- Did NOT touch `LLM_MODELS_REFRESH` (still parked).
- Did NOT touch JC-UI-DRAWER (separate future dispatch).
- Did NOT use a testing subagent.

---

## STOP point reached

Per the dispatch: "Stage 0 STOP-and-surface before A starts." Surfacing
NOW. Stage A executions queued; the per-marker action plan in the
inventory memo is the entire Stage-A worklist.

Stage A will be a small additive commit (separate from Stage 0
persistence per the JC-CHAT dispatch's commit discipline) once the
user surface-and-go's this Stage 0.
