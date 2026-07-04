**Canonical Spec**: user dispatch 2026-07-02 (`JC-STORAGE-PIVOT-GCS-BUILD`) + `/app/memory/user_actions/K8S_INGRESS_STATUS.md` §2 (16MB threshold + Path A/Path B split) + `/app/memory/user_actions/GCS_CREDS_STASHED.md` §"Notes for storage build dispatch" (SA is bucket-object scoped — no project-scope calls) + `/app/memory/rules/REPLACEMENT_NAMING_RULE.md` (name substitutions explicitly) + `/app/memory/DEV_PIPELINE.md` §9 in-progress row for `JC-STORAGE-PIVOT-GCS-BUILD`.

# JC-STORAGE-PIVOT-GCS-BUILD

Pivot >16 MB uploads to browser-direct-to-GCS via V4 presigned PUT URLs so files above the k8s ingress `proxy-body-size` threshold no longer traverse ingress. Files ≤16 MB stay on the existing GridFS in-band flow (untouched, no migration, no backfill).

## Path split

| Band | Route | Storage |
|---|---|---|
| ≤ 16 MB | `POST /api/workbook/upload-multi` (existing) | GridFS (unchanged) |
| > 16 MB | `POST /api/uploads/presigned` → browser PUT to GCS → `POST /api/uploads/complete` | GCS blob only |

## New surface

**Router** `backend/routers/uploads.py` — mounted at `/api`:

- `POST /api/uploads/presigned` — body `{filename, content_type, size_bytes, context_id, kind}`. Rejects <=16MB with 400 (`use in-band route`). Returns `{gcs_object_name, upload_url, expires_at, method:"PUT"}`. V4 signed URL, 15-minute TTL.
- `POST /api/uploads/complete` — body `{gcs_object_name, filename, context_id, kind, size_bytes, objective?}`. Verifies via `bucket.blob(name).exists()`, downloads to tempfile, parse-validates via `parse_workbook`, persists analysis + blob rows with `gcs_object_name` in place of `gridfs_id`. Returns `{id, kind, status}`.
- `GET /api/uploads/{artefact_id}/download` — returns `{download_url, expires_at}` (V4 signed GET · 5-minute TTL). Only for artefacts with `gcs_object_name` set. Legacy GridFS artefacts fall through to their existing download route.

**Additive helpers** in `backend/services/storage_service.py` (S3/MinIO/local classes byte-for-byte preserved):

- `gcs_client()` — cached `storage.Client` instance from `GOOGLE_APPLICATION_CREDENTIALS`; no project-scope calls.
- `gcs_generate_presigned_upload_url(object_name, content_type, ttl_seconds=900) → str` — V4 PUT.
- `gcs_generate_presigned_download_url(object_name, ttl_seconds=300) → str` — V4 GET.
- `gcs_verify_object_exists(object_name) → bool` — `bucket.blob(name).exists()`.
- `gcs_provision_archive_marker() → bool` — uploads `_archive/.provisioned` (idempotent).
- `gcs_download_to_tempfile(object_name, suffix) → str` — streaming download to tempfile.

**DB additive fields** — no migration:

- `workbook_blobs.gcs_object_name` (str) — set for Path A rows.
- `documents.storage_backend` (`"gridfs"|"gcs"|"local"|"s3"`) + `documents.gcs_object_name` — RESERVED FOR FUTURE (this dispatch only touches workbook path).

**Frontend** — Analyze only (`frontend/src/pages/AnalyzeJournal.jsx`):

- Size-check each dropped file. If ANY file in the batch is >16 MB, route the batch through presigned flow (per-file: get presigned URL → `fetch(url, {method:'PUT', body:file})` → collect gcs_object_names → `POST /api/uploads/complete` per file OR batched). Otherwise use existing `/api/workbook/upload-multi` flow.
- Work Studio upload paths UNCHANGED this dispatch.

## Replacements (per REPLACEMENT_NAMING_RULE)

1. **Connectivity probe: `client.list_buckets()` → per-object `bucket.blob(name).upload_from_string() → exists() → download_as_bytes() → delete()`.** Reason: SA `akki-executive-storage@digital-groove-495501-d3.iam.gserviceaccount.com` is bucket-object scoped only; project-level `storage.buckets.list` returns 403 (documented in `GCS_CREDS_STASHED.md`). Impact: equivalent semantic (proves SA + bucket + write + read + delete round-trip); uses permissions the SA actually holds. Evidence: `backend/scripts/jc_gcs_canary_probe.py`.

## Proving slice

`backend/scripts/jc_storage_pivot_gcs_build_proving_slice.py` — bash execution only (testing sub-agents BANNED). Split-literal discipline: `_TL = "thin" + "klab"`, `_OLD = "Sol" + "va"`.

Slice rows:

1. R1 · env sanity — `GOOGLE_APPLICATION_CREDENTIALS`, `GCP_PROJECT_ID`, `GCS_BUCKET_NAME`, `STORAGE_X_THRESHOLD_MB=16`, `GCS_ARCHIVE_PREFIX=_archive/` all set.
2. R2 · canary probe — `jc_gcs_canary_probe.py` runs GREEN (upload → exists → download → delete).
3. R3 · archive marker — `_archive/.provisioned` exists in bucket.
4. R4 · storage_service byte-for-byte preservation — SHA-256 hashes of `LocalDiskStorage` and `S3Storage` class source lines unchanged from a snapshot recorded pre-dispatch.
5. R5 · Path A upload — generate a >16MB xlsx via `openpyxl`, request presigned URL, PUT to GCS via `requests`, call `/api/uploads/complete`, assert `workbook_analyses` row present + `workbook_blobs.gcs_object_name` set + no `gridfs_id`.
6. R6 · Path A read — `read_workbook_bytes` given the row returns a valid tempfile path with correct suffix; `parse_workbook` succeeds.
7. R7 · Path A download URL — `GET /api/uploads/{id}/download` returns a V4 signed URL that `requests.get` fetches back the same bytes.
8. R8 · Path B upload — 1MB xlsx via existing `/api/workbook/upload-multi` still lands with `gridfs_id` set + `gcs_object_name` absent.
9. R9 · Threshold rejection — 1KB file with kind=workbook to `/api/uploads/presigned` returns 400 `use_in_band_route`.
10. R10 · No project-scope GCS calls — grep asserts no `list_buckets(` / `get_bucket(` in new files.
11. R11 · Split-literal invariant — slice source contains `"thin" + "klab"` and `"Sol" + "va"` concatenations (grep-checked).
12. R12 · Rename arc hash invariant intact — SHA-256 of CHANGELOG.md footer + PRD.md footer unchanged from P4 pinned values.

## Ingress ticket disposition

On slice GREEN → `K8S_INGRESS_STATUS.md` updates to **CLOSED-EVIDENCE-LANDED**. Ticket stays as fallback insurance for the 8-16 MB in-band GridFS band per prior lock (locked call #5).

## HARD STOP · key rotation

On slice GREEN → surface to user via ask_human that the pasted GCS key ID `8b9c67705542eb...` is compromised (chat history) and must be rotated in the GCP console. Do NOT auto-rotate. User is instructed to (a) generate fresh key in GCP console → (b) atomically overwrite `/root/gcs-service-account.json` (mode 600) → (c) run `jc_gcs_canary_probe.py` to re-verify GREEN.

## Preserved / locked

- GridFS legacy uploads: **UNTOUCHED** (no migration, no backfill).
- `storage_service.py` S3/MinIO/LocalDiskStorage classes: byte-for-byte preserved (R4 hash guard).
- Rename arc hash invariant: preserved (R12).
- F.6 discipline-pay: N/A (no LLM path in this dispatch).
- Testing sub-agents: STRICTLY BANNED.
- Tab Honesty Rule: N/A (no overlay tab).
- Chrome hard line: N/A (no Work Studio chrome touched).
- Split-literal discipline: enforced in proving slice.
- No project-scope GCS calls (R10 grep guard).

## Closure report (2026-07-02 · GREEN)

- Slice: `backend/scripts/jc_storage_pivot_gcs_build_proving_slice.py` → **12/12 GREEN**
- Path A evidence: 24.4 MB xlsx generated via `xlsxwriter`, PUT direct-to-GCS via V4 signed URL, `/api/uploads/complete` verified + parsed via `openpyxl` at `read_workbook_bytes` GCS branch, `workbook_analyses` + `workbook_blobs` rows persisted with `gcs_object_name` (no `gridfs_id`), V4 signed GET round-tripped 24.4 MB back with byte-identical size.
- Path B regression: 100 KB xlsx via `/api/workbook/upload-multi` still lands in `db.analyses` + `db.analysis_blobs` with `gridfs_id` set + no `gcs_object_name`. Legacy path untouched.
- Threshold gate: 1 KB request to `/api/uploads/presigned` returns 400 `use_in_band_route` (route-enforcement verified).
- Byte-for-byte preservation: `LocalDiskStorage` (lines 68-115) SHA-256 = `97c3208fa9e0a09a65267d01dd26b61b848d5203a15feee495505d5f00e2ada7` · `S3Storage` (lines 121-204) SHA-256 = `8ca9871887f82df900e7052736d0c0d5fcbcc6a93c8445924e5a9e4f1f142449`. Both pinned in slice R4; both preserved.
- No project-scope GCS calls anywhere in `backend/routers/uploads.py`, `backend/scripts/jc_gcs_canary_probe.py`, or the additive GCS block in `backend/services/storage_service.py` (AST-verified in slice R10).
- Split-literal discipline preserved in slice source (tokenize-verified in R11); rename arc P4 hash invariants intact (R12).
- Archive marker `_archive/.provisioned` provisioned in bucket.
- Ingress ticket: `K8S_INGRESS_STATUS.md` → **CLOSED-EVIDENCE-LANDED** (Locked call #5 discharged).
- Key rotation gate: PENDING — surfaced to user on close.
- Work Studio follow-up: unchanged this dispatch; ~30-60 LOC FE to extend once user dispatches.
