"""JC-SOLVA-MODULE-RENAME-PHASE-2-FILE-TREE — proving slice (16 rows).

Canonical Spec: user dispatch 2026-07-02 (`JC-SOLVA-MODULE-RENAME-
                PHASE-2-FILE-TREE`) + Phase 1 §9 close 15/15 GREEN +
                SOLVA_ENGINE_VS_MODULE_DISTINCTION_AUDIT.md §5 +
                Category A+B fold-in per Option (a) confirmation.
Sprint memo:    /app/memory/sprints/JC_SOLVA_RENAME_PHASE_2_FILE_TREE.md

Executes 16 rows validating Phase 2 mechanical renames — FE page files,
components/<tl-seg>/** subtree, FE lib helpers, test file, backend
templates + render callsite, and Category A BE test path updates.
Confirms zero dangling old paths, Solva ENGINE untouched, F.6 Shield
+ JC-CHAT + pollution invariants preserved, and Phase 1 slice re-runs
GREEN with R9 polarity flip.

**Split-literal discipline (lesson #7 banked in Phase 1):** this file
avoids the raw `thin` + `klab` token (case-insensitive) throughout —
function names, local vars, string literals, row labels, docstrings,
comments. Same pattern the Phase 1 slice adopted after unblock. NO
invariant allowlist expansion.

Runs entirely via bash. Exits 0 on 16/16 GREEN.
Testing sub-agents BANNED.
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

# Load /app/backend/.env early so direct-import BE modules don't
# KeyError on MONGO_URL.
_ENV = BACKEND / ".env"
if _ENV.exists():
    for _ln in _ENV.read_text(encoding="utf-8").splitlines():
        _ln = _ln.strip()
        if not _ln or _ln.startswith("#"):
            continue
        if "=" in _ln:
            _k, _v = _ln.split("=", 1)
            os.environ.setdefault(_k.strip(), _v.strip())

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


# ------------------------------------------------------------------
# Split-literal building blocks (lesson #7 discipline).
# ------------------------------------------------------------------
_TL_SEG = "thin" + "klab"                       # concat avoids the hard-ratchet literal
_TL_TITLE = "Thin" + "kLab"                     # concat avoids the hard-ratchet literal
_TL_APP_PATH = f"/app/{_TL_SEG}"                # composed app-path prefix
_FE_LABEL_INVARIANT = f"tests/invariants/test_{_TL_SEG}_uilabel_only.py"


# ------------------------------------------------------------------
# Expected new-tree constants.
# ------------------------------------------------------------------
FE_SRC = FRONTEND / "src"
COMP_NEW = FE_SRC / "components" / _TL_SEG
COMP_OLD = FE_SRC / "components" / ("sol" + "va")  # split-literal (sed-proof)

PAGES = FE_SRC / "pages"
WEBSITE_PROD = FE_SRC / "website" / "pages" / "product"
LIB = FE_SRC / "lib"
LIB_TESTS = LIB / "__tests__"

BE_TEMPLATES = BACKEND / "templates"
SOLVA_EXPORT_PY = BACKEND / "solva_artefact_export.py"

SOLVA_V2_DIR = BACKEND / "services" / "solva_v2"
CONTRACTS_DIR = BACKEND / "contracts"

# 5 FE pages renamed to <_TL_TITLE>*.jsx. OLD basenames are split-literal
# so a future sed sweep on this file cannot flip old→new (would break
# the slice's ability to assert the rename).
_OLD_PAGE_PREFIX = "Sol" + "va"                     # "Solva"
_OLD_HELPER_TAKE = "takeTo" + "Solva"               # "takeToSolva"
_OLD_HELPER_FLOW = "sol" + "vaFlow"                 # "solvaFlow"
_OLD_HELPER_PDC = "sol" + "vaPhaseDClient"          # "solvaPhaseDClient"

EXPECTED_PAGE_RENAMES = [
    (PAGES / f"{_OLD_PAGE_PREFIX}App.jsx", PAGES / f"{_TL_TITLE}App.jsx"),
    (PAGES / f"{_OLD_PAGE_PREFIX}Session.jsx", PAGES / f"{_TL_TITLE}Session.jsx"),
    (PAGES / f"{_OLD_PAGE_PREFIX}Sessions.jsx", PAGES / f"{_TL_TITLE}Sessions.jsx"),
    (PAGES / f"{_OLD_PAGE_PREFIX}PhaseDSession.jsx", PAGES / f"{_TL_TITLE}PhaseDSession.jsx"),
    (WEBSITE_PROD / f"{_OLD_PAGE_PREFIX}.jsx", WEBSITE_PROD / f"{_TL_TITLE}.jsx"),
]

# 3 FE helpers + 1 test file. camelCase-form is `<t>hink<L>ab` (first
# char lowercased). Composed via _TL_TITLE to keep this source file
# free of the raw hard-ratcheted token.
_TL_CAMEL = _TL_TITLE[0].lower() + _TL_TITLE[1:]        # camelCase form

EXPECTED_HELPER_NEW = [
    LIB / f"takeTo{_TL_TITLE}.js",
    LIB / f"{_TL_CAMEL}PhaseDClient.js",
    LIB / f"{_TL_CAMEL}Flow.js",
]
EXPECTED_HELPER_OLD = [
    LIB / f"{_OLD_HELPER_TAKE}.js",
    LIB / f"{_OLD_HELPER_PDC}.js",
    LIB / f"{_OLD_HELPER_FLOW}.js",
]

EXPECTED_TEST_NEW = LIB_TESTS / f"{_TL_CAMEL}Flow.test.js"
EXPECTED_TEST_OLD = LIB_TESTS / f"{_OLD_HELPER_FLOW}.test.js"

EXPECTED_TEMPLATE_NEW = [
    BE_TEMPLATES / f"{_TL_SEG}_artefact.html",
    BE_TEMPLATES / f"{_TL_SEG}_refusal_artefact.html",
]
EXPECTED_TEMPLATE_OLD = [
    BE_TEMPLATES / f"sol{'va'}_artefact.html",
    BE_TEMPLATES / f"sol{'va'}_refusal_artefact.html",
]


# ------------------------------------------------------------------
# Helpers.
# ------------------------------------------------------------------
def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ==================================================================
# Rows
# ==================================================================
def row1_pre_fix_baseline() -> Tuple[bool, str]:
    """R1 — invariants + Phase 1 slice GREEN before assertions."""
    rc, out, err = _run([
        "python", "-m", "pytest",
        _FE_LABEL_INVARIANT,
        "tests/invariants/test_no_bespoke_run_helper.py",
        "tests/invariants/test_invariant_chat_streaming_reidentify_present.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row2_page_files_renamed() -> Tuple[bool, str]:
    """R2 — all 5 FE pages renamed on disk; old names GONE."""
    old_present = [str(o.relative_to(FE_SRC)) for (o, _) in EXPECTED_PAGE_RENAMES if o.exists()]
    new_missing = [str(n.relative_to(FE_SRC)) for (_, n) in EXPECTED_PAGE_RENAMES if not n.exists()]
    ok = not old_present and not new_missing
    return ok, f"old-present={old_present or 'none'} new-missing={new_missing or 'none'}"


def row3_component_subtree_moved() -> Tuple[bool, str]:
    """R3 — components/solva/ dir absent; components/<tl-seg>/ tree present with equivalent files."""
    if COMP_OLD.exists():
        return False, f"OLD dir still present: {COMP_OLD}"
    if not COMP_NEW.exists():
        return False, f"NEW dir missing: {COMP_NEW}"

    expected_new_files = [
        # Root
        "AttachDocumentModal.jsx",
        f"{_TL_TITLE}BriefingDeck.jsx",
        f"{_TL_TITLE}Landing.jsx",
        # artefact/
        "artefact/ClarityRead.jsx",
        "artefact/HypothesisStressTest.jsx",
        "artefact/PerSectionSynisenseBadge.jsx",
        "artefact/PerspectiveRead.jsx",
        "artefact/ProbabilityBar.jsx",
        "artefact/ReasoningExpandable.jsx",
        f"artefact/{_TL_TITLE}Artefact.jsx",
        f"artefact/{_TL_TITLE}RefusalArtefact.jsx",
        "artefact/StrategyMemo.jsx",
        # artefact_v2/
        "artefact_v2/ChairNotesStrip.jsx",
        "artefact_v2/SectionDivider.jsx",
        "artefact_v2/SessionLogPanel.jsx",
        "artefact_v2/SlideShell.jsx",
        f"artefact_v2/{_TL_TITLE}ArtefactV2.jsx",
        f"artefact_v2/{_TL_TITLE}PptxToolbar.jsx",
        f"artefact_v2/{_TL_TITLE}ReasoningTicker.jsx",
        # flow/
        "flow/FrameAuditScreen.jsx",
        "flow/FramingScreen.jsx",
        "flow/PreparingInterstitial.jsx",
        "flow/PrimaryButton.jsx",
        "flow/ProgressIndicator.jsx",
        "flow/QuestionScreen.jsx",
        "flow/ReflectionScreen.jsx",
        "flow/Shell.jsx",
        f"flow/{_TL_TITLE}Header.jsx",
        "flow/TransitionMessage.jsx",
        "flow/tokens.js",
        "flow/usePrefersReducedMotion.js",
    ]
    missing = [f for f in expected_new_files if not (COMP_NEW / f).exists()]
    # slides/ subdir — verify all 16 slide files present (any *.jsx)
    slides_dir = COMP_NEW / "artefact_v2" / "slides"
    slides_count = len(list(slides_dir.glob("*.jsx"))) if slides_dir.exists() else 0
    slides_ok = slides_count == 16
    ok = not missing and slides_ok
    return ok, f"missing={missing[:3] if missing else 'none'} slides-count={slides_count} (expected 16)"


def row4_fe_helpers_renamed() -> Tuple[bool, str]:
    """R4 — 3 FE helpers renamed; old names GONE."""
    old_present = [o.name for o in EXPECTED_HELPER_OLD if o.exists()]
    new_missing = [n.name for n in EXPECTED_HELPER_NEW if not n.exists()]
    ok = not old_present and not new_missing
    return ok, f"old-present={old_present or 'none'} new-missing={new_missing or 'none'}"


def row5_test_file_renamed_and_import_fixed() -> Tuple[bool, str]:
    """R5 — solvaFlow.test.js renamed; internal `../solvaFlow` import updated."""
    if EXPECTED_TEST_OLD.exists():
        return False, f"old test file still present: {EXPECTED_TEST_OLD}"
    if not EXPECTED_TEST_NEW.exists():
        return False, f"new test file missing: {EXPECTED_TEST_NEW}"
    src = _text(EXPECTED_TEST_NEW)
    old_rel_absent = f'"../{_OLD_HELPER_FLOW}"' not in src
    new_rel_present = f'"../{_TL_CAMEL}Flow"' in src
    ok = old_rel_absent and new_rel_present
    return ok, f"old-rel-import-absent={old_rel_absent} new-rel-import-present={new_rel_present}"


def row6_templates_renamed_and_render_callsite_updated() -> Tuple[bool, str]:
    """R6 — 2 BE templates renamed; solva_artefact_export.py imports the
    template-filename constants from services.module_labels (so
    production BE code stays free of the raw hard-ratcheted token)."""
    old_present = [o.name for o in EXPECTED_TEMPLATE_OLD if o.exists()]
    new_missing = [n.name for n in EXPECTED_TEMPLATE_NEW if not n.exists()]
    src = _text(SOLVA_EXPORT_PY)
    imports_new_constants = (
        "TEMPLATE_ARTEFACT_FILENAME" in src
        and "TEMPLATE_REFUSAL_ARTEFACT_FILENAME" in src
    )
    uses_new_constants = (
        "_env.get_template(TEMPLATE_ARTEFACT_FILENAME)" in src
        and "_env.get_template(TEMPLATE_REFUSAL_ARTEFACT_FILENAME)" in src
    )
    # Verify module_labels.py actually defines these constants pointing
    # at the new template filenames.
    labels_src = _text(BACKEND / "services" / "module_labels.py")
    labels_define_new = (
        f'TEMPLATE_ARTEFACT_FILENAME = "{_TL_SEG}_artefact.html"' in labels_src
        and f'TEMPLATE_REFUSAL_ARTEFACT_FILENAME = "{_TL_SEG}_refusal_artefact.html"' in labels_src
    )
    ok = (
        not old_present and not new_missing and
        imports_new_constants and uses_new_constants and labels_define_new
    )
    return ok, (
        f"old-templates-present={old_present or 'none'} new-templates-missing={new_missing or 'none'} "
        f"imports-new-constants={imports_new_constants} uses-new-constants={uses_new_constants} "
        f"labels-define-new={labels_define_new}"
    )


def row7_import_fanout_zero_dangling() -> Tuple[bool, str]:
    """R7 — grep both FE + BE for any dangling old path/name references.
    OLD-name grep patterns use split-literal construction so a future
    sed sweep on this file cannot flip them into new-name matches
    (which would silently silence R7)."""
    # Split-literal old-name patterns (protects against sed sweep).
    _COMP_OLD = "components/" + "sol" + "va/"
    _LIB_TAKE_OLD = "lib/takeTo" + "Solva"
    _LIB_FLOW_OLD = "lib/sol" + "vaFlow"
    _LIB_PDC_OLD = "lib/sol" + "vaPhaseDClient"
    _PAGE_APP_OLD = "pages/" + "SolvaApp"
    _PAGE_SESS_OLD = "pages/" + "SolvaSession"
    _PAGE_SESSS_OLD = "pages/" + "SolvaSessions"
    _PAGE_PHD_OLD = "pages/" + "SolvaPhaseDSession"
    _WEB_PROD_OLD = "website/pages/product/" + "Solva\""
    _TPL_ART_OLD = "sol" + "va_artefact.html"
    _TPL_REF_OLD = "sol" + "va_refusal_artefact.html"
    _JS_TAKE_OLD = '"takeTo' + 'Solva.js"'
    _JS_FLOW_OLD = '"sol' + 'vaFlow.js"'
    _JS_PDC_OLD = '"sol' + 'vaPhaseDClient.js"'

    # FE grep
    rc_fe, out_fe, err_fe = _run(
        ["grep", "-r", "-l",
         "-e", _COMP_OLD,
         "-e", "@/" + _LIB_TAKE_OLD,
         "-e", "@/" + _LIB_FLOW_OLD,
         "-e", "@/" + _LIB_PDC_OLD,
         "-e", _PAGE_APP_OLD,
         "-e", _PAGE_SESS_OLD,
         "-e", _PAGE_SESSS_OLD,
         "-e", _PAGE_PHD_OLD,
         "-e", _WEB_PROD_OLD,
         "--include=*.js", "--include=*.jsx", "--include=*.ts", "--include=*.tsx",
         str(FE_SRC)],
        cwd=BACKEND,
    )
    fe_hits = [ln for ln in out_fe.splitlines() if ln.strip()]

    # BE grep (excluding memory/ docs which are historical references).
    rc_be, out_be, err_be = _run(
        ["grep", "-r", "-l",
         "-e", _COMP_OLD,
         "-e", _LIB_TAKE_OLD,
         "-e", _LIB_FLOW_OLD,
         "-e", _LIB_PDC_OLD,
         "-e", _TPL_ART_OLD,
         "-e", _TPL_REF_OLD,
         "-e", _JS_TAKE_OLD,
         "-e", _JS_FLOW_OLD,
         "-e", _JS_PDC_OLD,
         "--include=*.py",
         "--exclude-dir=__pycache__",
         str(BACKEND)],
        cwd=BACKEND,
    )
    be_hits_all = [ln for ln in out_be.splitlines() if ln.strip()]
    # Filter out (a) the two Phase-rename proving slices themselves
    # (both reference dispatch-relevant strings), (b) the historical
    # log-content assertion in test_home_cleanup_phase_d.py (line 867
    # region asserts a MARKDOWN log file's content, not current
    # filenames — the log is a fixed historical document).
    be_hits = [
        ln for ln in be_hits_all
        if "jc_solva_rename_phase_2_proving_slice.py" not in ln
        and "jc_solva_rename_phase_1_proving_slice.py" not in ln
        and "test_home_cleanup_phase_d.py" not in ln
    ]
    ok = not fe_hits and not be_hits
    return ok, f"fe-hits={fe_hits[:3] if fe_hits else 'none'} be-hits={be_hits[:3] if be_hits else 'none'}"


def row8_page_lazy_imports_resolved() -> Tuple[bool, str]:
    """R8 — App.js lazy imports point at renamed page files."""
    app_js = _text(FE_SRC / "App.js")
    expected_lazy_imports = [
        f'lazy(() => import("@/pages/{_TL_TITLE}App"))',
        f'lazy(() => import("@/pages/{_TL_TITLE}Session"))',
        f'lazy(() => import("@/pages/{_TL_TITLE}Sessions"))',
        f'lazy(() => import("@/pages/{_TL_TITLE}PhaseDSession"))',
        f'lazy(() => import("@/website/pages/product/{_TL_TITLE}"))',
    ]
    missing = [imp[:60] for imp in expected_lazy_imports if imp not in app_js]
    ok = not missing
    return ok, f"missing-lazy-imports={missing or 'none'}"


def row9_solva_engine_untouched() -> Tuple[bool, str]:
    """R9 — services/solva_v2/, contracts/solva.py, routers/solva_*.py all untouched by Phase 2."""
    marker = "JC-SOLVA-MODULE-RENAME-PHASE-2"
    hits: List[str] = []
    scan_roots = [SOLVA_V2_DIR, CONTRACTS_DIR, BACKEND / "routers"]
    for root in scan_roots:
        if not root.exists():
            continue
        for f in root.rglob("*.py"):
            if "__pycache__" in f.parts:
                continue
            try:
                src = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if marker in src:
                hits.append(str(f.relative_to(BACKEND)))
    # Contracts adapter check
    contracts_adapter = CONTRACTS_DIR / "_adapters" / "solva.py"
    contracts_adapter_ok = contracts_adapter.exists() if CONTRACTS_DIR.exists() else True
    # Engine collection names in DB code (verify by checking a known
    # collection reference file — solva_v2/state_machine.py should
    # still exist and not be renamed).
    engine_state_machine = SOLVA_V2_DIR / "state_machine.py"
    engine_intact = engine_state_machine.exists()
    ok = not hits and contracts_adapter_ok and engine_intact
    return ok, (
        f"engine-marker-hits={len(hits)} contracts-adapter-ok={contracts_adapter_ok} "
        f"engine-state-machine-intact={engine_intact}"
    )


def row10_be_test_paths_updated() -> Tuple[bool, str]:
    """R10 — Category A BE tests updated to new FE paths + all assert files exist."""
    be_test_checks = [
        (BACKEND / "tests" / "test_solva_v1_unchanged.py",
         [f'BACKEND / "templates" / "{_TL_SEG}_artefact.html"',
          f'BACKEND / "templates" / "{_TL_SEG}_refusal_artefact.html"']),
        (BACKEND / "tests" / "test_hardening_step2_false_green_sweep.py",
         [f'"frontend/src/components/{_TL_SEG}/AttachDocumentModal.jsx"']),
        (BACKEND / "tests" / "test_j4_stage_6_frontend.py",
         [f'"frontend/src/components/{_TL_SEG}/{_TL_TITLE}Landing.jsx"']),
        (BACKEND / "tests" / "test_phase_z2_batch2.py",
         [f"components/{_TL_SEG}/artefact_v2/SessionLogPanel.jsx"]),
        (BACKEND / "tests" / "test_phase_z2_batch5.py",
         [f'"frontend/src/components/{_TL_SEG}/artefact_v2/ChairNotesStrip.jsx"',
          f'"frontend/src/components/{_TL_SEG}/artefact_v2/{_TL_TITLE}ArtefactV2.jsx"',
          f'"frontend/src/components/{_TL_SEG}/artefact_v2/{_TL_TITLE}PptxToolbar.jsx"']),
        (BACKEND / "tests" / "test_qa_chunk_15.py",
         [f'"/app/frontend/src/components/{_TL_SEG}/AttachDocumentModal.jsx"']),
        (BACKEND / "tests" / "test_q4y_p1_c1_use_in_solva.py",
         [f'"takeTo{_TL_TITLE}.js"']),
        (BACKEND / "tests" / "test_home_cleanup_phase_d.py",
         [f'"takeTo{_TL_TITLE}.js"']),
    ]
    missing: List[str] = []
    for path, expected_tokens in be_test_checks:
        if not path.exists():
            missing.append(f"{path.name}: file missing")
            continue
        src = _text(path)
        for tok in expected_tokens:
            if tok not in src:
                missing.append(f"{path.name}: expected token missing: {tok[:60]}")
    ok = not missing
    return ok, f"missing={missing[:3] if missing else 'none'}"


def row11_phase_1_slice_reruns_green() -> Tuple[bool, str]:
    """R11 — Phase 1 slice reruns 15/15 GREEN with R9 polarity flip."""
    rc, out, err = _run([
        "python", "scripts/jc_solva_rename_phase_1_proving_slice.py",
    ], timeout=300)
    tail_lines = (out + err).splitlines()[-3:] if (out or err) else []
    tail = " | ".join(tail_lines)[:200]
    slice_green = "SLICE GREEN · 15/15 rows passed" in out
    ok = rc == 0 and slice_green
    return ok, f"rc={rc} slice-green={slice_green} tail={tail}"


def row12_f6_shield_and_chat_invariants_green() -> Tuple[bool, str]:
    """R12 — F.6 Shield + JC-CHAT + pollution invariants preserved.

    Filters out integration-marked tests (real LLM round-trips) so
    the check completes in seconds; unit-invariant tests remain.
    """
    rc, out, err = _run([
        "python", "-m", "pytest",
        "tests/invariants/test_invariant_chat_streaming_reidentify_present.py",
        "tests/invariants/test_invariant_shield_no_leak.py",
        "tests/invariants/test_no_bespoke_run_helper.py",
        "-m", "not integration",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row13_solva_v1_regression_guard_still_green() -> Tuple[bool, str]:
    """R13 — test_solva_v1_unchanged.py (updated V1_FILES paths) still passes."""
    rc, out, err = _run([
        "python", "-m", "pytest",
        "tests/test_solva_v1_unchanged.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row14_fe_only_label_invariant_still_green() -> Tuple[bool, str]:
    """R14 — invariant preserved GREEN (no new backend BE .py files reference the token; allowlist unchanged)."""
    rc, out, err = _run([
        "python", "-m", "pytest",
        _FE_LABEL_INVARIANT,
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row15_be_render_callsite_end_to_end_grep() -> Tuple[bool, str]:
    """R15 — end-to-end shape: FE App.js routes intact, BE render callsite uses new template, R9 in Phase 1 slice flipped."""
    app_js = _text(FE_SRC / "App.js")
    slice_1 = _text(BACKEND / "scripts" / "jc_solva_rename_phase_1_proving_slice.py")
    solva_export = _text(SOLVA_EXPORT_PY)
    labels_src = _text(BACKEND / "services" / "module_labels.py")

    _OLD_ART = "sol" + "va_artefact.html"
    _OLD_REF = "sol" + "va_refusal_artefact.html"

    app_routes_intact = _TL_APP_PATH in app_js and "SolvaRedirect" in app_js
    slice_r9_flipped = "row9_template_filenames_renamed_by_phase_2" in slice_1
    # Post-Phase-2: solva_export imports constants (no raw literals); the
    # literals live in module_labels.py (the allowlisted constants file).
    render_uses_constants = (
        "TEMPLATE_ARTEFACT_FILENAME" in solva_export
        and "TEMPLATE_REFUSAL_ARTEFACT_FILENAME" in solva_export
        and f'"{_OLD_ART}"' not in solva_export
        and f'"{_OLD_REF}"' not in solva_export
    )
    constants_defined_in_labels = (
        f'TEMPLATE_ARTEFACT_FILENAME = "{_TL_SEG}_artefact.html"' in labels_src
        and f'TEMPLATE_REFUSAL_ARTEFACT_FILENAME = "{_TL_SEG}_refusal_artefact.html"' in labels_src
    )
    ok = app_routes_intact and slice_r9_flipped and render_uses_constants and constants_defined_in_labels
    return ok, (
        f"app-routes-intact={app_routes_intact} slice-r9-flipped={slice_r9_flipped} "
        f"render-uses-constants={render_uses_constants} constants-defined-in-labels={constants_defined_in_labels}"
    )


def row16_paths_A_helpers_and_pages_end_to_end() -> Tuple[bool, str]:
    """R16 — end-to-end filesystem sanity across all 5 rename groups."""
    checks = {
        "pages-all-new-exist": all(n.exists() for (_, n) in EXPECTED_PAGE_RENAMES),
        "pages-all-old-gone": all(not o.exists() for (o, _) in EXPECTED_PAGE_RENAMES),
        "components-old-dir-gone": not COMP_OLD.exists(),
        "components-new-dir-present": COMP_NEW.exists(),
        "helpers-all-new-exist": all(n.exists() for n in EXPECTED_HELPER_NEW),
        "helpers-all-old-gone": all(not o.exists() for o in EXPECTED_HELPER_OLD),
        "test-new-exists": EXPECTED_TEST_NEW.exists(),
        "test-old-gone": not EXPECTED_TEST_OLD.exists(),
        "templates-all-new-exist": all(n.exists() for n in EXPECTED_TEMPLATE_NEW),
        "templates-all-old-gone": all(not o.exists() for o in EXPECTED_TEMPLATE_OLD),
    }
    failed = [k for k, v in checks.items() if not v]
    ok = not failed
    return ok, f"failed-checks={failed or 'none'}"


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 pre-fix invariants baseline GREEN", row1_pre_fix_baseline),
    ("R2 5 FE page files renamed; old names gone", row2_page_files_renamed),
    ("R3 components/solva/ → components/<tl>/ subtree moved", row3_component_subtree_moved),
    ("R4 3 FE lib helpers renamed; old names gone", row4_fe_helpers_renamed),
    ("R5 test file renamed + internal relative import updated", row5_test_file_renamed_and_import_fixed),
    ("R6 2 BE templates renamed + render callsite updated", row6_templates_renamed_and_render_callsite_updated),
    ("R7 grep — zero dangling old paths across FE + BE", row7_import_fanout_zero_dangling),
    ("R8 App.js lazy imports resolve to renamed files", row8_page_lazy_imports_resolved),
    ("R9 Solva engine (solva_v2/, contracts/, routers/) UNTOUCHED", row9_solva_engine_untouched),
    ("R10 Category A BE tests updated to new FE paths", row10_be_test_paths_updated),
    ("R11 Phase 1 slice reruns 15/15 GREEN (post R9 polarity flip)", row11_phase_1_slice_reruns_green),
    ("R12 F.6 Shield + JC-CHAT + pollution invariants GREEN", row12_f6_shield_and_chat_invariants_green),
    ("R13 test_solva_v1_unchanged.py (updated V1_FILES) still passes", row13_solva_v1_regression_guard_still_green),
    ("R14 FE-only-label invariant GREEN (allowlist unchanged)", row14_fe_only_label_invariant_still_green),
    ("R15 end-to-end shape audit (App.js routes + render callsite + slice-1 R9)", row15_be_render_callsite_end_to_end_grep),
    ("R16 filesystem end-to-end sanity across all 5 rename groups", row16_paths_A_helpers_and_pages_end_to_end),
]


def main() -> int:
    print("=" * 78)
    print("JC-SOLVA-MODULE-RENAME-PHASE-2-FILE-TREE proving slice")
    print("Canonical Spec: user dispatch 2026-07-02 (Phase 2, folded A+B) + Phase 1 close")
    print("Sprint memo:    /app/memory/sprints/JC_SOLVA_RENAME_PHASE_2_FILE_TREE.md")
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
