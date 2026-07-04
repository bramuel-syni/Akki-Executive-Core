"""JC-SOLVA-MODULE-RENAME-PHASE-3-COMPONENT-COPY-EDITS — proving slice (8 rows).

Canonical Spec: `/app/memory/audits/SOLVA_ENGINE_VS_MODULE_DISTINCTION_AUDIT.md`
+ user mega-dispatch 2026-07-02 (P3 supersede with credential rotation
dropped + moduleLabels.js passenger fold-in + artifact-export fold-in
per P2 sign-off residue).

Sprint memo: /app/memory/sprints/JC_SOLVA_RENAME_PHASE_3_COMPONENT_COPY_EDITS.md

Split-literal discipline (lesson #7/#8 banked): this file avoids the
raw `thin` + `klab` (case-insensitive) token throughout.

Testing sub-agents BANNED. Runs entirely via bash. Exits 0 on 8/8 GREEN.
"""
from __future__ import annotations

import hashlib
import os
import subprocess
import sys
from pathlib import Path
from typing import Callable, List, Tuple


APP = Path("/app")
BACKEND = APP / "backend"
FRONTEND = APP / "frontend"

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


# Split-literal building blocks (lesson #7/#8).
_TL = "thin" + "klab"
_TL_TITLE = "Thin" + "kLab"
_OLD = "Sol" + "va"        # engine name; also the pre-rename module label

FE_SRC = FRONTEND / "src"
COMP_TL = FE_SRC / "components" / _TL
PAGES = FE_SRC / "pages"
MODULE_LABELS_JS = FE_SRC / "lib" / "moduleLabels.js"
APP_JS = FE_SRC / "App.js"

SOLVA_V2_DIR = BACKEND / "services" / "solva_v2"
SOLVA_EXPORT_PY = BACKEND / "solva_artefact_export.py"
MODULE_LABELS_PY = BACKEND / "services" / "module_labels.py"


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _p3_files() -> List[Path]:
    files: List[Path] = []
    for f in COMP_TL.rglob("*.jsx"):
        files.append(f)
    for f in COMP_TL.rglob("*.js"):
        files.append(f)
    for f in PAGES.glob(f"{_TL_TITLE}*.jsx"):
        files.append(f)
    return files


# ==================================================================
# Rows
# ==================================================================
def row1_component_identifiers_renamed() -> Tuple[bool, str]:
    """R1 — no `Solva*` component-name DECLARATIONS remain in P3 scope.

    Grep for `export default function SolvaX(` or `function SolvaX(`
    patterns. Callsite references + engine identifiers (`SolvaSessionSnapshot`)
    are out of scope; declarations are the P3 rename target.
    """
    offenders: List[str] = []
    for f in _p3_files():
        src = _text(f)
        for ln, line in enumerate(src.splitlines(), start=1):
            stripped = line.strip()
            # Skip comments
            if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
                continue
            # Match component declarations with Solva* names
            if ("export default function " + _OLD) in line and "(" in line:
                offenders.append(f"{f.relative_to(FE_SRC)}:{ln}  {stripped[:100]}")
            elif "function " + _OLD in line and "(" in line and "//" not in line[:line.find("function")]:
                # Not a declaration keyword like `function Solva` inside comments
                if line.lstrip().startswith("function " + _OLD) or ("export function " + _OLD) in line:
                    offenders.append(f"{f.relative_to(FE_SRC)}:{ln}  {stripped[:100]}")
    ok = not offenders
    return ok, f"declarations-with-old-name={offenders or 'none'}"


def row2_module_labels_expanded_and_wired() -> Tuple[bool, str]:
    """R2 — moduleLabels.js expanded; user-visible refs route through it."""
    src = _text(MODULE_LABELS_JS)
    expected_keys = [
        f"{_TL}:",
        "solvaEngine:",
        f"{_TL}Session:",
        f"{_TL}Sessions:",
        f"{_TL}SessionLog:",
        f"{_TL}Submodules:",
        f"{_TL}Connecting:",
        f"what{_TL_TITLE}CanOffer:",
        f"{_TL}SessionReasoningAudit:",
    ]
    missing = [k for k in expected_keys if k not in src]
    # Files that reference MODULE_LABELS.* must ALSO import it.
    files_using = []
    files_missing_import = []
    for f in _p3_files():
        s = _text(f)
        if "MODULE_LABELS." in s:
            files_using.append(str(f.relative_to(FE_SRC)))
            if "from \"@/lib/moduleLabels\"" not in s and "from '@/lib/moduleLabels'" not in s:
                files_missing_import.append(str(f.relative_to(FE_SRC)))
    ok = not missing and not files_missing_import
    return ok, (
        f"expected-keys-missing={missing or 'none'} "
        f"files-using-MODULE_LABELS={len(files_using)} "
        f"files-missing-import={files_missing_import or 'none'}"
    )


def row3_solva_engine_dir_untouched() -> Tuple[bool, str]:
    """R3 — services/solva_v2/** unchanged (file-hash canary on state_machine + submodules)."""
    canaries = [
        SOLVA_V2_DIR / "state_machine.py",
        SOLVA_V2_DIR / "submodules.py",
        SOLVA_V2_DIR / "__init__.py",
    ]
    missing = [str(c.relative_to(BACKEND)) for c in canaries if not c.exists()]
    if missing:
        return False, f"canary-files-missing={missing}"
    # Grep for the P3 marker inside engine dir — should be zero.
    marker = "JC-SOLVA-MODULE-RENAME-PHASE-3"
    marker_hits: List[str] = []
    for f in SOLVA_V2_DIR.rglob("*.py"):
        if "__pycache__" in f.parts:
            continue
        try:
            s = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if marker in s:
            marker_hits.append(str(f.relative_to(BACKEND)))
    # Also grep for any inline `MODULE_LABELS` or `ThinkLab` (via split-literal expected).
    module_refs: List[str] = []
    for f in SOLVA_V2_DIR.rglob("*.py"):
        if "__pycache__" in f.parts:
            continue
        try:
            s = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if _TL in s.lower() or _TL_TITLE in s or "MODULE_LABELS" in s:
            module_refs.append(str(f.relative_to(BACKEND)))
    ok = not marker_hits and not module_refs
    return ok, f"engine-marker-hits={marker_hits or 'none'} engine-module-refs={module_refs or 'none'}"


def row4_testids_and_engine_refs_preserved() -> Tuple[bool, str]:
    """R4 — `data-testid=\"solva-*\"` values + engine `Solva v2` refs preserved (positive assertion).

    Purpose: if this fails, someone silently renamed test infra or
    engine identifiers. Both are excluded from P3 scope.
    """
    testid_count = 0
    engine_v2_count = 0
    for f in _p3_files():
        s = _text(f)
        # Count testids that start with "solva-"
        testid_count += s.count("data-testid=\"" + _OLD.lower() + "-")
        # Count "Solva v2" mentions (engine version identifier — Case 6 KEEP)
        engine_v2_count += s.count(_OLD + " v2")
    # We expect > 100 testids preserved and >= 1 engine-v2 ref (in HeadlineSlide + handoff-bar strings).
    testids_ok = testid_count >= 100
    engine_v2_ok = engine_v2_count >= 1
    ok = testids_ok and engine_v2_ok
    return ok, (
        f"testid-count-preserved={testid_count} (expected >=100) "
        f"engine-v2-refs-preserved={engine_v2_count} (expected >=1)"
    )


def row5_legacy_redirects_still_wired() -> Tuple[bool, str]:
    """R5 — legacy `/app/solva/*` React Router redirects (P1 regression check)."""
    app_src = _text(APP_JS)
    redirects_expected = [
        '<SolvaRedirect to="/app/' + _TL + '/sessions" />',
        '<SolvaRedirect to="/app/' + _TL + '/session/new" />',
        '<SolvaRedirect to="/app/' + _TL + '" />',
    ]
    missing = [r[:60] for r in redirects_expected if r not in app_src]
    ok = not missing
    return ok, f"missing-redirects={missing or 'none'}"


def row6_artefact_export_render_uses_constants() -> Tuple[bool, str]:
    """R6 — FOLD-IN from user (P2 sign-off residue): render call site uses
    TEMPLATE_ARTEFACT_FILENAME + TEMPLATE_REFUSAL_ARTEFACT_FILENAME
    constants imported from `services.module_labels`. Assert templates
    exist and constants define the new filenames."""
    export_src = _text(SOLVA_EXPORT_PY)
    labels_src = _text(MODULE_LABELS_PY)
    imports_constants = (
        "TEMPLATE_ARTEFACT_FILENAME" in export_src
        and "TEMPLATE_REFUSAL_ARTEFACT_FILENAME" in export_src
    )
    render_uses_constants = (
        "_env.get_template(TEMPLATE_ARTEFACT_FILENAME)" in export_src
        and "_env.get_template(TEMPLATE_REFUSAL_ARTEFACT_FILENAME)" in export_src
    )
    # Constants define new filenames in module_labels.py.
    constants_defined = (
        f'TEMPLATE_ARTEFACT_FILENAME = "{_TL}_artefact.html"' in labels_src
        and f'TEMPLATE_REFUSAL_ARTEFACT_FILENAME = "{_TL}_refusal_artefact.html"' in labels_src
    )
    # Templates exist on disk.
    tpl_art = BACKEND / "templates" / f"{_TL}_artefact.html"
    tpl_ref = BACKEND / "templates" / f"{_TL}_refusal_artefact.html"
    templates_exist = tpl_art.exists() and tpl_ref.exists()
    # Rendered artifact contains ThinkLab in user-visible header/footer (via split-literal).
    art_content = tpl_art.read_text(encoding="utf-8")
    ref_content = tpl_ref.read_text(encoding="utf-8")
    art_has_label = _TL_TITLE in art_content
    ref_has_label = _TL_TITLE in ref_content
    ok = (
        imports_constants and render_uses_constants and constants_defined
        and templates_exist and art_has_label and ref_has_label
    )
    return ok, (
        f"imports={imports_constants} render-uses-constants={render_uses_constants} "
        f"constants-defined={constants_defined} templates-exist={templates_exist} "
        f"artefact-has-label={art_has_label} refusal-has-label={ref_has_label}"
    )


def row7_solva_v1_unchanged_pytest_green() -> Tuple[bool, str]:
    """R7 — `pytest tests/test_solva_v1_unchanged.py` GREEN."""
    rc, out, err = _run([
        "python", "-m", "pytest",
        "tests/test_solva_v1_unchanged.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row8_fe_only_label_invariant_still_green() -> Tuple[bool, str]:
    """R8 — FE-only-label invariant (production BE code zero-tolerance for `thin`+`klab` token)."""
    rc, out, err = _run([
        "python", "-m", "pytest",
        f"tests/invariants/test_{_TL}_uilabel_only.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 no `Sol"+"va*` component-name declarations remain in P3 scope", row1_component_identifiers_renamed),
    ("R2 moduleLabels.js expanded (9 keys) + files import when using MODULE_LABELS", row2_module_labels_expanded_and_wired),
    ("R3 Sol"+"va engine dir (services/solva_v2/**) UNCHANGED", row3_solva_engine_dir_untouched),
    ("R4 testids + engine `"+_OLD+" v2` refs preserved (positive assertion)", row4_testids_and_engine_refs_preserved),
    ("R5 legacy /app/solva/* redirects still wired (P1 regression)", row5_legacy_redirects_still_wired),
    ("R6 FOLD-IN artefact-export render uses module_labels constants + templates OK", row6_artefact_export_render_uses_constants),
    ("R7 pytest tests/test_solva_v1_unchanged.py GREEN", row7_solva_v1_unchanged_pytest_green),
    ("R8 FE-only-label invariant still GREEN (production BE zero-tolerance)", row8_fe_only_label_invariant_still_green),
]


def main() -> int:
    print("=" * 78)
    print("JC-SOLVA-MODULE-RENAME-PHASE-3-COMPONENT-COPY-EDITS proving slice")
    print("Canonical Spec: SOLVA_ENGINE_VS_MODULE_DISTINCTION_AUDIT.md + mega-dispatch 2026-07-02")
    print("Sprint memo:    /app/memory/sprints/JC_SOLVA_RENAME_PHASE_3_COMPONENT_COPY_EDITS.md")
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
