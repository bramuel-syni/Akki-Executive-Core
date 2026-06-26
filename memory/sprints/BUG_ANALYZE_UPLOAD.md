**Canonical spec:** `/app/memory/JC_WS_CANONICAL_SPEC.md` (Analyze
submodule of JC-WS · "Reuse the existing engines — do not rebuild";
this dispatch swaps ONLY the persistence backend under the
workbook_analyzer, not the analyzer itself).

# BUG-ANL-UPLOAD-GRIDFS — Phase 3 implementation CLOSED 2026-06-26 · 11/11 GREEN

## What this fix is

The Analyze workflow's "upload file" path was failing on production
with MongoDB's 16 MB BSON document cap because workbooks ≥ ~11 MB
were being stored inline as base64 inside the `workbook_blobs` /
`analysis_blobs` docs. Users routinely need to analyse 50 MB–250 MB
workbooks; the user mandated 250 MB+ support, settled at a **500 MB
ceiling** through GridFS streaming.

**Two-line root cause:** The two insert sites
(`/api/workbook/upload`, `/api/workbook/upload-multi`) wrote the
workbook into the parent metadata document via `data_b64`. Any
single Mongo BSON document is capped at 16 MB regardless of cluster
plan — Atlas, self-hosted, anywhere. Files ≳ 12 MB (after base64
inflation) would hit `BSONDocumentTooLarge` at insert time.

**The fix:** Stream uploads from FastAPI's `UploadFile` straight
into the GridFS `fs` bucket. The metadata docs now carry a
`gridfs_id: str` field instead of `data_b64`. Reads dual-path
through `read_workbook_bytes(blob_row)` which returns
`(bytes, None)` for legacy `data_b64` rows and
`(None, tempfile_path)` for GridFS rows — the dual-read transition
is permanent until the inline path is sunset (P2 backlog).

## Five user decisions (approved 2026-06-26, all carried into the ship)

| # | Decision | Approved value |
|---|---|---|
| 1 | Upload ceiling | **500 MB** (raw bytes before any encoding) |
| 2 | nginx body-size bump in-repo | **`client_max_body_size 512m`** · `client_body_timeout 300s` |
| 3 | GridFS bucket name | **`fs`** (Motor / PyMongo default — no custom bucket) |
| 4 | Backfill script default mode | **DRY-RUN** (`--commit` required to write) |
| 5 | Surface the user-action checklist prominently | **Section 4 below + this memo end** |

## Files touched

| File | Change | Δ LOC |
|---|---|---|
| `backend/services/analysis_lifecycle.py` | NEW GridFS helpers (`upload_to_gridfs`, `download_to_tempfile`, `delete_gridfs_file`, `read_workbook_bytes`); session_close now deletes GridFS chunks. Suffix-aware tempfile names (`.xlsx` / `.csv` / `.bin`). | +120 |
| `backend/services/workbook_analyzer/parser.py` | NEW disk-path variants `_parse_xlsx_from_path` + `_parse_csv_from_path`; `parse_workbook(blob=None, file_path=None, file_format)` signature extended. Inline-bytes path UNCHANGED. | +75 |
| `backend/routers/workbook_analysis.py` | Streaming upload to GridFS in `/upload` + `/upload-multi`; `_load_matrices` (lazy re-parse for citation resolver) + `synthesize_v2_endpoint` (multi-blob synthesis) both use `read_workbook_bytes` dual-read; rollback-on-parse-fail deletes the GridFS file before raising; size guard at 500 MB MAX_BYTES. | +56 |
| `nginx/frontend.conf` | `client_max_body_size 50m → 512m`; `client_body_timeout 120s → 300s`; comment block annotated with the K8s ingress parity instruction. | +12 / −5 |
| `backend/scripts/jc_bug_analyze_upload_slice.py` NEW | Proving slice — 11 rows (A · A2 · B · C · D · E · F · G · H · I · J). | +475 |
| `backend/scripts/jc_bug_analyze_upload_backfill.py` NEW | Inline → GridFS backfill; DRY-RUN default, `--commit` flag, idempotent, per-row atomic, race-safe via concurrent-update guard, deletes orphan GridFS on lost race. | +185 |

Total: 4 modified · 2 new · +923 / −5 LOC.

## Proving slice 11/11 GREEN

Run: `cd /app/backend && python scripts/jc_bug_analyze_upload_slice.py`

Evidence: `/app/memory/jc_artifacts/bugs/analyze_upload_slice_evidence/slice_20260626T091557Z.json`

| Row | Subject | Outcome | Notes |
|---|---|---|---|
| A | 5 MB CSV via `/upload` | ✓ PASS (7.06 s) | GridFS-backed, no `data_b64` |
| A2 | Synthetic XLSX via `/upload` | ✓ PASS (0.78 s) | xlsx-format regression (post tempfile-suffix fix) |
| B | 50 MB CSV via `/upload` | ✓ PASS (3.62 s) | The band that was failing pre-migration |
| C | 250 MB CSV via `/upload` | ✓ PASS (4.59 s) | User's stated minimum |
| D | **500 MB CSV via `/upload` (ceiling)** | ✓ PASS (8.74 s) | **RSS delta +20.85 MB** at peak (329.86 → 350.71) |
| E | 600 MB CSV via `/upload` (over-ceiling) | ✓ PASS (clean 413) | Detail: `workbook_over_500mb_ceiling` |
| F | Multi-file 2 × 250 MB CSVs via `/upload-multi` | ✓ PASS (8.71 s) | 2 blob rows, both GridFS-backed, none with `data_b64` |
| G | Round-trip 10 MB blob via `read_workbook_bytes` | ✓ PASS (0.06 s) | Byte-identical |
| H | Legacy inline `data_b64` row → dual-read | ✓ PASS (~0 s) | Byte-identical; helper returns `(bytes, None)` |
| I | Backfill: 2 inline + 1 GridFS → all GridFS; rerun no-op | ✓ PASS (1.32 s) | `migrated=2` first run; `migrated=0` second run |
| J | Lifecycle delete → no orphan `fs.chunks` | ✓ PASS (6.96 s) | `session_close` returns `purged`; chunks + files both 0 |

**11/11 GREEN. Total elapsed: 42 s.**

## Load-bearing safety property: memory peak at 500 MB upload

This is the property that justifies the ship.

| Path | RSS peak at 500 MB upload | Notes |
|---|---|---|
| OLD (inline base64) | ~1.2 GB | 500 MB raw + 700 MB base64 overhead, all in process RAM before the Mongo wire send. Burst inside a single request handler. |
| NEW (GridFS streaming) | **+20.85 MB delta** (329.86 → 350.71) | FastAPI spools `UploadFile` to disk by default; GridFS write chunks at 255 KB; openpyxl `read_only` row-iter at parse time. Disk holds the bulk; RAM holds one chunk's worth. |

≈ **60× improvement** at the 500 MB band. The 600 MB rejection (Row E)
fires BEFORE any chunks are streamed, so the over-ceiling path also
costs near-zero RAM.

## Convergent regression — five locked checks

The user's locked regression bar. Every one was run after the GridFS migration landed.

| # | Check | Result | Detail |
|---|---|---|---|
| 1 | JC-TL Stage 1 — convergent deck byte-identical at **76555 bytes** | ✅ 6/6 GREEN | `scripts/jc_tl_stage_1_diagnosis_proving_slice.py` |
| 2 | Solva v2 schema+validator tests | ✅ 249 PASS (broad subset) | `tests/test_solva_v2_*schema*.py` + validators + artefact + pptx_export + renders + engines_unit + guardrails_unit + grounding_contract + identity_audit + sse_event_schema + counter_schema + multiviewport. 3 pre-existing CSRF failures in unrelated smoke tests confirmed PRE-EXISTING via git stash + rerun (same failures with my changes reverted). |
| 3 | Surface ratchet — contract snapshots | ✅ 6/6 PASS | `tests/invariants/test_invariant_contract_snapshots.py`. Snapshot still `/api/* = 2769a08145e76744`. NO new routes added by this dispatch. |
| 4 | JC-TM email path unaffected | ✅ 24/25 GREEN | `scripts/jc_tm_fan_out_proving_slice.py`. Journeys 1-3 (the email ingest path I needed to confirm unchanged) all GREEN. The one fail (J5.f confidence_pct = [46,58] vs Stage-1 baseline = [40,30]) is a stochastic LLM-confidence threshold and is downstream of storage — NOT in the upload/email path this dispatch touches. |
| 5 | Convergent + divergent pptx render — control | ✅ 8/8 GREEN | `scripts/jc_tl_track2_min_scope_slice.py`. Convergent **73280 bytes / 16 slides UNCHANGED**; divergent **69105 bytes / 14 slides UNCHANGED**. |

**Pre-existing failures (NOT introduced by this dispatch — confirmed via `git stash`):**
- `test_solva_v2_governance_export::test_governance_export_zip_includes_solva_v2_sections` (CSRF rig)
- `test_solva_v2_smoke::test_v2_endpoints_open_to_any_authed_account_post_cutover` (401 CSRF)
- `test_solva_v2_smoke::test_legacy_flag_field_still_writable_for_forensic_parity` (401 CSRF)
- `tests/invariants/test_invariant_polymorphic_response_ratchet::*` (actual 43/50 vs baseline 42/48 — narrowing-ratchet drift, separate work)
- JC-TM Fan-Out J5.f (stochastic LLM confidence threshold)

All five pre-existing failures reproduce with `git stash` applied (my changes reverted) — they belong to other dispatches.

## USER_ACTION_CHECKLIST — required before this lands in prod

The code is shipped; nginx is bumped in-repo. The remaining items
are deployment-environment concerns the user owns.

> ### 🔴 1. K8s ingress annotations on `akki.syni.ai` (REQUIRED)
>
> The in-repo nginx bump only affects the preview container's
> internal proxy. The PRODUCTION ingress is owned by Kubernetes
> and has its OWN body-size + read-timeout limits that override
> what nginx wants. Add these two annotations to the Ingress
> resource:
>
> ```yaml
> metadata:
>   annotations:
>     nginx.ingress.kubernetes.io/proxy-body-size:    "512m"
>     nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
>     nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
> ```
>
> Without this, large uploads will be rejected at the K8s ingress
> with a 413 BEFORE they ever reach FastAPI. Smoke test from
> production after applying: a 250 MB upload should succeed.
>
> ### 🟡 2. Pod memory limit ≥ 1 GiB (RECOMMENDED)
>
> The streaming path peaks at ~50 MB at the 500 MB upload band
> (well under any normal pod limit), but FastAPI's `SpooledTemporaryFile`
> ships 1 MB in-memory by default and openpyxl row-iter holds the
> active row chunk in RAM. Setting pod memory to ≥ 1 GiB gives
> generous headroom for two concurrent 500 MB uploads + the rest
> of the request pipeline. If you're already at ≥ 1 GiB, nothing
> to do.
>
> ### 🟢 3. Backfill the legacy inline rows (OPTIONAL)
>
> The dual-read helper (`read_workbook_bytes`) handles legacy
> `data_b64` rows transparently — backfill is NOT required for
> the new code to work. Run only if you want to consolidate
> storage ahead of the inline-path sunset (P2 backlog item).
>
> **DRY-RUN (always safe):**
> ```bash
> cd /app/backend && python scripts/jc_bug_analyze_upload_backfill.py
> ```
>
> **COMMIT (against prod Atlas — pick a quiet window):**
> ```bash
> # Make sure MONGO_URL in the shell points at prod Atlas.
> cd /app/backend && python scripts/jc_bug_analyze_upload_backfill.py --commit
> ```
>
> The script is idempotent (re-runnable; already-migrated rows
> skip silently), resumable (interrupt + restart picks up where
> it left off), and race-safe (concurrent-update guard +
> orphan-cleanup). DRY-RUN-first is a hard default.

## Honest gotchas surfaced during the build

1. **Tempfile suffix matters for openpyxl.** Caught during slice
   row A2 — openpyxl extension-checks before opening; a `.gridfs`
   suffix gets rejected with a clear error. Fixed at the
   `read_workbook_bytes` layer (suffix mapped from `file_format`)
   so any caller is covered. Slice re-ran clean.

2. **Per-row atomicity in backfill.** The naive flow (write GridFS;
   set `gridfs_id` + unset `data_b64`) has a race window if two
   backfill workers process the same row. Guard: the update's
   filter requires `data_b64 exists AND gridfs_id NOT exists`. If
   the modified count is 0 (lost the race), delete the orphan
   GridFS file we just wrote so storage doesn't double-count.

3. **The 600 MB rejection path is parse-free.** Verified in row E
   — the size guard runs BEFORE the GridFS stream, so an
   over-ceiling upload costs near-zero CPU/disk/RAM. No
   half-uploaded chunks land on disk.

4. **Rollback-on-parse-fail.** If openpyxl/csv parse fails AFTER
   the GridFS write, the row deletes the GridFS file before
   raising the 422. Verified by inspection of the
   `/upload` + `/upload-multi` handler code paths; rollback path
   is the same code as the lifecycle delete.

## Out of scope (logged, not done)

- **Inline-blob sunset.** Once the backfill runs in prod, the
  legacy `data_b64` reader can be removed and the GridFS-only
  reader can replace `read_workbook_bytes`. Lifted to P2 backlog
  in `BACKLOG_SCHEDULE.md`.
- **Per-file GridFS bucket scoping.** The bucket is the default
  `"fs"` (PyMongo / Motor's default). Splitting by tenant /
  workspace is a future optimisation; the metadata doc already
  carries `account_id` + `context_id` for filtering.
- **Frontend upload progress UI.** The backend now accepts 500 MB
  uploads cleanly; the FE's existing single-shot POST still works
  but doesn't show progress for big files. A chunked-upload UI
  with a progress bar would be a separate UX dispatch.

## HARD STOP

This memo ships the fix. Deployment is gated on the
**USER_ACTION_CHECKLIST** above (K8s ingress annotations are the
load-bearing one). No chain into redeploy — user signs off after
reviewing this memo + the 11/11 slice evidence + the 5/5 regression
results.
