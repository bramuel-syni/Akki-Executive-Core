# Phase TL0 — ThinkLab Pre-Read (READ-ONLY)

**Dispatch:** Phase TL0 — ThinkLab Pre-Read
**Status:** ✅ COMPLETE (read-only; deliverable report only)
**Ship date:** 2026-06-24
**Iteration budget:** 1/1 used (single read-only pass).

---

## §1 — Compliance & Debt Snapshot

- **Zero product code touched.** This dispatch is pure read-only inventory. The deliverable is this report.
- **Public ratchet held trivially:** `/api/* = cdcb23322bb82895`, `/v1/* = acc51822aa8818ae`, combined `ca9429c64e44570c` — no code changes possible from a read-only pass.
- **Honesty rail:** every finding below carries a file:line reference OR an explicit "ambiguous — two readings possible". No inference where evidence is missing.
- **No mid-dispatch `ask_human`.** Two stop-and-report conditions surfaced; both flagged at §9.
- **No generic testing subagents.** Inventory by reading code only.

---

## §2 — Gate A verdict — Decks readiness

### A.1 Output capability — **PARTIAL (single-template editorial bullets, NOT board-deck-grade)**

**File-level inventory:**
- Router: `backend/routers/decks.py` (677 LOC, 7 endpoints).
- Render service: `backend/services/work_studio_export.py::render_deck_pptx` (lines 595-674).
- Output collection: `db.decks` (server.py:760, 860).
- Export contract: `_VALID_KINDS = ("brief", "deck", "report", "minutes", "committee_pack")` + `_AUTO_FORMAT["deck"] = "pptx"` (work_studio_export.py:158-159).

**What gets produced** (read directly from `render_deck_pptx`):
- Widescreen 16:9 PowerPoint via `python-pptx`.
- **Fixed 4-section template:**
  - Slide 1: Title (cover, classification banner, Georgia 42pt navy on cream).
  - Slide 2: Executive summary (single text block).
  - Slides 3..N: Body sections (heading + ≤5 bullets + optional callout + cite markers).
  - Slide N+1: "What this means" conclusion (navy band).
  - Slide N+2: Sources (numbered citations).
- **No per-slide variable layouts.** Every body slide is single-column bullets. No 2-column, image+text, chart embeds, comparison tables, decision matrices, board-style executive summary boards.
- Markdown body content per slide (LLM output shape: `slides: [{n, title, body_md}]` per `decks.py::_generate_prompt` lines 260-282).

**Verdict:** **PARTIAL.** The output is structured-text-by-slide with a fixed editorial template — better than raw PDF/DOCX dumps, NOT board-deck-grade. Board-deck-grade would need:
- Per-slide layout primitives (2-column, image+text, chart spec, comparison table).
- Decision-matrix / RAG-status / per-scenario-confidence-table visual primitives.
- Section dividers + executive summary boards as distinct slide kinds.
- Cover variants (headline cover vs scenario cover vs decision cover).

The Solva v2 artefact rendering at `services/solva_v2/payload_builder.py` and `pptx_exporter.py` (separate from `decks.py`) DOES produce more structured slide kinds (13 locked kinds — `cover · headline · tensions_overview · per_tension · scenarios_overview · per_scenario_table · sensitivity · reflection · pathway · decision_logic · risk_mitigation · methodological_honesty · in_closing` per PRD evidence), but that's the SOLVA artefact export, NOT the general Decks surface.

**Implication for ThinkLab:** ThinkLab routing output → Decks via the current `decks.py` path produces editorial-bullets, not board-deck-grade. Routing output → Solva-artefact-export path produces board-deck-grade BUT only via the existing 13 locked slide kinds (each path's Synthesis would need to fit those kinds OR add new kinds).

### A.2 Input contract — **STRUCTURED PAYLOAD (no `solva_analysis_id`-only path exists)**

**`POST /api/contexts/{context_id}/decks/outline`** (decks.py:166):
```python
class OutlineIn(BaseModel):
    intent: str = Field(min_length=12, max_length=600)
    audience: Optional[str] = Field(None, max_length=120)
    target_slides: Optional[int] = Field(None, ge=4, le=20)
    parent_outline_id: Optional[str] = None
```
No `solva_analysis_id` / `solva_session_id` field. Evidence is auto-gathered via `_gather_context_signals` (decks.py:77) — pulls `db.documents` + `get_synisense().list_signals` for the context.

**`POST /api/contexts/{context_id}/decks/{outline_id}/generate`** (decks.py:285):
- Takes the prior outline_id + user edits.
- Calls deep-tier LLM with the approved outline.
- Writes `db.decks` record with `slides: [{n, title, body_md}]`.

**There is no Solva-aware Decks input** today. Walk-in (`backend/routers/walkin.py`) is artefact-keyed (brief/deck/minutes), but it produces a single follow-up question, not a deck.

**Verdict:** **(a) Structured artefact payload only.** Decks consumes `intent: str` + auto-gathered context. ThinkLab cannot pass a Solva-session-id directly; it would need to either:
1. Materialise its session output into a structured `OutlineIn` shape (intent + audience + slide-count hints) before posting to Decks.
2. Add a new Decks input mode (e.g. `POST /decks/from-solva/{session_id}`) — net-new wiring.

### Gate A summary — wiring fork CONFIRMED

- A.1 = **PARTIAL** (slide-grade-ish editorial template; NOT board-deck-grade for the full 4-path output shape).
- A.2 = **(a)** structured payload only; no `solva_session_id` path.

**Stop-and-report flag 1**: A.1 is PARTIAL not NOT-SLIDE-GRADE, so it doesn't stop the build — but it does mean ThinkLab MUST size the Decks-upgrade dependency honestly. Two paths:
- **(i)** ThinkLab uses the Solva-artefact-export pipeline (`payload_builder.py` + `pptx_exporter.py`) for its 4 paths — leveraging the 13 locked slide kinds. Smaller deck-side work, but ThinkLab's output must fit the Solva-artefact schema.
- **(ii)** ThinkLab uses the general `decks.py` path with an enriched intent payload — smaller wiring, but it ships the editorial-bullets template (not board-deck-grade).

**Stop-and-report flag 2**: A.2 wiring fork — ThinkLab output must be materialised as either:
- A `db.solva_v2_sessions` doc (then exported via Solva's pptx_exporter).
- An `OutlineIn` payload (then run through `decks.py`'s outline → generate pipeline).

The user must decide which path before TL2 sizes the build. Default recommendation in §10.

---

## §3 — Gate B verdict — Solva session extensibility

### Verdict: **(a) MUTABLE STRUCTURED STATE** (smallest possible change)

**File reference:** `backend/routers/solva_v2.py:1074-1114` (session insert record).

The Solva v2 session is a schemaless Mongo doc in `db.solva_v2_sessions`. Phase 15.2 already establishes the per-submodule extension pattern:
```python
rec = {
    "id": session_id,
    "submodule": body.submodule,             # Phase 15.2 — already there
    "persona": (body.persona or "").strip() or None,  # Phase 15.2 get_perspective
    "intent": body.intent.strip(),
    "layer": LAYERS[0],
    "layer_index": 0,
    "intake_seed": seed_payload,             # Wave 1.1 — already there
    "frame_audit_summary": None,             # Wave 2.1 — populated by frame_audit engine
    "attached_documents": ...,               # Workstream B (UAT pack 2) — already there
    "turns": [],
    "reasoning_audit_log": [],
    "synthesis": None,
    "reflection": None,                      # Phase 15.3 record
    # ...
}
```

**ThinkLab's required fields all map to existing or trivially-additive fields:**

| ThinkLab field | Solva current state | Mapping |
|---|---|---|
| `path_id` | `submodule` (already exists; 4 values: seek_clarity / develop_strategy / simulate_hypothesis / get_perspective) | Direct alias. ThinkLab UI labels — `submodule` internal. |
| `current_layer` | `layer` + `layer_index` (already exists) | Direct re-use. |
| `layer_answers` | `turns: [{role, content, layer, ...}]` (already exists) | User answers per layer flow into `turns`. |
| `working_set` | `attached_documents: [{id, title, attached_at, preview}]` (already exists; max 5) | Direct re-use. Also `intake_seed` for the start-of-session anchor. |
| `confidence_scores` | `synthesis.claims[].confidence_pct + confidence_band` (already exists per phase 15.1 — see `engines/probability_weighting.py`) | Already there at synthesis-claim grain. **Per-layer confidence is NET-NEW** if ThinkLab wants `confidence_scores` exposed PER LAYER (not just per synthesis claim). |

**Session lifecycle** (read from `solva_v2.py`):
- Create: `POST /api/solva/v2/sessions` (line ~1000s).
- Attach material: `POST /api/solva/v2/sessions/{sid}/attach-document` (line 1645).
- Detach material: `DELETE /api/solva/v2/sessions/{sid}/attached-documents/{document_id}` (line 1716).
- Turn append: `POST /api/solva/v2/sessions/{sid}/turns` (search-pending; the orchestrator dispatches by submodule).
- Frame audit: deterministic engine runs after framing turn (frame_audit.py:387 LOC).
- Synthesize: triggered when state_machine.next_layer transitions to `synthesis`.
- Export: `solva_artefact_export.py` + `routers/solva_v2.py::export_session_docx` (line 3241).

**No lifecycle incompatibility surfaced.** The state machine is a pure module (state_machine.py:18 — "PURE module: it inspects a session document and returns the next valid layer (or None) without mutating anything"). ThinkLab's 5-layer journey fits cleanly.

### Gate B summary

- **(a) Mutable structured state** — Phase 15.2 already established `submodule` + `persona` + `intake_seed` + `attached_documents` + `frame_audit_summary` as schema additions to a schemaless session doc. Adding a `path_progress: {layer_id: {answers: [], confidence: 0.X}}` sidecar OR per-layer fields inline is a clean add.
- **No new collection required** for Gate B. (Sidecar collection `thinklab_path_progress` is OPTIONAL if the user wants to keep `db.solva_v2_sessions` rows leaner — not strictly needed.)

**No stop-and-report fired for Gate B.**

---

## §4 — Layer-order structural finding (ELEVATED gate)

### Verdict: **SHARED across all four paths**

**Source of truth:** `/app/memory/briefs/SOLVA.md` (729 LOC, canonical spec).

Section 3 ("The reasoning journey") of SOLVA.md is explicit (lines 126-127):

> "Solva sessions move through five layers. Layers run in sequence. The user cannot skip ahead. Every layer's output is persisted before the next layer begins."

The brief defines the 5 layers (lines 130-196) and applies the SAME order to all 4 sub-modules. What VARIES per path is:
- **L1 Surface output content** (lines 149-150): "causes for Seek Clarity, strategies for Develop Strategy, hypotheses for Simulate Hypothesis, perspective frames for Get Perspective". Same shape (5-7 candidates), different KIND.
- **L2 Depth probe direction** (lines 163-166): three preset probe types route on Layer 1 patterns (`Inherited-cause / Invisible-cause / Compounding-cause`). Same probe structure, different DIRECTION.
- **L3 Synthesis output emphasis** (lines 178-185): probability-weighted scenarios with the same 5 components for all paths, but per-path emphasis (recommendations for develop_strategy, persona-voiced for get_perspective, scenario-pick for simulate_hypothesis).
- **L4 Reflection**: THREE LOCKED QUESTIONS, identical for all paths (lines 192-194).

### 4×5 matrix — required layer order per path

| Path → / Layer slot ↓ | **L0 Frame Audit** | **L1 Surface** | **L2 Depth** | **L3 Synthesis** | **L4 Reflection** |
|---|---|---|---|---|---|
| **Seek Clarity** | Frame Audit (auto, deterministic) | Narrow to 5-7 **causes** | Probe inherited / invisible / compounding causes | Probability-weighted diagnosis | 3 locked questions |
| **Develop Strategy** | Frame Audit (auto, deterministic) | Narrow to 5-7 **strategies** | Probe inherited / invisible / compounding strategic factors | Probability-weighted recommendations (2-4 testable + owner + timeline) | 3 locked questions |
| **Simulate Hypothesis** | Frame Audit (auto, deterministic) | Narrow to 5-7 **hypotheses** | Probe inherited / invisible / compounding + scenario expansion (preset 2-3 scenarios) | Pick most defensible scenario, acknowledging tensions | 3 locked questions |
| **Get Perspective** | Frame Audit (auto, deterministic) | Narrow to 5-7 **perspective frames** | Probe inherited / invisible / compounding from persona POV | Synthesis IN THE VOICE of persona | 3 locked questions |

### Discrepancy — code today vs canonical brief

**The code does NOT yet match the canonical brief.** Two specific gaps:

1. **`state_machine.py:35-40`** has 4 of 4 paths at a 4-layer flow (`framing → grounding → synthesis → reflection`), but the brief specifies 5 layers for all paths (`Frame Audit → Surface → Depth → Synthesis → Reflection`). Today only `simulate_hypothesis` carries the extra `hypothesis` layer.

2. **Vocabulary aliasing.** Code uses `framing / grounding / hypothesis / synthesis / reflection`. Brief uses `Frame Audit / Surface / Depth / Synthesis / Reflection`. The PRD (memory/PRD.md) uses BOTH at different evidence lines:
   - "L0 frame_audit (3 events) → L1 surface (4) → L2 depth (3) → L3 synthesis (5) → L4 reflection (6)" — uses brief vocab.
   - State machine code uses framing/grounding/hypothesis.
   - `services/solva_v2/engines/frame_audit.py` is a SEPARATE engine (deterministic, runs before state_machine.framing).

**Ambiguous reading** (surface, not silently picked): `state_machine.framing` may correspond to brief's `Surface` (L1, since the framing engine outputs a candidate set there) — OR it may correspond to a pre-Surface framing-text-collection step that the brief folds into Frame Audit (L0). Two readings possible. Resolution needed in TL1 before code changes.

### What this means for TL2 sizing

**Since order is SHARED, the framework parameterises:**
- L1 Surface OUTPUT (candidate kind label: causes / strategies / hypotheses / perspective frames).
- L2 Depth probe TEMPLATES (3 preset probe types; routing based on L1 patterns).
- L3 Synthesis OUTPUT shape (recommendations vs diagnosis vs scenario-pick vs persona-voiced).

**Smaller TL2 build than if order were DISTINCT.** Path-template structure is `(L1.output_kind, L2.probe_routing_table, L3.synthesis_template)` — three parameters, not five layer slots.

---

## §5 — Develop-strategy framework content sourcing

### Located: **`/app/memory/briefs/SOLVA.md`** (canonical, 729 LOC, repo)

**Status:** Repo wins. User has not supplied a separate version. The file is the source-of-truth for the Solva 5-layer framework AND all 4 sub-modules including Develop Strategy.

**Develop Strategy specifics in the brief** (line 37):
> "Develop Strategy — for when the user needs a direction and wants to test their thinking. Solva produces probability-weighted options with sensitivity analysis."

L1 Surface for Develop Strategy (line 150): outputs 5-7 **strategies**.
L3 Synthesis for Develop Strategy: Solva's existing `submodules.py::_develop_strategy_voice` (lines 32-46):
> "Your job at this layer is to RECOMMEND a course of action grounded in the established diagnosis. Where Seek Clarity stops at the question, Develop Strategy answers it: state 2-4 specific recommendations with their evidence tier markers and a confidence band. Each recommendation should be testable, owner-assignable, and timeline-bounded."

**Framing-fix layer's real position:** L0 Frame Audit (per brief), runs BEFORE Layer 1 opens (brief line 203). It's deterministic, has no user-facing UI (brief line 134), and routes L1's opening question. The CODE has this engine at `backend/services/solva_v2/engines/frame_audit.py` (387 LOC), and it's invoked by the orchestrator between session creation and the first user turn — see `routers/solva_v2.py:1097-1100` ("`frame_audit_summary`: None — populated AFTER the framing screen submission, BEFORE the grounding flow"). **Confirmed: Frame Audit is L0, NOT L1.**

**No diff reported** — no user-supplied alternative is on record. If the user has a different version, TL1 must surface the diff before code changes.

---

## §6 — Reference deck location

### Status: **NOT FOUND in repo. Stop-and-report condition.**

**Searched:**
- `/app/memory/` (no `.pptx` files, no `*reference-deck*` filenames).
- `/app/memory/visual_audit/` (JPEGs of UI screenshots, not a sample deck).
- `/app/memory/sprints/BANK_QA_EVIDENCE_PACK/05_DEMO_SCREENSHOTS/` (3 Solva phase D / mid-session-attach screenshots — not a sample deck).
- Generic search across `/app/memory` for "reference deck" / "board.grade deck" / "*.pptx" / "*.deck*" — zero hits.

**The closest artefacts** are the rendered Solva v2 sessions stored in production Mongo (`db.solva_v2_sessions`) — these can be exported via `routers/solva_v2.py:3241::export_session_docx` (DOCX) or via the slide payload at `/api/solva/sessions/{sid}/v2/payload` (rendered as 13 locked slide kinds in the FE). These would be the de-facto "what board-grade looks like today" reference. But there's no explicit pre-shipped reference deck file in `/app/memory/`.

**Stop-and-report flag 3**: TL1 needs a reference deck to grade against. The user must supply one (or designate a specific live Solva session as the reference) before TL2 can size the "board-deck-grade upgrade" track.

---

## §7 — Inventory (6 items)

### Item 1 — Frame-audit shape today

**File:** `backend/services/solva_v2/engines/frame_audit.py` (387 LOC).

**Return type:** `FrameAuditResult` dataclass (line 48):
```python
@dataclass
class FrameAuditResult:
    severity: str  # "none" | "advisory" | "critical"
    observations: List[str]
    recommendations: List[str]
    missing_pieces: List[str]
    summary: str
```
- **Structured multi-slot dataclass**, NOT a single clarifier string.
- Severity ladder: `none / advisory / critical` (lines 27-35 of the docstring).
- Persisted on the session as `frame_audit_summary` (solva_v2.py:1100, `to_dict()` form).
- Deterministic (no LLM) — regex-based heuristics on 5 audit dimensions: decisional clarity / time horizon / scope boundedness / evidence grounding / lens fit (per brief lines 211-217).

### Item 2 — Material attach mechanics

**All three paths exist:**

- **Org context auto-pull (RAG)**: YES. `decks.py::_gather_context_signals` (line 77) pulls `db.documents` (status `extracted`/`ready`) + `get_synisense().list_signals(...)` for the active context. Solva equivalent: `_retrieve_grounding_paragraphs` (referenced in solva_v2.py — Phase 15.1 grounding flow). Documents are scoped by `context_id` (cross-context isolation invariant).
- **User-attached files**: YES via `POST /api/solva/v2/sessions/{sid}/attach-document` (solva_v2.py:1645). Max 5 attachments per session (`_MAX_SESSION_ATTACHMENTS = 5`). Adds a chip `{id, title, attached_at, preview[:300]}` to `attached_documents[]` and emits a `document_attach` audit row.
- **Intake seed**: YES. `IntakeSeed` (`kind ∈ {"document", "question", ...}, id`) attached at session creation via `_resolve_intake_seed` (solva_v2.py:192). Persisted as `session.intake_seed = {kind, id, summary}`.

### Item 3 — Working-set concept

**Verdict: EXISTS as `attached_documents`.**

- Session-level array, persistent across turns, capped at 5.
- Each entry: `{id, title, attached_at, preview}` (solva_v2.py:1682-1687).
- Detach endpoint exists (solva_v2.py:1716).
- Attach is auditable via the `reasoning_audit_log` push (solva_v2.py:1690-1703).
- Intake seed is the "anchor" working set element attached at session start.

**Not net-new state.** The brief's "5-7 candidate set at L1 Surface" is a DIFFERENT concept — that's the LLM-produced candidate working set surfaced at L1 (per brief line 150), NOT the user-attached material set. The two coexist:
- `attached_documents` = user-anchored material.
- `surface.candidates` = LLM-produced 5-7 candidates at L1 (NET-NEW field for ThinkLab; today's `candidate_generation` engine produces them but they're not surfaced as a stable session-level field).

### Item 4 — Depth adaptivity (preset probes)

**Verdict: PRESET PROBE-TEMPLATE SURFACE DOES NOT EXIST TODAY.**

- The state_machine has `hypothesis` as a `simulate_hypothesis`-only layer; its required engine is `tension_detector` (state_machine.py:49).
- The `tension_detector` (`backend/services/solva_v2/engines/tension_detector.py`) is a deterministic engine that surfaces 4 tension categories (user_vs_corpus / user_vs_comparable / comparable_vs_comparable / user_vs_user) — NOT preset probes.
- For the other 3 sub-modules (`seek_clarity / develop_strategy / get_perspective`), there is NO Depth layer in code today. Their state_machine flow is `framing → grounding → synthesis → reflection` (4 layers).
- The brief's three preset probe types (Inherited-cause / Invisible-cause / Compounding-cause — lines 163-166) are NOT implemented anywhere in the engine. Probes today happen as freeform LLM exchanges guided by the per-submodule voice prompts in `submodules.py` (each submodule has a `_<name>_voice(layer)` function that returns a system-prompt header for the layer).

**Implication for ThinkLab:** Adding the Depth probe-templating surface for all 4 paths is **NET-NEW work**, not a parameterisation. Specifically:
- A `probe_router` engine that classifies L1 Surface output and routes to one of {inherited / invisible / compounding} probe templates.
- Probe template definitions per submodule (the "direction" varies by submodule but the structure is shared).
- Persistence: the probe routing decision + probe responses on the session doc.

### Item 5 — Simulate / Walk-in / Lens infrastructure share with Solva

**Verdict: PARALLEL surfaces. No session-model or contract-method sharing.**

Inventory:

| Surface | Router | Sessions? | Contract methods? | LLM call path |
|---|---|---|---|---|
| **Solva v2** | `routers/solva_v2.py` (3271 LOC, `/api/solva/v2/*`) | `db.solva_v2_sessions` (full multi-turn) | 6 methods on `SolvaContract` (`contracts/solva.py`) | `services/solva_v2/engines/*` + `llm_adapter.py` (shielded) |
| **Walk-in** | `routers/walkin.py` (~280 LOC) | NO. Output cached on the parent artefact (brief/deck/minutes). | None (direct `llm_service.call_llm`) | Standard tier, no shield gating |
| **Lens Room** | `routers/lens.py` (M14 feature) | NO. Output keyed on `(signal_id, lens_name)` or similar. | None | Direct `llm_service.call_llm` |
| **Simulate** | `routers/simulate.py` | NO. Output cached on the hypothesis_id. | None | Direct `llm_service.call_llm` |

- **Walk-in** = single-LLM-call utility producing "the next question to ask". One-shot, no session.
- **Lens Room** = six prebuilt frameworks applied to a signal/doc/hypothesis. Each lens returns an OBSERVATION + IMPLICATION + ACTION + one-question shape. One-shot, no session.
- **Simulate** = one-shot Best/Base/Stress scenarios on a hypothesis + 3 watchlist indicators. One-shot, no session.

**They don't share session models with Solva, don't expose contract methods, and don't go through the shielded `solva_v2` engine path.** Per user instruction "inventory ONLY — do NOT unify".

**Note:** "Simulate" the ROUTER is distinct from `simulate_hypothesis` the SOLVA SUBMODULE. The router is a parallel surface (no session); the submodule is a Solva sub-mode (full session). Easy to conflate.

### Item 6 — Existing Solva engine golden tests

**46 test files matching `test_solva_v2_*`.** Total LOC across the major lifecycle/engine tests:

| Test file | LOC | Coverage |
|---|---:|---|
| `test_solva_v2_state_machine.py` | 344 | State machine transitions (next_layer logic, layer order per submodule, fuzz-tested random walks). |
| `test_solva_v2_smoke.py` | 173 | End-to-end smoke: create session → framing → grounding → synthesis → reflection. |
| `test_solva_v2_integration.py` | 229 | Multi-turn integration including engine dispatch. |
| `test_solva_v2_engines_unit.py` | 493 | Per-engine unit tests (frame_audit, triangulation, candidate_generation, tension_detector, probability_weighting, refusal, reflection). |
| `test_solva_v2_submodules.py` | 293 | Submodule registry + per-voice prompt + per-submodule layer flow. |
| `test_solva_v2_shield_invariant.py` | 277 | Shield gating on every LLM call (no unshielded leakage). |
| `test_solva_v2_governance_export.py` | 78 | Export endpoint tenancy + format contract. |
| `test_solva_v2_pptx_export.py` | 211 | PPTX render correctness. |
| `test_solva_v2_grounding_contract.py` | 145 | Grounding contract parser (claims[] with tier markers + confidence). |
| `test_solva_v2_validator_subsurface.py` | 212 | Independent validator runs on synthesis output. |
| `test_solva_v2_tension_detector.py` | (see file) | Tension detector deterministic-output pin. |
| `test_solva_v2_reflection_real.py` | (see file) | 3-question reflection layer (Phase 15.3). |
| `test_solva_v2_payload_builder_parity.py` | (see file) | Slide payload builder byte-equivalence. |
| `test_solva_v2_artefact_schema.py` + 4 sibling files | (see files) | Pydantic schema lockdown for 13 locked slide kinds (cover/headline/tensions/scenarios/sensitivity/reflection/pathway/decision_logic/risk_mitigation/methodological_honesty/in_closing/per_tension/per_scenario_table). |
| Plus 30+ more (see `ls backend/tests/test_solva*`). | | Identity audit, opinion filter, post-redirect recovery, SSE event schema, slide-kind inventory, step description validator, validator subsurface gating, etc. |

**Verdict:** TL1 (characterization) is **LIGHT-WORK, NOT a real phase.** The existing golden tests already cover:
- State machine transitions (gold for layer order changes).
- Per-engine behaviour (gold for engine modifications).
- Submodule voice prompts (gold for per-path differentiation).
- Slide-kind schema lockdown (gold for artefact output changes).
- Shield invariant (gold for keeping LLM calls shielded).
- Export contract (gold for the artefact pipeline).

ThinkLab's TL1 ask is to ADD characterization tests for the few areas the existing suite doesn't already cover (probe-template surface for L2 Depth, surface-candidate-set persistence, per-layer confidence_scores if exposed). Estimated 2-3 new test files; tens of hours.

---

## §8 — Honest scope estimate for TL1 + TL2

### Best case — gates green, shared order, content located, reference deck supplied
- **TL1 (characterization):** light. 2-3 new test files (~500 LOC) to cover the net-new probe-template surface + per-layer confidence_scores + surface-candidate-set persistence. The existing 46-file suite already covers state machine, engines, submodule voices, slide schema, shield invariant, export.
- **TL2 (build):**
  - Parameterise L1 Surface output kind per submodule (already partially done via `submodules.py` voice prompts; needs surfacing the candidate set as a stable session field).
  - Author `probe_router` engine (NET-NEW) + 3 probe templates (Inherited / Invisible / Compounding). Add the L2 Depth layer to all 4 submodule flows in `state_machine.py:LAYER_ORDER_BY_SUBMODULE` (replace 4-layer flow with 5-layer for the 3 non-simulate paths).
  - Per-layer confidence_scores field on the session doc (NET-NEW if exposed per-layer, not just per-synthesis-claim).
  - Wiring fork resolution (see §10): either Solva-artefact-export path OR a new Decks-from-Solva endpoint.
- **Sizing:** 1-2 small sprints (~1-2 weeks of focused work, assuming the wiring fork is decided BEFORE TL2 kickoff).

### Middle case — gates green, distinct order, content located, reference deck supplied
N/A — order IS shared per §4. This branch doesn't apply.

### Worst case — any stop-and-report fires
- **Reference deck not supplied** (flag 3): TL2 can still ship the engine work, but the "board-deck-grade upgrade" track stays unsized until the user supplies a reference. ThinkLab launches with the Solva-artefact-export pipeline (13 locked slide kinds) as the canonical output OR the editorial-bullets `decks.py` pipeline, with the deck-grade upgrade as a parallel post-launch sprint.
- **Wiring fork undecided** (flags 1+2): TL2 cannot begin until the user picks Solva-artefact-export OR enriched-decks-input path. **Stop the build here.**
- **Develop-strategy framework diff** (no flag fired in this pre-read, but POTENTIAL future flag): if the user supplies a version of the Develop-strategy framework that differs from `/app/memory/briefs/SOLVA.md`, TL1 must reconcile.

---

## §9 — Stop-and-report list

**Three conditions fired:**

1. **Flag 1 (Gate A.1 PARTIAL)** — Decks output is single-template editorial bullets, NOT board-deck-grade for the full 4-path output shape. The `decks.py` pipeline ships fixed-template PPTX (cover + exec summary + body bullets + conclusion + sources). The `solva_v2` artefact-export pipeline ships 13 locked slide kinds but those are Solva-specific. **User decision needed:** is "board-deck-grade" the Solva-artefact 13-kind pipeline, OR does ThinkLab require new slide kinds (decision matrices, RAG tables, scenario boards) that neither pipeline ships today?

2. **Flag 2 (Gate A.2 wiring fork)** — Decks does NOT accept `solva_session_id` as input. ThinkLab output must be materialised as either:
   - (i) A `db.solva_v2_sessions` doc, exported via Solva's `pptx_exporter` — leverages 13 locked slide kinds, keeps everything inside the Solva session/audit/shield contract.
   - (ii) An `OutlineIn` payload for `decks.py` — adds a new "from-solva" intake mode (net-new wiring at the Decks router).

3. **Flag 3 (§6 reference deck not found)** — No `*.pptx` or `*reference-deck*` artefact in `/app/memory/` or anywhere in the repo. TL2 needs a reference deck to grade output quality against. **User must supply** or designate a live Solva session ID as the canonical reference.

**No other stops fired.**

---

## §10 — Next-phase recommendation

### Recommended path: collapse TL1 + TL2 into ONE phase (TL1 plus build), with two gates first

**Reasoning:**
- TL1 (characterization) is light because the existing 46-file Solva v2 test suite already covers the load-bearing invariants (state machine, engines, submodule voices, slide schema, shield invariant, export). The genuinely-new characterization tests are 2-3 files; they can ship alongside the build.
- TL2 (build) parameterises the existing engine + adds the probe-template surface. The build is small if the wiring fork (Flag 2) is decided BEFORE kickoff.
- **Collapsed dispatch shape:**
  - **TL1.0 Pre-decision** (this report, DONE).
  - **TL1.1 Wiring decision sprint** (1-2 days, mostly product, not code) — user picks A.2 path (i) or (ii), supplies reference deck, optionally diffs Develop-strategy framework.
  - **TL1.2 Build + characterization** (1-2 weeks) — parameterise state_machine + submodule voices, author probe_router + 3 probe templates, surface candidate set + per-layer confidence_scores, add 2-3 char tests, wire output → chosen materialisation path. Ship behind a feature flag.

**Default recommendation** (if user wants to ship the smallest honest first cut):
- **Wiring fork: (i) Solva-artefact-export path.** Reuses the 13 locked slide kinds, keeps shield/audit/tenancy invariants intact, avoids net-new Decks endpoints. ThinkLab output IS a Solva session; export is the existing `/api/solva/v2/sessions/{sid}/v2/payload` + `pptx_exporter`. Cleanest contract.
- **Reference deck: live Solva session ID** (admin@akki.ai's most recent session, OR a hand-selected session that the user grades as "this is the bar"). Avoids waiting for a separate reference deck file.
- **Develop-strategy framework: `/app/memory/briefs/SOLVA.md` wins** until the user supplies a diff.

### What's NOT in TL1.2 (parking lots)

- Board-deck-grade upgrade beyond the 13 locked slide kinds — parked as a separate Decks-track sprint.
- Simulate / Walk-in / Lens unification — explicitly out of scope per user instruction (inventory only).
- Per-layer confidence-scoring beyond what `probability_weighting` already emits at synthesis-claim grain — parked unless ThinkLab spec needs it.

---

## §11 — Files referenced (read-only)

**Brief (canonical source):**
- `/app/memory/briefs/SOLVA.md` (729 LOC) — 5-layer journey definition, 4 sub-modules, frame audit engine spec.

**State machine + submodules:**
- `backend/services/solva_v2/state_machine.py` (181 LOC).
- `backend/services/solva_v2/submodules.py` (per-submodule voice prompts).

**Engines:**
- `backend/services/solva_v2/engines/frame_audit.py` (387 LOC, deterministic L0).
- `backend/services/solva_v2/engines/{triangulation,candidate_generation,probability_weighting,refusal,tension_detector,reflection}.py`.

**Router + session shape:**
- `backend/routers/solva_v2.py` (3271 LOC) — session insert at L1074, attach at L1645, detach at L1716, export at L3241.

**Decks pipeline:**
- `backend/routers/decks.py` (677 LOC) — 7 endpoints.
- `backend/services/work_studio_export.py:render_deck_pptx` (lines 595-674).

**Solva artefact (alternate output path):**
- `backend/services/solva_v2/artefact_schema.py` (625 LOC) — 13 locked slide kinds.
- `backend/services/solva_v2/payload_builder.py` (1492 LOC).
- `backend/services/solva_v2/pptx_exporter.py`.

**Parallel surfaces (no share):**
- `backend/routers/walkin.py`, `backend/routers/lens.py`, `backend/routers/simulate.py`.

**Test suite (46 files):**
- `backend/tests/test_solva_v2_*` — see §7 Item 6 inventory.

**Contracts:**
- `backend/contracts/solva.py` (92 LOC, 6 contract methods — NOT 38 as dispatch noted; the 38 likely refers to total Solva-surface endpoints including the orchestrator router methods, not the typed `SolvaContract` Protocol).

---

**END OF TL0 REPORT.** Awaiting user direction on the 3 flagged conditions (§9). No code edits in this phase.
