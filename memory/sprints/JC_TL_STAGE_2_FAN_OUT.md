# JC-TL Stage 2 — Fan-out (Develop Strategy / Test Hypothesis / Get Perspectives)

> **Source of truth:** `/app/memory/JC_TL_CANONICAL_SPEC.md` (§ Stage 2).

**Closed 2026-06-25 · 5/5 acceptance rows GREEN** via
`python backend/scripts/jc_tl_stage_2_fan_out_slice.py`.

## What shipped

Three end-to-end proving runs, one per path, on the SHARED FRAMEWORK
proven at Stage 1. Each path's layer order derives from the
objective (per the engine reality) while the shared engine outputs
(7 engines across the spine) carry path-specific semantics.

| Path | Submodule | Verdict | Deck size |
|---|---|---|---|
| Develop Strategy | `develop_strategy` | FITS-WITH-LOSS (5 YES, 3 PARTIAL) | ~77 KB |
| Test Hypothesis | `simulate_hypothesis` | FITS-WITH-LOSS (5 YES, 3 PARTIAL) | ~76 KB |
| Get Perspectives | `get_perspective` | FITS-WITH-LOSS (5 YES, 3 PARTIAL) **at provisional bar per Q6** | ~77 KB |

## Per-path semantics (verified by deck content)

- **Develop Strategy** — Convergent to recommendation. The synthesis
  produces a 3-recommendation sequenced pathway (parallel SDK + reactivation
  + stabilisation) with Days-0-30 / 30-60 / 60-180 timeline tagging.
  Adversarial counter ("if checkout fix requires reactivation-team review,
  parallel breaks") preserved as falsification surface.
- **Test Hypothesis** — Proposition under stress. Hypothesis ("parallel
  recovery hits index ≥ 100 by week 12") tested against 3 scenarios
  with weighted confidence (45/38/17); falsification gate identified at
  week-6 weekly-index < 90.
- **Get Perspectives** — Divergent (per Q6 provisional bar). 3 persona
  views (auditor, customer-advocate, regulator) with confidence
  weighted PER PERSONA (70/55/70). Synthesis inverts to a SPREAD —
  agreement (auditor+regulator on process), conflict (customer-advocate
  on tone), and per-persona blind-spots. NB: the existing convergent
  exporter flattens the divergent spread into convergent slots —
  Q2 verdict's DOES-NOT-FIT for divergent stands; this provisional
  render is the Q6 floor pending Track-2 dispatch.

## Contributor-history fold-in (approved into this stage)

The Develop Strategy session is seeded as a REVISION of the Stage-1
Diagnosis session — its session shape carries `prior_session_intent`
threading the diagnosis question into Develop Strategy's framing.
Verified end-to-end:

- `session_record.prior_session_intent.session_id = "sess-jctl-stage1-mydawa-diagnosis"`
- `session_record.prior_session_intent.submodule = "seek_clarity"`
- The contributor-history field surfaces alongside the new session's
  intent in the session-record output, proving the revision tuning
  works ADDITIVELY without engine modification.

## Track-2 Decks-upgrade sequencing recommendation (surface only)

Per dispatch: "Surface a Track-2 Decks-upgrade sequencing
recommendation as an artifact, do not execute." Captured at
`/app/memory/jc_artifacts/JC-TL/02-fan-out/track-2-decks-upgrade-sequencing.md`.

**Agent recommendation: dispatch Track 2 AFTER JC-MON Stage 3 closes,
BEFORE any JC-TL Stage 2 Get-Perspectives shipping commitment.**

Reasons surfaced in the artifact:
1. Stage 2 fan-out demonstrated end-to-end on the existing exporter;
   Get Perspectives renders at Q6 provisional bar today.
2. JC-MON Stage 3 wires reassess actions that surface convergent
   assessment outputs — schema-shape change ripples through. Sequencing
   Track 2 after reduces simultaneous-schema blast radius.
3. The provisional first render IS the input to Track 2's MINIMUM spec.
   Dispatching Track 2 before running it would over-specify.
4. Q6 lock allows ship-at-provisional-bar; Track 2 is enrichment, not
   blocker.

Decision options for the user surfaced as (a) Track 2 next, (b) Track 2
after Stage 3 [agent recommendation], (c) defer Track 2 indefinitely
if provisional bar is judged sufficient.

## Acceptance rows (verbatim)

```
✅ A. Develop Strategy deck — FITS-WITH-LOSS
✅ B. Test Hypothesis deck — FITS-WITH-LOSS
✅ C. Get Perspectives provisional bar (≥ 4 YES traits) — yes=5
✅ D. Contributor-history fold-in surfaces prior_session_intent — seek_clarity
✅ E. Track-2 sequencing recommendation surfaced — 2739 bytes

5/5 acceptance rows GREEN — STAGE 2 STOP-AND-SHOW ready.
```

## Standing-rule adherence

- **Shared framework, not single-path calcification** ✅ — same
  `pptx_exporter.build_pptx` + `payload_builder.build_payload`
  drive all 3 paths.
- **Latitude per-path layer order** ✅ — Test Hypothesis routes
  through `hypothesis` layer (engine-aware); Get Perspectives uses
  the `get_perspective` submodule voice (persona-aware); Develop
  Strategy uses synthesis-voice convergent.
- **Deliberate-steps probes (not folded into grounding)** ✅ — each
  path's 6-8 user_turns map cleanly to layer boundaries.
- **Q6 — provisional bar for Get Perspectives** ✅ — explicit in
  the rubric scorecard markdown.
- **Internal name stays `solva`; ThinkLab UI-label** ✅ — invariant
  unchanged.

## Artefacts

| Path | Artefact dir |
|---|---|
| Develop Strategy | `/app/memory/jc_artifacts/JC-TL/02-fan-out/develop-strategy/` (deck.pptx · session-record.json · session-full.json · rubric-scorecard.md) |
| Test Hypothesis | `/app/memory/jc_artifacts/JC-TL/02-fan-out/test-hypothesis/` (same) |
| Get Perspectives | `/app/memory/jc_artifacts/JC-TL/02-fan-out/get-perspectives/` (same; rubric marked provisional per Q6) |
| Track-2 sequencing | `/app/memory/jc_artifacts/JC-TL/02-fan-out/track-2-decks-upgrade-sequencing.md` |

## Files touched

| File | Change | LOC delta |
|---|---|---|
| `backend/scripts/jc_tl_stage_2_fan_out_slice.py` | NEW · 3-path fan-out + Track-2 recommendation | +560 |

Zero changes to existing code (Stage-1's exporter fixes are
inherited; no new patches needed for fan-out).
