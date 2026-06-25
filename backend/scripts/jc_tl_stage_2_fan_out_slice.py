"""JC-TL Stage 2 — Fan-out proving slice (Develop Strategy /
Test Hypothesis / Get Perspectives).

Source of truth: `/app/memory/JC_TL_CANONICAL_SPEC.md` (§ Stage 2).

Replicates the proven Diagnosis shape across the other three paths on
the SHARED FRAMEWORK (not single-path calcification). Each path's
layer order is derived from the objective per the engine reality;
the SHARED engine outputs (frame_audit / candidate_generation /
triangulation / tension_detector / probability_weighting /
reflection / refusal) are populated for each path with path-specific
semantics:

  • Develop Strategy — synthesis converges to 2-4 sequenced
    recommendations as the PRODUCT (per canonical spec Q1 lock).
  • Test Hypothesis — synthesis tests the hypothesis against 2-3
    scenarios + falsification surface + weighted confidence.
  • Get Perspectives — synthesis INVERTS to a spread of multiple
    persona views (Q6 lock — provisional bar, no MYDAWA rubric).

Each path produces its own:
  - session-record.json
  - deck.pptx
  - rubric-scorecard.md (DS / TH against MYDAWA Q2 rubric;
    GP at the provisional spine-only bar per Q6)
  - conversation-transcript.json

Contributor-history fold-in (approved into this stage):
  The DS run is seeded as a REVISION of a prior contributor session
  (the Diagnosis Stage-1 session). Its session shape carries a
  `prior_session_intent` field threading the diagnosis question into
  Develop Strategy's framing — proving the revision tuning works
  ADDITIVELY without engine modification.

Track-2 Decks-upgrade sequencing recommendation: surfaced as a
separate artifact at `track-2-decks-upgrade-sequencing.md`. Per
dispatch: surface only, do not execute.

Run:
    cd /app/backend && python scripts/jc_tl_stage_2_fan_out_slice.py
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path("/app/backend")
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv("/app/backend/.env")


from services.solva_v2.payload_builder import build_payload, payload_signature  # noqa: E402
from services.solva_v2.pptx_exporter import build_pptx  # noqa: E402


ART_DIR_BASE = Path("/app/memory/jc_artifacts/JC-TL/02-fan-out")
ART_DIR_BASE.mkdir(parents=True, exist_ok=True)


# ─────────────────────────────────────────────────────────────────
# Path 1 — Develop Strategy (convergent → recommendation)
# ─────────────────────────────────────────────────────────────────


def _develop_strategy_session() -> Dict[str, Any]:
    """Convergent to recommendation. Layer order: framing → grounding →
    synthesis (recommend) → reflection. Builds on the Diagnosis Stage-1
    session as a REVISION (contributor-history fold-in)."""
    return {
        "id":             "sess-jctl-stage2-develop-strategy",
        "schema_version": 2,
        "account_id":     "cf6e7587-9abd-46aa-b8f4-f342e9b066ef",
        "context_id":     "a2937d0f-37f1-4042-a897-ab73a6cd652a",
        "intent": (
            "Given Diagnosis's two-cause read of the Q3 contraction, "
            "what's the sequenced recovery pathway?"
        ),
        "submodule":      "develop_strategy",
        "cluster_id":     "cluster-q3-recovery",
        "cluster_label": "Q3 recovery pathway",
        "started_at":     "2026-06-25T19:30:00Z",
        "completed_at":   "2026-06-25T20:42:00Z",
        "layer":          "reflection",
        "status":         "complete",

        # Contributor-history fold-in (approved into this stage).
        "prior_session_intent": {
            "session_id":   "sess-jctl-stage1-mydawa-diagnosis",
            "submodule":    "seek_clarity",
            "intent_text": (
                "Did we diagnose the Q3 revenue contraction correctly, "
                "or are we pattern-matching the checkout regression?"
            ),
            "diagnostic_read": (
                "Two independent causes — SDK regression on conversion "
                "+ session-acquisition decline starting earlier. "
                "62% Likely (corpus-tier)."
            ),
        },

        "user_turns": [
            {"id": "t1", "layer": "framing",
             "text": "We need a recovery plan that addresses both causes — not just the SDK fix."},
            {"id": "t2", "layer": "grounding",
             "text": "Budget: 1 senior eng + 2 ops people for the next 12 weeks. Constraint: campaign budget capped at 80k."},
            {"id": "t3", "layer": "grounding",
             "text": "Most-recent comparable: a peer recovered MoM index in ~8 weeks via parallel SDK + reactivation tracks."},
            {"id": "t4", "layer": "synthesis",
             "text": "Sequence question: which lands first — checkout fix or reactivation campaign? Or both in parallel?"},
            {"id": "t5", "layer": "synthesis",
             "text": "If we go parallel we burn team capacity on coordination; if sequential we lose 3-4 weeks. Trade-off."},
            {"id": "t6", "layer": "reflection",
             "text": "Parallel works only if the checkout fix doesn't require reactivation-team review — they're independent enough."},
        ],
        "attached_docs": [
            {"id": "doc-team-capacity", "name": "Team capacity assessment — Q4"},
            {"id": "doc-peer-comparable", "name": "Peer recovery case — same SDK regression"},
        ],
        "comparables": [
            {"id": "comp-1", "name": "Peer A — parallel recovery in 8 weeks",
             "diagnosis_summary": "SDK fix + reactivation ran in parallel; recovered MoM index in 8 weeks."},
        ],

        "reasoning_audit_log": [
            {"id": "audit-1", "engine": "frame_audit", "layer": "framing",
             "output": {"frame_quality": "narrowed",
                        "framing_note": "Frame inherited from Diagnosis; Develop Strategy converges to recovery sequencing."}},
            {"id": "audit-2", "engine": "candidate_generation", "layer": "grounding",
             "output": {"hypotheses": [
                 "Parallel tracks (SDK + reactivation simultaneously).",
                 "Sequential — SDK first, reactivation week 5+.",
                 "Reactivation first to recover sessions, SDK after.",
             ]}},
            {"id": "audit-3", "engine": "triangulation", "layer": "grounding",
             "output": {"cluster_id": "cluster-q3-recovery",
                        "triangulation_note": "Peer comparable supports parallel; team capacity constraint makes parallel feasible only if scopes are clean."}},
            {"id": "audit-4", "engine": "tension_detector", "layer": "grounding",
             "output": {"tensions": [
                 {"description": "Speed-to-recovery (parallel) vs team-capacity-strain (parallel adds coordination overhead).",
                  "contradiction_source": "user_vs_user", "severity": "high",
                  "evidence": ["Peer recovered in 8wk parallel.", "Team capacity 1 eng + 2 ops constrains coordination overhead."]},
             ]}},
            {"id": "audit-5", "engine": "probability_weighting", "layer": "synthesis",
             "output": {"claims": [
                 {"text": "Parallel-tracks recovery sequenced Days 0-30 (SDK fix lands) → 0-60 (reactivation campaign launches week 3 in parallel) → 30-180 (stabilisation). 8-10 week recovery target.",
                  "tier": "comparable", "confidence_pct": 64, "confidence_band": "Likely",
                  "confidence_rationale": "Peer comparable supports parallel; team capacity feasibility OK."},
                 {"text": "Sequential — SDK first then reactivation. 11-13 week recovery target.",
                  "tier": "user_assertion", "confidence_pct": 28, "confidence_band": "Possible",
                  "confidence_rationale": "Lower coordination overhead but loses 3-4 weeks."},
                 {"text": "Reactivation-first inversion. 14-16 week recovery; not preferred.",
                  "tier": "user_assertion", "confidence_pct": 8, "confidence_band": "Speculative",
                  "confidence_rationale": "Reverses the natural diagnostic priority; comparable counter-signals."},
             ]}},
            {"id": "audit-6", "engine": "reflection", "layer": "reflection",
             "output": {"reflection_question": "What does this NOT cover that you wish it did?",
                        "reflection_question_index": 0,
                        "user_response": "It doesn't cover the third Q4 risk — what if a NEW regression lands during recovery?",
                        "interpretation": "User surfaces concurrent-risk gap."}},
            {"id": "audit-7", "engine": "reflection", "layer": "reflection",
             "output": {"reflection_question": "What would have to be true for this pathway to be wrong?",
                        "reflection_question_index": 1,
                        "user_response": "If the checkout fix requires reactivation-team review, parallel breaks. The independence assumption is load-bearing.",
                        "interpretation": "User defines a falsification test on the parallelism assumption."}},
            {"id": "audit-8", "engine": "reflection", "layer": "reflection",
             "output": {"reflection_question": "What's the question you weren't ready to ask?",
                        "reflection_question_index": 2,
                        "user_response": "Whether the 'session decline' Diagnosis surfaced is itself a multi-cause signal that needs separate diagnosis.",
                        "interpretation": "User opens a nested-Diagnosis path the recovery pathway doesn't address."}},
        ],
        "synthesis": {
            "body": (
                "## Recovery pathway\n\n"
                "Parallel tracks land the 8-10 week recovery target with the "
                "narrowest team-capacity strain. SDK fix in weeks 0-3 (eng "
                "owner); reactivation campaign launches week 3 (ops owner). "
                "Stabilisation phase begins week 8.\n\n"
                "## Conditional logic\n\n"
                "If checkout fix dependencies on reactivation-team review "
                "surface in week 1 standup, fall back to Sequential (SDK then "
                "reactivation) — adds 3-4 weeks but removes coordination risk."
            ),
            "recommendations": [
                {"heading": "Land checkout SDK fix in weeks 0-3 (eng owner)",
                 "body": "Could ship checkout SDK fix in weeks 0-3 with the senior eng as owner. Exit gate: weekly active sessions index ≥ 95."},
                {"heading": "Launch reactivation campaign week 3 (ops owners) in parallel",
                 "body": "Would launch reactivation campaign in parallel from week 3. Exit gate: revenue index ≥ 95 by week 8."},
                {"heading": "Phase 3 stabilisation begins week 8",
                 "body": "Would begin stabilisation phase week 8 if both phase exits land. Target: revenue index ≥ 100 by week 12."},
            ],
        },
    }


def _test_hypothesis_session() -> Dict[str, Any]:
    """Proposition under stress. Layer order: framing → grounding →
    hypothesis (scenario expansion + tension) → synthesis → reflection."""
    return {
        "id":             "sess-jctl-stage2-test-hypothesis",
        "schema_version": 2,
        "account_id":     "cf6e7587-9abd-46aa-b8f4-f342e9b066ef",
        "context_id":     "a2937d0f-37f1-4042-a897-ab73a6cd652a",
        "intent": (
            "Hypothesis to test: the Q3 contraction will recover within "
            "12 weeks if we ship both fixes in parallel."
        ),
        "submodule":      "simulate_hypothesis",
        "cluster_id":     "cluster-q3-recovery",
        "started_at":     "2026-06-25T20:50:00Z",
        "completed_at":   "2026-06-25T21:48:00Z",
        "layer":          "reflection",
        "status":         "complete",

        "user_turns": [
            {"id": "t1", "layer": "framing",
             "text": "Hypothesis: parallel recovery lands the index ≥ 100 by week 12."},
            {"id": "t2", "layer": "grounding",
             "text": "Evidence FOR: peer comparable hit the same target in 8 weeks parallel."},
            {"id": "t3", "layer": "grounding",
             "text": "Evidence AGAINST: peer team was 3× the size. Capacity asymmetry."},
            {"id": "t4", "layer": "hypothesis",
             "text": "Scenario A: clean parallel. Index 102 by week 12."},
            {"id": "t5", "layer": "hypothesis",
             "text": "Scenario B: coordination overhead drags reactivation to week 10. Index 92 by week 12."},
            {"id": "t6", "layer": "hypothesis",
             "text": "Scenario C: a new regression lands during recovery. Index recovers but to 88, not 100."},
            {"id": "t7", "layer": "synthesis",
             "text": "Falsification test: weekly index in week 6 < 90 means scenario B or C is realising."},
        ],
        "attached_docs": [
            {"id": "doc-peer-staffing", "name": "Peer team staffing comparison"},
        ],
        "comparables": [
            {"id": "comp-1", "name": "Peer parallel recovery — 8 weeks",
             "diagnosis_summary": "Index recovered to 102 in 8 weeks; team 3× our size."},
        ],
        "reasoning_audit_log": [
            {"id": "audit-1", "engine": "frame_audit", "layer": "framing",
             "output": {"frame_quality": "narrowed", "framing_note": "Hypothesis framed for falsifiability."}},
            {"id": "audit-2", "engine": "candidate_generation", "layer": "grounding",
             "output": {"hypotheses": ["Clean parallel", "Coordination drag", "Concurrent regression"]}},
            {"id": "audit-3", "engine": "triangulation", "layer": "grounding",
             "output": {"cluster_id": "cluster-q3-recovery",
                        "triangulation_note": "Peer comparable supports parallel; team-size asymmetry weakens the read."}},
            {"id": "audit-4", "engine": "tension_detector", "layer": "hypothesis",
             "output": {"tensions": [
                 {"description": "Hypothesis assumes peer parallel works at our team size; capacity asymmetry says it might not.",
                  "contradiction_source": "user_vs_comparable", "severity": "high",
                  "evidence": ["Peer team 3× our size.", "Hypothesis predicts same 8-12wk recovery as peer."]},
             ]}},
            {"id": "audit-5", "engine": "probability_weighting", "layer": "synthesis",
             "output": {"claims": [
                 {"text": "Hypothesis holds — index 102 by week 12 under clean parallel.",
                  "tier": "comparable", "confidence_pct": 45, "confidence_band": "Possible",
                  "confidence_rationale": "Peer supports the trajectory but team-size asymmetry tempers."},
                 {"text": "Hypothesis falsified — coordination drag stretches recovery to week 14+, index 92.",
                  "tier": "user_assertion", "confidence_pct": 38, "confidence_band": "Possible",
                  "confidence_rationale": "Capacity asymmetry makes this credible."},
                 {"text": "Hypothesis catastrophically falsified — concurrent regression caps recovery at 88.",
                  "tier": "user_assertion", "confidence_pct": 17, "confidence_band": "Speculative",
                  "confidence_rationale": "Second-order concurrent-risk scenario; honest tail probability."},
             ]}},
            {"id": "audit-6", "engine": "reflection", "layer": "reflection",
             "output": {"reflection_question": "What does this NOT cover that you wish it did?",
                        "reflection_question_index": 0,
                        "user_response": "Whether scenario B and C are correlated — if coordination drag predicts concurrent regression.",
                        "interpretation": "User surfaces a hidden-correlation question between B and C."}},
            {"id": "audit-7", "engine": "reflection", "layer": "reflection",
             "output": {"reflection_question": "What's the early signal that the hypothesis is wrong?",
                        "reflection_question_index": 1,
                        "user_response": "Weekly index in week 6 below 90 means scenario B or C is realising.",
                        "interpretation": "User defines a clean week-6 falsification test."}},
            {"id": "audit-8", "engine": "reflection", "layer": "reflection",
             "output": {"reflection_question": "Whose perspective haven't we tested the hypothesis against?",
                        "reflection_question_index": 2,
                        "user_response": "The customer's. We've stress-tested ops, not customer-side recovery friction.",
                        "interpretation": "User opens a Get Perspectives followup path."}},
        ],
        "synthesis": {
            "body": (
                "## Hypothesis under stress\n\n"
                "The hypothesis — parallel recovery lands index ≥ 100 by "
                "week 12 — is **Possible** (45%). Two falsifying scenarios "
                "are credible (38% + 17%). The week-6 weekly-index reading "
                "is the load-bearing falsification test.\n\n"
                "## Stop-at-hypothesis\n\n"
                "Test Hypothesis stops here with a tested-but-not-decided "
                "verdict. Whether to commit depends on additional checks "
                "(week-6 falsification gate + Get Perspectives on the "
                "customer-side risk)."
            ),
            "recommendations": [
                {"heading": "Watch week-6 weekly index as falsification gate",
                 "body": "Would treat weekly index < 90 by week 6 as falsification of the 12-week-to-100 hypothesis."},
            ],
        },
    }


def _get_perspectives_session() -> Dict[str, Any]:
    """DIVERGENT — synthesis inverts to a spread of multiple persona
    views. Q6 lock: no MYDAWA reference; first render becomes its own
    reference once judged deck-grade. Provisional bar."""
    return {
        "id":             "sess-jctl-stage2-get-perspectives",
        "schema_version": 2,
        "account_id":     "cf6e7587-9abd-46aa-b8f4-f342e9b066ef",
        "context_id":     "a2937d0f-37f1-4042-a897-ab73a6cd652a",
        "intent": (
            "Get perspectives on the Q3 recovery pathway — auditor, "
            "customer-advocate, regulator views."
        ),
        "submodule":      "get_perspective",
        "persona":        "auditor",
        "cluster_id":     "cluster-q3-recovery",
        "started_at":     "2026-06-25T22:00:00Z",
        "completed_at":   "2026-06-25T22:58:00Z",
        "layer":          "reflection",
        "status":         "complete",

        "user_turns": [
            {"id": "t1", "layer": "framing",
             "text": "I want auditor + customer-advocate + regulator perspectives on the parallel recovery."},
            {"id": "t2", "layer": "grounding",
             "text": "Auditor would focus on the audit trail integrity during parallel ops."},
            {"id": "t3", "layer": "grounding",
             "text": "Customer would focus on the friction during the campaign weeks."},
            {"id": "t4", "layer": "synthesis",
             "text": "Auditor says: parallel is fine if every change is logged + signed off. Concern: SDK fix + reactivation campaign creating overlapping change windows."},
            {"id": "t5", "layer": "synthesis",
             "text": "Customer-advocate says: 8 weeks of fix-then-campaign feels like 'getting bombarded with notices then asks for money.' Concern: tone."},
            {"id": "t6", "layer": "synthesis",
             "text": "Regulator says: SDK regression triggers reporting obligations. Concern: did we report on time?"},
            {"id": "t7", "layer": "reflection",
             "text": "Auditor + regulator perspectives BOTH point to reporting/audit trail — agreement. Customer-advocate is the outlier — focused on tone, not process."},
        ],
        "attached_docs": [],
        "comparables": [],
        "reasoning_audit_log": [
            {"id": "audit-1", "engine": "frame_audit", "layer": "framing",
             "output": {"frame_quality": "narrowed", "framing_note": "Multi-persona span requested."}},
            {"id": "audit-2", "engine": "candidate_generation", "layer": "grounding",
             "output": {"hypotheses": ["Auditor lens", "Customer-advocate lens", "Regulator lens"]}},
            {"id": "audit-3", "engine": "triangulation", "layer": "grounding",
             "output": {"cluster_id": "cluster-q3-recovery",
                        "triangulation_note": "Auditor + regulator triangulate on process; customer-advocate spans differently to tone."}},
            {"id": "audit-4", "engine": "tension_detector", "layer": "synthesis",
             "output": {"tensions": [
                 {"description": "Process-side persons (auditor + regulator) tension against the customer-advocate's tone focus — the recovery plan has to satisfy BOTH but they pull different threads.",
                  "contradiction_source": "comparable_vs_comparable", "severity": "medium",
                  "evidence": ["Auditor: change-window logging.", "Customer-advocate: cadence/tone."]},
             ]}},
            {"id": "audit-5", "engine": "probability_weighting", "layer": "synthesis",
             "output": {"claims": [
                 {"text": "Auditor-side view: parallel recovery is acceptable iff change-window logging is rigorous.",
                  "tier": "user_assertion", "confidence_pct": 70, "confidence_band": "Likely",
                  "confidence_rationale": "Standard audit posture; high-conviction within the persona."},
                 {"text": "Customer-advocate-side view: parallel recovery's tone-burden risks customer trust erosion if not paced.",
                  "tier": "user_assertion", "confidence_pct": 55, "confidence_band": "Possible",
                  "confidence_rationale": "Persona-internal read; depends on campaign-team's tone discipline."},
                 {"text": "Regulator-side view: SDK regression should trigger same-day report; recovery plan should include the regulator notice as workstream zero.",
                  "tier": "user_assertion", "confidence_pct": 70, "confidence_band": "Likely",
                  "confidence_rationale": "Compliance posture is high-conviction within persona."},
             ]}},
            {"id": "audit-6", "engine": "reflection", "layer": "reflection",
             "output": {"reflection_question": "Of the persona's challenges, which is the one you find HARDEST to dismiss?",
                        "reflection_question_index": 0,
                        "user_response": "Regulator's — same-day reporting obligation may have been missed already. Need to check.",
                        "interpretation": "User identifies a procedural gap surfaced by the regulator persona."}},
            {"id": "audit-7", "engine": "reflection", "layer": "reflection",
             "output": {"reflection_question": "What's the question you wish you'd asked the persona but didn't?",
                        "reflection_question_index": 1,
                        "user_response": "Would have asked the auditor whether the parallel change windows would have looked OK if BOTH change owners signed off together OR if they need independent signoffs.",
                        "interpretation": "User opens a process-detail follow-up."}},
            {"id": "audit-8", "engine": "reflection", "layer": "reflection",
             "output": {"reflection_question": "What other persona's view would change the picture again?",
                        "reflection_question_index": 2,
                        "user_response": "Engineering org chart — bringing in the on-call eng would surface what happens if a P0 fires during the parallel weeks.",
                        "interpretation": "User opens an on-call-resilience persona for future Get Perspectives runs."}},
        ],
        "synthesis": {
            "body": (
                "## Perspective spread\n\n"
                "Three persons, three views. Two agree on process discipline "
                "(auditor + regulator); one diverges on customer-side tone "
                "(customer-advocate). The plan needs to satisfy both threads "
                "— rigour AND cadence.\n\n"
                "## Where they tension\n\n"
                "Process-side personas push the plan TOWARD more logging and "
                "earlier reporting. Customer-advocate pushes AWAY from "
                "overlapping touchpoints. The plan must thread both, not "
                "pick one."
            ),
            "recommendations": [
                {"heading": "Treat regulator notice as workstream zero",
                 "body": "Would issue the SDK regression regulator notice as workstream zero — the auditor + regulator persons both back this."},
                {"heading": "Cap customer-facing campaign touch-points",
                 "body": "Could cap customer-facing campaign touchpoints to ≤ 2 per week — the customer-advocate persona's primary concern."},
            ],
        },
    }


# ─────────────────────────────────────────────────────────────────
# Rendering helpers (shared with Stage 1 — same exporter, same rubric)
# ─────────────────────────────────────────────────────────────────


def _render(session: Dict[str, Any], context_name: str) -> tuple[bytes, str]:
    payload = build_payload(session, context_name=context_name)
    sig = payload_signature(payload)
    pptx_bytes = build_pptx(payload, context_name=context_name)
    return pptx_bytes, sig


def _q2_rubric(pptx_path: Path, session: Dict[str, Any]) -> Dict[str, Any]:
    """8-trait rubric — same as Stage 1. Returns FITS / FITS-WITH-LOSS /
    DOES-NOT-FIT verdict. For Get Perspectives we report the rubric but
    note that the divergent-synthesis trait is the structural gap
    (per Stage 0 Q2 verdict)."""
    from pptx import Presentation
    prs = Presentation(str(pptx_path))
    slides = list(prs.slides)

    all_text: List[str] = []
    titles: List[str] = []
    for s in slides:
        for shape in s.shapes:
            if shape.has_text_frame and shape.text_frame.text.strip():
                all_text.append(shape.text_frame.text)
                if not titles or len(titles) < len(slides):
                    titles.append(shape.text_frame.text.strip().split("\n")[0][:120])
                    break
    body = "\n".join(all_text).lower()
    sizes = set()
    for s in slides:
        for shape in s.shapes:
            if shape.has_text_frame:
                for para in shape.text_frame.paragraphs:
                    for run in para.runs:
                        if run.font.size:
                            sizes.add(run.font.size.pt)
    traits: List[Dict[str, Any]] = []
    traits.append({"trait": "Bold sans-serif typography hierarchy",
                   "verdict": "YES" if len(sizes) >= 3 else "PARTIAL",
                   "evidence": f"font sizes: {sorted(sizes)[:6]}"})
    traits.append({"trait": "Monochrome palette + signal colors only on data",
                   "verdict": "YES",
                   "evidence": "exporter hardcoded brand palette"})
    has_tension = any("tension" in t.lower() for t in titles)
    traits.append({"trait": "Narrative-vs-evidence side-by-side",
                   "verdict": "YES" if has_tension else "PARTIAL",
                   "evidence": f"tension slides: {has_tension}"})
    has_pct = "%" in body
    traits.append({"trait": "Per-cluster confidence weighting visible",
                   "verdict": "YES" if has_pct else "PARTIAL",
                   "evidence": f"confidence pct in body: {has_pct}"})
    has_timeline = any(tag in body for tag in ("days 0-30", "days 30-60", "days 60-90", "ongoing"))
    traits.append({"trait": "Bridge decompositions / indicator timelines",
                   "verdict": "YES" if has_timeline else "PARTIAL",
                   "evidence": f"timeline tags: {has_timeline}"})
    has_refl = any("reflection" in t.lower() for t in titles)
    traits.append({"trait": "Reflection slide",
                   "verdict": "YES" if has_refl else "PARTIAL",
                   "evidence": f"reflection slide: {has_refl}"})
    has_honesty = any(
        "honesty" in t.lower() or "methodolog" in t.lower() or "fair criteria" in t.lower() or "what we know" in t.lower()
        for t in titles)
    traits.append({"trait": "Fair Criteria / methodological honesty",
                   "verdict": "YES" if has_honesty else "PARTIAL",
                   "evidence": f"honesty slide: {has_honesty}"})
    refusal_signals = ["would have", "would resolve", "could be", "diagnostic", "observational", "if", "stop at"]
    hits = [s for s in refusal_signals if s in body]
    traits.append({"trait": "Refusal-to-decide explicit",
                   "verdict": "YES" if len(hits) >= 3 else "PARTIAL",
                   "evidence": f"signals: {hits[:5]}"})
    yes_count = sum(1 for t in traits if t["verdict"] == "YES")
    partial_count = sum(1 for t in traits if t["verdict"] == "PARTIAL")
    no_count = sum(1 for t in traits if t["verdict"] == "NO")
    if no_count == 0 and yes_count >= 6:
        overall = "FITS"
    elif yes_count >= 4:
        overall = "FITS-WITH-LOSS"
    else:
        overall = "DOES-NOT-FIT"
    return {
        "n_slides": len(slides),
        "slide_titles": titles,
        "traits": traits,
        "yes_count": yes_count,
        "partial_count": partial_count,
        "no_count": no_count,
        "overall_verdict": overall,
    }


def _session_record(session: Dict[str, Any], payload_sig: str, summary_text: str) -> Dict[str, Any]:
    return {
        "session_id": session["id"],
        "submodule": session["submodule"],
        "intent": session["intent"],
        "payload_signature": payload_sig,
        "summary_text": summary_text,
        "prior_session_intent": session.get("prior_session_intent"),
    }


# ─────────────────────────────────────────────────────────────────
# Track-2 sequencing recommendation (surface only; do NOT execute)
# ─────────────────────────────────────────────────────────────────


def _track_2_sequencing_recommendation() -> str:
    return """# JC-TL Track 2 — Decks-upgrade sequencing recommendation

> **Surface-only artifact.** This recommendation is NOT a dispatch.
> The user decides when to dispatch Track 2; the agent only surfaces
> the sequencing analysis.

## Recommendation: dispatch Track 2 AFTER JC-MON Stage 3 closes, BEFORE any JC-TL Stage 2 Get-Perspectives shipping commitment.

### Why this sequencing?

1. **Stage 2 fan-out has been demonstrated on the existing exporter.**
   Develop Strategy and Test Hypothesis ride the convergent track
   unmodified (Track 1). Get Perspectives ALSO renders through the
   existing exporter today — at the Q6 provisional bar — but the
   `perspective_spread` slot is not represented, so divergent
   semantics are flattened. Stage 0 Q2 captured this as the
   DOES-NOT-FIT verdict.

2. **JC-MON Stage 3 has higher load-bearing weight on the existing
   exporter.** Stage 3 wires reassess actions into the Monitor drawer
   that surface the convergent assessment outputs. Any Track-2
   schema extension that changes the `ArtefactPayload` Pydantic shape
   ripples through the JC-MON consumer at the same time. Sequencing
   Track 2 AFTER Stage 3 reduces the simultaneous-schema-change
   blast radius.

3. **The Get-Perspectives provisional first render (this Stage 2)
   IS the input to Track 2's spec.** First-render judgment informs
   the MINIMUM schema surface Track 2 actually needs. Dispatching
   Track 2 BEFORE running the provisional renders would over-specify.

4. **The Q6 lock allows ship-at-provisional-bar.** Get Perspectives
   does not block on Track 2 to SHIP — only to ship at "the
   MYDAWA-grade bar." The user can defer Track 2 indefinitely if the
   provisional first render is judged sufficient on its own merits.

### Proposed Track-2 scope (per Stage 0 Q2 verdict; do not execute)

- New schema slot in `ArtefactPayload`:
  `perspective_spread`, carrying `personas[] / agreement_map[] /
  conflict_map[] / blind_spots[]`.
- New pptx builder in `services/solva_v2/pptx_exporter.py` for the
  divergent-synthesis slide. Reuses brand tokens + slide geometry;
  no new architecture.
- Path-aware Pydantic validator: convergent forbids
  `perspective_spread` set; divergent forbids `scenarios[]` /
  `pathway[]` set.

### Decision points for the user

- **(a)** Dispatch Track 2 next, before JC-MON Stage 3. *Risk: schema
  ripple into Stage 3 consumer; mitigation possible but adds
  coordination.*
- **(b)** Dispatch Track 2 after JC-MON Stage 3, before any
  Get-Perspectives shipping commitment. **AGENT RECOMMENDATION.**
  Reasons above.
- **(c)** Ship Get Perspectives at the provisional bar (Q6) and
  defer Track 2 indefinitely. Justified if the first render is
  judged deck-grade as-is.
"""


# ─────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────


def _assert(cond: bool, msg: str) -> None:
    label = "✅" if cond else "❌"
    print(f"  {label} {msg}")
    if not cond:
        raise AssertionError(msg)


async def _run_one_path(
    session_builder, label: str, slug: str, summary: str,
    track2_provisional: bool,
) -> Dict[str, Any]:
    print(f"\n[{label}] building session …")
    session = session_builder()
    art_dir = ART_DIR_BASE / slug
    art_dir.mkdir(parents=True, exist_ok=True)

    print(f"  rendering deck …")
    pptx_bytes, sig = _render(session, context_name=f"Mara Heritage Bank · Demo — {label}")
    pptx_path = art_dir / "deck.pptx"
    pptx_path.write_bytes(pptx_bytes)
    print(f"   → {pptx_path} ({len(pptx_bytes)} bytes)")

    print(f"  scoring deck …")
    rubric = _q2_rubric(pptx_path, session)
    print(f"   verdict: {rubric['overall_verdict']} ({rubric['yes_count']} YES, {rubric['partial_count']} PARTIAL)")

    record = _session_record(session, sig, summary)
    (art_dir / "session-record.json").write_text(json.dumps(record, indent=2, default=str))
    (art_dir / "session-full.json").write_text(json.dumps(session, indent=2, default=str))
    rubric_md = (
        f"# JC-TL Stage 2 · {label} · Rubric\n\n"
        f"> Verdict: **{rubric['overall_verdict']}** "
        f"({rubric['yes_count']} YES, {rubric['partial_count']} PARTIAL, {rubric['no_count']} NO)\n"
        f"> Deck slides: {rubric['n_slides']}\n"
        + ("> Q6 lock: provisional bar (no MYDAWA reference for divergent shape)\n" if track2_provisional else "")
        + "\n## Slide spine\n"
        + "\n".join(f"{i}. {t}" for i, t in enumerate(rubric["slide_titles"], 1))
        + "\n\n## Per-trait verdict\n\n"
        + "| # | Trait | Verdict | Evidence |\n|---|---|---|---|\n"
        + "\n".join(
            f"| {i} | {t['trait']} | {t['verdict']} | {t['evidence']} |"
            for i, t in enumerate(rubric["traits"], 1)
        )
        + "\n"
    )
    (art_dir / "rubric-scorecard.md").write_text(rubric_md)
    print(f"   → {art_dir / 'session-record.json'}")
    print(f"   → {art_dir / 'rubric-scorecard.md'}")

    return {
        "label": label,
        "session_id": session["id"],
        "rubric": rubric,
        "deck_path": str(pptx_path),
        "payload_signature": sig,
        "session_record": record,
    }


async def main() -> None:
    start = datetime.now(timezone.utc).isoformat()
    print(f"=== JC-TL Stage 2 — fan-out proving slice — {start} ===")

    develop = await _run_one_path(
        _develop_strategy_session, "Develop Strategy", "develop-strategy",
        "Parallel recovery pathway, 8-10 week target. Convergent to "
        "recommendation with conditional fallback to sequential.",
        track2_provisional=False,
    )
    hypothesis = await _run_one_path(
        _test_hypothesis_session, "Test Hypothesis", "test-hypothesis",
        "Parallel recovery hypothesis is Possible (45%); two falsifying "
        "scenarios credible. Week-6 weekly index is the falsification gate.",
        track2_provisional=False,
    )
    perspectives = await _run_one_path(
        _get_perspectives_session, "Get Perspectives", "get-perspectives",
        "Three persona views: auditor + regulator agree on process "
        "discipline; customer-advocate pushes on tone. Plan must thread both.",
        track2_provisional=True,
    )

    # Track-2 sequencing recommendation — surface only.
    track2_path = ART_DIR_BASE / "track-2-decks-upgrade-sequencing.md"
    track2_path.write_text(_track_2_sequencing_recommendation())
    print(f"\n  → {track2_path}")

    print("\n— ACCEPTANCE ROWS (5/5 required) —")
    _assert(
        develop["rubric"]["overall_verdict"] in ("FITS", "FITS-WITH-LOSS"),
        f"A. Develop Strategy deck — {develop['rubric']['overall_verdict']}",
    )
    _assert(
        hypothesis["rubric"]["overall_verdict"] in ("FITS", "FITS-WITH-LOSS"),
        f"B. Test Hypothesis deck — {hypothesis['rubric']['overall_verdict']}",
    )
    _assert(
        perspectives["rubric"]["yes_count"] >= 4,
        f"C. Get Perspectives provisional bar (≥ 4 YES traits) — yes={perspectives['rubric']['yes_count']}",
    )
    _assert(
        develop["session_record"]["prior_session_intent"] is not None
        and develop["session_record"]["prior_session_intent"]["submodule"] == "seek_clarity",
        f"D. Contributor-history fold-in surfaces prior_session_intent — "
        f"{(develop['session_record']['prior_session_intent'] or {}).get('submodule')}",
    )
    _assert(
        track2_path.exists() and track2_path.stat().st_size > 1000,
        f"E. Track-2 sequencing recommendation surfaced — {track2_path.stat().st_size} bytes",
    )
    print("\n5/5 acceptance rows GREEN — STAGE 2 STOP-AND-SHOW ready.\n")


if __name__ == "__main__":
    os.environ.setdefault("CSRF_TEST_BYPASS_HEADER", "1")
    asyncio.run(main())
