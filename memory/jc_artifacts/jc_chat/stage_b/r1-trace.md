# JC-CHAT Stage B · R1 — End-to-end chat trace

> **Source of truth:** `/app/memory/JC_CHAT_CANONICAL_SPEC.md` (§ B — Parity).
> **Captured:** 2026-06-25.
> **Discipline:** measurement only — Shield path OUT OF BOUNDS. Cite
> file:line for every claim; classify "frontend-fixable" vs "Shield-path"
> per the dispatch.

---

## 1 · The wire-level flow (composer keystroke → rendered token)

| # | Step | Surface | File:line | Class |
|---|---|---|---|---|
| 1 | User types in composer; presses Enter | FE | `pages/Chat.jsx:556-657` (`onSend`) | FE-FIXABLE |
| 2 | Optimistic user bubble + streaming placeholder appended to local state | FE | `pages/Chat.jsx:665-680` | FE-FIXABLE |
| 3 | CSRF token ensured (production lesson — `axios` interceptor doesn't run on raw `fetch()`) | FE | `pages/Chat.jsx:706-711` | FE-FIXABLE |
| 4 | Active-context header attached (`X-Active-Context`) | FE | `pages/Chat.jsx:751-753` | FE-FIXABLE |
| 5 | `fetch('POST /api/chats/{cid}/messages/stream', body={content, attached_document_ids, …})` | FE | `pages/Chat.jsx:745-769` | FE-FIXABLE (transport choice) |
| 6 | Server resolves chat row + tenancy gates | BE | `routers/chat.py` `stream_message` (line 2722) | BE — NOT Shield path |
| 7 | Outbound text classification (turn class — `strategic_deliverable` / `casual` / `clarifier` …) | BE | `routers/chat.py:159 _classify_turn` | BE — non-Shield |
| 8 | **Outbound shield**: PII screen on the user's text BEFORE the LLM call (regex → presidio → LLM fallback) | BE-SHIELD | `services/synisense/shield/streaming.py:_stream_with_shield` + `services/synisense/pipeline.py` | **SHIELD-PATH — OUT OF BOUNDS** |
| 9 | LLM call via `litellm.acompletion(stream=True)` through the emergent integration proxy | BE-SHIELD | `services/synisense/shield/streaming.py:_stream_via_litellm_proxy` (line 247) | **SHIELD-PATH — OUT OF BOUNDS** |
| 10 | Delta loop: each LLM delta is passed through the inbound shield (`StreamingReidentifier`) | BE-SHIELD | `services/synisense/shield/streaming.py` | **SHIELD-PATH — OUT OF BOUNDS** |
| 11 | SSE frames written to the response stream as `data: {...}\n\n` | BE | `routers/chat.py:stream_message` SSE writer | BE — framing only |
| 12 | Audit row written per turn (Shield trust receipt, layer breakdown, identifier counts) | BE-SHIELD | `services/synisense/pipeline.py + routers/chat_audit_panel.py` | **SHIELD-PATH — OUT OF BOUNDS** (audit shape) |
| 13 | Terminal `message` event with rehydrated `assistant_text` | BE | `routers/chat.py:stream_message` | BE — framing only |
| 14 | FE parses SSE deltas, applies markdown stream renderer | FE | `pages/Chat.jsx:741-866` (raw fetch + ReadableStream parser); `components/chat/markdownStream.js` | FE-FIXABLE |
| 15 | On terminal `message`, FE swaps streamed text for rehydrated assistant_text | FE | `pages/Chat.jsx:applyStreamUpdate` | FE-FIXABLE |
| 16 | Per-message badge mounts (`PerMessageSynisenseBadge`) — JC-CHAT Stage A surviving marker | FE | `components/chat/PerMessageSynisenseBadge.jsx` | FE-FIXABLE (Stage A landed) |

## 2 · Class summary (what can move where)

| Class | Count | Examples | Action latitude |
|---|---:|---|---|
| **FE-FIXABLE** | 9 | composer / optimistic UI / SSE consumer / markdown stream / badge | Free latitude — Stage A landed surface cleanup; Stage C can extend (rename / restore / permanent-delete / edit-prompt) |
| **BE non-Shield (framing only)** | 3 | endpoint resolution / tenancy / SSE writer | Within scope IF we touch them; mostly stable |
| **BE non-Shield (turn classifier)** | 1 | `_classify_turn` | Within scope but historically stable — change only with evidence |
| **SHIELD-PATH — OUT OF BOUNDS** | 5 | outbound shield · LLM call · inbound shield · audit / receipt | **Touch is FORBIDDEN by dispatch.** Measurement only. |

## 3 · "Parity to native frontier-LLM" — what's missing and where

The dispatch frames Stage B as measuring parity to "native frontier-LLM
experience without touching the Shield path." The 9 FE-FIXABLE steps
above contain every parity-gap candidate the Shield-path *isn't*
contributing to. From a UX walk-through against ChatGPT/Claude/Gemini
native surfaces:

| Parity gap | Where it lives | Class | Fix-track |
|---|---|---|---|
| Markdown rendering (LaTeX / table inline) | `components/chat/markdownStream.js` | FE-FIXABLE | Stage C polish |
| Citations / source chips inline with text | FE renderer (`components/chat/`) | FE-FIXABLE | Stage C |
| "Stop generating" mid-stream (cancel) | `pages/Chat.jsx:728-730` AbortController already wired | FE — partially landed | Verify on FE only |
| "Edit prompt" affordance (return to composer with previous text) | FE — does NOT exist today | FE-FIXABLE | Stage C punch-list (per Q5: R5 verbatim-report only) |
| Conversation rename (without permanent delete) | FE | FE-FIXABLE | Stage C punch-list |
| Soft-restore (un-archive) | FE | FE-FIXABLE | Stage C punch-list |
| Permanent delete (hard-delete) | FE + BE non-Shield | FE-FIXABLE | Stage C punch-list |
| Token-level streaming smoothness | The SSE delta cadence is ALREADY token-level via `_stream_via_litellm_proxy` (see R2). | Shield-path internal | **OUT OF BOUNDS** — measured, not modified |
| Aggregate latency vs frontier | See R3 measurement. | Shield-path internal | **OUT OF BOUNDS** — surfaced, not modified |

All five Shield-path steps are intentionally left as-is per the
dispatch. The remaining nine FE-fixable steps are where Stage C
work would land.

## 4 · Trace conclusion

The chat path threads 16 wire-level steps. Nine are frontend (free
to modify in Stage C). Three are backend-framing-only (resolve +
tenancy + SSE writer — touch with caution; no fix needed today).
One is backend-classifier (`_classify_turn` — stable; don't churn).
**Five are Shield-path** (outbound shield → LLM call → inbound shield
+ delta restore → SSE-framed deltas with audit annotations → audit
trust-receipt). Per dispatch: measurement only on those five.

The parity gaps that motivate Stage C ALL live in the nine
FE-fixable steps. None require Shield-path modification.
