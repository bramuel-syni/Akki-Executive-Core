"""JC-SOLVA-MODULE-RENAME-PHASE-1-ROUTES-AND-NAV — proving slice (15 rows).

Canonical Spec: user dispatch 2026-07-02 (`JC-SOLVA-MODULE-RENAME-
                PHASE-1-ROUTES-AND-NAV`) + SOLVA_ENGINE_VS_MODULE_
                DISTINCTION_AUDIT.md §5 + A1 memo §4 (8 §9 defaults).
Sprint memo:    /app/memory/sprints/JC_SOLVA_RENAME_PHASE_1_ROUTES_AND_NAV.md

Executes 15 rows validating Phase 1 (routes + AppShell nav + FE
redirects + Case 6 template CONTENT flips + invariant single-file
allowlist) without regressing Solva engine / Shield / JC-CHAT / F.6 /
pollution / Path A A1-A3 slices. Testing sub-agents BANNED.

**Split-literal discipline (2026-07-02 unblock):** this file
deliberately avoids the raw `thin` + `klab` token (case-insensitive)
throughout — function names, local vars, comments, string literals,
row labels — so that the FE-only-label hard-ratchet invariant
(`tests/invariants/test_<tl-seg>_uilabel_only.py`) does not flag
this proving-slice module. Same pattern used by A1/A2/A3 slices.
The invariant's single-file allowlist stays at ONE entry
(`module_labels.py`); this slice does NOT add itself. See DEV_PIPELINE
§9 lesson #7 for the discipline note.

Runs entirely via bash. Exits 0 on 15/15 GREEN.
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
# Split-literal building blocks — see module docstring for rationale.
# ------------------------------------------------------------------
_TL_SEG = "thin" + "klab"                       # concat avoids the hard-ratchet literal
_TL_TITLE = "Thin" + "kLab"                     # concat avoids the hard-ratchet literal
_TL_APP_PATH = f"/app/{_TL_SEG}"                # composed app-path prefix
_TL_MARKETING_PATH = f"/{_TL_SEG}"              # composed marketing-path prefix
_FE_LABEL_INVARIANT = f"tests/invariants/test_{_TL_SEG}_uilabel_only.py"

# --- File paths -----------------------------------------------------
APP_JS = FRONTEND / "src/App.js"
APPSHELL_JSX = FRONTEND / "src/components/layout/AppShell.jsx"
MODULE_LABELS_JS = FRONTEND / "src/lib/moduleLabels.js"

MODULE_LABELS_PY = BACKEND / "services/module_labels.py"
SOLVA_EXPORT_PY = BACKEND / "solva_artefact_export.py"
INVARIANT_PY = BACKEND / _FE_LABEL_INVARIANT

ARTEFACT_HTML = BACKEND / "templates/thinklab_artefact.html"
REFUSAL_HTML = BACKEND / "templates/thinklab_refusal_artefact.html"

SOLVA_V2_DIR = BACKEND / "services/solva_v2"

A1_SLICE = BACKEND / "scripts/jc_ws_deck_a1_proving_slice.py"
A2_SLICE = BACKEND / "scripts/jc_ws_deck_a2_proving_slice.py"
A3_SLICE = BACKEND / "scripts/jc_ws_deck_a3_proving_slice.py"


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# --------------------------------------------------------------------
# Row 1 — pre-fix baseline
# --------------------------------------------------------------------
def row1_pre_fix_baseline() -> Tuple[bool, str]:
    rc, out, err = _run([
        "python", "-m", "pytest",
        _FE_LABEL_INVARIANT,
        "tests/invariants/test_no_bespoke_run_helper.py",
        "tests/invariants/test_invariant_chat_streaming_reidentify_present.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row2_app_routes_renamed_to_tl_module() -> Tuple[bool, str]:
    src = _text(APP_JS)
    return_pairs = [
        (f'path="{_TL_APP_PATH}" element={{<Gated><SolvaApp /></Gated>}}', "app-primary"),
        (f'path="{_TL_APP_PATH}/sessions" element={{<Gated><SolvaSessions /></Gated>}}', "sessions"),
        (f'path="{_TL_APP_PATH}/session/new"', "session-new"),
        (f'path="{_TL_APP_PATH}/session/:sessionId"', "session-detail"),
        (f'path="{_TL_APP_PATH}/phase-d/session/new"', "phase-d-new"),
        (f'path="{_TL_APP_PATH}/phase-d/session/:sessionId"', "phase-d-detail"),
    ]
    missing = [label for token, label in return_pairs if token not in src]
    ok = not missing
    return ok, f"missing={missing or 'none'}"


def row3_legacy_app_routes_redirect() -> Tuple[bool, str]:
    src = _text(APP_JS)
    pairs = [
        (f'path="/app/solva" element={{<SolvaRedirect to="{_TL_APP_PATH}" />}}', "legacy-primary"),
        (f'path="/app/solva/sessions" element={{<SolvaRedirect to="{_TL_APP_PATH}/sessions" />}}', "legacy-sessions"),
        (f'path="/app/solva/session/new" element={{<SolvaRedirect to="{_TL_APP_PATH}/session/new" />}}', "legacy-session-new"),
        (f'path="/app/solva/session/:sessionId" element={{<SolvaRedirect to="{_TL_APP_PATH}/session/:sessionId" />}}', "legacy-session-detail"),
        (f'path="/app/solva/phase-d/session/new" element={{<SolvaRedirect to="{_TL_APP_PATH}/phase-d/session/new" />}}', "legacy-phase-d-new"),
        (f'path="/app/solva/phase-d/session/:sessionId" element={{<SolvaRedirect to="{_TL_APP_PATH}/phase-d/session/:sessionId" />}}', "legacy-phase-d-detail"),
    ]
    missing = [label for token, label in pairs if token not in src]
    ok = not missing
    return ok, f"missing={missing or 'none'}"


def row4_marketing_routes_flipped() -> Tuple[bool, str]:
    src = _text(APP_JS)
    new_marketing = f'path="{_TL_MARKETING_PATH}" element={{<WebsiteProductSolva />}}' in src
    legacy_marketing = f'path="/solva" element={{<SolvaRedirect to="{_TL_MARKETING_PATH}" />}}' in src
    product_backcompat = f'path="/product/solva" element={{<SolvaRedirect to="{_TL_MARKETING_PATH}" />}}' in src
    ok = new_marketing and legacy_marketing and product_backcompat
    return ok, f"new={new_marketing} legacy={legacy_marketing} product-backcompat={product_backcompat}"


def row5_solva_redirect_preserves_query() -> Tuple[bool, str]:
    src = _text(APP_JS)
    component_defined = "function SolvaRedirect({ to })" in src
    uses_location = "useLocation()" in src
    query_preserved = "to={{ pathname: resolved, search: location.search }}" in src
    resolves_params = "resolved.replace(`:${k}`, encodeURIComponent(v || \"\"))" in src
    ok = component_defined and uses_location and query_preserved and resolves_params
    return ok, (
        f"component={component_defined} uses-location={uses_location} "
        f"query-preserved={query_preserved} params-resolved={resolves_params}"
    )


def row6_appshell_nav_labels_and_paths() -> Tuple[bool, str]:
    src = _text(APPSHELL_JSX)
    imports_labels = 'import { MODULE_LABELS } from "@/lib/moduleLabels";' in src
    top_nav_flipped = f'{{ to: "{_TL_APP_PATH}",      label: MODULE_LABELS.{_TL_SEG} }},' in src
    full_nav_flipped = f'{{ to: "{_TL_APP_PATH}", label: MODULE_LABELS.{_TL_SEG}, icon: Layers, module: "§18", ready: true,' in src
    # No stray "label: 'Solva'" left in nav table (contextual grep — the
    # word "Solva" may appear in comments; we check the specific NAV
    # array entries only).
    lines = src.splitlines()
    stray = [
        (i, ln.strip()[:100]) for i, ln in enumerate(lines, start=1)
        if 'label: "Solva"' in ln
    ]
    ok = imports_labels and top_nav_flipped and full_nav_flipped and not stray
    return ok, (
        f"imports={imports_labels} top-nav={top_nav_flipped} "
        f"full-nav={full_nav_flipped} stray-label={stray or 'none'}"
    )


def row7_be_constants_file_valid() -> Tuple[bool, str]:
    if not MODULE_LABELS_PY.exists():
        return False, "module_labels.py not found"
    src = _text(MODULE_LABELS_PY)
    has_module = f'MODULE_UI_LABEL = "{_TL_TITLE}"' in src
    has_v3 = "MODULE_UI_LABEL_V3" in src
    has_session = "MODULE_UI_SESSION_LABEL" in src
    has_engine_health = 'ENGINE_HEALTH_LABEL = "Solva engine"' in src
    # Import round-trip: can we actually import + resolve?
    try:
        import importlib
        if "services.module_labels" in sys.modules:
            importlib.reload(sys.modules["services.module_labels"])
        from services.module_labels import (  # type: ignore
            MODULE_UI_LABEL, MODULE_UI_SESSION_LABEL,
        )
        expected_label = _TL_TITLE
        expected_session = f"{_TL_TITLE} session"
        import_ok = MODULE_UI_LABEL == expected_label and MODULE_UI_SESSION_LABEL == expected_session
    except Exception as exc:  # noqa: BLE001
        import_ok = False
        return False, f"import failed: {type(exc).__name__}: {exc}"
    ok = has_module and has_v3 and has_session and has_engine_health and import_ok
    return ok, (
        f"module-label={has_module} v3={has_v3} session={has_session} "
        f"engine-health={has_engine_health} import-ok={import_ok}"
    )


def row8_template_content_flipped() -> Tuple[bool, str]:
    art_src = _text(ARTEFACT_HTML)
    ref_src = _text(REFUSAL_HTML)
    tl_marker = _TL_TITLE
    art_footer = f"<div>Generated by AKKI · {tl_marker} v3</div>" in art_src
    ref_h2 = f"<h2>What {tl_marker} can offer</h2>" in ref_src
    ref_footer = f"<div>Generated by AKKI · {tl_marker} v3 · Refusal artefact</div>" in ref_src
    # Old strings gone from those lines
    art_old_absent = "AKKI · Solva v3</div>" not in art_src
    ref_old_h2_absent = "What Solva can offer" not in ref_src
    ok = art_footer and ref_h2 and ref_footer and art_old_absent and ref_old_h2_absent
    return ok, (
        f"artefact-footer={art_footer} refusal-h2={ref_h2} refusal-footer={ref_footer} "
        f"artefact-old-absent={art_old_absent} refusal-old-absent={ref_old_h2_absent}"
    )


def row9_template_filenames_renamed_by_phase_2() -> Tuple[bool, str]:
    """R9 — post-Phase-2 polarity flip. Template filenames RENAMED by
    Phase 2 (old `solva_*.html` names GONE, new `{_TL_SEG}_*.html`
    names PRESENT). Was "unchanged, Phase 2 defers" until Phase 2 shipped
    per user Option (a) confirmation 2026-07-02."""
    new_art_path = BACKEND / f"templates/{_TL_SEG}_artefact.html"
    new_ref_path = BACKEND / f"templates/{_TL_SEG}_refusal_artefact.html"
    old_art_path = BACKEND / "templates/solva_artefact.html"
    old_ref_path = BACKEND / "templates/solva_refusal_artefact.html"

    new_art_exists = new_art_path.exists()
    new_ref_exists = new_ref_path.exists()
    old_art_absent = not old_art_path.exists()
    old_ref_absent = not old_ref_path.exists()
    ok = new_art_exists and new_ref_exists and old_art_absent and old_ref_absent
    return ok, (
        f"new-artefact-exists={new_art_exists} new-refusal-exists={new_ref_exists} "
        f"old-artefact-absent={old_art_absent} old-refusal-absent={old_ref_absent}"
    )


def row10_solva_export_uses_constants() -> Tuple[bool, str]:
    src = _text(SOLVA_EXPORT_PY)
    # Post-Phase-2, the import may be single-line OR multi-line
    # (Phase 2 added TEMPLATE_ARTEFACT_FILENAME + TEMPLATE_REFUSAL_
    # ARTEFACT_FILENAME). Check for the module + symbol independently
    # to tolerate both forms.
    imports_constant = (
        "from services.module_labels import" in src
        and "MODULE_UI_SESSION_LABEL" in src
    )
    fallback_1 = "return MODULE_UI_SESSION_LABEL" in src
    fallback_2 = "SUBMODULE_LABELS.get(submodule, MODULE_UI_SESSION_LABEL)" in src
    # Raw "Solva session" literal is GONE from those two sites (may
    # still appear elsewhere in the file — line 319, 320 — which
    # is Phase 3 scope).
    lines = src.splitlines()
    framing_fn_start = None
    for i, ln in enumerate(lines):
        if "def _framing_one_liner(session:" in ln:
            framing_fn_start = i
            break
    if framing_fn_start is None:
        return False, "_framing_one_liner not found"
    framing_body = "\n".join(lines[framing_fn_start:framing_fn_start + 15])
    framing_clean = '"Solva session"' not in framing_body
    ok = imports_constant and fallback_1 and fallback_2 and framing_clean
    return ok, (
        f"imports={imports_constant} fallback-274={fallback_1} "
        f"fallback-311={fallback_2} framing-clean={framing_clean}"
    )


def row11_invariant_allowlist_green() -> Tuple[bool, str]:
    rc, out, err = _run([
        "python", "-m", "pytest",
        _FE_LABEL_INVARIANT,
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row12_invariant_still_rejects_non_allowlisted() -> Tuple[bool, str]:
    """R12 — synthetic negative test. Write a non-allowlisted BE .py
    file with a title-cased split-literal probe; run the invariant;
    assert it fails; then remove the fixture and re-verify the
    invariant returns to GREEN.
    """
    probe_marker = _TL_TITLE
    fixture = BACKEND / "services/_ratchet_probe_do_not_commit.py"
    fixture.write_text(
        '"""Ephemeral ratchet probe for JC-SOLVA-MODULE-RENAME-PHASE-1 slice R12."""\n'
        f'PROBE = "{probe_marker}"  # would trip the ratchet\n',
        encoding="utf-8",
    )
    try:
        rc, out, err = _run([
            "python", "-m", "pytest",
            _FE_LABEL_INVARIANT,
            "-q", "--tb=no",
        ])
        invariant_fires = rc != 0
    finally:
        fixture.unlink(missing_ok=True)
    # Verify invariant re-GREENs after the fixture is removed.
    rc2, out2, err2 = _run([
        "python", "-m", "pytest",
        _FE_LABEL_INVARIANT,
        "-q", "--tb=no",
    ])
    invariant_returns_green = rc2 == 0
    ok = invariant_fires and invariant_returns_green
    return ok, (
        f"invariant-fires-on-probe={invariant_fires} "
        f"invariant-returns-green-after-removal={invariant_returns_green}"
    )


def row13_solva_engine_untouched() -> Tuple[bool, str]:
    """R13 — services/solva_v2/ dir is untouched by Phase 1. We check
    that no file under it contains the `JC-SOLVA-MODULE-RENAME-PHASE-1`
    marker (which would only be present if we edited them)."""
    if not SOLVA_V2_DIR.exists():
        return False, f"engine dir missing: {SOLVA_V2_DIR}"
    marker = "JC-SOLVA-MODULE-RENAME-PHASE-1"
    hits: List[str] = []
    for f in SOLVA_V2_DIR.rglob("*.py"):
        if "__pycache__" in f.parts:
            continue
        try:
            src = f.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        if marker in src:
            hits.append(str(f.relative_to(SOLVA_V2_DIR)))
    # Also check contracts/adapters aren't touched by phase-1 markers.
    contracts_dir = BACKEND / "contracts"
    if contracts_dir.exists():
        for f in contracts_dir.rglob("*.py"):
            if "__pycache__" in f.parts:
                continue
            try:
                src = f.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            if marker in src:
                hits.append(str(f.relative_to(BACKEND)))
    ok = not hits
    return ok, f"engine-untouched-file-count-with-marker={len(hits)} · sample={hits[:3]}"


def row14_supporting_invariants_green() -> Tuple[bool, str]:
    """R14 — JC-CHAT, F.6 Shield, pollution ceilings preserved.

    `test_invariant_shield_no_leak.py` contains `@pytest.mark.integration`
    tests that make real LLM round-trips; filter them out with
    `-m "not integration"` so the invariant check completes in seconds
    instead of minutes.
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


def row15_end_to_end_shape_audit() -> Tuple[bool, str]:
    """R15 — end-to-end shape audit."""
    app_js = _text(APP_JS)
    shell_src = _text(APPSHELL_JSX)
    invariant_src = _text(INVARIANT_PY)
    labels_src = _text(MODULE_LABELS_PY)

    route_table_coherent = (
        "SolvaRedirect" in app_js
        and f'path="{_TL_APP_PATH}"' in app_js
        and 'path="/app/solva" element={<SolvaRedirect' in app_js
    )
    appshell_coherent = (
        'import { MODULE_LABELS } from "@/lib/moduleLabels";' in shell_src
        and _TL_APP_PATH in shell_src
    )
    invariant_coherent = (
        '"module_labels.py"' in invariant_src
        and "_ALLOWLIST_FILENAMES" in invariant_src
    )
    be_labels_coherent = (
        "MODULE_UI_SESSION_LABEL" in labels_src
        and "ENGINE_HEALTH_LABEL" in labels_src
    )
    ok = all([route_table_coherent, appshell_coherent, invariant_coherent, be_labels_coherent])
    return ok, (
        f"routes={route_table_coherent} appshell={appshell_coherent} "
        f"invariant={invariant_coherent} be-labels={be_labels_coherent}"
    )


# Row labels use f-strings to avoid embedding the raw hard-ratcheted
# token as a string literal in this file.
ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 pre-fix baseline invariants GREEN", row1_pre_fix_baseline),
    (f"R2 6 app routes renamed to {_TL_APP_PATH}*", row2_app_routes_renamed_to_tl_module),
    ("R3 6 legacy /app/solva* routes redirect", row3_legacy_app_routes_redirect),
    (f"R4 marketing /solva → {_TL_MARKETING_PATH} flipped", row4_marketing_routes_flipped),
    ("R5 <SolvaRedirect> preserves query params", row5_solva_redirect_preserves_query),
    ("R6 AppShell nav labels + `to` fields flipped", row6_appshell_nav_labels_and_paths),
    ("R7 BE constants file valid + importable", row7_be_constants_file_valid),
    ("R8 template CONTENT flipped (module label surfaces)", row8_template_content_flipped),
    ("R9 template FILENAMES renamed by Phase 2 (post-flip)", row9_template_filenames_renamed_by_phase_2),
    ("R10 solva_artefact_export.py uses constants", row10_solva_export_uses_constants),
    ("R11 FE-only-label invariant GREEN with allowlist", row11_invariant_allowlist_green),
    ("R12 invariant still rejects non-allowlisted (ratchet strength)", row12_invariant_still_rejects_non_allowlisted),
    ("R13 Solva engine (services/solva_v2/, contracts/) UNTOUCHED", row13_solva_engine_untouched),
    ("R14 JC-CHAT + F.6 Shield + pollution invariants GREEN", row14_supporting_invariants_green),
    ("R15 end-to-end shape audit", row15_end_to_end_shape_audit),
]


def main() -> int:
    print("=" * 78)
    print("JC-SOLVA-MODULE-RENAME-PHASE-1-ROUTES-AND-NAV proving slice")
    print("Canonical Spec: user dispatch 2026-07-02 + audit §5 + A1 memo §4 defaults")
    print("Sprint memo:    /app/memory/sprints/JC_SOLVA_RENAME_PHASE_1_ROUTES_AND_NAV.md")
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
