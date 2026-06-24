# Dev Pipeline & QA Log

> **Maintained by:** orchestrator + builder.
> **Updated at:** every dispatch + every phase close. Builder updates as part of phase-close deliverable.
> **For:** user QA review.

## 1. Current State

Builder idle. Awaiting user Flag 3 (ThinkLab reference deck anchor) decision before TL1.1 dispatch.

## 2. Active Dispatch

None — TL0 closed 2026-06-24. Builder idle. Awaiting orchestrator's TL1.1 brief.

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

### 3.3 Track Chat — Consumer-Grade Chat UX (parallel product track)
- **Current state:** B0 queued behind TL1.2 close
- **Locked decisions:** sub-300ms first-token latency bar · providers = Claude + OpenAI + Gemini (no long tail) · in-org retrieval trigger = model-tool-call with explicit-attach fallback (no intent classifier) · Work Studio fix-first then model-tool-call (manual affordance interim) · NO SyniSense tokenization change in scope · Shield as ONLY outbound path
- **Locked B0 scope:** fidelity probe matrix (text/PNG/PDF/DOCX/XLSX/image-with-text → PASS/PARTIAL/DEGRADE/FAIL) + streaming-reidentify verification + Emergent proxy fronts all 3 providers confirm + in-org retrieval mechanism inventory + Work Studio actual-state probe
- **Next dispatch:** Chat B0 (read-only) — fires after TL1.2 closes
- **Then:** Chat B1+ sized at ~3-4 phases after B0 returns honest scope
- **Sprint memos:** [none yet]

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
| Schema correctness | first-session-response-shape + http-transport-pydantic-kwargs | ✅ |
| Deploy | deploy-smoke present (CI gate) | ✅ |
| CI gates | codemod-drift + dep-audit-strict + invariants.yml + backend-tests.yml (scoped) | ✅ |

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

| Phase | Closed | Summary | Sprint Memo |
|---|---|---|---|
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
