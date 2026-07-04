"""JC-WS-DECK-A4-FIVE-TAB-OVERLAY — proving slice (10 rows).

Canonical Spec: `/app/memory/audits/JC_WS_DECK_CONFORMANCE_AUDIT.md §5`
+ `/app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md`
+ `/app/memory/sprints/JC_WS_DECK_A4_ADVANCE_SCAN.md`
+ user chained mega-dispatch 2026-07-02 (P4 → A4-KICK).

Sprint memo: /app/memory/sprints/JC_WS_DECK_A4_FIVE_TAB_OVERLAY.md

STATE: SCAFFOLDED — NOT executed until A4 build ships. Rows defined
against pre-build state, so slice runs RED at scaffold time. Ok:
scaffold's purpose is to lock the acceptance shape.

Testing sub-agents BANNED. Runs entirely via bash. Exits 0 on 10/10 GREEN.
Split-literal discipline (lesson #7/#8): raw `thin` + `klab` avoided
throughout — this slice targets Work Studio surfaces, not ThinkLab.
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


DOCUMENT_OVERLAY = (
    FRONTEND / "src" / "components" / "work_studio" / "overlay" / "DocumentOverlay.jsx"
)
UI_TABS = FRONTEND / "src" / "components" / "ui" / "tabs.jsx"


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# Pre-A4 baseline of testids in DocumentOverlay for R10 regression check.
# Captured 2026-07-02 pre-A4 (must survive the tab-shell re-parenting).
# These testids are already present today; A4 MUST preserve them.
PRE_A4_PRESERVED_TESTIDS = [
    "document-overlay-intelligence-section-",   # existing per-section chip
]


# ==================================================================
# Rows
# ==================================================================
def row1_tabs_primitive_imported_and_mounted() -> Tuple[bool, str]:
    """R1 — `<Tabs>` primitive imported from `@/components/ui/tabs` + mounted in DocumentOverlay body."""
    src = _text(DOCUMENT_OVERLAY)
    imported = ("from \"@/components/ui/tabs\"" in src) or ("from '@/components/ui/tabs'" in src)
    mounted = "<Tabs" in src or "<TabsList" in src
    ok = imported and mounted
    return ok, f"imported={imported} mounted={mounted}"


def row2_five_tab_triggers_rendered() -> Tuple[bool, str]:
    """R2 — 5 tab-triggers rendered with expected data-testids."""
    src = _text(DOCUMENT_OVERLAY)
    expected_testids = [
        "document-overlay-tab-document",
        "document-overlay-tab-intelligence",
        "document-overlay-tab-notes",
        "document-overlay-tab-signals",
        "document-overlay-tab-related",
    ]
    missing = [t for t in expected_testids if t not in src]
    ok = not missing
    return ok, f"expected-testids-missing={missing or 'none'}"


def row3_document_tab_default_landing() -> Tuple[bool, str]:
    """R3 — Default active tab is `document`; DocumentSurface renders inside Document tab shell."""
    src = _text(DOCUMENT_OVERLAY)
    default_value = 'defaultValue="document"' in src or "defaultValue={'document'}" in src or 'defaultValue={"document"}' in src
    surface_in_document_tab = False
    # Match: <TabsContent value="document"> ... <DocumentSurface ... />
    m = re.search(
        r'<TabsContent\s+value=[\'"]document[\'"][^>]*>[\s\S]{0,5000}?<DocumentSurface',
        src,
    )
    if m:
        surface_in_document_tab = True
    ok = default_value and surface_in_document_tab
    return ok, f"default-value=document={default_value} DocumentSurface-inside-document-tab={surface_in_document_tab}"


def row4_intelligence_tab_hosts_intelligence_card() -> Tuple[bool, str]:
    """R4 — Intelligence tab renders IntelligenceCard inline (re-parented)."""
    src = _text(DOCUMENT_OVERLAY)
    m = re.search(
        r'<TabsContent\s+value=[\'"]intelligence[\'"][^>]*>[\s\S]{0,5000}?<IntelligenceCard',
        src,
    )
    ok = bool(m)
    return ok, f"IntelligenceCard-inside-intelligence-tab={ok}"


def row5_placeholder_shells_for_notes_signals_related() -> Tuple[bool, str]:
    """R5 — Notes / Signals / Related tabs render "Coming soon" placeholder shells."""
    src = _text(DOCUMENT_OVERLAY)
    expected_placeholders = [
        "document-overlay-tab-content-notes-placeholder",
        "document-overlay-tab-content-signals-placeholder",
        "document-overlay-tab-content-related-placeholder",
    ]
    missing = [t for t in expected_placeholders if t not in src]
    ok = not missing
    return ok, f"placeholder-testids-missing={missing or 'none'}"


def row6_url_param_tab_sync() -> Tuple[bool, str]:
    """R6 — URL param `?tab=<name>` pre-selects a tab on overlay open.

    Look for any of: useSearchParams / URLSearchParams / window.location.search hooks
    coupled with a state initializer keyed on the `tab` param.
    """
    src = _text(DOCUMENT_OVERLAY)
    url_param_hook = (
        "useSearchParams" in src
        or "URLSearchParams" in src
        or "window.location.search" in src
    )
    tab_param_read = '"tab"' in src or "'tab'" in src or "get('tab')" in src or 'get("tab")' in src
    ok = url_param_hook and tab_param_read
    return ok, f"url-param-hook={url_param_hook} tab-param-read={tab_param_read}"


def row7_toolbar_outside_tabs() -> Tuple[bool, str]:
    """R7 — Toolbar (Layer 1) stays OUTSIDE the Tabs primitive."""
    src = _text(DOCUMENT_OVERLAY)
    # Find first <Toolbar> and first <Tabs> — Toolbar's opening tag must come BEFORE <Tabs> opening.
    tb_idx = src.find("<Toolbar")
    tabs_idx = src.find("<Tabs")
    if tb_idx < 0 or tabs_idx < 0:
        return False, f"toolbar-idx={tb_idx} tabs-idx={tabs_idx} (both required)"
    toolbar_before_tabs = tb_idx < tabs_idx
    ok = toolbar_before_tabs
    return ok, f"toolbar-idx={tb_idx} tabs-idx={tabs_idx} toolbar-before-tabs={toolbar_before_tabs}"


def row8_ai_revision_panel_still_sidebar() -> Tuple[bool, str]:
    """R8 — AIRevisionPanel still opens as sidebar (not migrated into a tab)."""
    src = _text(DOCUMENT_OVERLAY)
    # AIRevisionPanel must NOT be inside a <TabsContent> block.
    # Approximation: find <AIRevisionPanel and assert its most-recent-opening ancestor is NOT a TabsContent.
    for m in re.finditer(r'<AIRevisionPanel\b', src):
        pos = m.start()
        # Scan backwards for nearest <TabsContent or nearest close of any TabsContent.
        prefix = src[:pos]
        last_tc_open = prefix.rfind("<TabsContent")
        last_tc_close = prefix.rfind("</TabsContent>")
        if last_tc_open > last_tc_close:
            return False, f"AIRevisionPanel inside TabsContent at pos={pos} (violates sidebar preservation)"
    ok = "<AIRevisionPanel" in src
    return ok, f"AIRevisionPanel-present={ok} not-inside-any-TabsContent=True"


def row9_modals_stay_overlay_level() -> Tuple[bool, str]:
    """R9 — Modals (IntelligenceModal / VersionHistoryModal / CommitConfirmationModal) mount at overlay level."""
    src = _text(DOCUMENT_OVERLAY)
    modals = ["IntelligenceModal", "VersionHistoryModal", "CommitConfirmationModal"]
    inside_tabs = []
    for name in modals:
        for m in re.finditer(rf"<{name}\b", src):
            pos = m.start()
            prefix = src[:pos]
            last_tc_open = prefix.rfind("<TabsContent")
            last_tc_close = prefix.rfind("</TabsContent>")
            if last_tc_open > last_tc_close:
                inside_tabs.append(f"{name}@{pos}")
    ok = not inside_tabs and all(f"<{n}" in src for n in modals)
    return ok, f"modals-inside-tabs={inside_tabs or 'none'} all-present={all(f'<{n}' in src for n in modals)}"


def row10_testid_preservation() -> Tuple[bool, str]:
    """R10 — Every pre-A4 `document-overlay-*` testid still present in the source (regression check)."""
    src = _text(DOCUMENT_OVERLAY)
    missing = [t for t in PRE_A4_PRESERVED_TESTIDS if t not in src]
    ok = not missing
    return ok, f"preserved-testids-missing={missing or 'none'} baseline-count={len(PRE_A4_PRESERVED_TESTIDS)}"


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 <Tabs> primitive imported from @/components/ui/tabs + mounted", row1_tabs_primitive_imported_and_mounted),
    ("R2 5 tab-triggers with expected data-testids (document/intelligence/notes/signals/related)", row2_five_tab_triggers_rendered),
    ("R3 Document tab is default landing + DocumentSurface inside Document TabsContent", row3_document_tab_default_landing),
    ("R4 Intelligence tab hosts IntelligenceCard inline (re-parented)", row4_intelligence_tab_hosts_intelligence_card),
    ("R5 Notes / Signals / Related tabs render Coming-soon placeholder shells", row5_placeholder_shells_for_notes_signals_related),
    ("R6 URL param ?tab=<name> pre-selects tab (useSearchParams / URLSearchParams hook + tab-param read)", row6_url_param_tab_sync),
    ("R7 Toolbar stays outside <Tabs> (chrome pattern preservation)", row7_toolbar_outside_tabs),
    ("R8 AIRevisionPanel still sidebar (not tab-migrated)", row8_ai_revision_panel_still_sidebar),
    ("R9 Modals (IntelligenceModal / VersionHistoryModal / CommitConfirmationModal) stay overlay-level", row9_modals_stay_overlay_level),
    ("R10 Data-testid preservation regression check", row10_testid_preservation),
]


def main() -> int:
    print("=" * 78)
    print("JC-WS-DECK-A4-FIVE-TAB-OVERLAY proving slice (SCAFFOLDED)")
    print("Canonical Spec: JC_WS_DECK_CONFORMANCE_AUDIT.md §5 + PATH_A_EXECUTION_PLAN + A4_ADVANCE_SCAN")
    print("Sprint memo:    /app/memory/sprints/JC_WS_DECK_A4_FIVE_TAB_OVERLAY.md")
    print("STATE:          SCAFFOLDED — runs RED at scaffold time; GREEN on A4 build close.")
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
        print(f"SLICE RED · {len(failures)}/{len(ROWS)} failed (EXPECTED at scaffold time)")
        for f in failures:
            print(f"  ! {f}")
        return 1
    print(f"SLICE GREEN · {len(ROWS)}/{len(ROWS)} rows passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
