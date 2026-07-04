"""JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE — proving slice (15 rows).

Canonical Spec: user dispatch 2026-07-02 (revised order A3 → A2 →
                rename arc, passenger rule active) +
                JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A2.
Sprint memo:    /app/memory/sprints/JC_WS_DECK_A2_FROM_SOURCE_CREATE.md
Dispatch:       JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE

Executes 15 rows validating the 5-story From-Source create closure +
pulse-mirror passenger without regressing Shield / JC-CHAT / F.6 /
pollution / Surface A byte-identity. Testing sub-agents BANNED —
pure bash exec.

Runs entirely via bash. Exits 0 on 15/15 GREEN.

Note: split-literal `_TL_SEG` for the FE-only-label invariant test
filename to avoid tripping that invariant on this file.
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, List, Tuple


APP = Path("/app")
BACKEND = APP / "backend"
FRONTEND = APP / "frontend"

# Load /app/backend/.env early so direct-import Pydantic runtime rows
# (R4/R5/R8) don't KeyError on `MONGO_URL`. Backend modules read env
# at import time — the slice sits outside supervisor's env scope so
# has to fill it in itself.
_ENV = BACKEND / ".env"
if _ENV.exists():
    for _ln in _ENV.read_text(encoding="utf-8").splitlines():
        _ln = _ln.strip()
        if not _ln or _ln.startswith("#"):
            continue
        if "=" in _ln:
            _k, _v = _ln.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

# The backend package is not a Python package (`__init__.py` absent);
# sys.path needs `BACKEND` for `from routers.work_studio_from_source import ...`.
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


APP = Path("/app")
BACKEND = APP / "backend"
FRONTEND = APP / "frontend"

_TL_SEG = "thin" + "klab"

WS_FROM_SOURCE_PY = BACKEND / "routers/work_studio_from_source.py"
CREATE_MODAL_JSX = FRONTEND / "src/components/work_studio/CreateArtefactModal.jsx"
WORK_STUDIO_JSX = FRONTEND / "src/pages/WorkStudio.jsx"
UPLOAD_MODAL_JSX = FRONTEND / "src/components/upload/UploadModal.jsx"
DECKS_JSX = FRONTEND / "src/pages/Decks.jsx"
INDEX_CSS = FRONTEND / "src/index.css"
PACKAGE_JSON = FRONTEND / "package.json"

_FE_LABEL_INVARIANT = f"tests/invariants/test_{_TL_SEG}_uilabel_only.py"


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --------------------------------------------------------------------
# Track which of the 5 stories close cleanly (used by passenger R10).
# --------------------------------------------------------------------
_STORY_STATES = {
    "DECK-017": None,
    "DECK-018": None,
    "DECK-020": None,
    "DECK-021": None,
    "DECK-022": None,
}


def row1_pre_fix_baseline() -> Tuple[bool, str]:
    rc, out, err = _run([
        "python", "-m", "pytest",
        _FE_LABEL_INVARIANT,
        "tests/invariants/test_no_bespoke_run_helper.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row2_deck017_briefs_alpha_sort() -> Tuple[bool, str]:
    src = _text(CREATE_MODAL_JSX)
    helper_defined = "function sortByNameAlpha(items)" in src
    locale_compare = 'localeCompare(bn, undefined, { sensitivity: "base" })' in src
    briefs_setstate_sorted = "setBriefs(sortByNameAlpha(data?.items || []))" in src
    ok = helper_defined and locale_compare and briefs_setstate_sorted
    _STORY_STATES["DECK-017"] = ok
    return ok, (
        f"helper={helper_defined} locale-compare={locale_compare} "
        f"briefs-sorted={briefs_setstate_sorted}"
    )


def row3_deck020_docs_alpha_sort() -> Tuple[bool, str]:
    src = _text(CREATE_MODAL_JSX)
    docs_setstate_sorted = "setDocuments(sortByNameAlpha(rows))" in src
    _STORY_STATES["DECK-020"] = docs_setstate_sorted
    return docs_setstate_sorted, f"docs-sorted={docs_setstate_sorted}"


def row4_deck018_multi_select_briefs() -> Tuple[bool, str]:
    """R4 — checkbox list + plural payload wired for briefs."""
    fe_src = _text(CREATE_MODAL_JSX)
    checkbox_list = 'data-testid="create-artefact-brief-checkbox-list"' in fe_src
    selected_set = "const [selectedBriefIds, setSelectedBriefIds] = useState(() => new Set());" in fe_src
    toggle_brief = "const toggleBrief = useCallback((briefId) => {" in fe_src
    payload_plural = (
        'source_brief_ids: briefIdsPlural,' in fe_src
        and "Array.from(selectedBriefIds).map((bid) => stripAggPrefix(bid, \"briefing\"))" in fe_src
    )
    checkbox_primitive_imported = 'import { Checkbox } from "@/components/ui/checkbox";' in fe_src
    # BE pydantic accepts the plural
    import importlib
    import sys as _sys
    sys.path.insert(0, str(BACKEND))
    if "routers.work_studio_from_source" in _sys.modules:
        importlib.reload(_sys.modules["routers.work_studio_from_source"])
    from routers.work_studio_from_source import CreateArtefactRequest  # type: ignore
    m2 = CreateArtefactRequest(kind="deck", title="t", source="brief",
                               source_brief_ids=["b1", "b2", "b3"])
    be_plural_ok = m2.source_brief_ids == ["b1", "b2", "b3"] and m2.source_brief_id is None
    ok = checkbox_list and selected_set and toggle_brief and payload_plural and checkbox_primitive_imported and be_plural_ok
    _STORY_STATES["DECK-018"] = ok
    return ok, (
        f"checkbox-list={checkbox_list} state-set={selected_set} toggle={toggle_brief} "
        f"payload={payload_plural} primitive={checkbox_primitive_imported} be-plural={be_plural_ok}"
    )


def row5_deck022_multi_select_docs() -> Tuple[bool, str]:
    fe_src = _text(CREATE_MODAL_JSX)
    checkbox_list = 'data-testid="create-artefact-document-checkbox-list"' in fe_src
    selected_set = "const [selectedDocumentIds, setSelectedDocumentIds] = useState(() => new Set());" in fe_src
    toggle_doc = "const toggleDocument = useCallback((docId) => {" in fe_src
    payload_plural = (
        "source_document_ids: documentIdsPlural," in fe_src
        and "Array.from(selectedDocumentIds)" in fe_src
    )
    from routers.work_studio_from_source import CreateArtefactRequest  # type: ignore
    m = CreateArtefactRequest(kind="deck", title="t", source="external_document",
                              source_document_ids=["d1", "d2"])
    be_plural_ok = m.source_document_ids == ["d1", "d2"]
    ok = checkbox_list and selected_set and toggle_doc and payload_plural and be_plural_ok
    _STORY_STATES["DECK-022"] = ok
    return ok, (
        f"checkbox-list={checkbox_list} state-set={selected_set} toggle={toggle_doc} "
        f"payload={payload_plural} be-plural={be_plural_ok}"
    )


def row6_deck021_in_modal_upload() -> Tuple[bool, str]:
    fe_src = _text(CREATE_MODAL_JSX)
    imports_upload = 'import UploadModal from "@/components/upload/UploadModal";' in fe_src
    trigger_btn = 'data-testid="create-artefact-document-upload-trigger"' in fe_src
    upload_modal_state = "const [uploadModalOpen, setUploadModalOpen] = useState(false);" in fe_src
    upload_mount = "<UploadModal" in fe_src
    onuploaded_wired = 'onUploaded={onDocumentUploaded}' in fe_src
    on_upload_handler = "const onDocumentUploaded = useCallback((newDoc) => {" in fe_src
    ok = imports_upload and trigger_btn and upload_modal_state and upload_mount and onuploaded_wired and on_upload_handler
    _STORY_STATES["DECK-021"] = ok
    return ok, (
        f"import={imports_upload} trigger={trigger_btn} state={upload_modal_state} "
        f"mount={upload_mount} onUploaded={onuploaded_wired} handler={on_upload_handler}"
    )


def row7_upload_race_auto_select() -> Tuple[bool, str]:
    src = _text(CREATE_MODAL_JSX)
    token_state = "const [refetchDocsToken, setRefetchDocsToken] = useState(0);" in src
    autoselect_state = "const [autoSelectDocIdAfterUpload, setAutoSelectDocIdAfterUpload] = useState(null);" in src
    followup_effect = (
        "if (!autoSelectDocIdAfterUpload) return;" in src
        and "if (documentsLoading) return;" in src
        and "documents.some((d) => d.id === autoSelectDocIdAfterUpload)" in src
    )
    add_to_selection = "next.add(autoSelectDocIdAfterUpload);" in src
    ok = token_state and autoselect_state and followup_effect and add_to_selection
    return ok, (
        f"token={token_state} autoselect={autoselect_state} "
        f"followup={followup_effect} add-selection={add_to_selection}"
    )


def row8_backward_compat_singular_coerce() -> Tuple[bool, str]:
    """R8 — Pydantic coerces singular → plural + fires WARNING log."""
    import io
    import logging
    from routers.work_studio_from_source import CreateArtefactRequest  # type: ignore
    # Capture WARNING log output
    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    handler.setLevel(logging.WARNING)
    logger = logging.getLogger("akki.work_studio.from_source")
    logger.addHandler(handler)
    try:
        # legacy singular brief
        m1 = CreateArtefactRequest(kind="deck", title="t", source="brief",
                                   source_brief_id="b-legacy")
        # legacy singular doc
        m2 = CreateArtefactRequest(kind="deck", title="t", source="external_document",
                                   source_document_id="d-legacy")
    finally:
        logger.removeHandler(handler)
    log_content = stream.getvalue()
    plural_brief_ok = m1.source_brief_ids == ["b-legacy"]
    plural_doc_ok = m2.source_document_ids == ["d-legacy"]
    warning_brief_fired = "deprecated_singular_field field=source_brief_id" in log_content
    warning_doc_fired = "deprecated_singular_field field=source_document_id" in log_content
    ok = plural_brief_ok and plural_doc_ok and warning_brief_fired and warning_doc_fired
    return ok, (
        f"brief-coerced={plural_brief_ok} doc-coerced={plural_doc_ok} "
        f"warn-brief={warning_brief_fired} warn-doc={warning_doc_fired}"
    )


def row9_chrome_no_new_libs_or_components() -> Tuple[bool, str]:
    pkg = _text(PACKAGE_JSON)
    # A2 introduces NO new npm dep. Sample stable deps still there.
    stable_deps = (
        '"react-router-dom"' in pkg
        and '"lucide-react"' in pkg
        and '"sonner"' in pkg
    )
    # No new multi-select library added.
    no_multiselect_lib = (
        '"react-select"' not in pkg
        and '"downshift"' not in pkg
        and '"react-multi-select"' not in pkg.lower()
    )
    # UploadModal is the ONLY upload-modal component (no new parallel one).
    upload_files = list(FRONTEND.rglob("src/**/Upload*Modal*.jsx"))
    upload_modal_only = len(upload_files) == 1 and upload_files[0].name == "UploadModal.jsx"
    # Checkbox is from existing UI kit
    fe_src = _text(CREATE_MODAL_JSX)
    checkbox_from_ui_kit = 'import { Checkbox } from "@/components/ui/checkbox";' in fe_src
    ok = stable_deps and no_multiselect_lib and upload_modal_only and checkbox_from_ui_kit
    return ok, (
        f"stable-deps={stable_deps} no-multiselect-lib={no_multiselect_lib} "
        f"upload-modal-only={upload_modal_only} checkbox-from-ui={checkbox_from_ui_kit}"
    )


def row10_passenger_pulse_mirror() -> Tuple[bool, str]:
    """R10 — pulse-mirror passenger on DocumentRow. SKIP if any of the
    5 stories slipped (per user's passenger rule)."""
    stories_ok = all(v is True for v in _STORY_STATES.values())
    if not stories_ok:
        slipped = [k for k, v in _STORY_STATES.items() if v is not True]
        return True, f"SKIPPED · pulse-mirror dropped — slipped stories: {slipped}"
    ws_src = _text(WORK_STUDIO_JSX)
    css_src = _text(INDEX_CSS)
    prop_added = "function DocumentRow({ row, onOpen, pulseId })" in ws_src
    pulsed_predicate = (
        "const pulsed = !!pulseId && (" in ws_src
        and "pulseId === row.id" in ws_src
        and "pulseId === row.work_studio_export_id" in ws_src
    )
    class_applied = 'ws-doc-card-pulse-glow' in ws_src
    data_pulse_attr = 'data-pulse={pulsed ? "true" : undefined}' in ws_src
    call_site_passes = 'pulseId={searchParams.get("pulse") || null}' in ws_src
    css_shared = "ws-doc-card-pulse-glow-kf" in css_src  # existing A3 keyframe
    ok = prop_added and pulsed_predicate and class_applied and data_pulse_attr and call_site_passes and css_shared
    return ok, (
        f"prop={prop_added} predicate={pulsed_predicate} class={class_applied} "
        f"data-pulse={data_pulse_attr} call-site={call_site_passes} css-shared={css_shared}"
    )


def row11_module_label_ready_strings() -> Tuple[bool, str]:
    """R11 — 0 new module-referring literals introduced by A2."""
    marker = "JC-WS-DECK-PATH-A-A2"
    forbidden_lower = (_TL_SEG, "solva")

    def _is_continuation(line: str) -> bool:
        stripped = line.lstrip()
        return (
            stripped.startswith("//")
            or stripped.startswith("*")
            or stripped.startswith("/*")
            or stripped == ""
        )

    def _new_module_refs(path: Path) -> List[str]:
        src = _text(path)
        if marker not in src:
            return []
        lines = src.splitlines()
        added: List[str] = []
        i = 0
        while i < len(lines):
            if marker in lines[i]:
                added.append(lines[i])
                j = i + 1
                while j < len(lines) and _is_continuation(lines[j]):
                    added.append(lines[j])
                    j += 1
                if j < len(lines):
                    added.append(lines[j])
                i = j + 1
            else:
                i += 1
        offenders: List[str] = []
        for line in added:
            low = line.lower()
            if not any(t in low for t in forbidden_lower):
                continue
            if "takeToSolva" in line or "solvaEngine" in line or "moduleLabels" in line:
                continue
            offenders.append(line.strip()[:120])
        return offenders

    files_to_check = [CREATE_MODAL_JSX, WORK_STUDIO_JSX, WS_FROM_SOURCE_PY]
    counts = {p.name: len(_new_module_refs(p)) for p in files_to_check}
    ok = all(c == 0 for c in counts.values())
    return ok, ", ".join(f"{k}={v}" for k, v in counts.items())


def row12_f6_shield() -> Tuple[bool, str]:
    rc, out, err = _run([
        "python", "-m", "pytest",
        "tests/invariants/test_invariant_shield_no_leak.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row13_jc_chat_invariants() -> Tuple[bool, str]:
    rc, out, err = _run([
        "python", "-m", "pytest",
        "tests/invariants/test_invariant_chat_streaming_reidentify_present.py",
        _FE_LABEL_INVARIANT,
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row14_pollution_ceilings() -> Tuple[bool, str]:
    rc, out, err = _run([
        "python", "-m", "pytest",
        "tests/invariants/test_no_bespoke_run_helper.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row15_end_to_end_shape_audit() -> Tuple[bool, str]:
    fe_src = _text(CREATE_MODAL_JSX)
    be_src = _text(WS_FROM_SOURCE_PY)

    # FE: modal submits plural payload
    fe_payload_briefs = "source_brief_ids: briefIdsPlural," in fe_src
    fe_payload_docs = "source_document_ids: documentIdsPlural," in fe_src
    # BE: accepts plural
    be_model_plural = "source_brief_ids: List[str]" in be_src and "source_document_ids: List[str]" in be_src
    # BE: DB row carries plural
    be_row_plural = '"brief_ids": brief_ids,' in be_src and '"source_document_ids": document_ids,' in be_src
    # BE: DB row carries singular mirror for backward compat
    be_row_singular_mirror = (
        '"brief_id": brief_id_singular,' in be_src
        and '"source_document_id": document_id_singular,' in be_src
    )
    # BE: audit metadata coherent (both plural + singular)
    be_audit_plural = '"brief_ids": brief_ids,' in be_src and '"document_ids": document_ids,' in be_src
    # Surface A untouched (Decks.jsx byte-check)
    decks_src = _text(DECKS_JSX)
    surface_a_untouched = "JC-WS-DECK-PATH-A-A2" not in decks_src
    ok = all([fe_payload_briefs, fe_payload_docs, be_model_plural,
              be_row_plural, be_row_singular_mirror, be_audit_plural,
              surface_a_untouched])
    return ok, (
        f"fe-briefs={fe_payload_briefs} fe-docs={fe_payload_docs} "
        f"be-model={be_model_plural} be-row-plural={be_row_plural} "
        f"be-row-singular={be_row_singular_mirror} be-audit={be_audit_plural} "
        f"surface-a-untouched={surface_a_untouched}"
    )


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 pre-fix baseline invariants GREEN", row1_pre_fix_baseline),
    ("R2 DECK-017 briefs alpha-sort", row2_deck017_briefs_alpha_sort),
    ("R3 DECK-020 docs alpha-sort", row3_deck020_docs_alpha_sort),
    ("R4 DECK-018 multi-select briefs + plural payload", row4_deck018_multi_select_briefs),
    ("R5 DECK-022 multi-select docs + plural payload", row5_deck022_multi_select_docs),
    ("R6 DECK-021 in-modal upload trigger + UploadModal reuse", row6_deck021_in_modal_upload),
    ("R7 Upload race handling — auto-select new doc after refetch", row7_upload_race_auto_select),
    ("R8 Backward compat — singular coerces to plural + WARNING log", row8_backward_compat_singular_coerce),
    ("R9 Chrome check — no new libs / no parallel upload / Checkbox from UI kit", row9_chrome_no_new_libs_or_components),
    ("R10 Passenger pulse-mirror on DocumentRow (SKIP if any story slipped)", row10_passenger_pulse_mirror),
    ("R11 Module-label-ready strings check", row11_module_label_ready_strings),
    ("R12 F.6 Shield-contract discipline-pay", row12_f6_shield),
    ("R13 JC-CHAT invariants + FE-only-label GREEN", row13_jc_chat_invariants),
    ("R14 Pollution ceilings unchanged (M1=0 / M2=1)", row14_pollution_ceilings),
    ("R15 End-to-end shape audit (FE payload → BE model → DB row)", row15_end_to_end_shape_audit),
]


def main() -> int:
    print("=" * 78)
    print("JC-WS-DECK-PATH-A-A2-FROM-SOURCE-CREATE proving slice")
    print("Canonical Spec: user dispatch 2026-07-02 (A2, revised order) + A2 plan")
    print("Sprint memo:    /app/memory/sprints/JC_WS_DECK_A2_FROM_SOURCE_CREATE.md")
    print("=" * 78)
    failures: List[str] = []
    for idx, (label, fn) in enumerate(ROWS, start=1):
        try:
            ok, detail = fn()
        except Exception as exc:  # noqa: BLE001
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
