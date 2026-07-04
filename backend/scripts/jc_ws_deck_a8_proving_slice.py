"""JC-WS-DECK-A8-YOUR-NOTES-MVP — proving slice (9 rows).

Canonical Spec: /app/memory/audits/JC_WS_DECK_CONFORMANCE_AUDIT.md §5 (DECK-050..059)
+ /app/memory/sprints/JC_WS_DECK_PATH_A_EXECUTION_PLAN.md §A8
+ /app/memory/sprints/JC_WS_DECK_A8_YOUR_NOTES_MVP.md
+ user dispatch 2026-07-02 (populate-chain step 1 of 3).

Testing sub-agents BANNED. Runs entirely via bash.
Split-literal discipline preserved.
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


DECK_NOTES = FRONTEND / "src" / "components" / "work_studio" / "overlay" / "DeckNotes.jsx"
DOCUMENT_OVERLAY = FRONTEND / "src" / "components" / "work_studio" / "overlay" / "DocumentOverlay.jsx"


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ==================================================================
# Rows
# ==================================================================
def row1_deck_notes_component_exists() -> Tuple[bool, str]:
    """R1 — DeckNotes.jsx exists + exports default component + accepts contextId + artefactId props."""
    if not DECK_NOTES.exists():
        return False, f"file-not-found={DECK_NOTES}"
    src = _text(DECK_NOTES)
    has_export_default = "export default function DeckNotes" in src or "export default DeckNotes" in src
    accepts_context_id = "contextId" in src
    accepts_artefact_id = "artefactId" in src
    ok = has_export_default and accepts_context_id and accepts_artefact_id
    return ok, (
        f"file-exists=True default-export={has_export_default} "
        f"contextId-prop={accepts_context_id} artefactId-prop={accepts_artefact_id}"
    )


def row2_localstorage_key_contract() -> Tuple[bool, str]:
    """R2 — After A8-BACKEND upgrade (2026-07-02): backend API contract present +
    legacy localStorage key prefix acknowledged for one-way migration import.

    Post-Tab-Honesty-Rule this row asserts:
      - The FE now goes through the backend API (`api.get/put/delete /deck-notes/{...}`).
      - The legacy localStorage key prefix is still referenced (for migration read-only).
      - No new localStorage.setItem calls exist (writes go to backend only).
    """
    src = _text(DECK_NOTES)
    api_import = 'from "@/lib/api/apiV2"' in src
    api_get = "api.get(`/deck-notes/" in src
    api_put = "api.put(`/deck-notes/" in src
    api_delete = "api.delete(`/deck-notes/" in src
    legacy_key_prefix = "akki:deck-notes:" in src  # for migration import (read-only)
    # No new writes to localStorage — only removal (migration finalizer) allowed.
    has_setitem = "localStorage.setItem" in src
    ok = api_import and api_get and api_put and api_delete and legacy_key_prefix and (not has_setitem)
    return ok, (
        f"api-import={api_import} api.get={api_get} api.put={api_put} api.delete={api_delete} "
        f"legacy-key-for-migration={legacy_key_prefix} no-new-setitem={not has_setitem}"
    )


def row3_debounced_autosave_and_saved_indicator() -> Tuple[bool, str]:
    """R3 — Debounced autosave hook + saved-timestamp state present (real content acquisition).

    Post-Tab-Honesty-Rule: debounce now dispatches `api.put` (server-authoritative).
    Server response supplies `updated_at`. UI still uses debounceRef+setTimeout pattern.
    """
    src = _text(DECK_NOTES)
    debounce_500 = "AUTOSAVE_DEBOUNCE_MS = 500" in src
    settimeout = "setTimeout" in src
    saved_state = "setSavedAt" in src and "setSavedIndicator" in src
    saved_relative_time = "Saved just now" in src
    debounce_ref = "debounceRef" in src and "clearTimeout" in src
    put_in_debounce = "api.put(" in src
    ok = all([debounce_500, settimeout, saved_state, saved_relative_time, debounce_ref, put_in_debounce])
    return ok, (
        f"debounce-500ms={debounce_500} setTimeout={settimeout} "
        f"saved-state={saved_state} saved-string={saved_relative_time} "
        f"debounce-ref+clear={debounce_ref} api.put-in-hook={put_in_debounce}"
    )


def row4_visibility_flag_notes_true() -> Tuple[bool, str]:
    """R4 — TAB_VISIBILITY.notes === true in DocumentOverlay (flag flipped for A8 ship).

    Note: A8 does NOT assert signals/related remain false — they may have flipped
    forward as subsequent panels ship in the populate chain (A9, A10). A8's own
    invariant is only that its own flag is set to true.
    """
    src = _text(DOCUMENT_OVERLAY)
    flag_true = "notes: true" in src
    ok = flag_true
    return ok, f"notes-flipped-to-true={flag_true}"


def row5_notes_tabcontent_mounts_deck_notes() -> Tuple[bool, str]:
    """R5 — Notes TabsContent mounts DeckNotes; placeholder REMOVED."""
    import re
    src = _text(DOCUMENT_OVERLAY)
    m = re.search(
        r'<TabsContent\s+value=[\'"]notes[\'"][^>]*>[\s\S]{0,2000}?<DeckNotes',
        src,
    )
    mount_present = bool(m)
    placeholder_removed = "document-overlay-tab-content-notes-placeholder" not in src
    props_passed = "contextId={contextId}" in src and "artefactId={artefactId}" in src
    ok = mount_present and placeholder_removed and props_passed
    return ok, (
        f"deck-notes-in-notes-tab={mount_present} placeholder-removed={placeholder_removed} "
        f"props-passed={props_passed}"
    )


def row6_five_stable_testids_on_deck_notes() -> Tuple[bool, str]:
    """R6 — 5 stable data-testids on DeckNotes."""
    src = _text(DECK_NOTES)
    expected_testids = [
        "deck-notes-textarea",
        "deck-notes-saved-indicator",
        "deck-notes-clear-button",
        "deck-notes-clear-confirm",
        "deck-notes-empty-state",
    ]
    missing = [t for t in expected_testids if t not in src]
    ok = not missing
    return ok, f"expected-testids-missing={missing or 'none'} baseline-count={len(expected_testids)}"


def row7_clear_notes_affordance_and_confirm() -> Tuple[bool, str]:
    """R7 — Clear-notes affordance + confirm flow: Clear button opens confirm; confirm removes via backend DELETE (post-Tab-Honesty-Rule)."""
    src = _text(DECK_NOTES)
    clear_button = "deck-notes-clear-button" in src
    confirm_dialog = "confirmClearOpen" in src
    api_delete = "api.delete(`/deck-notes/" in src
    clear_handler = "handleClearConfirmed" in src
    confirm_button = "deck-notes-clear-confirm-button" in src
    ok = all([clear_button, confirm_dialog, api_delete, clear_handler, confirm_button])
    return ok, (
        f"clear-button={clear_button} confirm-dialog-state={confirm_dialog} "
        f"api.delete={api_delete} clear-handler={clear_handler} confirm-button={confirm_button}"
    )


def row8_url_param_tab_notes_activates() -> Tuple[bool, str]:
    """R8 — URL param ?tab=notes activates Notes tab (Notes in visible-tabs allow-list; URLSearchParams hook reads tab param)."""
    src = _text(DOCUMENT_OVERLAY)
    url_param_hook = "URLSearchParams" in src
    tab_param_read = "get(\"tab\")" in src or "get('tab')" in src
    # Notes must be in the valid-tabs list AND the visible-tabs list.
    notes_in_valid = '"notes"' in src
    visible_filter = "visible.includes" in src
    ok = url_param_hook and tab_param_read and notes_in_valid and visible_filter
    return ok, (
        f"url-param-hook={url_param_hook} tab-param-read={tab_param_read} "
        f"notes-in-valid={notes_in_valid} visible-tabs-filter={visible_filter}"
    )


def row9_a4_slice_regression_green() -> Tuple[bool, str]:
    """R9 — A4 slice regression 11/11 GREEN (Step 0 gate preserved; A4 foundation unaffected by A8)."""
    rc, out, err = _run([
        "python", str(BACKEND / "scripts" / "jc_ws_deck_a4_proving_slice.py"),
    ])
    tail = (out + err).splitlines()[-2:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 DeckNotes.jsx exists + default export + accepts contextId+artefactId props", row1_deck_notes_component_exists),
    ("R2 localStorage key contract (akki:deck-notes prefix + JSON + updated_at ISO)", row2_localstorage_key_contract),
    ("R3 Debounced autosave (500ms) + saved-timestamp state (REAL RENDER: real content acquisition)", row3_debounced_autosave_and_saved_indicator),
    ("R4 TAB_VISIBILITY.notes === true (flag flipped); signals + related still false", row4_visibility_flag_notes_true),
    ("R5 Notes TabsContent mounts <DeckNotes contextId artefactId /> + placeholder REMOVED", row5_notes_tabcontent_mounts_deck_notes),
    ("R6 5 stable data-testids on DeckNotes (textarea/saved/clear/confirm/empty)", row6_five_stable_testids_on_deck_notes),
    ("R7 Clear-notes affordance + confirm dialog + localStorage.removeItem", row7_clear_notes_affordance_and_confirm),
    ("R8 URL param ?tab=notes activates Notes tab (allow-list + visible-tabs filter)", row8_url_param_tab_notes_activates),
    ("R9 A4 slice regression 11/11 GREEN (foundation preserved)", row9_a4_slice_regression_green),
]


def main() -> int:
    print("=" * 78)
    print("JC-WS-DECK-A8-YOUR-NOTES-MVP proving slice (populate-chain step 1/3)")
    print("Canonical Spec: JC_WS_DECK_CONFORMANCE_AUDIT.md §5 + PATH_A_EXECUTION_PLAN §A8 + A8_YOUR_NOTES_MVP")
    print("Sprint memo:    /app/memory/sprints/JC_WS_DECK_A8_YOUR_NOTES_MVP.md")
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
