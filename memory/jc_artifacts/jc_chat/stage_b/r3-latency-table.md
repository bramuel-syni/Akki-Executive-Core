# JC-CHAT Stage B · R3 — Latency table

> Captured: 2026-06-25T21:24:29.144401+00:00
> Trials per shape: 3
> Shapes measured: direct_frontier (litellm via emergent proxy, no Shield), shield_routed (shielded_call via solva_v2 adapter — same primitive used by the production chat surface).

## Per-model · per-prompt medians (ms)

### gemini-2.5-flash

| Prompt | direct ttft (ms) median | direct total (ms) median | shield ttft (ms) median | shield total (ms) median | Δ ttft (ms) | Δ total (ms) | Δ total ratio |
|---|---:|---:|---:|---:|---:|---:|---:|
| simple_question | 3214 | 3215 | 9916 | 9916 | 6702 | 6701 | 3.08x |
| structured_request | 3127 | 3128 | 8664 | 8664 | 5537 | 5536 | 2.77x |
| longer_thought | 3074 | 3075 | 10265 | 10265 | 7191 | 7190 | 3.34x |

## Notes

- **direct_frontier** uses `litellm.acompletion(stream=True)` with the emergent integration proxy — same network hop as Shield, no Shield processing. TTFT measured at first SSE delta.
- **shield_routed** uses `shielded_call(...)` — outbound PII screen + classifier + LLM call + restore + audit. The chat surface's `/messages/stream` endpoint composes the same pipeline plus an SSE-streaming wrapper; the wrapper itself adds < 50ms framing overhead per measurement-sub-experiments (see R2 note).
- Network jitter ≈ ±50ms; medians over 3 trials chosen to absorb single outliers.
- Δ total ratio = shield_total ÷ direct_total. A ratio of 1.0 = Shield adds zero overhead vs. direct. > 1.0 = Shield-side overhead.