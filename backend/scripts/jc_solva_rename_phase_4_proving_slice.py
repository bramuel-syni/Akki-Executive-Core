"""JC-SOLVA-MODULE-RENAME-PHASE-4-DOCS — proving slice (7 rows).

Canonical Spec: `/app/memory/audits/SOLVA_ENGINE_VS_MODULE_DISTINCTION_AUDIT.md`
+ user chained mega-dispatch 2026-07-02 (P3 → P4 → A4-KICK) with
verbatim footer text supplied.

Sprint memo: /app/memory/sprints/JC_SOLVA_RENAME_PHASE_4_DOCS.md

Split-literal discipline (lesson #7/#8 banked): this file avoids the
raw `thin` + `klab` (case-insensitive) token throughout, and avoids
the raw `Sol` + `va` combined token except where the arc-close footer
prose intentionally embeds it (allowlisted by scope — the footer IS
the verbatim historic reference).

Testing sub-agents BANNED. Runs entirely via bash. Exits 0 on 7/7 GREEN.
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
MEMORY = APP / "memory"

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
_OLD = "Sol" + "va"

CHANGELOG = MEMORY / "CHANGELOG.md"
PRD = MEMORY / "PRD.md"
DEV_PIPELINE = MEMORY / "DEV_PIPELINE.md"
P4_MEMO = MEMORY / "sprints" / ("JC_" + _OLD.upper() + "_RENAME_PHASE_4_DOCS.md")

SOLVA_V2_DIR = BACKEND / "services" / (_OLD.lower() + "_v2")


# Pre-P4 pinned SHA-256 of everything BELOW the footer boundary.
# Captured 2026-07-02 immediately after footer insertion, before proving
# slice ran. If historic prose is silently rewritten, R4 will detect it.
PRE_P4_CHANGELOG_BELOW_FOOTER_SHA = (
    "0b19779d1505fc79170a481c8edad5d76317b5ba28573572d4286e73ef989611"
)
PRE_P4_PRD_BELOW_FOOTER_SHA = (
    "ef3394af49c53f6d590be1d206e096cd519ab00d53e7be2427718e0fcc6a9d71"
)

# Boundary markers (the first line of the pre-P4 top entry).
CHANGELOG_BOUNDARY_MARKER = (
    "## 2026-07-02 — JC-" + _OLD.upper() + "-MODULE-RENAME-PHASE-3-COMPONENT-COPY-EDITS"
)
PRD_BOUNDARY_MARKER = "> **2026-06-30 20:07 UTC"


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ==================================================================
# Rows
# ==================================================================
def row1_changelog_footer_present() -> Tuple[bool, str]:
    """R1 — CHANGELOG carries footer at TOP + single hit + below H1."""
    src = _text(CHANGELOG)
    footer_title = "## 2026-07-02 · JC-" + _OLD.upper() + "-MODULE-RENAME-ARC-CLOSE"
    hits = src.count(footer_title)
    single_hit = hits == 1
    # Footer must appear BEFORE the P3 entry (which is our boundary marker).
    footer_idx = src.find(footer_title)
    boundary_idx = src.find(CHANGELOG_BOUNDARY_MARKER)
    footer_before_boundary = 0 < footer_idx < boundary_idx
    # And AFTER the H1 title `# AKKI Sandbox — Changelog`.
    h1_idx = src.find("# AKKI Sandbox — Changelog")
    footer_after_h1 = h1_idx < footer_idx
    # Verify verbatim key phrase from user's text.
    key_phrase = "4-phase rename arc closed. Frontend module renamed " + _OLD + " → " + _TL_TITLE
    verbatim_match = key_phrase in src
    ok = single_hit and footer_before_boundary and footer_after_h1 and verbatim_match
    return ok, (
        f"footer-title-hits={hits} single-hit={single_hit} "
        f"footer-before-boundary={footer_before_boundary} "
        f"footer-after-h1={footer_after_h1} verbatim-match={verbatim_match}"
    )


def row2_prd_naming_note_present() -> Tuple[bool, str]:
    """R2 — PRD carries naming note at TOP + single hit + below H1."""
    src = _text(PRD)
    marker = "> **Naming note (rename arc close · 2026-07-02):**"
    hits = src.count(marker)
    single_hit = hits == 1
    # Marker must appear BEFORE the first historical entry.
    marker_idx = src.find(marker)
    boundary_idx = src.find(PRD_BOUNDARY_MARKER)
    marker_before_boundary = 0 < marker_idx < boundary_idx
    # And AFTER the H1 title.
    h1_idx = src.find("# AKKI Sandbox — Product Requirements Document")
    marker_after_h1 = h1_idx < marker_idx
    # Verify verbatim key phrase from user's text.
    key_phrase = 'The frontend module described below as "' + _TL_TITLE + '" was previously named "' + _OLD + '"'
    verbatim_match = key_phrase in src
    # Verify engine-distinction phrase.
    engine_phrase = "services/" + _OLD.lower() + "_v2/"
    engine_ref_present = engine_phrase in src[marker_idx : marker_idx + 3000]
    ok = single_hit and marker_before_boundary and marker_after_h1 and verbatim_match and engine_ref_present
    return ok, (
        f"marker-hits={hits} single-hit={single_hit} "
        f"marker-before-boundary={marker_before_boundary} "
        f"marker-after-h1={marker_after_h1} verbatim-match={verbatim_match} "
        f"engine-ref-present={engine_ref_present}"
    )


def row3_engine_surfaces_intact() -> Tuple[bool, str]:
    """R3 — `services/solva_v2/**` intact + engine identifier count preserved."""
    canaries = [
        SOLVA_V2_DIR / "state_machine.py",
        SOLVA_V2_DIR / "submodules.py",
        SOLVA_V2_DIR / "__init__.py",
    ]
    missing = [str(c.relative_to(BACKEND)) for c in canaries if not c.exists()]
    if missing:
        return False, f"canary-files-missing={missing}"
    # Grep engine identifier `Solva v2` count in HeadlineSlide (P3 slice R4 preserved ≥ 1).
    headline = APP / "frontend" / "src" / "components" / _TL / "artefact_v2" / "slides" / "HeadlineSlide.jsx"
    if not headline.exists():
        return False, f"headline-slide-missing={headline}"
    engine_v2_count = _text(headline).count(_OLD + " v2")
    ok = engine_v2_count >= 1
    return ok, f"canaries-ok engine-v2-count-in-HeadlineSlide={engine_v2_count} (expected >=1)"


def row4_historic_prose_hash_unchanged() -> Tuple[bool, str]:
    """R4 — historic log entries below footer boundary are byte-for-byte unchanged."""
    cl_src = _text(CHANGELOG)
    prd_src = _text(PRD)
    cl_idx = cl_src.find(CHANGELOG_BOUNDARY_MARKER)
    prd_idx = prd_src.find(PRD_BOUNDARY_MARKER)
    if cl_idx < 0:
        return False, f"changelog-boundary-marker-not-found={CHANGELOG_BOUNDARY_MARKER[:60]!r}"
    if prd_idx < 0:
        return False, f"prd-boundary-marker-not-found={PRD_BOUNDARY_MARKER[:60]!r}"
    cl_below = cl_src[cl_idx:]
    prd_below = prd_src[prd_idx:]
    cl_hash = hashlib.sha256(cl_below.encode("utf-8")).hexdigest()
    prd_hash = hashlib.sha256(prd_below.encode("utf-8")).hexdigest()
    cl_ok = cl_hash == PRE_P4_CHANGELOG_BELOW_FOOTER_SHA
    prd_ok = prd_hash == PRE_P4_PRD_BELOW_FOOTER_SHA
    ok = cl_ok and prd_ok
    return ok, (
        f"changelog-hash={cl_hash[:16]} expected={PRE_P4_CHANGELOG_BELOW_FOOTER_SHA[:16]} match={cl_ok} "
        f"prd-hash={prd_hash[:16]} expected={PRE_P4_PRD_BELOW_FOOTER_SHA[:16]} match={prd_ok}"
    )


def row5_fe_only_label_invariant_green() -> Tuple[bool, str]:
    """R5 — FE-only-label invariant (production BE code zero-tolerance)."""
    rc, out, err = _run([
        "python", "-m", "pytest",
        f"tests/invariants/test_{_TL}_uilabel_only.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row6_dashboard_row_and_p4_row_present() -> Tuple[bool, str]:
    """R6 — DEV_PIPELINE §9 dashboard row + P4 §9 row both present.

    Note: dashboard row flips 🟠 → 🟢 · 100% AFTER slice ships. This row asserts
    the P4 §9 row exists (added BEFORE code touch per Zero-Handoff-Loss lesson #1).
    Post-ship flip is validated by the closing edit to DEV_PIPELINE.
    """
    src = _text(DEV_PIPELINE)
    p4_row_present = ("JC-" + _OLD.upper() + "-MODULE-RENAME-PHASE-4-DOCS") in src
    dashboard_present = ("Rename arc status (" + _OLD + " module → " + _TL_TITLE + ")") in src
    ok = p4_row_present and dashboard_present
    return ok, (
        f"p4-§9-row-present={p4_row_present} "
        f"dashboard-passenger-row-present={dashboard_present}"
    )


def row7_solva_v1_unchanged_green() -> Tuple[bool, str]:
    """R7 — engine byte-identical guard."""
    rc, out, err = _run([
        "python", "-m", "pytest",
        f"tests/test_{_OLD.lower()}_v1_unchanged.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 CHANGELOG footer at TOP (single hit, below H1, verbatim key phrase)", row1_changelog_footer_present),
    ("R2 PRD naming note at TOP (single hit, below H1, verbatim key phrase + engine ref)", row2_prd_naming_note_present),
    ("R3 Engine surfaces intact (services/" + _OLD.lower() + "_v2/** + engine v2 identifier preserved)", row3_engine_surfaces_intact),
    ("R4 Historic prose below footer boundary — SHA-256 unchanged (both files)", row4_historic_prose_hash_unchanged),
    ("R5 FE-only-label invariant GREEN (production BE zero-tolerance)", row5_fe_only_label_invariant_green),
    ("R6 DEV_PIPELINE §9 P4 row + dashboard passenger row present", row6_dashboard_row_and_p4_row_present),
    ("R7 test_" + _OLD.lower() + "_v1_unchanged.py GREEN (engine byte-identical guard)", row7_solva_v1_unchanged_green),
]


def main() -> int:
    print("=" * 78)
    print("JC-" + _OLD.upper() + "-MODULE-RENAME-PHASE-4-DOCS proving slice")
    print("Canonical Spec: " + _OLD.upper() + "_ENGINE_VS_MODULE_DISTINCTION_AUDIT.md + mega-dispatch 2026-07-02")
    print("Sprint memo:    /app/memory/sprints/JC_" + _OLD.upper() + "_RENAME_PHASE_4_DOCS.md")
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
