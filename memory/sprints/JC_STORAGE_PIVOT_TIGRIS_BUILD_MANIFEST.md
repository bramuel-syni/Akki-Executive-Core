**Canonical Spec**: `sprints/JC_STORAGE_PIVOT_TIGRIS_RESCOPE.md §4` (Path A' assumption locked at rescope surface pending user direction) + Emergent Object Store integration playbook (`integration_playbook_expert_v2` 2026-06-30) + predecessor `sprints/JC_STORAGE_PIVOT_AZURE_SAS_BUILD_MANIFEST.md` (SUPERSEDED by this manifest; retained for audit).

# JC_STORAGE_PIVOT_TIGRIS_BUILD_MANIFEST — Path A' pre-staged manifest

**Status**: PRE-STAGED (manifest only) · READ-ONLY · HARD STOP at manifest surface · assumes Path A' (built-in Tigris backend-mediated) per rescope memo §4 · pivots to `boto3` + `@aws-sdk/client-s3` shape if user chooses B'/C'
**Date**: 2026-06-30
**Predecessor**: `sprints/JC_STORAGE_PIVOT_TIGRIS_RESCOPE.md` (rescope with 3-path decomposition)
**Fires when**: user acknowledges rescope + confirms Path A' (or pivots to B'/C' triggering a manifest rewrite)

---

## §0 — Fire-trigger preconditions

| # | Precondition | Status |
|---|---|---|
| 1 | Rescope memo shipped with 3-path decomposition | ✅ `sprints/JC_STORAGE_PIVOT_TIGRIS_RESCOPE.md` |
| 2 | Quota headroom check GREEN | ✅ 0.977 GB local / 5 GB quota (§1 of rescope) |
| 3 | `EMERGENT_LLM_KEY` env var present | ✅ confirmed via `grep -c` on `backend/.env` (name-only) |
| 4 | User acknowledges rescope + confirms Path A' | ⚠️ PENDING |
| 5 | DEV_PIPELINE §9 row added BEFORE manifest | ✅ done at rescope dispatch |
| 6 | Cluster-G arc CLOSED (unrelated but tracked) | ✅ |
| 7 | Inline-blob sunset arc PAUSED at Gate A creds prerequisite | ✅ (tracked separately; sunset dispatch gated on Gate A + timer 2026-07-03) |

Preconditions 1-3 + 5-7 ✅ DONE. Precondition 4 ⚠️ USER-BLOCKING.

---

## §1 — File-by-file delta plan (LOC estimates for Path A')

### §1.1 — Backend NEW files

| Path | Status | Purpose | Est. LOC |
|---|---|---|---:|
| `backend/services/storage/__init__.py` | NEW | Package marker | ~5 |
| `backend/services/storage/tigris_client.py` | NEW | Emergent Object Store wrapper: `init_storage()`, `put_object(path, data, content_type)`, `get_object(path)`, `list_objects(prefix, max_results=1000)`. Module-global `storage_key`. `init_storage()` idempotent + re-init on 403. | ~180 |
| `backend/services/storage/_test_mock_tigris.py` | NEW | Local mock endpoint at `/_test/mock-tigris/{path}` returning Tigris-shape PUT/GET responses; in-memory dict; mounted ONLY when `STORAGE_MOCK_ENABLED=1` (default off) | ~70 |
| `backend/scripts/jc_storage_pivot_tigris_proving_slice.py` | NEW | 14-row proving slice per §6 | ~260 |

**Backend NEW subtotal**: ~515 LOC (~50 LOC less than Azure manifest due to no SAS-signer, no user-delegation-key rotation, no CORS-config helper)

### §1.2 — Backend MOD files

| Path | Status | Purpose | Est. LOC |
|---|---|---|---:|
| `backend/server.py` | MOD | Add `init_storage()` call to FastAPI startup event (5 LOC after existing MongoDB init block) | ~+5 |
| `backend/routers/workbook_analysis.py` | MOD | Add `POST /api/workbook/upload/large-file` endpoint accepting multipart form-data > 16 MB threshold; streams into `put_object`; returns `{object_ref, size, tigris_status}`; add branch to `read_workbook_bytes` that routes to Tigris when metadata carries `object_ref` (parallel to `gridfs_id` branch). Preserve GridFS-only branch for files ≤ 16 MB. | ~+90 |
| `backend/services/analysis_lifecycle.py` | MOD | Extend `build_analysis_metadata()` to accept `object_ref` (Tigris path) alongside `gridfs_id` (GridFS ObjectId); extend `read_workbook_bytes()` triple-read priority order (gridfs_id → object_ref → data_b64 legacy) | ~+45 |
| `backend/routers/workbook_analysis.py` (2nd MOD site) | MOD | Update small-file upload endpoint to enforce 16 MB threshold: if body > 16 MB, return 400 with instruction to use `/large-file` endpoint | ~+10 |

**Backend MOD subtotal**: ~+150 LOC

### §1.3 — Frontend NEW files

| Path | Status | Purpose | Est. LOC |
|---|---|---|---:|
| `frontend/src/services/large_file_upload.js` | NEW | Wrapper around `fetch('/api/workbook/upload/large-file', {method: 'POST', body: formData})` with progress events + retry on 5xx | ~95 |

**Frontend NEW subtotal**: ~95 LOC (~30 LOC less than Azure counterpart — no browser-side SAS-URL fetch step)

### §1.4 — Frontend MOD files

| Path | Status | Purpose | Est. LOC |
|---|---|---|---:|
| `frontend/src/components/WorkbookAnalyzer.jsx` | MOD | Threshold branch on file size at drop/select time: > 16 MB → `large_file_upload.js` path; ≤ 16 MB → existing in-band upload path (unchanged) | ~+35 |

**Frontend MOD subtotal**: ~+35 LOC

### §1.5 — NO NPM deps added

Path A' uses browser `fetch` + FormData — **no new npm packages needed**. Compare Azure which needed `@azure/storage-blob` (larger + adds SDK build weight).

### §1.6 — NO Python deps added

Playbook uses `requests` (already in backend). No `azure-storage-blob` needed. No `boto3` needed.

### §1.7 — Env vars

| Var | Path A' | Notes |
|---|---|---|
| `EMERGENT_LLM_KEY` | REQUIRED (already present) | Auth for `init_storage()` |
| `TIGRIS_STORAGE_URL` | OPTIONAL (default `https://integrations.emergentagent.com/objstore/api/v1/storage`) | Override for testing |
| `TIGRIS_APP_NAME` | REQUIRED (`akki`) | Path prefix for tenancy isolation |
| `STORAGE_MOCK_ENABLED` | OPTIONAL (default `0`) | Enables `_test_mock_tigris.py` local endpoint |
| `LARGE_FILE_THRESHOLD_MB` | OPTIONAL (default `16`) | X threshold from D1 |

**Sensible defaults**: no user creds needed. `EMERGENT_LLM_KEY` already in `backend/.env`. Others fall to sensible defaults.

---

## §2 — Architecture summary

```
┌─────────────────┐   POST /api/workbook/upload/large-file
│ Browser         │───────────────────────────────────────►┐
│ WorkbookAnalyzer│   (multipart form-data, streamed)      │
└─────────────────┘                                        │
                                                           ▼
                                                ┌───────────────────┐
                                                │ FastAPI backend   │
                                                │ (K8s ingress →    │
                                                │  nginx → FastAPI) │
                                                │                   │
                                                │ workbook_analysis │
                                                │   .py             │
                                                └─────────┬─────────┘
                                                          │
                                       put_object(path,   │
                                       data, ct)          ▼
                                          ┌───────────────────────────┐
                                          │ Emergent Object Store     │
                                          │ (Tigris, wrapped API at   │
                                          │ integrations.emergent.../ │
                                          │ objstore/api/v1/storage)  │
                                          │                           │
                                          │ Auth: X-Storage-Key       │
                                          │  (from init_storage()     │
                                          │   with EMERGENT_LLM_KEY)  │
                                          └───────────────────────────┘
```

**Data flow**: browser → K8s ingress → FastAPI (accepts full body) → Tigris (backend-mediated PUT via `X-Storage-Key`).

**Ingress dependency**: LOAD-BEARING for ALL files > 8 MB (nginx-ingress stock default). Path A' does NOT bypass the ingress; it flows through. **This is the CRITICAL trade-off vs Azure browser-direct-presigned.**

---

## §3 — Storage-path convention

```
akki/{context_id}/{account_id}/{uuid}.{ext}
```

- **App prefix `akki`**: playbook mandates app-name prefix for bucket collision avoidance
- **`{context_id}` + `{account_id}` prefixes**: tenancy isolation via list-prefix filter (`list_objects(prefix=f"akki/{context_id}/...")`)
- **`{uuid}.{ext}`**: UUID prevents 409 Conflict on retries; extension preserved for content-type hint

DB `workbook_blobs` row schema extension:
```python
{
    "id": "<workbook_blob_id>",
    "context_id": "<context_id>",
    "account_id": "<account_id>",
    "gridfs_id": <ObjectId or null>,     # populated for ≤ 16 MB files
    "object_ref": "<akki/.../uuid.ext>", # populated for > 16 MB files (NEW)
    "size": <bytes>,
    "content_type": "<mime>",
    "created_at": "<iso8601>",
    "is_deleted": false,                 # soft-delete flag (playbook mandate)
}
```

`gridfs_id` XOR `object_ref` invariant (both null = legacy `data_b64` row awaiting sunset; both populated = migration transient — should not persist).

---

## §4 — What's out of scope for v1 (deferred to v1.1)

| Item | Reason for deferral | Where it lives |
|---|---|---|
| 24 h staging retention on `-uploads` paths | No native Tigris lifecycle → needs backend cron sweep. Not blocking initial ship. | Deferred to `JC-STORAGE-PIVOT-TIGRIS-V1.1-LIFECYCLE` |
| Archive-path move (`akki/archive/...`) after analysis completes | Same reason (needs backend cron). Manual move helper OK for v1. | Deferred to v1.1 |
| Multi-region Tigris | Platform handles region; not agent-configurable | Deferred until residency requirement surfaces (per Azure D8 §12 pivot-vector doctrine) |

---

## §5 — Migration policy (unchanged from Azure scope)

- **Existing GridFS rows**: 100% preserved. Small files stay on GridFS per D1 threshold.
- **Files > 16 MB uploaded post-ship**: land in Tigris. Direct.
- **Legacy `data_b64` rows**: still governed by inline-blob sunset arc (see `sprints/JC_INLINE_BLOB_SUNSET_EVALUATION.md`).
- **No prod-side backfill of the 4 test-fixture files > 16 MB**: they're proving-slice artifacts; can be manually cleaned up outside this build.

---

## §6 — Proving slice spec (14 rows)

| Row | Check | Notes |
|---:|---|---|
| 1 | `init_storage()` succeeds with `EMERGENT_LLM_KEY` from `.env` | Startup-boot happy path |
| 2 | `put_object(path, b"test", "text/plain")` returns `{path, size, etag}` on 200 | Happy PUT |
| 3 | `get_object(path)` returns matching bytes + content_type | Happy GET |
| 4 | `list_objects(prefix="akki/{ctx_id}/")` returns the row from Row 2 | Tenancy prefix isolation |
| 5 | Duplicate PUT to same path returns 409; new UUID path succeeds | Playbook-mandated behavior |
| 6 | `POST /api/workbook/upload/large-file` with 20 MB CSV: 200 + `object_ref` written to `workbook_blobs` | End-to-end upload path |
| 7 | Analyze pipeline reads the Tigris blob via `read_workbook_bytes()`: bytes match input | End-to-end read path |
| 8 | Small file (5 MB) still routes to GridFS (threshold check) | Threshold branch |
| 9 | `synisense_security` defensive suite: no regression (Shield contract preserved) | F.6 discipline-pay Row #1 |
| 10 | `phase_a` real-Shield-call exercise: no regression | F.6 discipline-pay Row #2 |
| 11 | Surface ratchet unchanged `2769a08145e76744` | No new/removed routes vs baseline (large-file endpoint is NEW — ratchet updates; capture new value) |
| 12 | Invariant suite 3/3 (M1=0/M2=1 UNCHANGED FINAL) | Storage NOT in M1+M2 family |
| 13 | AST source-check: `object_ref` present in workbook_blobs schema; `read_workbook_bytes()` triple-read priority order intact | Lesson #4 |
| 14 | Log scan during 100 MB upload: 0 `413 Payload Too Large` from ingress + 0 Tigris 403/429 | Ingress annotation dependency check |

**Row 14 is the load-bearing check for the ingress annotation dependency**. If Row 14 fails with 413 → K8s ingress annotations NOT applied → sub-dispatch to apply annotations before shipping.

---

## §7 — Locked-area sweep (CLEAN at manifest surface)

Same as rescope memo §5. No product code touched at manifest surface. Locked areas cleared for the build dispatch.

---

## §8 — Discipline notes

- F.3-ADVANCE APPLIED: manifest ships alongside rescope memo, both after §9 row
- F.5 YAML-edit N/A at manifest surface (no YAML edits)
- F.6 Shield-contract discipline-pay APPLIES at build dispatch (Rows 9-10)
- G.1 poll-cadence N/A at manifest surface
- G.3-VERIFICATION AST-over-grep APPLIES at build (Row 13)
- NEW lesson #5 UNQUARANTINED runtime PASS baseline APPLIES at build (Row 1 of slice)
- NEW lesson #6 file-names-from-disk APPLIED at manifest (file paths sourced from real `ls` + playbook, not memo prose)
- Credential-hygiene: 0 raw credentials in manifest; `EMERGENT_LLM_KEY` name-only
- HARD STOP at manifest surface pending user direction confirmation

---

## §9 — Forward look

Once user confirms Path A':
1. Fire `JC-STORAGE-PIVOT-TIGRIS-BUILD` dispatch (single slug)
2. Ship all §1 files in one PR
3. Run 14-row proving slice
4. Ship to prod IF Row 14 (ingress log scan) is GREEN — else pause and re-open the K8s ingress annotation ticket

If user pivots to Path B' or C':
1. Rewrite this manifest for `boto3` + `@aws-sdk/client-s3` shape (~closer to the SUPERSEDED Azure manifest)
2. Await user BYO S3/GCS credentials via mounted secret path
3. Re-fire dispatch

---

## §10 — Cross-references

- Rescope memo: `sprints/JC_STORAGE_PIVOT_TIGRIS_RESCOPE.md`
- SUPERSEDED Azure manifest: `sprints/JC_STORAGE_PIVOT_AZURE_SAS_BUILD_MANIFEST.md`
- SUPERSEDED Azure scope: `sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md`
- K8s ingress recontextualization: `user_actions/K8S_INGRESS_STATUS.md`
- Sunset eval Gate B: `sprints/JC_INLINE_BLOB_SUNSET_EVALUATION.md §Gate B`
- Emergent Object Store integration playbook: retrieved via `integration_playbook_expert_v2` 2026-06-30
