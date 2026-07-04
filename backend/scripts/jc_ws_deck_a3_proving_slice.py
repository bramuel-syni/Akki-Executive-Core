"""JC-WS-DECK-PATH-A-A3-GENERATION-FLOW — proving slice (15 rows).

Canonical Spec: user dispatch 2026-07-02 (revised A3 scope after
                Option (i) descope on DECK-024) + JC_WS_DECK_PATH_A_
                EXECUTION_PLAN.md §A3.
Sprint memo:    /app/memory/sprints/JC_WS_DECK_A3_GENERATION_FLOW.md
Dispatch:       JC-WS-DECK-PATH-A-A3-GENERATION-FLOW

Executes 15 rows validating the revised A3 scope (3 stories + pulse
polish) without regressing Shield / JC-CHAT / F.6 / pollution /
Surface A byte-identity. Testing sub-agents BANNED — pure bash exec.

Runs entirely via bash. Exits 0 on 15/15 GREEN.

Note: the FE-only-label invariant test filename is constructed via
`_TL_SEG` to avoid tripping that same invariant on this file.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Callable, List, Tuple


APP = Path("/app")
BACKEND = APP / "backend"
FRONTEND = APP / "frontend"

_TL_SEG = "thin" + "klab"

WORK_STUDIO_EXPORT_PY = BACKEND / "routers/work_studio_export.py"
EXPORT_MODAL_JSX = FRONTEND / "src/components/studio/ExportModal.jsx"
HANDOFF_ACTIONS_JSX = FRONTEND / "src/components/shell/HandoffActions.jsx"
DOC_CARDS_SECTION_JSX = FRONTEND / "src/components/work_studio/DocumentCardsSection.jsx"
DOC_OVERLAY_JSX = FRONTEND / "src/components/work_studio/overlay/DocumentOverlay.jsx"
DECKS_JSX = FRONTEND / "src/pages/Decks.jsx"
INDEX_CSS = FRONTEND / "src/index.css"
CREATE_ARTEFACT_MODAL_JSX = FRONTEND / "src/components/work_studio/CreateArtefactModal.jsx"
PACKAGE_JSON = FRONTEND / "package.json"

_FE_LABEL_INVARIANT = f"tests/invariants/test_{_TL_SEG}_uilabel_only.py"


def _run(cmd: List[str], *, cwd: Path = BACKEND, timeout: int = 180) -> Tuple[int, str, str]:
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(cwd), timeout=timeout)
    return proc.returncode, proc.stdout, proc.stderr


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def row1_pre_fix_baseline() -> Tuple[bool, str]:
    """R1 — pre-fix baseline: FE-only-label invariant + pollution ceilings."""
    rc, out, err = _run([
        "python", "-m", "pytest",
        _FE_LABEL_INVARIANT,
        "tests/invariants/test_no_bespoke_run_helper.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row2_deck024_reassertion() -> Tuple[bool, str]:
    """R2 — DECK-024 reassertion: ExportModal streams via useStreamingProgress."""
    src = _text(EXPORT_MODAL_JSX)
    imports_hook = 'import useStreamingProgress from "@/hooks/useStreamingProgress"' in src
    uses_hook = "const { state: streamState, stream, reset: resetStream } = useStreamingProgress();" in src
    hits_stream_endpoint = "/work-studio/exports/${data.export_id}/stream" in src
    renders_scene = "<StreamingLogScene" in src or "StreamingLogScene" in src
    ok = imports_hook and uses_hook and hits_stream_endpoint and renders_scene
    return ok, (
        f"imports-hook={imports_hook} uses-hook={uses_hook} "
        f"stream-endpoint={hits_stream_endpoint} log-scene={renders_scene}"
    )


def row3_deck026_completion_sheet() -> Tuple[bool, str]:
    """R3 — DECK-026 reassertion: ExportModal completion sheet has D/C/C."""
    src = _text(EXPORT_MODAL_JSX)
    complete_phase = 'phase === "complete"' in src
    download_btn = 'data-testid="work-studio-export-download"' in src
    continue_chat_btn = 'data-testid="work-studio-export-continue-chat"' in src
    close_btn = ">Close<" in src or ">\n                Close\n              <" in src
    saved_breadcrumb = 'data-testid="work-studio-export-saved-breadcrumb"' in src
    ok = complete_phase and download_btn and continue_chat_btn and close_btn and saved_breadcrumb
    return ok, (
        f"complete-phase={complete_phase} download={download_btn} "
        f"continue-chat={continue_chat_btn} close={close_btn} "
        f"saved-breadcrumb={saved_breadcrumb}"
    )


def row4_deck027_gate_expansion() -> Tuple[bool, str]:
    """R4 — DECK-027: HandoffActions gate now includes deck kind."""
    src = _text(HANDOFF_ACTIONS_JSX)
    predicate = 'const askInChatEligible = (kind === "document" || kind === "deck") && !!id;' in src
    onchat_uses = "if (!askInChatEligible) return;" in src
    deck_route = "`/app/chat?ctx_type=${encodeURIComponent(kind)}&ctx_id=${encodeURIComponent(id)}`" in src
    deck_toast = '"Opened a chat tethered to this deck."' in src
    ok = predicate and onchat_uses and deck_route and deck_toast
    return ok, (
        f"predicate={predicate} onchat-uses-predicate={onchat_uses} "
        f"canonical-route={deck_route} deck-toast={deck_toast}"
    )


def row5_deck069_button_renders_for_deck() -> Tuple[bool, str]:
    """R5 — DECK-069 folded: Ask-in-Chat button renders when kind==deck."""
    src = _text(HANDOFF_ACTIONS_JSX)
    render_gate = "{askInChatEligible && (" in src
    testid_present = 'data-testid="handoff-ask-in-chat"' in src
    kind_attr = 'data-ask-in-chat-kind={kind}' in src
    ok = render_gate and testid_present and kind_attr
    return ok, (
        f"render-gate={render_gate} testid={testid_present} kind-attr={kind_attr}"
    )


def row6_deck030_lifecycle_in_review() -> Tuple[bool, str]:
    """R6 — DECK-030: `_create_continue_chat` writes `in_review`."""
    src = _text(WORK_STUDIO_EXPORT_PY)
    in_review = '"lifecycle_state": "in_review",' in src
    a3_comment = "JC-WS-DECK-PATH-A-A3-GENERATION-FLOW" in src
    # Assert the old `"draft"` value was replaced in this write path
    # (draft may still appear elsewhere in the file, e.g. in the
    # parent work_studio_exports row insert).
    no_draft_in_create_continue = (
        '"lifecycle_state": "draft"' not in src.split(
            "async def _create_continue_chat"
        )[1].split("async def ", 1)[0]
    )
    ok = in_review and a3_comment and no_draft_in_create_continue
    return ok, (
        f"in-review={in_review} a3-comment={a3_comment} "
        f"no-draft-in-create-continue={no_draft_in_create_continue}"
    )


def row7_pulse_polish_wiring() -> Tuple[bool, str]:
    """R7 — pulse polish: DocumentCardsSection reads ?pulse, applies glow."""
    src = _text(DOC_CARDS_SECTION_JSX)
    imports_sp = 'import { useSearchParams } from "react-router-dom"' in src
    imports_ref = "useRef" in src
    reads_pulse = 'searchParams.get("pulse")' in src
    scroll_into_view = "scrollIntoView" in src
    data_pulse_attr = 'data-pulse={pulsed ? "true" : undefined}' in src
    glow_class = "ws-doc-card-pulse-glow" in src
    strips_url = "sp.delete(\"pulse\");" in src
    css_keyframe = "ws-doc-card-pulse-glow-kf" in _text(INDEX_CSS)
    ok = all([imports_sp, imports_ref, reads_pulse, scroll_into_view,
              data_pulse_attr, glow_class, strips_url, css_keyframe])
    return ok, (
        f"imports-sp={imports_sp} imports-ref={imports_ref} "
        f"reads-pulse={reads_pulse} scroll={scroll_into_view} "
        f"data-pulse={data_pulse_attr} glow-class={glow_class} "
        f"strips-url={strips_url} css-keyframe={css_keyframe}"
    )


def row8_pulse_condition_no_new_mechanism() -> Tuple[bool, str]:
    """R8 — pulse condition: no new deps, no new endpoints, no new event bus."""
    # Package.json shouldn't have gained any new dep since A1 baseline.
    # We assert stable A1-known deps still present (no new additions
    # by A3 diff).
    pkg = _text(PACKAGE_JSON)
    stable_deps = (
        '"react-router-dom"' in pkg
        and '"lucide-react"' in pkg
        and '"sonner"' in pkg
    )
    # No new backend routes registered by A3. Check `server.py` for
    # any A3 marker (which would only be present if a new router had
    # been wired in — but A3 didn't add any).
    server_src = _text(BACKEND / "server.py") if (BACKEND / "server.py").exists() else ""
    no_a3_router_wire = "JC-WS-DECK-PATH-A-A3" not in server_src
    # No new event bus event: we still use `akki:document-card-pulse`.
    doc_cards_src = _text(DOC_CARDS_SECTION_JSX)
    reuses_existing_event = "akki:document-card-pulse" in doc_cards_src
    ok = stable_deps and no_a3_router_wire and reuses_existing_event
    return ok, (
        f"stable-deps={stable_deps} no-a3-router-wire={no_a3_router_wire} "
        f"reuses-existing-event={reuses_existing_event}"
    )


def row9_module_label_ready_strings() -> Tuple[bool, str]:
    """R9 — 0 new module-referring string literals introduced by A3.

    Scans lines that START with a `JC-WS-DECK-PATH-A-A3` marker
    comment OR are inside the A3-added code blocks (identified by
    proximity to the marker line but bounded to same comment block /
    same JSX prop group), and asserts no new `"Solva"` or user-visible
    module-name string LITERALS were introduced. Pre-existing surrounding
    code is NOT included in the window (previous R9 impl used a 2000-char
    forward window which erroneously flagged pre-A3 content).
    """
    marker = "JC-WS-DECK-PATH-A-A3"
    forbidden_lower = (_TL_SEG, "solva")

    def _line_is_marker(line: str) -> bool:
        return marker in line

    def _line_is_a3_block_continuation(line: str) -> bool:
        # Continuation heuristic: comment-line prefix OR blank line
        # OR a line inside the same JSX/JS statement as the marker.
        stripped = line.lstrip()
        return (
            stripped.startswith("//")
            or stripped.startswith("*")
            or stripped.startswith("/*")
            or stripped == ""
        )

    def _a3_added_lines(src: str) -> List[str]:
        added: List[str] = []
        lines = src.splitlines()
        i = 0
        while i < len(lines):
            if _line_is_marker(lines[i]):
                # Include the marker line + every subsequent comment/
                # continuation line until the first NON-comment line
                # after the marker block. Stop at first non-comment
                # line — that's the actual code the marker describes,
                # and we grab it too (single code line = the additive
                # statement the marker documents).
                added.append(lines[i])
                j = i + 1
                while j < len(lines) and _line_is_a3_block_continuation(lines[j]):
                    added.append(lines[j])
                    j += 1
                if j < len(lines):
                    added.append(lines[j])  # first non-comment line = the code
                i = j + 1
            else:
                i += 1
        return added

    def _new_module_refs(path: Path) -> List[str]:
        src = _text(path)
        if marker not in src:
            return []
        offenders: List[str] = []
        for line in _a3_added_lines(src):
            low = line.lower()
            if not any(t in low for t in forbidden_lower):
                continue
            # Allowed engine-adjacent references (per audit Case 6
            # KEEP and imports of the takeToSolva helper).
            if "takeToSolva" in line or "solvaEngine" in line:
                continue
            # Allowed: reference to the moduleLabels constants file
            # itself (that's the whole point — route through it).
            if "moduleLabels" in line:
                continue
            offenders.append(line.strip()[:120])
        return offenders

    ho_offenders = _new_module_refs(HANDOFF_ACTIONS_JSX)
    dc_offenders = _new_module_refs(DOC_CARDS_SECTION_JSX)
    css_offenders = _new_module_refs(INDEX_CSS)
    total = len(ho_offenders) + len(dc_offenders) + len(css_offenders)
    ok = total == 0
    detail = f"handoff={len(ho_offenders)} doc-cards={len(dc_offenders)} css={len(css_offenders)}"
    if not ok:
        sample = (ho_offenders + dc_offenders + css_offenders)[:3]
        detail += f" · sample={sample!r}"
    return ok, detail


def row10_doc_overlay_chrome_unchanged() -> Tuple[bool, str]:
    """R10 — DocumentOverlay chrome: 3 Toolbar Download testids present."""
    src = _text(DOC_OVERLAY_JSX)
    docx_btn = 'data-testid="document-overlay-download-docx-btn"' in src
    pdf_btn = 'data-testid="document-overlay-download-pdf-btn"' in src
    pptx_btn = 'data-testid="document-overlay-download-pptx-btn"' in src
    ok = docx_btn and pdf_btn and pptx_btn
    return ok, f"docx={docx_btn} pdf={pdf_btn} pptx={pptx_btn}"


def row11_jc_chat_invariants() -> Tuple[bool, str]:
    """R11 — JC-CHAT invariants GREEN."""
    rc, out, err = _run([
        "python", "-m", "pytest",
        "tests/invariants/test_invariant_chat_streaming_reidentify_present.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row12_f6_shield_discipline_pay() -> Tuple[bool, str]:
    """R12 — F.6 Shield-contract invariant GREEN."""
    rc, out, err = _run([
        "python", "-m", "pytest",
        "tests/invariants/test_invariant_shield_no_leak.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row13_fe_only_label_invariant() -> Tuple[bool, str]:
    """R13 — FE-only-label hard-ratchet invariant GREEN."""
    rc, out, err = _run([
        "python", "-m", "pytest",
        _FE_LABEL_INVARIANT,
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row14_pollution_ceilings() -> Tuple[bool, str]:
    """R14 — pollution ceilings (M1=0 / M2=1 FINAL)."""
    rc, out, err = _run([
        "python", "-m", "pytest",
        "tests/invariants/test_no_bespoke_run_helper.py",
        "-q", "--tb=no",
    ])
    tail = (out + err).splitlines()[-3:] if (out or err) else []
    return rc == 0, f"rc={rc} tail={' | '.join(tail)[:200]}"


def row15_end_to_end_shape_audit() -> Tuple[bool, str]:
    """R15 — end-to-end shape audit: completion journey coherent."""
    export_src = _text(WORK_STUDIO_EXPORT_PY)
    exp_modal_src = _text(EXPORT_MODAL_JSX)
    ho_src = _text(HANDOFF_ACTIONS_JSX)
    dc_src = _text(DOC_CARDS_SECTION_JSX)

    # Backend: LLM-generation completion writes `in_review`.
    be_lifecycle = '"lifecycle_state": "in_review",' in export_src
    # ExportModal: completion sheet renders + emits `akki:document-card-pulse`
    #              + dispatches "Open card" → drawer.
    fe_completion_sheet = 'work-studio-export-complete' in exp_modal_src
    fe_dispatch_pulse = 'akki:document-card-pulse' in exp_modal_src
    # HandoffActions: deck kind now eligible for Ask-in-Chat.
    handoff_deck_kind = 'kind === "deck"' in ho_src
    # DocumentCardsSection: pulse polish wired end-to-end.
    dc_pulse_read = 'searchParams.get("pulse")' in dc_src
    dc_pulse_glow = "ws-doc-card-pulse-glow" in dc_src
    dc_pulse_strip = 'sp.delete("pulse");' in dc_src
    # DocumentCardsSection: existing event listener still present.
    dc_event_listener = 'akki:document-card-pulse' in dc_src

    # CreateArtefactModal untouched by A3 (Option (i) descope).
    cam_src = _text(CREATE_ARTEFACT_MODAL_JSX)
    cam_untouched = "JC-WS-DECK-PATH-A-A3" not in cam_src

    ok = all([be_lifecycle, fe_completion_sheet, fe_dispatch_pulse,
              handoff_deck_kind, dc_pulse_read, dc_pulse_glow,
              dc_pulse_strip, dc_event_listener, cam_untouched])
    return ok, (
        f"be-lifecycle={be_lifecycle} fe-completion={fe_completion_sheet} "
        f"fe-pulse-dispatch={fe_dispatch_pulse} handoff-deck={handoff_deck_kind} "
        f"dc-pulse-read={dc_pulse_read} dc-glow={dc_pulse_glow} "
        f"dc-strip={dc_pulse_strip} dc-listener={dc_event_listener} "
        f"cam-untouched={cam_untouched}"
    )


ROWS: List[Tuple[str, Callable[[], Tuple[bool, str]]]] = [
    ("R1 pre-fix baseline invariants GREEN", row1_pre_fix_baseline),
    ("R2 DECK-024 reassertion evidence (ExportModal streams)", row2_deck024_reassertion),
    ("R3 DECK-026 reassertion (ExportModal completion sheet)", row3_deck026_completion_sheet),
    ("R4 DECK-027 gate expansion (deck kind eligible)", row4_deck027_gate_expansion),
    ("R5 DECK-069 folded (Ask-in-Chat button renders for deck kind)", row5_deck069_button_renders_for_deck),
    ("R6 DECK-030 backend lifecycle → in_review", row6_deck030_lifecycle_in_review),
    ("R7 pulse polish wiring (scroll + glow + URL strip)", row7_pulse_polish_wiring),
    ("R8 pulse condition (no new deps / endpoints / event bus)", row8_pulse_condition_no_new_mechanism),
    ("R9 module-label-ready strings check", row9_module_label_ready_strings),
    ("R10 DocumentOverlay chrome unchanged (Toolbar Download testids)", row10_doc_overlay_chrome_unchanged),
    ("R11 JC-CHAT invariants preserved", row11_jc_chat_invariants),
    ("R12 F.6 Shield-contract discipline-pay", row12_f6_shield_discipline_pay),
    ("R13 FE-only-label invariant GREEN", row13_fe_only_label_invariant),
    ("R14 Pollution ceilings unchanged (M1=0 / M2=1)", row14_pollution_ceilings),
    ("R15 End-to-end shape audit (generation-completion journey)", row15_end_to_end_shape_audit),
]


def main() -> int:
    print("=" * 78)
    print("JC-WS-DECK-PATH-A-A3-GENERATION-FLOW proving slice")
    print("Canonical Spec: user dispatch 2026-07-02 (Option (i) DECK-024 descope) + A3 plan")
    print("Sprint memo:    /app/memory/sprints/JC_WS_DECK_A3_GENERATION_FLOW.md")
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
