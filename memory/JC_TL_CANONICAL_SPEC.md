# JC-TL — ThinkLab build · Canonical Specification

> **Source:** User dispatch — 2026-06-25
> **Status:** ACTIVE
> **Supersedes:** Any prior ThinkLab brief in handoffs / runway docs /
> sprint memos. Includes prior **ThinkLab Gate A** / **TL0** backlog items
> from `DEV_PIPELINE.md` §6 / §9 — those are now folded into JC-TL Stage 0.
>
> **Handoff-durability contract.** This file + `DEV_PIPELINE.md` §2 + the
> most recent JC-TL sprint memo together MUST be sufficient to resume the
> build without re-asking the user any locked decision. Every JC-TL sprint
> memo MUST cite this file on line 1 as "Source of truth."
>
> **Reference deck (locked quality bar):**
> `/app/memory/reference_assets/MYDAWA_Reference_Deck.pptx`. Every render
> rubric, every probe-authoring decision, every "is it deck-grade" verdict
> measures against this file. **Pinned 2026-06-25.**

---

## Framing — the anchor (locked)

ThinkLab is the guided, multi-path reasoning experience over the existing
Solva engine. The engine is real and substantial; the four paths and
their methodology primitives already exist. This phase builds the
**EXPERIENCE** that lets a non-creator run any path to the bar of the
reference deck — and proves the deck-grade artifact gate before
committing the artifact path. **Proof = a real session producing a deck
at the reference bar, shown — not "wired/tests pass."**

The quality bar is the **DIAGNOSIS METHODOLOGY** that produced the
MYDAWA reference deck — NOT Develop-strategy. That deck is the
seek_clarity/diagnosis path run to full synthesis. Its power is the
methodological spine, which is path-agnostic and **IS the Solva
model's integrity**:

```
frame-audit
  → candidate-generation
    → triangulation (narrative vs evidence)
      → tension-detection
        → probability-weighting (confidence per cluster)
          → sensitivity ("what would change this picture")
            → reflection (deliberately uncomfortable questions)
              → refusal (does not decide for the user)
```

Every path holds **this bar**. The reference deck is the standard each
path's output is measured against.

---

## Part 0 — Solva model integrity (non-negotiable)

- Methodology primitives are SHARED ENGINES and stay intact — do not
  rebuild or weaken: `frame_audit` · `candidate_generation` ·
  `triangulation` · `tension_detector` · `probability_weighting` ·
  `reflection` · `refusal`. Every path composes them; none reimplements
  them.
- Internal names stay **"solva."** ThinkLab is a UI label only,
  enforced by the build-breaking invariant
  (`tests/invariants/test_thinklab_uilabel_only.py` — landed Stage 1
  audit close-out).
- Every LLM call routes through SyniSense Shield; audit + trust receipt
  per call; tenancy + fail-closed unchanged. Reuse the existing deck
  exporter — do not build a parallel one.
- Status is not truth. Classify each path by **EXECUTION** (run it,
  read the output) before building or repairing.

---

## Part 1 — The four paths (shared engines; per-path layer order
derived from objective)

Latitude granted: layer order may differ per path where the objective
demands it — the engine already does this. Use that latitude to surface
the loved primitives (triangulation, weighting, sensitivity, reflection)
as **DELIBERATE STEPS**, not folded invisibly inside "grounding."

### 1. DIAGNOSIS / SEEK CLARITY — the reference path (proven; THE PROVING SLICE)

- Objective: sharpen the real question; diagnose; **STOP at the
  question** (does not recommend).
- Flow: `framing → grounding → triangulation+tension →
  weighting+sensitivity → reflection`.
- This is exactly what the MYDAWA deck shows. Build the experience so a
  user reproduces that deck's shape on their own problem. **THIS path
  is the proving slice; the other three fan out only after this is
  shown.**

### 2. DEVELOP STRATEGY — convergent to recommendation

- Objective: where Seek Clarity stops at the sharpened question,
  Develop Strategy ANSWERS it — 2-4 specific, sequenced recommendations
  grounded in the diagnosis.
- Flow: the diagnosis spine through the weighted picture, THEN
  synthesis converges to a sequenced pathway (the reference deck's
  Days 0-30 / 0-90 / 30-180 pathway, but as the **PRODUCT**, not an
  appendix).

### 3. TEST HYPOTHESIS / SIMULATE — proposition under stress

- Objective: take the user's hypothesis, expand to 2-3 scenarios with
  second-order effects, test what would falsify it, weight, refuse to
  over-claim.
- Flow: `framing → grounding → hypothesis (scenario-expansion +
  tension) → weighting → synthesis → reflection`.

### 4. GET PERSPECTIVES — the divergent outlier (and the deck gate stress case)

- Objective: **DIVERGE** to a spread — multiple legitimate persona
  views, their agreements, conflicts, and blind-spots — NOT converge
  to a single weighted picture.
- Flow: same primitives (triangulation, tension, refusal) but
  synthesis **INVERTS** — the object is "the span of views and where
  they tension," not "the most probable cause."

---

## Q1 LOCKED — Non-creator experience shape (load-bearing; the deck IS the storyboard)

Hold the MYDAWA deck as the **experiential spec**, not just the quality
bar. The deck is the journey's storyboard. The session walks the user
through producing exactly that artifact.

- **Entry:** ThinkLab is its own surface (the existing Solva surface
  relabeled per the UI-label invariant) — not buried in another module.
- **Path selection:** a **4-way picker with one line of objective each**,
  not a routing question:
  - "Sharpen a question (diagnose)"
  - "Develop a strategy (recommend)"
  - "Test a hypothesis"
  - "Get perspectives"

  The user names their own intent rather than answering a quiz that
  guesses it — same anti-classifier discipline as Chat.
- **Bring material:** **upload + paste + attach-from-context** (reuse
  the existing retrieval/attach rails — do not build new). It's
  **optional** — the session runs on conversation alone if nothing's
  brought, exactly as the MYDAWA session did (its inputs were
  "conversational responses + operational data").
- **Layer-by-layer flow:** **guided one-thing-at-a-time conversation,
  NOT a form, NOT a scrollable wizard.** Solva already walks "one
  layer at a time and asks the questions a sharp counterpart would
  ask" — that's in the engine voice. Each layer asks its preset
  probes, the user answers in natural language, the session advances
  when the layer's engines have what they need.
- **Why this shape, not a form:** the whole value is the **probing** —
  the candor the MYDAWA session extracted ("you weren't certain
  whether you were diagnosing accurately or pattern-matching") only
  happens in a guided exchange, never in a form. **Build the
  conversation, not the questionnaire.**
- **Outputs:** The session output accretes into the session record.
  At synthesis, the deck-grade artifact is produced.

---

## Q5 LOCKED — Two distinct outputs

- **Summary = the session record** (what was reasoned and what was
  concluded). Always produced.
- **Deck = the shareable artifact** (the exportable synthesis at
  deck-grade). The synthesis output of the session.

Two distinct artifact types. **Do not build one and call it the other.**

---

## Stage 0 — Gates (resolve before build; reproducible verdicts)

### S0-Q2 — Deck-grade comparison rubric (reproducible verdict, not judgment call)

Render TWO shapes through the existing exporter, measured against
`/app/memory/reference_assets/MYDAWA_Reference_Deck.pptx`:

- (a) Diagnosis / Develop-strategy output (convergent: tensions +
  weighted picture + pathway)
- (b) Get-perspectives output (divergent spread: multiple views,
  agreement / conflict / blind-spots)

**Comparison rubric (use this — do not improvise):**

- Bold sans-serif typography hierarchy (yes / no / partial)
- Monochrome palette + signal colors only on data (yes / no / partial)
- Narrative-vs-evidence side-by-side layout present (yes / no / partial)
- Per-cluster confidence weighting visible (yes / no / partial)
- Bridge decompositions / indicator timelines (yes / no / partial)
- "Reflection — Not for the Deck" slide equivalent (yes / no / partial)
- "Fair Criteria" slide equivalent (yes / no / partial)
- Refusal-to-decide explicit on the surface (yes / no / partial)

Per-trait verdict + overall **FITS / FITS-WITH-LOSS / DOES-NOT-FIT**
per render. **Output to**
`/app/memory/audit/JC_TL_S0_deck_gate_verdict.md` with the actual
rendered .pptx files attached + reference deck cited.

**Decision rules:**
- Both FIT → one track; confirm exporter as ThinkLab deck surface
- Get-perspectives DOES-NOT-FIT → two-track build (ThinkLab + Decks
  upgrade). Surface now, not in build.
- FITS-WITH-LOSS → scope the MINIMUM exporter change for
  spread-expressibility, nothing more

### S0-Q4 — Probe provenance classify-by-execution

Read each path's existing probes in the engine. Report per-path:

- **Diagnosis / Seek Clarity probes:** EXIST (produced MYDAWA) —
  name count + cite engine file:line
- **Develop Strategy probes:** EXIST / NEED AUTHORING — name count if
  exist, gap if not
- **Test Hypothesis probes:** EXIST / NEED AUTHORING — same
- **Get Perspectives probes:** EXIST / NEED AUTHORING — same

**Honest expectation:** Diagnosis exists; the other three likely need
probe authoring against their objectives. **That's content work
inside the engine, not engine-reuse.** If authoring is needed, name
it as such with per-path count and the proposed probe text **BEFORE**
writing any probe code. Do not let "wire it up" silently absorb
probe authorship.

**Output to** `/app/memory/audit/JC_TL_S0_probe_provenance.md`. **User
watchpoint:** "if the other three paths' probes need authoring and
that gets reported as 'done' without the actual probe content shown,
that's the quality hole." Show the probe content per path, in
writing, before claiming the path is built.

**S0 verdict report combines Q2 + Q4 in one surface point before any
build starts.**

---

## Stage 1 — Diagnosis proving slice (Q3 LOCKED: Diagnosis first, fan-out after show)

Diagnosis is the proving slice. Build the experience for **ONE path**
(Diagnosis / Seek Clarity) end-to-end:

- ThinkLab entry surface (relabeled Solva)
- 4-way picker rendered (other 3 paths grayed as "coming after the
  slice" — or just non-functional for now; UI presence is enough to
  lock the picker shape)
- Diagnosis path selected → material attach (upload + paste +
  attach-from-context, all optional) → **guided one-thing-at-a-time
  conversation** walking the layers: `framing → grounding →
  triangulation+tension → weighting+sensitivity → reflection →
  refusal`
- Session record accretes (Q5: summary)
- Synthesis produces deck-grade artifact (Q5: deck) measured against
  MYDAWA via the Q2 rubric

**Proving slice acceptance:** a non-creator runs Diagnosis on a real
problem, brings minimal material (or none), answers preset probes in
conversation, leaves with a coherent session summary **AND** a deck
that meets the Q2 rubric at FITS or FITS-WITH-LOSS level against
MYDAWA. **STOP-and-show before fan-out.**

**Artefacts:** `/app/memory/jc_artifacts/JC-TL/01-diagnosis-proving-slice/`:
- Session record JSON
- Deck-grade artefact .pptx
- Q2 rubric scorecard for the produced deck vs MYDAWA
- Refusal evidence (if user input was thin, the engine refused to
  over-claim)
- Conversation transcript showing the probing exchange (proves
  "build the conversation, not the questionnaire")

**Sprint memo:**
`/app/memory/sprints/JC_TL_STAGE_1_DIAGNOSIS_PROVING_SLICE.md`
citing canonical spec on line 1.

---

## Stage 2 — Fan out the other three (only after Stage 1 STOP-show)

Replicate the proven Diagnosis shape across the other three paths on
the SHARED FRAMEWORK (not single-path calcification, not
built-blind-parallel):

- **Develop Strategy** — convergent to recommendation. Layer order
  derived from objective per engine reality. Probes per S0-Q4 verdict
  (author if needed, show content). Output deck shape: diagnosis
  spine → weighted picture → Days 0-30 / 0-90 / 30-180 pathway as the
  PRODUCT.
- **Test Hypothesis** — proposition under stress. Hypothesis layer +
  falsification logic. Probes per S0-Q4 verdict. Output deck shape:
  2-3 scenarios with second-order effects + falsification surface +
  weighted confidence.
- **Get Perspectives** — divergent. Synthesis INVERTS. Probes per
  S0-Q4 verdict. **Q6 LOCKED:** no reference deck exists for this —
  the divergent artifact doesn't exist yet. The quality bar is
  methodology spine + your judgment on first render. **Explicitly
  provisional until that render exists.** First Get-perspectives
  deck rendered becomes its own reference once judged deck-grade.

Per path: ONE artefact set, sprint memo, Q2-style rubric application
(where applicable — Get Perspectives uses spine-only assessment, not
MYDAWA rubric).

**Artefacts:**
`/app/memory/jc_artifacts/JC-TL/02-fan-out/{develop-strategy,test-hypothesis,get-perspectives}/`.
**Sprint memo:** `/app/memory/sprints/JC_TL_STAGE_2_FAN_OUT.md`.

---

## Acceptance

A non-creator completes ANY of the four paths unaided and leaves with
a coherent summary plus a deck-grade artifact at the reference bar
(or, for Get-perspectives, at the provisional spine-only bar). The
four are visibly distinct — three converge on different objects
(sharpened question / recommendation / tested hypothesis), one
diverges (spread of views). The Solva methodology spine is intact
across all four; the deck gate is closed on evidence, one-track or
two. The reference standard is the MYDAWA deck — nothing ships below
it (except Get-perspectives, which ships at its own first-render bar
with explicit user-judgment lock).

---

## Standing rules (JC-TL)

- Reuse the existing engines (Solva primitives + deck exporter) — do
  not rebuild.
- Every LLM call Shield-routed; account/context-scoped; audit +
  fail-closed unchanged.
- Internal name stays "solva"; ThinkLab is UI label only
  (build-breaking invariant already landed).
- "Status is not truth" — classify by execution before building or
  repairing.
- Latitude per-path layer order BUT constrained to "deliberate steps,
  not folded invisibly inside grounding."
- Build the CONVERSATION, not the questionnaire (Q1 lock).
- Summary ≠ Deck (Q5 lock).
- Diagnosis first, fan-out after STOP-show (Q3 lock).
- Probe provenance: show authored content per path, not just "wired"
  (Q4 lock + user watchpoint).
- Get-perspectives quality bar is provisional until first render (Q6
  lock).
- Escalate STOPs (deck gate result if non-trivial; probe authorship
  if larger than expected; engine truly can't produce required
  output) / architectural forks only.

---

## Parallel execution context (three streams)

- Stream 1: **JC-MON Stage 2a** (BE achievement engine thin slice)
- Stream 2: **JC-CHAT Stage A** (FE marker surface execution)
- Stream 3: **JC-TL Stage 0 + Stage 1** (ThinkLab build with Diagnosis
  proving slice)

Three submodules, no expected tree collision. If any cross-component
touch surfaces (e.g., JC-TL touches the existing Solva surface which
JC-MON also wires for objective auto-suggest), serialize at smallest
possible scope; don't pause the larger work.

Surface all three streams together when each reaches its STOP point:
- JC-MON Stage 2a thin-slice artefacts
- JC-CHAT Stage A before/after marker surface
- JC-TL Stage 0 deck gate + probe provenance verdicts (S0 surfaces
  BEFORE Stage 1 starts; Stage 1 proving-slice surfaces after S0
  closes)

---

## Execution order (JC-TL specifically)

1. Persist canonical spec at `/app/memory/JC_TL_CANONICAL_SPEC.md`,
   save MYDAWA deck to `/app/memory/reference_assets/`, update
   `DEV_PIPELINE.md` references + KNOWN_MAPPINGS. Commit:
   `chore(JC-TL): persist canonical spec, reference deck, and
   pipeline references`.
2. **Stage 0** — S0-Q2 deck gate rubric + S0-Q4 probe provenance.
   Surface BOTH in one report. STOP-and-show.
3. **Stage 1** — Diagnosis proving slice end-to-end (after S0
   closes). STOP-and-show.
4. **Stage 2** — fan out the other three paths (only after Stage 1
   STOP-show approved).

---

## Artefact manifest (per-stage handoff durability)

**Persistence (commit 1):**
- `/app/memory/JC_TL_CANONICAL_SPEC.md` (this file)
- `/app/memory/reference_assets/MYDAWA_Reference_Deck.pptx`
- `DEV_PIPELINE.md` §1 / §2 / §4 / §9 references updated
- KNOWN_MAPPINGS extended with `JC_TL_*` patterns

**Stage 0:**
- `/app/memory/audit/JC_TL_S0_deck_gate_verdict.md` (Q2; rubric
  scorecard for both renders + reference deck citation)
- `/app/memory/audit/JC_TL_S0_probe_provenance.md` (Q4; per-path
  EXIST / NEED-AUTHORING + proposed probe content where needed)
- Sprint memo: `/app/memory/sprints/JC_TL_STAGE_0_GATES.md`
- Renders: `/app/memory/jc_artifacts/JC-TL/00-deck-gate/convergent.pptx`
  + `/app/memory/jc_artifacts/JC-TL/00-deck-gate/divergent.pptx`

**Stage 1 (Diagnosis proving slice):**
- `/app/memory/jc_artifacts/JC-TL/01-diagnosis-proving-slice/`
  - `session-record.json`
  - `deck.pptx`
  - `rubric-scorecard.md`
  - `refusal-evidence.json`
  - `conversation-transcript.json`
- Sprint memo:
  `/app/memory/sprints/JC_TL_STAGE_1_DIAGNOSIS_PROVING_SLICE.md`

**Stage 2 (fan-out):**
- `/app/memory/jc_artifacts/JC-TL/02-fan-out/develop-strategy/...`
- `/app/memory/jc_artifacts/JC-TL/02-fan-out/test-hypothesis/...`
- `/app/memory/jc_artifacts/JC-TL/02-fan-out/get-perspectives/...`
- Sprint memo: `/app/memory/sprints/JC_TL_STAGE_2_FAN_OUT.md`

All sprint memos: first line cites this file. `DEV_PIPELINE.md`
§1/§2/§4/§9 updated BEFORE each memo. KNOWN_MAPPINGS extended for
`JC_TL_*` pattern.
