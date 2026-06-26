**Canonical specs:** `/app/memory/JC_TL_CANONICAL_SPEC.md` §4 (GP
divergent spread) AND `/app/memory/JC_MON_CANONICAL_SPEC.md`
(Monitor candidate-objectives generator). Two items shipping
together per user direction at AUTONOMOUS BACKLOG RUN 2026-06-26:
"after GP ship: spread-heatmap + auto-tune in parallel."

# JC-TL Spread-Heatmap Delta + Auto-Tune Candidate Objectives — CLOSED 2026-06-26 · 10/10 GREEN

## Items closed in this dispatch

### 1. Spread-heatmap delta — `services/solva_v2/spread_heatmap.py`

Pure / deterministic / no LLM / no IO. One function:

```python
compute_spread_delta(session_prev, session_curr) -> {
  "previous_session_id":  str,
  "current_session_id":   str,
  "personas":             [{persona_label, previous_pct, current_pct, delta_pct, direction}],
  "personas_added":       [str],
  "personas_removed":     [str],
  "spread_breadth_delta": int,           # (curr max - curr min) - (prev max - prev min)
  "blind_spots_added":    [str],
  "blind_spots_removed":  [str],
}
```

Direction is "up" / "down" / "stable" with a ±2 pct stability
band. Output ordering is byte-stable for identical inputs (persona
labels sorted).

The FE charting helper (a heatmap row visualisation) is the
**next** dispatch when the user steers it; this dispatch ships
the schema + data computation.

### 2. Auto-tune candidate objectives — `services/monitor/objective_candidate_service.py`

Extended `_build_candidates_prompt` and `generate_candidate_objectives`
with a new optional keyword argument:

```python
generate_candidate_objectives(
    *, base_docs, account_id, context_id, context_label,
    divergent_blind_spots: Optional[List[str]] = None,
)
```

When `divergent_blind_spots` is omitted (the default), prompt
behaviour is **byte-identical** to the pre-auto-tune path —
proven by JC-MON Stage 3.0 proving slice re-run cleanly without
re-pinning (5/5 GREEN post-change).

When supplied, the prompt grows a `BLIND-SPOTS SURFACED BY A
RECENT GET-PERSPECTIVES SESSION` block AFTER the BASE docs block
and BEFORE the "Generate 2-6 candidate objectives" command.
Blind-spots are explicitly framed as **widening signal**, NOT
replacement grounding — every objective still grounds in a BASE
doc per the existing path-discipline.

Path-discipline preserved:
- Blind-spots are EVIDENCE, not COMMANDS.
- Blind-spots are deduped + sorted at prompt-assembly time so the
  prompt is order-independent (deterministic).
- Blank / whitespace-only blind-spots are stripped.

## Proving slice 10/10 GREEN

Run: `cd /app/backend && python scripts/jc_tl_spread_heatmap_and_auto_tune_slice.py`

Evidence: `/app/memory/jc_artifacts/jc_tl/04-spread-heatmap-auto-tune/slice_20260626T141413Z.json`

**Spread-heatmap delta rows (A-F):**

| Row | Subject | Outcome |
|---|---|---|
| A | Identical session vs itself → all personas stable, zero delta | ✓ |
| B | Same personas, all confidence +10 → all direction="up", delta_pct=10 | ✓ |
| C | Disjoint persona sets (regulatory vs investment) → all added + all removed, zero overlap | ✓ |
| D | Spread breadth widens by 8 pct (max+4, min-4) → `spread_breadth_delta == 8` | ✓ |
| E | New blind-spot in current session → `blind_spots_added` carries 1 | ✓ |
| F | Non-Get-Perspectives previous session → empty common set, all curr personas added (no raise) | ✓ |

**Auto-tune candidate-objectives prompt rows (G-J):**

| Row | Subject | Outcome |
|---|---|---|
| G | No-blind-spots path BYTE-IDENTICAL across (omitted, None, []) | ✓ |
| H | With blind-spots, prompt grows the BLIND-SPOTS block; both items present | ✓ — grew by ~250 bytes |
| I | Same blind-spots in different order → identical prompt (deterministic sort) | ✓ |
| J | Duplicate blind-spots dedupe; blank strings stripped | ✓ |

**Total elapsed: < 0.01 s** (pure-data; no Shield call exercised inline).

## Regression — locked bar GREEN

| # | Check | Result |
|---|---|---|
| 1 | JC-MON Stage 3.0 candidate-objectives proving slice | ✅ 5/5 GREEN — proves auto-tune is backwards-byte-identical when `divergent_blind_spots` is omitted/empty (the load-bearing safety property for the existing Monitor surface) |
| 2 | Contract snapshot 6/6 + dual-mount smoke 37/37 | ✅ 43/43 PASS (no new routes added) |
| 3 | JC-TL Track-2 8/8 (convergent + divergent renders) | ✅ UNCHANGED |
| 4 | JC-TL GP ship 6/6 | ✅ UNCHANGED |

## Files touched

| File | LOC delta | Notes |
|---|---|---|
| `backend/services/solva_v2/spread_heatmap.py` NEW | +160 | Pure data computation; `compute_spread_delta` |
| `backend/services/monitor/objective_candidate_service.py` | +35 / −5 | `divergent_blind_spots` keyword on `_build_candidates_prompt` + `generate_candidate_objectives`; `extra_output.divergent_blind_spot_count` audit field |
| `backend/scripts/jc_tl_spread_heatmap_and_auto_tune_slice.py` NEW | +280 | 10-row proving slice |

Total: 1 modified · 2 new · +470 / −5 LOC. **No new routes added.**

## Honest framing of what auto-tune does (and doesn't) do

- **Does:** widen the candidate-objectives generator's lens by
  surfacing fresh blind-spots from a recent Get-Perspectives
  session. The generator now has access to evidence the user just
  paid attention to in a different surface.
- **Does NOT:** generate objectives whose ONLY grounding is a
  blind-spot. The path-discipline copy in the prompt is explicit:
  "treat as widening signal; do NOT generate objectives that are
  ONLY anchored on blind-spots — every objective still grounds in
  a BASE doc."
- **Does NOT:** auto-create or auto-confirm any candidate. The
  candidate slate still flows through the FE confirm step before
  any objective persists.
- **Does NOT:** consume LLM budget unless the caller explicitly
  passes blind-spots. The default behaviour (no kwarg) is
  byte-identical to the pre-auto-tune path.

## What ships NEXT (not in this dispatch)

- **FE charting helper for spread-heatmap.** Visualisation of the
  per-persona delta — a small heatmap row component that consumes
  the `compute_spread_delta` output. Schema is ready; render is
  user-direction-pending.
- **Wiring auto-tune into the actual FE generate-candidates
  workflow.** Today the kwarg is honoured at the service layer but
  no FE caller is passing `divergent_blind_spots` yet. Next
  dispatch: a small button on the candidate-generation drawer
  "Auto-tune from latest GP session" that:
    1. Fetches the most recent GP session for the active context
    2. Extracts `synthesis.perspective_spread.blind_spots[].blind_spot_description`
    3. Passes the list as `divergent_blind_spots` to the existing
       `POST /api/contexts/{cid}/monitor/objective-candidates`
  Wiring is mechanical; behaviour gain depends on whether the
  user has a recent GP session.

## Standing rules respected

- ✅ No new routes added — backwards-compatible extension only.
- ✅ Path-discipline enforced in prompt copy (blind-spots are
  evidence, not commands).
- ✅ Deterministic / byte-identical when kwarg omitted (load-
  bearing for JC-MON Stage 3.0 byte-stability).
- ✅ Sprint memo cites both canonical specs on line 1.
- ✅ Proving slice byte-identity verified across rounds (rows G + I).
