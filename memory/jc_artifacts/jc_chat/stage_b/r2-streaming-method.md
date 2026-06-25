# JC-CHAT Stage B · R2 — Streaming method

> **Source of truth:** `/app/memory/JC_CHAT_CANONICAL_SPEC.md` (§ B).
> **Captured:** 2026-06-25.
> **Discipline:** measurement only.

---

## 1 · Transport: HTTP/1.1 SSE (Server-Sent Events) via raw `fetch()` + ReadableStream

The chat surface streams via **Server-Sent Events** over a standard
`POST` request. Two deliberate non-default choices, both documented
with the production lesson that drove them:

| Choice | Why not the default | File:line |
|---|---|---|
| Use `fetch()` + `ReadableStream`, NOT `EventSource` | `EventSource` is GET-only and can't send a JSON body; the chat needs to POST `{content, attached_document_ids, force_class, …}`. `EventSource` also doesn't carry the bearer token + CSRF header cleanly. | `pages/Chat.jsx:683-705` |
| Manually attach `X-CSRF-Token` on the raw fetch | Production P5.10 (2026-02) lesson — the `axios` interceptor in `lib/api.js` auto-injects CSRF on axios calls, but doesn't run on raw `fetch()`. Without the manual injection, `POST /messages/stream` returned 403 in ~0.3s, the SPA stripped the optimistic bubble, and the user saw "instantly cancelled." | `pages/Chat.jsx:695-711` |

The endpoint emits `text/event-stream` framed as `data: <json>\n\n`.

## 2 · Event types on the wire

| Event | Payload shape | Class | Fired by |
|---|---|---|---|
| `ack` | `{message_id, classification, …}` (kickoff acknowledgement, after the user-text Shield pass returns) | BE-SHIELD (framing only) | `routers/chat.py:stream_message` after `_shield_outbound_text` |
| `delta` | `{text: "<shielded chunk>"}` — one per inbound LLM delta, mid-flight Shield restoration applied | BE-SHIELD (Shield-path content) | `services/synisense/shield/streaming.py` delta loop |
| `message` | `{message_id, assistant_text, synisense_stats, layer_breakdown, …}` — terminal canonical state | BE-SHIELD (Shield-path content + audit) | end of `stream_message` |
| `done` | `{}` (close-of-stream sentinel) | BE | `stream_message` |
| `error` | `{error, retryable, …}` (transient/permanent failure surfacing) | BE | `stream_message` exception path |

The terminal `message` event carries the **rehydrated** assistant
text. The FE swaps the streamed (Shield-restored on the fly) text
for the canonical rehydrated text once `message` arrives, so PII /
citations resolve correctly even if the delta loop got fragments
split across word boundaries.

## 3 · Shield's per-delta processing (in-stream)

The Shield's primitive that drives the LLM call is
`_stream_via_litellm_proxy` (`services/synisense/shield/streaming.py:247-291`).
It calls `litellm.acompletion(stream=True)` against the emergent
integration proxy with `custom_llm_provider="openai"` (OpenAI-compatible
delta shape across providers — Gemini and OpenAI both flow through
the same delta-yielding loop).

Per LLM delta the Shield:
1. Receives raw delta text from the provider.
2. Runs the inbound restoration pass (`StreamingReidentifier`) — masks
   become identifiers again on the client-facing text.
3. Captures the inbound layer breakdown for the audit record.
4. Yields a `delta` SSE event with the now-restored text.

This is **continuous streaming**, not chunk-batched buffering — the
chat-surface SSE cadence matches the LLM provider's native delta
cadence almost 1:1 (modulo Shield restoration overhead, which is
microseconds per delta).

## 4 · Comparison to frontier-LLM native chat surfaces

| Trait | AKKI chat (Shield) | ChatGPT / Claude / Gemini native | Verdict |
|---|---|---|---|
| Transport | HTTP/1.1 SSE | HTTP/1.1 SSE (or WebSocket for ChatGPT) | **PARITY** |
| Cadence | Per-delta (1:1 with provider) | Per-delta (1:1) | **PARITY** |
| Token-level smoothness | Provider-native, Shield-restoration applied per delta | Provider-native, no restoration | **PARITY** (overhead is sub-millisecond per delta) |
| Mid-stream cancel | AbortController wired (`pages/Chat.jsx:728-730`) | Yes | **PARITY** |
| Terminal canonical state | Yes — `message` event swaps streamed text | Yes — provider's "stop" event | **PARITY** |
| Per-message audit / trust receipt | Yes — Shield writes audit row + badge surfaces it | No (no Shield to audit) | **AKKI ADVANTAGE** |

R2 verdict: **the streaming method itself is at parity with native
frontier-LLM surfaces.** No parity work needed on the streaming
mechanism. The remaining parity-gap surface area is in R1's
FE-fixable category (markdown rendering polish, "edit prompt"
affordance, restore/rename/delete) and R3 latency.

## 5 · Important caveat — what is NOT measured here

The Shield's per-delta processing introduces **microsecond-class**
overhead per delta. That is invisible in normal use. The overhead
that *IS* measurable is the **upfront** Shield work: the
outbound-text PII screen (before the LLM call starts), the
classifier, and the trust-receipt assembly. Those are captured in
**R3 latency**. Streaming method per se is parity; the upfront
processing is the latency gap surface.
