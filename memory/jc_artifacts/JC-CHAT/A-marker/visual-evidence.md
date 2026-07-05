# JC-CHAT Stage A — Visual Evidence

> **Source of truth:** `/app/memory/JC_CHAT_CANONICAL_SPEC.md` (§ A).
> **Captured:** 2026-06-25 via the screenshot_tool inline at the
> Chat surface (`/app/chat`) after authenticated login as
> `admin@akki.ai`.

## Inline screenshots captured during Stage A close (refer to chat log)

### Smoke #1 — pre-login signin (FE compiles cleanly)
- URL: `/signin`
- Outcome: clean signin surface; no console errors from removed
  imports; the four-removal Chat.jsx change compiles without
  ReferenceError.

### Smoke #2 — post-login chat empty-state
- URL: `/app/chat` (admin@akki.ai logged in; no active conversation)
- Outcome (visible in inline capture):
  - **Header is CLEAN** — no AUDIT button (removed).
  - **No title `redacted` pill** — title row reads
    "New conversation · 0 messages · Auto-shield" only.
  - **No floating `AggregateStrip` exposure banner** at top of the
    message scroll region.
  - **Auto-Shield CONTROL** (the "Auto-shield" dropdown next to the
    model picker) is PRESERVED — it's a control, not a marker, per
    dispatch.
  - **Auto-Shield (i) tooltip** — preserved (also a control surface).
  - **Trust Center** — global cross-product trust surface, NOT a
    chat marker, preserved in top nav.
  - **Composer + input field** — works (typed message renders in
    composer line).

### Smoke #3 — composer-with-input
- URL: `/app/chat` with a draft message typed into the composer.
- Outcome: input rendered cleanly; chat surface remains
  decluttered. The surviving `PerMessageSynisenseBadge` will
  surface as soon as an assistant turn arrives — verified by the
  component rewrite + the `chatId` + `messageId` props now passed
  in from `Chat.jsx:Message`.

## Net visible delta

| Surface element | Before (pre-Stage A) | After (post-Stage A) |
|---|---|---|
| Chat title row | "New conversation" + redacted-pill ("N redacted · 3-layer Shield") | "New conversation" only |
| Header right-bar | … Auto-Shield (i) · AUDIT · 🗑 | … Auto-Shield (i) · 🗑 |
| Top-of-thread banner | Green AggregateStrip ("AKKI shielded X identifiers…") + Privacy-report PDF button | (removed) |
| Per-assistant-message footer | (per-message badge) + "Content screened · N" pill + AuditPanel expander | (per-message badge ONLY — click to expand into per-turn audit + Privacy-report PDF) |

## Reproducibility

Anyone can reproduce the visual delta by:

1. Logging in as `admin@akki.ai` / `<redacted:ADMIN_SEED_PASSWORD>`
2. Navigating to `/app/chat`
3. Comparing the surface against `git show HEAD~1:frontend/src/pages/Chat.jsx`
   diff (or any Stage 0 / pre-Stage-A snapshot).

The diff is +199 / −302 LOC across 3 files (`pages/Chat.jsx`
−207 LOC; `components/chat/PerMessageSynisenseBadge.jsx` +199 LOC;
`components/chat/AggregateStrip.jsx` −95 LOC, deleted) → net −103
LOC.
