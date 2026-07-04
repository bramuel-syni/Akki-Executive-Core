"""JC-WS-DECK-A10-RELATED-DOCS-MVP — proving slice (8 rows).

Canonical Spec: /app/memory/audits/JC_WS_DECK_CONFORMANCE_AUDIT.md §5 (DECK-064..067)
+ /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A10
+ /app/memory/sprints/JC_WS_DECK_A10_RELATED_DOCS_MVP.md
+ user dispatch 2026-07-02 (populate-chain step 3 of 3 · chain close).

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


RELATED_DOCS = FRONTEND / "src" / "components" / "work_studio" / "overlay" / "RelatedDocuments.jsx"
DOCUMENT_OVERLAY = FRONTEND / "src" / "components" / "work_studio" / "overlay" / "DocumentOverlay.jsx"


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def row1_related_documents_exists() -> Tuple[bool, str]:
    """R1 — RelatedDocuments.jsx exists + default export + accepts doc prop."""
    if not RELATED_DOCS.exists():
        return False, f"file-not-found={RELATED_DOCS}"
    src = _text(RELATED_DOCS)
    has_export_default = "export default function RelatedDocuments" in src
    accepts_doc = "{ doc }" in src
    ok = has_export_default and accepts_doc
    return ok, f"file-exists=True default-export={has_export_default} accepts-doc-prop={accepts_doc}"


def row2_reads_source_document_ids() -> Tuple[bool, str]:
    """R2 — Reads doc.source_document_ids (existing shape)."""
    src = _text(RELATED_DOCS)
    reads_ids = "doc.source_document_ids" in src or "source_document_ids" in src
    array_guard = "Array.isArray(doc.source_document_ids)" in src or "Array.isArray" in src
    ok = reads_ids and array_guard
    return ok, f"reads-source-ids={reads_ids} array-guard={array_guard}"


def row3_real_render_of_source_ids() -> Tuple[bool, str]:
    """R3 — REAL RENDER: .map() over source_document_ids + JSX chip + click handler."""
    src = _text(RELATED_DOCS)
    has_map = "sourceIds.map(" in src or ".map((docId" in src
    binds_id = "{docId}" in src
    click_handler = "handleOpen" in src or "onClick" in src
    dispatches_event = "akki:open-document-overlay" in src
    ok = has_map and binds_id and click_handler and dispatches_event
    return ok, (
        f"array-map={has_map} id-binding={binds_id} click-handler={click_handler} "
        f"dispatches-overlay-event={dispatches_event}"
    )


def row4_visibility_flag_related_true() -> Tuple[bool, str]:
    """R4 — TAB_VISIBILITY.related === true (flag flipped for MVP ship)."""
    src = _text(DOCUMENT_OVERLAY)
    related_true = "related: true" in src
    ok = related_true
    return ok, f"related-flipped-to-true={related_true}"


def row5_related_tabcontent_mounts_component() -> Tuple[bool, str]:
    """R5 — Related TabsContent mounts <RelatedDocuments doc={doc} /> + placeholder REMOVED."""
    src = _text(DOCUMENT_OVERLAY)
    m = re.search(
        r'<TabsContent\s+value=[\'"]related[\'"][^>]*>[\s\S]{0,2000}?<RelatedDocuments',
        src,
    )
    mount_present = bool(m)
    placeholder_removed = "document-overlay-tab-content-related-placeholder" not in src
    doc_passed = "<RelatedDocuments doc={doc}" in src
    ok = mount_present and placeholder_removed and doc_passed
    return ok, (
        f"related-docs-in-tab={mount_present} placeholder-removed={placeholder_removed} "
        f"doc-prop={doc_passed}"
    )


def row6_empty_state_present() -> Tuple[bool, str]:
    """R6 — Empty state rendered when source_document_ids empty."""
    src = _text(RELATED_DOCS)
    empty_testid = "related-docs-empty-state" in src
    empty_conditional = "sourceIds.length === 0" in src or "length === 0" in src
    ok = empty_testid and empty_conditional
    return ok, f"empty-testid={empty_testid} empty-conditional={empty_conditional}"


def row7_stable_testids() -> Tuple[bool, str]:
    """R7 — Stable testids on RelatedDocuments."""
    src = _text(RELATED_DOCS)
    expected = [
        "related-docs-root",
        "related-docs-item",
        "related-docs-empty-state",
    ]
    missing = [t for t in expected if t not in src]
    ok = not missing
    return ok, f"expected-testids-missing={missing or 'none'} baseline-count={len(expected)}"


def row8_regressions_green() -> Tuple[bool, str]:
    """R8 — A4 + A8 + A9 slice regressions all GREEN."""
    results = []
    for name in ["a4", "a8", "a9"]:
        rc, out, _ = _run(["python", str(BACKEND / "scripts" / f"jc_ws_deck_{name}_proving_slice.py")])
        tail = out.splitlines()[-1] if out else "no output"
        results.append((name, rc == 0, tail))
    ok = all(r[1] for r in results)
    detail = " | ".join(f"{n}={'GREEN' if g else 'RED'}({t.strip()[-40:]})" for n, g, t in results)
    return ok, detail


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 RelatedDocuments.jsx exists + default export + accepts doc prop", row1_related_documents_exists),
    ("R2 Reads doc.source_document_ids (existing shape)", row2_reads_source_document_ids),
    ("R3 REAL RENDER — .map() over source_document_ids + click handler + akki:open-document-overlay dispatch", row3_real_render_of_source_ids),
    ("R4 TAB_VISIBILITY.related === true (flag flipped)", row4_visibility_flag_related_true),
    ("R5 Related TabsContent mounts <RelatedDocuments doc={doc} /> + placeholder REMOVED", row5_related_tabcontent_mounts_component),
    ("R6 Empty state rendered when source_document_ids empty", row6_empty_state_present),
    ("R7 Stable testids on RelatedDocuments (root/item/empty-state)", row7_stable_testids),
    ("R8 A4 + A8 + A9 slice regressions all GREEN", row8_regressions_green),
]


def main() -> int:
    print("=" * 78)
    print("JC-WS-DECK-A10-RELATED-DOCS-MVP proving slice (populate-chain step 3/3 · CLOSE)")
    print("Canonical Spec: JC_WS_DECK_CONFORMANCE_AUDIT.md §5 + PATH_A_EXECUTION_PLAN §A10 + A10_RELATED_DOCS_MVP")
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
    print(f"SLICE GREEN · {len(ROWS)}/{len(ROWS)} rows passed · POPULATE CHAIN CLOSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
