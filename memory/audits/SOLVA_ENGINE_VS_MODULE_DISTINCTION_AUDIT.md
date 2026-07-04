**Canonical Spec:** User directive **2026-07-02** — "Solva" has TWO distinct meanings; the **engine** (`services/solva_v2/`, backend internals, LLM adapters, service classes, prompts, DB collections, config vars, log channels) KEEPS the name "Solva". The **module** (user-visible product surface — nav labels, page titles, headers, button copy, emails, PDF/PPTX headers, Doc Journal copy, any external user-facing string) RENAMES to "ThinkLab". This audit is orthogonal to and does NOT reuse the halted `SOLVA_MODULE_RENAME_REGRESSION_AUDIT.md` conclusion (which was written under the reverse premise; renamed from `SOLVA_THINKLAB_RENAME_REGRESSION_AUDIT.md` at 2026-07-02 baseline restoration).

# SOLVA-ENGINE-VS-MODULE-DISTINCTION-AUDIT

**Type:** READ-ONLY grep-driven scope audit.
**Ships:** 2026-07-02.
**Dispatch:** `SOLVA-ENGINE-VS-MODULE-DISTINCTION-AUDIT` (Task C of the 2026-07-02 three-task dispatch).
**Testing method:** N/A (documentation audit; no code touched).
**Locked-area sweep:** 0 product code touched · 0 test files touched · 0 sprint memos edited outside this memo + the `DEV_PIPELINE.md §9` row entered BEFORE this file.

---

## 0. Distinction Restatement

**Two "Solva"s, two rename verdicts.**

| Aspect | Engine (KEEP) | Module (RENAME to ThinkLab) |
| :--- | :--- | :--- |
| What it is | LLM reasoning pipeline + orchestration + adapter fabric | User-facing product surface built on top of the engine |
| Where it lives | `backend/services/solva_v2/**`, `backend/services/solva_voice_audit/**`, backend routers, backend contracts, prompts, DB, env vars, log channels | Frontend pages, components, routes, nav labels, user copy, emails, PDF/PPTX headers, Doc Journal copy |
| Naming rule | Solva remains the canonical name. Any file, class, function, prompt, DB collection, env var, log channel referencing the reasoning engine STAYS as `solva*` | Every user-visible string that today says "Solva" (or "solva") RENAMES to "ThinkLab" (or "thinklab" where lowercase) |
| Rationale | Engine name is stable technical infrastructure; renaming imposes migration cost with no product value | Product surface name is the user-facing brand; the module gets a differentiated name from the engine |

**Sprint-memo shorthand** (`JC-TL`, `PHASE_TL0`, `TL1.1`, `Track ThinkLab`) is internal — orthogonal to both classifications; stays as-is.

---

## 1. Engine References — KEEP as "Solva"

### 1.1 Backend services (core engine)

**Directory: `backend/services/solva_v2/`** (~26 files)

| File | Role | Verdict |
| :--- | :--- | :--- |
| `__init__.py` | Package init | KEEP |
| `analyze_narration.py` | Narration engine | KEEP |
| `artefact_schema.py` | Artefact Pydantic models | KEEP |
| `chair_notes.py` | Chair notes generator | KEEP |
| `chat_v2_fixtures.py` | Stream fixture stubs (test-adjacent) | KEEP |
| `chat_v2_prompts.py` | Chat-v2 system-message builder | KEEP |
| `citation_resolver.py` | Citation resolution engine | KEEP |
| `engines/**` | Sub-engine directory (framing, grounding, synthesis, tension, etc.) | KEEP |
| `feature_flag.py` | `solva_v2_enabled_for(account)` — env `SOLVA_V2_ENABLED` + `account.feature_flags.solva_v2` | KEEP |
| `grounding_contract.py` | `CONTRACT_VERSION = "solva_v2_grounding@1.0"` | KEEP |
| `guardrails.py` | Engine guardrails | KEEP |
| `integrity_validators.py` | Validators | KEEP |
| `llm_adapter.py` | LLM adapter — logs `akki.solva_v2.adapter`, `module="solva_v2.{engine}"` | KEEP |
| `opinion_filter.py` | Opinion filter | KEEP |
| `payload_builder.py` | Payload builder | KEEP |
| `pptx_exporter.py` | PPTX generator | KEEP infrastructure name; but user-visible strings within (footer "Solva Session Output") RENAME — see §2 |
| `spread_heatmap.py` | Spread heatmap generator | KEEP |
| `state_machine.py` | Engine state machine | KEEP |
| `stream_schema.py` | Stream schema | KEEP |
| `stream_synthesizer.py` | Stream synthesizer | KEEP |
| `submodules.py` | Sub-module logic | KEEP |
| `v2_prompts.py` | Master prompts | KEEP |

**Directory: `backend/services/solva_voice_audit/**`** — Voice-audit sub-engine.

**Verdict: KEEP all filenames and code.**

### 1.2 Backend routers (engine-adjacent HTTP surface)

| File | Role | Verdict |
| :--- | :--- | :--- |
| `backend/routers/solva_v2.py` | Engine HTTP endpoints under `/api/solva/v2/*` and `/api/contexts/{cid}/solva/v2/*` | KEEP path + module name — this is the engine's HTTP surface, not the product module. But see §4 Ambiguous #1 for the `/app/solva` FE route reconciliation. |
| `backend/routers/solva_phase_d.py` | Voice-audit HTTP surface | KEEP |
| `backend/routers/solva_phase_d_admin.py` | Voice-audit admin | KEEP |
| `backend/routers/solva_phase_e_polish.py` | Polish endpoint | KEEP |
| `backend/routers/solva_telemetry_admin.py` | Voice-audit telemetry admin | KEEP |

### 1.3 Backend contracts (typed transport layer)

| File | Role | Verdict |
| :--- | :--- | :--- |
| `backend/contracts/solva.py` | Solva context contract methods | KEEP (typed contract layer; engine-adjacent) |
| `backend/contracts/_adapters/solva.py` | Solva context adapter | KEEP |
| `backend/contracts/types.py` | Types incl. `SolvaSessionSnapshot` | KEEP class names (engine-shape types); consider user-facing rename in Ambiguous §4 |

### 1.4 Other backend engine references

* `backend/solva_artefact_export.py` — Engine-adjacent export helper. KEEP filename. User-visible strings inside (e.g. `"Solva session"` fallback labels) RENAME — see §2.
* `backend/solva_session_status.py` — Session-status helper. KEEP filename.
* Feature flag: env `SOLVA_V2_ENABLED` — KEEP.
* Log channels: `akki.solva_v2.adapter`, `akki.solva_v2.engine`, etc. — KEEP.
* Contract version: `solva_v2_grounding@1.0` — KEEP.
* Consumer ID string `consumer_id="solva"` (in analyze_narration.py:716) — KEEP (internal identifier).

### 1.5 DB collections

| Collection | Verdict |
| :--- | :--- |
| `db.solva_v2_sessions` | KEEP — engine-emitted session artefact |
| `db.solva_v2_poc` (legacy) | KEEP name (or archive; not a rename) |
| `db.solva_phase_d_sessions` (voice-audit sessions) | KEEP — engine-emitted |
| `db.solva_v2_document_versions` (if exists) | KEEP |
| `db.solva_v2_kv` (grounding K-V store) | KEEP |

**No DB migration is needed for the module rename.** Engine collections keep their names.

### 1.6 Frontend imports referencing engine (KEEP the module paths)

Even though the FE module renames, some FE-side helper modules that talk to the engine may keep `solva`-style filenames because they're technical adapters, not UI:

| File | Role | Verdict |
| :--- | :--- | :--- |
| `frontend/src/lib/takeToSolva.js` | Handoff helper — POSTs to `/api/solva/v2/seed` (engine endpoint) | ⚠️ AMBIGUOUS — filename references engine (KEEP path structure); but conceptually the CTA text on the button that calls this helper is "Take into Solva" → RENAME the button text; helper filename could stay `takeToSolva.js` or rename to `takeToThinkLab.js`. Recommend RENAME the helper filename too for consistency with the module rename; internal engine calls stay against `/api/solva/v2/*`. |
| `frontend/src/lib/solvaPhaseDClient.js` | Voice-audit HTTP client wrapping `/api/contexts/{cid}/solva/v2/*` | ⚠️ AMBIGUOUS — same reasoning. Recommend RENAME to `thinkLabPhaseDClient.js`; internal API calls remain against `/api/contexts/{cid}/solva/v2/*`. |
| `frontend/src/lib/solvaFlow.js` (and its `__tests__/solvaFlow.test.js`) | Flow logic for the module | RENAME to `thinkLabFlow.js` (this is module-side flow, not engine) |

---

## 2. Module References — RENAME to "ThinkLab"

### 2.1 Frontend pages (user-visible product surface)

| Current file | Renamed file | Notes |
| :--- | :--- | :--- |
| `frontend/src/pages/SolvaApp.jsx` | `ThinkLabApp.jsx` | Landing page for the module |
| `frontend/src/pages/SolvaSession.jsx` | `ThinkLabSession.jsx` | Session detail page |
| `frontend/src/pages/SolvaSessions.jsx` | `ThinkLabSessions.jsx` | Sessions list |
| `frontend/src/pages/SolvaPhaseDSession.jsx` | `ThinkLabPhaseDSession.jsx` | Voice-audit session page |
| `frontend/src/website/pages/product/Solva.jsx` | `ThinkLab.jsx` | Public marketing page |

### 2.2 Frontend component tree

| Path | Verdict |
| :--- | :--- |
| `frontend/src/components/solva/**` (whole subtree — ~30 files: `SolvaLanding.jsx`, `SolvaArtefact.jsx`, `SolvaRefusalArtefact.jsx`, `SolvaBriefingDeck.jsx`, `SolvaHeader.jsx`, `SolvaPptxToolbar.jsx`, `SolvaArtefactV2.jsx`, `SolvaReasoningTicker.jsx`, `SessionLogPanel.jsx`, `SectionDivider.jsx`, `SlideShell.jsx`, flow components, etc.) | Rename directory `solva/` → `thinklab/`; rename each `Solva*.jsx` → `ThinkLab*.jsx`; update all imports across the codebase. |

### 2.3 Route paths (user-visible URLs)

| Current | Renamed | Notes |
| :--- | :--- | :--- |
| `/app/solva` | `/app/thinklab` | Primary module landing (AppShell.jsx:84,114) |
| `/app/solva/session/new` | `/app/thinklab/session/new` | Session-new pathway (takeToSolva.js:9 helper) |
| `/app/solva/sessions` | `/app/thinklab/sessions` | Sessions list |
| `/app/solva?ctx_type=…&submodule=…` | `/app/thinklab?ctx_type=…&submodule=…` | Query-param URLs from `TaskDrawer.jsx:1543-1546` |
| `/product/solva` | `/product/thinklab` | Marketing page |

**URL redirect layer required** — see §7 Migration.

### 2.4 Nav labels + user-visible copy

| File | Line | Current string | Renamed |
| :--- | ---: | :--- | :--- |
| `AppShell.jsx` | 84 | `label: "Solva"` | `label: "ThinkLab"` |
| `AppShell.jsx` | 114 | `label: "Solva"` | `label: "ThinkLab"` |
| `HandoffActions.jsx` | 142 | `"Take into Solva"` | `"Take into ThinkLab"` |
| `HandoffActions.jsx` | 10 | comment `// Take into Solva → /app/solva/session/new` | Update comment |
| `SolvaLanding.jsx` | 11 | `Editorial title "Solva" (Georgia 44px…)` | Editorial title "ThinkLab" |
| `SolvaLanding.jsx` | 543 | `aria-label="Solva sub-modules"` | `aria-label="ThinkLab sub-modules"` |
| `StepReveal.jsx` | 52 | `title: "Solva did the work you saw."` | `title: "ThinkLab did the work you saw."` |
| `WorkspaceEntryScene.jsx` | 65 | `"Solva is opening."` | `"ThinkLab is opening."` |
| `sandbox/Step.jsx` | 14 | `solva: { label: "Solva", reveal: "That is Solva — reasoning with…" }` | `thinklab: { label: "ThinkLab", reveal: "That is ThinkLab — reasoning with…" }` |
| `SolvaArtefact.jsx` | 93, 198, 703 | `"Solva session"` / `SUBMODULE_LABELS[…] || "Solva"` fallback | `"ThinkLab session"` / `… || "ThinkLab"` |
| `SolvaRefusalArtefact.jsx` | 19, 35, 44 | `"Solva does not have enough grounded evidence…"` | `"ThinkLab does not have enough grounded evidence…"` |
| `SessionLogPanel.jsx` | 74 | `aria-label="Solva session log"` | `aria-label="ThinkLab session log"` |
| `SectionDivider.jsx` | 65 | `"Solva Session Output · Confidential · {ctx}"` — PDF/PPTX footer | `"ThinkLab Session Output · Confidential · {ctx}"` |
| `SlideShell.jsx` | 5, 99 | Same footer literal | Same rename |
| `SolvaReasoningTicker.jsx` | 126 | `"Solva — connecting"` | `"ThinkLab — connecting"` |
| `FramingScreen.jsx` | 72 | `"Solva session"` fallback | `"ThinkLab session"` |
| `DocumentRoutingActions.jsx` | 59 | toast `"Solva session created."` | `"ThinkLab session created."` |
| `SourceStep.jsx` | 360 | `"Solva session isn't ready"` | `"ThinkLab session isn't ready"` |
| `ThreePillars.jsx` | 9 | comment `"Solve" renamed to "Solva"` — historical | Historical only; keep OR update note to `"Solve" → "Solva" → "ThinkLab"` for chain of custody |
| `TierChip.jsx` | 117 | `"Solva's judgement, not directly grounded."` | `"ThinkLab's judgement, not directly grounded."` |
| `TrustCenter.jsx` | 756 | `escalation_offered: "Solva escalation offered"` | ⚠️ AMBIGUOUS — see §4 |
| `StatusPage.jsx` | 26 | `solva_engine: "Solva engine"` | ⚠️ AMBIGUOUS — see §4 |

### 2.5 Backend user-visible strings (PDF/PPTX/email templates)

| File | Line | Current | Renamed |
| :--- | ---: | :--- | :--- |
| `backend/templates/solva_artefact.html` | 237 | `"Generated by AKKI · Solva v3"` — PDF/PPTX footer | `"Generated by AKKI · ThinkLab v3"` |
| `backend/templates/solva_refusal_artefact.html` | 105 | `"What Solva can offer"` — header | `"What ThinkLab can offer"` |
| `backend/templates/solva_refusal_artefact.html` | 131 | `"Generated by AKKI · Solva v3 · Refusal artefact"` | `"Generated by AKKI · ThinkLab v3 · Refusal artefact"` |
| `backend/solva_artefact_export.py` | 274, 311 | `"Solva session"` (fallback title) | `"ThinkLab session"` |

**Note:** the template FILENAMES (`solva_artefact.html`, `solva_refusal_artefact.html`) reference the engine's export path — these could stay OR rename. Recommend rename to `thinklab_artefact.html` / `thinklab_refusal_artefact.html` for consistency; requires updating the `render_template` call sites (currently exclusively inside `solva_artefact_export.py`).

### 2.6 Ownership emails / Owner Digest

**None currently reference "Solva" in user-visible copy.** Owner digest + cron endpoints (`/api/cron/owner-digest`) don't emit module-name strings. If future email templates gain "Solva" copy → RENAME.

### 2.7 Doc Journal entry copy

Grep across `backend/routers/document*.py` + `backend/services/document_journal*.py` for "Solva" strings that render into Doc Journal entries:

* `routers/monitor_strategic_items.py:6` — `"cycles + Solva sessions"` in module docstring — comment/docstring; not user-visible → KEEP (comment context) OR update for consistency.
* `routers/monitor_strategic_items.py:104` — docstring `"cycles and Solva sessions"` — same.
* `routers/solva_v2.py:1799` — `short_text = syn_body or intent or "Solva session question"` — this string renders as `cycle_question.short_text` → USER-VISIBLE via Question surfaces → RENAME to `"ThinkLab session question"`.
* `routers/solva_v2.py:2090` — `citation_label = (s.get("framing") or "Solva session")[:80] + "…"` — surfaces as citation label → RENAME to `"ThinkLab session"`.
* `routers/solva_v2.py:1484` — docstring — KEEP (comment).
* `routers/sandbox.py:1452` — docstring comment — KEEP.

### 2.8 Marketing / product PRD copy

* `frontend/src/website/pages/product/Solva.jsx` — public marketing page — RENAME to `ThinkLab.jsx` with all "Solva" copy → "ThinkLab".
* `frontend/src/components/marketing/ThreePillars.jsx:9` — historical rename note — see §2.4 (keep as historical or update chain).
* `memory/PRD.md` (planning document) — grep occurrences; user-facing feature description strings that would be quoted in product marketing → RENAME. Internal engine-facing prose → KEEP.

---

## 3. DB Collections / Config Vars / Env Vars — Full Reconciliation

**All KEEP:**
* `db.solva_v2_sessions` — engine artefact.
* `db.solva_v2_poc` — legacy engine.
* `db.solva_phase_d_sessions` — voice-audit engine.
* Env `SOLVA_V2_ENABLED` — feature flag.
* Account feature flag key `account.feature_flags.solva_v2` — internal.
* Log channels `akki.solva_v2.adapter`, `akki.solva_v2.engine` — internal.
* Contract version `solva_v2_grounding@1.0` — internal.
* Consumer ID literal `consumer_id="solva"` — internal.

**No DB migration required.** The module rename is a pure FE + user-visible-string rename; internal storage keeps its schema.

---

## 4. Ambiguous Cases (with per-case recommendation)

**Case 1 — `/api/solva/v2/*` API endpoints (backend engine HTTP surface).**

* **Nature:** These paths are consumed by the FE module today. When the FE module renames to ThinkLab, does the FE keep calling `/api/solva/v2/*` (engine-shape API), or do we alias `/api/thinklab/v2/*` for cleaner FE code?
* **Recommendation: KEEP `/api/solva/v2/*` (engine endpoints). Do NOT alias.** Rationale: (a) endpoint path is not a user-visible URL (it's XHR-only); (b) engine name stays "Solva" per user directive; (c) aliasing doubles the surface area with no product value. If the FE reads cleaner with `/api/solva/v2/*` unchanged, that's fine — it's the engine surface.

**Case 2 — `frontend/src/lib/takeToSolva.js` filename + `takeToSolva` function name.**

* **Nature:** This is a FE helper that POSTs to the engine's seed endpoint. Filename references "Solva".
* **Recommendation: RENAME to `takeToThinkLab.js` + `takeToThinkLab` function.** Rationale: the helper is called from module-side code (user clicks "Take into ThinkLab"); consistent module-side naming aids readability. Internal API calls STAY against `/api/solva/v2/seed` (engine endpoint per Case 1).

**Case 3 — `frontend/src/lib/solvaPhaseDClient.js` + `frontend/src/lib/solvaFlow.js`.**

* **Nature:** FE clients / flow helpers.
* **Recommendation: RENAME both.** `solvaPhaseDClient.js` → `thinkLabPhaseDClient.js`; `solvaFlow.js` → `thinkLabFlow.js`; update all imports. Internal API paths unchanged.

**Case 4 — `SolvaSessionSnapshot` Pydantic model in `backend/contracts/types.py`.**

* **Nature:** Typed contract model — used by internal typed transport + FE for typed props.
* **Recommendation: KEEP class name `SolvaSessionSnapshot`.** Rationale: it's a typed contract (engine-shape data type); renaming imposes migration cost across the contract layer with no product value. FE code that uses it can still refer to it as `SolvaSessionSnapshot`; the label "ThinkLab session" is a UI string surfaced next to the data, not a type name.

**Case 5 — `TrustCenter.jsx:756` `escalation_offered: "Solva escalation offered"`.**

* **Nature:** Trust Center telemetry label — "Solva escalation" is a user-visible term but semantically refers to the engine's ability to escalate to a Solva session.
* **Recommendation: RENAME to `"ThinkLab escalation offered"`.** Rationale: the user-visible copy in Trust Center should say the product-surface name; the engine capability (escalation) is what's offered but users experience it as an offer to enter the ThinkLab module.

**Case 6 — `StatusPage.jsx:26` `solva_engine: "Solva engine"`.**

* **Nature:** Health-status page displaying an engine health check.
* **Recommendation: KEEP as `"Solva engine"`.** Rationale: unlike Case 5 (which is about entering the module), this label is EXPLICITLY about the engine's technical health. It's an admin/status affordance for internal understanding. Users seeing "Solva engine" here are correctly seeing an engine-health probe; renaming to "ThinkLab engine" would be misleading (the engine is called Solva).

**Case 7 — `_archived/e4_doc_routes/components/reading/TierChip.jsx:117` `"Solva's judgement, not directly grounded."`.**

* **Nature:** Archived component; not shipped.
* **Recommendation: KEEP as archived** — do not touch. Historical record.

**Case 8 — `routers/monitor_strategic_items.py:6,104` docstrings mentioning "Solva sessions".**

* **Nature:** Backend docstrings describing that the router surfaces candidates derived from Solva sessions.
* **Recommendation: KEEP.** Docstrings are internal engineering documentation; they correctly refer to the engine capability.

**Case 9 — `backend/services/solva_v2/analyze_narration.py:716` `consumer_id="solva"`.**

* **Nature:** Internal identifier for a consumer of an event.
* **Recommendation: KEEP.** Internal identifier; not user-visible.

---

## 5. Rename Scope Estimate

### 5.1 File counts

| Category | File count | Notes |
| :--- | ---: | :--- |
| Backend engine files (KEEP as-is) | ~40 | `services/solva_v2/`, `services/solva_voice_audit/`, engine routers, contracts, DB access |
| Backend user-visible strings to change | ~4 template files + `solva_artefact_export.py` + `routers/solva_v2.py` (2 lines) | Template body copy + fallback labels. Template FILENAMES optional rename. |
| Frontend page files to rename | 5 | `pages/Solva*.jsx` + `website/pages/product/Solva.jsx` |
| Frontend component tree to rename | ~30 | `components/solva/**` directory + files |
| Frontend helper libs to rename | 3 | `takeToSolva.js`, `solvaPhaseDClient.js`, `solvaFlow.js` |
| Frontend user-visible string edits (in-place) | ~40 lines across ~20 files | Nav labels, buttons, copy, aria-labels, tooltips |
| Route path renames | 5 URL prefixes | `/app/solva*` + `/product/solva` |
| Import path updates | 100+ | Every file that imports from `components/solva/**` needs its import updated |

**LOC delta estimate:** ~500-800 LOC touched across ~80-100 files. Mostly renames + string edits; net LOC change is close to zero (renames don't add lines).

### 5.2 Backend endpoint path changes

**None required.** Engine endpoints (`/api/solva/v2/*`, `/api/contexts/{cid}/solva/v2/*`) STAY unchanged per Case 1. Frontend continues to call them by their existing names.

### 5.3 Frontend route changes

**5 URL prefix renames:**
* `/app/solva` → `/app/thinklab`
* `/app/solva/session/new` → `/app/thinklab/session/new`
* `/app/solva/sessions` → `/app/thinklab/sessions`
* `/app/solva?query` → `/app/thinklab?query`
* `/product/solva` → `/product/thinklab`

**Redirect layer required** — see §7.

### 5.4 Email template changes

**No user-facing email templates currently reference "Solva".** Owner Digest and other transactional emails render generic Akki branding. If future emails add module-name copy → follow module rename.

### 5.5 Cross-integration surfaces

| Surface | Affected? | Notes |
| :--- | :--- | :--- |
| Chat | ⚠️ MINIMAL — `HandoffActions.jsx:142` "Take into Solva" button text renames | 1 line copy edit |
| Work Studio | ✅ NO — Work Studio doesn't display "Solva" in user-visible copy | Grep confirms zero |
| Monitor | ⚠️ DOCSTRING — `routers/monitor_strategic_items.py` docstrings reference "Solva sessions" as source; not user-visible | KEEP docstrings |
| Doc Journal | ⚠️ MINIMAL — cycle-question `short_text` fallback + citation labels | 2 line edits in `routers/solva_v2.py` |
| Pulse | ✅ NO — no "Solva" strings | Grep confirms zero |
| Trust Center | ⚠️ 1 line — see §4 Case 5 | 1 edit (rename to ThinkLab) |
| Status Page | ⚠️ 1 line — see §4 Case 6 | KEEP as-is (engine health) |

### 5.6 Estimated dispatch size

**Single dispatch is FEASIBLE but risky** given ~100 files touched. **Recommend phased dispatch — see §8.**

---

## 6. Locked-Area Sweep

**Does the rename touch protected zones?**

| Zone | Touched? | Notes |
| :--- | :--- | :--- |
| Shield / Synisense | ❌ NO | Zero "Solva" references in `backend/services/synisense/**` or Shield-adjacent code |
| Track-2 (chat / streaming reidentifier / JC-CHAT invariants) | ⚠️ MINIMAL | 1 button text "Take into Solva" → "Take into ThinkLab" in `HandoffActions.jsx`. JC-CHAT invariant suite unaffected. |
| OAuth / Auth | ❌ NO | No "Solva" references in auth layer |
| Monitor | ⚠️ DOCSTRING-ONLY | See §5.5. No user-visible surface. |
| Storage arc (Azure Blob path) | ❌ NO | Zero references |
| F.6 discipline-pay | ❌ NO | Shield contract not affected |
| Pollution ceilings | ⚠️ CHAT.JSX ONE-LINE | 1 line edit; well within envelope |

**Surface ratchet implications:** none. Engine paths (`/api/solva/v2/*`) unchanged; public OpenAPI sha (`cdcb23322bb82895`) unchanged. Only frontend route paths change (which are not on the ratchet — that's a backend `/api/*` path ratchet).

---

## 7. Migration Considerations

### 7.1 URL redirects

**Users with bookmarked `/app/solva/*` URLs will 404 after the rename unless redirects are added.**

**Recommendation:** add lightweight FE-side redirects using React Router's `Navigate` component. Redirect the 5 old paths to their new equivalents, preserving query params.

```jsx
// In App.jsx or the router config
<Route path="/app/solva" element={<Navigate to="/app/thinklab" replace />} />
<Route path="/app/solva/session/new" element={<Navigate to="/app/thinklab/session/new" replace />} />
<Route path="/app/solva/sessions" element={<Navigate to="/app/thinklab/sessions" replace />} />
<Route path="/product/solva" element={<Navigate to="/product/thinklab" replace />} />
```

**Preserve query params** — `Navigate` doesn't automatically forward them; may need a small `<SolvaRedirect />` wrapper component that reads `useLocation().search` and appends.

### 7.2 DB migrations

**None required.** All Solva-related collections keep their existing names (§3).

### 7.3 Cached client state

* **localStorage / sessionStorage:** grep for `localStorage.setItem.*solva` / `sessionStorage.setItem.*solva`.
  * Result of grep across `frontend/src/`: no keys explicitly named `solva*`. Some keys embed session IDs (`akki:solva-session-{id}`) — RENAME the key prefix in the rename dispatch to `akki:thinklab-session-{id}` OR keep as-is (transparent to user; internal key format).
  * **Recommendation:** KEEP localStorage keys with `solva` prefix — they're internal storage, not user-visible.
* **IndexedDB:** not used for module state.
* **Cookies:** no Solva-specific cookies.

### 7.4 Analytics / search-engine reputation

* **Analytics:** if event names include `solva_*`, renaming breaks dashboards. Grep across `frontend/src/lib/analytics/` for event names.
  * Grep result: no `solva_*` event names identified in a quick scan. Safe.
* **SEO:** `/product/solva` marketing page has whatever SEO weight it has. Redirect + `301` in the FE-side redirect helps but doesn't fully preserve. Recommend also updating the `<title>` and meta tags.
* **Search-engine indexing:** the sitemap (if any) needs updating to reference `/product/thinklab`.

### 7.5 Documentation cross-refs

`/app/memory/**` contains many "Solva" references — most are internal planning memos (KEEP). PRD.md and CHANGELOG.md may contain user-facing product descriptions that should be updated. Rename dispatch should include a scoped `memory/PRD.md` and `memory/CHANGELOG.md` review for user-visible product-description language.

---

## 8. Recommended Dispatch Shape

**Option A — Single MODULE-RENAME dispatch.**
Advantages: atomic; clean git history. Risks: ~100 files touched; if any FE import path is missed, the app breaks; import fixing across the codebase is tedious and error-prone.

**Option B — Phased (RECOMMENDED).**
Split into 4 sequential dispatches to minimize regression risk and preserve the Cluster-G HARD-STOP discipline:

* **Phase 1 — Route + navigation rename** (~1-2 days). Rename routes (`/app/solva` → `/app/thinklab`); update AppShell nav labels; add redirects for old URLs. Ship + proving slice + surface. Result: users see "ThinkLab" in nav, URL bar; all functionality preserved.
* **Phase 2 — File / component tree rename** (~2-3 days). Rename `pages/Solva*.jsx` → `ThinkLab*.jsx`; rename `components/solva/**` → `components/thinklab/**`; rename helper libs (`takeToSolva.js` etc.); update all imports across FE. Ship + slice + surface. Result: filesystem consistency.
* **Phase 3 — User-visible copy rename** (~2 days). All string edits — aria-labels, tooltips, headers, button copy, PDF/PPTX headers, email templates (if any). Ship + slice + surface. Result: end-to-end consistency in user-visible strings.
* **Phase 4 — PRD.md / CHANGELOG.md / marketing consistency pass** (~1 day). Update planning-doc references where they describe user-facing product; leave engine references alone. Ship + surface.

**Total calendar: 6-8 days across 4 dispatches, each JC-shaped (closes a specific rename surface).**

**Option C — Journey-completion-shaped per surface (nav / detail / export / marketing).**
Roughly equivalent to Option B; renames per JC-shaped journey rather than by asset type. Recommend Option B over C — asset-type grouping is cleaner for a rename (less code-review overhead).

---

## 9. Escalation Items (require user decision)

**9.1 Casing convention.** Options:
* `ThinkLab` (PascalCase, one word) — RECOMMENDED for product name; matches typical product-name conventions.
* `Thinklab` (only initial cap) — less common; harder to read at glance.
* `Think Lab` (two words with space) — imposes cross-file consistency burden; harder to search.

**Recommendation: `ThinkLab`** (PascalCase). User confirms before Phase 1 dispatches.

**9.2 Branded tone.** Is "ThinkLab" a lowercase-branded label (like "iPhone") or a normal proper noun? Affects style — do we ever write `thinklab` (all lowercase) in file paths / class names / URL segments?

* URL segments MUST be lowercase per HTTP conventions → `/app/thinklab`.
* React component filenames use PascalCase → `ThinkLabApp.jsx`.
* CSS class names (BEM-style) use lowercase → `thinklab-header`.
* User-visible display strings always PascalCase "ThinkLab".

**Recommendation: standard mixed-casing conventions per context** — lowercase for URLs/CSS/env-var-style; PascalCase for React components/classes; user-visible strings PascalCase "ThinkLab" always.

**9.3 `SolvaSessionSnapshot` typed model rename decision (§4 Case 4).** Recommend KEEP. User confirms.

**9.4 `takeToSolva` FE helper rename (§4 Case 2 + 3).** Recommend RENAME. User confirms.

**9.5 `TrustCenter.jsx:756` "Solva escalation offered" (§4 Case 5) vs. `StatusPage.jsx:26` "Solva engine" (§4 Case 6) semantic split.** Recommend split as proposed. User confirms.

**9.6 Template filename renames** (`backend/templates/solva_artefact.html` → `thinklab_artefact.html`, etc). Recommend RENAME (matches module rename). User confirms.

**9.7 localStorage key prefix `akki:solva-session-{id}`.** Recommend KEEP (internal); rename adds no product value. User confirms.

**9.8 `memory/PRD.md` / `memory/CHANGELOG.md` review scope.** How much planning-doc rewrite does user want? Recommend: touch only user-visible product-description prose; leave engine-adjacent memo history alone.

---

## 10. Migration Test Plan (recommended per-phase proving slices)

Each of the 4 phased dispatches ships with its own proving slice, matching the discipline used across JC-CHAT / JC-WS / JC-MON arcs:

* **Phase 1 slice** — ~5 rows: (a) `/app/thinklab` responds 200; (b) `/app/solva` redirects with 3xx to new path; (c) nav labels grep clean; (d) existing engine endpoints still return 200 (no impact); (e) F.6 discipline-pay + JC-CHAT invariants GREEN.
* **Phase 2 slice** — ~7 rows: (a) new filenames exist + old filenames absent; (b) all imports resolve (build compiles clean); (c) no `import.*from.*"@/components/solva` in codebase; (d) FE lint clean; (e) FE builds without error; (f) engine endpoints unaffected; (g) F.6 + JC-CHAT invariants GREEN.
* **Phase 3 slice** — ~6 rows: (a) `grep -rn "Solva" frontend/src` returns zero user-visible strings (engine class-name imports allowed); (b) PDF/PPTX-export copy shows "ThinkLab"; (c) Doc Journal citation labels use "ThinkLab session"; (d) Handoff button says "Take into ThinkLab"; (e) F.6 + JC-CHAT invariants GREEN; (f) any user-facing email template regeneration passes.
* **Phase 4 slice** — ~3 rows: (a) PRD.md user-visible strings updated; (b) CHANGELOG entry added for rename; (c) no unintended engine-side edits.

---

## 11. Locked-Area Sweep (memo)

* 0 product code touched.
* 0 test files touched.
* 0 sprint memos edited outside this memo + the `DEV_PIPELINE.md §9` row entered BEFORE this file.
* Zero-Handoff-Loss discipline honoured.
* Six banked lessons in play.
* Prior halted audit `SOLVA_MODULE_RENAME_REGRESSION_AUDIT.md` (renamed from `SOLVA_THINKLAB_RENAME_REGRESSION_AUDIT.md` at 2026-07-02 baseline restoration) NOT reused (inverted premise — that audit assumed Solva stays everywhere; this audit distinguishes engine vs module).

## 12. HARD STOP

Read-only classification audit complete. **No renames executed. No dispatches fired.** Surfacing for user direction on:

* §9 escalation items (8 items).
* §8 dispatch shape approval (A / B / C — recommend B, phased).
* Timing — start Phase 1 immediately or wait until upstream items clear.

**Once approved, Phase 1 (route + nav rename) opens as the first dispatch under this audit's scope.**
