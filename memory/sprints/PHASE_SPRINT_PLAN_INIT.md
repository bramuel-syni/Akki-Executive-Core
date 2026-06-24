# Phase SPRINT_PLAN_INIT — Sprint Plan + Workflow Log Established

**Date:** 2026-06-24
**Status:** CLOSED
**Type:** Orchestration scaffolding (no product code change)
**Source dispatch:** User dispatch "SPRINT_PLAN.md Write" (verbatim memo).

## Deliverable

`/app/memory/SPRINT_PLAN.md` established as the canonical decisions+sequence
source for the multi-track sprint. 8 sections per the user-specified shape:

1. Sprint Goal — three-product platform (SyniSense · Solva · Akki) with two
   consumer-grade surfaces (ThinkLab + Chat); zero behaviour change on
   `/api/*` surface throughout; boundary fitness 0 violations throughout.
2. Tracks — Track A (CLOSED, attested), Track ThinkLab (TL0 closed,
   awaiting Flag 3 + Gate A), Track Chat (B0 closed, awaiting B1+).
3. Sequence Map — Planned order, not current state.
4. Orchestration Protocols — 14 rules I follow, each user-stated or
   learned from a mixup (Protocol #14 "Status ≠ works" added pre-write).
5. Locked Decisions Per Track — ThinkLab locks, Chat locks, cross-track
   locks (path-list ratchet sha, Shield-as-only-outbound, no generic
   testing subagents during architectural phases).
6. Agreements Ledger — append-only, date-stamped. No silent edits.
7. Known Mixups & Corrections — durable lessons table.
8. External Action Items — TL Flag 3, TL Gate A, platform unlock, branch
   protection, Stripe key, GCP OAuth.

## Source-of-Truth Role Boundary

`SPRINT_PLAN.md` §0 establishes the explicit non-overlap with the other
two ledgers:

- `SPRINT_PLAN.md` — decisions + sequence (this file).
- `DEV_PIPELINE.md` — live state + QA dashboard.
- `MASTER_STATE.md` — history + durable comprehensive record.

If two files describe the same fact differently, the role boundary
above decides which wins. Drift between them is the §7-class mixup
this doc exists to prevent.

## Pre-write amendments captured in §6 Agreements Ledger

- Track A status marked **orchestrator-attested**, not user-verified.
- ThinkLab layer-order pulled back from blanket "SHARED" to "five-layer
  LOGIC shared, per-path ORDER confirmed against each path's real
  structure" — diagnosis canon (cite `briefs/SOLVA.md:126-127`) is
  Develop-strategy specific, not universal.
- "All four at once, equally" replaced with proving-template-then-
  configurations mechanism — Develop-strategy proves the framework
  first; Test-hypothesis / Find-clarity / Get-perspectives are
  configurations in the same dispatch scope, not equal-effort parallel
  builds.
- Deck-grade reuse target moved from §5.1 lock to §8 gated decision
  (pending Flag 3 verification + Gate A render check).
- Protocol #14 "Status ≠ works" added — classify capabilities by
  EXECUTION before repairing; "Live" in a spec doc is documentation,
  not verification (Work Studio is the case in point).

## Maintenance Protocol Compliance

Per the flipped order established by Phase Pipeline-Log-Sync:

1. ✅ `DEV_PIPELINE.md` §9 Phase History row added for
   `SPRINT_PLAN_INIT` BEFORE this memo was written.
2. ✅ `pipeline-log-sync.yml` KNOWN_MAPPINGS extended with
   `"SPRINT_PLAN_INIT": "SPRINT_PLAN_INIT"` BEFORE this memo was
   written.
3. ✅ This memo written into a state where §9 + the gate's
   identifier mapping are already in place.

Verified locally: `pipeline-log-sync.yml` Python logic exits 0 against
the working tree at memo-write time.

## Out of Scope (Deliberately)

- No product code touched.
- No new ledger surface — SPRINT_PLAN supplements `DEV_PIPELINE.md` +
  `MASTER_STATE.md` per the §0 role boundary; it does not replace
  either.
- No reshuffle of the §9 Phase History rows — append-only at this layer
  too.

## Next

Per the queue rebalance dispatched by user 2026-06-24 (consolidated
build direction):

1. Chat B1 (Section A — multi-provider routing + grouped selector +
   no-leak generalization + in-org/vanilla switch + AST invariant on
   StreamingReidentifier).
2. WS0 Classify (Section B — 8-capability execution-evidence
   classification matrix).
3. ThinkLab Gate A render-check + Flag 3 verification (demoted; runs
   after Chat B1 + WS0 close).
