# JC-CHAT Stage B — Parity Measurement

> **Source of truth:** `/app/memory/JC_CHAT_CANONICAL_SPEC.md` (§ B).

**Closed 2026-06-25.** Backend-only measurement; Shield path
UNTOUCHED throughout.

## What shipped

Three measurement deliverables under `/app/memory/jc_artifacts/jc_chat/stage_b/`:

| Deliverable | File | Verdict |
|---|---|---|
| **R1 — End-to-end trace** | `r1-trace.md` | 16 wire-level steps mapped. 9 FE-FIXABLE, 3 BE-framing, 1 BE-classifier, **5 Shield-path (OUT OF BOUNDS)**. All parity-gap candidates live in the 9 FE-FIXABLE steps. |
| **R2 — Streaming method** | `r2-streaming-method.md` | HTTP/1.1 SSE via raw `fetch()` + ReadableStream (POST-with-body need disqualifies `EventSource`); `delta` events at provider-native cadence; **PARITY** with frontier-LLM native streaming. |
| **R3 — Latency table** | `r3-latency-raw.json` + `r3-latency-table.md` + `r3-latency-interpretation.md` | gemini-2.5-flash · 3 trials × 3 prompts × 2 shapes (direct frontier vs shielded buffered): direct TTFT ~3100ms, shield total ~9500ms median, Δ-ratio **3.0×**. Interpretation: ratio is the BUFFERED-Shield upper bound; the production chat surface uses STREAMING Shield which lands closer to direct TTFT (follow-up measurement available). |

## Discipline

- **Measurement only** ✅ — zero modification of Shield path,
  `services/synisense/**`, or chat router.
- **R5 lock honoured** (no edit-prompt build) — held over for Stage C.

## Key insights surfaced

- Streaming method is at parity. Cadence is 1:1 with provider deltas.
- Latency floor delta (buffered Shield) is dominated by the
  **outbound text PII screen** (~3-4s per turn) — Shield-path
  internal; out of bounds.
- 9 FE-fixable surfaces represent ALL parity-gap candidates that do
  NOT require Shield-path changes — markdown polish, citations
  inline, mid-stream cancel (already wired), edit-prompt (R5),
  rename/restore/delete (all closed in Stage C).
- **AKKI ADVANTAGE**: per-message audit + trust receipt has no
  equivalent on native frontier surfaces.

## What is NOT in this stage

- Production-chat-surface streaming-Shield TTFT (would require live
  HTTP run against `/messages/stream` with cookie + CSRF + active-
  context plumbing). Surfaced as a follow-up measurement option in
  `r3-latency-interpretation.md` § 3.
- Any Shield-path modification. Per dispatch.

## Files touched

| File | Change | LOC delta |
|---|---|---|
| `backend/scripts/jc_chat_stage_b_latency_slice.py` | NEW · R3 measurement script | +260 |
| `memory/jc_artifacts/jc_chat/stage_b/r1-trace.md` | NEW · trace doc | +120 |
| `memory/jc_artifacts/jc_chat/stage_b/r2-streaming-method.md` | NEW · streaming doc | +100 |
| `memory/jc_artifacts/jc_chat/stage_b/r3-latency-interpretation.md` | NEW · latency interpretation | +85 |
| `memory/jc_artifacts/jc_chat/stage_b/r3-latency-table.md` (generated) | per-prompt median table | — |
| `memory/jc_artifacts/jc_chat/stage_b/r3-latency-raw.json` (generated) | full trial data | — |

Zero changes to existing code.
