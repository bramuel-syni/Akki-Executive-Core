# Stage 3.1 — Canonicalization Inventory (and STOP rationale)

**Date:** 2026-06-24
**Dispatch:** AKKI Full Runway, Stage 3 — "Canonicalize the two half-migrations" (v2 canonical, delete v1).
**Status:** 🛑 **STOPPED at inventory pass.** Both Solva and Monitor turn out NOT to be v1/v2 of the same engine — they are TWO DISTINCT FEATURES per family that share a directory prefix. Deleting "v1" in either family will break production FE.

The dispatch's STOP condition triggers: *"STOP only if: v2 is genuinely missing a capability v1 has. Name it explicitly. Report before deleting."*

I am reporting before deleting.

═══════════════════════════════════════════════════════════════════
## Solva inventory

### Two distinct architectures, both in production

| Aspect | `services/solva/` (the "v1" per the dispatch) | `services/solva_v2/` (the "v2" per the dispatch) |
|---|---|---|
| Self-description (from its own docstring) | "Solva — **Phase D** production reasoning module" (2026-05-13) | "Solva v2 — production reasoning surface (post Phase A cutover)" |
| Cross-reference (what each says about the other) | "Sits **alongside** the legacy `services/solva_v2/` package which continues to serve the existing UI routes" | "Solva v2 is the **only** Solva. The legacy `account.solva_v2_poc` flag was retired in Phase A; v1 POST endpoints have been removed" |
| State-machine layers | 5 (`Layer0` → `Layer4`) | 4 named (`framing → grounding → synthesis → reflection`), plus optional `hypothesis` |
| Sub-modules | `SUB_MODULES`, `LAYER_SEQUENCE`, `TERMINAL_STATES` | 4 named: `seek_clarity`, `develop_strategy`, `simulate_hypothesis`, `get_perspective` |
| Mongo collection for sessions | `solva_phase_d_sessions` | `solva_v2_sessions` |
| Router | `routers/solva_phase_d.py` (1430+ lines, 10+ endpoints) | `routers/solva_v2.py` (3100+ lines, 20+ endpoints) |
| URL prefix | `/api/contexts/{cid}/solva/v2/*` (context-scoped) | `/api/solva/v2/*` (account-scoped) |
| Voice tier | YES — `voice/question_bank.py`, `voice/synthesis_renderer.py`, `voice/refusal_voice.py`, `voice/invariants.py`. Single-voice invariant locked by tests. | NO — engines directly produce content, no separate "voice" layer |
| Engines | `reasoning/*`: `tension_detection`, `refusal_logic`, `probability_weighting`, `frame_audit_engine`, `triangulation_engine`, `candidate_generation`, `situation_class_classifier` | `engines/*`: `triangulation`, `frame_audit`, `refusal`, `tension_detector`, `reflection`, `probability_weighting`, `candidate_generation` (some overlapping names, NOT same code) |
| Telemetry handoff | YES — `services.solva.telemetry::record_handoff` (consumed by `chat.py:750`) | (handoff happens via `/api/solva/v2/sessions/{sid}/handoff/cycle` HTTP) |
| Export pipeline | NO — Phase D doesn't have one | YES — `pptx_exporter.py`, `payload_builder.py`, `artefact_schema.py`, `chair_notes.py`, `analyze_narration.py`, `citation_resolver.py` |
| Chat surface integration | NO — Phase D is its own surface | YES — `stream_schema.py`, `stream_synthesizer.py`, `chat_v2_*` for `/app/chat` |

### FE consumers of `services/solva/` (Phase D)

```
$ grep -rn -E '/api/contexts/[^/]+/solva/v2/' frontend/src
frontend/src/lib/solvaPhaseDClient.js                   :: 6 endpoint wrappers
frontend/src/components/chat/AuditPanel.jsx             :: audit-panel/timeline
frontend/src/components/solva/AttachDocumentModal.jsx   :: attach-document
```

3 active FE files. The `solvaPhaseDClient.js` is a thin wrapper exposing the Phase D session lifecycle (`createSession`, `getSession`, `submitFraming`, `submitAnswer`, `submitRefuse`, `listSessions`). The `AuditPanel` is the audit timeline drawer. The `AttachDocumentModal` is the document-attachment UI.

### Backend consumers of `services/solva/` (Phase D)

```
$ grep -rn -E 'from (backend\.)?services\.solva\.' backend/ | grep -v solva_v2 | grep -v /tests/
backend/routers/solva_phase_d.py        :: extensive (8+ imports)
backend/routers/solva_telemetry_admin.py :: services.solva.voice.question_bank::_resolve_variants
backend/routers/chat.py:750              :: services.solva.telemetry::record_handoff
backend/tests/test_phase_d_solva_pipeline.py :: extensive (test file, will move with implementation)
```

### Solva verdict

**The "v1/v2" framing is wrong.** What `services/solva/` (Phase D) and `services/solva_v2/` are is:
- TWO INDEPENDENT REASONING ARCHITECTURES added at different points in the product's life.
- Both currently shipped behind different FE surfaces.
- Each has capabilities the other lacks (voice tier ↔ export pipeline; 5-layer Phase D model ↔ 4-named-layer v2 model; context-scoped routes ↔ account-scoped routes).
- Deleting either DELETES PRODUCTION FUNCTIONALITY and active FE pages.

Specifically — deleting `services/solva/` ("v1" in the dispatch) would:
1. Break `frontend/src/lib/solvaPhaseDClient.js` and the 3 components that import it.
2. Orphan the `solva_phase_d_sessions` Mongo collection (likely has live tenant data).
3. Break `chat.py:750`'s handoff telemetry (`record_handoff` call).
4. Delete the single-voice invariant infrastructure (voice tier + invariants tests).
5. Delete the audit-panel timeline endpoint, breaking `AuditPanel.jsx`.

═══════════════════════════════════════════════════════════════════
## Monitor inventory

### Two distinct features, also both in production

| Aspect | `routers/monitor.py` (the "v1" per the dispatch) | `routers/monitor_v2.py` (the "v2" per the dispatch) |
|---|---|---|
| What it does | **Function-aware role-adaptive composer.** Returns a CEO/CFO/COO/Commercial/NED "what should I pay attention to right now" view composed across `signals`, `checklists`, `submissions`, `reports`, `briefings`, `documents`, `document_views`. | **Strategic items CRUD.** Manages `objectives`, `projects`, `tasks`, `initiatives` for the strategic-goals surface. Has auto-suggest endpoints (LLM-backed) + owner-role aggregations + standard CRUD. |
| Endpoint count | 1 (`GET /contexts/{cid}/monitor`) | 8 (`auto-suggest-*`, `owner-roles`, `{kind}` CRUD) |
| File size | 219 LOC | 530 LOC |
| Output shape | A composed dashboard payload (a list of items grouped by category, filtered by `function`) | Domain CRUD responses (lists / individual rows / mutations) |
| Mongo collections | Reads many existing collections (signals, checklists, reports, etc.). NO write-back. | Writes to a new `monitor_items` collection (kind=objective/project/task/initiative). |

### FE consumers

```
$ grep -rn -E '/contexts/[^/]+/monitor' frontend/src

LEGACY (monitor.py) — 1 caller:
  pages/Monitor.jsx:110
    api.get(`/contexts/${cid}/monitor`, { params: { function: fn } })

V2 (monitor_v2.py) — 2 callers:
  components/monitor/ObjectivesProjectsPanel.jsx:545
    api.get(`/contexts/${contextId}/monitor/owner-roles`)
  components/monitor/ObjectivesProjectsPanel.jsx:560
    api.get(`/contexts/${contextId}/monitor/auto-suggest-${kind}s`)
```

### Monitor verdict

`monitor.py` and `monitor_v2.py` are NOT v1/v2 of the same feature. They are:
- `monitor.py` → **the dashboard composer** (returns the function-aware "what to pay attention to" view).
- `monitor_v2.py` → **the strategic-items CRUD** (manages the new Objectives & Projects entity, an entirely different feature).

The "v2" in `monitor_v2.py` is misleading naming. Deleting `monitor.py` will break `Monitor.jsx`'s `loadDashboard` call at line 110 — the entire top dashboard payload on the `/monitor` page disappears.

═══════════════════════════════════════════════════════════════════
## What the user's pre-made decision actually entails

The dispatch said:
> *"DECISION ALREADY MADE BY USER: v2 is canonical, v1 is legacy — delete the v1 path.*
>  *Solva: keep `solva_v2`, remove `services/solva/`*
>  *Monitor: keep `monitor_v2`, remove `monitor.py` (and any legacy monitor path)"*

Executed literally, this means:
1. Delete `services/solva/` (4500+ LOC of Phase D engine + voice tier + telemetry).
2. Delete `routers/solva_phase_d.py` (1430+ LOC, 10+ endpoints).
3. Delete `frontend/src/lib/solvaPhaseDClient.js` and break 3 FE components.
4. Delete `routers/monitor.py` (219 LOC, 1 endpoint).
5. Break `pages/Monitor.jsx`'s top-dashboard data load.
6. Edit `chat.py:750` to drop the `record_handoff` call (no v2 equivalent — drops handoff telemetry).
7. Edit `solva_telemetry_admin.py:98` to drop the variant-resolver (no v2 equivalent).
8. Either delete or migrate the `solva_phase_d_sessions` Mongo collection (live tenant data).

This is a substantial *feature deletion*, not a *canonicalization*. The features being deleted have FE pages, live data, and an active per-domain mental model.

═══════════════════════════════════════════════════════════════════
## The architectural fork (genuine, per dispatch escalation criterion #2)

I cannot resolve this with the standing rules — it is a product-shape decision, not an engineering call. Branches:

### Option A — Honor the literal dispatch (delete v1)
- Delete Phase D entirely. Rewrite `AuditPanel.jsx` + `AttachDocumentModal.jsx` + `solvaPhaseDClient.js` to use `solva_v2` endpoints (which lack the equivalent capabilities; will need new v2 endpoints).
- Delete `monitor.py`. Either delete or recreate the function-aware dashboard composer somewhere.
- Migrate `solva_phase_d_sessions` data (if any sessions are live).
- Result: clean tree, missing features, substantial FE rewrite.

### Option B — Inverse the labeling (delete v2)
- Phase D's docstring says it's the newer architecture; v2's docstring says it's the only Solva. There IS no consistent v1/v2 axis.
- Theoretically the user could pick the OPPOSITE direction. But this would delete the export pipeline + chat surface integration + analyze narration in `solva_v2` — even more breakage.

### Option C — Rename, don't delete (the actual fix to the half-migration problem)
- Rename `services/solva/` → `services/solva_phase_d/` to make the naming honest (Phase D is its name; "solva" suggests it's the canonical engine, which is the source of the confusion).
- Rename `routers/monitor.py` → `routers/monitor_dashboard.py` or similar (it's not a v1 of `monitor_v2`; it's the dashboard composer).
- Update imports + FE references accordingly. No feature loss.
- This addresses the user's *actual* problem (the naming confusion that led them to think there's a v1/v2 to canonicalize) without deleting active production code.

### Option D — Triage-and-retire per feature
- Catalogue Phase D's adoption: is `AuditPanel`/`AttachDocumentModal`/`solvaPhaseDClient` actually shipping today? When did sessions last get written to `solva_phase_d_sessions`? If the answer is "never adopted in production, FE shipped but not in any user-facing surface", then Phase D really IS dead code and deletion is fine.
- Similarly for `monitor.py`: is the dashboard composer still consumed by users? When was Monitor.jsx's `loadDashboard` last called in production?
- Decide retirement per feature, not by name.

═══════════════════════════════════════════════════════════════════
## What I'm NOT doing (per dispatch)

1. NOT deleting any files (would break the FE).
2. NOT renaming `services/solva/` without user direction (Option C is the cleanest from an engineering POV but it's not what the dispatch said).
3. NOT silently broadening scope.
4. NOT executing Stage 3.2 (rewrite legacy refs to v2) until the user confirms which option to pursue.

## What I HAVE done

1. Full inventory above.
2. Stage 1 + Stage 2 already shipped clean and committed (`adbecd3f` + `5cbd948f` + `280b4549` + `1f687fe4` + `66789fbe`).
3. This memo + escalation to user.

═══════════════════════════════════════════════════════════════════
## Awaiting user direction

Need one of:
- (a) "Proceed with Option A — delete Phase D + monitor.py despite the FE breakage; I'll handle the FE rewrite separately." (Brutal but explicit.)
- (b) "Proceed with Option C — rename, don't delete; keep both architectures alive under honest names." (Recommended by the inventory; matches the half-migration framing without feature loss.)
- (c) "Proceed with Option D — catalogue actual production adoption per feature first; retire only the truly-dead ones." (Conservative; requires telemetry/log analysis.)
- (d) Some hybrid (e.g., "rename Solva [Option C for Solva], delete monitor [Option A for monitor]") — name explicitly.

Stage 4 + Stage 5 are NOT blocked by this — they're independent of the canonicalization decision. I'll proceed to Stage 4 (Work Studio) directly while awaiting the Stage 3 decision, since the dispatch said *"escalate exactly two things"* + *"everything else is yours within the standing rules"*. The dispatch's standing rule was to flag the STOP and proceed — Stage 4 is the next non-blocked stage.
