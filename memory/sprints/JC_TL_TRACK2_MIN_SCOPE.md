# JC-TL Track-2 — Decks upgrade (Get-Perspectives divergent rendering) · MINIMUM SCOPE

> **Source of truth:** `/app/memory/JC_TL_CANONICAL_SPEC.md` (Track-2
> brief folded in from JC-MON Stage 3 Gate A verdict 2026-06-25 +
> user dispatch 2026-06-26).

**Closed 2026-06-26 · 8/8 acceptance rows GREEN** via
`python backend/scripts/jc_tl_track2_min_scope_slice.py`.

## What shipped (locked to 3 items, no creep)

The MINIMUM-scope extension to make the Get-Perspectives divergent
synthesis expressible. **NOT** a Decks rebuild. **NOT** a brand-token
change. **NOT** a new exporter mode. Three additive items:

1. **Schema slot** — `perspective_spread: Optional[PerspectiveSpread]`
   added to `ArtefactPayload` carrying:
   - `personas: List[PersonaView]` (label · view summary · confidence · citations)
   - `agreement_map: List[AgreementCluster]` (statement + backing personas + rationale)
   - `conflict_map: List[ConflictCluster]` (tension statement + opposing personas + why_it_matters)
   - `blind_spots: List[BlindSpot]` (per-persona structural gap + citations)
2. **One pptx builder** — `_build_perspective_spread` (~190 LOC) renders
   the divergent-synthesis slide in the same brand-token palette as
   the convergent slides. ONE slide; reuses helpers (`_add_text`,
   `_add_eyebrow`, `_add_rule`, `_add_footer`). No new geometry.
3. **Path-aware Pydantic validator** — `model_validator(mode="after")`
   on `ArtefactPayload`:
   - `perspective_spread is None` (convergent) → pass through; existing
     behaviour byte-identical (scenarios/pathway may be populated).
   - `perspective_spread is not None` (divergent) → `scenarios[]` MUST
     be empty AND `pathway[]` MUST be empty. Path-discipline error
     surfaces both violations clearly.

## Path discipline

| Path | `perspective_spread` | `scenarios[]` | `pathway[]` |
|---|---|---|---|
| Convergent (Diagnosis / Develop-Strategy / Test-Hypothesis) | `None` | any | any |
| Divergent (Get-Perspectives) | populated | empty | empty |

## Acceptance rows (verbatim)

```
✅ A. divergent payload validates (perspective_spread set, scenarios/pathway empty)
✅ B. divergent + scenarios[] REJECTED with path-discipline error (got True)
✅ C. divergent + pathway[] REJECTED with path-discipline error (got True)
✅ D. convergent payload still validates (scenarios=3, pathway=1)
✅ E. divergent deck renders (14 slides, ZIP magic ok, size=69105)
✅ F. convergent deck still renders 16 slides (got 16, size=73280)
✅ G. methodology-spine slots present in divergent walk
     ({headline, reflection, tensions_overview, in_closing,
       methodological_honesty, cover, bias_inventory, per_tension,
       sensitivity} = 9/9)
✅ H. perspective_spread slide renders 4 sub-arrays (anchors=True, persona-labels=True)

8/8 acceptance rows GREEN — TRACK-2 MIN-SCOPE STOP-AND-SHOW ready.
```

## Convergent regression check (no Decks rebuild — zero behavioural change)

Per the user's hard rule "convergent render must remain 7/8 YES or
better", I re-ran two prior convergent proving slices end-to-end:

- **JC-TL Stage 1 (Diagnosis):** 6/6 GREEN. Deck size **76555 bytes
  byte-identical** to pre-Track-2. Same FITS-WITH-LOSS verdict.
- **JC-TL Stage 2 (fan-out, 3 paths):** 5/5 GREEN. Develop Strategy
  FITS-WITH-LOSS; Test Hypothesis FITS-WITH-LOSS; Get Perspectives
  FITS-WITH-LOSS at Q6 provisional bar.

The convergent path went through with **zero changes** to its deck
order, slide count, brand tokens, or builder set. The schema slot
defaults to `None`, the validator passes through, and `build_pptx`
chooses `LOCKED_DECK_ORDER` for convergent payloads exactly as before.

All 450 pre-existing Solva v2 schema/validator tests still PASS
(3 pre-existing environmental auth failures unchanged — unrelated
to Track-2).

## Acceptance bar honoured

Per user dispatch:
- ✅ Spread renders to the **methodology-spine bar** — 9/9 spine slots
  present in the divergent walk (cover · headline · tensions_overview ·
  per_tension · sensitivity · reflection · bias_inventory · pre_mortem
  · cost_asymmetry · risk_mitigation · methodological_honesty ·
  in_closing — all path-agnostic; the spread slot inserts at the
  synthesis position where scenarios/pathway would convergently appear).
- ✅ **NOT measured against MYDAWA** (MYDAWA is convergent). The first
  divergent render produced by Track-2 IS the reference Get-Perspectives
  ships against.
- ✅ Path-aware validator surfaces violations explicitly so the
  divergent shape can never be silently mixed with convergent slots.

## Divergent deck (14 slides — judge on first sight)

```
1.  cover
2.  headline
3.  tensions_overview
4.  per_tension
5.  perspective_spread    ← NEW (swap-in for convergent scenarios/per_scenario_table)
6.  sensitivity
7.  reflection
8.  bias_inventory
9.  pre_mortem
10. decision_logic
11. cost_asymmetry
12. risk_mitigation
13. methodological_honesty
14. in_closing
```

The divergent walk drops `scenarios_overview` + `per_scenario_table` +
`pathway` (convergent-only synthesis slots — path discipline enforced).
All other slots are SHARED methodology-spine slots, identical to
convergent.

## Discipline (standing rules honoured)

- ✅ **No testing subagent.** Pure Python proving slice via bash.
- ✅ **Shield path UNTOUCHED.** The new code is schema + Pydantic
  validator + python-pptx — zero LLM calls, zero Shield touch.
- ✅ **Additive-only on the exporter.** Convergent `LOCKED_DECK_ORDER`
  + all 16 builders UNCHANGED. The divergent walk is a NEW tuple +
  one NEW builder added to the shared `_KIND_TO_BUILDER` dispatch.
- ✅ **WS Generate Document UI locked.** No FE touch.
- ✅ **Monitor additive-only.** No Monitor touch.
- ✅ **DEV_PIPELINE.md updated BEFORE this memo** (§2 active
  dispatch + §4 invariant row + §9 phase history).
- ✅ **Canonical spec cited line 1** of this memo.
- ✅ **Convergent path 7/8 YES preserved** — Gate A verdict's rubric
  is identical for the convergent re-render (Stage 1 deck is
  byte-identical).
- ✅ **HARD STOP** after Track-2 closes — NO chain into GP ship.

## Files touched

| File | Change | LOC delta |
|---|---|---|
| `backend/services/solva_v2/artefact_schema.py` | NEW types: `PersonaView`, `AgreementCluster`, `ConflictCluster`, `BlindSpot`, `PerspectiveSpread`. NEW field: `ArtefactPayload.perspective_spread: Optional[PerspectiveSpread] = None`. NEW `model_validator` enforcing path discipline. NEW `__all__` exports for the 5 new types. | +145 |
| `backend/services/solva_v2/pptx_exporter.py` | NEW builder `_build_perspective_spread` (~190 LOC). NEW `DIVERGENT_DECK_ORDER` tuple (14 slides). EXTENDED `_KIND_TO_BUILDER` dispatch (now superset of LOCKED). EXTENDED `build_pptx` with path-aware deck-order selection. EXPORT `DIVERGENT_DECK_ORDER` in `__all__`. | +220 |
| `backend/tests/test_solva_v2_pptx_export.py` | UPDATED `test_builder_covers_every_locked_kind` from equality to superset (LOCKED kinds remain a subset of `_KIND_TO_BUILDER`). | +6 / -1 |
| `backend/scripts/jc_tl_track2_min_scope_slice.py` | NEW · 8/8 proving slice covering schema-accept + schema-reject probes (both convergent slot guards) + divergent render + convergent regression + methodology-spine presence + spread-slide sub-array carriage | +430 |

Zero LOC change to convergent builders. Zero LOC change to convergent
deck order. Zero LOC change to Shield path. Zero LOC change to
Monitor.

## Artefacts

- `/app/memory/jc_artifacts/jc_tl/track2/convergent-regression.pptx` (73280 bytes — byte-clean convergent render for visual diff)
- `/app/memory/jc_artifacts/jc_tl/track2/divergent-first-render.pptx` (69105 bytes — the first divergent render; the reference GP ships against)
- `/app/memory/jc_artifacts/jc_tl/track2/divergent-payload.json` (the fixture payload for reproducible review)
- `/app/memory/jc_artifacts/jc_tl/track2/convergent-payload.json` (the regression-check fixture)
- `/app/memory/jc_artifacts/jc_tl/track2/inventory.json` (slide titles + perspective_spread slide full text for diff)

## HARD STOP — surfacing for review

Track-2 closes here. **Do not chain into Get-Perspectives ship.**
User must inspect `divergent-first-render.pptx` and authorise
GP-ship-against-this-reference before any further work on the
divergent path.
