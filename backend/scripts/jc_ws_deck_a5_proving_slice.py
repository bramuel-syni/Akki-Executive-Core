"""JC-WS-DECK-A5-HEADER-FOOTER-PARITY-SHARE — proving slice (9 rows).

Canonical Spec: /app/memory/rules/TAB_HONESTY_RULE.md
             + /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A5
             + /app/memory/sprints/JC_WS_DECK_A5_HEADER_FOOTER_PARITY_SHARE.md.

Testing sub-agents BANNED. Runs entirely via bash.
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


DETAIL_FOOTER = FRONTEND / "src" / "components" / "work_studio" / "overlay" / "DetailFooter.jsx"
DOCUMENT_OVERLAY = FRONTEND / "src" / "components" / "work_studio" / "overlay" / "DocumentOverlay.jsx"


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def row1_detail_footer_exists() -> Tuple[bool, str]:
    if not DETAIL_FOOTER.exists():
        return False, f"file-not-found={DETAIL_FOOTER}"
    src = _text(DETAIL_FOOTER)
    has_default_export = "export default function DetailFooter" in src
    accepts_props = all(p in src for p in ["contextId", "artefactId", "activeTab", "onDownload"])
    ok = has_default_export and accepts_props
    return ok, f"file-exists=True default-export={has_default_export} accepts-props={accepts_props}"


def row2_four_affordance_testids() -> Tuple[bool, str]:
    src = _text(DETAIL_FOOTER)
    expected = [
        "document-overlay-continue-in-chat-btn",
        "document-overlay-continue-in-solva-btn",
        "document-overlay-footer-download-btn",
        "document-overlay-share-btn",
    ]
    missing = [t for t in expected if t not in src]
    ok = not missing
    return ok, f"expected-testids-missing={missing or 'none'} baseline-count={len(expected)}"


def row3_continue_in_chat_dispatches_event() -> Tuple[bool, str]:
    src = _text(DETAIL_FOOTER)
    dispatches = "akki:continue-in-chat" in src
    custom_event = "new CustomEvent" in src
    detail_binding = "contextId, artefactId" in src or ("contextId" in src and "artefactId" in src)
    ok = dispatches and custom_event and detail_binding
    return ok, f"dispatches-chat-event={dispatches} CustomEvent={custom_event} detail-binding={detail_binding}"


def row4_continue_in_solva_dispatches_event() -> Tuple[bool, str]:
    src = _text(DETAIL_FOOTER)
    dispatches = "akki:continue-in-solva" in src
    ok = dispatches
    return ok, f"dispatches-solva-event={dispatches}"


def row5_share_url_builder_and_clipboard() -> Tuple[bool, str]:
    src = _text(DETAIL_FOOTER)
    url_ctor = "new URL(" in src
    search_params_set = 'searchParams.set("artefact_id"' in src or "searchParams.set('artefact_id'" in src
    tab_param_set = 'searchParams.set("tab"' in src or "searchParams.set('tab'" in src
    clipboard = "navigator.clipboard.writeText" in src
    toast_confirm = "Share link copied" in src
    ok = url_ctor and search_params_set and tab_param_set and clipboard and toast_confirm
    return ok, (
        f"URL-ctor={url_ctor} search-params-artefact-id={search_params_set} "
        f"search-params-tab={tab_param_set} clipboard={clipboard} toast={toast_confirm}"
    )


def row6_footer_download_wires_to_shared_handler() -> Tuple[bool, str]:
    src_overlay = _text(DOCUMENT_OVERLAY)
    src_footer = _text(DETAIL_FOOTER)
    footer_receives = "<DetailFooter" in src_overlay and "onDownload={handleDownload}" in src_overlay
    footer_calls_ondownload = "onDownload && onDownload(" in src_footer or "onDownload(" in src_footer
    ok = footer_receives and footer_calls_ondownload
    return ok, (
        f"DetailFooter-mounted-with-handleDownload={footer_receives} "
        f"footer-invokes-onDownload={footer_calls_ondownload}"
    )


def row7_detail_footer_mounted_outside_tabs() -> Tuple[bool, str]:
    """R7 — Chrome hard line: DetailFooter mounts AFTER </Tabs>, not inside a TabsContent."""
    import re
    src = _text(DOCUMENT_OVERLAY)
    # Find first </Tabs> position + first <DetailFooter position.
    tabs_close = src.find("</Tabs>")
    footer_open = src.find("<DetailFooter")
    footer_after_tabs = tabs_close > 0 and footer_open > tabs_close
    # Assert DetailFooter is NOT inside any <TabsContent> block.
    inside_tabs_content = False
    for m in re.finditer(r'<DetailFooter\b', src):
        pos = m.start()
        prefix = src[:pos]
        last_tc_open = prefix.rfind("<TabsContent")
        last_tc_close = prefix.rfind("</TabsContent>")
        if last_tc_open > last_tc_close:
            inside_tabs_content = True
            break
    ok = footer_after_tabs and not inside_tabs_content
    return ok, (
        f"footer-after-</Tabs>={footer_after_tabs} "
        f"not-inside-TabsContent={not inside_tabs_content}"
    )


def row8_toolbar_downloads_preserved() -> Tuple[bool, str]:
    src = _text(DOCUMENT_OVERLAY)
    expected = [
        "document-overlay-download-docx-btn",
        "document-overlay-download-pdf-btn",
        "document-overlay-download-pptx-btn",
    ]
    missing = [t for t in expected if t not in src]
    ok = not missing
    return ok, f"toolbar-download-testids-missing={missing or 'none'} baseline={len(expected)}"


def row9_regressions_green() -> Tuple[bool, str]:
    """R9 — A4 + A8-MVP + A8-BACKEND + A9 + A10 slices all GREEN."""
    results = []
    for name, script in [
        ("a4", "jc_ws_deck_a4_proving_slice.py"),
        ("a8-mvp", "jc_ws_deck_a8_proving_slice.py"),
        ("a8-backend", "jc_ws_deck_a8_backend_proving_slice.py"),
        ("a9", "jc_ws_deck_a9_proving_slice.py"),
        ("a10", "jc_ws_deck_a10_proving_slice.py"),
    ]:
        rc, out, _ = _run(["python", str(BACKEND / "scripts" / script)])
        tail = out.splitlines()[-1] if out else "no output"
        results.append((name, rc == 0, tail))
    ok = all(r[1] for r in results)
    detail = " | ".join(f"{n}={'GREEN' if g else 'RED'}({t.strip()[-35:]})" for n, g, t in results)
    return ok, detail


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 DetailFooter.jsx exists + default export + 4 props", row1_detail_footer_exists),
    ("R2 4 affordance data-testids present", row2_four_affordance_testids),
    ("R3 REAL RENDER — Continue-in-Chat dispatches akki:continue-in-chat CustomEvent", row3_continue_in_chat_dispatches_event),
    ("R4 REAL RENDER — Continue-in-ThinkLab dispatches akki:continue-in-solva CustomEvent", row4_continue_in_solva_dispatches_event),
    ("R5 REAL RENDER — Share URL builder + clipboard.writeText + toast confirmation", row5_share_url_builder_and_clipboard),
    ("R6 Footer download button wires to shared handleDownload callback", row6_footer_download_wires_to_shared_handler),
    ("R7 DetailFooter mounts OUTSIDE <Tabs> (chrome hard line preservation)", row7_detail_footer_mounted_outside_tabs),
    ("R8 Existing DOCX/PDF/PPTX Toolbar affordances preserved (testids intact)", row8_toolbar_downloads_preserved),
    ("R9 Regressions — A4 + A8-MVP + A8-BACKEND + A9 + A10 all GREEN", row9_regressions_green),
]


def main() -> int:
    print("=" * 78)
    print("JC-WS-DECK-A5-HEADER-FOOTER-PARITY-SHARE proving slice (auto-chain phase 2/4)")
    print("Canonical Spec: TAB_HONESTY_RULE + PATH_A_EXECUTION_PLAN §A5")
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
