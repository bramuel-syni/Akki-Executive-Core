# JC-MON Stage 3 close · GATE A verdict (deck exporter)

> **Source of truth:** `/app/memory/JC_MON_CANONICAL_SPEC.md` (Stage 3 close).
> **Cross-ref:** `/app/memory/JC_TL_CANONICAL_SPEC.md` § Stage 0 · S0-Q2 rubric.

**Closed 2026-06-25 · convergent FITS · divergent DOES-NOT-FIT · Track-2 dispatch REQUIRED.**

## What this is

At the close of JC-MON Stage 3, this is the standalone deck-exporter
**Gate A** verdict for the two render shapes:

- **Convergent** (load-bearing for Diagnosis / Develop-Strategy /
  Test-Hypothesis) — measured against the MYDAWA reference deck.
- **Divergent** (load-bearing for Get-Perspectives) — measured
  against the same rubric.

The verdict drives the Track-2 dispatch decision (Decks upgrade for
divergent rendering, separate dispatch).

## Verdict matrix

| Gate | Outcome | Source artifact |
|---|---|---|
| Convergent | **FITS** (7/8 YES · 1 PARTIAL · 0 NO) | `/app/memory/jc_artifacts/jc_mon/gate_a_verdict.md` |
| Divergent | **DOES-NOT-FIT** (5/8 YES · 2 PARTIAL · 1 NO + structural gap) | same |
| Track-2 dispatch | **REQUIRED** (minimum scope, divergent-only — NOT a Decks rebuild) | same |
| JC-MON Stage 3 → Gate A | **CLOSED** | this memo |

## What changed vs Stage 0 Q2

- **Convergent: still FITS, now cleaner.** Three latent
  attribute-reference defects in `pptx_exporter.py` (TensionSlide,
  TensionDeepDive, RiskMitigation — fixed during JC-TL Stage 1)
  closed during the fan-out. The convergent render is byte-clean
  post-fix.
- **Divergent: still DOES-NOT-FIT, structural gap unchanged.** The
  `ArtefactPayload` schema has no `perspective_spread` slot; the
  divergent render flattens persona views into the convergent
  `per_tension` slots and loses divergent semantics. Stage 2's
  provisional Get-Perspectives render is the Q6 floor pending
  Track-2 dispatch.

## Track-2 minimum scope (carried forward unchanged)

Per the standalone Gate A verdict + Stage 0 recommendation:

1. New `perspective_spread` slot in
   `services/solva_v2/artefact_schema.py` carrying:
   - `personas: List[PersonaView]` (name, view summary, evidence ids)
   - `agreement_map: List[AgreementCluster]` (statement + which personas back it)
   - `conflict_map: List[ConflictCluster]` (tension + opposing personas)
   - `blind_spots: List[BlindSpot]` (per-persona)
2. New pptx builder for the divergent-synthesis slide in
   `services/solva_v2/pptx_exporter.py` (~80-120 LOC, reusing
   the existing brand-token palette + grid geometry).
3. Path-aware Pydantic validator: convergent path forbids
   `perspective_spread`; divergent path forbids `scenarios[]` /
   `pathway[]`.

**NOT** a Decks rebuild. **NOT** a brand-token change. **NOT** a new
exporter. Schema extension + 1 builder + 1 validator.

## Sequencing decision

Track-2 dispatch is now UNBLOCKED. JC-MON Stage 3 closes here; the
prior recommendation to dispatch "AFTER JC-MON Stage 3, BEFORE any
Get-Perspectives shipping commitment" is now SATISFIED on the LHS.
Get-Perspectives ships at the Q6 provisional bar UNTIL Track-2 lands.

## Files touched

| File | Change | LOC delta |
|---|---|---|
| `backend/scripts/jc_mon_stage_3_gate_a_verdict.py` | NEW · standalone verdict producer (pptx inventory + 8-trait scoring + Track-2 decision) | +210 |

Zero changes to existing exporter or schema (Track-2 lands those).

## Artefacts

- `/app/memory/jc_artifacts/jc_mon/gate_a_verdict.md` — verdict markdown
- `/app/memory/jc_artifacts/jc_mon/gate_a_inventory.json` — machine-readable inventory of both decks + scoring summary
- Cited deck artefacts (already on disk from JC-TL Stages 1 + 2):
  - `/app/memory/jc_artifacts/JC-TL/01-diagnosis-proving-slice/deck.pptx` (convergent)
  - `/app/memory/jc_artifacts/JC-TL/02-fan-out/get-perspectives/deck.pptx` (divergent)
