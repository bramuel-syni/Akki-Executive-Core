# INVARIANT_HEALTH — observability dashboard for the AKKI invariant ladder

> **Status:** scaffold. This file aggregates **the state of every
> invariant guard** the codebase carries. It is NOT enforcement —
> the actual ratchets live in `backend/tests/invariants/` and
> `backend/scripts/`. This file is a single-pane-of-glass view.
>
> **Update cadence:** appended whenever a guard rolls forward or a
> new guard lands. Mirrors `DEV_PIPELINE.md` §4 in structure but
> adds: "last verified", "verification command", "current value".
>
> **Last refresh:** 2026-06-26 — BUG-ANL-UPLOAD-GRIDFS close.

## How to read this dashboard

Each row carries five fields:

| Field | Meaning |
|---|---|
| Layer | Architectural slice the guard belongs to |
| Invariant | What the guard preserves |
| Verification command | Bash one-liner that re-proves the guard |
| Last verified | UTC timestamp of the last clean run |
| State | ✅ Green · 🟡 Pre-existing-fail · 🔴 New-fail |

A 🟡 row carries a known pre-existing failure that pre-dates the
current dispatch. A 🔴 row demands immediate halt-and-surface
attention.

## Code-layer invariants

| Layer | Invariant | Verification command | Last verified | State |
|---|---|---|---|---|
| Cross-context | `4_3_enforce_mode` 0 violations / 0 annotations | `pytest tests/invariants/test_invariant_4_3_enforce_mode.py -q` | 2026-06-25 | ✅ |
| Tenancy enforce-mode | 100% routes through canonical membership gate | `pytest tests/invariants/test_context_route_membership_gate.py -q` | 2026-06-24 | ✅ |
| Tenancy escape register | 12 untenanted + 179 markers, all audited | `pytest tests/invariants/test_tenancy_escape_hatch_allowlist.py -q` | 2026-06-24 | ✅ |
| Engine vs surface name guard | `backend/` MUST NOT contain `thinklab` (case-insensitive) | `pytest tests/invariants/test_thinklab_uilabel_only.py -q` | 2026-06-24 | ✅ |
| Function-based naming for Solva/Monitor | no `_vN` suffixes (except grandfathered `solva_v2`); no legacy imports | `pytest tests/invariants/test_no_legacy_solva_monitor_names.py -q` | 2026-06-24 | ✅ |

## Contract & schema invariants

| Layer | Invariant | Verification command | Last verified | State |
|---|---|---|---|---|
| Contract snapshot | 68 typed methods (3 contexts × N) | `pytest tests/invariants/test_invariant_contract_snapshots.py -q` | 2026-06-26 | ✅ |
| API: public path-list ratchet | `/api/* = e0e4e1a48a57cef9` · `/v1/* = a2c20282a273d240` · combined `1cee028104e93e99` | `pytest tests/test_phase4_4_dual_mount_smoke.py -q` | 2026-06-26 | ✅ |
| API: dual-mount byte-equivalence | 45/45 routes mirror | `pytest tests/test_phase4_4_dual_mount_smoke.py -q` | 2026-06-26 | ✅ |
| SDK slice consistency | 4/4 slice ↔ live OpenAPI | `pytest tests/test_phase4_4_dual_mount_smoke.py -q` | 2026-06-26 | ✅ |
| Schema correctness — first-session/transport | first-session-response-shape + http-transport-pydantic-kwargs + chat-streaming-reidentify-present | `pytest tests/test_solva_v2_*schema*.py -q` | 2026-06-26 | ✅ |
| Shield-no-leak ratchet | 3 providers · deliberate-violation rail · 7 default-lane + 4 integration-marked tests | `pytest tests/test_shield_no_leak.py -q` | 2026-06-25 | ✅ |
| BE polymorphic-response-ratchet | 47 typed routes, shrinking | `pytest tests/invariants/test_invariant_polymorphic_response_ratchet.py -q` | 2026-06-26 | 🟡 actual=43 > baseline=42 (PRE-EXISTING drift; +1 route + 2 markers added pre-this-dispatch — RFC narrowing batch deferred to Phase 5.6+) |

## Test-hygiene invariants

| Layer | Invariant | Verification command | Last verified | State |
|---|---|---|---|---|
| FE hygiene | no-raw-axios (codemod 001 enforced) | `cd /app/frontend && node scripts/codemod_001_check.js` | 2026-06-24 | ✅ |
| Test hygiene | no-silent-skips (AST scan) | `python /app/backend/scripts/test_hygiene_no_silent_skip.py` | 2026-06-24 | ✅ |
| Deploy smoke | deploy-smoke present (CI gate) | `pytest tests/test_phase4_4_dual_mount_smoke.py::test_deploy_smoke -q` | 2026-06-26 | ✅ |
| CI gates | codemod-drift + dep-audit-strict + invariants.yml + backend-tests.yml | (via GitHub Actions) | 2026-06-24 | ✅ |
| Pipeline-log sync | sprint memo ↔ DEV_PIPELINE §9 row consistency | (manual review at phase close) | 2026-06-26 | ✅ |

## Repo & CI hygiene

| Layer | Invariant | Verification command | Last verified | State |
|---|---|---|---|---|
| Repo hygiene | committed dev-DB dumps scrubbed (no `*.bson` in history) | `git log -p \| grep '\\.bson$'` (empty) | 2026-06-24 | ✅ |
| CI hygiene | dep-audit-strict (pip + npm) + requirements-guard + gitleaks GREEN under documented allowlists | (via GitHub Actions) | 2026-06-24 | ✅ |

## JC-WS · JC-TM · JC-MON · JC-TL · JC-CHAT closed-feature guards

| Layer | Invariant | Verification command | Last verified | State |
|---|---|---|---|---|
| JC-WS spec lock | `JC_WS_CANONICAL_SPEC.md` — UI-untouched hard rule | (manual review at phase close) | 2026-06-26 | ✅ |
| JC-TM Stage 1 — Compile Bridge | `compile_service.run_drafting` routes through `work_studio_export._run_export` ONE-per-format; PATCH-after-commit→409 | `python scripts/jc_tm_compile_bridge_proving_slice.py` | 2026-06-25 | ✅ |
| JC-TM Stage 2 — Fan-out | 7 journeys assembled; `source_document_ids` wired through Coordinate → Manage → Compile | `python scripts/jc_tm_fan_out_proving_slice.py` | 2026-06-26 | 🟡 24/25 (J5.f stochastic LLM confidence; storage path unaffected) |
| JC-MON Stage 3.0 — candidate-objectives generator | NEVER writes; refusal short-circuit on empty BASE docs | `python scripts/jc_mon_stage_3_0_candidate_objectives_slice.py` | 2026-06-25 | ✅ |
| JC-MON Stage 3.1 — task discriminator + email loop | TM-mode byte-for-byte unchanged; Monitor-mode additive | `python scripts/jc_mon_stage_3_1_task_discriminator_slice.py` | 2026-06-25 | ✅ |
| JC-TL Stage 1 — convergent deck byte-identical at 76555 bytes | proving slice acceptance row | `python scripts/jc_tl_stage_1_diagnosis_proving_slice.py` | 2026-06-26 | ✅ |
| JC-TL Track-2 — divergent rendering | 8/8 — convergent 73280 bytes + divergent 69105 bytes UNCHANGED | `python scripts/jc_tl_track2_min_scope_slice.py` | 2026-06-26 | ✅ |
| JC-CHAT Stage A — sole surviving Synisense marker | per-message badge ONLY | (manual UI inspection at sprint close) | 2026-06-25 | ✅ |
| **BUG-ANL-UPLOAD-GRIDFS** — Analyze upload uses GridFS streaming | 11/11 — 500 MB ceiling, +20.85 MB RSS delta at peak, no orphan `fs.chunks` on lifecycle delete | `python scripts/jc_bug_analyze_upload_slice.py` | 2026-06-26 | ✅ |

## Pre-existing drift queue (🟡 rows — context for triage)

The following guards are 🟡 — they're not regressing per se, but
they carry a baseline drift that pre-dates the current dispatch.
Surface them for triage during the next mechanical/clean-up sprint:

1. **Polymorphic response ratchet** — `actual=43 > baseline=42`; one new
   route at `routers/<unknown>` added with `response_model=Optional[Dict[str, Any]]`
   sometime between JC-MON Stage 3.0 close and now. `actual=50 narrow
   markers > baseline=48`. Triage = pick up during Wave 3 FE-debt
   cleanup or as standalone batch under Phase 5.6+.

2. **Solva v2 governance/smoke CSRF rig** — 3 HTTP-layer tests fail
   because the test rig issues `/api/auth/login` without the CSRF
   token round-trip (`csrf_token_missing`). Failures unrelated to
   any feature path; symptom of test-rig drift after CSRF middleware
   landed. Triage = fix the test rig fixture (~30 min).

3. **JC-TM Fan-Out J5.f** — stochastic LLM-confidence threshold check
   that varies by ±10 pct per run. Triage = either raise the
   threshold floor or convert to a "passes ≥ 70% of N runs" gate.

## What's intentionally NOT in this dashboard

- Per-route response-time SLAs (orthogonal — observed via APM)
- LLM-budget burn rate (orthogonal — observed via Emergent dashboard)
- Mongo collection sizes / index health (orthogonal — DBA tooling)

The dashboard is scoped to **correctness invariants** — guards that
keep the codebase from sliding out of its known-good shape.

## Pending guard scaffolding (P2 — when product team calls)

- `inline-blob sunset` ratchet — once the backfill `--commit` runs
  in prod and a 7-day soak passes, add a guard at
  `tests/invariants/test_no_inline_data_b64.py` that asserts zero
  rows in `workbook_blobs` / `analysis_blobs` carry `data_b64`.
- `GridFS orphan absence` ratchet — assert every `fs.files` row has
  at least one matching metadata row in `workbook_blobs` /
  `analysis_blobs`. Catches "successful GridFS write + failed
  metadata write" leaks. Currently impossible (per-row atomic
  rollback covers this) but worth a guard once at-scale.

## How to add a new row

1. Land the underlying enforcement in `tests/invariants/` or
   `backend/scripts/`.
2. Append a row to the relevant table in this file.
3. Mention the row in the sprint memo that introduced the guard.
