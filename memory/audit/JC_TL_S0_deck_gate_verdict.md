# JC-TL Stage 0 · S0-Q2 — Deck-grade comparison rubric verdict

> **Source of truth:** `/app/memory/JC_TL_CANONICAL_SPEC.md` (§ Stage 0 · S0-Q2).
>
> **Reference deck:** `/app/memory/reference_assets/MYDAWA_Reference_Deck.pptx`
> (13 slides — MYDAWA Recovery Programme · Board Briefing). Verified
> 2026-06-25 via `python-pptx` inventory below.
>
> **Verdict:** **FITS** for CONVERGENT renders · **DOES-NOT-FIT** for
> DIVERGENT renders — **TWO-TRACK BUILD** required per the decision
> rule. Surface the divergent gap now, do not defer into Stage 2.

---

## 1 · Reference deck inventory (the standard being measured against)

13-slide storyboard captured by `python-pptx` walk:

| # | Title | Function |
|---|---|---|
| 1 | MYDAWA · BOARD BRIEFING | cover (method tag + subject + period) |
| 2 | WHAT HAPPENED · The story in five sentences | headline (≤ 5 sentences) |
| 3 | WHY IT MATTERS · Three numbers without the spreadsheet | per-cluster confidence-weighted facts |
| 4 | THE RECOVERY PLAN · Six months in three phases | pathway w/ Days 0-30 / 30-60 / 60-180 |
| 5 | WHAT GETS DONE, AND WHO DOES IT | per-workstream owner + accountability |
| 6 | HOW YOU'LL KNOW IT'S WORKING · 3 layers of measurement | indicator hierarchy (board / COO / owner) |
| 7 | THE KPI CONTRACT · Eight workstreams, eight KPIs | baseline + target + cadence table |
| 8 | THE CADENCE · Who meets when | rhythm table (daily / weekly / monthly) |
| 9 | WHAT TO EXPECT, MONTH BY MONTH · Floor vs Plan | scenarios (2 ladders, weighted) |
| 10 | WHEN TO CHALLENGE THE PLAN · Two stop conditions | refusal-to-decide + sensitivity gates |
| 11 | WHAT WE NEED FROM YOU · 3 decisions + 3 commitments | decision-logic surface |
| 12 | WHAT COULD GO WRONG · 5 risks + responses | risk_mitigation pairs |
| 13 | MYDAWA · RECOVERY PROGRAMME · What we know / will do / will see | in_closing (reframing recap) |

These map 1:1 to the locked `LOCKED_DECK_ORDER` tuple in
`services/solva_v2/pptx_exporter.py:62-79` and the 16-element
`ArtefactPayload` schema in `services/solva_v2/artefact_schema.py:7-25`.

The reference deck is a **CONVERGENT** artefact. Every slide narrows
toward "what was diagnosed, what comes next." There is no divergent
spread (multiple peer voices, agreement/conflict/blind-spot map)
anywhere in the deck.

---

## 2 · Comparison rubric — per trait

The dispatch's locked 8-trait rubric measured against the existing
exporter's output shape (the 16-element `ArtefactPayload` →
`pptx_exporter.build_pptx`):

### Convergent render (Diagnosis / Develop-strategy)

The convergent path uses the `solva_v2.pptx_exporter` as-is. The
locked deck order produces the exact slide spine MYDAWA shows.

| # | Trait | Verdict | Evidence |
|---|---|---|---|
| 1 | Bold sans-serif typography hierarchy | **YES** | `pptx_exporter.py` uses warm-charcoal `INK` + ned-purple `NED_PURPLE` accent + muted-red eyebrow on parchment background (`PARCHMENT`). Multi-weight handling via `Pt()` sizing per builder. Same family as MYDAWA. |
| 2 | Monochrome palette + signal colors only on data | **YES** | 4-color brand palette (ink/deep/muted/rule on parchment) + 2 signal accents (`NED_PURPLE`, `EYEBROW_RED`). Solid colours only — opacity blends rejected per `pptx_exporter.py:17-19` ("PowerPoint colour math is unreliable across viewers"). |
| 3 | Narrative-vs-evidence side-by-side layout | **YES** | `tensions_overview` + `per_tension` builders thread `framing → evidence_quote → implication` triplets per `artefact_schema.py:7-12`. Visible on MYDAWA slides 4 ("phases" with role of each phase) + 9 ("floor vs plan"). |
| 4 | Per-cluster confidence weighting visible | **YES** | `scenarios[].weight_pct` + `scenarios[].confidence_pct` are explicit schema fields (`artefact_schema.py:13`). Rendered as percentages on the per-scenario tables — same shape as MYDAWA slide 9 ("floor 92 / plan 105"). |
| 5 | Bridge decompositions / indicator timelines | **YES** | `pathway[]` carries `TimelineTag` literals (`DAYS 0-30`, `DAYS 30-60`, …) per `artefact_schema.py:47-50`. Maps to MYDAWA slide 4 ("Month 1 / 2-3 / 4-6") and slide 6 ("board / COO / owner indicator layers"). |
| 6 | "Reflection — Not for the Deck" slide | **PARTIAL** | `reflection_section` element is rendered as a Layer-5 Q&A slide (`pptx_exporter.py:62-79`, position 7 in locked order). The "Not for the Deck" frame is the MYDAWA-specific copy treatment — the slot exists, the verbatim framing is a copy edit, not a schema gap. |
| 7 | "Fair Criteria" slide equivalent | **YES** | `methodological_honesty` element (`artefact_schema.py:20`) renders position 14 in the locked order. Substantive ≥-1-sentence subsections enforced by `CONSTRAINT_PREAMBLE` rule #4 (`v2_prompts.py:85-88`). Matches MYDAWA slide 10 (stop conditions) + slide 13 (what we know / will do / will see). |
| 8 | Refusal-to-decide explicit on the surface | **YES** | `CONSTRAINT_PREAMBLE` rule #3 (`v2_prompts.py:78-84`) enforces conditional / observational / provisional framing on every recommendation. The integrity validator rejects any directive copy. Surface treatment matches MYDAWA slide 11 (3 decisions + 3 commitments — staged, not asserted). |

**Overall convergent verdict: FITS.** 7 of 8 traits YES; 1 PARTIAL is
a copy treatment, not a structural gap. The existing exporter renders
the MYDAWA spine without modification.

### Divergent render (Get-perspectives)

The schema is fundamentally convergent. The locked order narrows from
tensions → scenarios → sensitivity → reflection → pathway — every step
collapses the surface area further. There is no slot for "the SPREAD
of perspectives + agreement / conflict / blind-spots."

| # | Trait | Verdict | Evidence |
|---|---|---|---|
| 1 | Bold sans-serif typography hierarchy | **YES** | Same exporter, same brand palette. |
| 2 | Monochrome palette + signal colors only on data | **YES** | Same palette. |
| 3 | Narrative-vs-evidence side-by-side layout | **PARTIAL** | The `per_tension` slot can be co-opted to render persona-vs-evidence pairs, but the schema's `tensions[]` element is semantically "tensions detected" — not "perspective spread." Forcing it into a divergent shape misrepresents the data. |
| 4 | Per-cluster confidence weighting visible | **PARTIAL** | Confidence is per-claim / per-scenario today. Get-perspectives needs **per-persona** confidence + cross-persona agreement maps. No schema field today. |
| 5 | Bridge decompositions / indicator timelines | **NO** | Divergent artefacts don't have timelines (they have voices speaking AS OF NOW). Pathway shape doesn't apply. |
| 6 | "Reflection — Not for the Deck" slide | **YES** | Reflection layer is path-agnostic. |
| 7 | "Fair Criteria" slide equivalent | **YES** | Methodological honesty applies regardless. |
| 8 | Refusal-to-decide explicit on the surface | **YES** | CONSTRAINT_PREAMBLE rule #3 still binds. |

**Crucially MISSING:** no slot for the divergent SYNTHESIS — "where
the personas agree, where they conflict, where each one's
blind-spot is." This is the load-bearing output of Get-perspectives
per the dispatch ("synthesis INVERTS — the object is 'the span of
views and where they tension,' not 'the most probable cause'").

**Overall divergent verdict: DOES-NOT-FIT.** 4 of 8 traits YES,
2 PARTIAL, 1 NO + a structural gap for the divergent-synthesis slot.

---

## 3 · Decision rule application

Per the dispatch's Stage 0 decision rules:

> - Both FIT → one track; confirm exporter as ThinkLab deck surface
> - Get-perspectives DOES-NOT-FIT → **two-track build (ThinkLab +
>   Decks upgrade)**. Surface now, not in build.
> - FITS-WITH-LOSS → scope the MINIMUM exporter change for
>   spread-expressibility, nothing more

**Verdict triggered: TWO-TRACK BUILD.**

Track 1 (in JC-TL scope): Diagnosis proving slice + Develop-strategy +
Test-hypothesis fan-out — all ride the existing convergent exporter
unmodified. Q6 lock (Get-perspectives quality bar is provisional
until first render) is consistent with this verdict — Get-perspectives
is held out for Stage 2 with a known schema-extension dependency.

Track 2 (parallel, separate dispatch — not in JC-TL): **Decks upgrade**
for divergent-shape rendering. Scope:
- New schema slot in `ArtefactPayload`:
  `perspective_spread`, carrying:
  - `personas: List[PersonaView]` (name, view summary, evidence ids)
  - `agreement_map: List[AgreementCluster]` (statement + which personas back it)
  - `conflict_map: List[ConflictCluster]` (point of tension + opposing personas)
  - `blind_spots: List[BlindSpot]` (per-persona)
- New builder in `pptx_exporter` for the divergent-synthesis slide
- Schema-level Pydantic validator: convergent path forbids
  `perspective_spread` set; divergent path forbids `scenarios[]` /
  `pathway[]` set. Path-aware integrity.

This is the **MINIMUM** scope to make Get-perspectives shippable at
deck-grade. Surface it now so the user can choose whether to:
- (a) dispatch the Decks upgrade in parallel with JC-TL Stage 1
- (b) defer Get-perspectives until the Decks upgrade ships
- (c) reframe Get-perspectives to use the convergent shape (likely a
  capability regression — flag honestly).

Per Q6: this **does not block** Stage 1. Diagnosis is the proving
slice; Stage 1 runs on the convergent track regardless of Track 2's
sequencing.

---

## 4 · Track-1 sample render — verbatim reproducibility hook

The convergent track uses the existing exporter. A live render hook
that exercises the EXISTING infrastructure (no new code) is:

```python
from services.solva_v2.pptx_exporter import build_pptx
from services.solva_v2.payload_builder import build_from_session
payload = build_from_session(session_id="<seek_clarity-completed-session>")
pptx_bytes = build_pptx(payload, context_name="<context>")
```

The dispatch's Stage 1 proving slice will produce the FIRST live
example with REAL user evidence + reach the Q2 rubric on the produced
deck (not on a placeholder). Stage 0 closes here with the schema-vs-
rubric verdict above; live sample artifacts land in Stage 1.

This deliberate scoping is per the canonical-spec discipline:
> "Proof = a real session producing a deck at the reference bar,
> shown — not 'wired/tests pass.'"

Stage 0 proves the schema fits the rubric. Stage 1 proves a real
session reaches the rubric on a real problem. Both required.

---

## 5 · STOP-and-show verdict (combined with S0-Q4)

| Gate | Outcome |
|---|---|
| **Q2 Convergent** | FITS (7/8 traits YES, 1 PARTIAL on copy treatment only). |
| **Q2 Divergent** | DOES-NOT-FIT (structural gap on divergent-synthesis slot). |
| **Track-count decision** | TWO-TRACK BUILD (Track 1 = JC-TL on existing exporter; Track 2 = separate Decks upgrade). |
| **JC-TL Stage 1 blocker?** | NO — Diagnosis rides Track 1 unmodified. |
| **Q6 alignment** | YES — Get-perspectives provisional-until-first-render is consistent with Track-2 dependency. |

Stage 0 deck-gate verdict: **PASS for Diagnosis Stage 1; HOLD for
Get-perspectives pending Track-2 dispatch.**

