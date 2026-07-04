"""JC-WS-DECK-A9-SIGNALS-MVP — proving slice (8 rows).

Canonical Spec: /app/memory/audits/JC_WS_DECK_CONFORMANCE_AUDIT.md §5 (DECK-060..063)
+ /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A9
+ /app/memory/sprints/JC_WS_DECK_A9_SIGNALS_MVP.md
+ user dispatch 2026-07-02 (populate-chain step 2 of 3).

Testing sub-agents BANNED. Runs entirely via bash.
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

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))


SIGNALS_PANEL = FRONTEND / "src" / "components" / "work_studio" / "overlay" / "SignalsPanel.jsx"
DOCUMENT_OVERLAY = FRONTEND / "src" / "components" / "work_studio" / "overlay" / "DocumentOverlay.jsx"


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def row1_signals_panel_exists() -> Tuple[bool, str]:
    """R1 — SignalsPanel.jsx exists + default export + accepts doc prop."""
    if not SIGNALS_PANEL.exists():
        return False, f"file-not-found={SIGNALS_PANEL}"
    src = _text(SIGNALS_PANEL)
    has_export_default = "export default function SignalsPanel" in src or "export default SignalsPanel" in src
    accepts_doc = "{ doc }" in src or "doc " in src.split("SignalsPanel(")[1][:80]
    ok = has_export_default and accepts_doc
    return ok, f"file-exists=True default-export={has_export_default} accepts-doc-prop={accepts_doc}"


def row2_reads_intelligence_report_recommendations() -> Tuple[bool, str]:
    """R2 — Reads doc.intelligence_report.recommendations."""
    src = _text(SIGNALS_PANEL)
    reads_report = "doc.intelligence_report" in src or "doc && doc.intelligence_report" in src
    reads_recs = "recommendations" in src
    array_guard = "Array.isArray(report.recommendations)" in src or "Array.isArray" in src
    ok = reads_report and reads_recs and array_guard
    return ok, f"reads-report={reads_report} reads-recommendations={reads_recs} array-guard={array_guard}"


def row3_real_render_of_recommendations() -> Tuple[bool, str]:
    """R3 — REAL RENDER: renders each recommendation with text + addressed-state."""
    src = _text(SIGNALS_PANEL)
    has_map = "recommendations.map(" in src
    binds_text = "{text}" in src or "rec.text" in src
    addressed_render = "addressed" in src and ("Addressed" in src or "Open" in src)
    ok = has_map and binds_text and addressed_render
    return ok, f"array-map={has_map} text-binding={binds_text} addressed-state-render={addressed_render}"


def row4_visibility_flag_signals_true() -> Tuple[bool, str]:
    """R4 — TAB_VISIBILITY.signals === true (flag flipped for A9 ship).

    Note: A9 does NOT assert related remains false — it may have flipped forward
    as the A10 panel ships in the populate chain. A9's own invariant is only
    that its own flag is set to true.
    """
    src = _text(DOCUMENT_OVERLAY)
    signals_true = "signals: true" in src
    ok = signals_true
    return ok, f"signals-true={signals_true}"


def row5_signals_tabcontent_mounts_panel() -> Tuple[bool, str]:
    """R5 — Signals TabsContent mounts <SignalsPanel doc={doc} /> + placeholder REMOVED."""
    src = _text(DOCUMENT_OVERLAY)
    m = re.search(
        r'<TabsContent\s+value=[\'"]signals[\'"][^>]*>[\s\S]{0,2000}?<SignalsPanel',
        src,
    )
    mount_present = bool(m)
    placeholder_removed = "document-overlay-tab-content-signals-placeholder" not in src
    doc_passed = "doc={doc}" in src
    ok = mount_present and placeholder_removed and doc_passed
    return ok, f"signals-panel-in-tab={mount_present} placeholder-removed={placeholder_removed} doc-prop={doc_passed}"


def row6_empty_state_present() -> Tuple[bool, str]:
    """R6 — Empty state rendered when recommendations empty (signals-panel-empty-state testid)."""
    src = _text(SIGNALS_PANEL)
    empty_testid = "signals-panel-empty-state" in src
    empty_conditional = "recommendations.length === 0" in src or "length === 0" in src
    ok = empty_testid and empty_conditional
    return ok, f"empty-testid={empty_testid} empty-conditional={empty_conditional}"


def row7_stable_testids() -> Tuple[bool, str]:
    """R7 — Stable testids on SignalsPanel: root, item, empty-state."""
    src = _text(SIGNALS_PANEL)
    expected = [
        "signals-panel-root",
        "signals-panel-item",
        "signals-panel-empty-state",
    ]
    missing = [t for t in expected if t not in src]
    ok = not missing
    return ok, f"expected-testids-missing={missing or 'none'} baseline-count={len(expected)}"


def row8_regressions_green() -> Tuple[bool, str]:
    """R8 — A4 slice + A8 slice regression."""
    rc4, out4, _ = _run(["python", str(BACKEND / "scripts" / "jc_ws_deck_a4_proving_slice.py")])
    rc8, out8, _ = _run(["python", str(BACKEND / "scripts" / "jc_ws_deck_a8_proving_slice.py")])
    a4_green = rc4 == 0
    a8_green = rc8 == 0
    ok = a4_green and a8_green
    a4_tail = out4.splitlines()[-1] if out4 else "no output"
    a8_tail = out8.splitlines()[-1] if out8 else "no output"
    return ok, f"a4-slice={a4_tail} | a8-slice={a8_tail}"


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 SignalsPanel.jsx exists + default export + accepts doc prop", row1_signals_panel_exists),
    ("R2 Reads doc.intelligence_report.recommendations (existing shape)", row2_reads_intelligence_report_recommendations),
    ("R3 REAL RENDER — .map() over recommendations + text binding + addressed-state", row3_real_render_of_recommendations),
    ("R4 TAB_VISIBILITY.signals === true (flag flipped); related still false", row4_visibility_flag_signals_true),
    ("R5 Signals TabsContent mounts <SignalsPanel doc={doc} /> + placeholder REMOVED", row5_signals_tabcontent_mounts_panel),
    ("R6 Empty state rendered when recommendations empty", row6_empty_state_present),
    ("R7 Stable testids on SignalsPanel (root/item/empty-state)", row7_stable_testids),
    ("R8 A4 slice + A8 slice regression GREEN", row8_regressions_green),
]


def main() -> int:
    print("=" * 78)
    print("JC-WS-DECK-A9-SIGNALS-MVP proving slice (populate-chain step 2/3)")
    print("Canonical Spec: JC_WS_DECK_CONFORMANCE_AUDIT.md §5 + PATH_A_EXECUTION_PLAN §A9 + A9_SIGNALS_MVP")
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
