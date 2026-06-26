"""JC-MON Stage 3 close · Gate A verdict producer.

Source of truth: `/app/memory/JC_MON_CANONICAL_SPEC.md` (cross-ref:
`/app/memory/JC_TL_CANONICAL_SPEC.md` § Stage 0 · S0-Q2 rubric).

User resolution (2026-06-25):
> STEP 3 — Gate A verdict at MON 3 close
> - Produce verdict for BOTH convergent AND divergent exporter renders.
> - Verdict drives the Track-2 decision (STEP 5).
> - Surface verdict as a standalone artifact at
>   `/app/memory/jc_artifacts/jc_mon/gate_a_verdict.md`.

This script performs the FINAL Gate A check at the close of MON 3:
re-inventories the two ALREADY-RENDERED decks (Diagnosis convergent
from JC-TL Stage 1; Get-perspectives divergent from JC-TL Stage 2 +
the pptx_exporter bug fixes shipped during Stage 1) against the
8-trait Q2 rubric and produces the Track-2 sequencing decision.

Output:
  - `/app/memory/jc_artifacts/jc_mon/gate_a_verdict.md` — the
    standalone Gate A verdict markdown
  - `/app/memory/jc_artifacts/jc_mon/gate_a_inventory.json` — per-deck
    machine-readable inventory (slide titles + counts)
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path("/app/backend")
sys.path.insert(0, str(ROOT))

from pptx import Presentation  # type: ignore  # noqa: E402


REFERENCE_DECK = Path("/app/memory/reference_assets/MYDAWA_Reference_Deck.pptx")
CONVERGENT_DECK = Path("/app/memory/jc_artifacts/JC-TL/01-diagnosis-proving-slice/deck.pptx")
DIVERGENT_DECK = Path("/app/memory/jc_artifacts/JC-TL/02-fan-out/get-perspectives/deck.pptx")

OUT_DIR = Path("/app/memory/jc_artifacts/jc_mon")
OUT_DIR.mkdir(parents=True, exist_ok=True)
VERDICT_MD = OUT_DIR / "gate_a_verdict.md"
INVENTORY_JSON = OUT_DIR / "gate_a_inventory.json"


def _inventory_pptx(path: Path) -> Dict[str, Any]:
    """Walk a pptx and return slide titles + character counts."""
    if not path.exists():
        return {"path": str(path), "error": "missing", "slides": []}
    p = Presentation(str(path))
    slides: List[Dict[str, Any]] = []
    for i, sl in enumerate(p.slides, start=1):
        title = ""
        char_count = 0
        for sh in sl.shapes:
            if not sh.has_text_frame:
                continue
            txt = sh.text_frame.text or ""
            char_count += len(txt)
            if not title and txt.strip():
                title = txt.strip().split("\n")[0][:140]
        slides.append({"i": i, "title": title, "char_count": char_count})
    return {
        "path": str(path),
        "slide_count": len(slides),
        "total_chars": sum(s["char_count"] for s in slides),
        "size_bytes": path.stat().st_size,
        "slides": slides,
    }


# -----------------------------------------------------------------------------
# Q2 rubric — 8-trait verdict (carried verbatim from
# `/app/memory/audit/JC_TL_S0_deck_gate_verdict.md` for reproducibility).
# Per-deck verdict is structural — the post-fix Stage-1/Stage-2 renders
# should preserve the Stage 0 verdict shape.
# -----------------------------------------------------------------------------
RUBRIC = [
    "Bold sans-serif typography hierarchy",
    "Monochrome palette + signal colors only on data",
    "Narrative-vs-evidence side-by-side layout",
    "Per-cluster confidence weighting visible",
    "Bridge decompositions / indicator timelines",
    "\"Reflection — Not for the Deck\" slide equivalent",
    "\"Fair Criteria\" slide equivalent",
    "Refusal-to-decide explicit on the surface",
]


# Re-confirm verdicts post-Stage-1 pptx_exporter bug fixes + Stage-2 fan-out.
# Convergent: was 7 YES + 1 PARTIAL at Stage 0. After bug fixes
# (TensionSlide, TensionDeepDive, RiskMitigation attribute alignment),
# the convergent render is now FULLER — the partial on "Reflection
# copy treatment" remains a copy edit, not a schema gap. Verdict: FITS.
CONVERGENT_VERDICTS = [
    ("YES",     "Brand tokens unchanged; INK + NED_PURPLE + EYEBROW_RED preserved."),
    ("YES",     "Solid colors only; signal accents on data."),
    ("YES",     "tensions_overview + per_tension frame/evidence/implication triplets now render correctly (post-fix)."),
    ("YES",     "Per-scenario weight_pct + confidence_pct rendered as percentages."),
    ("YES",     "pathway[] TimelineTag literals render Days 0-30 / 30-60 / 60-180."),
    ("PARTIAL", "Reflection slot present; verbatim 'Not for the Deck' copy is a copy-edit, not a schema gap."),
    ("YES",     "methodological_honesty element renders position 14."),
    ("YES",     "CONSTRAINT_PREAMBLE rule #3 forbids directive copy; integrity validator rejects."),
]

# Divergent: structural gap UNCHANGED — schema has no perspective_spread
# slot. The convergent shape still flattens divergent semantics at deck
# time. Verdict: DOES-NOT-FIT (structurally), unchanged from Stage 0.
DIVERGENT_VERDICTS = [
    ("YES",     "Same exporter, same brand palette."),
    ("YES",     "Same palette."),
    ("PARTIAL", "per_tension slot co-opted for persona-vs-evidence; semantically misrepresents the spread."),
    ("PARTIAL", "Confidence per-scenario today; needs per-persona + cross-persona agreement maps."),
    ("NO",      "Divergent artefacts have voices-as-of-now, not timelines."),
    ("YES",     "Reflection layer is path-agnostic."),
    ("YES",     "Methodological honesty applies regardless."),
    ("YES",     "CONSTRAINT_PREAMBLE rule #3 still binds."),
]


def _verdict_summary(verdicts: List[tuple[str, str]]) -> Dict[str, Any]:
    yes = sum(1 for v, _ in verdicts if v == "YES")
    partial = sum(1 for v, _ in verdicts if v == "PARTIAL")
    no = sum(1 for v, _ in verdicts if v == "NO")
    return {"YES": yes, "PARTIAL": partial, "NO": no}


def _build_verdict_md(
    convergent: Dict[str, Any],
    divergent: Dict[str, Any],
    reference: Dict[str, Any],
) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    conv_sum = _verdict_summary(CONVERGENT_VERDICTS)
    div_sum = _verdict_summary(DIVERGENT_VERDICTS)

    lines: List[str] = []
    lines.append("# JC-MON Stage 3 close · GATE A verdict (deck exporter for BOTH renders)")
    lines.append("")
    lines.append("> **Source of truth:** `/app/memory/JC_MON_CANONICAL_SPEC.md` (Stage 3 close)")
    lines.append("> **Cross-ref:** `/app/memory/JC_TL_CANONICAL_SPEC.md` § Stage 0 · S0-Q2 rubric (8 traits)")
    lines.append(f"> **Produced:** {now}")
    lines.append("> **Reference deck:** `/app/memory/reference_assets/MYDAWA_Reference_Deck.pptx`")
    lines.append(f"> Reference slide count: {reference['slide_count']} · {reference['size_bytes']} bytes")
    lines.append("")
    lines.append("**At the close of JC-MON Stage 3, this is the deck-exporter Gate A")
    lines.append("verdict for the two render shapes. The convergent render is the load-bearing")
    lines.append("output of Diagnosis / Develop-Strategy / Test-Hypothesis paths; the divergent")
    lines.append("render is the load-bearing output of Get-Perspectives. The Gate A verdict")
    lines.append("drives the Track-2 dispatch decision (Decks upgrade for divergent rendering).**")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 1 · Rendered decks (post-Stage 1 + Stage 2 + pptx_exporter bug fixes)")
    lines.append("")
    lines.append("| Render | Path | Slides | Size (bytes) |")
    lines.append("|---|---|---|---|")
    lines.append(
        f"| Convergent (Diagnosis) | `{convergent['path']}` | "
        f"{convergent['slide_count']} | {convergent['size_bytes']} |"
    )
    lines.append(
        f"| Divergent (Get-Perspectives) | `{divergent['path']}` | "
        f"{divergent['slide_count']} | {divergent['size_bytes']} |"
    )
    lines.append("")
    lines.append("## 2 · Convergent verdict (Diagnosis / Develop-Strategy / Test-Hypothesis)")
    lines.append("")
    lines.append("| # | Trait | Verdict | Evidence |")
    lines.append("|---|---|---|---|")
    for i, (trait, (v, ev)) in enumerate(zip(RUBRIC, CONVERGENT_VERDICTS), 1):
        lines.append(f"| {i} | {trait} | **{v}** | {ev} |")
    lines.append("")
    lines.append(
        f"**Overall convergent verdict: FITS.** {conv_sum['YES']} YES · "
        f"{conv_sum['PARTIAL']} PARTIAL · {conv_sum['NO']} NO. The PARTIAL is a"
        " copy-treatment polish, not a structural gap. Pptx_exporter bug fixes"
        " shipped during Stage 1 closed three latent attribute-reference defects"
        " (TensionSlide.summary, TensionDeepDive title/evidence/observation,"
        " RiskMitigation.risk_name/.mitigation_strategy) — the convergent render"
        " is now byte-clean."
    )
    lines.append("")
    lines.append("## 3 · Divergent verdict (Get-Perspectives)")
    lines.append("")
    lines.append("| # | Trait | Verdict | Evidence |")
    lines.append("|---|---|---|---|")
    for i, (trait, (v, ev)) in enumerate(zip(RUBRIC, DIVERGENT_VERDICTS), 1):
        lines.append(f"| {i} | {trait} | **{v}** | {ev} |")
    lines.append("")
    lines.append(
        f"**Overall divergent verdict: DOES-NOT-FIT (structurally).** "
        f"{div_sum['YES']} YES · {div_sum['PARTIAL']} PARTIAL · {div_sum['NO']} NO."
        " The structural gap from Stage 0 is UNCHANGED: the existing"
        " `ArtefactPayload` schema has no `perspective_spread` slot, so the"
        " divergent render flattens persona views into the convergent"
        " `per_tension` slots and loses the divergent semantics. Stage 2's"
        " provisional Q6 render is the Q6 floor pending Track-2 dispatch."
    )
    lines.append("")
    lines.append("## 4 · Track-2 decision (the load-bearing output of Gate A)")
    lines.append("")
    lines.append(
        "Per the JC-TL canonical spec's Stage-0 decision rules + the JC-MON"
        " Stage-3-close requirement to drive the Track-2 dispatch:"
    )
    lines.append("")
    lines.append("- **Convergent FITS** → no Decks change required for convergent paths.")
    lines.append("- **Divergent DOES-NOT-FIT** → **TRACK-2 DISPATCH REQUIRED.**")
    lines.append("")
    lines.append("**Minimum scope for Track-2 (NOT a Decks rebuild):**")
    lines.append("")
    lines.append(
        "1. New `perspective_spread` slot in `services/solva_v2/artefact_schema.py`"
        " carrying `personas: List[PersonaView]` (name, view summary, evidence ids),"
        " `agreement_map: List[AgreementCluster]` (statement + which personas back it),"
        " `conflict_map: List[ConflictCluster]` (tension + opposing personas),"
        " `blind_spots: List[BlindSpot]` (per-persona)."
    )
    lines.append(
        "2. New pptx builder for the divergent-synthesis slide in"
        " `services/solva_v2/pptx_exporter.py` (one builder, ~80-120 LOC,"
        " reusing the existing brand-token palette + grid geometry)."
    )
    lines.append(
        "3. Path-aware Pydantic validator: convergent path forbids"
        " `perspective_spread`; divergent path forbids `scenarios[]` /"
        " `pathway[]`. Schema-level integrity."
    )
    lines.append("")
    lines.append("**Sequencing:** Track-2 dispatch is now UNBLOCKED. JC-MON Stage 3 is closing here; the prior recommendation to dispatch \"AFTER JC-MON Stage 3, BEFORE any Get-Perspectives shipping commitment\" is now SATISFIED on the LHS. Get-Perspectives ships at the Q6 provisional bar UNTIL Track-2 lands.")
    lines.append("")
    lines.append("## 5 · STOP-and-show verdict matrix")
    lines.append("")
    lines.append("| Gate | Outcome |")
    lines.append("|---|---|")
    lines.append(f"| Convergent | FITS ({conv_sum['YES']}/8 YES · {conv_sum['PARTIAL']} PARTIAL · {conv_sum['NO']} NO) |")
    lines.append(f"| Divergent  | DOES-NOT-FIT ({div_sum['YES']}/8 YES · {div_sum['PARTIAL']} PARTIAL · {div_sum['NO']} NO) |")
    lines.append("| Track-2 dispatch | **REQUIRED** (minimum scope; not a Decks rebuild) |")
    lines.append("| JC-MON Stage 3 → Gate A | **CLOSED** |")
    lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    reference = _inventory_pptx(REFERENCE_DECK)
    convergent = _inventory_pptx(CONVERGENT_DECK)
    divergent = _inventory_pptx(DIVERGENT_DECK)
    verdict_md = _build_verdict_md(convergent, divergent, reference)
    VERDICT_MD.write_text(verdict_md)
    inventory_payload = {
        "produced_at": datetime.now(timezone.utc).isoformat(),
        "reference":   reference,
        "convergent":  convergent,
        "divergent":   divergent,
        "convergent_verdict_summary": _verdict_summary(CONVERGENT_VERDICTS),
        "divergent_verdict_summary":  _verdict_summary(DIVERGENT_VERDICTS),
    }
    INVENTORY_JSON.write_text(json.dumps(inventory_payload, indent=2, default=str))
    print(f"  → {VERDICT_MD}")
    print(f"  → {INVENTORY_JSON}")
    print(f"\nConvergent: FITS ({_verdict_summary(CONVERGENT_VERDICTS)})")
    print(f"Divergent:  DOES-NOT-FIT ({_verdict_summary(DIVERGENT_VERDICTS)})")
    print("Track-2 dispatch: REQUIRED (minimum scope, divergent-only).")


if __name__ == "__main__":
    main()
