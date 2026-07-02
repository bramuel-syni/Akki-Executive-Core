"""JC-CHAT Stage A amendment — proving slice.

Canonical Spec: /app/memory/JC_CHAT_CANONICAL_SPEC.md §A + user amendment 2026-07-02
Dispatch:       JC-CHAT-STAGE-A-AMENDMENT-SHIELD-PILL-PLUS-SEE-MORE
Sprint memo:    /app/memory/sprints/JC_CHAT_STAGE_A_AMENDMENT.md

Executes 8 assertion rows validating the additive reinstate of the
"Content screened · N" pill + "See more" modal on the chat surface,
while preserving all other Stage A architectural changes.

Runs entirely via bash (no testing subagents). Exits 0 on 8/8 GREEN.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
from typing import Callable, List, Tuple


APP = Path("/app")
CHAT_JSX = APP / "frontend/src/pages/Chat.jsx"
PILL_JSX = APP / "frontend/src/components/chat/ShieldedContentPill.jsx"
BADGE_JSX = APP / "frontend/src/components/chat/PerMessageSynisenseBadge.jsx"
AGGREGATE_JSX = APP / "frontend/src/components/chat/AggregateStrip.jsx"
AMENDMENT_MEMO = APP / "memory/sprints/JC_CHAT_STAGE_A_AMENDMENT.md"

# Baseline captured 2026-07-02T16:15:36Z, pre-mod, before ShieldedContentPill
# component was authored. Pinned here for R4 byte-identical assertion.
BADGE_SHA_PRE_MOD = "c26bc2a1a72190f3"


def _sha16(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:16]


def _run(cmd: List[str]) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(APP))
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def row1_pill_and_badge_coexist() -> Tuple[bool, str]:
    """Chat.jsx mounts BOTH ShieldedContentPill AND PerMessageSynisenseBadge."""
    src = _text(CHAT_JSX)
    pill_import = 'import ShieldedContentPill from "@/components/chat/ShieldedContentPill"' in src
    badge_import = 'import PerMessageSynisenseBadge from "@/components/chat/PerMessageSynisenseBadge"' in src
    pill_mount = "<ShieldedContentPill" in src
    badge_mount = "<PerMessageSynisenseBadge" in src
    ok = pill_import and badge_import and pill_mount and badge_mount
    return ok, (
        f"pill_import={pill_import} badge_import={badge_import} "
        f"pill_mount={pill_mount} badge_mount={badge_mount}"
    )


def row2_pill_component_shape() -> Tuple[bool, str]:
    """Pill component exists with 3 required testids + See more wiring."""
    if not PILL_JSX.exists():
        return False, "ShieldedContentPill.jsx does not exist"
    src = _text(PILL_JSX)
    testid_pill = 'data-testid="chat-synisense-icon"' in src
    testid_more = 'data-testid="chat-synisense-see-more-btn"' in src
    testid_dialog = 'data-testid="chat-audit-dialog"' in src
    dialog_open_state = "setDialogOpen(true)" in src
    ok = testid_pill and testid_more and testid_dialog and dialog_open_state
    return ok, (
        f"testid_pill={testid_pill} testid_more={testid_more} "
        f"testid_dialog={testid_dialog} dialog_open_state={dialog_open_state}"
    )


def row3_modal_endpoint_parity() -> Tuple[bool, str]:
    """Modal references the 4 removed AuditDialog surfaces (endpoint parity)."""
    src = _text(PILL_JSX)
    audit_rows_ep = "/chats/${chatId}/audit`" in src
    metrics_ep = "/chats/${chatId}/synisense-metrics`" in src
    export_ep = "/chats/${chatId}/audit/export.zip`" in src
    trust_panel_evt = "akki:open-trust-panel" in src
    # Testid parity — the removed AuditDialog surfaced these testids:
    chat_audit_rows_tid = 'data-testid="chat-audit-rows"' in src
    metrics_tid = 'data-testid="chat-audit-synisense-metrics"' in src
    export_btn_tid = 'data-testid="chat-audit-export-btn"' in src
    trust_link_tid = 'data-testid="chat-audit-trust-panel-link"' in src
    ok = (
        audit_rows_ep
        and metrics_ep
        and export_ep
        and trust_panel_evt
        and chat_audit_rows_tid
        and metrics_tid
        and export_btn_tid
        and trust_link_tid
    )
    return ok, (
        f"audit_rows_ep={audit_rows_ep} metrics_ep={metrics_ep} export_ep={export_ep} "
        f"trust_panel_evt={trust_panel_evt} rows_tid={chat_audit_rows_tid} "
        f"metrics_tid={metrics_tid} export_btn_tid={export_btn_tid} "
        f"trust_link_tid={trust_link_tid}"
    )


def row4_badge_byte_identical() -> Tuple[bool, str]:
    """PerMessageSynisenseBadge.jsx byte-identical to pre-mod baseline."""
    current = _sha16(BADGE_JSX)
    ok = current == BADGE_SHA_PRE_MOD
    return ok, f"expected={BADGE_SHA_PRE_MOD} current={current}"


def row5_aggregatestrip_absent() -> Tuple[bool, str]:
    """AggregateStrip.jsx remains deleted (Stage A regression preservation)."""
    ok = not AGGREGATE_JSX.exists()
    return ok, f"exists={AGGREGATE_JSX.exists()}"


def row6_jc_chat_invariants_green() -> Tuple[bool, str]:
    """JC-CHAT-adjacent invariant suite still GREEN post-mod."""
    tests = [
        "backend/tests/invariants/test_invariant_chat_streaming_reidentify_present.py",
        "backend/tests/invariants/test_invariant_shield_no_leak.py",
        "backend/tests/invariants/test_invariant_audit_always.py",
    ]
    # Only run tests that exist to avoid false negatives on optional files.
    live = [t for t in tests if (APP / t).exists()]
    if not live:
        return False, "no JC-CHAT invariant tests found"
    rc, out, err = _run(["python", "-m", "pytest", "-q", "--tb=no", *live])
    ok = rc == 0
    tail = (out + err).strip().splitlines()[-3:] if (out or err) else []
    return ok, f"rc={rc} tests={len(live)} tail={' | '.join(tail)}"


def row7_f6_shield_contract_green() -> Tuple[bool, str]:
    """F.6 Shield-contract discipline-pay suite GREEN."""
    tests = [
        "backend/tests/test_synisense_security.py",
        "backend/tests/test_synisense_shield.py",
        "backend/tests/test_synisense_surface_validation.py",
    ]
    live = [t for t in tests if (APP / t).exists()]
    if not live:
        return False, "no F.6 tests found"
    rc, out, err = _run(["python", "-m", "pytest", "-q", "--tb=no", *live])
    ok = rc == 0
    tail = (out + err).strip().splitlines()[-3:] if (out or err) else []
    return ok, f"rc={rc} tests={len(live)} tail={' | '.join(tail)}"


def row8_pollution_ceilings() -> Tuple[bool, str]:
    """Pollution ceiling checks: Chat.jsx bounded delta, new file only, badge unchanged, AggregateStrip absent."""
    chat_loc = len(_text(CHAT_JSX).splitlines())
    # Pre-mod Chat.jsx was 2272 LOC (per pre-fix baseline). The block
    # replacement swapped a 10-line Stage A comment block for an 8-line
    # comment + mount, plus a 1-line import add — net delta = −1 LOC.
    # Bounded envelope: ±10 LOC around the pre-mod baseline.
    chat_delta_ok = 2262 <= chat_loc <= 2282
    pill_exists = PILL_JSX.exists()
    pill_loc = len(_text(PILL_JSX).splitlines()) if pill_exists else 0
    pill_bounded_ok = 100 <= pill_loc <= 320  # reasonable pill+modal bounded envelope
    badge_ok = _sha16(BADGE_JSX) == BADGE_SHA_PRE_MOD
    aggregate_absent = not AGGREGATE_JSX.exists()
    ok = chat_delta_ok and pill_exists and pill_bounded_ok and badge_ok and aggregate_absent
    return ok, (
        f"chat_loc={chat_loc}(2262<=x<=2282: {chat_delta_ok}) "
        f"pill_loc={pill_loc}(100<=x<=320: {pill_bounded_ok}) "
        f"badge_byte_identical={badge_ok} aggregate_absent={aggregate_absent}"
    )


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 pill+badge coexistence on chat surface", row1_pill_and_badge_coexist),
    ("R2 pill component shape (3 testids + modal wiring)", row2_pill_component_shape),
    ("R3 modal endpoint + testid parity vs removed AuditDialog", row3_modal_endpoint_parity),
    ("R4 PerMessageSynisenseBadge.jsx byte-identical to pre-mod", row4_badge_byte_identical),
    ("R5 AggregateStrip.jsx stays deleted (Stage A regression preservation)", row5_aggregatestrip_absent),
    ("R6 JC-CHAT invariant suite GREEN post-mod", row6_jc_chat_invariants_green),
    ("R7 F.6 Shield-contract discipline-pay GREEN", row7_f6_shield_contract_green),
    ("R8 pollution ceilings (Chat.jsx bounded, pill bounded, badge unchanged, AggregateStrip absent)", row8_pollution_ceilings),
]


def main() -> int:
    print("=" * 78)
    print("JC-CHAT-STAGE-A-AMENDMENT-SHIELD-PILL-PLUS-SEE-MORE proving slice")
    print("Canonical Spec: JC_CHAT_CANONICAL_SPEC.md §A + user amendment 2026-07-02")
    print(f"Amendment memo: {AMENDMENT_MEMO}")
    print("=" * 78)
    failures: List[str] = []
    for idx, (label, fn) in enumerate(ROWS, start=1):
        try:
            ok, detail = fn()
        except Exception as exc:  # noqa: BLE001 — slice is authoritative on raw error
            ok = False
            detail = f"raised {type(exc).__name__}: {exc}"
        status = "✅ PASS" if ok else "❌ FAIL"
        print(f"[{idx}/{len(ROWS)}] {status} — {label}")
        print(f"       {detail}")
        if not ok:
            failures.append(f"R{idx}: {label}")
    print("=" * 78)
    if failures:
        print(f"SLICE RED · {len(failures)}/{len(ROWS)} failed")
        for f in failures:
            print(f"  ✗ {f}")
        return 1
    print(f"SLICE GREEN · {len(ROWS)}/{len(ROWS)} rows passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
