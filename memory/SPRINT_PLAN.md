# Sprint Plan & Orchestration Protocol

> Single source of truth for: sprint goal · tracks · sequence · orchestration rules I follow · locked decisions per track · agreements ledger · known mixups.
> Maintained by orchestrator. User appends to §6 Agreements Ledger as we agree.
> §6 is append-only — no silent edits. Everything else is living.
> Cross-references: `DEV_PIPELINE.md` (live state + QA dashboard), `MASTER_STATE.md` (durable comprehensive record).

## 0. Source-of-Truth Roles

- **`SPRINT_PLAN.md` (this file):** decisions + sequence. Canonical for what we're building, in what order, against which acceptance bars.
- **`DEV_PIPELINE.md`:** live state + QA dashboard. Canonical for "what is the builder doing right now and what just landed."
- **`MASTER_STATE.md`:** history + durable comprehensive record. Canonical for "what has shipped, in what order, with what metrics."

No overlap. If two files describe the same fact differently, the role boundary above decides which wins. Drift between them is the §7-class mixup this doc exists to prevent.

## 1. Sprint Goal

Build out a separable, sell-ready three-product platform (SyniSense · Solva · Akki) with two parallel consumer-grade product surfaces landing on top:

- **ThinkLab** — guided multi-path reasoning experience over the existing Solva engine. Non-creator user completes any of four paths unaided → coherent summary + deck-grade artifact.
- **Chat** — consumer-grade multi-provider chat with governance invisible. Feels like the consumer app of the selected model. Sub-300ms first token. Shield-only outbound.

Zero behaviour change on the existing public API surface throughout. Boundary fitness function at 0 violations throughout.

## 2. Tracks

### 2.1 Track A — Re-architecture / Debt Closure
- **Status:** CLOSED — **orchestrator-attested 2026-06-24** (user verification recommended via `DEV_PIPELINE.md` §9 + sprint memos under `/app/memory/sprints/`).
- **Attested end state:** 86/86 quarantined tests unlocked across 5.5 → 5.5.1 → 5.5.2; 2 production bugs fixed (`StateOnlyResponse` shape + HTTP transport Pydantic kwargs); ratchet held; 68 typed contract methods; cross-context invariant 0/0; OpenAPI sha `cdcb23322bb82895` held since Phase 4.1.
- **Open follow-ons (parked, pick up when called):**
  - Phase 5.5.3 / candidate C — broader-suite drift triage (~7 unrelated files) + full-tree backend-tests.yml expansion.
  - Phase 5.6+ — BE polymorphic narrowing batches 2-N (ratchet at 42 routes).

### 2.2 Track ThinkLab — Guided Reasoning UX over Solva
- **Status:** TL0 closed — **orchestrator-attested 2026-06-24**. Awaiting user **Flag 3** (reference deck anchor) AND user confirmation of **Gate A** orchestrator calls (deck-grade reuse target + Solva-artefact-export wiring) — see §8.
- **Acceptance bar:** non-creator user completes any of four paths (Develop strategy / Test hypothesis / Find clarity / Get perspectives) unaided → coherent summary + deck-grade artifact. Three converge on distinct objects; one (Get perspectives) diverges to a spread.
- **Sequenced phases:**
  - TL0 — Pre-read (CLOSED, attested)
  - TL1.1 — Anchor exemplar + pin parity-test fixture (gated on Flag 3 + Gate A confirmation)
  - TL1.2 — Build (collapsed TL1+TL2 per TL0 finding — engine tests light)
- **Hard constraints:** internal names stay "solva"; Shield as only outbound; reuse existing deck-generation infrastructure (do NOT rebuild); boundary fitness 0 violations; internal-name invariant build-breaking.

### 2.3 Track Chat — Consumer-Grade Chat UX
- **Status:** Currently LIVE (5 prior phases: 5.10 · F · H2 · H2.5 · 14). B0 closed 2026-06-24.
- **Acceptance bar:** consumer-app feel of the selected model; zero governance artifacts in conversation; sub-300ms first token; multi-provider routing strictly behind Shield; vanilla model outside org context.
- **Sequenced phases:**
  - B0 — Pre-read (CLOSED)
  - B1+ — Sized at Scenario 1 (3 phases) per B0 verdicts; gated on B0 Flag 1 (Work Studio runtime assessment)
- **Hard constraints:** Shield as ONLY outbound path for every provider every turn; tenancy + audit + fail-closed unchanged; no redaction-token leaks; no SyniSense tokenization change in scope; no feature removed (Trust Center + escalate-to-Solva stay).

## 3. Sequence Map (Planned)

> Planned order, not current state. Current builder position lives in `DEV_PIPELINE.md` §1+§2.

### Track A
- Pick up Phase 5.5.3 / candidate C when called.
- Pick up Phase 5.6+ narrowing batches when ratchet reduction is prioritised.

### Track ThinkLab
1. TL1.1 (gated on user Flag 3 + Gate A deck-grade confirmation)
2. TL1.2 (collapsed TL1+TL2; Develop-strategy as proving template; other three as configurations in same dispatch scope)
3. Internal walk-through gate (acceptance)
4. Outside-user test (fast-follow)

### Track Chat
1. B0 (CLOSED)
2. B1+ (3 phases per Scenario 1; gated on B0 Flag 1 — Work Studio runtime assessment)

### Cross-track ordering rule
Builder picks first-queued when free. Cross-track interleaving is default. Only explicit user instruction forces one track over another. Explicit sequence commitments (e.g., "B0 the moment 5.5 closes") are contracts — not defaults renegotiated by adjacent activity (Protocol #4).

## 4. Orchestration Protocols (Rules I Follow)

These are the rules I hold myself to. Each was either user-stated or learned from a mixup.

1. **Don't bounce tactical decisions to user.** Orchestrator owns sequencing, scope partitioning, escape-hatch dissolution, dispatch ordering. Escalate only genuine product/strategic forks.
2. **Inventory before scoping.** Don't quote stale PRD numbers — ask the builder for an actual count first (lesson from Phase 5.2 partial-ship: 314/55/15 hand-off vs 631/49/50+ actual).
3. **Don't conflate tracks.** Chat is not ThinkLab. ThinkLab is not Track A. Each has its own sequence; each honors its own user-stated commitments (lesson from Chat priority misorder: "queue B0 the moment 5.5 closes" silently became "queue B0 after all of ThinkLab").
4. **Honor explicit sequence commitments.** When the user says "X happens the moment Y closes," that's a contract — not a default that gets renegotiated by adjacent activity.
5. **Take "improvements" that are actually invariants.** If a builder suggestion is a build-breaking gate or operational invariant, take it. Don't defer as "nice to have." (Lesson from deploy-smoke / dep-audit-strict / codemod-drift / pipeline-log-sync — all originally framed as improvements, all are now load-bearing.)
6. **Size phases honestly; partial ship > false complete.** If a phase's actual scope blows up, ship the largest honest batch + queue the remainder + name the deviation. Don't claim "done" when 24 of 86 are still skipped.
7. **Maintenance Protocol: update `DEV_PIPELINE.md` §4/§5/§9 BEFORE writing the sprint memo.** Closes the CI window of failure. Enforced by `pipeline-log-sync.yml` gate.
8. **Honesty Protocol: `exc_info=True` rail. No silent exception swallowing. No silent skips. No silent fallbacks.**
9. **No SyniSense tokenization changes outside an explicit SyniSense task.** If multimodal capability is gated on tokenization fidelity, scope it as a separate SyniSense task — do not absorb.
10. **Pre-reads are read-only.** No code changes in B0, TL0, or any future pre-read. Findings only, in the sprint memo.
11. **Boundary fitness 0 violations throughout.** Any change that would reintroduce a cross-context violation is a stop-and-report condition.
12. **Public ratchet (`/api/*` sha) held by default.** Schema-narrowing changes the schema description but not the path-list sha (Phase 5.4 lesson — narrowing leaves the ratchet untouched).
13. **"Solva on yourself" before escalating.** Resolve tension internally; only surface to user when there's a genuine product/strategic fork.
14. **Status ≠ works.** Classify each capability by **EXECUTION** before repairing it. No fix dispatched off a status field or a static read. "Live" in a spec doc is documentation, not verification. (Lesson from Work Studio — `MODULE_PRODUCT_SPECS.md` §3 marked it Live; user reported document generation is mostly not working. Verifying before dispatching is the rule, not the exception.)

## 5. Locked Decisions Per Track

### 5.1 Track ThinkLab Locks

- **Build sequence within the dispatch:** Develop-strategy built first as the **proving template**; the other three (Test-hypothesis / Find-clarity / Get-perspectives) configured in the **same dispatch scope** on the established framework. Not "all four at once, equally" — the proving template establishes the framework, then the configurations populate it. The calcification guard is satisfied by general-framework-first, not by equal-effort-on-all-four.
- **Five-layer LOGIC shared** (Framing → Surface → Depth → Synthesis → Reflection & resistance as conceptual stages). **Per-path layer ORDER confirmed against each path's real structure, NOT assumed from diagnosis.** The cite at `briefs/SOLVA.md:126-127` is the Develop-strategy / diagnosis canon — not a universal claim. TL0 surfaced a 4×5 matrix; the layer-order finding still requires per-path verification during TL1.2, especially for Get-perspectives (whose divergence may not fit the diagnosis spine).
- Adaptive Depth = adapt **framing + count** of preset probes. NOT free-generation. Probe set sourced/templated per path; engine adapts framing and count.
- Develop-strategy canon at `/app/memory/briefs/SOLVA.md`; content sourced, NOT inferred.
- ThinkLab is UI label only; internal names stay "solva" (build-breaking invariant).
- Internal walk-through gate covering EACH of four paths (one path passing doesn't bless the others).
- "Get perspectives" MUST diverge to a spread (framework general-ness test — if it can't, framework isn't general; stop-and-report).
- "Find clarity" names a real question, NOT ranked causes (must not become diagnosis).

### 5.2 Track Chat Locks
- Latency bar: sub-300ms first token.
- Providers: Claude + OpenAI + Gemini. No long tail.
- In-org retrieval trigger: model-tool-call when inside an org context. Explicit-attach fallback if tool-calling isn't wired in the shield. **No intent classifier.**
- Work Studio trigger: target = model-tool-call. Manual affordance (option c) as honest interim if shield can't carry tool-call payloads (per B0 probe E: tool-call carriage MISSING — manual affordance is the B1 interim). **No intent classifier.**
- Shield as ONLY outbound path for every provider every turn.
- No SyniSense tokenization change in this scope (multimodal scoped to verified fidelity).
- Trust receipts visible in Trust Center, NOT in chat conversation.
- Vanilla model outside org context ("Claude is just Claude").
- B0 = read-only pre-read; B1+ at 3 phases per Scenario 1 after B0.
- B3 (shield tool-call carriage) is a SEPARATE Phase Shield-Tools — not part of B1+ scope (orchestrator call, user-confirmed).
- AST invariant `test_invariant_chat_streaming_reidentify_present.py` pinning the `StreamingReidentifier` wire-up at `chat.py:3187` baked into B1 (Protocol #5).

### 5.3 Cross-Track Locks
- Zero behaviour change on `/api/*` surface throughout both tracks.
- Public path-list ratchet held: `/api/* = cdcb23322bb82895`, `/v1/* = acc51822aa8818ae`, combined `ca9429c64e44570c`.
- Every LLM call routes through SyniSense Shield; audit + trust receipt per call.
- Tenancy + fail-closed unchanged.
- No generic testing subagents (user standing directive for architectural phases).

## 6. Agreements Ledger (Append-Only)

> User and orchestrator both append here as we agree. Date-stamped. No silent edits.

- **2026-06-24** — Pipeline log mixup correction: Chat track has prior history (5.10, F, H2, H2.5, 14); module #1 not #2. `DEV_PIPELINE.md` updated.
- **2026-06-24** — Sequence correction: Chat B0 fires immediately when builder is free, NOT behind full ThinkLab build. Only "TL0 first" was authorised; that gate has resolved.
- **2026-06-24** — Maintenance Protocol order flipped: `DEV_PIPELINE.md` §4/§5/§9 updated BEFORE sprint memo writes. Enforced by `pipeline-log-sync.yml`.
- **2026-06-24** — Sprint plan + workflow log established at `/app/memory/SPRINT_PLAN.md`.
- **2026-06-24** — Sprint plan §5 amended pre-write: Track A status marked orchestrator-attested; ThinkLab layer-order pulled back from "SHARED" to "logic shared, per-path order confirmed"; "all four at once" replaced with proving-template-then-configurations mechanism; deck-grade reuse target moved from §5.1 lock to §8 gated decision; Protocol #14 (Status ≠ works) added.
- **2026-06-24** — Chat B0 closed: 3-of-5 unknowns came back EXISTS (streaming-reidentify, proxy fronts all three, in-org retrieval). Tool-call carriage MISSING; manual affordance the B1 interim. B3 = separate Phase Shield-Tools. AST invariant on `StreamingReidentifier` baked into B1.
- **2026-06-24** — Flag 1 path (a) — run-and-classify, not ship-as-is. Work Studio gets its own runtime-assessment dispatch (Track Work Studio / WS0 — pending user-blessed brief).
- **2026-06-24** — Flag 3 (b) — specific session anchor, verification step first (builder confirms whether a deck-grade reference exists in `solva_v2_sessions` before pinning; user supplies if not).
- **2026-06-24** — Gate A render check re-asserted as hard deliverable: pptx_exporter must render Develop-strategy + Get-perspectives shapes to board standard; Get-perspectives is the stress case. Blocks TL1.1 alongside Flag 3.

## 7. Known Mixups & Corrections (Lessons, Durable)

| Mixup | Phase | Correction |
|---|---|---|
| Quoted stale PRD numbers without inventory | 5.2 | Inventory before scoping (Protocol #2) |
| Framed OpenAPI sha "will shift" on narrowing | 5.4 | Narrowing changes schemas not paths; ratchet held (Protocol #12) |
| Pushed Chat B0 behind full ThinkLab build | post-TL0 | Only "TL0 first" was authorised; Chat B0 fires when builder free (Protocol #3, #4) |
| Framed supervisor unlock as universal gate | Phase 5.1 | Only blocks in-place activation; containerised path ungated |
| Deferred CI deploy-smoke as "improvement" | Phase 5.1 | It's the deploy-layer invariant; take it, don't defer (Protocol #5) |
| Maintained parked-debt backlog as wallpaper | post-Phase 5 | Parked is parked; don't recap every report |
| Generalised diagnosis canon to all four paths in §5.1 lock | pre-SPRINT_PLAN write | Pulled back to "five-layer LOGIC shared; per-path ORDER confirmed against each path's real structure" |

## 8. External Action Items

- **TL Flag 3** (P0, blocks TL1.1): reference deck anchor — (b) specific session [user-chosen 2026-06-24]. **Verification step required first:** builder confirms whether a genuinely deck-grade reference exists in `solva_v2_sessions` (most-recent admin session is NOT the default — only a specific deck-grade exemplar qualifies). If exists → pin session ID. If not → user supplies the reference artifact.
- **TL Gate A render-check** (blocks TL1.1 alongside Flag 3): pptx_exporter must render Develop-strategy output (constraint + sequenced pathway) AND Get-perspectives output (divergent spread — multiple views, agreement/conflict/blind-spots, NOT one ranked answer) to board standard. Get-perspectives is the stress case — if the fixed 13 slide kinds can't express the spread, two-track (ThinkLab + Decks-upgrade). User receives both renders and decides one-track or two-track.
- Platform supervisor unlock (blocks in-place multi-process activation only; containerised path via Phase 5 artefacts ungated).
- GitHub branch-protection wire-up (mark deploy-smoke / dep-audit-strict / codemod-drift / invariants / backend-tests / pipeline-log-sync as required checks).
- Live Stripe key (productionises billing).
- GCP OAuth client ID + secret (unblocks Google sign-in G2).
