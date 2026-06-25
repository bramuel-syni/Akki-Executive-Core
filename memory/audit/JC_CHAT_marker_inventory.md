# JC-CHAT Stage 0 — Marker inventory (R4 / F1 / F2 classification)

> **Source of truth:** `/app/memory/JC_CHAT_CANONICAL_SPEC.md`
>
> **Purpose:** Classify-before-remove per the R4 lock
> ("assume-shared-until-proven-chat-only"). Output per-marker verdict
> (REMOVE / HIDE-ON-CHAT-SURFACE) + Privacy-report scope (F1) +
> AUDIT-button a11y (F2). Surface BEFORE Stage A runs the executions.

---

## S0-R4 — Per-marker inventory

The dispatch names 5 markers (one survives, four are proposed for
removal). Inventory by import-site lookup across
`/app/frontend/src/**/*.{jsx,tsx}`:

| # | Marker (dispatch name) | Component / location | Render-site(s) | Used outside Chat? | **Verdict** |
|---|---|---|---|:---:|:---:|
| 1 | Title `redacted` pill | `SynisenseInlineBadge` — defined inline in `pages/Chat.jsx:2420-2449` (function); rendered at `Chat.jsx:1534` from `<ChatHeader>` | Chat header (one site) | ❌ NO — defined inside `Chat.jsx`, exported nowhere, imported nowhere else | **REMOVE** (chat-only) |
| 2 | Per-message "class chip" | Inline JSX block in `MessageBubble` (`Chat.jsx:1857-1872`) — `data-testid="chat-synisense-icon"`. The "Content screened · {n}" button-pill on assistant bubbles | Per-message (every assistant turn with spans_redacted > 0) | ❌ NO — inline JSX, no shared component | **REMOVE** (chat-only) |
| 3 | Header `AUDIT` button | `<button data-testid="chat-audit-btn">` at `Chat.jsx:1566-1573` (inline) — opens `<AuditDialog>` (defined at `Chat.jsx:2284-2418`) | Chat header (one site) | ❌ NO — button inline; the dialog it opens is also defined inline in `Chat.jsx` | **REMOVE** (chat-only) |
| 4 | Floating exposure banner + Privacy-report button | `AggregateStrip` — `components/chat/AggregateStrip.jsx` (98 LOC). Mounts at `Chat.jsx:1389` | Chat surface (one site) | ❌ NO — imported only from `pages/Chat.jsx:46`; no other consumers | **REMOVE** (chat-only) |
| 5 | "Synisense audit" expander | `AuditPanel` — `components/chat/AuditPanel.jsx` (shared component). Mounts at `Chat.jsx:1878` (per assistant message) | Chat + Solva voice audit + Solva Phase D | ✅ **YES** — imported in 3 surfaces: `pages/Chat.jsx:45`, `pages/SolvaSession.jsx:53,521`, `pages/SolvaPhaseDSession.jsx:20,455` | **HIDE-ON-CHAT-SURFACE** (per R4 lock — assume-shared-until-proven-chat-only). Component itself stays — Solva keeps it. |
| — | **SURVIVING** marker (NOT in this table) | `PerMessageSynisenseBadge` — `components/chat/PerMessageSynisenseBadge.jsx`. Mounts at `Chat.jsx:1752` (per assistant message) | Chat only | ❌ NO — chat-only | **KEEP** — sole surviving marker per dispatch Part A |

### What the four "REMOVE" markers actually delete

- (1) `SynisenseInlineBadge` function declaration (Chat.jsx:2420-2449) + its render site (Chat.jsx:1534)
- (2) The 16-line inline JSX block (Chat.jsx:1857-1872) including its testid `chat-synisense-icon`
- (3) The `<button data-testid="chat-audit-btn">` block (Chat.jsx:1566-1573); after the A11y-binding migration (S0-F2), `<AuditDialog>` itself stays defined (it's invoked from the per-message badge's "Open audit" expansion, not just the header button — verify before the A pass)
- (4) `AggregateStrip` mount (Chat.jsx:1389) + its `import` statement; the component file `components/chat/AggregateStrip.jsx` itself can be deleted (zero imports elsewhere). The Privacy-report endpoint `/api/chats/{cid}/privacy-report.pdf` is UNTOUCHED — only the FE invocation moves into the surviving badge's audit panel (per S0-F1 verdict below).

### What the "HIDE-ON-CHAT-SURFACE" marker does

- (5) `AuditPanel` itself: untouched (Solva keeps it).
- The chat-side mount at `Chat.jsx:1878` is gated behind a chat-only conditional that defaults to **hidden** so the AuditPanel does not render on the chat surface. The surviving `PerMessageSynisenseBadge` expansion delivers the same per-message audit access via its own UI.
- If a future requirement reverses (e.g. "show AuditPanel on chat for power-users"), the gate flips with no component change.

---

## S0-F1 — Privacy-report scope check

Endpoint: `GET /api/chats/{chat_id}/privacy-report.pdf`
(`routers/solva_phase_e_polish.py:389-447`).

Endpoint shape:
```python
@chat_pdf_router.get("/{chat_id}/privacy-report.pdf")
async def chat_privacy_report_pdf(
    chat_id: str,
    account: Dict[str, Any] = Depends(get_current_account),
):
    """Generate a privacy-report PDF for one chat. Streams as
    `application/pdf`. Strict scoping: the chat must belong to the
    requesting account.
    ...
    """
```

The URL path requires `{chat_id}`. The handler scopes to that chat
explicitly (`_chat_obj = await get_akki().get_chat(account_id=...,
chat_id=chat_id)`). There is NO global-across-conversations variant.

**FE call site:** `components/chat/AggregateStrip.jsx:46` —
`api.get('/chats/${chatId}/privacy-report.pdf', ...)`. Passes the
current chat's id; no batch/global invocation anywhere.

### Verdict

**The Privacy-report is PER-CONVERSATION today.** Relocating it from
the floating `AggregateStrip` banner into the per-message badge's
audit-expansion is a **CLEAN MOVE** — same scope, different surface.
**No additive-vs-narrowing concern** — the F1 lock only triggers if
the export had been global; it wasn't.

The locked decision on the relocation shape:

> When the user expands the surviving `PerMessageSynisenseBadge` for a
> turn, the audit-expansion panel surfaces a `Download privacy report
> for this conversation` action. It calls the same
> `/api/chats/{chatId}/privacy-report.pdf` endpoint with the same
> `chatId`. The PDF content is **byte-identical** to what
> `AggregateStrip` produced today.

---

## S0-F2 — Accessibility hooks on the AUDIT button

The header `AUDIT` button (Chat.jsx:1566-1573):

```jsx
<button
  onClick={onAudit}
  className="text-[var(--muted)] hover:text-[var(--ink)] text-[11.5px] uppercase tracking-wider inline-flex items-center gap-1 px-2 py-1 rounded-sm hover:bg-[var(--cream-deep)]/40"
  data-testid="chat-audit-btn"
  title="View audit log"
>
  <Eye className="w-3 h-3" /> Audit
</button>
```

A11y bindings present:
- ✅ `title="View audit log"` (tooltip — hover)
- ❌ no keyboard shortcut (no `accessKey`, no global keydown listener for an Audit hotkey grep'd in `Chat.jsx`)
- ❌ no `aria-label` (only the text content "Audit")
- ❌ no `role` attribute (defaults to `button`)
- ❌ no ARIA-controls binding to the dialog

### Verdict

**Minimal a11y binding — only the `title="View audit log"` tooltip.**
No keyboard shortcut to preserve.

**Migration plan for the surviving marker (PerMessageSynisenseBadge):**
- Add `title` attribute on the expanded badge's "open audit" affordance
  (or its wrapping button): `"Open this turn's audit log"`.
- Add `aria-label` matching the title (filling the gap from the
  removed marker).
- No keyboard-shortcut binding to migrate — the dispatch doesn't
  call out a hotkey, and none exists today.

---

## Summary table (verdicts in one place)

| Marker | Verdict | Notes |
|---|---|---|
| Title `redacted` pill (`SynisenseInlineBadge`) | **REMOVE** | Chat-only inline function. |
| Per-message "Content screened · N" pill | **REMOVE** | Chat-only inline JSX. |
| Header `AUDIT` button | **REMOVE** | Chat-only inline; minor a11y (title-only) migrates to surviving badge. |
| Floating exposure banner (`AggregateStrip`) + Privacy-report button | **REMOVE** | Chat-only component (`components/chat/AggregateStrip.jsx`); Privacy-report action moves into surviving badge's audit panel; PDF endpoint is per-conversation today (F1 = clean move, not narrowing). |
| `AuditPanel` expander | **HIDE-ON-CHAT-SURFACE** | Shared (Chat + Solva + Solva Phase D). Component untouched. Chat render gated to hidden by default. |
| `PerMessageSynisenseBadge` | **KEEP (sole surviving marker)** | Picks up the migrated Privacy-report action + a11y (`title`/`aria-label`). |

---

## Stage A execution plan (CLEARED by this classification)

When Stage A runs:

1. **Remove** four chat-only markers (one inline function + one inline
   JSX block + one inline button + one imported component +
   delete the `AggregateStrip.jsx` file).
2. **Hide-on-chat-surface** the `AuditPanel` mount in `Chat.jsx:1878`
   only — DO NOT touch the component file.
3. **Migrate** the Privacy-report action into the surviving badge's
   audit-expansion panel — same endpoint, same chat scope, same PDF.
4. **Migrate** the minor a11y binding (`title="View audit log"`) onto
   the surviving badge's expand affordance, plus the now-missing
   `aria-label`.
5. Auto-shield CONTROL (not a marker — keep distinct per dispatch).

### Files touched (preview)

| Layer | File | Change |
|---|---|---|
| FE | `pages/Chat.jsx` | Remove inline `SynisenseInlineBadge` function + its render site (line 1534); remove inline "Content screened" pill (1857-1872); remove header AUDIT button (1566-1573); remove `<AggregateStrip>` import + mount (line 46 + 1389); gate `<AuditPanel>` render at 1878 behind `show_chat_audit_panel = false` constant. ~60 LOC delta. |
| FE | `components/chat/PerMessageSynisenseBadge.jsx` | Add a11y (`title`, `aria-label`) on expand affordance; add `Download privacy report for this conversation` action that calls the existing `/chats/{chatId}/privacy-report.pdf` endpoint. ~20 LOC delta. |
| FE | `components/chat/AggregateStrip.jsx` | **Delete file** (zero imports elsewhere; behaviour migrated). |
| BE | (none) | **Shield path untouched.** No backend changes in Stage A. |

**No backend changes. Shield path untouched.** This is a pure
surfacing pass per the dispatch.
