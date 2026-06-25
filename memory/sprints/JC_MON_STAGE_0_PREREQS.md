Source of truth: `/app/memory/JC_MON_CANONICAL_SPEC.md`

# JC-MON Stage 0 — Prerequisites · Q4 + Q2 surface together

> **Closed:** 2026-06-25
> **Stage 0 STOP point reached** — Q4 + Q2 reports surfaced together
> as the canonical-spec dispatch requires. Stage 1 ingestion is
> CLEARED to start; Stage 2 engine work is CLEARED with the
> THIN-ADAPTER verdict on Q4.
>
> Item 1 (JC-TM round-trip breadcrumb close-out) shipped first and
> separately per dispatch order — evidence at
> `/app/memory/jc_artifacts/JC-TM-roundtrip-breadcrumb.jpg` and append
> in `sprints/JC_TM_FAN_OUT.md`.

---

## Verdicts

### Q4 — Solva `probability_weighting` fit verification

**THIN ADAPTER · PROCEED.** The engine
(`services/solva_v2/engines/probability_weighting.py`) accepts the
inputs a Monitor objective + tracked evidence would hand it once a
**single-claim adapter** maps the objective into the engine's
`claims: List[Dict]` shape. The adapter is ≈ 25 LOC and lives in a new
file `services/monitor/assessment_service.py`. No engine reshape. No
fork. The refusal discipline the canonical spec demands ("thin
evidence → say so; do not emit a confident probability over nothing")
is already enforced by the engine's tier invariants + parse-failure
fallback, with the adapter adding a `no_tracking_evidence_yet`
short-circuit ABOVE the engine.

**Full side-by-side mapping (every input, every transformation, every
missing field) lives in
`/app/memory/audit/JC_MON_solva_fit_verification.md`** — reproducible
by the user from line-number citations into the engine source. The
verdict is derived from the table; not asserted.

### Q2 — Tracking-checkbox upload-surface inventory

**12 surfaces inventoried · 7 in-scope (gets the shared affordance)
· 5 out-of-scope (transient artefacts not persisted to `db.documents`
for tracking).** One shared component (`UploadOptions.jsx`, ≈ 70 LOC
new) + 7 small wire-in touch-ups (3-5 LOC each) + 2 additive optional
form fields on the two upload endpoints (`POST /contexts/{cid}/documents`,
`POST /tasks/contribute/{token}/upload`). Footprint total ≈ 110 LOC.

**Full per-surface plan + integration order in
`/app/memory/audit/JC_MON_upload_surface_inventory.md`.**

The 5 SKIPPED surfaces (EnhanceModal, Chat attachment, Solva
AttachDocumentModal, Solva FramingScreen, BlockComposer) are all
transient artefacts — not Journal docs, not tracking-eligible. The
classification is defensible per-surface and called out explicitly.

---

## Why these are gates, not footnotes

The canonical spec's framing: **"prerequisites (gates, not footnotes;
report before building)."**

- **Q4** is the load-bearing test that the architectural reuse premise
  holds. If the engine had required a reshape, Stage 2 would have been
  a STOP — we'd have to build a new probability engine or rewrite the
  Solva v2 one. The thin-adapter verdict means Stage 2a's proving
  slice can be wired in ≈ 25 LOC across ONE new service file, not
  rebuilt.
- **Q2** is the surface-count truth-check before fan-out. 12 surfaces
  is large enough that "available anywhere" is a moving target
  without a single canonical component. The shared `UploadOptions`
  affordance closes the inventory at ONE component, prevents drift,
  and keeps the per-surface cost small.

---

## What ships in Stage 1 (next)

Per the canonical spec § Stage 1:

- **BASE docs** — uploaded via Monitor surface (`ObjectivesProjectsPanel`),
  `is_base_document=true` set via `UploadOptions` (with `allowBase={true}`).
- **TRACKING docs** — the `use_for_tracking` checkbox available
  anywhere (Q2 plan, 7 surfaces).
- **EMAILED docs** — arrive via `source_channel="email"` (existing
  `routers/inbound_email.py` pipeline), land in the Document Journal
  with a **new `state="pending"`** field. A pending-filter on the
  Journal lists them with an "Accept into Journal" action; accept
  flips them to `state="active"` (and into the tracking set if
  flagged).

**Proving slice for Stage 1**: base doc on Monitor page + tracking-flagged
doc elsewhere via the shared affordance + emailed doc accepted from the
Journal pending filter. Show all three landing with their flags.

---

## Honest notes (scope-cuts called out)

- **Comparables** for the probability engine are not wired in v1. The
  engine accepts them; Monitor doesn't yet produce them. Future P2
  layer adds industry-benchmark comparables.
- **The single-claim adapter** is the chosen simplification. An
  alternative ("emit N claims per objective, one per success
  criterion, aggregate to objective-level") gives finer-grain rationale
  but expands the engine round-trip and adds an aggregation rule. v1
  ships the single-claim adapter; v2 can split per criterion.
- **The transient session-mint** in the adapter doesn't persist a
  `solva_v2_sessions` row. The Shield audit chain still flows via
  `audit_entries[]` in the engine return; Monitor persists those into
  its own `objective_assessment_audit` collection.
- **The `ObjectivesProjectsPanel` already has its own upload input**
  (line 326). We replace that input with the file picker + the shared
  `UploadOptions` component — additive, not a redesign of the panel.

---

## Files produced

- `/app/memory/audit/JC_MON_solva_fit_verification.md` (Q4 — 8 sections,
  side-by-side mapping with line citations)
- `/app/memory/audit/JC_MON_upload_surface_inventory.md` (Q2 — 12-surface
  table + per-surface plan + LOC estimate)

## DEV_PIPELINE.md updates pending after this memo

§1 (current state) — set Stage 0 = CLOSED, Stage 1 = NEXT.
§2 (active dispatch) — JC-MON Stage 0 closed; Stage 1 queued with
explicit reference to the 3 proving-slice surfaces.
§4 (evidence index) — Q4 + Q2 docs cited.

KNOWN_MAPPINGS already extended for `JC_MON_*` patterns (this commit).

---

## Standing-rules check (per dispatch)

- [x] No remote pushes
- [x] No JC-WS Generate-Document UI touched
- [x] No regression risk to JC-TM (the breadcrumb close-out is
      additive; ExportLifecycleResponse uses `extra="allow"` so the
      `source_task_id` field surfaces transparently)
- [x] Real evidence on disk (screenshot + 2 audit docs)
- [x] Stage 0 STOP point honoured — surfacing BEFORE Stage 1 build
- [x] `LLM_MODELS_REFRESH` still parked
- [x] No testing subagent used
