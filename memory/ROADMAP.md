# AKKI Sandbox — Roadmap

> Prioritised backlog of remaining product work.
> See `/app/memory/SYSTEM_STATE.md` §7 for tech debt.

## P0 — Active dispatch state (post-autonomous-run 2026-06-25)

**7 stages cleared overnight; 1 HALT-AND-SURFACE.**

1. **JC-MON Stage 2a** — ✅ CLOSED 2026-06-25.
2. **JC-MON Stage 2b.1 (recommendations)** — ✅ CLOSED 2026-06-25.
3. **JC-MON Stage 2b.2 (explanation)** — ✅ CLOSED 2026-06-25.
4. **JC-MON Stage 2b.3 (extended health)** — ✅ CLOSED 2026-06-25.
5. **JC-MON Stage 3 (Two-section UX + Email loop + Origin-triggered
   Briefs fold-in)** — 🟡 HALT-AND-SURFACE per HALT condition #7
   (scope ambiguity). Three ambiguity points surfaced. Two clean
   sub-slices (3.0 Reassess action + 3.1 task-drawer
   `objective_id` discriminator) proposed if user wants progress
   before full scope clarification.
6. **JC-CHAT Stage A** — ✅ CLOSED 2026-06-25.
7. **JC-CHAT Stage B (parity measurement)** — ✅ CLOSED 2026-06-25.
8. **JC-CHAT Stage C (punch-list verify-then-close)** — ✅ CLOSED
   2026-06-25.
9. **JC-TL Stage 0 (gates)** — ✅ CLOSED 2026-06-25.
10. **JC-TL Stage 1 (Diagnosis proving slice)** — ✅ CLOSED 2026-06-25.
11. **JC-TL Stage 2 (fan-out 3 paths + Contributor-history fold-in)** —
    ✅ CLOSED 2026-06-25.

Full handoff note: `/app/memory/AUTONOMOUS_RUN_2026-06-25.md`.

## P0 — Next actions awaiting user

1. **JC-MON Stage 3 scope clarification OR clean sub-slices approval**
   (3.0 + 3.1). See halt note for the three ambiguity points.
2. **JC-TL Track 2 (Decks upgrade) sequencing decision** — agent
   recommendation: dispatch AFTER JC-MON Stage 3, BEFORE
   Get-Perspectives ship. See
   `jc_artifacts/JC-TL/02-fan-out/track-2-decks-upgrade-sequencing.md`.
3. **JC-CHAT C.4 (edit-prompt R5)** — three user options surfaced;
   user picks keep-populate-composer / in-place / branching.

## P0 — Separate dispatches surfaced this stream

1. **JC-TL Track 2 — Decks upgrade for divergent rendering**
   (surfaced 2026-06-25 by JC-TL S0-Q2 verdict). Minimum scope:
   `perspective_spread` schema slot + divergent pptx builder +
   path-aware Pydantic validator. Does NOT block JC-TL — Stage 2
   shipped Get Perspectives at Q6 provisional bar.

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
