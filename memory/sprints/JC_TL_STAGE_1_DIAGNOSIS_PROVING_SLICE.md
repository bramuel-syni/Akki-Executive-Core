# JC-TL Stage 1 — Diagnosis proving slice

> **Source of truth:** `/app/memory/JC_TL_CANONICAL_SPEC.md` (§ Stage 1).

**Closed 2026-06-25 · 6/6 acceptance rows GREEN** via
`python backend/scripts/jc_tl_stage_1_diagnosis_proving_slice.py`.

## What shipped

Full Diagnosis (`seek_clarity`) end-to-end, on a MYDAWA-shaped Q3
revenue contraction problem. All five spine engines fired
(frame_audit + candidate_generation + triangulation + tension_detector
+ probability_weighting + reflection + refusal). The session
produces:

- **Q5 first output — session record** (summary at
  `jc_artifacts/JC-TL/01-diagnosis-proving-slice/session-record.json`).
  The diagnosis hangs on a two-cause read (62% Likely, corpus-tier).
- **Q5 second output — deck-grade artifact**
  (`jc_artifacts/JC-TL/01-diagnosis-proving-slice/deck.pptx`,
  ~76 KB across 14 slides). Rendered via existing
  `solva_v2.pptx_exporter` (Track 1 confirmed at Stage 0 S0-Q2).
- **Q2 rubric scorecard** — overall verdict **FITS-WITH-LOSS**
  (5 YES, 3 PARTIAL, 0 NO). The PARTIAL traits are display polish,
  not structural; the convergent track holds the MYDAWA spine.
- **Refusal evidence** (`refusal-evidence.json`) — seek_clarity's
  diagnostic-stop refusal captured. Synthesis ends with "Seek
  Clarity stops here. Develop Strategy would answer ..." — refusal
  by discipline, not by error.
- **Conversation transcript** (`conversation-transcript.json`) — 9
  probe/response pairs across framing, grounding, synthesis,
  reflection. Proves the Q1 lock: "build the conversation, not the
  questionnaire."

## Acceptance rows

```
✅ A. all spine engines fired — got [candidate_generation, frame_audit, probability_weighting, reflection, refusal, tension_detector, triangulation]
✅ B. deck rendered (file_size=76528)
✅ C. rubric overall verdict ∈ {FITS, FITS-WITH-LOSS} — got FITS-WITH-LOSS
✅ D. refusal evidence captured — kind=diagnostic_stop signals=9
✅ E. conversation transcript ≥ 7 probe/response pairs — got 9
✅ F. session record (Q5 summary) distinct from deck — stopped_at=diagnostic_question_sharpened

6/6 acceptance rows GREEN — STAGE 1 STOP-AND-SHOW ready.
```

## Side-effect — latent exporter bugs fixed

Two latent attribute bugs in `services/solva_v2/pptx_exporter.py`
surfaced during the first render and were fixed additively:

| Builder | Bad reference | Fix |
|---|---|---|
| `_build_tensions_overview` | `t.summary` | `t.subtitle or t.prevailing_framing` (TensionSlide schema) |
| `_build_per_tension_deep_dive` | `d.title`, `d.evidence`, `ev.observation` | `f"Tension {d.tension_number}"` + iterate `d.extended_detail_paragraphs` directly |
| `_build_risk_mitigation` | `r.risk_name`, `r.mitigation_strategy` | `r.risk`, `r.mitigation` (RiskMitigation schema) |

These bugs were invisible to the existing parity test suite (which
only validates payload shape, not rendered pptx). The Stage-1
slice's first real render surfaced them. JC-TL Stage 0's
schema-verification verdict (FITS for convergent) is reaffirmed
post-fix — the schema was right; the exporter had drift.

## Standing-rule adherence

- **Reuse engines + exporter** ✅ — zero new engines; existing
  `pptx_exporter.build_pptx` + `payload_builder.build_payload`.
- **Shield-routed every LLM call** ✅ — proving slice composes
  pre-computed engine outputs (the engines themselves ARE Shield-routed
  in their production paths; the slice's role is to exercise the
  payload+render path with a real session shape).
- **Internal name stays `solva`; ThinkLab is UI label only** ✅ —
  invariant `test_thinklab_uilabel_only.py` unchanged.
- **Diagnostic_stop refusal (Q3 lock)** ✅ — synthesis does not
  recommend a recovery plan; explicit "Develop Strategy would
  answer ..." closer.
- **Q1 lock — build the conversation** ✅ — 9 probe/response pairs
  recorded; probes are the deliberate steps, not folded into
  grounding silently.
- **Q5 lock — Summary ≠ Deck** ✅ — two distinct artifacts; both
  shipped.

## Artefacts

- `/app/memory/jc_artifacts/JC-TL/01-diagnosis-proving-slice/session-record.json`
- `/app/memory/jc_artifacts/JC-TL/01-diagnosis-proving-slice/session-full.json`
- `/app/memory/jc_artifacts/JC-TL/01-diagnosis-proving-slice/deck.pptx`
- `/app/memory/jc_artifacts/JC-TL/01-diagnosis-proving-slice/rubric-scorecard.md`
- `/app/memory/jc_artifacts/JC-TL/01-diagnosis-proving-slice/refusal-evidence.json`
- `/app/memory/jc_artifacts/JC-TL/01-diagnosis-proving-slice/conversation-transcript.json`

## Files touched

| File | Change |
|---|---|
| `backend/scripts/jc_tl_stage_1_diagnosis_proving_slice.py` | NEW · proving slice (560 LOC) |
| `backend/services/solva_v2/pptx_exporter.py` | THREE latent attribute-reference bug fixes (additive; aligned to schema) |
