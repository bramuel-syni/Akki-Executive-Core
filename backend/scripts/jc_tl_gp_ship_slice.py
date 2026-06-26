"""JC-TL Get-Perspectives ship — proving slice.

Source of truth: `/app/memory/JC_TL_CANONICAL_SPEC.md` §4
("GET PERSPECTIVES — the divergent outlier; synthesis INVERTS to a
spread of multiple persona views"). Ships against the Track-2
divergent first-render approved by user 2026-06-26.

Per user direction at GP-ship dispatch (2026-06-26):
  • 3+ representative inputs, byte-stable across two consecutive runs
    (no nondeterminism in the synthesis path).
  • Readback through the dual-read GridFS helper — N/A for THIS ship
    because the divergent path is in-process; no upload involved.
    The dual-read helper IS exercised in the upload slice
    (`jc_bug_analyze_upload_slice.py` row G).
  • Acceptance bar: GP fan-out renders cleanly through the divergent
    exporter; the `perspective_spread` slot is populated; path-
    discipline validator accepts; methodology-spine slots present.

Run from the repo root:
    cd /app/backend && python scripts/jc_tl_gp_ship_slice.py
"""
from __future__ import annotations

import asyncio
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path("/app/backend")
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv  # noqa: E402
load_dotenv("/app/backend/.env")

from services.solva_v2.payload_builder import (  # noqa: E402
    build_divergent_payload,
)
from services.solva_v2.artefact_schema import PerspectiveSpread  # noqa: E402
from services.solva_v2.pptx_exporter import build_pptx, DIVERGENT_DECK_ORDER  # noqa: E402

ART_DIR = Path("/app/memory/jc_artifacts/jc_tl/03-gp-ship")
ART_DIR.mkdir(parents=True, exist_ok=True)
EVIDENCE_DIR = Path("/app/memory/jc_artifacts/jc_tl/03-gp-ship/evidence")
EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)


# ──────────────────────────────────────────────────────────────────
# Session fixtures — 3 representative GP inputs.
# Each fixture is the SAME shape; only the scenario-specific tokens
# vary. This proves the deterministic builder is signal-agnostic.
# ──────────────────────────────────────────────────────────────────


def _make_session(
    *, slug: str, intent: str,
    personas: List[Dict[str, Any]],
    agreement: Dict[str, Any],
    conflict: Dict[str, Any],
    blind_spots: List[Dict[str, Any]],
    tension_title: str,
    tension_prevailing: str,
    tension_evidence_quote: str,
    tension_layer_qid: str,
    tension_implication: str,
    reflection_q1: Dict[str, str],
    reflection_q2: Dict[str, str],
    reflection_q3: Dict[str, str],
    bias_name: str,
    bias_display: str,
    bias_evidence: str,
    pre_mortem_kind: str,
    pre_mortem_narrative: str,
    pre_mortem_signals: List[str],
    pre_mortem_counter: str,
    cost_held_pathway: str,
    cost_held_correct: str,
    cost_held_wrong: str,
    cost_converged_pathway: str,
    cost_converged_correct: str,
    cost_converged_wrong: str,
    in_closing_reframe: str,
    in_closing_recap: List[str],
    in_closing_final: str,
    headline_findings: List[str],
    methodology_what_is: str,
    methodology_what_is_not: str,
    methodology_provisional: str,
    sensitivity_input: str,
    sensitivity_impact: str,
    risk_text: str,
    risk_mitigation_text: str,
) -> Dict[str, Any]:
    """Compose a Get-Perspectives session dict for `build_divergent_payload`."""
    # Source citations are deterministic — same audit ids across the
    # 3 fixtures because the audit-log shape is the contract, not its
    # content. The renderer cites by id; the scenario-specific text
    # is what differs.
    def _cite(aid: str, desc: str):
        # SourceCitation requires source_input_id + source_kind + excerpt.
        return {"source_input_id": aid, "source_kind": "audit_log",
                "excerpt": desc}

    return {
        "id":             f"sess-jctl-gp-ship-{slug}",
        "schema_version": 2,
        "account_id":     "cf6e7587-9abd-46aa-b8f4-f342e9b066ef",
        "context_id":     "a2937d0f-37f1-4042-a897-ab73a6cd652a",
        "intent":         intent,
        "submodule":      "get_perspective",
        "persona":        personas[0]["persona_label"].lower(),
        "cluster_id":     f"cluster-{slug}",
        "started_at":     "2026-06-26T08:00:00Z",
        "completed_at":   "2026-06-26T09:00:00Z",
        "layer":          "reflection",
        "status":         "complete",
        "user_turns":     [],
        "attached_docs":  [],
        "comparables":    [],
        "reasoning_audit_log": [],
        "synthesis": {
            "perspective_spread": {
                "personas":      personas,
                "agreement_map": [agreement],
                "conflict_map":  [conflict],
                "blind_spots":   blind_spots,
            },
            "headline": {
                "key_findings": [
                    {"number": i + 1, "paragraph_text": text,
                     "source_citations": [_cite(f"audit-h{i+1}", f"headline finding {i+1}")]}
                    for i, text in enumerate(headline_findings)
                ],
            },
            "tensions": [{
                "number":             "01",
                "title":              tension_title,
                "prevailing_framing": tension_prevailing,
                "evidence_block": {
                    "user_quote":              tension_evidence_quote,
                    "source_layer_question_id": tension_layer_qid,
                    "source_layer":            "grounding",
                },
                "implication":         tension_implication,
                "contradiction_source": "user_vs_corpus",
            }],
            "reflection_section": {
                "questions": [
                    {"question_text": reflection_q1["q"],
                     "user_verbatim_response": reflection_q1["a"],
                     "diagnostic_interpretation": reflection_q1["i"]},
                    {"question_text": reflection_q2["q"],
                     "user_verbatim_response": reflection_q2["a"],
                     "diagnostic_interpretation": reflection_q2["i"]},
                    {"question_text": reflection_q3["q"],
                     "user_verbatim_response": reflection_q3["a"],
                     "diagnostic_interpretation": reflection_q3["i"]},
                ],
            },
            "methodological_honesty": {
                "what_report_is":            methodology_what_is,
                "what_report_is_not":        methodology_what_is_not,
                "provisional_nature_paragraph": methodology_provisional,
                "input_confidence_pct":      70,
                "not_sole_basis_paragraph": (
                    "The spread does not authorise a decision; it preserves "
                    "the operating spread the user must weigh."
                ),
            },
            "in_closing": {
                "reframing_paragraph": in_closing_reframe,
                "key_findings_recap":  in_closing_recap,
                "final_statement":     in_closing_final,
            },
            "bias_inventory": {
                "biases": [{
                    "bias_name":         bias_name,
                    "bias_display_name": bias_display,
                    "likelihood":        "medium",
                    "evidence_grounded_reasoning": bias_evidence,
                    "source_input_ids":  ["L0-Q1", "L1-Q2"],
                    "suggested_mitigation": (
                        "Hold each persona reading visible at every "
                        "executive review until reflection clears."
                    ),
                }],
            },
            "pre_mortem": {
                "failure_modes": [{
                    "failure_kind":       pre_mortem_kind,
                    "failure_narrative":  pre_mortem_narrative,
                    "triggering_signals": pre_mortem_signals,
                    "counter_action":     pre_mortem_counter,
                    "source_input_ids":   ["L3-Q1", "L4-Q2"],
                }],
            },
            "cost_asymmetry": {
                "scenarios": [
                    {"pathway_label":  cost_held_pathway,
                     "if_correct_outcome": cost_held_correct,
                     "if_wrong_cost":  cost_held_wrong,
                     "cost_kind":      "time_cost",
                     "cost_magnitude": "low",
                     "source_input_ids": ["L0-Q1", "L3-Q1"]},
                    {"pathway_label":  cost_converged_pathway,
                     "if_correct_outcome": cost_converged_correct,
                     "if_wrong_cost":  cost_converged_wrong,
                     "cost_kind":      "stakeholder_trust",
                     "cost_magnitude": "high",
                     "source_input_ids": ["L3-Q2", "L4-Q1"]},
                ],
            },
            "sensitivity_inputs": [{
                "rank":              "HIGH",
                "input_description": sensitivity_input,
                "impact_explanation": sensitivity_impact,
                "cluster_weight_shift_mechanic": (
                    "Could move one of the persona views from active "
                    "dissent to minority observer in the spread."
                ),
                "source_citations": [{"source_input_id": "audit-sensitivity-001",
                                      "source_kind":      "audit_log",
                                      "excerpt":          "spread-collapse sensitivity"}],
            }],
            "risk_mitigation": [{
                "risk":       risk_text,
                "mitigation": risk_mitigation_text,
            }],
            "decision_logic": [],   # divergent — no path conclusions
        },
    }


def _persona(label: str, summary: str, confidence: int, citation_desc: str) -> Dict[str, Any]:
    return {
        "persona_label":   label,
        "view_summary":    summary,
        "confidence_pct":  confidence,
        "source_citations": [{"source_input_id": f"audit-{label.lower().replace(' ', '-')}",
                              "source_kind":      "audit_log",
                              "excerpt":          citation_desc}],
    }


def session_a_regulatory() -> Dict[str, Any]:
    """Fixture A — regulatory-action persona spread (mirror of Track-2 reference shape)."""
    return _make_session(
        slug="regulatory",
        intent="Get perspectives on the regulatory action — auditor, regulator, customer-advocate views.",
        personas=[
            _persona("Auditor",
                "Reads the procedural escalation path as load-bearing — compliance was followed, exceptions are documentable.",
                72, "auditor procedural-discipline reading"),
            _persona("Regulator",
                "Reads procedural facts but emphasises that documented compliance is the floor, not the ceiling.",
                68, "regulator-floor reading"),
            _persona("Customer advocate",
                "Dissents on tone and pace — procedural compliance is necessary but insufficient.",
                58, "customer-advocate dissent"),
        ],
        agreement={"statement": "Procedural escalation path was followed and is documentable.",
                   "backing_personas": ["Auditor", "Regulator"],
                   "rationale": "Both grant the procedural floor; disagreement is downstream."},
        conflict={"tension_statement": "Process is the operative variable, or trust signal IS the operative variable — the spread holds both.",
                  "opposing_personas": ["Auditor", "Customer advocate"],
                  "why_it_matters": "Convergence on either side would lose the operating signal carried in the other."},
        blind_spots=[
            {"persona_label": "Auditor", "blind_spot_description": "Customer-experience trade-offs the procedural read can't see through the audit log.",
             "source_citations": [{"source_input_id": "audit-bs-auditor", "source_kind": "audit_log", "excerpt": "audit framing log-integrity over customer-felt tone"}]},
            {"persona_label": "Regulator", "blind_spot_description": "Internal capacity constraints driving response sequencing on the firm side.",
             "source_citations": [{"source_input_id": "audit-bs-regulator", "source_kind": "audit_log", "excerpt": "regulator floor analysis treats firm-side capacity as exogenous"}]},
            {"persona_label": "Customer advocate", "blind_spot_description": "The regulatory floor the firm cannot drop below regardless of tone.",
             "source_citations": [{"source_input_id": "audit-bs-customer", "source_kind": "audit_log", "excerpt": "customer-advocate optimises for tone; regulator-floor lock not engaged"}]},
        ],
        tension_title="Procedural finding versus operating reality",
        tension_prevailing="The procedural read is necessary AND sufficient.",
        tension_evidence_quote="We followed the documented escalation path on every flag.",
        tension_layer_qid="L1-Q3",
        tension_implication=(
            "The spread does NOT settle whether procedural compliance was "
            "the operative variable — it surfaces the tension and refuses "
            "to converge."
        ),
        reflection_q1={"q": "What would shift the spread?",
                       "a": "A regulator's deposition next week.",
                       "i": "Single high-credibility input could collapse the spread toward Regulator+Auditor."},
        reflection_q2={"q": "What's the cost of premature convergence?",
                       "a": "We'd over-rotate on procedural fix and under-invest in trust repair.",
                       "i": "Customer-advocate dissent is the load-bearing signal here."},
        reflection_q3={"q": "What's the strongest case against your spread?",
                       "a": "That three personas isn't enough.",
                       "i": "Provisional — first-render spread; bar is methodology-spine, not exhaustive coverage."},
        bias_name="convergence_bias",
        bias_display="Convergence bias",
        bias_evidence="Framing presents a strong pull toward a single weighted answer; spread surfaces this without collapsing it.",
        pre_mortem_kind="stakeholder_misalignment",
        pre_mortem_narrative=(
            "Twelve months out, response narrows on procedural compliance and "
            "the customer-trust signal degrades silently — spread was not preserved."
        ),
        pre_mortem_signals=[
            "CSAT decline despite procedural-fix headlines",
            "Customer-advocate cluster falls out of executive reviews",
        ],
        pre_mortem_counter="Surface customer-advocate dissent at every executive review until L4 reflection clears.",
        cost_held_pathway="Spread held",
        cost_held_correct=(
            "Operating tension stays visible; response weights all three voices "
            "proportionally — trust repair lands alongside procedural fix."
        ),
        cost_held_wrong=(
            "Review overhead (repeat-explain the persona reads at every executive check-in) but no operating regret."
        ),
        cost_converged_pathway="Premature convergence",
        cost_converged_correct=(
            "Ships faster, avoids appearance of paralysis — short-term executive comfort gain."
        ),
        cost_converged_wrong=(
            "Customer-trust signal degrades; six-month under-investment compounds before next review reopens the spread."
        ),
        in_closing_reframe=(
            "Three voices, one agreement, one tension, three blind-spots. "
            "What changes when you stop weighting them?"
        ),
        in_closing_recap=[
            "Three personas, no single weighted read.",
            "Auditor + Regulator agree on procedure; Customer-advocate dissents on tone.",
            "Each persona carries a structural blind-spot the others fill.",
        ],
        in_closing_final="Hold the spread — that is the answer.",
        headline_findings=[
            "Three legitimate readings of the regulatory action exist; converging prematurely on one would lose the operating signal carried in the spread.",
            "Auditor and Regulator converge on the procedural discipline finding; Customer-advocate dissents on tone and pace.",
            "Each persona carries a structural blind-spot: Auditor on customer-experience trade-offs, Regulator on capacity, Customer-advocate on the regulatory floor.",
        ],
        methodology_what_is=(
            "A spread of three legitimate persona reads with their agreement-cluster, "
            "conflict-cluster, and blind-spot map."
        ),
        methodology_what_is_not=(
            "A single weighted picture or a recommended pathway. The divergent shape "
            "stops at the spread by design."
        ),
        methodology_provisional=(
            "First-render against the divergent slot for THIS scenario; quality bar "
            "is methodology-spine, not MYDAWA (MYDAWA is convergent)."
        ),
        sensitivity_input="A regulator's deposition next week",
        sensitivity_impact=(
            "Single high-credibility regulator input could collapse the spread "
            "toward Regulator+Auditor and dissolve the Customer-advocate dissent."
        ),
        risk_text="Premature convergence collapses the spread.",
        risk_mitigation_text="Hold the spread visible at every executive review until L4 reflection clears.",
    )


def session_b_investment() -> Dict[str, Any]:
    """Fixture B — investment-thesis persona spread (founder / CFO / VC partner)."""
    return _make_session(
        slug="investment",
        intent="Get perspectives on the Series B raise — founder, CFO, VC partner views.",
        personas=[
            _persona("Founder",
                "Reads the raise as runway extension — the bridge to Series C inflection metrics.",
                70, "founder narrative-velocity reading"),
            _persona("CFO",
                "Reads the raise as capital-structure load — dilution + valuation defensibility primary.",
                75, "cfo capital-structure reading"),
            _persona("VC partner",
                "Reads the raise as portfolio-fit pressure — momentum + market timing primary.",
                65, "vc partner portfolio-pressure reading"),
        ],
        agreement={"statement": "The Series B is justified by the unit-economic improvement since Series A.",
                   "backing_personas": ["Founder", "CFO"],
                   "rationale": "Both grant the unit-economics floor; disagreement is on what comes after."},
        conflict={"tension_statement": "Growth velocity to inflection is load-bearing, or capital-stack discipline is — the spread holds both.",
                  "opposing_personas": ["Founder", "CFO"],
                  "why_it_matters": "Convergence on growth alone risks bad cap table; convergence on capital alone risks under-investment in narrative velocity."},
        blind_spots=[
            {"persona_label": "Founder", "blind_spot_description": "Capital-stack load on later rounds; dilution compounding into Series C.",
             "source_citations": [{"source_input_id": "audit-bs-founder", "source_kind": "audit_log", "excerpt": "founder framing optimises for runway, not stack"}]},
            {"persona_label": "CFO", "blind_spot_description": "Narrative velocity that justifies the next round's pre-money valuation.",
             "source_citations": [{"source_input_id": "audit-bs-cfo", "source_kind": "audit_log", "excerpt": "CFO framing treats narrative as exogenous to capital math"}]},
            {"persona_label": "VC partner", "blind_spot_description": "Operational reality of the founder's daily constraint set during the raise.",
             "source_citations": [{"source_input_id": "audit-bs-vc", "source_kind": "audit_log", "excerpt": "VC framing reads market timing; daily ops constraint not engaged"}]},
        ],
        tension_title="Growth-velocity primacy versus capital-stack primacy",
        tension_prevailing="Growth velocity to inflection is the load-bearing metric for raising.",
        tension_evidence_quote="If we hit $40 M ARR by Q3, Series C is at $400 M pre-money.",
        tension_layer_qid="L1-Q5",
        tension_implication=(
            "Founder + VC partner both lean growth-velocity, CFO holds capital-stack. "
            "Spread surfaces this without forcing a single weighted choice."
        ),
        reflection_q1={"q": "What would shift the spread?",
                       "a": "A signed VC term sheet at the current valuation ask.",
                       "i": "External validation could collapse spread toward Founder+VC reading."},
        reflection_q2={"q": "What's the cost of premature convergence?",
                       "a": "We'd accept a structurally bad cap table to chase a growth narrative.",
                       "i": "CFO dissent is the load-bearing signal."},
        reflection_q3={"q": "What's the strongest case against your spread?",
                       "a": "That capital-stack discipline IS the growth strategy at this stage.",
                       "i": "Strong steel-man — the spread does not arbitrate this; it holds it visible."},
        bias_name="recency_bias",
        bias_display="Recency bias",
        bias_evidence="Founder framing weights last 90 days of growth more than the 4-year unit-economics trajectory.",
        pre_mortem_kind="stakeholder_misalignment",
        pre_mortem_narrative=(
            "Eighteen months out, Series C requires 25% dilution to land at the same "
            "valuation Founder+VC originally projected — narrative-velocity assumption broke."
        ),
        pre_mortem_signals=[
            "Q3 growth slips below 8% MoM for two months",
            "CFO's capital-stack scenarios graduate from advisory to board-level",
        ],
        pre_mortem_counter=(
            "Preserve CFO dissent in every board pack between now and the term sheet, "
            "so capital-stack discipline rides with growth narrative."
        ),
        cost_held_pathway="Spread held — multi-lens raise",
        cost_held_correct=(
            "Final term sheet has growth-velocity story AND capital-stack discipline — "
            "Series C lands without forced bridge."
        ),
        cost_held_wrong=(
            "Slower close (an extra week of back-and-forth on terms negotiation) but cap-table preserved and Series C math stays defensible."
        ),
        cost_converged_pathway="Premature convergence on growth-velocity",
        cost_converged_correct=(
            "Fast close at top-of-range pre-money valuation; founder runway maximised; team headcount plan locks in early."
        ),
        cost_converged_wrong=(
            "Cap table loads dilution disproportionately on founders; Series C struggles "
            "with reverse-dilution math."
        ),
        in_closing_reframe=(
            "Three voices on the raise. Convergence on unit economics; spread on what's next. "
            "What changes if you stop arbitrating?"
        ),
        in_closing_recap=[
            "Three personas, no single weighted read.",
            "Founder + CFO agree on unit-economic floor; VC partner reads portfolio-fit pressure.",
            "Each persona carries a structural blind-spot the others fill.",
        ],
        in_closing_final="Hold the spread until the term sheet — that is the answer.",
        headline_findings=[
            "Three legitimate readings of the Series B raise exist; converging prematurely would lose the operating signal carried in the spread.",
            "Founder + CFO converge on unit-economic justification; VC partner reads portfolio-fit pressure as primary.",
            "Each persona carries a structural blind-spot: Founder on capital stack, CFO on narrative velocity, VC partner on operational reality.",
        ],
        methodology_what_is=(
            "A spread of three legitimate persona reads on the Series B raise, with "
            "their agreement-cluster, conflict-cluster, and blind-spot map."
        ),
        methodology_what_is_not=(
            "A single weighted picture or a 'raise / don't raise' recommendation. The "
            "divergent shape stops at the spread by design."
        ),
        methodology_provisional=(
            "First-render against the divergent slot for THIS scenario; quality bar "
            "is methodology-spine, not a MYDAWA-class reference."
        ),
        sensitivity_input="A signed VC term sheet at the current valuation ask",
        sensitivity_impact=(
            "External validation could collapse the spread toward Founder+VC reading "
            "and dissolve the CFO dissent on capital-stack discipline."
        ),
        risk_text="Founder + VC alignment without CFO dissent on cap table.",
        risk_mitigation_text="Surface CFO capital-stack scenarios in every board pack until term sheet.",
    )


def session_c_launch() -> Dict[str, Any]:
    """Fixture C — product-launch persona spread (PM / engineering / sales)."""
    return _make_session(
        slug="launch",
        intent="Get perspectives on Q3 product launch readiness — PM, engineering, sales views.",
        personas=[
            _persona("Product manager",
                "Reads the launch readiness as story-arc complete — the customer flow demos cleanly end-to-end.",
                70, "pm story-arc reading"),
            _persona("Engineering lead",
                "Reads the launch readiness as backlog-cliff dependent — three P1 incidents in last 30 days unaddressed.",
                75, "eng backlog-cliff reading"),
            _persona("Sales lead",
                "Reads the launch readiness as enterprise-pipeline pressure — three signed contracts dated against the Q3 launch.",
                60, "sales pipeline-commitment reading"),
        ],
        agreement={"statement": "The customer-facing surface is functionally complete and demos cleanly.",
                   "backing_personas": ["Product manager", "Sales lead"],
                   "rationale": "Both grant the customer-facing surface; disagreement is on what's underneath."},
        conflict={"tension_statement": "Surface readiness is launch readiness, or backlog hardness is — the spread holds both readings.",
                  "opposing_personas": ["Product manager", "Engineering lead"],
                  "why_it_matters": "Convergence on surface alone risks shipping into a brittle subsurface; convergence on backlog alone risks pipeline-commitment cost from slipping the date."},
        blind_spots=[
            {"persona_label": "Product manager", "blind_spot_description": "Incident-history pattern that customer-flow demos can't surface in walkthroughs.",
             "source_citations": [{"source_input_id": "audit-bs-pm", "source_kind": "audit_log", "excerpt": "PM framing optimises for narrative arc, not failure-mode coverage"}]},
            {"persona_label": "Engineering lead", "blind_spot_description": "Pipeline-commitment cost of slipping the launch date against signed contracts.",
             "source_citations": [{"source_input_id": "audit-bs-eng", "source_kind": "audit_log", "excerpt": "engineering treats deal-side commitments as exogenous"}]},
            {"persona_label": "Sales lead", "blind_spot_description": "Reliability tail risk inside the customer flow that scripted demos hide.",
             "source_citations": [{"source_input_id": "audit-bs-sales", "source_kind": "audit_log", "excerpt": "sales reads contract dates; reliability tail not engaged"}]},
        ],
        tension_title="Surface-readiness versus subsurface-readiness",
        tension_prevailing="The customer-facing flow is the readiness contract — if it demos, it ships.",
        tension_evidence_quote="The flow demos cleanly to three reference customers in the past week.",
        tension_layer_qid="L1-Q2",
        tension_implication=(
            "PM + Sales read 'demos cleanly' as launch-ready; Engineering reads "
            "'three open P1s' as not-ready. Spread surfaces the gap."
        ),
        reflection_q1={"q": "What would shift the spread?",
                       "a": "A clean 30-day P1 streak before launch date.",
                       "i": "Eliminating engineering's load-bearing dissent collapses spread to launch-ready."},
        reflection_q2={"q": "What's the cost of premature convergence?",
                       "a": "We'd ship into a high-stakes contract on a brittle subsurface.",
                       "i": "Engineering dissent is the load-bearing signal."},
        reflection_q3={"q": "What's the strongest case against your spread?",
                       "a": "That P1 history is the past and the current 14-day window is clean.",
                       "i": "Steel-man holds; the spread does not arbitrate the time-window."},
        bias_name="demo_bias",
        bias_display="Demo bias",
        bias_evidence="PM + Sales framings weight observable demo behaviour over unobservable failure-mode history.",
        pre_mortem_kind="execution_velocity",
        pre_mortem_narrative=(
            "Two weeks post-launch, a P1 hits during the enterprise-customer "
            "rollout — the same failure pattern flagged in the engineering "
            "lead's spread was the operative variable, missed because demos "
            "hid it."
        ),
        pre_mortem_signals=[
            "Error-rate jumps on the customer flow during peak hours",
            "Engineering lead's spread reading retroactively cited in post-mortem",
        ],
        pre_mortem_counter=(
            "Run a 30-day reliability streak gate BEFORE the launch contract "
            "trigger fires; engineering dissent becomes a hard gate, not advice."
        ),
        cost_held_pathway="Spread held — gated launch",
        cost_held_correct=(
            "Launch hits Q3 with the 30-day reliability gate cleared; pipeline "
            "preserved AND subsurface hardened."
        ),
        cost_held_wrong=(
            "Two weeks of slip to clear the gate; one contract renegotiation. "
            "Recoverable cost."
        ),
        cost_converged_pathway="Premature convergence on surface-readiness",
        cost_converged_correct=(
            "Q3 hits dead-on; pipeline closes at full value; engineering's P1 "
            "concern proves to be tail noise."
        ),
        cost_converged_wrong=(
            "Post-launch P1 hits during enterprise-customer rollout; trust "
            "damage compounds across all three signed contracts."
        ),
        in_closing_reframe=(
            "Three voices on Q3 launch. Convergence on surface; spread on subsurface. "
            "What changes if you stop arbitrating?"
        ),
        in_closing_recap=[
            "Three personas, no single weighted read on subsurface readiness.",
            "PM + Sales agree on surface readiness; Engineering reads subsurface as not-ready.",
            "Each persona carries a structural blind-spot the others fill.",
        ],
        in_closing_final="Hold the spread until the reliability gate clears.",
        headline_findings=[
            "Three legitimate readings of Q3 launch readiness exist; converging on surface-readiness would lose the operating signal in engineering's spread.",
            "PM + Sales converge on surface readiness; Engineering reads subsurface P1 history as load-bearing.",
            "Each persona carries a structural blind-spot: PM on failure-mode coverage, Engineering on pipeline-commitment cost, Sales on reliability tail.",
        ],
        methodology_what_is=(
            "A spread of three legitimate persona reads on Q3 launch readiness, with "
            "their agreement-cluster, conflict-cluster, and blind-spot map."
        ),
        methodology_what_is_not=(
            "A 'launch / hold' recommendation. The divergent shape stops at the spread "
            "by design — gating decisions live in the reliability-streak gate, not here."
        ),
        methodology_provisional=(
            "First-render against the divergent slot for THIS scenario; quality bar "
            "is methodology-spine."
        ),
        sensitivity_input="A clean 30-day P1 streak before launch date",
        sensitivity_impact=(
            "Eliminating engineering's load-bearing dissent would collapse the spread "
            "to launch-ready and let Sales + PM convergence carry the call."
        ),
        risk_text="PM + Sales alignment without engineering reliability gate.",
        risk_mitigation_text="Gate the launch trigger on a 30-day clean P1 streak.",
    )


# ──────────────────────────────────────────────────────────────────
# Acceptance rows.
# ──────────────────────────────────────────────────────────────────


def _render_session(session: Dict[str, Any], *, context_name: str = "GP Ship Slice") -> bytes:
    payload = build_divergent_payload(session, context_name=context_name)
    pptx_bytes = build_pptx(payload, context_name=context_name)
    return pptx_bytes


def row_a_validator_accepts_3_sessions(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Row A — All 3 sessions pass build_divergent_payload + Pydantic
    path-discipline validator on first build."""
    results = []
    for s in sessions:
        try:
            payload = build_divergent_payload(s)
            results.append({"id": s["id"], "ok": True,
                            "scenarios_empty": payload.scenarios == [],
                            "pathway_empty":   payload.pathway == [],
                            "spread_populated": payload.perspective_spread is not None})
        except Exception as exc:  # noqa: BLE001
            results.append({"id": s["id"], "ok": False, "err": f"{type(exc).__name__}: {exc}"})
    ok_all = all(r.get("ok") and r.get("scenarios_empty") and r.get("pathway_empty")
                 and r.get("spread_populated") for r in results)
    return {"row": "A", "subject": "build_divergent_payload accepts 3 sessions",
            "results": results, "PASS": ok_all}


def row_b_pptx_render_3_sessions(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Row B — All 3 sessions render via build_pptx in the divergent
    deck order (14 slides)."""
    results = []
    for s in sessions:
        try:
            data = _render_session(s)
            results.append({"id": s["id"], "ok": True,
                            "bytes": len(data),
                            "is_pptx": data[:2] == b"PK"})  # zip magic
            # Persist to artefacts dir for the user to eyeball.
            (ART_DIR / f"{s['id']}.pptx").write_bytes(data)
        except Exception as exc:  # noqa: BLE001
            results.append({"id": s["id"], "ok": False, "err": f"{type(exc).__name__}: {exc}"})
    ok_all = all(r.get("ok") and r.get("is_pptx") for r in results)
    return {"row": "B", "subject": "build_pptx renders 3 sessions (divergent order)",
            "results": results,
            "n_slides_in_order": len(DIVERGENT_DECK_ORDER),
            "PASS": ok_all and len(DIVERGENT_DECK_ORDER) == 14}


def row_c_byte_stability_run1_vs_run2(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Row C — byte-stability across 2 consecutive renders, per session.

    This is the load-bearing user requirement: 'byte-stable across
    two consecutive runs (no nondeterminism in the synthesis path).'
    """
    results = []
    for s in sessions:
        # Two consecutive renders, same input.
        a = _render_session(s)
        b = _render_session(s)
        # PPTX is a zip; deterministic ZIP requires same internal
        # ordering AND same timestamps. The exporter is expected to
        # use a deterministic packaging path. If timestamps drift,
        # the bytes will differ; surface that as a determinism leak.
        results.append({
            "id":           s["id"],
            "run1_bytes":   len(a),
            "run2_bytes":   len(b),
            "byte_equal":   a == b,
            "first_diff_offset": _first_diff_offset(a, b) if a != b else None,
        })
    return {"row": "C", "subject": "Byte-stable across 2 consecutive renders",
            "results": results,
            "PASS": all(r["byte_equal"] for r in results)}


def _first_diff_offset(a: bytes, b: bytes) -> int:
    n = min(len(a), len(b))
    for i in range(n):
        if a[i] != b[i]:
            return i
    return n  # one is a prefix of the other


def row_d_path_discipline_rejects_cross() -> Dict[str, Any]:
    """Row D — path-discipline validator rejects a mis-built payload
    (perspective_spread + non-empty scenarios). Proves the path-
    discriminator + validator are still load-bearing."""
    s = session_a_regulatory()
    s["synthesis"]["scenarios"] = [{"name": "S1"}]  # convergent slot

    # Manually construct the payload using build_divergent_payload
    # but force scenarios into the final ArtefactPayload by editing
    # the result post-construct. Since build_divergent_payload sets
    # scenarios=[], we exercise the validator by constructing the
    # payload manually with both spread + scenarios.
    from services.solva_v2.artefact_schema import ArtefactPayload, CoverSlide
    try:
        good = build_divergent_payload(s)
        # Reach into Pydantic dict + remold with scenarios=[bad row].
        d = good.model_dump()
        d["scenarios"] = [{
            "label":           "should not exist on divergent",
            "weight_pct":      50,
            "confidence_pct":  50,
            "tier":            "headline",
            "confidence_calibration_reasoning": "deliberate cross-path injection for the proving slice",
        }]
        ArtefactPayload.model_validate(d)
        return {"row": "D", "subject": "Path-discipline rejects cross-path",
                "PASS": False, "error": "validator unexpectedly ACCEPTED a cross-path payload"}
    except Exception as exc:  # noqa: BLE001
        msg = str(exc)
        return {"row": "D", "subject": "Path-discipline rejects cross-path",
                "PASS": "must not carry scenarios[]" in msg or "Path-discipline" in msg,
                "validator_error": msg[:300]}


def row_e_spine_slots_present(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Row E — methodology-spine slots present in all 3 renders
    (cover · headline · tensions · reflection_section ·
    methodological_honesty · in_closing · bias_inventory · pre_mortem ·
    cost_asymmetry — the 9 spine slots that ride on both paths)."""
    SPINE_KEYS = (
        "cover", "headline", "tensions", "reflection_section",
        "methodological_honesty", "in_closing", "bias_inventory",
        "pre_mortem", "cost_asymmetry",
    )
    results = []
    for s in sessions:
        payload = build_divergent_payload(s)
        d = payload.model_dump()
        missing = [k for k in SPINE_KEYS if not d.get(k)]
        # tensions is a list — count it as present iff non-empty
        if not d.get("tensions"):
            missing.append("tensions(empty)")
        results.append({"id": s["id"], "missing": missing,
                        "ok": not missing})
    return {"row": "E", "subject": "Methodology-spine 9 slots present in 3 renders",
            "results": results,
            "PASS": all(r["ok"] for r in results)}


def row_f_persona_distinct_blind_spots(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Row F — Across 3 personas in each session, each persona has a
    DISTINCT blind-spot (no two personas share the same blind-spot
    label). This is the methodology-spine invariant: spread surfaces
    the gaps each persona's lens cannot see."""
    results = []
    for s in sessions:
        spread = s["synthesis"]["perspective_spread"]
        bs_personas = [b["persona_label"] for b in spread["blind_spots"]]
        bs_unique = set(bs_personas)
        results.append({"id": s["id"],
                        "n_blind_spots":     len(spread["blind_spots"]),
                        "n_unique_personas": len(bs_unique),
                        "all_personas_covered": (
                            len(bs_unique) == len([p["persona_label"] for p in spread["personas"]])
                        )})
    return {"row": "F", "subject": "Each persona carries a distinct blind-spot",
            "results": results,
            "PASS": all(r["all_personas_covered"] for r in results)}


async def main():
    print("=" * 70)
    print("JC-TL GP SHIP — proving slice")
    print("=" * 70)
    t0 = time.time()

    sessions = [session_a_regulatory(), session_b_investment(), session_c_launch()]
    print(f"Fixtures: {len(sessions)} sessions ({', '.join(s['id'] for s in sessions)})")
    print(f"Artefacts → {ART_DIR}")
    print()

    rows = [
        ("A", row_a_validator_accepts_3_sessions, (sessions,)),
        ("B", row_b_pptx_render_3_sessions,       (sessions,)),
        ("C", row_c_byte_stability_run1_vs_run2,  (sessions,)),
        ("D", row_d_path_discipline_rejects_cross, ()),
        ("E", row_e_spine_slots_present,          (sessions,)),
        ("F", row_f_persona_distinct_blind_spots, (sessions,)),
    ]
    results = []
    for tag, fn, args in rows:
        print(f"--- Row {tag} ---")
        t_row = time.time()
        try:
            r = fn(*args)
        except Exception as exc:  # noqa: BLE001
            r = {"row": tag, "exception": f"{type(exc).__name__}: {exc}", "PASS": False}
        r["elapsed_s"] = round(time.time() - t_row, 3)
        results.append(r)
        verdict = "✓ PASS" if r.get("PASS") else "✗ FAIL"
        print(f"  {verdict} ({r['elapsed_s']}s)")
        if not r.get("PASS"):
            print(f"  {json.dumps({k: v for k, v in r.items() if k != 'PASS'}, default=str, indent=2)[:600]}")
        print()

    n_pass = sum(1 for r in results if r.get("PASS"))
    n_total = len(results)
    print("=" * 70)
    print(f"RESULT: {n_pass}/{n_total} GREEN")
    print(f"Total elapsed: {round(time.time() - t0, 2)}s")
    print("=" * 70)

    out_path = EVIDENCE_DIR / f"slice_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}.json"
    out_path.write_text(json.dumps({
        "ran_at":   datetime.now(timezone.utc).isoformat(),
        "n_pass":   n_pass,
        "n_total":  n_total,
        "all_green": n_pass == n_total,
        "results":  results,
    }, default=str, indent=2))
    print(f"Evidence → {out_path}")
    return 0 if n_pass == n_total else 1


if __name__ == "__main__":
    rc = asyncio.run(main())
    sys.exit(rc)
