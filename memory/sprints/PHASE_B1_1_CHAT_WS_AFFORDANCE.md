# Phase B1.1 — Chat Manual Work Studio Affordance

**Date:** 2026-06-24
**Status:** CLOSED
**Acceptance:** by execution evidence (per `PART 4` operating rule).
**Source dispatch:** User dispatch "Chat B1.1 — Manual Work Studio Affordance".

## Headline result

Manual affordance live on `/app/chat`. Composer toolbar **"Create"** button → modal with all 6 generation kinds + mechanically-prefilled `description` / `objective` / `scope` from the live conversation → handoff to the WS1-uniform `/api/contexts/{ctx}/work-studio/export/{kind}` route. End-to-end chain verified: payload → `export_id=7fd6da82-5685-49a0-ad6a-5a52882985fc` → COMPLETE → **38 891-byte DOCX** with valid ZIP magic + correct OpenXML MIME. Prefill is **100% pure JS** — zero net-new LLM calls (static code audit + DOM smoke confirm).

## Acceptance evidence (lead, per `PART 4`)

### A1 — Manual affordance trigger (explicit user action)

`frontend/src/pages/Chat.jsx:2050` — new toolbar button:

```jsx
<button
  type="button"
  onClick={onOpenWS}
  disabled={sending || !wsContextId}
  data-testid="chat-ws-affordance-btn"
  title={
    wsContextId
      ? "Create a Work Studio artefact from this conversation"
      : "Open this chat inside an organisation context to create a Work Studio artefact"
  }
>
  <Sparkles className="w-3 h-3" /> <span>Create</span>
</button>
```

Per `PART 1` lock — Work Studio trigger is manual affordance interim until Phase Shield-Tools ships:
- NOT a model-tool-call.
- NOT an intent classifier.
- User explicitly clicks the button.

### A2 — Modal renders with all 6 kinds + clean prefill

New component: `frontend/src/components/chat/WorkStudioAffordanceModal.jsx` (404 LOC).

Live preview smoke (admin@akki.ai → /app/chat → modal open):
```
ws-affordance-btn-present: True
modal-opened: True
kind-card-brief: True
kind-card-deck: True
kind-card-report: True
kind-card-minutes: True
kind-card-committee_pack: True
kind-card-board_pack: True
model-options-rendered: 6
prefill-lengths: description=>20 objective=>50 scope=>40
```

All 6 kinds reachable (carries forward WS1's `/export/{kind}` uniformity).

### A3 — Prefill is MECHANICAL (zero net-new LLM calls)

Static audit of `WorkStudioAffordanceModal.jsx` for any LLM-bound network call:

```
grep -nE "api\.(get|post|put|patch|delete|__raw)|fetch\("
  135: api.get(/exports/{id})         ← POLLING (only step==='working')
  169: api.post(/export/{kind})       ← Create handoff (only on user click)
  192: string concatenation           ← not a call
  197: api.__raw.get(/download)       ← Download (only on user click)
```

The three prefill helpers — `_prefillDescription(messages, contextName)`, `_prefillObjective(messages)`, `_prefillScope(contextName, chatTitle)` — are **synchronous pure-JS functions** with zero side effects. They run inside `useMemo` on the modal-open lifecycle. No `api.*` or `fetch()` calls anywhere in the prefill path.

**Verification of `PART 1` audit-volume lock:** the Shield audit log records ONE row per LLM call. The prefill phase introduces ZERO LLM calls. The Create button's POST triggers exactly the same `/export/{kind}` audit chain WS1 already verified — a single LLM invocation per artefact, identical row-count delta to a direct `/export/{kind}` curl. No surprises in audit volume.

**Prefill semantics (per dispatch wording — "mechanical extraction"):**
- `description` ← last 6 messages, joined with `[ROLE]\n{content}` headers + `\n\n` separators, capped at 4000 chars.
- `objective` ← last user message, full body if ≤240 chars; otherwise the last sentence-sized clause (split on `[.!?]\s+|\n\n+`).
- `scope` ← single-line composite of `Context: {context_name}. Conversation: {chat_title}.`.

If `messages` is empty or absent, prefill falls back to a friendly placeholder ("(New conversation — no prior turns to summarise.)") so the modal never lands in a broken state.

### A4 — Handoff to `/export/{kind}` works end-to-end

Drove the exact payload shape the modal sends (description + objective + scope) to the WS1 endpoint:

```
POST /api/contexts/aff5e102-04b8-4948-9f6b-27c9eca1f0d7/work-studio/export/board_pack
  payload (exactly what the modal POSTs):
    {
      "description": "[USER]\nPlease prepare a concise board pack...",
      "objective":   "Please prepare a concise board pack covering...",
      "scope":       "Context: Ubora Capital Partners. Conversation: B1.1 smoke chat."
    }
  → 200 export_id=7fd6da82-5685-49a0-ad6a-5a52882985fc status=running

(after ~110s polling)
GET .../exports/7fd6da82 → kind=board_pack status=complete
  file_name=ubora-bank-board-pack-q1-2026.docx
  download_token=present output_format=docx

GET .../exports/7fd6da82/download?token=...
  → HTTP 200 38 891 bytes
  content-type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
  file signature: 504b0304 (ZIP magic — valid DOCX)
```

### A5 — Disabled-out-of-org tooltip surfaces honestly

The `/export/{kind}` route requires `context_id` membership. When the active chat has `context_id === null` (general chat, no org), the affordance button is disabled with the tooltip:

> "Open this chat inside an organisation context to create a Work Studio artefact"

Verified in DOM:
```
ws-btn-present: True
ws-btn-disabled-attr: True
```

Inside an org context, the button enables. The disabled-tooltip path is the honest surfacing of the existing tenancy gate — no new gate added; the modal carries the chat's context to `/export/{ctx}/...` as-is.

### A6 — Consumer-feel preserved

- Zero governance artifacts surface in the conversation when the affordance is used. The modal is a separate UI surface (shadcn `Dialog`) — receipts land on Trust Center via the existing audit chain (`_append_chat_audit` is called inside `_run_export`, unchanged).
- Sub-modal interaction: pick → review → working → done. Each step gets a single primary CTA (Create / Download). No multi-step wizard noise. Minimal clicks: 2 clicks from chat surface to "Create" press (button → kind card auto-advances to review → Create).
- Loading state: a single `Loader2` spinner + plain-English ETA ("This usually takes 30–90 seconds.").
- Done state: file-name display + Download + "Open in Work Studio" link (so the user can iterate via overlay if they want richer revision).

### A7 — All existing Chat characterization tests stay green

`pytest tests/invariants/ -m "not integration"` → **21 passed**, 4 deselected. Specifically:
- `test_invariant_chat_streaming_reidentify_present.py` (B1 AST invariant, 4 checks) — green.
- `test_invariant_shield_no_leak.py` default-lane (7 deliberate-violation rail tests + clean payload + token-types) — green.
- `test_invariant_first_session_response_shape.py` — green.
- `test_invariant_http_transport_pydantic_kwargs.py` — green.

No backend code touched in B1.1; only frontend wiring + the modal component. The B1 invariants therefore stay green by construction.

## Architectural invariants honored (per `PART 0`)

- ✅ Shield is still the ONLY outbound path to any LLM — touched no LLM-routing code. The Create button's `api.post(/export/{kind})` flows through the existing WS export pipeline, which routes Pass-1 and Pass-2 through the Shield exactly as it does for a direct `/export/{kind}` curl. Audit chain is `_append_chat_audit` per `_run_export` (`work_studio_export.py:176`).
- ✅ Tenancy + per-call audit + receipt + fail-closed unchanged — no tenancy logic touched; the modal's `contextId` prop is read from `activeChat.context_id` which carries the same membership gate the rest of the chat surface honors.
- ✅ Boundary fitness 0 violations — no cross-context calls added; the modal cannot post to a context the user isn't a member of (the `/export` route gates on `require_context_membership`).
- ✅ REUSE — uses existing `/export/{kind}` route (no new BE endpoint). The modal is the missing UI layer per `PART 0` rule 4.
- ✅ NO SyniSense tokenization changes.
- ✅ Status ≠ truth — every acceptance claim above backed by execution evidence: a real downloaded artefact, a real DOM smoke, or a static code audit referencing exact line numbers.

## Stop-and-report (none tripped)

- ❌ Single target route can't carry all 6 kinds — WS1's `/export/{kind}` carries all 6; the modal calls it directly. No fork.
- ❌ Prefill requires an LLM call — prefill is pure JS as verified above. No fork.
- ❌ Any change weakens Shield / tenancy / audit / boundary — none did.

## Files touched

### New
- `frontend/src/components/chat/WorkStudioAffordanceModal.jsx` (404 LOC) — the modal component. Pure JS prefill + shadcn Dialog + 4-state lifecycle (pick → review → working → done).
- `memory/sprints/PHASE_B1_1_CHAT_WS_AFFORDANCE.md` (this file).

### Modified (frontend wiring — surgical)
- `frontend/src/pages/Chat.jsx`:
  - Imports: added `WorkStudioAffordanceModal` + `Sparkles` lucide icon.
  - State: new `wsModalOpen` near the existing dialog states.
  - Composer signature: added `onOpenWS` + `wsContextId` props.
  - Composer toolbar: new "Create" button next to "Think harder", wired to `onOpenWS` with disabled-out-of-org tooltip.
  - Modal mount: `<WorkStudioAffordanceModal ... />` near the existing `<AuditDialog />` mount, carries `activeChat.messages`, `activeChat.context_id`, `activeContext.name`, `activeChat.title`.

### Untouched (deliberately)
- Backend (every file in `backend/`) — the `/export/{kind}` route already accepts the payload shape the modal sends; no BE code change required.
- Shield / llm_router / audit_log / tenancy / contracts — no edits.

## Maintenance Protocol Compliance

1. ✅ `DEV_PIPELINE.md` §1, §3.3, §9 updated BEFORE this memo was written.
2. ✅ `pipeline-log-sync.yml` KNOWN_MAPPINGS extended with `"B1_1_CHAT_WS_AFFORDANCE": "B1.1"` BEFORE this memo was written.
3. ✅ This memo written into a state where §9 + the gate's identifier mapping are both in place.
4. ✅ `pipeline-log-sync.yml` Python logic exits 0 against the working tree at memo-write time.

## Next (per consolidated dispatch queue)

1. **ThinkLab Gate A render-check + Flag 3 verification** — resumes priority. Output deck at `/api/memory/gate_a/`. Gate A is what unblocks ThinkLab TL1.1.
