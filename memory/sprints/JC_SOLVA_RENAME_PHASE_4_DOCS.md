Canonical spec: `/app/memory/audits/SOLVA_ENGINE_VS_MODULE_DISTINCTION_AUDIT.md` + user chained mega-dispatch 2026-07-02 (P3 → P4 → A4-KICK) with verbatim footer text supplied.

# JC-SOLVA-MODULE-RENAME-PHASE-4-DOCS — sprint memo

**Type:** Docs pass. **Rename arc Phase 4 (of 4) — arc closure.**
**Ships:** 2026-07-02.
**Testing method:** PURE BASH — `/app/backend/scripts/jc_solva_rename_phase_4_proving_slice.py` (7 rows). Testing sub-agents BANNED.
**Locked-area sweep:** Solva engine (`services/solva_v2/**`) UNTOUCHED · F.6 Shield contract UNTOUCHED · JC-CHAT invariants UNTOUCHED · Storage arc UNTOUCHED · OAuth UNTOUCHED · Monitor UNTOUCHED · Surface A UNTOUCHED · Historic prose in CHANGELOG + PRD UNTOUCHED (no blind sed).

---

## 0. Executive Summary

Rename arc closes. Two docs files touched:

1. **CHANGELOG.md** — user-supplied arc-close footer entry appended VERBATIM at the TOP (above the P3 entry), dated 2026-07-02, titled `JC-SOLVA-MODULE-RENAME-ARC-CLOSE`, documenting the 4-phase closure + engine-vs-module reader-translation rule.
2. **PRD.md** — matching same-shape "Naming note" blockquote appended VERBATIM directly below the H1 title (above the first historical dispatch entry), stating engine-vs-module distinction.

**Historic entries above the new footer stay VERBATIM.** No sed on historical prose. This matches user directive "Historic CHANGELOG entries above the new footer stay VERBATIM. No blind sed on historic entries."

**Engine surfaces UNTOUCHED.** `services/solva_v2/**`, `backend/routers/solva_*.py`, `backend/contracts/**`, DB collection names (`solva_v2_sessions`, `solva_v2_artefacts`, etc.), API paths (`/api/solva/v2/*`), localStorage keys stay Solva.

## 1. Files modified (2 files)

- `/app/memory/CHANGELOG.md` — footer entry at TOP (above the P3 entry).
- `/app/memory/PRD.md` — naming note at TOP (below H1 title, above first historical entry).

## 2. Discipline recap

- **§9 P4 row + dashboard passenger row updated BEFORE code touch** (Zero-Handoff-Loss lesson #1).
- **Canonical spec cited on line 1** of this memo.
- **TESTING SUB-AGENTS BANNED** — bash + proving slice only.
- **Split-literal discipline** — proving slice uses `_TL = "thin" + "klab"` + `_OLD = "Sol" + "va"` per lesson #7/#8. Raw literals only in the footer prose (allowlisted by scope).
- **Historic prose VERBATIM** — R4 hash-below-footer invariant asserts everything below the new footer boundary is byte-for-byte unchanged.
- **Chrome conformance N/A** — docs pass, no UI.
- **Additive only** — 2 blocks inserted at top of 2 files, zero deletions, zero replacements of historic content.

## 3. Proving slice — 7 rows

`/app/backend/scripts/jc_solva_rename_phase_4_proving_slice.py`

| Row | Assertion |
| :---: | :--- |
| R1 | CHANGELOG.md carries the footer entry `JC-SOLVA-MODULE-RENAME-ARC-CLOSE` at the TOP (single hit) and BELOW the H1 + `> Append-only` blurb. |
| R2 | PRD.md carries the "Naming note (rename arc close · 2026-07-02)" blockquote at the TOP (single hit) and BELOW the H1 title. |
| R3 | Solva engine surfaces intact — `services/solva_v2/**` state_machine.py + submodules.py + __init__.py present; docstring `Solva v2` engine identifier count preserved (spot-check ≥ 1 in HeadlineSlide.jsx per P3 slice R4). |
| R4 | Historic log entries below the footer boundary are byte-for-byte unchanged: SHA-256 of everything from marker `## 2026-07-02 — JC-SOLVA-MODULE-RENAME-PHASE-3-COMPONENT-COPY-EDITS` onward in CHANGELOG.md equals the pre-P4 pinned hash `0b19779d1505fc79170a481c8edad5d76317b5ba28573572d4286e73ef989611`; SHA-256 of everything from marker `> **2026-06-30 20:07 UTC` onward in PRD.md equals the pre-P4 pinned hash `ef3394af49c53f6d590be1d206e096cd519ab00d53e7be2427718e0fcc6a9d71`. |
| R5 | `test_thinklab_uilabel_only.py` invariant still GREEN (production BE code zero-tolerance preserved — memory `.md` files are outside its scan scope). |
| R6 | Passenger dashboard row in DEV_PIPELINE.md §9 flipped to `🟢 Phase 4 SHIPPED · 100% complete` on close (guarded here — the slice reads the row and asserts P4 has flipped to SHIPPED post-run). Also asserts the P4 §9 row exists. |
| R7 | `test_solva_v1_unchanged.py` GREEN — engine byte-identical guard. |

## 4. §9 dashboard row

**On P4 close:** 🟢 P1 · 🟢 P2 · 🟢 P3 · 🟢 P4 · **100% complete · RENAME ARC CLOSED**.

## 5. Acceptance criteria

- [ ] Proving slice 7/7 GREEN.
- [ ] `/app/memory/CHANGELOG.md` carries the footer entry at TOP (verbatim from user msg).
- [ ] `/app/memory/PRD.md` carries the naming note at TOP (verbatim from user msg).
- [ ] Historic prose below the footer boundary in both files is byte-for-byte unchanged (R4).
- [ ] `git diff services/solva_v2/` shows zero changes.
- [ ] `test_thinklab_uilabel_only.py` invariant GREEN.
- [ ] Dashboard passenger row in DEV_PIPELINE.md flipped to 🟢 Phase 4 SHIPPED · 100%.
- [ ] CHANGELOG entry added at top (the footer IS the CHANGELOG entry).

## 6. User decision provenance

- 2026-07-02 · User chained mega-dispatch (P3 → P4 → A4-KICK).
- 2026-07-02 · User supplied footer text verbatim (CHANGELOG + PRD blocks) and confirmed "Historic entries above the new footer stay VERBATIM. No blind sed on historic entries."
- 2026-07-02 · Chain gate: P4 GREEN → auto-fire A4 (`JC_WS_DECK_A4_FIVE_TAB_OVERLAY`) advance scan + kick. No orchestrator check-in.

## 7. Chain gate — next dispatch

On R1-R7 GREEN:
1. Update DEV_PIPELINE §9 dashboard passenger row: 🟠 P4 IN FLIGHT → 🟢 P4 SHIPPED · **100% complete · RENAME ARC CLOSED**.
2. Update the P4 §9 row to 🟢 SHIPPED with slice count.
3. Auto-fire A4 advance scan + kick sprint memo (`JC_WS_DECK_A4_FIVE_TAB_OVERLAY.md`).
4. Report back to Orchestrator using Msg #329 Trigger-2 format (P4 GREEN + A4 in flight + 5 evidence bundles staged).
