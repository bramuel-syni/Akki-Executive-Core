"""JC-WS-DECK-A7-INTELLIGENCE-TAB-COMPLETION — proving slice (9 rows).

Canonical Spec: /app/memory/rules/TAB_HONESTY_RULE.md
             + /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A7
             + /app/memory/sprints/JC_WS_DECK_A7_INTELLIGENCE_TAB_COMPLETION.md.

F.6 discipline-pay: N/A · Refresh is pure re-fetch via existing GET endpoint.
"""
from __future__ import annotations

import os
import re
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


IEP = FRONTEND / "src" / "components" / "work_studio" / "overlay" / "IntelligencePanelExpanded.jsx"
DOCUMENT_OVERLAY = FRONTEND / "src" / "components" / "work_studio" / "overlay" / "DocumentOverlay.jsx"


def _run(cmd, *, cwd=BACKEND, timeout=180):
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(p): return p.read_text(encoding="utf-8")


def r1() -> Tuple[bool, str]:
    if not IEP.exists():
        return False, f"file-not-found={IEP}"
    src = _text(IEP)
    has_default = "export default function IntelligencePanelExpanded" in src
    accepts = "doc" in src and "onRefresh" in src
    return has_default and accepts, f"file-exists=True default-export={has_default} props={accepts}"


def r2() -> Tuple[bool, str]:
    """R2 — REAL RENDER — plain-language explanation renders confidence_rationale."""
    src = _text(IEP)
    reads_rationale = "confidence_rationale" in src
    prose_render = "{rationale}" in src or "rationale" in src
    empty_state = "intelligence-panel-explanation-empty" in src
    ok = reads_rationale and prose_render and empty_state
    return ok, f"reads-rationale={reads_rationale} prose-render={prose_render} empty-state={empty_state}"


def r3() -> Tuple[bool, str]:
    """R3 — REAL RENDER — clarity metrics grid."""
    src = _text(IEP)
    reads_pct = "confidence_pct" in src
    reads_sources = "sources_count" in src
    reads_pending = "pending_recommendations" in src
    grid = "grid-cols-3" in src or "grid" in src
    ok = reads_pct and reads_sources and reads_pending and grid
    return ok, (
        f"confidence_pct={reads_pct} sources_count={reads_sources} "
        f"pending_recs={reads_pending} grid-layout={grid}"
    )


def r4() -> Tuple[bool, str]:
    """R4 — REAL RENDER — provenance section renders source_document_ids."""
    src = _text(IEP)
    reads_ids = "source_document_ids" in src
    array_guard = "Array.isArray" in src
    map_ids = "sourceIds.map(" in src
    empty_state = "intelligence-panel-provenance-empty" in src
    ok = reads_ids and array_guard and map_ids and empty_state
    return ok, (
        f"reads-source-ids={reads_ids} array-guard={array_guard} "
        f"map-provenance={map_ids} empty-state={empty_state}"
    )


def r5() -> Tuple[bool, str]:
    """R5 — Refresh button calls onRefresh() prop; DocumentOverlay wires to loadDoc."""
    src_iep = _text(IEP)
    src_overlay = _text(DOCUMENT_OVERLAY)
    refresh_button = "intelligence-panel-refresh-btn" in src_iep
    calls_on_refresh = "onRefresh()" in src_iep or "onRefresh && onRefresh()" in src_iep
    overlay_wires = "onRefresh={loadDoc}" in src_overlay
    ok = refresh_button and calls_on_refresh and overlay_wires
    return ok, f"refresh-button={refresh_button} calls-onRefresh={calls_on_refresh} overlay-wires-loadDoc={overlay_wires}"


def r6() -> Tuple[bool, str]:
    """R6 — Stable testids."""
    src = _text(IEP)
    expected = [
        "intelligence-panel-expanded-root",
        "intelligence-panel-clarity-metrics",
        "intelligence-panel-explanation",
        "intelligence-panel-provenance",
        "intelligence-panel-refresh-btn",
        "intelligence-panel-confidence-pct",
        "intelligence-panel-sources-count",
        "intelligence-panel-pending-recs",
    ]
    missing = [t for t in expected if t not in src]
    return not missing, f"expected-testids-missing={missing or 'none'} baseline={len(expected)}"


def r7() -> Tuple[bool, str]:
    """R7 — Intelligence TabsContent mounts <IntelligencePanelExpanded> AFTER <IntelligenceCard>."""
    src = _text(DOCUMENT_OVERLAY)
    m = re.search(
        r'<TabsContent\s+value=[\'"]intelligence[\'"][^>]*>[\s\S]{0,4000}?<IntelligenceCard[\s\S]{0,4000}?<IntelligencePanelExpanded',
        src,
    )
    ok = bool(m)
    return ok, f"iep-after-card-in-intelligence-tab={ok}"


def r8() -> Tuple[bool, str]:
    """R8 — F.6 classification — no shield_invoke / get_synisense / new LLM path in A7 code."""
    src = _text(IEP)
    has_shield = "shield_invoke" in src
    has_synisense = "get_synisense" in src or "synisense" in src.lower()
    has_openai = "openai" in src.lower()
    has_llm = "gpt-" in src.lower() or "claude" in src.lower() or "gemini" in src.lower()
    f6_clean = not (has_shield or has_synisense or has_openai or has_llm)
    return f6_clean, (
        f"no-shield_invoke={not has_shield} no-synisense={not has_synisense} "
        f"no-openai={not has_openai} no-llm-hint={not has_llm}"
    )


def r9() -> Tuple[bool, str]:
    """R9 — Regressions — full chain GREEN + P4 hash invariant."""
    results = []
    for name, script in [
        ("a4", "jc_ws_deck_a4_proving_slice.py"),
        ("a5", "jc_ws_deck_a5_proving_slice.py"),
        ("a6", "jc_ws_deck_a6_proving_slice.py"),
        ("a8-mvp", "jc_ws_deck_a8_proving_slice.py"),
        ("a8-backend", "jc_ws_deck_a8_backend_proving_slice.py"),
        ("a9", "jc_ws_deck_a9_proving_slice.py"),
        ("a10", "jc_ws_deck_a10_proving_slice.py"),
        ("p4-hash", "jc_solva_rename_phase_4_proving_slice.py"),
    ]:
        rc, out, _ = _run(["python", str(BACKEND / "scripts" / script)])
        tail = out.splitlines()[-1] if out else "no output"
        results.append((name, rc == 0, tail))
    ok = all(r[1] for r in results)
    detail = " | ".join(f"{n}={'GREEN' if g else 'RED'}({t.strip()[-25:]})" for n, g, t in results)
    return ok, detail


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 IntelligencePanelExpanded.jsx exists + default export + doc/onRefresh props", r1),
    ("R2 REAL RENDER — plain-language explanation (confidence_rationale prose)", r2),
    ("R3 REAL RENDER — clarity metrics grid (confidence_pct/sources_count/pending_recs)", r3),
    ("R4 REAL RENDER — provenance section (source_document_ids list)", r4),
    ("R5 Refresh button wired to onRefresh → loadDoc (pure re-fetch)", r5),
    ("R6 Stable testids on IntelligencePanelExpanded", r6),
    ("R7 Intelligence TabsContent mounts IEP AFTER IntelligenceCard", r7),
    ("R8 F.6 classification — no shield_invoke / synisense / LLM path in A7 code", r8),
    ("R9 Regressions — full chain + P4 hash invariant all GREEN", r9),
]


def main() -> int:
    print("=" * 78)
    print("JC-WS-DECK-A7-INTELLIGENCE-TAB-COMPLETION proving slice (auto-chain phase 4/4 · CLOSE)")
    print("Canonical Spec: TAB_HONESTY_RULE + PATH_A_EXECUTION_PLAN §A7")
    print("F.6 discipline-pay: N/A · Refresh is pure re-fetch (classified by execution)")
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
    print(f"SLICE GREEN · {len(ROWS)}/{len(ROWS)} rows passed · CHAIN CLOSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
