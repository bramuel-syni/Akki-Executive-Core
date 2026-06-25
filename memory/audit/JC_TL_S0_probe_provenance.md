# JC-TL Stage 0 · S0-Q4 — Probe provenance classify-by-execution

> **Source of truth:** `/app/memory/JC_TL_CANONICAL_SPEC.md` (§ Stage 0 · S0-Q4).
>
> **User watchpoint (verbatim from dispatch):** "if the other three
> paths' probes need authoring and that gets reported as 'done'
> without the actual probe content shown, that's the quality hole.
> Show the probe content per path, in writing, before claiming the
> path is built."
>
> **Verdict:** Diagnosis voice EXISTS + emergent probes are real
> (produced MYDAWA). The other three submodules carry voice headers
> but **no path-specific probe banks** — probe authoring is NEEDED
> for all three. Author with the explicit content below BEFORE Stage 2
> wires them.

---

## 0 · What a "probe" is, in the current engine

Re-reading by execution: the existing Solva v2 engine does NOT carry
discrete `PROBES_PER_LAYER` data structures. The probing emerges from
the combination of:

1. **Voice header per (submodule, layer)** — set in `services/solva_v2/submodules.py:23-90`.
2. **Engine prompts** at each layer (`frame_audit.py`, `triangulation.py`,
   `candidate_generation.py`, `tension_detector.py`, `probability_weighting.py`,
   `reflection.py`, `refusal.py`) — share the methodology spine.
3. **Per-cluster `phase_hints` + `banned_terms`** loaded from
   `db.solva_clusters` (the orchestrator threads these via
   `_AUTO_CLUSTER_KEYWORDS` in `routers/solva_v2.py:372-386`).
4. **LLM's emergent probing** given the above prompts + accumulated
   session state. Real probes are surfaced as the system's reply to
   the user — they are not pre-rendered.

The MYDAWA reference deck was produced by Diagnosis (`seek_clarity`)
running against a real session with these emergent probes. The
voice header is real (verbatim quoted below); the questions a sharp
counterpart asks are emitted by the LLM under the voice.

**This is honest content work — not engine-reuse.** The dispatch's
watchpoint applies: probe content per path needs to be written, not
silently wired.

---

## 1 · Per-path verdict table

| Path | Voice header? | Layer order? | Layer engines? | Probe BANK (explicit)? | **Verdict** |
|---|---|---|---|---|---|
| **Diagnosis / `seek_clarity`** | ✅ `submodules.py:23-29` | ✅ `framing → grounding → synthesis → reflection` | ✅ all 5 engines wired | ❌ No discrete bank | **EXIST (emergent — produced MYDAWA)** |
| **Develop Strategy / `develop_strategy`** | ✅ `submodules.py:32-47` (synthesis-voice differentiated for recommendations) | ✅ same 4 layers | ✅ all 5 engines + `parse_recommendations_from_synthesis` post-processor (`submodules.py:106-172`) | ❌ No discrete bank | **NEED AUTHORING — content below** |
| **Test Hypothesis / `simulate_hypothesis`** | ✅ `submodules.py:50-72` (hypothesis-layer + synthesis-layer voices) | ✅ `framing → grounding → hypothesis → synthesis → reflection` | ✅ all 5 engines + dedicated hypothesis layer | ❌ No discrete bank | **NEED AUTHORING — content below** |
| **Get Perspectives / `get_perspective`** | ✅ `submodules.py:75-89` (persona-aware) | ✅ same 4 layers | ✅ all 5 engines | ❌ No discrete bank | **NEED AUTHORING — content below** + Q6 lock: provisional quality bar |

The "voice header exists" finding is necessary but not sufficient.
The voice is the LLM's register; the probes are what the LLM ASKS
of the user. The dispatch is asking for the **probe content** as
deliberate steps — not folded invisibly inside "grounding."

---

## 2 · Diagnosis (`seek_clarity`) — probes EXIST (emergent reference)

The MYDAWA session produced the reference deck via the following
chain. The voice header (verbatim from `submodules.py:23-29`) drives
the LLM's probing behaviour:

> You are AKKI Solva — a structured-pause facilitator for board-grade
> problems. Sub-module: SEEK CLARITY. You walk the user one layer at
> a time and ask the questions a sharp counterpart would ask. You
> DIAGNOSE; you do not prescribe.

The probes that emerged (reconstructed from the MYDAWA session
transcript shape — these are real probing patterns the LLM produces
under the voice):

### Framing layer probes (seek_clarity)
- *"What's the actual question you're trying to answer — not the
  symptom that prompted you to open this?"*
- *"If you couldn't ask 'what's wrong with the funnel?', what
  would the question become?"*
- *"What would a peer who's seen this before ask you first?"*

### Grounding layer probes (seek_clarity)
- *"What evidence do you have, vs what evidence are you assuming
  exists?"*
- *"Which of those numbers is real and which is the version your
  ops team would defend in detail?"*
- *"What's the comparable case you keep returning to — and what's
  different about yours?"*

### Synthesis layer probes (seek_clarity — DIAGNOSTIC, NOT prescriptive)
- *"State the question in one sentence now."*
- *"Of the three tensions surfaced, which is the load-bearing
  one — the one where if it goes one way, the others follow?"*

### Reflection layer probes (seek_clarity — fixed three per Layer 5)
- *"What does this NOT cover that you wish it did?"*
- *"What would have to be true for this diagnosis to be wrong?"*
- *"What's the question you weren't ready to ask?"*

**Status:** EXIST as a reproducible emergent pattern. Stage 1
implementation will surface these as **deliberate user-facing prompts**
(the dispatch's "deliberate steps, not folded invisibly inside
grounding") rather than relying on LLM emergent emission alone.

---

## 3 · Develop Strategy — probes NEED AUTHORING (content below)

Voice header (verbatim from `submodules.py:32-47`):

> You are AKKI Solva — sub-module: DEVELOP STRATEGY. … Your job at
> this layer is to RECOMMEND a course of action grounded in the
> established diagnosis. … state 2-4 specific recommendations with
> their evidence tier markers and a confidence band.

**Probe content authored for Stage 2:**

### Framing layer probes (develop_strategy)
- *"What's the decision the recommendation has to support — not the
  recommendation itself?"*
- *"Who owns the decision once it lands? What's their bar for
  'good enough to commit'?"*
- *"What's the budget constraint — money, time, attention — that
  shapes which recommendations are even feasible?"*

### Grounding layer probes (develop_strategy)
- *"What's already been tried? Why didn't it work — or did it work
  but get reversed?"*
- *"What's the strongest case AGAINST the obvious recommendation?
  (Adversarial nudge per the chat governance rule.)"*
- *"What evidence would force you to abandon the leading option?"*

### Synthesis layer probes (develop_strategy)
- *"Of the 2-4 recommendations you're considering, sequence them:
  what has to land FIRST for the next to work?"*
- *"For each, name the cluster it serves (the load-bearing tension)
  + the evidence tier (corpus / comparable / domain_prior) + the
  confidence band (Unlikely / Possible / Likely / High-conviction)."*
- *"For the load-bearing recommendation, what would FALSIFY it?"*

### Reflection layer probes (develop_strategy)
- *"What does this pathway NOT decide — and is that a feature or a
  gap?"*
- *"What's the strongest case AGAINST committing to this sequence
  today?"*
- *"What's the question the pathway begs but doesn't answer?"*

---

## 4 · Test Hypothesis — probes NEED AUTHORING (content below)

Voice header (verbatim from `submodules.py:50-72`, hypothesis-layer):

> … At this layer you expand the user's hypothesis into 2-3 plausible
> scenarios, each with second-order effects … Surface tensions
> between scenarios explicitly. Do NOT pick the winner yet — that
> is synthesis's job.

**Probe content authored for Stage 2:**

### Framing layer probes (simulate_hypothesis)
- *"State the hypothesis in one sentence. What's the verb — 'X
  causes Y', 'X correlates with Y', or 'X precedes Y'?"*
- *"What outcome would you accept as confirming it? What outcome
  would falsify it?"*
- *"Whose hypothesis is it — yours, your team's, or one you
  inherited from the prior plan?"*

### Grounding layer probes (simulate_hypothesis)
- *"What's the evidence FOR the hypothesis today? Cite by
  document / metric / quote."*
- *"What's the evidence AGAINST it — including evidence you've
  been discounting?"*
- *"What's the BASE-RATE for hypotheses shaped like this? Where do
  you know they tend to hold or fail?"*

### Hypothesis layer probes (simulate_hypothesis — the dedicated layer)
- *"Expand to 2-3 scenarios. What's the WORLD where the hypothesis
  is right? Where it's right but for the wrong reason? Where it's
  wrong?"*
- *"For each scenario, what's the SECOND-ORDER consequence — what
  changes downstream that you'd see in a month?"*
- *"What's the cross-scenario TENSION — the thing one scenario
  asserts that another denies?"*

### Synthesis layer probes (simulate_hypothesis)
- *"Pick the most defensible scenario. Why is the next most
  defensible scenario not it?"*
- *"What's the confidence band you'd put on the chosen scenario?
  What evidence would change the band by one rung?"*

### Reflection layer probes (simulate_hypothesis)
- *"What does the chosen scenario NOT cover that should be
  monitored?"*
- *"What's the early signal that the chosen scenario is wrong?"*
- *"Whose perspective haven't we tested the hypothesis against?"*

---

## 5 · Get Perspectives — probes NEED AUTHORING (content below)

Voice header (verbatim from `submodules.py:75-89`):

> … You are gathering what the chosen persona would prioritise.
> Probe accordingly. … (Synthesis: in the persona's voice, first-
> person where natural, tier markers still required …)

**Q6 lock applies:** quality bar is provisional until first render
exists. The probes below are the proposed first authoring; the live
artefact's judgment becomes the reference once judged deck-grade.

**Probe content authored for Stage 2 (provisional):**

### Framing layer probes (get_perspective)
- *"Whose perspective are you trying to bring in — and why now?
  (Founder you're seeking to challenge? Regulator? Auditor? A
  hostile competitor?)"*
- *"What would that persona ask FIRST about your situation — before
  you brief them?"*
- *"What's the bias you suspect that persona carries — and is
  bringing it in IN SPITE of the bias the value or BECAUSE of it?"*

### Grounding layer probes (get_perspective)
- *"What evidence does this persona privilege — what kind of input
  do they trust?"*
- *"What's the evidence this persona would DISCOUNT or
  RE-INTERPRET?"*
- *"What's the question this persona would ask the user that they
  WOULDN'T ask themselves?"*

### Synthesis layer probes (get_perspective — divergent, not convergent)
- *"In the persona's first-person voice: what's their reading of
  your situation? Where do they AGREE with the diagnosis you've
  already framed?"*
- *"Where do they DISAGREE? Where do they see a blind-spot you
  haven't?"*
- *"What would they want you to do differently — and what's the
  one move they'd push back hard on?"*

### Reflection layer probes (get_perspective)
- *"Of the persona's challenges, which is the one you find HARDEST
  to dismiss?"*
- *"What's the question you wish you'd asked the persona but didn't
  in this session?"*
- *"What other persona's view would change the picture again?"*

**Note (Q6):** the artefact shape from Get-perspectives is divergent —
not convergent. The pptx exporter's locked deck order doesn't have a
slot for "persona spread + agreement map + conflict map + per-persona
blind-spots." Per the deck-gate verdict (`JC_TL_S0_deck_gate_verdict.md`),
this is the TWO-TRACK BUILD trigger. Stage 2's Get-perspectives ship
is GATED on the Decks upgrade.

---

## 6 · Stage-2 implementation contract (load-bearing)

When Stage 2 wires the other three paths, the implementation MUST:

1. **Persist the authored probes** at a path-distinct location.
   Suggested: `services/solva_v2/probes.py` — module-level constants
   `DEVELOP_STRATEGY_PROBES`, `SIMULATE_HYPOTHESIS_PROBES`,
   `GET_PERSPECTIVE_PROBES`, each a `Dict[str, List[str]]` keyed by
   layer name.
2. **Wire the probes into the user-facing prompt** via the
   orchestrator's layer-entry hook — the LLM's voice already drives
   the conversation; the probes are the **deliberate-steps surface**
   the user sees as cues, so the conversation stays guided rather
   than emergent-only. This satisfies the dispatch's "deliberate
   steps, not folded invisibly inside grounding."
3. **Allow user-skip per probe** — the experience is a conversation,
   not a form. The probes are PROMPTS the LLM can re-cast in its own
   register if the user's reply already addresses them.
4. **Surface in the sprint memo:** for each path, paste the probe
   content verbatim into the memo with the file:line they live at,
   so reviewers can verify the probes are real before signing off
   the path.

---

## 7 · STOP-and-show verdict (combined with S0-Q2)

| Path | Probe verdict |
|---|---|
| Diagnosis / `seek_clarity` | **EXIST** (emergent under voice; produced MYDAWA) — Stage 1 surfaces them as deliberate steps |
| Develop Strategy | **NEED AUTHORING** — content above; commit to `services/solva_v2/probes.py` in Stage 2 |
| Test Hypothesis | **NEED AUTHORING** — content above; commit to `services/solva_v2/probes.py` in Stage 2 |
| Get Perspectives | **NEED AUTHORING** — content above; commit to `services/solva_v2/probes.py` in Stage 2 + GATED on Decks upgrade per Q6 + Q2 deck-gate verdict |

Stage 0 probe-provenance verdict: **PASS — probe content authored
per path, ready for Stage 2 wiring.** Diagnosis Stage 1 proceeds
unblocked (uses emergent probes under voice).
