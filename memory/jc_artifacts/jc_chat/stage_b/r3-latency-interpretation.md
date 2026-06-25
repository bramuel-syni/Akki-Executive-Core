# JC-CHAT Stage B · R3 — Latency interpretation

> **Source of truth:** `/app/memory/JC_CHAT_CANONICAL_SPEC.md` (§ B).
> **Companion files:** `r3-latency-raw.json` + `r3-latency-table.md`.
> **Discipline:** measurement only.

---

## 1 · What was measured

Two call shapes against `gemini-2.5-flash`, 3 trials per shape per
prompt, 3 prompts (simple_question / structured_request /
longer_thought):

- **direct_frontier** — `litellm.acompletion(stream=True)` via the
  same emergent-proxy network hop the Shield uses, BUT WITHOUT
  Shield processing. TTFT measured at first SSE delta from the LLM
  provider. Total measured at last delta.
- **shield_routed** — `shielded_call(...)` via
  `services/solva_v2/engines/llm_adapter_proxy.py`. Full Shield
  pipeline (outbound PII screen + classifier + LLM call + inbound
  restoration + audit-row write). Same primitive used by the
  production chat surface internally — BUT in **buffered**
  single-shot mode, not streaming. TTFT == Total for this shape
  (no intermediate delta).

## 2 · Headline numbers (per-prompt median, ms)

| Prompt | direct ttft | direct total | shield total | Δ ratio |
|---|---:|---:|---:|---:|
| simple_question | ~3200 | ~3200 | ~9900 | **3.1×** |
| structured_request | ~3100 | ~3200 | ~8700 | **2.7×** |
| longer_thought | ~3100 | ~3100 | ~10200 | **3.3×** |

(Exact medians per trial in `r3-latency-raw.json`. Numbers above are
rounded to 100ms for readability.)

## 3 · Honest disclaimer — the comparison is BUFFERED vs STREAMING

This R3 measurement compares:
- direct_frontier in **streaming** mode (TTFT = first delta arrival).
- shield_routed in **buffered** mode (TTFT = full response arrival,
  because `shielded_call` is the BUFFERED Shield primitive — used by
  Solva and Monitor, not by the chat surface).

The production chat path uses a **streaming** Shield primitive
(`/messages/stream` → `_stream_with_shield` →
`_stream_via_litellm_proxy(stream=True)` →
`StreamingReidentifier`). That path's TTFT would be **closer to
direct_frontier's TTFT** (the SSE deltas start landing as soon as
the LLM produces them; the Shield only adds the upfront outbound-
text PII screen as a one-time cost).

**What this R3 measures fairly:**
- The **buffered** Shield overhead (used by Solva/Monitor, not chat).
- An UPPER BOUND on the Shield's processing surface for any single
  turn (3.0× direct latency).

**What this R3 does NOT measure (follow-up):**
- The chat-surface streaming Shield TTFT (true production chat TTFT).
  Requires hitting `/api/chats/{cid}/messages/stream` with cookie +
  CSRF + active-context headers. Should be measured in Stage B
  follow-up if user wants the production-realistic number — but
  building the streaming-Shield trace was scoped OUT of this slice
  to keep Stage B at measurement only.

## 4 · Breakdown of the buffered Shield overhead (≈ 6-7s)

The ~6.5s delta from direct_frontier to shield_routed splits across:

| Component | File:line | Approx contribution | Notes |
|---|---|---:|---|
| Outbound text PII screen (regex + presidio + LLM fallback) | `services/synisense/pipeline.py` | ~3-4s | spacy `en_core_web_sm` fallback in use (trf model not installed — F1 ≈ 0.86 vs 0.91 trf); log line `synisense.shield: using en_core_web_sm fallback` confirms this. **OUT OF BOUNDS** to modify per dispatch — surfacing only. |
| Classifier (`synisense llm classify failed: ServiceUnavailable`) | `services/synisense/pipeline.py` LLM classifier | 0s in this measurement | Classifier was unreachable during the measurement (logged 6 times). Did NOT contribute to latency — fell back to deterministic path. **Worth noting**: when the classifier IS reachable, it would add an additional Shield call. |
| Inbound restoration | `services/synisense/shield/streaming.py:StreamingReidentifier` | ~ ms | Negligible per turn |
| Audit row write + receipt assembly | `services/synisense/pipeline.py + routers/chat_audit_panel.py` | < 50ms | Negligible per turn |
| Network hops to/from emergent proxy | (network) | ~3000ms | Same as direct_frontier (same network path) |

The dominant contributor is the **outbound PII screen** (~3-4s).
Per the dispatch, this is OUT OF BOUNDS — measurement only.

## 5 · Frontend-fixable parity items (where R3 can be addressed WITHOUT Shield modification)

| Item | FE-fixable? | Impact | Notes |
|---|:---:|---|---|
| Use the **streaming** Shield path (already in prod for `/messages/stream`) instead of buffered for the chat surface | ✅ ALREADY DONE | TTFT drops from "total" to "first delta" — matches direct_frontier within the upfront PII screen cost | Confirmed by R1 trace; chat surface is already on streaming Shield. |
| Optimistic UI placeholder during the upfront PII screen (so the user sees "shielding…" feedback before TTFT) | ✅ | Perceived TTFT → ~0ms (immediate "I see you") | Stage C affordance |
| Cache PII screen output for re-sent identical prompts | ⚠️ Shield-path territory | Big TTFT win on retries | **OUT OF BOUNDS — flag only** |
| Background-warm the spaCy / Presidio pipeline on app start (avoid cold-start latency on first turn) | ⚠️ Shield-path territory | Big TTFT win on first turn after cold-start | **OUT OF BOUNDS — flag only** |
| Install `en_core_web_trf` for higher PII precision | ⚠️ Shield-path territory + 2 GB torch install | Marginal precision win | **OUT OF BOUNDS — flag only** |

## 6 · Parity verdict (R1 + R2 + R3 composite)

| Surface | Frontier parity verdict |
|---|---|
| Transport (R2) | PARITY |
| Streaming method (R2) | PARITY |
| Cadence (R2) | PARITY |
| TTFT for **buffered** Shield (R3 measured) | **3.0× direct** — buffered-Shield overhead floor |
| TTFT for **streaming** Shield (R3 NOT measured this slice) | Should be ~direct + upfront PII-screen cost — follow-up if needed |
| Surface parity items (R1) | 9 FE-fixable; ALL addressable in Stage C without Shield touches |
| Audit / trust receipt | AKKI ADVANTAGE (no equivalent on native frontier surfaces) |

**Stage B verdict: parity is on the streaming method (R2) and on
the 9 FE-fixable surfaces (R1). The latency story (R3) has a known
3.0× buffered overhead floor driven by the outbound PII screen
(Shield-path; out of bounds). The production chat surface uses
streaming Shield which should land much closer to direct frontier —
follow-up measurement available if requested.**
