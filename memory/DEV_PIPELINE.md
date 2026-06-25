# Dev Pipeline & QA Log

> **Maintained by:** orchestrator + builder.
> **Updated at:** every dispatch + every phase close. Builder updates as part of phase-close deliverable.
> **For:** user QA review.

## 1. Current State

**JC-WS dispatch ACTIVE 2026-06-25.** User issued the full Work Studio build dispatch (Document Generation + Analyze) with locked design + production-quality bar + proving-slice discipline. Canonical spec persisted at **`/app/memory/JC_WS_CANONICAL_SPEC.md`** — single source of truth; every JC-WS sprint memo MUST cite it. **Hard rule (pinned 2026-06-25):** no pixel of the current Generate Document UI changes during JC-WS. Adding REAL data to existing UI fields = BEHAVIOUR (allowed). Adding new UI elements not named by the spec = UI change (STOP and surface). Stage 4.2 regex kind-recommender (`e0fb89b2`) stays as a quiet "Suggested" pill on chat affordance only; JC-WS does NOT use it for kind routing — **kind is selected by the journey the user enters**, not inferred. **UI inventory** persisted at **`/app/memory/audit/JC_WS_ui_inventory.md`** — 5 journeys inventoried, 7 truly-MISSING UI items surfaced for user direction (Brief's 3 source origins, Analyze's highlights-as-cards / prompt tool / question tips / "Finish & export" wizard handoff), all other JC-WS surfaces classified EXISTS-TODAY (CompilationWizard for Source-material packs, ExportModal already a wizard, DocumentOverlay lifecycle Draft/In Review/Committed + IntelligenceCard + AIRevisionPanel). **The Board Pack proving slice can proceed on EXISTS-TODAY UI** entirely via BE wiring — MISSING items don't block it. **AWAITING user direction** on how to handle the 7 MISSING items before proceeding.

**Runway Stage 5 CLOSED 2026-06-24** (prior — Full Runway dispatch complete). One verification commit confirms every backend the three Stage 5 FE shells (Task Manager · Monitor · Pulse) depend on serves authenticated members at runtime — STOP gate not tripped. 7 new live-call e2e tests + 57 pre-existing surface tests GREEN. Full Runway combined regression: 170/170 GREEN. Sprint memo at `sprints/STAGE_5_FE_SHELL_VERIFICATION.md`.

**Runway Stage 4 CLOSED 2026-06-24** (prior). Two product-code-disciplined commits ship the Work Studio end-to-end pass. **Stage 4.2** (`e0fb89b2`) — chat Work Studio affordance auto-picks the best-fit kind from the captured objective via a pure-JS regex pipeline (zero net-new LLM calls); ordered high → low confidence (board_pack > committee_pack > minutes > deck > report > brief). 21 jest unit cases lock the heuristic; UI surfaces a `Suggested` pill on the matching tile + a quiet reason line, and the moment the user clicks any tile the recommender stops auto-overwriting. **Stage 4.3** (`edc278fe`) — Solva v2 Analyze narration now lands in DOCX / PPTX / XLSX report exports. `WorkbookAnalysis` schema extended with two optional carriers (`analyze_narration_headline` + `analyze_narration_observations`); `_adapt_new_analysis_to_workbook_analysis` reads them from `row.headline` + `row.observations` (synthesize_v2 already mirrors `runs[-1]` there); the three builders inject a `Bottom Line` section (DOCX heading + paragraphs; PPTX slide; XLSX sheet at position 0) carrying the headline + observations with their cell-range citations. 4 e2e tests pass (DOCX / XLSX / PPTX content + pre-synthesis regression). Pattern: `httpx.AsyncClient + ASGITransport + @pytest.mark.asyncio` so the test client lives on conftest's session loop. Tenancy allowlist line-numbers refreshed (3 entries shifted by the adapter expansion). 98/98 invariants + Stage 4.3 tests GREEN. Sprint memo at `sprints/STAGE_4_WORK_STUDIO.md`.

**Runway Stage 3 CLOSED 2026-06-24** (prior). Function-based renames via Option C: `services/solva` → `services/solva_voice_audit`, `routers/monitor.py` → `routers/monitor_dashboard.py`, `routers/monitor_v2.py` → `routers/monitor_strategic_items.py`. 26 files moved, 63 import callsites updated, hard-ratchet invariant locks the new names. Sprint memo at `sprints/STAGE_3_FUNCTION_RENAMES.md`.

**Phase AUDIT_P1 closed 2026-06-24** (prior). CI lane greens (5/5 tasks, strict report-only / zero product code): `frontend/yarn.lock` committed; pip-audit GREEN under existing IGNORED_VULNS; spaCy github-release lines annotated with `# ci-requirements-guard: allow`; yarn audit GREEN under `--level high`; `.gitleaks.toml` allowlist extended for sprint/audit memos + PRODUCT_REVIEW.md (5 findings → 0). Sprint memo at `sprints/PHASE_AUDIT_P1.md`.

**Phase AUDIT_P0 closed 2026-06-24** (prior). Committed dev-DB dumps purged from git history via `git filter-repo`: 3 561 tracked files / 15 snapshot dirs / 1 022.9 MiB / 49 MiB packfile reclaimed. Sprint memo at `sprints/PHASE_AUDIT_P0.md`.

**Track Chat — Phase B1.1 closed 2026-06-24** (prior). Manual Work Studio affordance live on `/app/chat`: end-to-end chain verified `export_id=7fd6da82` → COMPLETE → 38 891-byte DOCX.

## 2. Active Dispatch

**JC-WS Work Studio build (Document Generation + Analyze)** — canonical spec at `/app/memory/JC_WS_CANONICAL_SPEC.md`; UI-untouched hard rule; proving-slice discipline. UI inventory at `/app/memory/audit/JC_WS_ui_inventory.md`. **AWAITING user direction** on 7 MISSING UI items before Board Pack proving slice resumes.

Stages 1-5 of the prior Full Runway dispatch CLOSED. Backlog: §9 follow-ups (`solva_v2` rename, Mongo collection rename, FE comment polish, `synisense_observability` mount), ThinkLab Gate A render-check + Flag 3 (separate user call — comes AFTER JC-WS per user's ordering Work Studio → ThinkLab → Chat).

## 3. Parallel Tracks

### 3.1 Track A — Re-architecture / Debt Closure
- **Status:** CLOSED (Phase 5.5.2)
- **End state:** 86/86 quarantined tests unlocked; 2 production bugs fixed; cross-context invariant 0/0; ratchet held throughout
- **Open follow-ons (parked):** Phase 5.5.3 candidate C (broader-suite drift across ~7 unrelated files); Phase 5.6+ BE narrowing batches 2-N (ratchet at 42 routes)

### 3.2 Track ThinkLab — Guided Reasoning Experience (parallel product track)
- **Current state:** TL0 closed; awaiting user Flag 3 (reference deck anchor) call
- **Locked decisions:** all 4 paths ship together · fixed structure + adaptive Depth (framing+count of preset probes) · 5-layer order SHARED · Develop-strategy canon at `/app/memory/briefs/SOLVA.md` · Solva `pptx_exporter` as deck-grade surface (orchestrator called Flags 1+2) · internal-name invariant build-breaking · internal walk-through verification gate
- **Next dispatch:** TL1.1 (anchor exemplar + pin parity-test fixture; ~1-2 days; minimal code)
- **Then:** TL1.2 (collapsed build+characterize: state-machine 5-layer parameterisation + 12 preset probe templates + L1 candidate persistence + confidence_scores per layer + UI rename + Solva-export wiring + parity test)
- **Sprint memos:** `/app/memory/sprints/PHASE_TL0_THINKLAB_PREREAD.md`

### 3.3 Track Chat — Consumer-Grade Chat UX
- **Status:** Currently **LIVE** (operational); B1 consumer-surface build closed 2026-06-24.
- **Prior history:**
  - **Phase B1.1** (2026-06-24) — Chat manual Work Studio affordance: composer toolbar "Create" button opens a modal with all 6 generation kinds + mechanically-prefilled description (last 6 turns) / objective (last user message) / scope (context + chat title). Handoff to the WS1-uniform `/api/contexts/{ctx}/work-studio/export/{kind}` route. End-to-end chain green: `export_id=7fd6da82` → COMPLETE → 38 891-byte DOCX with valid ZIP magic. Prefill is 100% pure JS — zero net-new LLM calls. Disabled-out-of-org tooltip handled honestly. New component `frontend/src/components/chat/WorkStudioAffordanceModal.jsx`. · `sprints/PHASE_B1_1_CHAT_WS_AFFORDANCE.md`.
  - **Phase B1** (2026-06-24) — Chat consumer-surface build: grouped two-level model picker (Claude · GPT · Gemini provider groups) + AST invariant `test_invariant_chat_streaming_reidentify_present.py` pinning `StreamingReidentifier(...)` in `stream_message` + generalised `test_invariant_shield_no_leak.py` chat surface across all 3 providers + deliberate-violation smoke rail (7 default-lane tests). Pre-B1 FE regressions repaired (missing `tsconfig.json` + `SessionTimeoutGuard` apiV2/raw-axios mix-up). · `sprints/PHASE_B1_CHAT_BUILD.md`.
  - **Phase 5.10** (2026-02-23 fork-resume) — Chat resilience: production cancellation + audit-panel red error fix on `/app/chat` + `/api/chats/{cid}/messages/stream` · `sprints/P5_10_chat_resilience.md`.
  - **Phase F** (2026-05-21) — Akki Chat boundary-removal pass: chrome refinement only, no palette/typography/IA changes · `sprints/PHASE_F_CHAT_BOUNDARY_STATE.md`.
  - **H2** (2026-05-24, read-only) — Shield Uniformity Audit: forensic check that LLMs never see confidential data + Shield-always-on across roles/surfaces; surfaced P0 caveats → H2.5 · `sprints/H2_SHIELD_UNIFORMITY_AUDIT.md`.
  - **H2.5** (2026-05-24) — Streaming PII fix + audit-integrity invariant: closed 3 P0s from H2 audit + audit-integrity violation; covers streaming PII fix for chat · `sprints/H2_5_STREAMING_PII_FIX_STATE.md`.
  - **Phase 14** (2026-06-05) — Chat Fluency & Detection Hardening: closed the "redacted tokens" / "did you mean" / disease-name-as-org failure modes; rewrote `system_msg` preamble; threaded `system_msg` kwarg through Shield client + LLM router · `sprints/PHASE_14_CHAT_FLUENCY.md`.
- **Current operational state** (per `MODULE_PRODUCT_SPECS.md` §1 — Chat is module #1, not #2):
  - **UI routes**: `/app/chat` → `Chat.jsx`; `/app/chats/archived` → `ArchivedChats.jsx`; inline in `AppHome.jsx` (recent chats card).
  - **BE endpoints**: 13 routes under `/api/chats/*` + dual-mount `/v1/akki/chats/*` (GET/POST/PATCH/DELETE per route; messages/stream + attach + audit + audit/export.zip + governance/solva-escalation-clicked; `/api/chat/models`; `/api/admin/chat-retention/sweep`; `/api/streaming/v9/*`).
  - **Owning context**: Akki (orchestration/persistence/UI). Every turn calls SyniSense `shield_invoke(...)` — the only outbound path to LLMs (Anthropic Claude Sonnet 4.5 via Emergent LLM Key).
  - **Integrations**: `get_synisense().shield_invoke` + `issue_trust_receipt` + `get_shield_audit_by_chat`; `get_akki().mark_solva_escalation_clicked`; quota gating via `services/llm_quota.py`.
  - **Known debt**: 6 `/api/chats/*` endpoints still `Optional[Dict[str, Any]]` with `# phase-3.0:narrow-in-3.1` marker (Phase 5.2 Part B partial narrowing); streaming Shield UI parked in Trust Center; per-tenant retention policy lacks central admin UI.
- **Planned next track (consumer-grade redesign) — Phase B0 CLOSED 2026-06-24:**
  - **B0 verdicts** (all 6 probes resolved — full report at `sprints/PHASE_B0_CHAT_PREREAD.md`):
    - **Fidelity matrix**: text PASS · PNG PARTIAL · PDF PARTIAL · DOCX PARTIAL · XLSX PARTIAL · image-with-text PARTIAL. All modalities pass through shield via text-extraction (`documents_service.py::extract_text`); no FAIL, no raw-leak; multimodal "model sees image directly" NOT supported.
    - **Streaming-reidentify**: **EXISTS** — `StreamingReidentifier` at `reidentifier.py:178-333` + wired in chat.py:3187 (`messages/stream`). Per-chunk inversion proven.
    - **Emergent proxy / keys**: **PROXY FRONTS ALL THREE** — Claude/OpenAI/Gemini all proxied via `litellm` + `EMERGENT_LLM_KEY` per `llm_router.py:140-200`. Two-day feature confirmed.
    - **In-org retrieval (RAG)**: **EXISTS BUT BM25-only + invocation-driven** — Phase 11 ITEM C `_retrieve_grounding_paragraphs` at `chat.py:1505-1596`. Tenant-scoped via membership check. Citation-pinned via `[[cite:<anchor>]]` markers. NOT model-tool-call driven; NOT vector-embedded.
    - **Tool-calling carriage**: **MISSING** — shield's `invoke_with_metering` signature has no `tools=` parameter; no `tool_use` references anywhere in `services/synisense/shield/`. Manual affordance becomes the honest interim per locked product call.
    - **Work Studio actual state**: **AMBIGUOUS** — BE code (6 routers, ~4,400 LOC) + module spec (Live) + 6/8 BE tests passing contradict user's "most document generation not working" claim. Verifiable from read-only BE inventory: routers + FE pages exist, tests largely green. User-supplied UX reproduction steps needed for further triage.
  - **Locked decisions** (carried into B1+): sub-300ms first-token latency bar · providers = Claude + OpenAI + Gemini (no long tail) · in-org retrieval trigger = model-tool-call with explicit-attach fallback (no intent classifier) · Work Studio fix-first then model-tool-call (manual affordance interim) · NO SyniSense tokenization change in scope · Shield as ONLY outbound path.
  - **Next dispatch:** B1 — sized per B0 verdicts. Best case: 3 phases (provider routing → manual Work Studio + retrieval affordance → tool-call carriage as a Shield sub-phase). Per B0's honest scope estimate.
  - **Then:** B2-B3 as B0 returns honest scope per the 3-scenario sizing.

### 3.4 Track Work Studio — runtime classification (parallel)
- **Status:** WS1 CLOSED 2026-06-24. WS0 classification + WS1 repair pass both shipped.
- **WS1 verdict (post-repair, execution evidence):**
  - **All 6 generation kinds reach `/export`** end-to-end (brief / deck / report / minutes / **committee_pack** / **board_pack**). Both new kinds verified to download as real DOCX (38 777 + 39 835 bytes, ZIP magic `504b0304`, correct OpenXML MIME).
  - **Overlay** reclassified to **WORKS** — list + get round-trip on same id round-trips green. WS0 verdict was a test-time misclassification (id picked from `db.documents` table, not `db.work_studio_exports`).
  - **Render (compile-then-render)** classified as **WORKS** — `/contexts/{cid}/work-studio/documents/{aid}/render?format={fmt}` on an artefact with non-empty `structured_content.sections`: DOCX (36 650 bytes), PPTX (29 085 bytes), PDF (1 631 bytes) all green.
- **Files touched (product code):**
  - `backend/routers/work_studio_export.py` — `_VALID_KINDS` extended to 6 kinds; `_AUTO_FORMAT["board_pack"]="docx"`; `_ENHANCE_KINDS` + `_ENHANCE_ACCEPTED_EXT_BY_KIND["board_pack"]` added; start_export render dispatcher group at line 760 extended to `("report","minutes","committee_pack","board_pack")` (docx + pdf); Pass-2 schema_doc dict gained a `board_pack` entry; enhance render dispatcher gained `board_pack` docx + pdf branches for parity; synisense-breakdown allow-list + `surface_family` map extended to board_pack.
- **Cross-track Chat handoff sub-matrix (POST-WS1):** all 6 kinds now safe for B1.1 manual affordance via the single `/export/{kind}` route. No exception list.
- **WS0 sprint memo:** `sprints/PHASE_WS0_CLASSIFY.md` (classification).
- **WS1 sprint memo:** `sprints/PHASE_WS1_REPAIR.md` (repair pass).

## 4. Invariant Ladder Snapshot

| Layer | Invariant | State |
|---|---|---|
| Code: cross-context | `4_3_enforce_mode` 0 violations / 0 annotations | ✅ |
| Code: tenancy | enforce-mode | ✅ |
| Code: contract snapshot | 68 typed methods | ✅ |
| API: public path-list ratchet | `/api/* = cdcb23322bb82895` · `/v1/* = acc51822aa8818ae` · combined `ca9429c64e44570c` | ✅ |
| API: dual-mount byte-equivalence | 45/45 routes | ✅ |
| API: SDK slice consistency | 4/4 slice ↔ live OpenAPI | ✅ |
| FE hygiene | no-raw-axios (codemod 001 enforced) | ✅ |
| BE hygiene | polymorphic-response-ratchet (42 remaining, shrinking) | ✅ |
| Test hygiene | no-silent-skips (AST scan) | ✅ |
| Schema correctness | first-session-response-shape + http-transport-pydantic-kwargs + chat-streaming-reidentify-present | ✅ |
| Schema correctness | shield-no-leak (3 providers · deliberate-violation rail · 7 default-lane tests + 4 integration-marked) | ✅ |
| Deploy | deploy-smoke present (CI gate) | ✅ |
| CI gates | codemod-drift + dep-audit-strict + invariants.yml + backend-tests.yml (scoped) | ✅ |
| CI gates | pipeline-log-sync (sprint memo ↔ DEV_PIPELINE §9 row consistency) | ✅ |
| Repo hygiene | committed dev-DB dumps scrubbed from history (`backup/` + `*.bson` blocked in `.gitignore`); AUDIT_P0 close-out 2026-06-24 | ✅ |
| CI hygiene | dep-audit-strict (pip + npm) + requirements-guard + gitleaks all provably GREEN under documented allowlists; AUDIT_P1 close-out 2026-06-24 | ✅ |
| Cross-tenant context isolation | every `{context_id}` route has a canonical membership gate or an audit-reviewed exception entry; hard ratchet at `tests/invariants/test_context_route_membership_gate.py`; Stage 1 close-out 2026-06-24 | ✅ |
| Tenancy escape register | explicit audited allowlist for all `untenanted=True` callsites (12) + `# tenancy:allow-no-account-id` markers (179); hard ratchet at `tests/invariants/test_tenancy_escape_hatch_allowlist.py`; Stage 1 close-out 2026-06-24 | ✅ |
| Engine vs surface name guard | `backend/` MUST NOT contain `thinklab` (case-insensitive); engine is Solva v2, ThinkLab is FE-only surface; hard ratchet at `tests/invariants/test_thinklab_uilabel_only.py`; Stage 1 close-out 2026-06-24 | ✅ |
| Function-based naming for Solva/Monitor families | no `_vN` suffixes in `services/solva*` or `routers/monitor*` (except grandfathered `solva_v2`); no legacy `services.solva` / `routers.monitor` / `routers.monitor_v2` imports; hard ratchet at `tests/invariants/test_no_legacy_solva_monitor_names.py`; Stage 3 close-out 2026-06-24 | ✅ |
| Decisions+sequence | `SPRINT_PLAN.md` — canonical for sprint goal · tracks · sequence · protocols · locks · agreements · mixups | ✅ |
| **JC-WS spec (Work Studio)** | `JC_WS_CANONICAL_SPEC.md` — canonical source of truth for Document Generation + Analyze; UI-untouched hard rule pinned 2026-06-25 | ✅ |
| **JC-WS UI inventory** | `audit/JC_WS_ui_inventory.md` — 5 journeys × N surfaces classified EXISTS-TODAY vs MISSING; 7 truly-missing items surfaced for user direction | ✅ |

## 5. Surface Ratchet

| Slice | Paths | Ops | sha256:16 |
|---|---:|---:|---|
| `/api/*` | 621 | 697 | `cdcb23322bb82895` |
| `/v1/*` | 619 | 695 | `acc51822aa8818ae` |
| Combined | 1240 | 1392 | `ca9429c64e44570c` |

Held since Phase 4.1 close.

## 6. External Blockers (User Action — Not Code)
- **TL Flag 3 (P0 right now):** reference deck anchor — (a) most-recent admin@akki.ai `solva_v2_sessions` row [default] · (b) specific session ID · (c) push back on framing → two-track ThinkLab + Decks-upgrade
- **Platform supervisor unlock:** only blocks in-place multi-process activation; containerised path via Phase 5 artefacts is ungated
- **GitHub branch-protection wire-up:** mark deploy-smoke / dep-audit-strict / codemod-drift / no-silent-skips / invariants / backend-tests as required checks
- **Live Stripe key:** productionises billing
- **GCP OAuth client ID + secret:** unblocks Google sign-in (G2)

## 7. Gated Phases (Trigger Conditions)
- **Phase 6** — Physical data carve · GATED on scale or signed sale
- **Phase 7** — Commercial surfaces · GATED on first paying customer

## 8. Parked (Pick Up When User Calls)
- **Phase 5.5.3 / candidate C** — broader-suite drift triage (~7+ unrelated test files) + full-tree `backend-tests.yml` CI lane expansion
- **Phase 5.6+** — BE polymorphic narrowing batches 2-N (each batch ~5-10 routes; ratchet currently 42)
- **`INVARIANT_HEALTH.md`** dashboard — status aggregation observability (not enforcement)

## 9. Phase History (Reverse Chronological)

> Sort order: **reverse chronological by ship date** (most recent first). Phases without an explicit ship date in MASTER_STATE are listed in the order they appear in MASTER_STATE §4.

| Phase | Closed | Summary | Sprint Memo |
|---|---|---|---|
| STAGE_5 | 2026-06-24 | FE shell verification (Task Manager / Monitor / Pulse) — STOP gate: "a backend a frontend needs doesn't actually work at runtime." Not tripped. 7 new live-call e2e tests in `tests/test_stage_5_fe_shell_backends.py` confirm `/api/tasks/counts` + `/api/tasks` (Task Manager top counts + list), `/api/contexts/{cid}/monitor` (dashboard composer at `monitor_dashboard.py`), `/api/contexts/{cid}/monitor/{kind}` (objective + project list at `monitor_strategic_items.py`; valid `_KIND` is `("objective","project")`), `/api/contexts/{cid}/monitor/owner-roles`, `/api/contexts/{cid}/pulse/feed`, `/api/contexts/{cid}/pulse/across-boards?window_days=30&limit=10` — all return 200 for an authenticated context-member on a fresh seed. Pattern: `httpx.AsyncClient + ASGITransport + @pytest.mark.asyncio`. 57 pre-existing surface tests across the 3 shells (`test_phase_aa_slice_1_tasks_initiatives.py`, `test_track_b_phase2_task_lifecycle.py`, `test_wave4_task_listing.py`, `test_patch_5_monitor_v2.py`, `test_monitor_v1_compat.py`, `test_phase_aa_slice_4_monitor.py`, `test_monitor_drawer_*`, `test_p1_a_intel_to_pulse.py`, `test_patch_6_pulse_synisense.py`) confirmed GREEN at this commit. Stage 3's function-based router renames hold cleanly — FE only references URL paths (unchanged), never Python module names. Combined regression sample: 170 passed / 10 skipped (all skips are pre-existing HUMAN_REQUIRED + deliberate-violation-smoke). Full Runway dispatch closes here. | `sprints/STAGE_5_FE_SHELL_VERIFICATION.md` |
| STAGE_4 | 2026-06-24 | Work Studio end-to-end. **4.2** (`e0fb89b2`): chat Work Studio affordance auto-picks the best-fit kind from the captured objective via a pure-JS regex pipeline (zero net-new LLM calls); ordered high → low confidence (board_pack > committee_pack > minutes > deck > report > brief). Heuristic lives in `frontend/src/components/chat/workStudioRecommender.js` and is consumed by `WorkStudioAffordanceModal.jsx`. UI surfaces a `Suggested` pill on the matching tile + a quiet reason line; user click flips `userPickedKind` so the recommender stops auto-overwriting their choice. 21 jest unit cases (empty input, null safety, every kind path, freeform fallback, priority order). **4.3** (`edc278fe`): Solva v2 Analyze narration now lands in DOCX / PPTX / XLSX report exports. The pre-Stage-4.3 `_adapt_new_analysis_to_workbook_analysis` was a Phase-1 shim that dropped synthesis data on the floor (explicit comment: "Phase 3 will replace this shim"); synthesize landed in Phase 3 but the adapter never got the update. Fix: 3-layer wiring — `WorkbookAnalysis` schema +2 optional carriers (`analyze_narration_headline` / `analyze_narration_observations`), adapter reads them from `row.headline` + `row.observations` (mirrors `runs[-1]` cached by synthesize_v2), and the 3 report builders inject a `Bottom Line` section (DOCX heading + paragraphs; PPTX slide; XLSX sheet at position 0) carrying the headline + observations with their cell-range citations. Branching is gated on `analyze_narration_headline` being non-empty so the legacy `wba-*` pipeline stays byte-identical. 4 e2e tests (DOCX / XLSX / PPTX content + pre-synthesis regression) on the `httpx.AsyncClient + ASGITransport + @pytest.mark.asyncio` pattern so the test client lives on conftest's session loop. Tenancy allowlist line-numbers refreshed for the 3 markers in `workbook_analysis.py` (L294→323, L724→753, L726→755). FE caveat copy on `AnalyzeDrawer.jsx` Export tab refreshed (was "Solva narration arrives in Phase 3"; now reflects the now-shipped Bottom Line carriage). Affected-test sample: 98/98 invariants + Stage 4.3 tests GREEN; 52/52 workbook + analyze_narration + stage_4 tests GREEN. Zero rename / Stage-4-induced regressions. | `sprints/STAGE_4_WORK_STUDIO.md` |
| STAGE_3 | 2026-06-24 | Function-based renames (Option C; user verbatim: "name by function, kill every v1/v2 implication"). `services/solva` → `services/solva_voice_audit` (captures the voice-tier + audit-panel-timeline capabilities vs the parallel `services/solva_v2`). `routers/monitor.py` → `routers/monitor_dashboard.py` (the function-aware dashboard composer). `routers/monitor_v2.py` → `routers/monitor_strategic_items.py` (the objectives/projects/tasks/initiatives CRUD; misleading "_v2" suffix dropped). 26 files moved, 63 import callsites updated. Hard-ratchet invariant `tests/invariants/test_no_legacy_solva_monitor_names.py` locks the new names (3 sub-tests). Commits: 2063f12a (inventory+STOP) + 7fcdb587 (solva) + 95ae06ba (monitor) + f8a91624 (invariant). Affected-test sample: 110 passed / 7 pre-existing failures (6 Synisense HTTP timeouts environmental + 1 unmounted-router check pre-existing). Zero rename-induced regressions. | `sprints/STAGE_3_FUNCTION_RENAMES.md` |
| STAGE_2 | 2026-06-24 | Verification-only pass. **Remote scan**: 4/4 branches (main + 3 github_actions dependabots) CLEAN_TREE + CLEAN_LOG. **Audit lanes**: pip-audit GREEN (0 REAL of 7 vulns, MITIGATED via IGNORED_VULNS); yarn audit GREEN (0 HIGH/CRITICAL of 40 vulns, 1 613 deps); requirements-guard OK (0 offenses); gitleaks GREEN (733 commits, 0 findings); pipeline-log-sync GREEN (102 memos, 34 §9-matched, 68 legacy). 10 commits ahead of remote (user push pending). | `sprints/STAGE_2_CLEAN_BOARD.md` |
| STAGE_1 | 2026-06-24 | Security ratchet (P2.1 + P2.2 + P2.4). **P2.1** (`adbecd3f`): `strategic_goal_evolution.py` Depends-swap from `get_current_account` → `require_context_membership()`; CVE-class IDOR closed. FE caller analysis SHOWN (only runtime caller `StrategicGoalsPanel.jsx:554` sources `contextId` from `useAuth().activeContext.id` ↔ `/api/me/contexts` membership list, boot-guarded). Security claim SHOWN via new dedicated test (non-member call → 403, no leaked title in body). **P2.2** (`5cbd948f`): two new build-breaking invariants — `test_context_route_membership_gate.py` (HARD RATCHET on `{context_id}` routes, 21 audit-derived exceptions in `context_route_membership_allowlist.yml`) + `test_tenancy_escape_hatch_allowlist.py` (12 `untenanted=True` callsites + 179 `# tenancy:allow-no-account-id` markers explicitly allowlisted with file:line + justification in `tenancy_escape_allowlist.yml`). **P2.4** (`280b4549`): `test_thinklab_uilabel_only.py` — case-insensitive scan of `backend/` for `thinklab`, hard ratchet at 0 hits, no allowlist; FE deliberately allowed. All 9 new invariant tests GREEN in <10 s. | `sprints/STAGE_1_SECURITY_RATCHET.md` |
| AUDIT_P1 | 2026-06-24 | CI lane greens (5/5 tasks, strict report-only / zero product code): `frontend/yarn.lock` committed (14 160 lines / 662 KB; `yarn install --frozen-lockfile` deterministic); pip-audit verified GREEN under existing CI IGNORED_VULNS (7 litellm CVEs MITIGATED via SECURITY_EXCEPTIONS.md, 0 REAL); `backend/requirements.txt:34-35` annotated with `# ci-requirements-guard: allow spacy-models-via-github-release` (guard exit 1→0; self-test 8 passed / 1 legacy-skipped); yarn audit verified GREEN under `--level high` (0 HIGH/CRITICAL / 1 613 deps; 16 Low + 24 Moderate below threshold); `.gitleaks.toml [allowlist].paths` extended with `^memory/sprints/.*\.md$` + `^memory/audit/.*\.md$` + `^docs/PRODUCT_REVIEW\.md$` (full-history `gitleaks detect` 5 findings → 0). Commits: 8b6b7fc7 + 9a3c6c97 + f944f365. Honest extension: P1.5 added a third allowlist path (`memory/audit/...`) beyond the dispatch's two because AUDIT_P0 created that directory between spec and execution. | `sprints/PHASE_AUDIT_P1.md` |
| AUDIT_P0 | 2026-06-24 | Committed dev-DB dumps purged from git history (`git filter-repo --path backup/ --invert-paths --force`): 3 561 tracked files across 15 snapshot dirs removed (1 022.9 MiB on disk; 49 MiB packfile reclaimed). `.gitignore` extended to block re-commit. CI lane triage produced — zero REAL failures, 2 RED lanes (requirements-guard, gitleaks) classified as POLICY/allowlist polish for P1. Exposure report + CI triage at `memory/audit/`. | `sprints/PHASE_AUDIT_P0.md` |
| B1.1 | 2026-06-24 | Chat manual Work Studio affordance: composer toolbar "Create" button → modal with all 6 generation kinds + mechanically-prefilled description / objective / scope from live conversation; handoff to WS1-uniform `/api/contexts/{ctx}/work-studio/export/{kind}`. Chain green: 38 891-byte DOCX with valid ZIP magic. Prefill is pure JS — zero net-new LLM calls. New component `WorkStudioAffordanceModal.jsx`. | `sprints/PHASE_B1_1_CHAT_WS_AFFORDANCE.md` |
| WS1 | 2026-06-24 | Work Studio repair pass: all 6 generation kinds now reach `/export` (committee_pack dispatcher branch + board_pack added to `_VALID_KINDS` + Pass-2 schema_doc + enhance + synisense-breakdown parity); committee_pack DOCX 38 777 bytes + board_pack DOCX 39 835 bytes verified end-to-end with correct ZIP magic + MIME. Overlay reclassified to WORKS (WS0 was a test-time misclassification — id picked from `db.documents`, not `db.work_studio_exports`). Compile-then-render smoke green for DOCX/PPTX/PDF on an artefact with non-empty structured_content. Chat B1.1 handoff matrix: 6/6 kinds safe. | `sprints/PHASE_WS1_REPAIR.md` |
| WS0 | 2026-06-24 | Work Studio runtime classification (read-only + execution-based, no product code touched): 8-capability matrix produced; 4 generate-kinds WORK (brief/deck/report/minutes), 1 BROKEN-AT-SEAM (committee_pack render dispatcher), 1 DEFERRED via `/export` (board_pack); Phase-C/C2 WORKS, overlay RUNS-BUT-AMBIGUOUS, render AMBIGUOUS (needs compile-then-render smoke), Analyze spreadsheet-only confirmed; objective→content TRUE, objective→kind FALSE; AnalyzeDrawer Phase-3 = CLEAN-PLACEHOLDER | `sprints/PHASE_WS0_CLASSIFY.md` |
| B1 | 2026-06-24 | Chat consumer-surface build: grouped two-level provider→version model picker on `/app/chat`; build-breaking AST invariant on `StreamingReidentifier` wire-up; shield-no-leak generalised across Claude/GPT/Gemini + deliberate-violation rail (7 default-lane tests); pre-B1 FE regressions repaired (`tsconfig.json` + `SessionTimeoutGuard.__raw`) | `sprints/PHASE_B1_CHAT_BUILD.md` |
| SPRINT_PLAN_INIT | 2026-06-24 | `SPRINT_PLAN.md` established as canonical decisions+sequence source (8 sections: sprint goal · tracks · sequence · protocols · locks · agreements · mixups · external action items); zero overlap with `DEV_PIPELINE.md` (live state) and `MASTER_STATE.md` (history) per §0 role boundary | `sprints/PHASE_SPRINT_PLAN_INIT.md` |
| B0 | 2026-06-24 | Chat consumer-grade redesign pre-read: 6 probes resolved (fidelity matrix, streaming-reidentify EXISTS, proxy fronts all 3, RAG BM25-exists, tool-call MISSING, Work Studio ambiguous); honest B1+ scope sized across 3 scenarios | `sprints/PHASE_B0_CHAT_PREREAD.md` |
| Pipeline-Log-Sync | 2026-06-24 | Sprint-memo ↔ DEV_PIPELINE §9 row consistency CI gate; first dogfooded by this entry | `sprints/PHASE_PIPELINE_LOG_SYNC.md` |
| TL0 | 2026-06-24 | ThinkLab pre-read; Gates A (PARTIAL) + B (GREEN) + layer-order SHARED; 3 stop-and-report flags surfaced | `sprints/PHASE_TL0_THINKLAB_PREREAD.md` |
| 5.5.2 | 2026-06-24 | Track A real closure; 2 production bug fixes (StateOnlyResponse + HTTP transport Pydantic kwargs); 86/86 quarantined unlocked end-to-end | `sprints/PHASE_5_5_2_TRACK_A_REAL_FIXES.md` |
| 5.5.1 | 2026-06-24 | 62/86 unlocked + 24 honest-skip with named candidates | `sprints/PHASE_5_5_1_TRACK_A_CLOSURE.md` |
| 5.5 | 2026-06-24 | Codemod CI gate + Track A iter-1 (3 fixed + 5 files quarantined) | `sprints/PHASE_5_5_CODEMOD_CI_AND_TRACK_A_TRIAGE.md` |
| 5.4 | — | Narrowing batch 1 (49→42 routes) + dep-audit strict CI gate | `sprints/PHASE_5_4_NARROWING_BATCH_1_AND_AUDIT_STRICT.md` |
| 5.3 | — | Dep-audit remediation (46/53 pip CVEs + 29/29 npm HIGH+) + codemod institutionalisation | `sprints/PHASE_5_3_DEP_AUDIT_AND_CODEMOD.md` |
| 5.2 | — | Debt close (314 FE migrations + invariant ratchets) + 7-module product specs | `sprints/PHASE_5_2_DEBT_CLOSE_AND_MODULE_SPECS.md` |
| 5.1 | — | Deploy boot smoke as operational invariant | `sprints/PHASE_5_1_DEPLOY_SMOKE.md` |
| 5 | — | Sell-ready package (SDK slices + Dockerfiles + compose + K8s skeletons + cron split + TS SDK + partner onboarding) | `sprints/PHASE_5_SELL_READY.md` |
| 4.4 | — | Dual-mount `/v1/{context}/*` versioned surface (1240 paths total; 37/37 byte-equivalence smoke) | `sprints/PHASE_4_4_DUAL_MOUNT.md` |
| 4.3 | — | Container topology + healthcheck triad + final 5-hatch dissolution + http default flip | `sprints/PHASE_4_3_TOPOLOGY.md` |
| 4.2 | — | HTTP transport + typed adapters + 53/58 hatch dissolution | `sprints/PHASE_4_2_HTTP_TRANSPORT.md` |
| 4.1 | — | Three FastAPI app entrypoints + 134 router redistribution | `sprints/PHASE_4_1_THREE_APPS.md` |
| 14 | 2026-06-05 | Chat Fluency & Detection Hardening — closed Claude "redacted tokens" / "did you mean" / disease-name-as-org failure modes; rewrote system_msg preamble; threaded kwarg through Shield client + LLM router | `sprints/PHASE_14_CHAT_FLUENCY.md` |
| H2.5 | 2026-05-24 | Streaming PII fix + audit-integrity invariant — closed 3 P0s from H2 audit + audit-integrity violation surfaced by independent verifier | `sprints/H2_5_STREAMING_PII_FIX_STATE.md` |
| H2 | 2026-05-24 (read-only) | Shield Uniformity Audit — forensic check that LLMs never see confidential data + Shield-always-on across roles/surfaces; surfaced P0 caveats → H2.5 | `sprints/H2_SHIELD_UNIFORMITY_AUDIT.md` |
| F | 2026-05-21 | Akki Chat boundary-removal pass — chrome refinement only, no palette/typography/IA changes | `sprints/PHASE_F_CHAT_BOUNDARY_STATE.md` |
| 5.10 | 2026-02-23 (fork-resume) | Chat resilience — production cancellation + audit-panel red error fix on `/app/chat` + `/api/chats/{cid}/messages/stream` | `sprints/P5_10_chat_resilience.md` |
| ... | — | (earlier phases per MASTER_STATE.md §8) | — |

## 10. QA Notes

_Free-form section for user to leave QA findings, follow-up asks, or observations. Orchestrator triages → either dispatches a fix or rolls into the next phase's brief._

<!-- USER QA ENTRIES START — append below this line -->

<!-- USER QA ENTRIES END -->

---
## Maintenance Protocol
- **Orchestrator** updates §1 Current State + §2 Active Dispatch + §3 track lines whenever a dispatch goes out or a phase closes.
- **Builder** updates §4 Invariant Ladder + §5 Surface Ratchet + §9 Phase History as part of each phase's close report. Builder must update before the phase-close summary is sent back.
- **User** appends QA findings to §10. Orchestrator triages within one orchestration turn.
- The file is treated as authoritative — if `MASTER_STATE.md` disagrees, this file wins for the live pipeline view; MASTER_STATE remains the comprehensive durable record.
