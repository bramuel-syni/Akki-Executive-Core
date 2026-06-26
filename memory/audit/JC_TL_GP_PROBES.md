**Canonical spec:** `/app/memory/JC_TL_CANONICAL_SPEC.md` §S0-Q4
(probe provenance classify-by-execution — "Show probe content per
path, in writing, before claiming the path is built").

# JC-TL Get-Perspectives — authored probe content (S0-Q4 evidence)

> **User watchpoint, verbatim:** "if the other three paths' probes
> need authoring and that gets reported as 'done' without the actual
> probe content shown, that's the quality hole."
>
> This file is the probe-authoring evidence for the Get-Perspectives
> path. Each probe is shown in writing here; no probe is "wired"
> without the content visible below.

## Path objective (from canonical spec §4)

> "DIVERGE to a spread — multiple legitimate persona views, their
> agreements, conflicts, and blind-spots — NOT converge to a single
> weighted picture. Synthesis INVERTS: the object is 'the span of
> views and where they tension,' not 'the most probable cause.'"

## Layer-by-layer probes

The Solva conversation walks 5 layers. The GP path replaces the
**Diagnose / Develop-strategy / Test-hypothesis** synthesis layer
with a **persona-spread** synthesis. Layers L0 (framing) through
L2 (triangulation+tension) ask probes shared with the other paths,
restated through the persona lens. Layer L3 (synthesis-divergent)
is GP-specific. Layer L4 (reflection) closes with refusal-to-
converge.

### L0 — Framing

| Probe ID | Probe text |
|---|---|
| L0-P1 | "**Whose viewpoints** do you want to read this situation through? Name the personas — by role, by stakeholder relation, or by lens they bring." |
| L0-P2 | "If we end with **only one weighted picture**, what gets lost? Name the read you'd lose first." |
| L0-P3 | "What's the framing each persona would resist? Name the framing they'd reject before you've started." |

Probe-authoring rationale: L0 in GP MUST gather the persona set
before any grounding work. The other three paths converge on a
single object early; GP keeps the set open. The "what gets lost"
probe is the anti-convergence brake at framing time.

### L1 — Grounding

| Probe ID | Probe text |
|---|---|
| L1-P1 | "What would **Persona X** most plausibly notice in the operating reality? Single sentence, observational, no judgment." |
| L1-P2 | "What would Persona X **not see** in the same operating reality? Name the gap that's structural to their lens, not the gap that's accidental." |
| L1-P3 | "Whose evidence does Persona X **trust first**? Name the evidence channel — audit trail, customer-signal, financial-report, regulator-comm." |

Probe-authoring rationale: L1 in GP grounds EACH persona
independently, not the consensus reading. The "not see" probe
foreshadows the blind-spot synthesis at L3.

### L2 — Triangulation + tension

| Probe ID | Probe text |
|---|---|
| L2-P1 | "Where do **two or more personas converge** on the same statement? Quote the statement; name which personas back it." |
| L2-P2 | "Where do personas **structurally disagree**? Name the fault-line — process-vs-trust, growth-vs-capital, surface-vs-subsurface. Don't arbitrate." |
| L2-P3 | "Is there a persona view that **cannot be triangulated** by any other? If yes, name it; it carries the load-bearing dissent." |

Probe-authoring rationale: L2 in GP surfaces both agreement
(which converges) and conflict (which doesn't). The third probe
is the catch for "outlier as load-bearing" — if one persona's
view is uniquely positioned, it's the spread's centre of
gravity, not noise.

### L3 — Synthesis-divergent (the GP-specific synthesis)

| Probe ID | Probe text |
|---|---|
| L3-P1 | "For each persona, name the **structural blind-spot** — what their lens cannot see that the others can. Use observational voice. One sentence." |
| L3-P2 | "What does the **spread itself say** about the operating question? Hold the personas visible; do not collapse to a single read." |
| L3-P3 | "If forced to weight, what would the act of weighting **destroy**? Name the read that would disappear under convergence pressure." |

Probe-authoring rationale: L3 is where the GP path inverts. The
convergent paths synthesise to a single best read; GP synthesises
to the spread, the agreement-cluster, the conflict-cluster, the
blind-spot map. The third probe is the **refusal-to-converge**
test — it gives the engine permission to refuse when convergence
would destroy operating signal.

### L4 — Reflection (closing — shared refusal logic, GP-flavoured)

| Probe ID | Probe text |
|---|---|
| L4-P1 | "What would **shift the spread**? Name the single observable signal that would collapse it toward one cluster." |
| L4-P2 | "What's the **cost of premature convergence**? Name what gets lost if we forced a single read now." |
| L4-P3 | "What's the **strongest case against your spread**? Steel-man the criticism — that one persona is missing, that personas were chosen for narrative, that the spread is performative." |

Probe-authoring rationale: L4 in GP closes by holding the spread
to scrutiny. The first probe is the sensitivity-input — the one
signal that would move the spread. The third probe is the
adversarial-counter — invited explicitly, not buried in
methodological honesty.

## Engine-call mapping

| Probe layer | Engine called | Output surface |
|---|---|---|
| L0 framing | `frame_audit` | `synthesis.cover` + `methodological_honesty.what_report_is` |
| L1 grounding | `candidate_generation` + `triangulation` (per-persona) | `synthesis.perspective_spread.personas[].view_summary` + `synthesis.perspective_spread.blind_spots[]` (preliminary) |
| L2 triangulation+tension | `triangulation` + `tension_detector` | `synthesis.perspective_spread.agreement_map[]` + `synthesis.perspective_spread.conflict_map[]` + `synthesis.tensions[]` |
| L3 synthesis-divergent | `probability_weighting` (per-persona confidence) + `meta_synthesis` (blind-spot finalise) | `synthesis.perspective_spread.personas[].confidence_pct` + `synthesis.perspective_spread.blind_spots[]` (final) + `synthesis.bias_inventory` |
| L4 reflection | `reflection` + `refuse_to_decide` | `synthesis.reflection_section` + `synthesis.methodological_honesty.provisional_nature_paragraph` |

Every L1–L4 engine call is Shield-routed under the standard
Solva surface (`solva_v2.synthesis_*` family).

## Refusal behaviour

GP path explicitly refuses to converge. The refusal surfaces are:

1. **L3-P3** (synthesis refusal) — if forced-weighting would
   destroy operating signal, the synthesis output stays at the
   spread. The `meta_synthesis` engine returns `refused=True,
   reason="convergence_would_destroy_operating_signal"`.
2. **`methodological_honesty.what_report_is_not`** — the deck
   surface states "this is NOT a single weighted picture" in plain
   text. The renderer enforces this slot.
3. **`refuse_to_decide` integrity validator** — runs against the
   deck payload before serialization. If `decision_logic` or
   `pathway` is populated on a divergent payload, the path-
   discipline validator on `ArtefactPayload` raises before any
   render happens (Track-2 schema enforcement, already shipped).

## What this dispatch does NOT claim

- **Probe content is shown above; probe code is NOT shipped in this
  dispatch.** The proving slice's 3 fixtures (regulatory /
  investment / launch) ship the `session.synthesis.perspective_spread`
  payload directly. The probe-to-synthesis pipeline (an
  Shield-routed LLM call that takes user turns through the L0–L4
  probes and emits the perspective_spread block) is the **next**
  dispatch — `LLM-DRIVEN-GP-SYNTHESIS` — and gets its own quality-
  regression check.

- **Deterministic builder, deterministic ship.** This dispatch's
  builder (`build_divergent_payload`) is byte-stable across two
  consecutive runs (Row C of the proving slice). The LLM-driven
  synthesis dispatch will move the byte-stability ratchet because
  LLM outputs are model-stable but not byte-stable across model
  swaps. That's expected.

## Standing rule respected

S0-Q4 lock honoured: **probe content shown in writing, per path,
before claiming the path is built.** The 15 probes above are the
content; the 3 rendered decks at
`/app/memory/jc_artifacts/jc_tl/03-gp-ship/*.pptx` are the
artefact evidence the methodology-spine holds across 3
representative scenarios.
