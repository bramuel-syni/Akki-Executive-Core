**Canonical spec:** `/app/memory/JC_TL_CANONICAL_SPEC.md` §4 (GET
PERSPECTIVES — divergent outlier; synthesis INVERTS to a spread of
multiple persona views). Ships against the Track-2 divergent
first-render approved by user 2026-06-26 ("ok for now").

# JC-TL Get-Perspectives ship — CLOSED 2026-06-26 · 6/6 GREEN

## What ships

The deterministic divergent payload builder + a 3-fixture proving
slice that renders byte-stably across two consecutive runs.

The convergent path is **unchanged**; the divergent path lives on
the Track-2 schema (`perspective_spread` + path-aware validator)
that shipped 2026-06-26. This dispatch adds the engine bridge:

  ```
  session  ──build_divergent_payload──▶  ArtefactPayload  ──build_pptx──▶  .pptx bytes
                  ^                                                          ^
                  │                                                          │
            new in this dispatch                       Track-2 (already shipped 2026-06-26)
  ```

`build_divergent_payload(session, context_name)`:
- PURE (no DB, no LLM, no IO)
- DETERMINISTIC (same input → identical output across N runs)
- PATH-DISPATCH at the top of the existing `build_payload`:
  `submodule in {"get_perspective", "get-perspectives"}` delegates
  to the divergent builder; everything else stays on the convergent
  path. **Convergent path behaviour unchanged.**
- Reads from `session.synthesis.{perspective_spread, headline,
  tensions, reflection_section, methodological_honesty, in_closing,
  bias_inventory, pre_mortem, cost_asymmetry, sensitivity_inputs,
  risk_mitigation, decision_logic, per_tension_deep_dive}`. The
  shape mirrors the convergent builder's session contract; only
  `perspective_spread` is divergent-specific.

## Proving slice 6/6 GREEN

Run: `cd /app/backend && python scripts/jc_tl_gp_ship_slice.py`

Evidence: `/app/memory/jc_artifacts/jc_tl/03-gp-ship/evidence/slice_20260626T140046Z.json`

| Row | Subject | Outcome |
|---|---|---|
| A | `build_divergent_payload` accepts 3 representative sessions; each produces a payload with `scenarios=[]`, `pathway=[]`, `perspective_spread` populated | ✓ |
| B | `build_pptx` renders all 3 in the divergent deck order (14 slides per `DIVERGENT_DECK_ORDER`); output is a valid PPTX (PK magic header) | ✓ |
| C | **Byte-stable across two consecutive renders, per session** (load-bearing user requirement: "no nondeterminism in the synthesis path") | ✓ — `run1_bytes == run2_bytes` for all 3 fixtures |
| D | Path-discipline validator REJECTS a cross-path payload (`perspective_spread` set AND `scenarios` non-empty) | ✓ — validator raises with `"must not carry scenarios[]"` |
| E | 9 methodology-spine slots present in all 3 renders (cover · headline · tensions · reflection_section · methodological_honesty · in_closing · bias_inventory · pre_mortem · cost_asymmetry) | ✓ |
| F | Across 3 personas per session, each persona has a DISTINCT blind-spot label (spread surfaces the gaps each lens cannot see) | ✓ |

**Total elapsed: 0.59 s.**

## Three representative renders

| Slug | Bytes | Personas | Operating question |
|---|---:|---|---|
| `regulatory.pptx` | 68 204 | Auditor · Regulator · Customer advocate | Regulatory action response |
| `investment.pptx` | 68 336 | Founder · CFO · VC partner | Series B raise readiness |
| `launch.pptx` | 68 234 | Product manager · Engineering lead · Sales lead | Q3 product launch readiness |

The bytes-on-disk are within ~150 bytes of each other — same slide
count + same renderer + scenario-specific text variation accounts
for the small delta. Each individually is byte-stable across runs.

## Live download URLs (superadmin only, for user review)

```
GET /api/jc-artifacts/gp-ship/regulatory.pptx
GET /api/jc-artifacts/gp-ship/investment.pptx
GET /api/jc-artifacts/gp-ship/launch.pptx
```

Route registered at `backend/routers/jc_artifacts.py`. Superadmin
gate enforced. Surface ratchet rolled forward to absorb the new
route: `/api/* = 9aa905f6d951f2a8` · `/v1/* = 6ce751ef812f6816` ·
combined `4f050f7e95b8dd10`. 43/43 contract-snapshot + dual-mount
tests GREEN.

## Probe authoring evidence (S0-Q4 lock)

User watchpoint, verbatim: "if the other three paths' probes need
authoring and that gets reported as 'done' without the actual
probe content shown, that's the quality hole."

The 15 GP probes are authored, in writing, at
`/app/memory/audit/JC_TL_GP_PROBES.md`:

- **L0 framing (3 probes)** — gather the persona set; surface what
  convergence would lose.
- **L1 grounding (3 probes per persona)** — what each persona
  notices, what each cannot see, whose evidence each trusts first.
- **L2 triangulation + tension (3 probes)** — where personas
  converge, where they structurally disagree, which persona
  cannot be triangulated.
- **L3 synthesis-divergent (3 probes)** — structural blind-spot
  per persona, what the spread itself says, refusal-to-converge
  test.
- **L4 reflection (3 probes)** — what would shift the spread,
  cost of premature convergence, steel-man against the spread.

Engine-call mapping table is in the same document, citing the
existing Solva primitives (`frame_audit`, `triangulation`,
`tension_detector`, `meta_synthesis`, `probability_weighting`,
`refuse_to_decide`). Every engine call is Shield-routed under the
standard Solva surface (`solva_v2.synthesis_*` family).

## Out of scope (deferred to next dispatch)

- **LLM-driven GP synthesis.** This dispatch ships the
  deterministic builder + 3 hand-curated fixtures. The
  next dispatch (`LLM-DRIVEN-GP-SYNTHESIS`) wires the L0–L4 probes
  to a Shield-routed LLM call that takes user turns through the
  probe sequence and emits the `perspective_spread` block. That
  dispatch will move the byte-stability ratchet (LLM outputs are
  model-stable, not byte-stable across model swaps) and gets its
  own forward-to-a-board subjective verification.

- **Spread-heatmap delta** (per-persona `confidence_pct` drift
  across consecutive GP sessions). Newly unblocked by this ship;
  next dispatch.

- **Auto-tune candidate objectives from divergent-spread** (persona
  blind-spots feed into MON 3.0's `generate_candidate_objectives`).
  Newly unblocked by this ship; parallel dispatch with
  spread-heatmap.

## Convergent regression — locked bar GREEN

| # | Check | Result |
|---|---|---|
| 1 | Contract snapshot 6/6 + dual-mount smoke 37/37 (post-ratchet-roll) | ✅ 43/43 PASS |
| 2 | JC-TL Track-2 8/8 (convergent 73 280 + divergent first-render 69 105 bytes) | ✅ UNCHANGED |
| 3 | Solva v2 artefact_schema + pptx_export | ✅ 25/25 PASS |

Stage 1 Diagnosis deck byte-identity at 76 555 bytes is **not
touched** in this dispatch — the divergent path is a separate
codepath in `build_payload`'s dispatch top, with the convergent
path unchanged.

## Files touched

| File | LOC delta | Notes |
|---|---|---|
| `backend/services/solva_v2/payload_builder.py` | +110 / −0 | `build_divergent_payload` + path dispatch in `build_payload` + import of `BiasInventorySection` + `PerspectiveSpread` |
| `backend/routers/jc_artifacts.py` | +50 / −0 | `/gp-ship/{filename}` route + 3 whitelist entries |
| `backend/tests/test_phase4_4_dual_mount_smoke.py` | +3 / −3 | Surface-ratchet roll |
| `backend/scripts/jc_tl_gp_ship_slice.py` NEW | +560 | Proving slice — 3 fixtures · 6 acceptance rows · byte-stability check |
| `memory/audit/JC_TL_GP_PROBES.md` NEW | +180 | Authored probe content (S0-Q4 lock evidence) |
| `memory/jc_artifacts/jc_tl/03-gp-ship/*.pptx` NEW × 3 | — | 3 representative divergent renders |

Total: 3 modified · 4 new (1 file + 3 artefacts) · +903 / −3 LOC.

## What this dispatch deliberately does NOT touch

- **Convergent path** (`build_payload` body where
  `submodule != "get_perspective"`) — unchanged. The Stage 1
  76 555-byte byte-identity ratchet is intact.
- **Track-2 schema** (`perspective_spread` + path-aware validator
  + divergent renderer + 14-slide divergent order) — shipped
  2026-06-26 in `JC_TL_TRACK2_MIN_SCOPE.md`; this dispatch
  consumes that contract unchanged.
- **Stage 1 / Stage 2 fan-out fixtures** in
  `scripts/jc_tl_stage_*_slice.py` — independent fixture sets;
  not consumed by GP ship.

## HARD STOP

This dispatch is the engine bridge with deterministic synthesis.
The LLM-driven persona-spread synthesis is the next dispatch and
will get its own quality-regression check.
