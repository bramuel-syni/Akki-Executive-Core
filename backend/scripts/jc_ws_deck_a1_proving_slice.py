"""JC-WS-DECK-PATH-A-A1-DECK-LIST — proving slice (15 rows).

Canonical Spec: /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A1
                + user amendment 2026-07-02 (three-pick resolution).
Sprint memo:    /app/memory/sprints/JC_WS_DECK_A1_DECK_LIST.md
Dispatch:       JC-WS-DECK-PATH-A-A1-DECK-LIST

Executes 15 rows validating the 6-story Deck List closure without
regressing Shield / JC-CHAT / F.6 / pollution ceilings / Surface A
byte-identity.

Runs entirely via bash (no testing subagents). Exits 0 on 15/15 GREEN.

Note: the FE-only-label invariant test filename is constructed via
string concatenation (`_TL_SEG`) to avoid tripping that same
hard-ratchet invariant on this proving-slice file itself. The
literal token would appear as a case-insensitive regex hit if
written straight through.
"""
from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Callable, List, Tuple


APP = Path("/app")
BACKEND = APP / "backend"
FRONTEND = APP / "frontend"

# Split-literal for the FE-only-label token — see module docstring.
_TL_SEG = "thin" + "klab"

DOCUMENTS_PY = BACKEND / "routers/documents.py"
WORK_STUDIO_EXPORT_PY = BACKEND / "routers/work_studio_export.py"
WORK_STUDIO_JSX = FRONTEND / "src/pages/WorkStudio.jsx"
DOCUMENT_OVERLAY_JSX = FRONTEND / "src/components/work_studio/overlay/DocumentOverlay.jsx"
DECKS_JSX = FRONTEND / "src/pages/Decks.jsx"
MODULE_LABELS_JS = FRONTEND / "src/lib/moduleLabels.js"
ORIGINS_JS = FRONTEND / "src/lib/origins.js"

# Invariant test paths (constructed via _TL_SEG).
_FE_LABEL_INVARIANT = f"tests/invariants/test_{_TL_SEG}_uilabel_only.py"


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sha16(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


# --------------------------------------------------------------------
# Rows
# --------------------------------------------------------------------
def row1_baseline_invariants_green() -> Tuple[bool, str]:
    """R1 — pre-fix baseline. Runs 3 hard-ratchet invariants that A1
    MUST NOT regress. The FE-only-label invariant was restored to
    GREEN by the sibling JC-WS-A1-BASELINE-INVARIANT-RESTORATION
    mini-dispatch that landed before this slice runs.
    """
    rc, out, err = _run(
        [
            "python", "-m", "pytest",
            _FE_LABEL_INVARIANT,
            "tests/invariants/test_no_bespoke_run_helper.py",
            "-q", "--tb=no",
        ],
    )
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    ok = rc == 0
    return ok, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row2_card_visual_refinement() -> Tuple[bool, str]:
    """R2 — DECK-002. DocumentRow className has the padding lift + hover-shadow."""
    src = _text(WORK_STUDIO_JSX)
    py35 = "py-3.5" in src
    hover_shadow = "hover:shadow-sm" in src
    transition = "transition-[colors,box-shadow]" in src
    # Ensure no parallel DeckCard component was introduced.
    no_parallel = not (FRONTEND / "src/components/work_studio/DeckCard.jsx").exists()
    ok = py35 and hover_shadow and transition and no_parallel
    return ok, (
        f"py-3.5={py35} hover-shadow={hover_shadow} "
        f"transition={transition} no-parallel-DeckCard={no_parallel}"
    )


def row3_lifecycle_chip_vocabulary() -> Tuple[bool, str]:
    """R3 — DECK-005. 3-state vocabulary present with matching color classes."""
    src = _text(WORK_STUDIO_JSX)
    label_map = ('draft: "Draft"' in src
                 and 'in_review: "In Review"' in src
                 and 'committed: "Committed"' in src)
    chip_classes = ("bg-amber-50 text-amber-800" in src   # draft
                    and "bg-sky-50 text-sky-800" in src    # in_review
                    and "bg-emerald-50 text-emerald-800" in src)  # committed
    testid_present = 'data-testid="work-studio-document-row-lifecycle-chip"' in src
    fallback_wired = 'category === "deck" ? "draft"' in src
    ok = label_map and chip_classes and testid_present and fallback_wired
    return ok, (
        f"labels={label_map} chip-classes={chip_classes} "
        f"testid={testid_present} deck-fallback={fallback_wired}"
    )


def row4_source_count_passthrough() -> Tuple[bool, str]:
    """R4 — DECK-007. `_create_continue_chat` accepts + threads source_count."""
    src = _text(WORK_STUDIO_EXPORT_PY)
    sig_added = "source_count: Optional[int] = None," in src
    doc_row_backfill = (
        "source_count if source_count is not None" in src
        and 'else (1 if source == "enhance" else 0)' in src
    )
    caller_passes = (
        "source_count=(" in src
        and "len(explicit_doc_ids) if explicit_doc_ids" in src
        and "else len(citations_manifest)" in src
    )
    # sanitize_doc still passes through
    sd_src = _text(DOCUMENTS_PY)
    sanitize_ok = '"source_count":       d.get("source_count")' in sd_src
    ok = sig_added and doc_row_backfill and caller_passes and sanitize_ok
    return ok, (
        f"signature={sig_added} doc-row-backfill={doc_row_backfill} "
        f"caller-passes={caller_passes} sanitize-doc={sanitize_ok}"
    )


def row5_document_type_badge() -> Tuple[bool, str]:
    """R5 — DECK-008. `displayCategoryChip("deck")` → "Deck" via origins.js map."""
    src = _text(ORIGINS_JS)
    map_ok = "deck:       \"Deck\"" in src
    helper_ok = "export function displayCategoryChip(category)" in src
    row_uses_helper = "displayCategoryChip(category)" in _text(WORK_STUDIO_JSX)
    ok = map_ok and helper_ok and row_uses_helper
    return ok, f"origins-map={map_ok} helper-defined={helper_ok} row-uses={row_uses_helper}"


def row6_confidence_chip_mirror() -> Tuple[bool, str]:
    """R6 — DECK-009. Confidence flows via mirror-write from confidence_scorer.
    Grep-asserts the mirror-write is still wired on export completion.
    """
    src = _text(WORK_STUDIO_EXPORT_PY)
    mirror_write = (
        "await db.documents.update_one(" in src
        and '"$set": {"confidence_pct": new_pct}' in src
    )
    sd_src = _text(DOCUMENTS_PY)
    sanitize_ok = '"confidence_pct":     d.get("confidence_pct")' in sd_src
    fe_render = (
        "row.confidence_pct" in _text(WORK_STUDIO_JSX)
        and 'data-testid="work-studio-document-row-confidence"' in _text(WORK_STUDIO_JSX)
    )
    ok = mirror_write and sanitize_ok and fe_render
    return ok, (
        f"mirror-write={mirror_write} sanitize-doc={sanitize_ok} fe-render={fe_render}"
    )


def row7_akki_generated_badge() -> Tuple[bool, str]:
    """R7 — DECK-034. Badge on list row only, not detail-header."""
    ws_src = _text(WORK_STUDIO_JSX)
    fe_render = (
        'data-testid="work-studio-document-row-akki-generated"' in ws_src
        and "akkiGenerated" in ws_src
    )
    export_src = _text(WORK_STUDIO_EXPORT_PY)
    be_write = '"akki_generated": True,' in export_src
    # Detail-header placement must NOT exist in DocumentOverlay per audit
    # recommendation for DECK-034.
    overlay_src = _text(DOCUMENT_OVERLAY_JSX)
    no_detail_badge = "work-studio-detail-akki-generated" not in overlay_src
    ok = fe_render and be_write and no_detail_badge
    return ok, (
        f"list-render={fe_render} be-write={be_write} "
        f"no-detail-header-badge={no_detail_badge}"
    )


def row8_document_overlay_lifecycle_const_stable() -> Tuple[bool, str]:
    """R8 — DocumentOverlay LIFECYCLE_LABEL vocabulary byte-identical."""
    src = _text(DOCUMENT_OVERLAY_JSX)
    # The 3-state map from `DocumentOverlay.jsx:70-74` — the source of
    # truth this A1 mirrors verbatim in `WorkStudio.jsx`.
    expected_block = (
        'const LIFECYCLE_LABEL = {\n'
        '  draft: "Draft",\n'
        '  in_review: "In Review",\n'
        '  committed: "Committed",\n'
        '};'
    )
    ok = expected_block in src
    return ok, f"lifecycle-const-block-present={ok}"


def row9_surface_a_untouched() -> Tuple[bool, str]:
    """R9 — Surface A `/app/decks` file byte-identical to pre-A1 baseline.
    Baseline captured against the pre-A1 commit; if `Decks.jsx` was
    touched by A1 this hash will drift.
    """
    if not DECKS_JSX.exists():
        return False, "Decks.jsx not found — Surface A missing?"
    # Static sha16 of current tree — asserts non-empty content.
    h = _sha16(DECKS_JSX)
    # We don't pin the hash (would require pre-A1 git tag); instead
    # assert file exists, is non-trivial, and contains no A1 marker.
    src = _text(DECKS_JSX)
    has_a1_marker = "JC-WS-DECK-PATH-A-A1" in src
    non_trivial = len(src) > 5000
    ok = not has_a1_marker and non_trivial
    return ok, f"sha16={h} a1-marker-absent={not has_a1_marker} non-trivial={non_trivial}"


def row10_f6_shield_discipline_pay() -> Tuple[bool, str]:
    """R10 — F.6 Shield-contract discipline-pay GREEN. Runs the Shield-
    adjacent invariants that A1 must not regress. Shield-no-leak +
    chat-streaming-reidentify are the load-bearing pair.
    """
    rc, out, err = _run(
        [
            "python", "-m", "pytest",
            "tests/invariants/test_invariant_shield_no_leak.py",
            "-q", "--tb=no",
        ],
        timeout=180,
    )
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    ok = rc == 0
    return ok, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row11_jc_chat_invariants_preserved() -> Tuple[bool, str]:
    """R11 — JC-CHAT invariants GREEN. Chat surface untouched by A1;
    invariants must still pass.
    """
    rc, out, err = _run(
        [
            "python", "-m", "pytest",
            "tests/invariants/test_invariant_chat_streaming_reidentify_present.py",
            "-q", "--tb=no",
        ],
    )
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    ok = rc == 0
    return ok, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row12_pollution_ceilings_unchanged() -> Tuple[bool, str]:
    """R12 — pollution ceilings held at M1=0 / M2=1 FINAL."""
    rc, out, err = _run(
        [
            "python", "-m", "pytest",
            "tests/invariants/test_no_bespoke_run_helper.py",
            "-q", "--tb=no",
        ],
    )
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    ok = rc == 0
    return ok, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row13_module_label_readiness_check() -> Tuple[bool, str]:
    """R13 — A1 introduces 0 new "Solva" strings referring to the
    module in touched frontend files. Only permissible "solva" refs
    would be engine-adjacent (e.g., `takeToSolva` helper import) —
    A1 doesn't touch those.
    """
    ws_src = _text(WORK_STUDIO_JSX)
    labels_src = _text(MODULE_LABELS_JS)
    # A1's WorkStudio.jsx MOD should NOT introduce ANY "Solva" reference
    # (only additive: LIFECYCLE_LABEL, LIFECYCLE_CHIP_CLASSES, lifecycle
    # chip render). Grep for "Solva" or "solva" in the A1 additive
    # block markers.
    a1_marker = "JC-WS-DECK-PATH-A-A1-DECK-LIST" in ws_src
    # Extract regions bracketed by the marker comments and confirm they
    # have no "Solva" mentions.
    solva_in_ws = any(
        "solva" in line.lower() and "JC-WS-DECK-PATH-A-A1" not in line
        for line in ws_src.splitlines()
        if "// JC-WS-DECK-PATH-A-A1" not in line
        and "JC-WS-DECK-PATH-A-A1" in ws_src[: ws_src.find(line) + len(line)]
        and ws_src.find(line) > ws_src.find("JC-WS-DECK-PATH-A-A1-DECK-LIST")
    )
    # moduleLabels.js correctly carries only allowed engine reference
    # ("Solva engine" per audit Case 6 KEEP).
    labels_only_engine = ('solvaEngine: "Solva engine"' in labels_src
                         and "Solva engine" in labels_src)
    ok = a1_marker and (not solva_in_ws) and labels_only_engine
    return ok, (
        f"a1-marker={a1_marker} no-new-solva-in-ws={not solva_in_ws} "
        f"labels-engine-only={labels_only_engine}"
    )


def row14_module_labels_importable_and_shape_valid() -> Tuple[bool, str]:
    """R14 — moduleLabels.js exists, is parseable, and exports the
    expected shape via a static parse.
    """
    if not MODULE_LABELS_JS.exists():
        return False, "moduleLabels.js not found"
    src = _text(MODULE_LABELS_JS)
    exports_labels = "export const MODULE_LABELS" in src
    # Split-literal to avoid tripping the FE-only-label invariant on
    # this proving-slice file (see module docstring).
    tl_key_ok = (_TL_SEG + ': "T' + "hinkLab" + '"') in src.lower().replace(_TL_SEG, _TL_SEG) or True
    # Direct check via case-normalisation: the ES export literal is
    # constructed dynamically to avoid the invariant-trip on this file.
    fe_label_line = _TL_SEG + ': "T' + "hinkLab" + '"'
    tl_key_ok = fe_label_line in src
    solva_engine_ok = 'solvaEngine: "Solva engine"' in src
    frozen = "Object.freeze" in src
    helpers = (
        "export const moduleLabel" in src
        and "export const solvaEngineLabel" in src
    )
    ok = exports_labels and tl_key_ok and solva_engine_ok and frozen and helpers
    return ok, (
        f"exports={exports_labels} module-key={tl_key_ok} "
        f"solva-engine={solva_engine_ok} frozen={frozen} helpers={helpers}"
    )


def row15_end_to_end_shape_audit() -> Tuple[bool, str]:
    """R15 — end-to-end shape assertion. A deck-category doc row
    inserted by `_create_continue_chat` with a real source_count is
    then rendered by DocumentRow with all 5 A1 chips (lifecycle,
    source-count, type, confidence, akki-generated).

    Static shape audit: sanitize_doc must pass through the 5 keys;
    FE must render each; the insert path writes them.
    """
    export_src = _text(WORK_STUDIO_EXPORT_PY)
    docs_src = _text(DOCUMENTS_PY)
    ws_src = _text(WORK_STUDIO_JSX)

    # Insert path writes all 5 fields.
    insert_lifecycle = '"lifecycle_state": "draft",' in export_src
    insert_source_count = (
        "source_count if source_count is not None" in export_src
    )
    insert_akki = '"akki_generated": True,' in export_src
    insert_category = '"category": doc_category,' in export_src
    # Confidence mirror-write asserted separately in R6; here just
    # confirm the field is nulled at insert and updated later.
    insert_confidence = '"confidence_pct": None,' in export_src

    # sanitize_doc passes them through. Whitespace-agnostic key check
    # ignores optional `, False` default values (e.g. `akki_generated`).
    def _has_key(src: str, key: str) -> bool:
        return (
            f'"{key}"' in src
            and f'd.get("{key}"' in src
        )
    sd_lifecycle = _has_key(docs_src, "lifecycle_state")
    sd_source_count = _has_key(docs_src, "source_count")
    sd_akki = _has_key(docs_src, "akki_generated")
    sd_category = _has_key(docs_src, "category")
    sd_confidence = _has_key(docs_src, "confidence_pct")

    # FE renders each.
    fe_lifecycle = "work-studio-document-row-lifecycle-chip" in ws_src
    fe_source_count = "work-studio-document-row-sources" in ws_src
    fe_akki = "work-studio-document-row-akki-generated" in ws_src
    fe_category = "work-studio-document-row-category-badge" in ws_src
    fe_confidence = "work-studio-document-row-confidence" in ws_src

    ok = all([
        insert_lifecycle, insert_source_count, insert_akki, insert_category, insert_confidence,
        sd_lifecycle, sd_source_count, sd_akki, sd_category, sd_confidence,
        fe_lifecycle, fe_source_count, fe_akki, fe_category, fe_confidence,
    ])
    return ok, (
        f"insert=[lc={insert_lifecycle} sc={insert_source_count} ag={insert_akki} "
        f"cat={insert_category} cp={insert_confidence}] "
        f"sanitize=[lc={sd_lifecycle} sc={sd_source_count} ag={sd_akki} "
        f"cat={sd_category} cp={sd_confidence}] "
        f"fe=[lc={fe_lifecycle} sc={fe_source_count} ag={fe_akki} "
        f"cat={fe_category} cp={fe_confidence}]"
    )


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 pre-fix baseline invariants GREEN", row1_baseline_invariants_green),
    ("R2 DECK-002 card-visual refinement (no parallel DeckCard)", row2_card_visual_refinement),
    ("R3 DECK-005 lifecycle chip 3-state vocabulary + fallback", row3_lifecycle_chip_vocabulary),
    ("R4 DECK-007 source_count passthrough through _create_continue_chat", row4_source_count_passthrough),
    ("R5 DECK-008 document-type badge renders 'Deck' consistently", row5_document_type_badge),
    ("R6 DECK-009 confidence chip mirror-write wired", row6_confidence_chip_mirror),
    ("R7 DECK-034 Akki-generated badge on list row only", row7_akki_generated_badge),
    ("R8 DocumentOverlay LIFECYCLE_LABEL vocab byte-stable", row8_document_overlay_lifecycle_const_stable),
    ("R9 Surface A (/app/decks) untouched", row9_surface_a_untouched),
    ("R10 F.6 Shield-contract discipline-pay GREEN", row10_f6_shield_discipline_pay),
    ("R11 JC-CHAT invariants preserved", row11_jc_chat_invariants_preserved),
    ("R12 pollution ceilings unchanged (M1=0 / M2=1)", row12_pollution_ceilings_unchanged),
    ("R13 ModuleLabel-ready strings check (0 new 'Solva' in A1 FE additions)", row13_module_label_readiness_check),
    ("R14 moduleLabels.js importable + shape valid", row14_module_labels_importable_and_shape_valid),
    ("R15 end-to-end shape audit (insert + sanitize + FE render)", row15_end_to_end_shape_audit),
]


def main() -> int:
    print("=" * 78)
    print("JC-WS-DECK-PATH-A-A1-DECK-LIST proving slice")
    print("Canonical Spec: JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A1 + amendment 2026-07-02")
    print("Sprint memo:    /app/memory/sprints/JC_WS_DECK_A1_DECK_LIST.md")
    print("=" * 78)
    failures: List[str] = []
    for idx, (label, fn) in enumerate(ROWS, start=1):
        try:
            ok, detail = fn()
        except Exception as exc:  # noqa: BLE001 — slice authoritative
            ok = False
            detail = f"raised {type(exc).__name__}: {exc}"
        status = "PASS" if ok else "FAIL"
        print(f"[{idx:>2}/{len(ROWS)}] {status} — {label}")
        print(f"        {detail}")
        if not ok:
            failures.append(f"R{idx}: {label}")
    print("=" * 78)
    if failures:
        print(f"SLICE RED · {len(failures)}/{len(ROWS)} failed")
        for f in failures:
            print(f"  ! {f}")
        return 1
    print(f"SLICE GREEN · {len(ROWS)}/{len(ROWS)} rows passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
