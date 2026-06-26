"""JC-TL Track-2 — Decks upgrade (divergent rendering) proving slice.

Source of truth: `/app/memory/JC_TL_CANONICAL_SPEC.md` (Track-2 brief
folded in from JC-MON Stage 3 Gate A verdict).

User dispatch (2026-06-26):
> Track-2 at MINIMUM SCOPE — schema slot + 1 builder + path-aware
> validator. NOT a Decks rebuild. Convergent render MUST remain
> 7/8 YES or better (no regression).

Acceptance rows (8/8 required):
  A. Schema acceptance — a divergent payload (perspective_spread
     populated, scenarios=[]/pathway=[]) validates cleanly.
  B. Schema rejection (convergent + perspective_spread) — a payload
     carrying perspective_spread + non-empty scenarios[] is REJECTED
     by the path-aware validator with a path-discipline error.
  C. Schema rejection (divergent + pathway) — a payload carrying
     perspective_spread + non-empty pathway[] is REJECTED.
  D. Schema acceptance (convergent unchanged) — a payload with
     perspective_spread=None + scenarios + pathway populated
     validates cleanly (BYTE-IDENTICAL convergent behaviour).
  E. Divergent deck renders — `build_pptx` on the divergent payload
     emits a real .pptx (ZIP magic 504b0304) with exactly 14 slides.
  F. Convergent regression check — `build_pptx` on a convergent
     payload still renders exactly 16 slides (LOCKED_DECK_ORDER).
  G. Methodology-spine slots present in divergent deck — the
     divergent walk includes tensions_overview + reflection +
     bias_inventory + methodological_honesty + sensitivity slots
     (the path-agnostic spine).
  H. Perspective-spread slide renders the 4 sub-arrays — the new
     slide carries the 4 SPREAD elements (personas + agreement_map
     + conflict_map + blind_spots) — checked by inspecting slide
     text content.

Artefacts → `/app/memory/jc_artifacts/jc_tl/track2/`.

Run from the repo root:
    cd /app/backend && python scripts/jc_tl_track2_min_scope_slice.py
"""
from __future__ import annotations

import io
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


from pydantic import ValidationError  # noqa: E402
from pptx import Presentation  # type: ignore  # noqa: E402

from services.solva_v2.artefact_schema import (  # noqa: E402
    AdversarialCounterCase,
    AgreementCluster,
    ArtefactPayload,
    BiasInventorySection,
    BiasItem,
    BlindSpot,
    ConflictCluster,
    CostAsymmetryScenario,
    CostAsymmetrySlide,
    CoverSlide,
    DecisionBranch,
    EvidenceBlock,
    HeadlineSlide,
    InClosing,
    KeyFinding,
    MethodologicalHonesty,
    PathwayItem,
    PerScenarioConfidenceTable,
    PersonaView,
    PerspectiveSpread,
    PreMortemFailureMode,
    PreMortemSlide,
    ReflectionQuestion,
    ReflectionSection,
    RiskMitigation,
    ScenarioRow,
    SensitivityInput,
    SourceCitation,
    TensionSlide,
)
from services.solva_v2.pptx_exporter import (  # noqa: E402
    DIVERGENT_DECK_ORDER,
    LOCKED_DECK_ORDER,
    build_pptx,
)


ART_DIR = Path("/app/memory/jc_artifacts/jc_tl/track2")
ART_DIR.mkdir(parents=True, exist_ok=True)


def _cite(sid: str = "audit-001", excerpt: str = "evidence-grounded snippet") -> SourceCitation:
    return SourceCitation(
        source_input_id=sid,
        source_kind="audit_log",
        excerpt=excerpt,
        source_layer="grounding",
    )


def _spine_shared_fields() -> Dict[str, Any]:
    """Path-agnostic methodology-spine slots that ride on both
    convergent and divergent payloads. Same shapes either way."""
    return dict(
        cover=CoverSlide(
            title="Spread of perspectives on the regulatory action",
            prepared_for="Track-2 proving slice · MYDAWA-shaped problem",
            subject="Get Perspectives",
            inputs_range="Layer 0 (frame audit) to Layer 4 (reflection), 9 user inputs",
            date_str="2026-06-26",
        ),
        headline=HeadlineSlide(
            key_findings=[
                KeyFinding(
                    number=1,
                    paragraph_text=(
                        "Three legitimate readings of the regulatory action "
                        "exist; converging prematurely on one would lose the "
                        "operating signal carried in the spread."
                    ),
                    source_citations=[_cite("audit-001", "regulatory framing — three personas")],
                ),
                KeyFinding(
                    number=2,
                    paragraph_text=(
                        "Auditor and Regulator converge on the procedural "
                        "discipline finding; Customer-advocate dissents on "
                        "the tone and pace of the response."
                    ),
                    source_citations=[_cite("audit-002", "agreement cluster · procedural read")],
                ),
                KeyFinding(
                    number=3,
                    paragraph_text=(
                        "Each persona carries a structural blind-spot: "
                        "Auditor on customer-experience trade-offs, Regulator "
                        "on internal capacity constraints, Customer-advocate "
                        "on the regulatory floor."
                    ),
                    source_citations=[_cite("audit-003", "blind-spot inventory")],
                ),
            ],
        ),
        tensions=[
            TensionSlide(
                number="01",
                title="Procedural finding versus operating reality",
                prevailing_framing="The procedural read is necessary AND sufficient",
                evidence_block=EvidenceBlock(
                    user_quote="We followed the documented escalation path on every flag.",
                    source_layer_question_id="L1-Q3",
                    source_layer="grounding",
                ),
                implication=(
                    "The persona spread does NOT settle whether procedural "
                    "compliance was the operative variable — it surfaces the "
                    "tension and refuses to converge."
                ),
                contradiction_source="user_vs_corpus",
            ),
        ],
        reflection_section=ReflectionSection(
            questions=[
                ReflectionQuestion(
                    question_text="What would shift the spread?",
                    user_verbatim_response="A regulator's deposition next week.",
                    diagnostic_interpretation=(
                        "Single high-credibility input could collapse the "
                        "spread toward Regulator+Auditor; without it, the "
                        "spread holds."
                    ),
                ),
                ReflectionQuestion(
                    question_text="What's the cost of premature convergence?",
                    user_verbatim_response="We'd over-rotate on procedural fix and under-invest in trust repair.",
                    diagnostic_interpretation=(
                        "Customer-advocate dissent is the load-bearing "
                        "signal here — losing it would distort the response."
                    ),
                ),
                ReflectionQuestion(
                    question_text="What's the strongest case against your spread?",
                    user_verbatim_response="That three personas isn't enough.",
                    diagnostic_interpretation=(
                        "Provisional — first-render spread; the bar is "
                        "methodology-spine, not exhaustive persona coverage."
                    ),
                ),
            ],
        ),
        risk_mitigation=[
            RiskMitigation(
                risk="Premature convergence collapses the spread",
                mitigation="Hold the spread visible at every executive review until Layer-4 reflection clears.",
            ),
        ],
        methodological_honesty=MethodologicalHonesty(
            what_report_is=(
                "A spread of three legitimate persona reads with their "
                "agreement-cluster, conflict-cluster, and blind-spot map."
            ),
            what_report_is_not=(
                "A single weighted picture or a recommended pathway. The "
                "divergent shape stops at the spread by design."
            ),
            provisional_nature_paragraph=(
                "First-render against the new divergent slot; quality bar "
                "is methodology-spine, not MYDAWA (MYDAWA is convergent)."
            ),
            input_confidence_pct=70,
            not_sole_basis_paragraph=(
                "The spread does not authorise a decision; it preserves "
                "the operating spread the user must weigh."
            ),
        ),
        in_closing=InClosing(
            reframing_paragraph=(
                "Three voices, one agreement, one tension, three blind-spots. "
                "What changes when you stop weighting them?"
            ),
            key_findings_recap=[
                "Three personas, no single weighted read.",
                "Auditor + Regulator agree on procedure; Customer-advocate dissents on tone.",
                "Each persona carries a structural blind-spot the others fill.",
            ],
            final_statement="Hold the spread — that is the answer.",
        ),
        bias_inventory=BiasInventorySection(
            biases=[
                BiasItem(
                    bias_name="convergence_bias",
                    bias_display_name="Convergence bias",
                    likelihood="medium",
                    evidence_grounded_reasoning=(
                        "The framing presents a strong pull toward a single weighted "
                        "answer; the persona spread surfaces this without collapsing it."
                    ),
                    source_input_ids=["L0-Q1", "L1-Q2"],
                    suggested_mitigation=(
                        "Inviting the user to read each persona aloud separately "
                        "before any synthesis surface."
                    ),
                ),
            ],
        ),
        pre_mortem=PreMortemSlide(
            failure_modes=[
                PreMortemFailureMode(
                    failure_kind="stakeholder_misalignment",
                    failure_narrative=(
                        "Twelve months from now the response narrows too far on "
                        "procedural compliance and the customer-trust signal "
                        "degrades silently — the spread was not preserved."
                    ),
                    triggering_signals=[
                        "CSAT decline despite procedural-fix headlines",
                        "Customer-advocate cluster falls out of executive reviews",
                    ],
                    counter_action=(
                        "Surfacing customer-advocate dissent at every executive "
                        "review until the L4 reflection clears."
                    ),
                    source_input_ids=["L3-Q1", "L4-Q2"],
                ),
            ],
        ),
        cost_asymmetry=CostAsymmetrySlide(
            scenarios=[
                CostAsymmetryScenario(
                    pathway_label="Spread held",
                    if_correct_outcome=(
                        "If the spread holds, the operating tension stays visible and "
                        "the response weights all three voices proportionally — "
                        "trust repair lands alongside procedural fix."
                    ),
                    if_wrong_cost=(
                        "If the spread is a red herring, the cost is review overhead "
                        "(repeat-explain the persona reads) but no operating regret."
                    ),
                    cost_kind="time_cost",
                    cost_magnitude="low",
                    source_input_ids=["L0-Q1", "L3-Q1"],
                ),
                CostAsymmetryScenario(
                    pathway_label="Premature convergence",
                    if_correct_outcome=(
                        "If premature convergence is justified, the response ships "
                        "faster and avoids the appearance of paralysis — short-term "
                        "executive comfort gain."
                    ),
                    if_wrong_cost=(
                        "If convergence was wrong, the customer-trust signal degrades "
                        "and a six-month under-investment compounds before the next "
                        "review can re-open the spread."
                    ),
                    cost_kind="stakeholder_trust",
                    cost_magnitude="high",
                    source_input_ids=["L3-Q2", "L4-Q1"],
                ),
            ],
        ),
        sensitivity_inputs=[
            SensitivityInput(
                rank="HIGH",
                input_description="A regulator's deposition next week",
                impact_explanation=(
                    "A single high-credibility regulator input could collapse the "
                    "spread toward Regulator+Auditor and dissolve the Customer-advocate "
                    "dissent — the spread is sensitive to this one signal."
                ),
                cluster_weight_shift_mechanic=(
                    "Could move the Customer-advocate persona from active dissent to "
                    "minority observer in the spread."
                ),
                source_citations=[_cite("audit-004", "regulator-deposition sensitivity")],
            ),
        ],
        decision_logic=[
            DecisionBranch(
                condition=(
                    "If the regulator's deposition next week confirms the procedural "
                    "framing"
                ),
                conclusion=(
                    "the spread narrows but does not collapse — Customer-advocate "
                    "dissent stays visible as a minority read."
                ),
                rationale=(
                    "The deposition would resolve the Auditor↔Regulator agreement "
                    "cluster but not the Customer-advocate tone-and-pace tension."
                ),
                adversarial_counter=AdversarialCounterCase(
                    targets_conclusion_id="decision-0",
                    steel_man_position=(
                        "The strongest case against narrowing the spread is that the "
                        "regulator's deposition itself reflects a procedural lens, "
                        "which would re-introduce convergence bias on a single high-"
                        "credibility input — losing the operating spread the divergent "
                        "synthesis was built to preserve."
                    ),
                    source_input_ids=["L3-Q1", "L4-Q1"],
                    why_it_matters=(
                        "If the spread collapses on procedural authority alone, the "
                        "Customer-advocate dissent becomes invisible in executive review."
                    ),
                ),
            ),
        ],
    )


def _divergent_payload() -> ArtefactPayload:
    """A divergent (Get-Perspectives) payload: perspective_spread
    populated; scenarios + pathway empty (path-discipline)."""
    shared = _spine_shared_fields()
    return ArtefactPayload(
        session_id="sess-track2-min-scope-divergent",
        **shared,
        scenarios=[],
        pathway=[],
        perspective_spread=PerspectiveSpread(
            personas=[
                PersonaView(
                    persona_label="Auditor",
                    view_summary=(
                        "Reads the procedural escalation path as load-bearing — "
                        "compliance was followed, exceptions are documentable, "
                        "and the audit trail closes the operating question."
                    ),
                    confidence_pct=72,
                    source_citations=[_cite("audit-005", "procedural-discipline reading")],
                ),
                PersonaView(
                    persona_label="Regulator",
                    view_summary=(
                        "Reads the same procedural facts but emphasises that "
                        "documented compliance is the floor, not the ceiling — "
                        "asks whether the discipline transferred to operating "
                        "behaviour during the live event."
                    ),
                    confidence_pct=68,
                    source_citations=[_cite("audit-006", "regulator-floor reading")],
                ),
                PersonaView(
                    persona_label="Customer advocate",
                    view_summary=(
                        "Dissents on tone and pace — procedural compliance is "
                        "necessary but insufficient, the customer-trust signal "
                        "was secondary in the response sequencing and that is "
                        "the operating tension worth preserving."
                    ),
                    confidence_pct=58,
                    source_citations=[_cite("audit-007", "customer-advocate dissent")],
                ),
            ],
            agreement_map=[
                AgreementCluster(
                    statement=(
                        "Procedural escalation path was followed and is "
                        "documentable from the audit log."
                    ),
                    backing_personas=["Auditor", "Regulator"],
                    rationale=(
                        "Both grant the procedural floor; the disagreement is "
                        "downstream (whether procedure is the operative variable)."
                    ),
                ),
            ],
            conflict_map=[
                ConflictCluster(
                    tension_statement=(
                        "Procedural compliance settles the operating question "
                        "(Auditor) versus procedural compliance is necessary "
                        "but insufficient (Regulator + Customer advocate)."
                    ),
                    opposing_personas=["Auditor", "Customer advocate"],
                    why_it_matters=(
                        "If the spread collapses on Auditor's reading, the "
                        "tone-and-pace dimension exits the operating frame."
                    ),
                ),
                ConflictCluster(
                    tension_statement=(
                        "Tone and pace of the response are first-order operating "
                        "variables (Customer advocate) versus second-order (Auditor + Regulator)."
                    ),
                    opposing_personas=["Customer advocate", "Auditor"],
                    why_it_matters=(
                        "The trust-repair operating thread runs through this "
                        "tension; losing it would cost the response its second axis."
                    ),
                ),
            ],
            blind_spots=[
                BlindSpot(
                    persona_label="Auditor",
                    blind_spot_description=(
                        "Customer-experience trade-offs that don't land in the "
                        "audit log are invisible to the Auditor's read by "
                        "construction — the persona reads the trail, not the experience."
                    ),
                    source_citations=[_cite("audit-008", "auditor blind-spot · trail-vs-experience")],
                ),
                BlindSpot(
                    persona_label="Regulator",
                    blind_spot_description=(
                        "Internal capacity constraints during the live event "
                        "are not in the Regulator's frame — the persona reads "
                        "the floor, not the operating headroom."
                    ),
                    source_citations=[_cite("audit-009", "regulator blind-spot · capacity headroom")],
                ),
                BlindSpot(
                    persona_label="Customer advocate",
                    blind_spot_description=(
                        "The regulatory floor exists for reasons that bind even "
                        "when the tone-and-pace optimum would deviate — the "
                        "persona reads the customer, not the regulatory frame."
                    ),
                    source_citations=[_cite("audit-010", "customer-advocate blind-spot · floor")],
                ),
            ],
        ),
    )


def _convergent_payload() -> ArtefactPayload:
    """A convergent (Diagnosis-shaped) payload: perspective_spread=None;
    scenarios + pathway populated. Should validate cleanly — proves the
    path discipline does NOT regress convergent."""
    shared = _spine_shared_fields()
    return ArtefactPayload(
        session_id="sess-track2-min-scope-convergent",
        **shared,
        scenarios=[
            ScenarioRow(
                label="Spread held",
                description="The response keeps all three persona reads visible.",
                weight_pct=55,
                confidence_pct=72,
                supporting_evidence=[_cite("audit-011", "spread-held scenario")],
                confidence_calibration_reasoning=(
                    "Two triangulating sources (audit-005 Auditor + audit-007 "
                    "Customer-advocate) support the >= 70 confidence."
                ),
            ),
            ScenarioRow(
                label="Convergence early",
                description="The response narrows on procedural framing within 30 days.",
                weight_pct=30,
                confidence_pct=55,
                supporting_evidence=[_cite("audit-012", "convergence-early scenario")],
                confidence_calibration_reasoning=(
                    "Confidence below 70 — only one source pattern grounds this "
                    "scenario, so we calibrate conservatively."
                ),
            ),
            ScenarioRow(
                label="Dissent escalation",
                description="The Customer-advocate cluster gains weight and reshapes the response.",
                weight_pct=15,
                confidence_pct=45,
                supporting_evidence=[_cite("audit-013", "dissent-escalation scenario")],
                confidence_calibration_reasoning=(
                    "Speculative branch — single-source grounding only, so "
                    "weight and confidence both held below 50."
                ),
            ),
        ],
        pathway=[
            PathwayItem(
                number=1,
                timeline_tag="DAYS 0-30",
                action_heading="Preserve the spread in every executive review",
                detail_paragraph=(
                    "Hold the three persona reads visible in board materials for "
                    "the next 30 days without weighting them toward a single answer."
                ),
                source_citations=[_cite("audit-014", "pathway · spread-preservation")],
            ),
        ],
        perspective_spread=None,  # convergent path discriminator
    )


def _assert(cond: bool, msg: str) -> None:
    label = "✅" if cond else "❌"
    print(f"  {label} {msg}")
    if not cond:
        raise AssertionError(msg)


def _zip_magic_ok(b: bytes) -> bool:
    return len(b) >= 4 and b[:4] == b"PK\x03\x04"


def _slide_titles(b: bytes) -> List[str]:
    buf = io.BytesIO(b)
    p = Presentation(buf)
    out: List[str] = []
    for sl in p.slides:
        title = ""
        for sh in sl.shapes:
            if sh.has_text_frame and sh.text_frame.text.strip():
                title = sh.text_frame.text.strip().split("\n")[0][:120]
                break
        out.append(title)
    return out


def _slide_full_text(b: bytes, slide_index: int) -> str:
    buf = io.BytesIO(b)
    p = Presentation(buf)
    sl = p.slides[slide_index]
    parts: List[str] = []
    for sh in sl.shapes:
        if sh.has_text_frame:
            parts.append(sh.text_frame.text)
    return "\n".join(parts)


def main() -> None:
    start = datetime.now(timezone.utc).isoformat()
    print(f"=== JC-TL Track-2 — minimum-scope proving slice — {start} ===\n")

    # Build the two payloads.
    print("[1/4] Building divergent payload (Get-Perspectives shape) …")
    divergent = _divergent_payload()
    print("[2/4] Building convergent payload (Diagnosis-shape regression check) …")
    convergent = _convergent_payload()

    # Schema rejection probes.
    print("[3/4] Schema-rejection probes …")
    rejected_with_scenarios: bool = False
    try:
        # Divergent payload trying to carry scenarios — should be rejected.
        ArtefactPayload(
            **{
                **divergent.model_dump(),
                "scenarios": [
                    ScenarioRow(
                        label="should fail", description="convergent slot on divergent path",
                        weight_pct=50, confidence_pct=60,
                        confidence_calibration_reasoning="dummy",
                    ).model_dump(),
                ],
            }
        )
    except ValidationError as e:
        rejected_with_scenarios = "Path-discipline" in str(e)

    rejected_with_pathway: bool = False
    try:
        ArtefactPayload(
            **{
                **divergent.model_dump(),
                "pathway": [
                    PathwayItem(
                        number=1, timeline_tag="DAYS 0-30",
                        action_heading="should fail",
                        detail_paragraph="convergent slot on divergent path",
                    ).model_dump(),
                ],
            }
        )
    except ValidationError as e:
        rejected_with_pathway = "Path-discipline" in str(e)

    # Render both decks.
    print("[4/4] Rendering both decks …")
    convergent_bytes = build_pptx(convergent, context_name="Track-2 · convergent regression")
    divergent_bytes = build_pptx(divergent, context_name="Track-2 · divergent first render")

    convergent_path = ART_DIR / "convergent-regression.pptx"
    divergent_path = ART_DIR / "divergent-first-render.pptx"
    convergent_path.write_bytes(convergent_bytes)
    divergent_path.write_bytes(divergent_bytes)
    print(f"  → {convergent_path} ({len(convergent_bytes)} bytes)")
    print(f"  → {divergent_path} ({len(divergent_bytes)} bytes)")

    # Persist payload dumps for review.
    (ART_DIR / "divergent-payload.json").write_text(
        json.dumps(divergent.model_dump(), indent=2, default=str)
    )
    (ART_DIR / "convergent-payload.json").write_text(
        json.dumps(convergent.model_dump(), indent=2, default=str)
    )

    # Inventory the divergent deck.
    div_titles = _slide_titles(divergent_bytes)
    conv_titles = _slide_titles(convergent_bytes)

    # Find the perspective_spread slide and inspect its content.
    spread_idx = DIVERGENT_DECK_ORDER.index("perspective_spread")
    spread_slide_text = _slide_full_text(divergent_bytes, spread_idx)

    # Acceptance rows.
    print("\n— ACCEPTANCE ROWS (8/8 required) —")
    # Row A — divergent payload validates.
    _assert(
        divergent.perspective_spread is not None
        and not divergent.scenarios and not divergent.pathway,
        "A. divergent payload validates (perspective_spread set, scenarios/pathway empty)",
    )
    # Row B — convergent slot rejection (scenarios)
    _assert(
        rejected_with_scenarios,
        f"B. divergent + scenarios[] REJECTED with path-discipline error (got {rejected_with_scenarios})",
    )
    # Row C — pathway rejection on divergent
    _assert(
        rejected_with_pathway,
        f"C. divergent + pathway[] REJECTED with path-discipline error (got {rejected_with_pathway})",
    )
    # Row D — convergent payload validates (regression check)
    _assert(
        convergent.perspective_spread is None
        and len(convergent.scenarios) > 0 and len(convergent.pathway) > 0,
        f"D. convergent payload still validates (scenarios={len(convergent.scenarios)}, pathway={len(convergent.pathway)})",
    )
    # Row E — divergent renders correctly (14 slides, ZIP magic)
    _assert(
        _zip_magic_ok(divergent_bytes) and len(div_titles) == len(DIVERGENT_DECK_ORDER),
        f"E. divergent deck renders ({len(div_titles)} slides, ZIP magic ok, size={len(divergent_bytes)})",
    )
    # Row F — convergent regression check (16 slides)
    _assert(
        _zip_magic_ok(convergent_bytes) and len(conv_titles) == len(LOCKED_DECK_ORDER),
        f"F. convergent deck still renders {len(LOCKED_DECK_ORDER)} slides (got {len(conv_titles)}, size={len(convergent_bytes)})",
    )
    # Row G — methodology-spine present in divergent deck
    spine_slots = {"cover", "headline", "tensions_overview", "per_tension",
                   "sensitivity", "reflection", "bias_inventory",
                   "methodological_honesty", "in_closing"}
    div_present = set(DIVERGENT_DECK_ORDER)
    _assert(
        spine_slots.issubset(div_present),
        f"G. methodology-spine slots present in divergent walk ({spine_slots & div_present} = {len(spine_slots & div_present)}/{len(spine_slots)})",
    )
    # Row H — the perspective_spread slide carries all 4 SPREAD sub-arrays
    spread_anchors_present = all(
        anchor in spread_slide_text
        for anchor in (
            "PERSONAS · WHO IS SPEAKING",
            "AGREEMENT · WHERE THEY CONVERGE",
            "TENSION · WHERE THEY DIVERGE",
            "BLIND-SPOTS · WHAT EACH ISN'T SEEING",
        )
    )
    persona_label_present = "Auditor" in spread_slide_text and "Customer advocate" in spread_slide_text
    _assert(
        spread_anchors_present and persona_label_present,
        f"H. perspective_spread slide renders 4 sub-arrays (anchors={spread_anchors_present}, persona-labels={persona_label_present})",
    )

    # Inventory dump.
    inventory = {
        "produced_at":       start,
        "convergent_path":   str(convergent_path),
        "divergent_path":    str(divergent_path),
        "convergent_slides": conv_titles,
        "divergent_slides":  div_titles,
        "convergent_count":  len(conv_titles),
        "divergent_count":   len(div_titles),
        "perspective_spread_slide_text": spread_slide_text,
    }
    (ART_DIR / "inventory.json").write_text(
        json.dumps(inventory, indent=2, default=str)
    )

    print("\n8/8 acceptance rows GREEN — TRACK-2 MIN-SCOPE STOP-AND-SHOW ready.\n")


if __name__ == "__main__":
    os.environ.setdefault("CSRF_TEST_BYPASS_HEADER", "1")
    main()
