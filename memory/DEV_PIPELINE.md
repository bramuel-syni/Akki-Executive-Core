# Dev Pipeline & QA Log

> **Maintained by:** orchestrator + builder.
> **Updated at:** every dispatch + every phase close. Builder updates as part of phase-close deliverable.
> **For:** user QA review.

## 1. Current State

Track Chat — Phase B1.1 closed 2026-06-24. Manual Work Studio affordance live on `/app/chat`: composer toolbar "Create" button opens a modal with all 6 kinds (brief/deck/report/minutes/committee_pack/board_pack) + mechanically-prefilled description (last 6 turns) / objective (last user message) / scope (context + chat title). Handoff to the WS1-uniform `/api/contexts/{ctx}/work-studio/export/{kind}` route. End-to-end chain verified: modal payload → `export_id=7fd6da82` → COMPLETE → 38 891-byte DOCX with valid ZIP magic. Prefill is 100% pure JS — zero net-new LLM calls (static code audit confirms only 3 network calls in the modal, all gated behind explicit user actions: Create / poll / Download). Disabled-out-of-org tooltip surfaces honestly. ThinkLab Gate A still queued.

## 2. Active Dispatch

None — B1.1 closed. ThinkLab Gate A render-check + Flag 3 verification is next per consolidated dispatch queue.

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
| Decisions+sequence | `SPRINT_PLAN.md` — canonical for sprint goal · tracks · sequence · protocols · locks · agreements · mixups | ✅ |

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
