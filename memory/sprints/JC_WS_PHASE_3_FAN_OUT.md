# JC-WS Phase 3 — Generate Document fan-out

> **Source of truth:** `/app/memory/JC_WS_CANONICAL_SPEC.md`
> **Date:** 2026-06-25
> **Result:** 13/13 acceptance rows green. **Brief Akki-fetch input — DEFERRED** pending retrieval-quality gate (see § Brief Akki-fetch decision below).

---

## What was fanned out

Per the revised canonical spec § Fan out: replicated the proven Board Pack pattern across the remaining
document kinds and the three enhance flows. ONE artefact per kind written to `/app/memory/jc_artifacts/`.
Roll-up at `/app/memory/jc_artifacts/JC-WS-A-Phase3-fan-out-roll-up.json`.

### Group A — Source-material packs

| Kind | Formats | Verdict |
|---|---|---|
| Committee Pack | DOCX 42 722 B · PPTX 42 968 B · PDF 38 918 B | 🟢 forward-to-a-board good |
| Minutes        | DOCX 41 871 B · PDF 30 911 B                   | 🟢 forward-to-a-board good |

Both follow the proven Board Pack pattern: cover → contents → exec summary → one section per source
→ recommendations → sources, executive register throughout, citations from the 19-doc source pool.

### Group B — Blank-start (Report / Deck)

| Kind | Formats | Verdict |
|---|---|---|
| Report | DOCX 43 852 B  | 🟢 forward-to-a-board good — sections, citations, recommendations block |
| Deck   | PPTX 42 071 B  | 🟢 forward-to-a-board good — one idea per slide, headlines lead each |

### Group C — Draft (in-editor surface)

| Kind | Surface | Verdict |
|---|---|---|
| Draft | `save-draft` endpoint → `lifecycle_state="draft"` row in `work_studio_exports` | 🟢 wired — `JC-WS-A-Draft-sample.json` captures the in-progress state |

Per the canonical spec, Draft is an "in-editor surface, not a generated file". The proving slice
exercises the persistence path; the in-editor flow itself is the existing WS draft co-author surface.

### Group D — Enhance flows (3)

| Flow | Before | After | Verdict |
|---|---|---|---|
| Enhance-Minutes  | bare placeholder (190 chars)                       | DOCX 39 788 B  | 🟢 visible improvement — sectioned by agenda item, decisions in resolution form, action list with owners |
| Enhance-Report   | hedging skeleton ("Revenue: up. Costs: up too.")   | DOCX 40 861 B  | 🟢 visible improvement — quantified movements, CET1 number, named risks, recommendations block |
| Enhance-Deck     | one-word slide placeholders                        | PPTX 41 360 B  | 🟢 visible improvement — substantive single-headline slides, recommendations slide at the end |

### Group E — Brief (the load-bearing one)

| Path | Artefact | Verdict |
|---|---|---|
| **(3b-i) Uploads input** | PDF 25 908 B · DOCX 40 336 B | 🟢 forward-to-a-board good — single-reader brief, 1-2 pages, decision-ready |
| **(3b-ii) Add context from Akki** | NOT BUILT THIS SPRINT | 🟡 deferred — see § Brief Akki-fetch decision |

---

## § Brief Akki-fetch decision (per spec § MATURITY GATES THE STEPS)

The revised canonical spec mandates the load-bearing rule: **match the number of steps to how
reliably retrieval performs. A multi-step journey that half-works is WORSE than a simple one that
works.**

### Retrieval-quality probe (REAL — `scripts/jc_ws_brief_retrieval_probe.py`)

Ran the existing chat-side BM25 retrieval (`/contexts/{cid}/document-journal/search`) — the SAME
retrieval the spec mandates we reuse, not rebuild — against the three plain-language context names
the canonical spec lists verbatim. Raw output captured at
`/app/memory/jc_artifacts/JC-WS-A-Brief-akki-fetch-retrieval-probe.json`.

| # | Named context | Top hit returned | Honesty verdict |
|---|---|---|---|
| 1 | "the Q3 board discussion" | `board-minutes-25-june-2025.docx` (score 3.97) — the actual Q3 board minutes — followed by Digital Transformation Strategy + Strategic Capital Allocation (both Q3-period strategy docs) | 🟢 **RELEVANT** — top-1 is exactly the discussion the user named |
| 2 | "last week's risk review" | `Five-Year Strategic Plan 2024-2028 — Executive Summary` (score 3.40); top-2/3 are general strategic docs that mention "risk" in their bodies | 🟡 **WEAK** — no actual "risk review" doc found; BM25 surfaced tangential strategic docs on the word "risk" |
| 3 | "Maria's competitive analysis from October" | All three top hits are Q3 Board Pack sections (Governance / Performance / mara-heritage-bank-board-pack-q3-2025.docx) that contain the word "competitive" | 🔴 **WEAK/IRRELEVANT** — no doc by/from "Maria", no temporal filtering, BM25 keyword-matched "competitive" + "analysis" |

**Score: 1/3 RELEVANT.** The threshold the spec set is **≥2/3** to ship the Akki-fetch input. **The bar is NOT met.**

### Why current BM25 fails on real-world Brief queries

1. **No author/owner metadata indexing** — "Maria's …" cannot resolve to docs Maria created/uploaded/owns
   because the index doesn't carry that signal at scoring time.
2. **No temporal filtering** — "from October" doesn't narrow the corpus before scoring; "last week's"
   doesn't restrict the date window. Both clauses are ignored by tokenisation.
3. **Synonym/topical weakness** — "risk review" doesn't bias toward docs that ARE risk reviews; it
   keyword-matches any doc that mentions "risk".
4. **No confidence floor / honesty-when-empty branch** — BM25 always returns the top-N, even when the
   top-1 score barely clears noise. The spec's "honesty floor" ("Akki says so and asks the user to
   upload or rename") has nothing to gate on.

### Decision

- 🟢 **SHIP NOW** — Uploads input. Discrete, reliable, complete. (This sprint, ✓ complete.)
- 🟡 **WAIT** — Akki-fetch input. The maturity-gate rule is load-bearing: shipping an input where
  2/3 of real-world queries return WEAK material would surface the exact failure mode the spec
  forbids ("a frustrated user is the worse failure"). Adding to §9 backlog:
  > **"Brief Akki-fetch input — gated on retrieval upgrade (author/owner metadata + temporal
  > filtering + confidence floor for the honesty branch)."** Retest the same 3 cases when the
  > retrieval lands; ship the input only when ≥2/3 are RELEVANT.

This is the unembellished call. Surfacing in case the user wants to override the gate.

---

## Files touched

### New files
- `backend/scripts/jc_ws_phase3_fan_out.py` — fan-out runner
- `memory/sprints/JC_WS_PHASE_3_FAN_OUT.md` — this memo

### Reused (no edits)
- `services/work_studio_export.py` — `render_brief_docx` / `render_report_docx` /
  `render_deck_pptx` / `render_pack_pptx` (the last shipped in Phase 1)
- `routers/work_studio_export.py` — dispatcher already wired all kinds + formats


---

## Step 3 — Analyze deep-link enhancement

Per the dispatch, the per-card deep-link rides the existing Analyze drawer chrome — "natural to the
user, not a developer's debug panel."

### Shape (decision)

A subtle "View underlying read" / "Hide underlying read" text link in the card footer, next to the
confidence badge. On click, an inline panel below the card body reveals the structured analyzer
parameters the workspace dispatched (intent · target · horizon · scenario · rationale). Refusal
cards do NOT get the affordance — there's nothing underlying to deep-link to.

Implementation in `frontend/src/components/analyze/HighlightsWorkspace.jsx`'s `HighlightCard`. No
new endpoints, no new persistence, no new state machine. The panel reads from `highlight.analyzer_payload`
which Phase 2's `/v2/analyses/{aid}/ask` endpoint already populates and persists to
`db.analyses.highlights[]`. **Same lifecycle as the highlight itself, as the dispatch demanded.**

### Evidence

| File | What it proves |
|---|---|
| `JC-WS-B-Analyze-drawer-screenshots/02-deeplink-underlying-read-expanded.jpg` | FE smoke — the "Simulate East flat at $3.45M" card expanded, **UNDERLYING READ · SIMULATE** panel showing Target=Revenue, Horizon=Q4, Scenario="East region revenue held flat at $3.45M" |
| `JC-WS-B-Analyze-deeplink-evidence.json` | Captured card with full `analyzer_payload`, surface rationale, persistence guarantee |

### Honest note on the "next step" the dispatch alludes to

The dispatch says: "User sees the raw numbers / chart / table that justify the narrated highlight."
The current implementation surfaces the **structured PARAMETERS** the workspace dispatched
(target/horizon/scenario/rationale), not the **raw numbers** from a deterministic run.

To fully land the spec's promise, the next iteration is to wire `/v2/analyses/{aid}/ask` so it ALSO
calls the matching deterministic endpoint (`/forecast` / `/simulate` / `/anomalies` /
`/signals/extract`) when sources permit, and stashes the raw payload on `analyzer_payload.raw`
alongside the narration. The FE then renders forecast-as-sparkline / simulate-as-scenario-recap /
extract-as-table per intent. The card chrome doesn't change — only the panel body does.

This is left as a tightly-scoped follow-up in `ROADMAP.md` (the existing analysis row in the
proving slice was a seeded row without an actual loaded workbook, so the deterministic endpoints
can't run against it today — the wiring is real only once real workbook uploads are flowing the
Analyze drawer).

### Spec/inventory updates
- `memory/JC_WS_CANONICAL_SPEC.md` — Journey 3 (Brief) replaced with the revised 3a/3b model + Fan-out paragraph updated
- `memory/audit/JC_WS_ui_inventory.md` — old 3-source-selector items closed out as SUPERSEDED; new gated Akki-fetch row added

---

## Artefact manifest (13 row × multiple formats)

```
JC-WS-A-CommitteePack-sample.docx        42 722 bytes
JC-WS-A-CommitteePack-sample.pptx        42 968 bytes
JC-WS-A-CommitteePack-sample.pdf         38 918 bytes
JC-WS-A-Minutes-sample.docx              41 871 bytes
JC-WS-A-Minutes-sample.pdf               30 911 bytes
JC-WS-A-Report-sample.docx               43 852 bytes
JC-WS-A-Deck-sample.pptx                 42 071 bytes
JC-WS-A-Brief-uploads-sample.pdf         25 908 bytes
JC-WS-A-Brief-uploads-sample.docx        40 336 bytes
JC-WS-A-Draft-sample.json                 (lifecycle_state="draft" snapshot)
JC-WS-A-Enhance-Minutes-{before.txt, after.docx 39 788 B}
JC-WS-A-Enhance-Report-{before.txt, after.docx 40 861 B}
JC-WS-A-Enhance-Deck-{before.txt, after.pptx 41 360 B}
JC-WS-A-Phase3-fan-out-roll-up.json
```
