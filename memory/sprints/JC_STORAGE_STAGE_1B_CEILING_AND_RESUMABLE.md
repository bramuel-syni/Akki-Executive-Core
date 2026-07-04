**Canonical Spec**: user dispatch 2026-07-02 (`JC-STORAGE-STAGE-1B-CEILING-AND-RESUMABLE`) + `/app/memory/sprints/JC_STORAGE_PIVOT_GCS_BUILD.md` (Stage 1 · 12/12 GREEN base) + `/app/memory/rules/TRUTH_IN_CAPABILITY_RULE.md` + `/app/memory/rules/AMENDMENT_ECHO_RULE.md` + `/app/memory/rules/CREDENTIALS_NEVER_IN_CHANNEL_RULE.md` + `/app/memory/rules/REPLACEMENT_NAMING_RULE.md` + `/app/memory/DEV_PIPELINE.md` §9 Stage 1B row landed 2026-07-02 BEFORE code (Zero-Handoff-Loss).

# Received-scope for JC-STORAGE-STAGE-1B-CEILING-AND-RESUMABLE

Per `AMENDMENT_ECHO_RULE.md` (banked 2026-07-02) — every amendment to an in-flight dispatch MUST be echoed back before build begins. This memo header enumerates all 8 amendments received:

- **AMENDMENT-1**: `STORAGE_MAX_UPLOAD_MB=500` — pre-provisioned in `backend/.env` from the compaction-dropped Stage 1 amendment; verified present at Stage 1B open.
- **AMENDMENT-2**: Resumable upload is the DEFAULT mechanism for ALL files >16 MB. Single-PUT is DEPRECATED for the >16 MB range. The ">100 MB threshold" that partially landed in the repo was builder-invented and is DISCARDED. Refactor to single-tier resumable-above-16MB.
- **AMENDMENT-3**: R-500MB-transport proving row — real or synthetic file via resumable, lands in GCS, size + SHA-256 verified. TRANSPORT-ONLY per Truth-in-capability rule (does NOT claim ingest at 500 MB).
- **AMENDMENT-4**: R-Ceiling-enforcement — 501 MB request → 413 with `ceiling_exceeded` payload.
- **AMENDMENT-5**: Stage 2 stub memo `sprints/JC_STORAGE_STAGE_2_INGEST_PROFILING.md` present with `STATUS: QUEUED · does not fire without user dispatch` + per-format profiling spec.
- **AMENDMENT-6**: Original Stage 1 24.4 MB Path A test regressed onto resumable mechanism — must still complete end-to-end (upload → GCS → Analyze ingest → artefact opens).
- **AMENDMENT-7**: Truth-in-capability applied — closure claims transport up to 500 MB proven; xlsx/CSV ingest at 500 MB explicitly NOT claimed (Stage 2 territory).
- **AMENDMENT-8**: Partially-landed 100 MB-tier scope refactor: remove `STORAGE_RESUMABLE_THRESHOLD_MB=100` env var; remove `STORAGE_PRESIGNED_TTL_SECONDS=3600` (single-PUT deprecated); collapse `/api/uploads/resumable-session` back into content-length-dispatching `/api/uploads/presigned`; refactor FE 3-tier routing → 2-tier; rebuild partial R13-R15 slice rows under the locked design.

# Locked design

**Two-tier size routing** (single-tier resumable above the 16 MB gate):

| Band | Route | Storage |
|---|---|---|
| ≤ 16 MB | `POST /api/workbook/upload-multi` (existing) | GridFS (unchanged) |
| 16 MB < size ≤ 500 MB | `POST /api/uploads/presigned` (content-length dispatch) → GCS resumable upload session URI → browser chunked PUT with `Content-Range: bytes X-Y/total` → `POST /api/uploads/complete` | GCS blob (no GridFS mirror) |
| > 500 MB | `POST /api/uploads/presigned` returns **413 `ceiling_exceeded`** | rejected upstream |

**Design lock justification** (encoded here so the choice doesn't get re-litigated):

- Dual-path would leave the 24-100 MB band on single-PUT with TTL / flaky-connection exposure unproven under real network conditions.
- Resumable is a superset — handles small large-files (~17 MB), big large-files (~500 MB), and network-flaky uploads via one mechanism.
- Session URIs have GCS-managed ~1-week default validity — no artificial time pressure from user-provided TTLs.
- One code path is simpler than two.
- The builder-invented ">100 MB threshold" for resumable is discarded per user directive.

# Landed surface (post-refactor)

**Backend**:

- `POST /api/uploads/presigned` — content-length dispatch:
  - ≤ 16 MB → 400 `{"error":"use_in_band_route", ...}`
  - 16 MB < size ≤ 500 MB → 200 `{gcs_object_name, upload_session_uri, method:"RESUMABLE", expires_at, content_type, max_upload_mb}`
  - > 500 MB → 413 `{"error":"ceiling_exceeded", "max_mb":500}`
- `POST /api/uploads/complete` — unchanged signature; verifies via `bucket.blob(name).exists()`, streams to tempfile, parses via `parse_workbook`, persists analysis + blob rows with `gcs_object_name`.
- `GET /api/uploads/{artefact_id}/download` — unchanged.
- **`POST /api/uploads/resumable-session`** — **DELETED** (collapsed into `/presigned`).

**Storage helpers** (`backend/services/storage_service.py`):

- `gcs_initiate_resumable_upload_session(object_name, content_type, size, origin)` — renamed from `gcs_create_resumable_upload_session` to match user spec-name (Replacement-naming rule: naming replacement only, no semantic change).
- `gcs_generate_presigned_upload_url` — **DEPRECATED**; docstring marks it, function kept per user directive ("Do NOT delete").
- All other helpers unchanged.

**Frontend** (`frontend/src/pages/AnalyzeJournal.jsx`):

- 2-tier routing: ≤16 MB in-band multipart to `/workbook/upload-multi` (unchanged); >16 MB resumable session URI + chunked PUT.
- Chunk size: 8 MiB (GCS-recommended range 256 KiB minimum, 8-256 MiB typical).
- XHR upload-progress for progress reporting.
- Retry-on-network-drop: on chunk failure, GET session URI with `Content-Range: bytes */total` to query the last-committed byte, then resume from that offset.
- Work Studio upload path unchanged this dispatch (deferred to follow-up per Stage 1 disposition).

**Env vars** (`backend/.env`):

- KEEP: `STORAGE_X_THRESHOLD_MB=16`, `STORAGE_MAX_UPLOAD_MB=500`, `GCS_ARCHIVE_PREFIX=_archive/`, GCS/GCP creds.
- REMOVE: `STORAGE_RESUMABLE_THRESHOLD_MB=100`, `STORAGE_PRESIGNED_TTL_SECONDS=3600` (both are single-PUT era artefacts).

**DB additive fields** — no migration:

- `workbook_blobs.gcs_object_name` (str) — set for GCS-path rows (from Stage 1; carried through).

# Replacements (per REPLACEMENT_NAMING_RULE)

1. `gcs_create_resumable_upload_session` → `gcs_initiate_resumable_upload_session`. Reason: user spec explicitly named the helper `gcs_initiate_resumable_upload_session`; original name matched the underlying GCS SDK method (`blob.create_resumable_upload_session`). Impact: naming only; identical semantics, zero behavioural change.
2. Endpoint `POST /api/uploads/resumable-session` → collapsed into `POST /api/uploads/presigned` (content-length dispatch). Reason: user directive locks `/presigned` as the single unified entry point for GCS uploads above the 16 MB gate. Impact: `resumable-session` endpoint deleted; `/presigned` now returns a resumable session URI (previously returned a V4 single-PUT URL) for the 16-500 MB band; response shape shifts from `{upload_url, method:"PUT"}` to `{upload_session_uri, method:"RESUMABLE"}`. Frontend uses the new shape.
3. From Stage 1 (unchanged, carried through): specced `list_buckets` probe → per-object `bucket.blob(name).upload_from_string→exists→download→delete` canary.

# Rotation debt

Both `8b9c...` (GCP-deleted) and `518d...` (currently-live) SA JSON keys are chat-exposed. Fresh key owed at next natural rotation opportunity via terminal-only. Tracked in `/app/memory/user_actions/GCS_KEY_ROTATION_OWED.md`. Per `CREDENTIALS_NEVER_IN_CHANNEL_RULE.md` (banked 2026-07-02) — this-incident override does not rescind the standing rule.

# Proving slice

`backend/scripts/jc_storage_stage_1b_proving_slice.py` — bash execution only. Testing sub-agents STRICTLY BANNED. Split-literal discipline preserved.

Rows:

- R1 · env sanity (STORAGE_MAX_UPLOAD_MB=500, STORAGE_X_THRESHOLD_MB=16, GCS creds present; `STORAGE_RESUMABLE_THRESHOLD_MB` + `STORAGE_PRESIGNED_TTL_SECONDS` REMOVED from `.env`)
- R2 · canary GREEN (per-object PUT/EXISTS/GET/DELETE against rotated `518d...` key)
- R3 · archive marker `_archive/.provisioned` present
- R4 · S3 + local storage classes preserved byte-for-byte (SHA-256 hash-guarded from Stage 1 snapshot)
- R5 · **Resumable is default for >16MB** — `POST /api/uploads/presigned` for a 24.4 MB xlsx returns `method:"RESUMABLE"` + `upload_session_uri` (not `upload_url`)
- R6 · **Single-PUT deprecated** — `services.storage_service.gcs_generate_presigned_upload_url` docstring contains `DEPRECATED`; endpoint `/api/uploads/resumable-session` NOT registered on the running app
- R7 · **24.4 MB Path A regressed onto resumable** — upload xlsx via session URI + chunked PUT → `/api/uploads/complete` → `workbook_analyses` + `workbook_blobs` rows persisted with `gcs_object_name` · `parse_workbook` OK · signed GET round-trip
- R8 · Path B (<16 MB via `/api/workbook/upload-multi`) still lands with `gridfs_id` set + `gcs_object_name` absent (regression)
- R9 · Threshold gate — 1 KB request to `/api/uploads/presigned` returns 400 `use_in_band_route`
- R10 · **R-Ceiling-enforcement** — 501 MB request to `/api/uploads/presigned` returns 413 `ceiling_exceeded`
- R11 · **R-500MB-transport (TRANSPORT-ONLY)** — synthetic 500 MB blob uploaded via resumable session (single-PUT termination), size + SHA-256 verified. Labeled TRANSPORT-ONLY per Truth-in-capability rule.
- R12 · **R-Retry-on-drop** — chunked resumable PUT with commit-state query after simulated drop; if not feasible in slice env, mark **BEST-EFFORT** and do NOT fake pass.
- R13 · No project-scope GCS calls (AST-verified)
- R14 · Split-literal discipline (tokenize-verified)
- R15 · Rename arc P4 hash invariant intact (CHANGELOG + PRD below-footer bytes unchanged)
- R16 · Stage 2 stub memo exists with `STATUS: QUEUED`

# Closure trajectory

On slice GREEN:

1. `DEV_PIPELINE.md §9` Stage 1B row 🟡 IN-PROGRESS → 🟢 SHIPPED with row count.
2. `CHANGELOG.md` top entry updated with Stage 1B closure.
3. `PRD.md` footer appended.
4. This memo's `## Closure report` section populated.
5. Trigger-2 close report to user with received-scope echo on line 1.

**No auto-fire to A6/A9/A10 backends** after Stage 1B — user directs next per post-close ordering.

# Standing constraints (all preserved)

- No project-scope GCS calls (AST-verified).
- Chrome hard line + engine surfaces + rename hash invariants + Tab Honesty Rule + Replacement-naming Rule + Credentials-never-in-channel (override logged; rule stands) + Amendment-echo Rule + Truth-in-capability Rule all preserved.
- Testing sub-agents BANNED.
- Split-literal discipline (`_TL = "thin" + "klab"`, `_OLD = "Sol" + "va"`).
- Zero-Handoff-Loss (§9 row landed BEFORE code refactor).
- F.6 discipline-pay N/A (no LLM path).
- GridFS legacy uploads untouched (no migration, no backfill).

# Closure report (2026-07-02 · GREEN)

Slice: `backend/scripts/jc_storage_stage_1b_proving_slice.py` → **16/16 GREEN**.

| Row | Detail |
|---|---|
| R1  | env sanity · x-threshold=16MB · ceiling=500MB · deprecated env vars (RESUMABLE_THRESHOLD_MB + PRESIGNED_TTL_SECONDS) ABSENT from `.env` |
| R2  | canary GREEN on rotated `518d39e1` key · ops=PUT/EXISTS/GET/DELETE |
| R3  | `_archive/.provisioned` present |
| R4  | LocalDiskStorage + S3Storage class bodies byte-for-byte preserved (Stage 1 SHA-256 pin) |
| R5  | 24.4 MB xlsx → `/api/uploads/presigned` returns `method:"RESUMABLE"` + `upload_session_uri` (no `upload_url`) |
| R6  | `gcs_generate_presigned_upload_url` docstring marked `DEPRECATED` (AST-verified) · `/api/uploads/resumable-session` endpoint NOT registered in openapi (collapsed into `/presigned`) |
| R7  | 24.4 MB Path A regressed onto resumable · full E2E: chunked PUT (8 MiB) → `/uploads/complete` → `workbook_analyses` + `workbook_blobs.gcs_object_name` persisted → `parse_workbook` OK on read side → signed GET round-trip returned same bytes |
| R8  | Path B <16 MB via `/api/workbook/upload-multi` still lands with `gridfs_id` set + `gcs_object_name` absent (regression asserted) |
| R9  | 1 KB → `/api/uploads/presigned` returns 400 `use_in_band_route` |
| R10 | 501 MB → `/api/uploads/presigned` returns 413 `ceiling_exceeded` |
| R11 | **TRANSPORT-ONLY 500 MB** synthetic (/dev/urandom) uploaded via resumable session (chunked PUT) · size + SHA-256 verified · labeled TRANSPORT-ONLY per Truth-in-capability rule |
| R12 | Retry-on-drop resume-from-commit-state OK · initial 8 MiB chunk landed · probe `Content-Range: bytes */TOTAL` returned `Range: bytes=0-8388607` · resumed from committed offset · completed |
| R13 | AST scan on `routers/uploads.py` + `scripts/jc_gcs_canary_probe.py` + `services/storage_service.py` — 0 forbidden `list_buckets(` or `get_bucket(` calls |
| R14 | Split-literal discipline preserved (tokenize-verified; no raw joined `"thinklab"` or `"Solva"` string literals) |
| R15 | Rename arc P4 hash invariants intact — CHANGELOG + PRD below-footer bytes match pinned SHA-256 |
| R16 | Stage 2 stub `sprints/JC_STORAGE_STAGE_2_INGEST_PROFILING.md` present with `STATUS: QUEUED · does not fire without user dispatch` marker |

## Replacements enumerated (per REPLACEMENT_NAMING_RULE)

1. `gcs_create_resumable_upload_session` → `gcs_initiate_resumable_upload_session`. Reason: user spec explicitly named the helper `gcs_initiate_resumable_upload_session`; original name matched underlying GCS SDK (`blob.create_resumable_upload_session`). Impact: naming only; identical semantics. Backwards-compat alias retained.
2. Endpoint `POST /api/uploads/resumable-session` → collapsed into `POST /api/uploads/presigned` (content-length dispatch). Reason: user directive locked `/presigned` as the single unified entry point for GCS uploads above the 16 MB gate. Impact: `resumable-session` endpoint deleted; `/presigned` now returns a resumable session URI for the 16-500 MB band; response shape shifted from `{upload_url, method:"PUT"}` to `{upload_session_uri, method:"RESUMABLE"}`. Frontend updated to consume the new shape.
3. Carried through from Stage 1: specced `list_buckets` connectivity probe replaced with per-object `bucket.blob(name).upload_from_string→exists→download→delete` canary (SA is bucket-object scoped).

## Truth-in-capability closure claims

- **TRANSPORT proven up to 500 MB** via GCS resumable session (chunked PUT) — R11.
- **xlsx ingest proven at ~17 MB** (24.4 MB payload, but nominal band-marker) via full E2E (upload → `/complete` → `parse_workbook` → artefact opens) — R7.
- **xlsx INGEST at 500 MB NOT PROVEN.** Stage 2 territory (`sprints/JC_STORAGE_STAGE_2_INGEST_PROFILING.md`).
- **CSV INGEST at any size NOT PROVEN** by this dispatch. Stage 2 territory.

## Rotation debt (per CREDENTIALS_NEVER_IN_CHANNEL_RULE.md)

Both SA JSON keys `8b9c...` (GCP-deleted) and `518d...` (currently-live at `/root/gcs-service-account.json`) are chat-exposed. Fresh key owed at next natural rotation opportunity — terminal-only, bundle with `JC-ADMIN-CRED-ROTATION-AND-ENV-VAR-REWIRE`. Tracked in `/app/memory/user_actions/GCS_KEY_ROTATION_OWED.md`. Standing rule remains — this-incident override does not rescind.

## Next queue (no auto-fire)

Per post-close ordering: user directs next — Stage 2 ingest profiling · A6 backend (F.6 N/A) · A9 backend (F.6 full) · A10 backend (F.6 partial) · credential rotation · other.
