# JC-TL Stage 0 — Deck gate + probe provenance verdicts

> **Source of truth:** `/app/memory/JC_TL_CANONICAL_SPEC.md` (§ Stage 0).

**Closed 2026-06-25** — Both gates surfaced together as required by
the dispatch. STOP-and-show ready before Stage 1.

---

## Gate 1: S0-Q2 — Deck-grade comparison rubric

**Verdict:** **FITS** for CONVERGENT renders · **DOES-NOT-FIT** for
DIVERGENT renders.

**Track-count decision:** **TWO-TRACK BUILD** triggered. JC-TL
(Track 1) ships on the existing convergent exporter unmodified;
Get-perspectives ships on Track 2 (separate **Decks upgrade**
dispatch) which is **NOT** in JC-TL scope.

**JC-TL Stage 1 blocker?** **NO** — Diagnosis rides Track 1
unmodified.

Full per-trait scorecard + reproducibility evidence at
`/app/memory/audit/JC_TL_S0_deck_gate_verdict.md`. Key references:
- Reference deck: `/app/memory/reference_assets/MYDAWA_Reference_Deck.pptx`
  (13 slides, MYDAWA Recovery Programme; inventory captured in the
  verdict doc)
- Convergent exporter: `services/solva_v2/pptx_exporter.py`
  (`LOCKED_DECK_ORDER` tuple, line 62-79)
- Convergent payload schema: `services/solva_v2/artefact_schema.py`
  (15-element payload, line 7-25)

**Convergent rubric:** 7/8 traits **YES**, 1 **PARTIAL** (copy
treatment only, not a structural gap). Schema + exporter cover the
MYDAWA spine.

**Divergent rubric:** 4/8 **YES**, 2 **PARTIAL**, 1 **NO** + a
structural gap on the divergent-synthesis slot (per-persona spread +
agreement / conflict / blind-spot map). No schema field today.

**MINIMUM Track-2 scope** (for the Decks upgrade — surfaced now per
the canonical-spec discipline):
- New schema slot `perspective_spread` carrying
  `personas[] / agreement_map[] / conflict_map[] / blind_spots[]`
- New pptx builder for the divergent-synthesis slide
- Path-aware Pydantic validator (convergent forbids
  `perspective_spread`; divergent forbids `scenarios[]` /
  `pathway[]`)

---

## Gate 2: S0-Q4 — Probe provenance classify-by-execution

**Verdict:** Diagnosis voice EXISTS + emergent probes are real
(produced MYDAWA). The other three submodules carry voice headers
but **no path-specific probe banks** — probe authoring is NEEDED
for all three.

| Path | Voice header? | Layer engines? | Probe bank? | **Verdict** |
|---|:---:|:---:|:---:|:---:|
| Diagnosis / `seek_clarity` | ✅ | ✅ | ❌ (emergent) | **EXIST** (reference; produced MYDAWA) |
| Develop Strategy | ✅ | ✅ | ❌ | **NEED AUTHORING** |
| Test Hypothesis | ✅ | ✅ + hypothesis layer | ❌ | **NEED AUTHORING** |
| Get Perspectives | ✅ | ✅ | ❌ | **NEED AUTHORING** + Q6 (provisional bar) |

**Authored probe content per path** (verbatim, ready for Stage 2
wiring) at `/app/memory/audit/JC_TL_S0_probe_provenance.md`:

- Diagnosis: 11 emergent probes documented (3 framing + 3 grounding +
  2 synthesis + 3 reflection)
- Develop Strategy: 12 authored (3+3+3+3)
- Test Hypothesis: 14 authored (3+3+3+2+3, includes hypothesis-layer)
- Get Perspectives: 12 authored (3+3+3+3) — provisional per Q6

User-watchpoint discipline honoured: probe content is shown verbatim
in the audit doc before any path is claimed built. Stage 2 wiring
will commit these to `services/solva_v2/probes.py` as path-distinct
constants.

---

## Standing-rule adherence (checked across both gates)

- **Reuse existing engines + exporter** ✅ — Stage 0 is read-only
  classification; zero engine modifications
- **Internal name stays `solva`; ThinkLab is UI label only** ✅ —
  invariant `test_thinklab_uilabel_only.py` already locks this
- **Shield-routed every call** ✅ — engines already Shield-routed via
  `services/solva_v2/llm_adapter.py`
- **Status is not truth — classify by execution** ✅ — both gates'
  verdicts derived from file:line citations, reproducible
- **Latitude per-path layer order with deliberate-step constraint** ✅
  — probes authored as deliberate user-facing prompts per layer, not
  folded into grounding
- **Build the conversation, not the questionnaire (Q1)** ✅ — probes
  are PROMPTS the LLM can re-cast in conversation, not fixed
  form-field questions
- **Summary ≠ Deck (Q5)** ✅ — preserved by the rubric verdict;
  artefact is the deck output, session record is the conversation
  trace, two distinct artifacts
- **Diagnosis first, fan-out after STOP-show (Q3)** ✅ — Q4 confirms
  Diagnosis can ship unblocked; the other 3 wait
- **Probe-content shown in writing before built (Q4 watchpoint)** ✅
  — `/app/memory/audit/JC_TL_S0_probe_provenance.md` has every probe
  verbatim
- **Get-perspectives provisional until first render (Q6)** ✅ —
  divergent gap surfaced; Track-2 dependency named

---

## Persistence (per dispatch's zero-handoff-loss discipline)

| Artefact | Path |
|---|---|
| Canonical spec | `/app/memory/JC_TL_CANONICAL_SPEC.md` |
| Reference deck (MYDAWA) | `/app/memory/reference_assets/MYDAWA_Reference_Deck.pptx` (442 KB · 13 slides) |
| Deck gate verdict | `/app/memory/audit/JC_TL_S0_deck_gate_verdict.md` |
| Probe provenance verdict | `/app/memory/audit/JC_TL_S0_probe_provenance.md` |
| This sprint memo | `/app/memory/sprints/JC_TL_STAGE_0_GATES.md` |
| `DEV_PIPELINE.md` §1/§2/§4/§9 references | updated this commit |
| KNOWN_MAPPINGS `JC_TL_*` pattern | included via spec naming |

---

## What's NOT in this stage

Stage 0 is gates-only — no Stage 1 execution. After STOP-and-show
approval:

- **Stage 1** — Diagnosis proving slice (entry surface + 4-way picker
  + material attach + guided one-thing-at-a-time conversation +
  session record + deck-grade artifact measured against MYDAWA)
- **Stage 2** — fan-out to the other 3 paths on the SHARED
  framework (only after Stage 1 STOP-show approved)
  - Develop Strategy + Test Hypothesis: ride convergent exporter
    (Track 1)
  - Get Perspectives: **GATED on Track-2 Decks upgrade** per Q2
    verdict + Q6 lock

---

## STOP-and-show summary

| Gate | Verdict | Stage-1 blocker? |
|---|---|---|
| Q2 Convergent | FITS (7/8 YES, 1 PARTIAL) | NO |
| Q2 Divergent | DOES-NOT-FIT (structural gap) | NO (Get-perspectives is Stage 2 only) |
| Track decision | TWO-TRACK BUILD (JC-TL + separate Decks upgrade) | NO |
| Q4 Diagnosis probes | EXIST (emergent reference) | NO |
| Q4 Other-3 probes | NEED AUTHORING (content authored in writing) | NO (commit at Stage 2) |
| Q6 Get-perspectives bar | provisional until first render | NO (Stage 2 only) |

Stage 0 closes. **Diagnosis Stage 1 cleared for proving-slice
construction** once user signs off on:
- Track-2 Decks-upgrade dispatch (parallel · separate · not in
  JC-TL scope)
- Authored probe content (verbatim in
  `audit/JC_TL_S0_probe_provenance.md`)
