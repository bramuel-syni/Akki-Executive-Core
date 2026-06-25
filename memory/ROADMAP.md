# AKKI Sandbox — Roadmap

> Prioritised backlog of remaining product work.
> See `/app/memory/SYSTEM_STATE.md` §7 for tech debt.

## P0 — Active dispatch (THREE PARALLEL STREAMS · STOP-AND-SHOW pending user sign-off)

1. **JC-MON Stage 2a** — CLOSED 2026-06-25 (5/5 acceptance rows GREEN).
   Awaits user STOP-show approval before Stage 2b widening.
2. **JC-CHAT Stage A** — CLOSED 2026-06-25 (4 markers removed + 1
   hidden + Privacy-report relocated + a11y migrated). Awaits user
   STOP-show approval before Stage B parity measurement.
3. **JC-TL Stage 0** — CLOSED 2026-06-25 (deck-gate verdict + probe
   provenance verdict). Awaits user decision on Track-2 (Decks
   upgrade) dispatch sequencing + Stage 1 (Diagnosis proving slice)
   start.

## P0 — Next stages (queued, gated on user STOP-show approvals above)

1. **JC-MON Stage 2b** — widen engine on the proven slice ONE-AT-A-TIME
   per quality bar: (a) recommendations / interventions, (b)
   explanation of performance, (c) extended health beyond RAG.
2. **JC-MON Stage 3** — two-section experience (objectives + tasks)
   + drawer-by-context + email-update loop additive on TM.
3. **JC-CHAT Stage B** — LLM experience parity measurement: R1 trace
   (frontend-fixable vs Shield-path), R2 streaming method, R3 latency
   table. Produces `audit/JC_CHAT_parity_report.md`. NO Shield mods.
4. **JC-CHAT Stage C** — completion punch-list (rename / restore /
   permanent-delete; edit-prompt R5 verbatim-report).
5. **JC-TL Stage 1** — Diagnosis proving slice (entry surface + 4-way
   picker + material attach + guided conversation + session record +
   deck-grade artefact measured against MYDAWA via Q2 rubric).
6. **JC-TL Stage 2** — fan-out to Develop Strategy + Test Hypothesis
   on Track 1; Get-Perspectives gated on Track 2.

## P0 — Separate dispatches surfaced this stream

1. **JC-TL Track 2 — Decks upgrade for divergent rendering**
   (surfaced 2026-06-25 by JC-TL S0-Q2 verdict). Minimum scope:
   `perspective_spread` schema slot + divergent pptx builder +
   path-aware Pydantic validator. Does NOT block JC-TL Stage 1.

## P0 — Pre-existing blocking items

1. **Deployment blockers (5)** — original audit items, not yet triaged.

## P1 — Next sprint candidates (parked)
1. **JC-UI-DRAWER** — system-wide drawer-width standard across 4
   modules (TaskDrawer / WorkStudio analyze / Monitor objective
   drawer / Document Journal preview). Separate one-line dispatch
   when user invokes JC-UI-DRAWER directly.
2. **LLM_MODELS_REFRESH** — refresh the model selection across
   Shield-routed LLM call paths; produce a model-selection matrix
   before changing anything; verify behind Shield.
3. **Brief Akki-fetch retrieval upgrade** — author/owner metadata
   indexing + temporal filtering + confidence floor; retest 3 named
   cases; ship only when ≥ 2/3 RELEVANT.
4. **Origin-triggered Briefs** — per-module "brief this" affordances
   on Solva / Monitor / Task Manager origin surfaces.
5. **Analyze deep-link — wire to deterministic analyzer payloads**
   for `/forecast` / `/simulate` / `/anomalies` / `/signals/extract`.
6. **Streaming UX retrofit** — convert Solva / Cycle compilation /
   Work Studio Enhance endpoints to SSE streams emitting `phase`
   events; then adopt `StreamingShell` on those surfaces.
7. **Objectives & Projects — ExCo-member chips + KPI chips** —
   the Monitor v2 brief's second filter row above the R/A/G tabs.
8. **Real calendar integration on Home 1** — replace empty-state
   calendar peek with real cycle + compilation cadence aggregation.
9. **7-insight cards — wire missing counts** — `cycles_closing_this_week`
   needs `expected_close_at` on cycle docs; `open_questions` needs
   `cycle_questions.assignee_account_id`.

## P2 — Polish and productisation
1. **Real news integration** for Home 1 — replace `mock_news.json`.
2. **Agent Cycle — real AI engine** — wizard Step 3 preview is
   deterministic; upgrading to an LLM-generated briefing is a future
   product decision.
3. **Real template library** for Compilation Wizard Step 1 — currently
   a single "Standard" template per artefact type.
4. **Unskip legacy test suites** — roughly 65 files quarantined in
   Patch 8; reintroduce them one at a time as their fixtures / schema
   are modernised.
5. **Marketing JS bundle code-split** — deferred.
6. **Pydantic v2 migration** — `.dict()` → `.model_dump()` sweep on
   new routers.
7. **Legacy Home components (`HomeExecutive/Ned/Dual`)** — delete
   after a full visual-parity audit against Home 2.

## P3 — 3rd-party integrations (PLANNED)
- Stripe
- Azure stack
- ClamAV
