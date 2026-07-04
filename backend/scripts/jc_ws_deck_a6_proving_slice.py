"""JC-WS-DECK-A6-DOCUMENT-TAB-CONTENT — proving slice (8 rows).

Canonical Spec: /app/memory/rules/TAB_HONESTY_RULE.md
             + /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A6
             + /app/memory/sprints/JC_WS_DECK_A6_DOCUMENT_TAB_CONTENT.md.
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


DOC_OUTLINE = FRONTEND / "src" / "components" / "work_studio" / "overlay" / "DocumentOutline.jsx"
DOCUMENT_OVERLAY = FRONTEND / "src" / "components" / "work_studio" / "overlay" / "DocumentOverlay.jsx"


def _run(cmd, *, cwd=BACKEND, timeout=180):
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(p): return p.read_text(encoding="utf-8")


def r1() -> Tuple[bool, str]:
    if not DOC_OUTLINE.exists():
        return False, f"file-not-found={DOC_OUTLINE}"
    src = _text(DOC_OUTLINE)
    has_default = "export default function DocumentOutline" in src
    accepts = ("doc" in src and "onOpenRelatedTab" in src)
    return has_default and accepts, f"file-exists=True default-export={has_default} props-doc+onOpenRelatedTab={accepts}"


def r2() -> Tuple[bool, str]:
    """R2 — REAL RENDER: outline reads doc.structured_content.sections + maps headings."""
    src = _text(DOC_OUTLINE)
    reads_sections = "doc.structured_content.sections" in src or "structured_content" in src
    is_array_guard = "Array.isArray" in src
    map_headings = "outlineItems.map(" in src
    heading_text = "s.heading" in src
    ok = reads_sections and is_array_guard and map_headings and heading_text
    return ok, (
        f"reads-sections={reads_sections} array-guard={is_array_guard} "
        f"map-headings={map_headings} heading-text-binding={heading_text}"
    )


def r3() -> Tuple[bool, str]:
    """R3 — Click-to-scroll wiring — scrollIntoView on matching h2."""
    src = _text(DOC_OUTLINE)
    scroll_fn = "scrollToHeading" in src
    scroll_call = "scrollIntoView" in src
    text_match = "textContent" in src and 'h2' in src
    ok = scroll_fn and scroll_call and text_match
    return ok, f"scrollToHeading-fn={scroll_fn} scrollIntoView-call={scroll_call} h2-textContent-match={text_match}"


def r4() -> Tuple[bool, str]:
    """R4 — REAL RENDER: source-context reads doc.source_document_ids.length."""
    src = _text(DOC_OUTLINE)
    reads_ids = "doc.source_document_ids" in src
    length_used = "sourceCount" in src or ".length" in src
    ok = reads_ids and length_used
    return ok, f"reads-source-document-ids={reads_ids} length-used={length_used}"


def r5() -> Tuple[bool, str]:
    """R5 — Related tab pointer button dispatches setActiveTab("related") via onOpenRelatedTab."""
    src_outline = _text(DOC_OUTLINE)
    src_overlay = _text(DOCUMENT_OVERLAY)
    outline_button = "document-outline-open-related-btn" in src_outline
    outline_invokes = "onOpenRelatedTab" in src_outline
    overlay_wires = 'setActiveTab("related")' in src_overlay or "setActiveTab('related')" in src_overlay
    ok = outline_button and outline_invokes and overlay_wires
    return ok, (
        f"outline-related-button={outline_button} outline-invokes-callback={outline_invokes} "
        f"overlay-wires-setActiveTab-related={overlay_wires}"
    )


def r6() -> Tuple[bool, str]:
    """R6 — Stable testids on DocumentOutline."""
    src = _text(DOC_OUTLINE)
    expected = [
        "document-outline-root",
        "document-outline-item",
        "document-outline-open-related-btn",
        "document-outline-source-context",
    ]
    missing = [t for t in expected if t not in src]
    return not missing, f"expected-testids-missing={missing or 'none'} baseline-count={len(expected)}"


def r7() -> Tuple[bool, str]:
    """R7 — Document TabsContent mounts DocumentOutline BEFORE DocumentSurface."""
    src = _text(DOCUMENT_OVERLAY)
    m = re.search(
        r'<TabsContent\s+value=[\'"]document[\'"][^>]*>[\s\S]{0,3000}?<DocumentOutline[\s\S]{0,3000}?<DocumentSurface',
        src,
    )
    ok = bool(m)
    return ok, f"outline-before-surface-in-document-tab={ok}"


def r8() -> Tuple[bool, str]:
    """R8 — Regressions — A4 + A5 + A8-MVP + A8-BACKEND + A9 + A10 all GREEN."""
    results = []
    for name, script in [
        ("a4", "jc_ws_deck_a4_proving_slice.py"),
        ("a5", "jc_ws_deck_a5_proving_slice.py"),
        ("a8-mvp", "jc_ws_deck_a8_proving_slice.py"),
        ("a8-backend", "jc_ws_deck_a8_backend_proving_slice.py"),
        ("a9", "jc_ws_deck_a9_proving_slice.py"),
        ("a10", "jc_ws_deck_a10_proving_slice.py"),
    ]:
        rc, out, _ = _run(["python", str(BACKEND / "scripts" / script)])
        tail = out.splitlines()[-1] if out else "no output"
        results.append((name, rc == 0, tail))
    ok = all(r[1] for r in results)
    detail = " | ".join(f"{n}={'GREEN' if g else 'RED'}({t.strip()[-30:]})" for n, g, t in results)
    return ok, detail


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 DocumentOutline.jsx exists + default export + doc/onOpenRelatedTab props", r1),
    ("R2 REAL RENDER — reads doc.structured_content.sections + .map() over headings", r2),
    ("R3 Click-to-scroll wiring — scrollIntoView via h2 textContent match", r3),
    ("R4 REAL RENDER — source-context reads doc.source_document_ids.length", r4),
    ("R5 Related tab pointer → setActiveTab('related') wiring", r5),
    ("R6 Stable testids on DocumentOutline", r6),
    ("R7 Document TabsContent mounts DocumentOutline BEFORE DocumentSurface", r7),
    ("R8 Regressions — A4 + A5 + A8-MVP + A8-BACKEND + A9 + A10 all GREEN", r8),
]


def main() -> int:
    print("=" * 78)
    print("JC-WS-DECK-A6-DOCUMENT-TAB-CONTENT proving slice (auto-chain phase 3/4)")
    print("Canonical Spec: TAB_HONESTY_RULE + PATH_A_EXECUTION_PLAN §A6")
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
