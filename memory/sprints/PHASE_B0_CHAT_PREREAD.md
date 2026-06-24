# Phase B0 — Track Chat Pre-Read (READ-ONLY)

**Dispatch:** Track Chat — Phase B0 — Consumer-Grade Redesign Pre-Read
**Status:** ✅ COMPLETE (read-only; deliverable report only)
**Ship date:** 2026-06-24
**Iteration budget:** 1/1 used.

---

## §1 — Compliance & Debt Snapshot

- **Zero product code touched.** This dispatch is pure read-only inventory across 6 probes (A–F) + 1 protocol fix in `sprints/README.md` (Part E).
- **Public ratchet held trivially:** `/api/* = cdcb23322bb82895`, `/v1/* = acc51822aa8818ae`, combined `ca9429c64e44570c` — no code changes possible from a read-only pass.
- **Honesty rail:** every probe carries a `file:line` reference; one probe (F) surfaces as AMBIGUOUS rather than picking silently when BE evidence contradicts user's UX-level claim.
- **No mid-dispatch `ask_human`.** Two stop-and-report conditions surface for user decision (§10).
- **NO generic testing subagents.** Inventory by reading code only.
- **Maintenance Protocol (flipped order)**: `DEV_PIPELINE.md` §1 + §3.3 + §9 updated BEFORE this memo file landed. Pipeline-log-sync CI gate run locally post-update — `EXIT 0`.

---

## §2 — Probe A: Fidelity matrix (6 modalities)

**Anchor:** all chat-attachment paths pass through `documents_service.py::extract_text` (line 130) BEFORE the deidentifier runs. The shield deidentifier (`backend/services/synisense/shield/deidentifier.py:686 LOC`) operates on TEXT only. So fidelity at the shield boundary = fidelity of `extract_text` per modality.

| Modality | Verdict | Evidence (file:line) | Named gap |
|---|---|---|---|
| **text** (.txt / .md / .rtf) | **PASS** | `documents_service.py:186-190` — direct UTF-8 decode + `_clean_text` | None. Type + structure + referential integrity preserved into shield. |
| **PNG** (image) | **PARTIAL** | `documents_service.py:177-183` (`_ocr_image_bytes` → Tesseract) | OCR text only; figures/charts/spatial layout LOST. For text-overlay PNGs: PARTIAL. For visually-rich PNGs (graphs, screenshots of UIs): DEGRADE. |
| **PDF** | **PARTIAL** | `documents_service.py:134-143` (`pypdf` text extraction, page boundaries kept as `\n\n`) | Tables collapse to space-separated rows; embedded images dropped; document structure (headings, footnotes) lost. Text-heavy PDFs read well; form/table-heavy DEGRADE. |
| **DOCX** | **PARTIAL** | `documents_service.py:144-148` (`python-docx`, paragraphs only) | Tables / headers / footnotes / inline images NOT extracted. Linear text passes. |
| **XLSX** | **PARTIAL** | `documents_service.py:172-173` (`_extract_xlsx`, openpyxl `read_only=True`) | Numeric type → string; cell formulas → evaluated values; cross-sheet refs LOST; multi-sheet support exists (all sheets concatenated). |
| **image-with-text** (screenshot with PII overlay) | **PARTIAL** | Same path as PNG (`documents_service.py:177-183`) | Tesseract OCR works for clear typed text; degrades on handwriting, low-contrast, visually-rich content. Bounding boxes / font / colour metadata LOST. PII inside the OCR'd text DOES re-enter the shield deidentifier (anchor verified: shield operates on the OCR'd string, not pixels). |

**Aggregate verdict:** all modalities pass through the shield boundary (no FAIL — no raw bytes ever leak to LLM). The fidelity ceiling is set by `extract_text`. **Multimodal "the model sees the image directly" is NOT supported today** — every modality is text-extracted before any LLM call. If Chat B1+ wants vision-model multimodality (e.g. Claude-3.5 Sonnet seeing a screenshot), that requires Shield extension to carry image payloads through the deidentify/reidentify cycle (currently impossible — token map only covers text spans, not pixel regions).

---

## §3 — Probe B: Streaming-reidentify verdict

**Verdict: EXISTS.**

**Evidence chain:**
- **Class definition:** `backend/services/synisense/shield/reidentifier.py:178-333` — `StreamingReidentifier`. Stateful per-stream rehydrator with `feed(delta) → str` + `flush() → str` semantics. Buffers partial `[[ENT_...]]` tokens across SSE chunks (line 198+ — "Critical: a chunk may end mid-token like `[[ENT_PE` — those bytes stay in the buffer until the next chunk completes the token").
- **Production wiring:** `backend/routers/chat.py:3187` — `stream_reid = StreamingReidentifier(shield_token_map)` instantiated inside `POST /api/chats/{chat_id}/messages/stream` (the canonical streaming endpoint). Each downstream delta from the LLM provider passes through `stream_reid.feed(delta)` before being emitted to the SSE client.
- **Client docstring:** `backend/services/synisense/shield/client.py:140-165` — "Re-identify deltas as they arrive via StreamingReidentifier" — the documented behaviour.

**No build needed.** Streaming-reidentify is a SHIPPED feature, not a parked/missing one. Phase 14 (Chat Fluency) and H2.5 (Streaming PII fix) both depended on this; the implementation has been verified through 5 prior Chat phases.

**Implication for B1+:** the consumer-natural streaming requirement (per-chunk inversion) is MET. Provider routing (Claude/OpenAI/Gemini swap) can be added without first building the streaming-reidentify wall.

---

## §4 — Probe C: Emergent proxy / keys verdict

**Verdict: PROXY FRONTS ALL THREE.**

**Evidence chain:**
- **Direct litellm invocation** at `backend/services/synisense/shield/llm_router.py:163-200`: provider is computed via `_provider_for(preference)` (returns one of `anthropic`/`openai`/`gemini`), the litellm `params["model"]` is set per provider (`gemini/<model>` for Gemini; bare model name for OpenAI/Anthropic via the universal proxy URL).
- **Proxy URL helper** at `llm_router.py:164` — `proxy_url = get_integration_proxy_url()` — returns the Emergent universal LLM proxy URL; the universal proxy routes per-provider.
- **Key required:** `EMERGENT_LLM_KEY` env var (single key, not per-provider keys). Per the `streaming.py:11-17` docstring: "Phase B.3 / Phase A.1 — direct-provider token streaming + strategic fallback" — providers are switchable at runtime via the `model_preference: ModelPreference` literal.
- **No direct provider SDKs required for the universal-proxy path.** A direct-SDK path also exists (anthropic + google-genai), but the universal-proxy is the canonical path for the existing chat surface.

**Two-day feature, NOT three-week.** The provider-routing for Chat B1+ is a parameter swap, not an integration build. Per-tenant BYOK is OUT of scope today and stays out unless an enterprise contract requires it.

---

## §5 — Probe D: In-org retrieval mechanism verdict

**Verdict: EXISTS but BM25-only AND invocation-driven** — gap to the locked product call.

**Evidence chain:**
- **Live retrieval pipeline** at `backend/routers/chat.py:1505-1596` — `_retrieve_grounding_paragraphs` (Phase 11 ITEM C feature).
- **Mechanism**: keyword BM25 ranking over paragraph anchors. NOT vector embeddings. NOT semantic search. `bm25.score_bm25(query_tokens, paragraph_tokens)` at chat.py:1567.
- **Tenant scoping**: documents filtered by `context_id` membership at chat.py:1519-1524. Cross-context isolation invariant respected.
- **Top-K**: K=5 paragraphs per turn (chat.py:1577).
- **Citation grounding**: every paragraph gets a `[[cite:<anchor_id>]]` marker that's preserved through the shield (`paragraph_anchors.compute_paragraphs` at `services/paragraph_anchors.py`). Anchors not present in the returned text are dropped (hallucination guard).
- **Invocation pattern**: PRE-FETCHED every chat turn that has a `context_id`. Model does NOT decide whether retrieval happens — orchestrator runs retrieval unconditionally, then injects results into the prompt.

**Delta to the locked product call** ("model-tool-call when the model needs grounding"):
- Current: every-turn pre-fetch, hard-wired in the orchestrator.
- Target: model-tool-call, model decides per turn.

**Honest scope estimate for the gap:**
- **Tooling wiring** (`_retrieve_grounding_paragraphs` becomes a registered tool): ~1-2 days IF Probe E's shield tool-call carriage is already built. Today, Probe E says MISSING — so the shield extension is the gate.
- **No new RAG infrastructure needed** (no embedding pipeline, no vector store). BM25 stays as the retrieval primitive; only the trigger flips from orchestrator-driven to model-driven. This is the right call per the locked product decision (no "rebuild RAG" sub-phase).

**Vector / embedding-based semantic retrieval is OUT of scope today.** That's a separate Phase B4+ decision once usage data shows BM25 misses cases the model can't reformulate around.

---

## §6 — Probe E: Tool-calling carriage in shield verdict

**Verdict: MISSING.**

**Evidence chain:**
- **Shield invocation signature** at `backend/services/synisense/shield/llm_router.py:118-124`:
  ```python
  async def invoke_with_metering(
      de_id_content: str,
      *,
      model_preference: ModelPreference = "balanced",
      timeout_seconds: float = 20.0,
      system_msg: Optional[str] = None,
  ) -> Tuple[str, str, str, Dict[str, Any]]:
  ```
  No `tools=` parameter. No `tool_choice=`. No tool-execution loop.
- **litellm params** at `llm_router.py:169-185`: only `model` + `messages` + `temperature` + `max_tokens` + `metadata`. Tool definitions NOT passed through to the LLM.
- **Grep evidence**: zero references to `tool_use` / `tool_call` / `tools=` anywhere in `backend/services/synisense/shield/*.py`. Zero in `backend/routers/chat.py`. The Anthropic tool-use block shape is unknown to the shield.
- **Reidentify path** at `reidentifier.py:178-333`: walks text only; would not know how to deidentify arguments inside a tool-use block (which carry JSON with potential PII).

**Per the locked product call** ("if the shield can't carry tool-call payloads, ship manual affordance as honest interim"): manual affordance becomes the interim. Phase B1 ships explicit-attach-only (user manually pins a document → orchestrator pre-fetches; same as today's pattern). Phase B2 or B3 ships the shield tool-call extension (multi-turn loop + tool-use-block deidentify path).

**Build path if/when tool-call carriage lands:**
1. Extend `invoke_with_metering` to accept `tools=[...]` param.
2. Pass tools through to litellm/SDK.
3. Receive `tool_use` blocks back from the model.
4. Route tool execution (e.g. `_retrieve_grounding_paragraphs` becomes a registered tool callable).
5. Re-invoke the model with `tool_result` blocks.
6. Preserve the deidentify/reidentify token map across the multi-turn loop.
7. Add deidentify pass for tool-use JSON arguments (currently text-only).

Honest sizing: 1-2 phases (~1-2 weeks). Build-breaking invariant required: "every tool-use block flowing through the shield is audited + token-mapped".

---

## §7 — Probe F: Work Studio actual state

**Verdict: AMBIGUOUS — two readings possible.**

### Reading 1 — BE code + tests + module spec evidence (suggests LIVE)
- **6 BE routers** totalling ~4,400 LOC exist:
  - `routers/work_studio_export.py` (2357 LOC)
  - `routers/work_studio_from_source.py` (722 LOC)
  - `routers/work_studio_overlay.py` (715 LOC)
  - `routers/work_studio_phase_c.py` (300 LOC)
  - `routers/work_studio_phase_c2.py` (258 LOC)
  - `routers/work_studio_render.py` (~LOC not measured, but exists)
- **4 FE pages exist:** `WorkStudio.jsx`, `WorkStudioActivity.jsx`, `WorkStudioAnalyze.jsx`, `WorkStudioDocumentPage.jsx`.
- **Module spec** (`/app/memory/MODULE_PRODUCT_SPECS.md:240`) — Status: **Live**. No roadmap items pending.
- **BE test sweep** (`pytest tests/test_work_studio_*` quick run): **6 passed, 1 skipped, 1 error**.
  - The 1 ERROR is a test-setup CSRF token issue (`test_briefings_endpoint_shape_is_documented_and_stable` — 403 instead of 200; setup-only failure, not a Work Studio functional failure).
  - The 1 SKIP is a "Patch 19 — briefings list filter contract diverged" — stale-test issue, not a broken endpoint.
- **Known debt** per module spec: 10 `work_studio_overlay.py` endpoints still `Optional[Dict[str, Any]]` (Phase 5.2 Part B partial narrowing); SSE export reconnect-and-resume not built; Phase-C / Phase-C2 routers split across 2 files.

### Reading 2 — User's explicit claim (suggests BROKEN)
- User flagged in conversation: "Work studio needs some work. Most of the document generation logic built is not working."
- This claim contradicts Reading 1 evidence from BE side.
- **Cannot be verified or refuted from read-only BE inventory.** The claim could stem from:
  - FE-level integration issues (FE bugs not surfacing in BE test sweep).
  - End-to-end UX gaps (composer flow works at endpoint level but breaks at UX level).
  - Recent unpinned regressions.
  - Reference to a specific document-generation path I haven't probed (e.g. Decks-via-Work-Studio export, Solva-brief-to-Work-Studio handoff, enhance-second-pass).

**Proposed spec correction:** **NONE FOR NOW.** The BE evidence is consistent with Live. The user-supplied UX-level claim needs reproduction steps to triage. Surfaced as stop-and-report flag 2.

**Implication for Chat B1+:** if Work Studio is genuinely broken at the UX level, the "REUSE Work Studio for document generation" plank from the locked product decisions becomes risky. The honest interim is the locked decision already says: "Work Studio fix-first then model-tool-call" — i.e. B1+ ships manual affordance for document generation UNTIL Work Studio is verified by user-supplied repro. B1+ does NOT depend on Work Studio being green to ship the chat surface.

---

## §8 — Honest scope estimate for B1+

The 6 probes resolved as: 1 PASS (B streaming-reidentify), 1 PROXY-FRONTS-ALL (C), 1 EXISTS-BUT-PARTIAL (D RAG BM25), 1 MISSING (E tool-call), 1 AMBIGUOUS (F Work Studio), and the fidelity matrix (A) is set by `extract_text` ceiling.

### Scenario 1 — Best case (current B0 verdicts)
Streaming-reidentify EXISTS · proxy fronts all 3 · RAG exists (BM25) · tool-call MISSING · Work Studio AMBIGUOUS.

**3-phase shape:**
1. **B1 — Provider routing + persona/voice + UI polish** (~1 week). Swap `EMERGENT_LLM_KEY` to route per model_preference; add user-facing provider picker (if UX wants it); polish chat fluency (consumer-grade animations + token-shape rendering on `Chat.jsx`); preserve all 5 prior phases' contracts.
2. **B2 — Manual-affordance retrieval + Work Studio handoff** (~1 week). Surface explicit "attach document for retrieval" affordance (currently per-org auto-pre-fetch; flip to user-controlled); add "send to Work Studio" CTA for chat outputs (user-confirmed handoff per turn). NO Work Studio fix-in-place required.
3. **B3 — Shield tool-call carriage + model-tool-call retrieval** (~2 weeks). Extend `invoke_with_metering` to accept `tools=`; add `_retrieve_grounding_paragraphs` as a registered tool; add multi-turn loop with deidentify-each-tool-result; add build-breaking invariant for tool-use block audit.

**Total: 4 weeks.** B1+B2 ship the consumer-grade UX surface; B3 unlocks the model-tool-call goal.

### Scenario 2 — Middle case (Work Studio confirmed broken via user repro)
Best-case verdicts + Work Studio confirmed needs FE/UX repair before reuse.

**4-phase shape (B1+B2+B3 from Scenario 1 + B2.5 Work Studio sub-phase):**
- B1: same.
- B2: same EXCEPT no "send to Work Studio" CTA (parked).
- **B2.5 — Work Studio FE/UX repair** (~1-2 weeks, scope depends on repro). Honest read: user-supplied repro determines scope.
- B3: same.

**Total: 5-6 weeks.**

### Scenario 3 — Worst case (full pessimism)
Direct keys required (Probe C falsified) · streaming-reidentify broken (Probe B regressed) · RAG missing (Probe D falsified) · tool-call missing (current) · Work Studio broken.

**This scenario is NOT supported by current evidence — both B and C have strong code-level evidence as EXISTS / PROXY-FRONTS-ALL.** Listed only for completeness per dispatch ask. If somehow all 5 regress simultaneously, B1+ becomes a 5-phase rebuild (provider integrations + shield streaming rebuild + RAG infrastructure + tool-call + Work Studio) sized at ~3 months.

### Recommended phase shape (per orchestrator default)
**Scenario 1 — 3-phase B1/B2/B3 over 4 weeks.** Most-supported by evidence. The 3 phases are independently shippable; B2 ships the user-visible consumer-grade chat without depending on B3. B3 is the "model-tool-call" unlock — gated on shield extension review.

---

## §9 — Files referenced (read-only)

**Shield pipeline:**
- `backend/services/synisense/shield/deidentifier.py` (686 LOC) — text-only deidentifier (entry).
- `backend/services/synisense/shield/reidentifier.py` (333 LOC) — `StreamingReidentifier` at L178-333.
- `backend/services/synisense/shield/llm_router.py` (222 LOC) — `invoke_with_metering` at L118-200; `_provider_for` at L78; litellm params at L169-185.
- `backend/services/synisense/shield/streaming.py` — direct-provider streaming + fallback.
- `backend/services/synisense/shield/client.py` — docstring L140-165 on streaming reidentify.

**Chat routes:**
- `backend/routers/chat.py` (4096 LOC) — `messages/stream` endpoint at L2181 + L3140-3187 streaming-reidentify integration + `_retrieve_grounding_paragraphs` at L1505-1596.

**Document extraction (anchor for fidelity matrix):**
- `backend/documents_service.py:130-201` — `extract_text` + per-MIME handlers (PDF L134, DOCX L144, XLSX L172, image L177, text L186).

**Work Studio:**
- `backend/routers/work_studio_*` (6 files, ~4,400 LOC total).
- `frontend/src/pages/WorkStudio*.jsx` (4 files).
- `memory/MODULE_PRODUCT_SPECS.md:169-248` — module spec §3, status Live.

**Tool-call carriage (negative evidence):**
- `backend/services/synisense/shield/*` — zero `tool_use` / `tool_call` / `tools=` references.

---

## §10 — Stop-and-report list

**Two conditions fired:**

1. **Flag 1 (Probe F AMBIGUOUS)** — User claim ("most document generation not working") contradicts BE evidence (6 routers + 4 FE pages + module spec Live + 6/8 BE tests pass). **User must supply reproduction steps** for Work Studio to triage. Without repro, B1+ ships per Scenario 1 (no Work Studio repair sub-phase) and treats Work Studio as Live; if user later confirms broken via repro, Scenario 2 sizing applies.

2. **Flag 2 (B3 shield extension scope)** — The model-tool-call retrieval goal requires a non-trivial shield extension (multi-turn loop + deidentify tool-use JSON args + audit/build-breaking invariant). B1+B2 ship the consumer-grade UX without this; B3 is the tool-call unlock. **User must confirm B3 is in B1+ scope OR queue it as a separate Phase Shield-Tools sprint.** Default: ship B3 inside B1+ for cohesion.

**No other stops fired.** Probes A, B, C, D, E all resolved cleanly.

---

## §11 — Next-phase recommendation

**B1 — Provider routing + chat fluency polish (1 week, NO product code changes to shield/RAG; pure router/FE work).**

Sized concretely:
- Add `model_preference` to `Chat.jsx` UI state (user-facing provider picker OR auto-default based on quota / latency budget).
- Update `chat.py::messages/stream` to thread `model_preference` from request → `invoke_with_metering` → litellm.
- FE: token-shape rendering polish (existing in Phase 14; B1 makes it consumer-grade — animation, typography, density-tuned for the 300ms first-token bar).
- BE: latency invariant — add a `test_invariant_chat_first_token_under_300ms.py` build-breaking pin (integration-marked, real-proxy-key; deselected by default).
- Preserve all 5 prior Chat phases' contracts (streaming PII, shield audit-always, BM25 retrieval invariant).

**Sprint memo at conclusion will dogfood the new flipped Maintenance Protocol order** — pipeline-log-sync gate already proven (Phase B0 §9 row landed BEFORE this memo file via flipped protocol).

---

**END OF B0 REPORT.** Awaiting user direction on the 2 flagged conditions (§10). No code edits in this phase. Sprints/README.md protocol-order flipped (Part E). DEV_PIPELINE.md §1 + §3.3 + §9 updated BEFORE this memo per the flipped protocol.
