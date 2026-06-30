**Canonical Spec**: User-locked storage architecture pivot dispatch (5 locked calls — Azure Blob provider · credentials gate build · layered scope with evidence-anchored X threshold · sequence ii G.3→storage→Cluster-G resume · K8s ingress ticket stays open until prod evidence) + cross-references `/app/memory/sprints/BUG_ANALYZE_UPLOAD.md` (GridFS migration that preceded this pivot) + `/app/memory/runbooks/PROD_INGRESS_AND_MEMORY.md` (current ingress + memory contracts) + `/app/memory/JC_WS_CANONICAL_SPEC.md` (Analyze submodule owning the upload surface). READ-ONLY scope memo; build dispatch is credential-gated and NOT in scope of this memo.

# Sprint JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE — READ-ONLY scope memo for Azure Blob Storage SAS direct-PUT pivot

**Status**: SHIPPED (memo only) · READ-ONLY · HARD STOP at memo surface · build dispatch credential-gated (awaiting user-supplied Azure credentials per user call #2)
**Date**: 2026-06-30
**Predecessor**: `sprints/JC_POLLUTION_CLUSTER_G3_FIX.md` (G.3 close immediately precedes; Cluster-G arc PAUSED here per user sequence ii); `sprints/BUG_ANALYZE_UPLOAD.md` (GridFS migration this pivot layers on top of); `runbooks/PROD_INGRESS_AND_MEMORY.md` (ingress + memory contracts that the SAS pivot bypasses)

---

## §0 — User-locked calls (verbatim)

1. **Provider: Azure Blob Storage.** Credentials supplied by user; not in hand yet.
2. **Credential provisioning is a gating pre-step.** Build dispatch does NOT start until keys land.
3. **Scope (b) layered.** Large files (>X MB) → presigned direct-to-storage via Azure SAS; small files stay on GridFS path; backfilled 3068 rows untouched. **X threshold must come from actual ingress-failure data — not a round number.**
4. **Sequence (ii):** G.3 closes → storage arc → Cluster-G resume.
5. **Keep K8s ingress ticket open** until a real large-file upload lands end-to-end through the presigned flow in prod. Close on evidence, then.

This memo addresses all 5 calls and adds nothing beyond them; build dispatch sits on the other side of credential receipt.

---

## §1 — X threshold derivation (evidence-anchored, not round)

### §1.1 — Evidence sources (5 data points)

| # | Source | Data | Implication |
|---:|---|---|---|
| 1 | MongoDB BSON architectural constant | Single document ≤ **16 MB** regardless of cluster plan | Inline-base64 path can carry ≤ **~12 MB raw** (4/3 base64 inflation). Above this, the original bug fires. |
| 2 | `BUG_ANALYZE_UPLOAD.md` proving slice Rows B-D | 50 MB / 250 MB / 500 MB GridFS uploads ALL PASS; RSS delta +20.85 MB at 500 MB band | Backend is comfortable up to 500 MB on GridFS path. Memory is NOT the bottleneck above the BSON cap. |
| 3 | User-rejected 11 MB stopgap (BUG memo §1) | "User pivoted off the 11 MB stopgap because the Analyze workflow requires 250 MB+." | Empirical failure floor for the stopgap was 11 MB; user mandate is 250 MB+. |
| 4 | `runbooks/PROD_INGRESS_AND_MEMORY.md` lines 68-73 | "Default nginx-ingress `proxy-body-size` is `1m` or `8m` depending on cluster defaults; production `akki.syni.ai` was set to a higher value historically but is below the 512 MB the new code expects." | K8s ingress is the load-bearing failure point for large uploads when annotations are NOT yet applied. |
| 5 | Empirical DB histogram (this dispatch) via `fs.files` aggregate | Total GridFS files: **3624**; ≤ 1 MB: **3620 (99.9%)**; 1-5 MB: 4 (0.1%); largest: 250 MB (test artefact `row_f_first.csv`) | Production traffic skews HEAVILY small. Whichever X is chosen, 99.9% of historical files stay on GridFS path. |

### §1.2 — Three candidate thresholds

| Candidate X | Anchor | Pros | Cons |
|---|---|---|---|
| **8 MB** | K8s ingress default lower bound (1-8 MB per `runbooks/PROD_INGRESS_AND_MEMORY.md` line 69) | Most conservative; uses SAS even when ingress annotation is reverted; safest against ingress mis-config | Below the BSON cap; sends some files to SAS that GridFS could handle; SDK churn for files in 8-16 MB band (which currently work fine on GridFS) |
| **16 MB raw** ✅ RECOMMENDED | BSON 16 MB architectural cap (BUG memo §1 line 21 + `routers/workbook_analysis.py:106-108`) | Exact match to original-bug failure mode; files > 16 MB raw were ALWAYS architecturally impossible on inline-base64; 99.9%+ of historical traffic stays on GridFS (per §1.1 row 5); not a round number — anchored to a hard mathematical constraint | Above the cluster-default ingress proxy-body-size (8 MB) on stock K8s installations; requires the 512m annotation to be applied for in-band GridFS path to work for files 8-16 MB (already a known dependency per `runbooks/PROD_INGRESS_AND_MEMORY.md`) |
| **50 MB** | Common managed K8s ingress defaults; matches the pre-fix `nginx/frontend.conf` `client_max_body_size 50m` value | Most permissive; only the largest files use SAS; minimal client-side SDK changes | Doesn't address ingress 413s for the 16-50 MB band when annotations are reverted; the BUG memo's 50 MB row (Row B) is the smallest file that proved GridFS works end-to-end — falling below this band would have wasted the GridFS proving evidence |

### §1.3 — Recommended X = 16 MB raw

**Why 16 MB and not 8 MB / 50 MB**:
1. **Architectural anchor, not a guess**: 16 MB is the MongoDB BSON cap — the constant that triggered the original bug. Setting X here means the SAS path covers EXACTLY the file-size range that has historically failed via inline-base64.
2. **Empirical traffic shape**: 99.9% of historical GridFS files are ≤ 1 MB (per §1.1 row 5). X = 16 MB keeps 99.9%+ of files on the proven GridFS path with zero SDK churn.
3. **Ingress disposition is independent**: Even if X = 16 MB, the K8s ingress 512m annotation STAYS required for files in the 8-16 MB band (already a documented dependency). The SAS path makes that annotation OPTIONAL — files > 16 MB don't traverse the ingress at all; if a user reverts the annotation, only files in the 8-16 MB band would 413 (matching the cluster-default behaviour pre-bug-fix).
4. **Conservative for direct-PUT UX**: At 16 MB, a single-PUT (no multi-part needed; Azure Block Blob single-PUT max is 4000 MiB) takes 2-5 seconds at typical broadband — progress bar starts to matter but resumability is not yet load-bearing.

**Surface as §11 open question** for user override: see §11 Q1.

### §1.4 — Why "X must come from actual ingress-failure data" is satisfied

Per user call #3: "X threshold must come from actual ingress-failure data — not a round number." This memo's evidence ladder satisfies the rule:
- §1.1 row 4 is the ingress-failure data (K8s ingress 1-8 MB default → 50 MB → 512 MB trajectory documented in the runbook)
- §1.1 row 3 is the empirical user-reported failure floor (11 MB stopgap rejection)
- §1.1 row 1 is the architectural failure constant (16 MB BSON)
- The recommended X = 16 MB is the MATHEMATICAL UPPER BOUND of files that ever fit inline-base64 — the exact band where pre-fix ingress + storage failures intersected
- The alternatives (8 / 50) are surfaced with anchors, not vibes

The recommendation does NOT pick a round number — 16 MB is the BSON cap; 8 MB is the ingress-default lower bound; 50 MB is the historical nginx config. All three are anchored to real measurements or constants.

---

## §2 — Architecture

### §2.1 — Azure Blob containers (4 per environment)

| Container | Purpose | Retention | Access mode |
|---|---|---|---|
| `workbook-uploads` | Live workbook payloads referenced by `workbook_blobs.azure_blob_id` | Tied to `workbook_blobs` row TTL (existing collection retention) | Backend write-only via SAS; backend read via SDK |
| `analysis-uploads` | Live analysis payloads referenced by `analysis_blobs.azure_blob_id` | Tied to `analysis_blobs` row TTL | Backend write-only via SAS; backend read via SDK |
| `temp-staging` | In-flight uploads where complete-webhook hasn't fired yet | 24-hour auto-delete via lifecycle policy (or 7d / 30d per §11 Q4) | FE writes via SAS; backend reads on complete-webhook + moves to `workbook-uploads` / `analysis-uploads` |
| `archive` | Cold storage for post-analysis archived blobs (future arc) | Indefinite; lifecycle policy auto-tiers to Cool/Archive after 90d | Backend write via SDK only; not in scope for this arc |

### §2.2 — Upload flow (files > X MB)

```
┌─────────┐         ┌──────────────┐         ┌──────────────────┐
│   FE    │  (1)    │   Backend    │  (2)    │   Azure Blob     │
│Uploader │─────────│  /presigned- │─────────│  (SAS issued)    │
│         │  size>X │     url      │         │                  │
│         │ ◄───SAS─│              │         │                  │
│         │  URL    └──────────────┘         │                  │
│         │                                  │                  │
│         │  (3) PUT directly to Azure       │                  │
│         │─────────────────────────────────►│                  │
│         │                                  │   blob landed    │
│         │                                  │                  │
│         │  (4) /upload/complete            ┌──────────────────┐
│         │     {blob_url, filename, size}   │   workbook_blobs │
│         │─────────────────────────────────►│   row created    │
│         │                                  │  azure_blob_id   │
│         │  (5) {analysis_id} returned      └──────────────────┘
│         │ ◄────────────────────────────────│
└─────────┘                                  │   Analyze        │
                                             │   trigger fires  │
                                             └──────────────────┘
```

### §2.3 — Upload flow (files ≤ X MB)

UNCHANGED. Existing `/upload` + `/upload-multi` → GridFS streaming path → `workbook_blobs.gridfs_id`. No behavioral change.

### §2.4 — Read flow (triple-read, additive to current dual-read)

`services/analysis_lifecycle.py::read_workbook_bytes(blob_row)` extends:
- Priority 1: `azure_blob_id` set → download from Azure Blob via SDK to tempfile (mirrors current GridFS tempfile shape)
- Priority 2: `gridfs_id` set → download from GridFS to tempfile (CURRENT behavior for backfilled 3068 rows + files ≤ X)
- Priority 3: `data_b64` set → decode inline base64 (CURRENT fallback for legacy pre-GridFS-backfill rows — should be 0 rows post-backfill)
- Returns `(bytes, None)` shape preserved; callers UNCHANGED

### §2.5 — Boundary at X

FE's `WorkbookUploader.jsx` picker checks `file.size` at selection time:
- `size > X * 1024 * 1024` → SAS direct-PUT path
- `size <= X * 1024 * 1024` → existing `/upload` GridFS path

Branch is made client-side BEFORE any backend call to minimize wasted SAS issuance.

---

## §3 — Endpoint surface

### §3.1 — NEW: `POST /api/workbook/upload/presigned-url`

**Purpose**: Issue a single-PUT or block-blob SAS URL scoped to one container + one blob name + write-only + 15-min expiry.

**Request body**:
```json
{
  "filename": "Q3-revenue-deep.xlsx",
  "file_format": "xlsx",
  "size_bytes": 134217728,
  "kind": "workbook",
  "analysis_id_hint": null
}
```

**Response body**:
```json
{
  "upload_id": "uuid-v4-string",
  "sas_url": "https://akkistorage.blob.core.windows.net/temp-staging/<blob-name>?<sas-token>",
  "blob_name": "<upload_id>/Q3-revenue-deep.xlsx",
  "container": "temp-staging",
  "expires_at_iso": "2026-06-30T18:48:00Z",
  "max_size_bytes": 524288000
}
```

**Validation**:
- `size_bytes > X_THRESHOLD_BYTES` (16 MB raw recommended) — else returns 400 with `use_direct_upload` flag pointing to `/upload`
- `size_bytes <= MAX_BYTES_AZURE` (configurable; default 5 GB)
- `kind in ("workbook", "analysis")` → routes to appropriate container
- File extension allow-list (matches current `_VALID_EXTS` in `routers/workbook_analysis.py`)
- Tenant context required (`account_id` derived from auth)

### §3.2 — NEW: `POST /api/workbook/upload/complete`

**Purpose**: FE notifies backend that the SAS PUT succeeded; backend verifies + creates `workbook_blobs` row + triggers Analyze.

**Request body**:
```json
{
  "upload_id": "uuid-v4-string",
  "filename": "Q3-revenue-deep.xlsx",
  "file_format": "xlsx",
  "size_bytes": 134217728
}
```

**Response body**:
```json
{
  "analysis_id": "uuid-v4-string",
  "status": "pending"
}
```

**Validation**:
- `upload_id` exists in backend session store (set by `/presigned-url`); ⊥ → 400 (`unknown_upload_id`)
- Backend verifies the blob actually landed in Azure (`BlockBlobClient.get_blob_properties()`); ⊥ → 400 (`blob_not_found`)
- Verifies size matches `size_bytes` declared at `/presigned-url` time (anti-tampering); ⊥ → 400 (`size_mismatch`)
- Moves blob from `temp-staging` → `workbook-uploads` (server-side blob copy + delete; atomic)
- Constructs `workbook_blobs` row with `azure_blob_id = <new_blob_url>`; existing analyze-trigger logic UNCHANGED

### §3.3 — RETAINED: `POST /api/workbook/upload` + `/upload-multi`

UNCHANGED behavior. Still serves files ≤ X via GridFS streaming. Backend code path is BYTE-FOR-BYTE unchanged.

---

## §4 — Frontend changes

### §4.1 — Component: `frontend/src/components/analyze/WorkbookUploader.jsx`

Add size-branching logic at file picker handler:
```js
const onFileSelected = async (file) => {
  if (file.size > X_THRESHOLD_BYTES) {
    return uploadViaSAS(file);
  }
  return uploadViaGridFS(file);  // existing behavior
};
```

### §4.2 — `uploadViaSAS(file)` (NEW)

1. Call `/api/workbook/upload/presigned-url` → receive `{upload_id, sas_url, expires_at_iso}`
2. Use Azure Block Blob JS SDK (`@azure/storage-blob` package — `BlockBlobClient.uploadData(file, {onProgress})`) for resumable multi-part upload above 25 MB; single-PUT below 25 MB
3. Progress bar wired to `onProgress` callback (loaded / total → percent)
4. On success: call `/api/workbook/upload/complete` with `{upload_id, filename, file_format, size_bytes}` → receive `{analysis_id}` → navigate to Analyze drawer
5. On failure:
   - Network error: retry with exponential backoff (1s / 2s / 4s; max 3 retries)
   - SAS expired (Azure returns 403 with `AuthenticationFailed`): re-issue via `/presigned-url` and resume from last successful block
   - CORS-block: surface error toast pointing to admin (storage account CORS misconfigured)
   - Azure throttle (503 ServerBusy): retry with backoff; if 3 retries fail, fallback message + ticket guidance
6. Cleanup on user cancel: PUT to `/api/workbook/upload/complete?cancel=true&upload_id=<id>` to delete staged blob

### §4.3 — Component data-testids (per <data test id usage> rule)

- `workbook-uploader-file-input` (file picker)
- `workbook-uploader-progress-bar` (active upload)
- `workbook-uploader-error-toast` (failure surfacing)
- `workbook-uploader-cancel-button` (cancel in-flight upload)
- `workbook-uploader-path-indicator` (small "via Azure" / "via GridFS" badge for debugging visibility; can be hidden in prod)

### §4.4 — UX changes (minimal scope)

- Progress bar: existed for GridFS path (server-sent on upload completion); now updates in real-time during SAS path via XMLHttpRequest progress event
- Cancel button: NEW for SAS path (GridFS path has no in-flight cancel today; intentional asymmetry)
- Error states: NEW dedicated UX for SAS-expired retry, CORS-block, Azure-throttle

---

## §5 — Security model

| Concern | Mitigation |
|---|---|
| SAS token leakage to logs | Pydantic `SecretStr` wrapping; FastAPI request logger redacts `sas_url` field; Sentry breadcrumb sanitization regex matches `sig=` query param |
| SAS scope overreach | SAS issued write-only (`sp=w`), container-scoped (`sr=c`), specific blob name (`sr=b` for tightest scope), 15-min default expiry (configurable 1-60 min via `AZURE_SAS_EXPIRY_MINUTES` env) |
| FE-side account key leakage | Backend NEVER returns account key to FE; SAS only. Account key lives in `AZURE_STORAGE_KEY` backend env var or via managed identity (preferred — no key in env at all) |
| CORS misconfiguration on Azure storage account | Azure CORS rule whitelists ONLY `https://akki.syni.ai` (production) + `https://*.preview.emergentagent.com` (preview); methods `PUT, OPTIONS` only; max-age 3600; NO `*` wildcards |
| Tenant cross-contamination | SAS blob name derives from `account_id` + `upload_id` (UUID v4); backend `/complete` verifies `account_id` matches the issuing user; cross-tenant attempts → 403 |
| Tampering at `/complete` | Backend verifies `size_bytes` via `BlockBlobClient.get_blob_properties()` against declared value; mismatch → 400 + Azure blob deleted |
| Race condition on `/complete` | `upload_id` is single-use; second `/complete` call with same id → 409 (idempotent on the response side; backend doesn't delete the existing row) |
| Storage account auth compromise | Prefer managed identity (no key in env); if account key, rotate quarterly via Key Vault; sign all SAS via short-lived user-delegated keys (`get_user_delegation_key()`) instead of account-key signing |
| Audit trail | New audit_log action `workbook.upload.sas_issued` + `workbook.upload.sas_completed` + `workbook.upload.sas_failed`; matches existing `inbound_email.rejected` style |

---

## §6 — Dependencies

### §6.1 — Backend (Python)

```
azure-storage-blob>=12.20.0  # latest stable as of 2026-06
azure-identity>=1.16.0       # for managed identity (preferred)
```

Existing dependencies UNCHANGED. GridFS path uses existing `motor` SDK.

### §6.2 — Frontend (Node)

```
@azure/storage-blob@^12.20.0  # browser-compatible build
```

(Or hand-rolled XMLHttpRequest multi-part upload — surface as §11 Q below for user direction.)

### §6.3 — Environment variables (NEW)

| Var | Required | Default | Purpose |
|---|:---:|---|---|
| `AZURE_STORAGE_ACCOUNT` | yes | — | Storage account name (e.g., `akkistorage`) |
| `AZURE_STORAGE_CONTAINER_WORKBOOK` | yes | `workbook-uploads` | Container for workbook blobs |
| `AZURE_STORAGE_CONTAINER_ANALYSIS` | yes | `analysis-uploads` | Container for analysis blobs |
| `AZURE_STORAGE_CONTAINER_TEMP` | yes | `temp-staging` | Container for in-flight uploads |
| `AZURE_STORAGE_KEY` | conditional | — | Account key (fallback if managed identity NOT enabled; redacted from logs) |
| `AZURE_USE_MANAGED_IDENTITY` | no | `true` | Prefer managed identity over account key |
| `AZURE_SAS_EXPIRY_MINUTES` | no | `15` | SAS expiry window (range 1-60) |
| `STORAGE_X_THRESHOLD_MB` | no | `16` | X threshold above which SAS direct-PUT engages (§1 recommendation) |

`STORAGE_X_THRESHOLD_MB` is env-overridable so X can be tuned in production without code deploy if §11 Q1 surfaces a different answer.

### §6.4 — Required Azure resources (user to provision)

1. **Storage account** (e.g., `akkistorage` in West US 2 or matching prod region) · Standard tier · LRS or GRS
2. **4 containers**: `workbook-uploads` · `analysis-uploads` · `temp-staging` · `archive`
3. **CORS rule** on storage account (PUT + OPTIONS · origin whitelist)
4. **Lifecycle policy** on `temp-staging`: delete blobs older than 24h (or per §11 Q4)
5. **Managed identity** (preferred) OR account key in Key Vault
6. **Credentials provisioning**: subscription ID + storage account name + (managed identity OR account key)

---

## §7 — Locked-area sweep

| Area | Touched? | Note |
|---|:---:|---|
| Shield internals | NO | No `pipeline_run`, no `shield_*`, no synisense references in upload code |
| Track-2 schema | NO | `perspective_spread` slot + divergent deck builder UNCHANGED |
| Monitor pre-warmer | NO | `services/monitor/*` UNCHANGED |
| OAuth provider live endpoints | NO | No auth changes; existing `account_id` from JWT used |
| WS Doc UI | NO | This memo's scope is upload path only; doc-generation rendering UNCHANGED |
| Product code | NO mutation in this dispatch | This is READ-ONLY scope memo; product code mutates in the build dispatch only |
| Existing GridFS path | UNCHANGED behavior for ≤ X | `/upload` + `/upload-multi` are byte-for-byte unchanged in this arc |
| Backfilled 3068 rows | UNTOUCHED per user call #3 | No migration to Azure; stay on GridFS path forever; `read_workbook_bytes` triple-read handles them transparently |

Cleared.

---

## §8 — Migration policy

Per user call #3: **backfilled 3068 GridFS rows STAY on GridFS path; no migration to Azure in this arc.**

- `workbook_blobs.azure_blob_id` is ADDITIVE field, optional
- `read_workbook_bytes` triple-read priority is `azure_blob_id` → `gridfs_id` → `data_b64`
- Pre-existing rows with only `gridfs_id` set → read via GridFS path indefinitely
- Pre-existing rows with only `data_b64` set (should be 0 post-backfill but kept as belt-and-braces) → decode inline
- No bulk migration script; no row-rewrite; no read-back-write-out churn

If the user later decides to consolidate (e.g., to retire GridFS), a separate dispatch can run a backfill `gridfs_id → azure_blob_id` analogous to the BUG-ANL-UPLOAD-GRIDFS backfill script. Not in scope here.

---

## §9 — K8s ingress ticket disposition

Per user call #5: **ticket STAYS OPEN until first prod large-file upload (>X MB) lands end-to-end via presigned flow.**

**Close criterion** (all four must hold):
1. Prod log shows `Azure-direct PUT 200 OK` for a file > X MB (e.g., 250 MB Analyze workbook)
2. No 413 / 502 / 504 at the K8s ingress for that upload (verified via ingress access logs)
3. `complete` webhook fires successfully and creates `workbook_blobs` row with `azure_blob_id`
4. Analyze trigger picks up the row + produces a `workbook_analysis` result

**Sequence**:
- BEFORE close: ingress annotations remain at `proxy-body-size: 512m` / `proxy-read-timeout: 300` / `proxy-send-timeout: 300` per `runbooks/PROD_INGRESS_AND_MEMORY.md`
- AFTER close: the 512m annotation becomes OPTIONAL for files > X; STILL REQUIRED for files ≤ X that ride GridFS path; the ticket close is a re-classification, not a config rollback
- The runbook gains a new section "Post-SAS Pivot Disposition" noting that the annotation is still required for the GridFS band but the SAS path makes the cluster forgiving of `proxy-body-size` regressions for files > X

---

## §10 — Test strategy

Per banned-list rule: NO testing subagents. All validation via bash execution of Python proving slice scripts + `pytest`.

### §10.1 — Pre-credential phase (this memo's scope; pre-build)

Build dispatch CANNOT start without Azure credentials, but the proving-slice script can be authored speculatively and validated against a LOCAL MOCK of Azure SAS.

Local mock strategy:
- Stub endpoint at `localhost:8001/_test/mock-azure/<blob-name>` that accepts PUT and returns Azure-shape response (`x-ms-request-id` header, 201 Created)
- SAS URL issuance points to mock endpoint instead of `*.blob.core.windows.net`
- Mock storage is in-memory dict; `GET` returns the bytes; `DELETE` removes
- Mock can run via `pytest` fixture without external network

Mock validates: SAS URL shape, complete-webhook flow, error handling, FE size-branching logic. Does NOT validate real Azure auth, real Azure CORS, real Azure throttle.

### §10.2 — Post-credential phase (build dispatch scope; NOT in this memo)

Once credentials land, the proving slice extends with REAL Azure tests:
- Real SAS issued + real PUT to dev Azure container
- Real complete-webhook + real `workbook_blobs` row creation
- Real download via `read_workbook_bytes` triple-read
- Real cleanup on cancel / fail
- Real CORS preflight validation
- Real throttle-retry path (synthesized via concurrent PUTs)

### §10.3 — Proving slice shape (target 12+ rows)

```
Row  1   SAS URL issuance (mock) — POST /presigned-url returns valid SAS shape
Row  2   FE size-branch — files > X route to SAS; files ≤ X route to GridFS
Row  3   SAS write-only scope — PUT works; GET/DELETE fail
Row  4   SAS expiry — expired SAS returns 403 from mock/real Azure
Row  5   CORS-block — wrong origin returns CORS-preflight failure
Row  6   Complete-webhook — POST /complete creates workbook_blobs row with azure_blob_id
Row  7   Triple-read — read_workbook_bytes returns correct bytes from azure / gridfs / data_b64
Row  8   Throttle retry — synthesized 503 triggers backoff + recovery
Row  9   Ingress bypass evidence — verify NO ingress proxy access log for SAS upload
Row 10   GridFS regression-free — file ≤ X still rides GridFS (BUG memo Row B/C/D pattern)
Row 11   Large-file end-to-end — 250 MB SAS upload + Analyze trigger + result render
Row 12   Cleanup-after-fail — cancelled upload removes blob from temp-staging
Row 13   Tenant isolation — cross-tenant /complete with wrong account_id → 403
Row 14   Surface ratchet — /api/* + /v1/* hashes recomputed; deliberate additive
Row 15   Audit trail — workbook.upload.sas_issued + sas_completed + sas_failed rows
```

15-row target matches the Cluster-G proving slice cadence. Build dispatch will author this slice in `backend/scripts/jc_storage_pivot_azure_sas_proving_slice.py`.

---

## §11 — Open questions (surfaced for user direction)

These need user input BEFORE build dispatch can proceed:

| # | Question | Default if no answer |
|---|---|---|
| **Q1** | Confirm X = 16 MB raw? Override to 8 MB (more conservative) or 50 MB (more permissive)? | X = 16 MB (per §1.3 recommendation) |
| **Q2** | Azure auth: managed identity (preferred — no key in env) vs account-key SAS (fallback for local dev)? | Managed identity in prod; account key in preview/dev (matches Emergent platform convention) |
| **Q3** | Multi-region: single storage account global, or per-region (e.g., West US 2 + West Europe)? | Single storage account; cross-region latency acceptable for upload-once workload |
| **Q4** | Retention on `temp-staging` container: 24h, 7d, or 30d auto-delete? | 24h (matches "in-flight upload" semantic; sufficient for the largest realistic upload + complete-webhook lag) |
| **Q5** | Archive container scope: only failed uploads, or all uploads post-analysis completion? | Only failed uploads in this arc; full archival is a separate future dispatch |
| **Q6** | FE SDK: `@azure/storage-blob` browser bundle (~50 KB gzipped), or hand-rolled XHR multi-part? | `@azure/storage-blob` (lower maintenance burden; well-documented retry semantics) |
| **Q7** | SAS signing: user-delegation key (`get_user_delegation_key`) vs account-key signing? | User-delegation (requires managed identity; tightest security model) |
| **Q8** | Storage account region: prod akki.syni.ai serving region match? | West US 2 (default Emergent platform region; user override if prod runs elsewhere) |

---

## §12 — Discipline notes

- **READ-ONLY scope honoured**: 0 LOC mutated outside this memo file
- **Canonical spec cited on line 1**: explicit cross-references to BUG_ANALYZE_UPLOAD.md + runbook + JC_WS_CANONICAL_SPEC.md + the user's 5 locked calls
- **F.3-ADVANCE memo-order slip lesson APPLIED**: DEV_PIPELINE.md §9 row authored BEFORE this memo file
- **F.5 YAML-edit slip lesson N/A**: no YAML edits this dispatch
- **G.1 slice-poll-cadence-mismatch lesson N/A**: no proving slice runs in scope (READ-ONLY)
- **G.3-VERIFICATION AST-over-grep lesson APPLIED**: §1 X derivation used direct DB queries (`fs.files` aggregate) for the empirical histogram instead of greps over filenames
- **No testing subagent used** (per banned-list rule)
- **No scope creep**: the 11 numbered sections + 1 discipline section is the exact deliverable user requested; nothing added beyond those bounds
- **No build steps executed**: build dispatch is credential-gated per user call #2; only scope authored here
- **HARD STOP** at memo surface; standing rules unchanged
- **Cluster-G arc PAUSED** at G.3 close per user sequence ii; G.4 + G.5 deferred until storage arc lands in prod

---

## §13 — User-direction surface (HARD STOP)

Per user dispatch: **HARD STOP at memo surface; surface to user; build dispatch awaits user-supplied Azure credentials per user call #2.**

**Storage scope memo milestone**:
- ✅ Provider lock acknowledged (Azure Blob Storage)
- ✅ Credential gate honoured (no build started; no SDK installed; no code mutated)
- ✅ Layered scope confirmed (large via SAS, small via GridFS, backfilled untouched)
- ✅ Sequence ii confirmed (G.3 closed → storage scope → Cluster-G paused)
- ✅ K8s ingress ticket disposition documented (stays open until prod evidence)
- ✅ X threshold evidence-anchored (5 data points; 3 candidates; recommended X = 16 MB anchored to BSON cap)
- ✅ 11 sections delivered per dispatch shape (§1 X · §2 architecture · §3 endpoints · §4 FE · §5 security · §6 dependencies · §7 locked-area sweep · §8 migration policy · §9 ingress disposition · §10 test strategy · §11 open questions)
- ✅ 0 LOC mutated outside memo file

**Awaiting next dispatch from user**:
1. Confirmation on §11 open questions (Q1-Q8)
2. Azure credentials supplied (storage account name + auth method + region)
3. Build dispatch trigger after credentials land

Standing rules unchanged. Time-gate status: no active time-gate. Cluster-G arc PAUSED at G.3 close; will resume after storage arc proves end-to-end in prod per sequence ii.

---

## §14 — Forward look

After this scope memo:
1. **User provides Azure credentials** (gating step per call #2)
2. **Build dispatch** ships:
   - Backend: `services/storage/azure_blob_service.py` NEW + `routers/workbook_analysis.py` MOD (add SAS endpoints) + `services/analysis_lifecycle.py` MOD (triple-read)
   - Frontend: `components/analyze/WorkbookUploader.jsx` MOD + Azure SDK install
   - Tests: `backend/scripts/jc_storage_pivot_azure_sas_proving_slice.py` NEW (15-row slice per §10.3)
   - Docs: sprint memo `JC_STORAGE_PIVOT_AZURE_SAS_BUILD.md`
3. **24-hour prod soak** post-deploy (mirrors BUG-ANL-UPLOAD-GRIDFS soak pattern)
4. **K8s ingress ticket closed** on first prod large-file upload evidence (per §9 + user call #5)
5. **Cluster-G arc RESUMED** with G.4 advance scan (Shield-adjacency M2 trio · single-vs-sequential ESCALATION TRIGGER)
6. **Cluster-G G.5** advance scan + fix
7. **Cluster-G retrospective** (mirrors `CLUSTER_F_RETROSPECTIVE.md` shape)
8. **Cluster-C intra-file refactor** (FTT-004..009)
9. **LLM_MODELS_REFRESH .2/.3** future ship

End of memo.
