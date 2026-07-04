**Canonical Spec**: user dispatch 2026-07-02 · Phase C interim guard block (verbatim §"PHASE C · INTERIM GUARD") + `/app/memory/sprints/JC_STORAGE_STAGE_2_INGEST_PROFILING.md` (§"STATUS: QUEUED" · this guard exists to close the Truth-in-capability gap surfaced at Stage 1B close) + `/app/memory/rules/TRUTH_IN_CAPABILITY_RULE.md` (transport-proven ≠ per-format-ingest-proven; ceiling must not overstate capability) + `/app/memory/DEV_PIPELINE.md §9` interim-guard row landed BEFORE code (Zero-Handoff-Loss).

# JC-STORAGE-INTERIM-GUARD

Temporary lowered upload ceiling gating Stage 2 per-format ingest profiling.

## Why this exists

Stage 1B shipped 16/16 GREEN with the following Truth-in-capability closure:

- **TRANSPORT proven up to 500 MB** via GCS resumable session (chunked PUT).
- **xlsx INGEST proven at ~17 MB** (via 24.4 MB Path A R7).
- **xlsx INGEST at 500 MB NOT PROVEN.** (Stage 2 territory.)
- **CSV INGEST at any size NOT PROVEN.** (Stage 2 territory.)

`STORAGE_MAX_UPLOAD_MB=500` at Stage 1B close was, strictly speaking, a **transport ceiling** — not a proven ingest ceiling. Leaving it at 500 while ingest capability at that size is unmeasured would silently overstate product capability (a Truth-in-capability rule violation). This guard closes that gap for the interim window between Stage 1B close and Stage 2 GREEN.

## Disposition (banked-rules pick per user directive)

**Temporary lowered ceiling `STORAGE_MAX_UPLOAD_MB=32`.**

Rationale:

- **Reuse**: Stage 1B R10 ceiling-enforcement infra (413 `ceiling_exceeded`) is already in place — only the env-var value + error-copy change.
- **Additive-only**: one env var + one copy tweak (~10 LOC total).
- **Classify-by-execution**: uploads either succeed (≤32 MB, ingest safe under known-good working point at ~17 MB Path A R7) or fail-fast with honest guidance (>32 MB, deferred pending Stage 2 profiling).
- **Maturity-gates**: ceiling explicitly gates behind Stage 2 findings — revertable per-format on Stage 2 close.

Alternative "queued-for-analysis holding state" REJECTED — introduces new UX + storage lifecycle for held files (~150-300 LOC), scope creep against a temporary guard.

## Landed surface

- `backend/.env` — `STORAGE_MAX_UPLOAD_MB=500` → `32`.
- `backend/routers/uploads.py` — `POST /api/uploads/presigned` 413 payload copy update:
  - error code: `ceiling_exceeded` → `ceiling_exceeded_interim_guard`
  - adds `note` field: "Temporary ceiling pending per-format ingest profiling (Stage 2). Transport up to 500MB proven via GCS resumable; per-format ingest capacity not yet measured at that scale."
  - HTTP status **413 preserved**.
- No other changes. `POST /api/uploads/complete`, `GET /api/uploads/{id}/download`, storage helpers, FE routing all UNCHANGED.

## Revert conditions (checked at Stage 2 close)

On `JC-STORAGE-STAGE-2-INGEST-PROFILING` close:

- **BOTH formats (CSV + xlsx) PROVEN at 500 MB** → raise `STORAGE_MAX_UPLOAD_MB` back to 500 (revert interim guard) + §9 close entry.
- **BOTH AT-RISK** → keep interim guard at 32 MB; surface pod-bump recommendation.
- **ANY BLOCKED** → keep interim guard at 32 MB (safe); surface three-options costed report for that format (pod bump / convert-on-ingest / per-format cap).

Ceiling change is NOT automatic beyond the both-PROVEN case. For AT-RISK or BLOCKED outcomes, user directs the ceiling behaviour.

## Rotation status

Parked (auxiliary per user directive "STAY ON THE JOB · ship product · no auxiliary goals · parked items stay parked"). Phase 0 canary at 2026-07-02 confirmed the current `518d39e16250` key GREEN via ops=PUT/EXISTS/GET/DELETE. `CREDENTIALS_NEVER_IN_CHANNEL_RULE.md` remains in force with no third override. Rotation debt tracked in `/app/memory/user_actions/GCS_KEY_ROTATION_OWED.md`.

## Proving slice

`backend/scripts/jc_storage_interim_guard_proving_slice.py` — 7 rows, bash-only:

- R1 · `.env` has `STORAGE_MAX_UPLOAD_MB=32`
- R2 · 33 MB `/api/uploads/presigned` → 413 with `ceiling_exceeded_interim_guard` code
- R3 · 30 MB `/api/uploads/presigned` → 200 `method:"RESUMABLE"` (still routes to GCS · under interim cap)
- R4 · this memo present + line-1 canonical-spec ref present
- R5 · Stage 1B R7 regression stand-in — 24.4 MB xlsx via resumable path still lands (spot-check; full Stage 1B slice remains callable)
- R6 · rename arc P4 hash invariants intact
- R7 · canary still GREEN on current key (identity prefix captured, no key content)

## Standing constraints preserved

- Testing sub-agents BANNED.
- Split-literal discipline (`_TL = "thin" + "klab"`, `_OLD = "Sol" + "va"`).
- No project-scope GCS calls.
- Zero-Handoff-Loss (§9 row landed BEFORE code).
- Chrome hard line + engine surfaces + rename hash invariants + Tab Honesty Rule + Replacement-naming Rule + Credentials-never-in-channel Rule (rotation parked, rule intact) + Amendment-echo Rule + Truth-in-capability Rule all preserved.

## Closure report (populated on GREEN)
