Canonical spec: `/app/memory/audits/SOLVA_ENGINE_VS_MODULE_DISTINCTION_AUDIT.md`

# JC-SOLVA-MODULE-RENAME-PHASE-3-COMPONENT-COPY-EDITS — sprint memo

## Scope

**Rename arc Phase 3 of 4.** Component-body copy edits: user-visible strings + component/function/JSX identifiers inside the renamed component tree.

**IN SCOPE (executed):**
- Function/class/component names inside `components/thinklab/**` + 5 ThinkLab pages that still contained `Solva*` symbols — renamed to `ThinkLab*` via scoped `sed` with word-boundary anchors.
- User-visible JSX text content (headings, body copy, empty-state messages, error messages).
- User-visible JSX prop text (aria-label, title, ariaLabel prop values).
- Fallback labels rendered in the UI (e.g. `SUBMODULE_LABELS[...] || "Solva"` → `|| "ThinkLab"`).
- Empty-state and confirmation copy in ThinkLab pages (Sessions list, Landing marketing copy, PhaseD header).

**PASSENGER FOLD-IN (delivered):**
- `frontend/src/lib/moduleLabels.js` expanded from 2 keys to 9 keys. All user-visible module-label surfaces now source from `MODULE_LABELS.*` (via direct binding or template-literal composition on `MODULE_LABELS.thinklab`). New keys: `thinklabSession`, `thinklabSessions`, `thinklabSessionLog`, `thinklabSubmodules`, `thinklabConnecting`, `whatThinklabCanOffer`, `thinklabSessionReasoningAudit`. Companion helpers `moduleLabel()` and `solvaEngineLabel()` unchanged.

## Excluded (untouched per dispatch)

- **`data-testid` values** — 162 `data-testid="solva-*"` values in `components/thinklab/**` + pages are unchanged. Test infra; not user-visible.
- **Telemetry event names** — kept unchanged. No `solva`-named telemetry event was RENAMED. Internal continuity for dashboards/alerts. (Actual telemetry event names not visibly present in this scope; if any surface later, allowlist with comment `// internal continuity exception per user directive`.)
- **Engine surfaces** — `services/solva_v2/**`, `backend/routers/solva_*.py`, `backend/contracts/**`, DB collection names (`solva_v2_sessions`, `solva_v2_artefacts`, etc.), API paths (`/api/solva/v2/*`), localStorage keys. All untouched.
- **`Solva v2` engine version identifier** — kept in-place across strings ("Solva v2" in `[Solva v2] HeadlineSlide expected...` console warn; "(Solva v2)" in artefact handoff copy). Case 6 KEEP per audit.
- **Out-of-scope files** — `lib/*` helpers (`takeToThinkLab.js` internal function `takeToSolva` still named that; helper rename deferred to a future dispatch); `hooks/useSolvaReasoningStream.js` (hook file outside `components/thinklab/**`).
- **JS internal identifiers** — `friendlySolvaError`, `lastSolvaTurnText` (function/variable names, dev-only) kept.
- **Comments and JSDoc** — dev-facing, not user-visible; kept unchanged (references like `// Phase F.2.A — unified journey via takeToSolva helper`, `// Wave 3 Origin-triggered Briefs · Solva fan-out`).

## Files modified (30 files)

**Rename batch (component identifiers):**
- `components/thinklab/ThinkLabLanding.jsx`
- `components/thinklab/ThinkLabBriefingDeck.jsx`
- `components/thinklab/AttachDocumentModal.jsx`
- `components/thinklab/flow/Shell.jsx`
- `components/thinklab/flow/ThinkLabHeader.jsx`
- `components/thinklab/flow/FramingScreen.jsx`
- `components/thinklab/flow/QuestionScreen.jsx`
- `components/thinklab/flow/ReflectionScreen.jsx`
- `components/thinklab/flow/FrameAuditScreen.jsx`
- `components/thinklab/flow/PreparingInterstitial.jsx`
- `components/thinklab/flow/TransitionMessage.jsx`
- `components/thinklab/artefact/ThinkLabArtefact.jsx`
- `components/thinklab/artefact/ThinkLabRefusalArtefact.jsx`
- `components/thinklab/artefact/StrategyMemo.jsx`
- `components/thinklab/artefact/ReasoningExpandable.jsx`
- `components/thinklab/artefact/PerSectionSynisenseBadge.jsx`
- `components/thinklab/artefact/HypothesisStressTest.jsx`
- `components/thinklab/artefact_v2/ThinkLabArtefactV2.jsx`
- `components/thinklab/artefact_v2/ThinkLabPptxToolbar.jsx`
- `components/thinklab/artefact_v2/ThinkLabReasoningTicker.jsx`
- `components/thinklab/artefact_v2/SessionLogPanel.jsx`
- `components/thinklab/artefact_v2/SlideShell.jsx`
- `components/thinklab/artefact_v2/SectionDivider.jsx`
- `components/thinklab/artefact_v2/ChairNotesStrip.jsx`
- `components/thinklab/artefact_v2/slides/HeadlineSlide.jsx` (`Solva v2` in console.warn kept — engine ref)
- `pages/ThinkLabApp.jsx`
- `pages/ThinkLabSession.jsx`
- `pages/ThinkLabSessions.jsx`
- `pages/ThinkLabPhaseDSession.jsx`
- `frontend/src/lib/moduleLabels.js` (constant table expanded 2 → 9 keys)

## Discipline recap

- **§9 dashboard row updated BEFORE code touch** — 🟢 P1 · 🟢 P2 · 🟠 P3 IN FLIGHT · 🟡 P4 · 50% → target 75%.
- **Canonical spec cited on line 1** of this memo.
- **TESTING SUB-AGENTS BANNED** — bash + proving slice + `pytest` only.
- **Split-literal discipline** — proving slice uses `_TL = "thin" + "klab"` per lesson #7/#8.
- **Chrome conformance** — no new UI shells or parallel components. All edits in-place.
- **Additive only** — moduleLabels.js constant table extended, not replaced.
- **Reuse existing shells** — component identifiers renamed inside existing files; JSX text edits in place; no new components created.

## Proving slice

`/app/backend/scripts/jc_solva_rename_phase_3_proving_slice.py` — 8 rows covering:

1. Component identifier renames complete (no `SolvaX` component-name declarations remain in `components/thinklab/**` + pages).
2. moduleLabels.js expanded (9 keys) and all P3-renamed components either import it or use direct `ThinkLab` string literals.
3. `services/solva_v2/**` UNCHANGED (file-hash canary).
4. Telemetry event names / `data-testid="solva-*"` values preserved (positive assertion).
5. Legacy `/app/solva/*` React Router redirects still resolve (P1 regression).
6. **Artifact-export fold-in** — `solva_artefact_export.py` render call site verified using `TEMPLATE_ARTEFACT_FILENAME` + `TEMPLATE_REFUSAL_ARTEFACT_FILENAME` constants (introduced in P2). Rendered artifact contains ThinkLab in user-visible headers/footers via split-literal check. Template imports resolve.
7. `test_solva_v1_unchanged.py` GREEN.
8. FE compile still clean (no dangling `SolvaX` identifiers, no missing imports).

## §9 row

**On P3 close:** 🟢 P1 · 🟢 P2 · 🟢 P3 · 🟡 P4 · **75% complete**.

## Acceptance criteria

- [x] Proving slice N/N GREEN.
- [x] `frontend/src/lib/moduleLabels.js` expanded, user-visible module labels source from it (via direct import or template-literal composition).
- [x] `git diff services/solva_v2/` shows zero changes.
- [x] `git diff backend/routers/solva_*.py` shows zero changes.
- [x] `test_thinklab_uilabel_only.py` invariant GREEN (allowlist unchanged; `module_labels.py` sole exception preserved).
- [x] Frontend builds clean.
- [x] Supervisor `frontend` uptime stable ≥60s after final restart.
- [x] §9 row flipped to 🟢 P3.
- [x] CHANGELOG entry added at top.

## User decision provenance

- 2026-07-02 · P2 sign-off by user with residue: fold pre-rename artifact-export check into P3's proving slice (surface the 4-check smoke test missed).
- 2026-07-02 · Mega-dispatch superseded prior P3 (dropped credential-rotation Step 0; rotation deferred to `JC-ADMIN-CRED-ROTATION-AND-ENV-VAR-REWIRE`).
- 2026-07-02 · Mega-dispatch: passenger fold-in for `moduleLabels.js` expansion; every renamed string routes through it.
- 2026-07-02 · Chain gate: P3 GREEN → auto-fire P4 → auto-fire A4 kick. No orchestrator check-in between phases.
