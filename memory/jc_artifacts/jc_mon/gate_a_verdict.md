# JC-MON Stage 3 close · GATE A verdict (deck exporter for BOTH renders)

> **Source of truth:** `/app/memory/JC_MON_CANONICAL_SPEC.md` (Stage 3 close)
> **Cross-ref:** `/app/memory/JC_TL_CANONICAL_SPEC.md` § Stage 0 · S0-Q2 rubric (8 traits)
> **Produced:** 2026-06-26 04:36 UTC
> **Reference deck:** `/app/memory/reference_assets/MYDAWA_Reference_Deck.pptx`
> Reference slide count: 13 · 442922 bytes

**At the close of JC-MON Stage 3, this is the deck-exporter Gate A
verdict for the two render shapes. The convergent render is the load-bearing
output of Diagnosis / Develop-Strategy / Test-Hypothesis paths; the divergent
render is the load-bearing output of Get-Perspectives. The Gate A verdict
drives the Track-2 dispatch decision (Decks upgrade for divergent rendering).**

---

## 1 · Rendered decks (post-Stage 1 + Stage 2 + pptx_exporter bug fixes)

| Render | Path | Slides | Size (bytes) |
|---|---|---|---|
| Convergent (Diagnosis) | `/app/memory/jc_artifacts/JC-TL/01-diagnosis-proving-slice/deck.pptx` | 16 | 76555 |
| Divergent (Get-Perspectives) | `/app/memory/jc_artifacts/JC-TL/02-fan-out/get-perspectives/deck.pptx` | 16 | 76881 |

## 2 · Convergent verdict (Diagnosis / Develop-Strategy / Test-Hypothesis)

| # | Trait | Verdict | Evidence |
|---|---|---|---|
| 1 | Bold sans-serif typography hierarchy | **YES** | Brand tokens unchanged; INK + NED_PURPLE + EYEBROW_RED preserved. |
| 2 | Monochrome palette + signal colors only on data | **YES** | Solid colors only; signal accents on data. |
| 3 | Narrative-vs-evidence side-by-side layout | **YES** | tensions_overview + per_tension frame/evidence/implication triplets now render correctly (post-fix). |
| 4 | Per-cluster confidence weighting visible | **YES** | Per-scenario weight_pct + confidence_pct rendered as percentages. |
| 5 | Bridge decompositions / indicator timelines | **YES** | pathway[] TimelineTag literals render Days 0-30 / 30-60 / 60-180. |
| 6 | "Reflection — Not for the Deck" slide equivalent | **PARTIAL** | Reflection slot present; verbatim 'Not for the Deck' copy is a copy-edit, not a schema gap. |
| 7 | "Fair Criteria" slide equivalent | **YES** | methodological_honesty element renders position 14. |
| 8 | Refusal-to-decide explicit on the surface | **YES** | CONSTRAINT_PREAMBLE rule #3 forbids directive copy; integrity validator rejects. |

**Overall convergent verdict: FITS.** 7 YES · 1 PARTIAL · 0 NO. The PARTIAL is a copy-treatment polish, not a structural gap. Pptx_exporter bug fixes shipped during Stage 1 closed three latent attribute-reference defects (TensionSlide.summary, TensionDeepDive title/evidence/observation, RiskMitigation.risk_name/.mitigation_strategy) — the convergent render is now byte-clean.

## 3 · Divergent verdict (Get-Perspectives)

| # | Trait | Verdict | Evidence |
|---|---|---|---|
| 1 | Bold sans-serif typography hierarchy | **YES** | Same exporter, same brand palette. |
| 2 | Monochrome palette + signal colors only on data | **YES** | Same palette. |
| 3 | Narrative-vs-evidence side-by-side layout | **PARTIAL** | per_tension slot co-opted for persona-vs-evidence; semantically misrepresents the spread. |
| 4 | Per-cluster confidence weighting visible | **PARTIAL** | Confidence per-scenario today; needs per-persona + cross-persona agreement maps. |
| 5 | Bridge decompositions / indicator timelines | **NO** | Divergent artefacts have voices-as-of-now, not timelines. |
| 6 | "Reflection — Not for the Deck" slide equivalent | **YES** | Reflection layer is path-agnostic. |
| 7 | "Fair Criteria" slide equivalent | **YES** | Methodological honesty applies regardless. |
| 8 | Refusal-to-decide explicit on the surface | **YES** | CONSTRAINT_PREAMBLE rule #3 still binds. |

**Overall divergent verdict: DOES-NOT-FIT (structurally).** 5 YES · 2 PARTIAL · 1 NO. The structural gap from Stage 0 is UNCHANGED: the existing `ArtefactPayload` schema has no `perspective_spread` slot, so the divergent render flattens persona views into the convergent `per_tension` slots and loses the divergent semantics. Stage 2's provisional Q6 render is the Q6 floor pending Track-2 dispatch.

## 4 · Track-2 decision (the load-bearing output of Gate A)

Per the JC-TL canonical spec's Stage-0 decision rules + the JC-MON Stage-3-close requirement to drive the Track-2 dispatch:

- **Convergent FITS** → no Decks change required for convergent paths.
- **Divergent DOES-NOT-FIT** → **TRACK-2 DISPATCH REQUIRED.**

**Minimum scope for Track-2 (NOT a Decks rebuild):**

1. New `perspective_spread` slot in `services/solva_v2/artefact_schema.py` carrying `personas: List[PersonaView]` (name, view summary, evidence ids), `agreement_map: List[AgreementCluster]` (statement + which personas back it), `conflict_map: List[ConflictCluster]` (tension + opposing personas), `blind_spots: List[BlindSpot]` (per-persona).
2. New pptx builder for the divergent-synthesis slide in `services/solva_v2/pptx_exporter.py` (one builder, ~80-120 LOC, reusing the existing brand-token palette + grid geometry).
3. Path-aware Pydantic validator: convergent path forbids `perspective_spread`; divergent path forbids `scenarios[]` / `pathway[]`. Schema-level integrity.

**Sequencing:** Track-2 dispatch is now UNBLOCKED. JC-MON Stage 3 is closing here; the prior recommendation to dispatch "AFTER JC-MON Stage 3, BEFORE any Get-Perspectives shipping commitment" is now SATISFIED on the LHS. Get-Perspectives ships at the Q6 provisional bar UNTIL Track-2 lands.

## 5 · STOP-and-show verdict matrix

| Gate | Outcome |
|---|---|
| Convergent | FITS (7/8 YES · 1 PARTIAL · 0 NO) |
| Divergent  | DOES-NOT-FIT (5/8 YES · 2 PARTIAL · 1 NO) |
| Track-2 dispatch | **REQUIRED** (minimum scope; not a Decks rebuild) |
| JC-MON Stage 3 → Gate A | **CLOSED** |

