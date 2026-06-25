# JC-TL Track 2 — Decks-upgrade sequencing recommendation

> **Surface-only artifact.** This recommendation is NOT a dispatch.
> The user decides when to dispatch Track 2; the agent only surfaces
> the sequencing analysis.

## Recommendation: dispatch Track 2 AFTER JC-MON Stage 3 closes, BEFORE any JC-TL Stage 2 Get-Perspectives shipping commitment.

### Why this sequencing?

1. **Stage 2 fan-out has been demonstrated on the existing exporter.**
   Develop Strategy and Test Hypothesis ride the convergent track
   unmodified (Track 1). Get Perspectives ALSO renders through the
   existing exporter today — at the Q6 provisional bar — but the
   `perspective_spread` slot is not represented, so divergent
   semantics are flattened. Stage 0 Q2 captured this as the
   DOES-NOT-FIT verdict.

2. **JC-MON Stage 3 has higher load-bearing weight on the existing
   exporter.** Stage 3 wires reassess actions into the Monitor drawer
   that surface the convergent assessment outputs. Any Track-2
   schema extension that changes the `ArtefactPayload` Pydantic shape
   ripples through the JC-MON consumer at the same time. Sequencing
   Track 2 AFTER Stage 3 reduces the simultaneous-schema-change
   blast radius.

3. **The Get-Perspectives provisional first render (this Stage 2)
   IS the input to Track 2's spec.** First-render judgment informs
   the MINIMUM schema surface Track 2 actually needs. Dispatching
   Track 2 BEFORE running the provisional renders would over-specify.

4. **The Q6 lock allows ship-at-provisional-bar.** Get Perspectives
   does not block on Track 2 to SHIP — only to ship at "the
   MYDAWA-grade bar." The user can defer Track 2 indefinitely if the
   provisional first render is judged sufficient on its own merits.

### Proposed Track-2 scope (per Stage 0 Q2 verdict; do not execute)

- New schema slot in `ArtefactPayload`:
  `perspective_spread`, carrying `personas[] / agreement_map[] /
  conflict_map[] / blind_spots[]`.
- New pptx builder in `services/solva_v2/pptx_exporter.py` for the
  divergent-synthesis slide. Reuses brand tokens + slide geometry;
  no new architecture.
- Path-aware Pydantic validator: convergent forbids
  `perspective_spread` set; divergent forbids `scenarios[]` /
  `pathway[]` set.

### Decision points for the user

- **(a)** Dispatch Track 2 next, before JC-MON Stage 3. *Risk: schema
  ripple into Stage 3 consumer; mitigation possible but adds
  coordination.*
- **(b)** Dispatch Track 2 after JC-MON Stage 3, before any
  Get-Perspectives shipping commitment. **AGENT RECOMMENDATION.**
  Reasons above.
- **(c)** Ship Get Perspectives at the provisional bar (Q6) and
  defer Track 2 indefinitely. Justified if the first render is
  judged deck-grade as-is.
