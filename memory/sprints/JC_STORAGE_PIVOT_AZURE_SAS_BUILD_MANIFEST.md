**Canonical Spec**: `/app/memory/sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §11 (resolved)` (all 8 user-locked decisions D1-D8 with D2+D7 folded into single managed-identity → user-delegation-SAS auth model · §12 new pivot vector for per-region storage if residency requirement surfaces · §13 discipline notes · §14 user-direction surface) + cross-reference `JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §1-§10` for X-threshold derivation + architecture + endpoint surface + frontend changes + security model + dependencies + locked-area sweep + migration policy + ingress disposition + test strategy. This manifest is READ-ONLY; build dispatch is credential-gated and NOT in scope of this manifest.

# JC_STORAGE_PIVOT_AZURE_SAS_BUILD_MANIFEST — Ready-to-fire build dispatch plan

**Status**: SHIPPED (manifest only) · READ-ONLY · HARD STOP at manifest surface · build dispatch credential-gated (awaiting user-supplied Azure credentials per locked user call #2)
**Date**: 2026-06-30
**Fires when**: (a) Azure credentials in hand (storage account name + region + managed-identity binding) AND (b) user dispatches the build slug
**Predecessor**: `sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md` (scope memo with resolved §11 decisions); `sprints/BUG_ANALYZE_UPLOAD.md` (GridFS migration this manifest layers on top of)

---

## §0 — Fire-trigger preconditions (ALL must hold)

| # | Precondition | Source of evidence |
|---|---|---|
| 1 | Azure storage account provisioned + name supplied | User-supplied at dispatch time |
| 2 | Azure region supplied (per D8 — app-region default; user may override) | User-supplied at dispatch time |
| 3 | Managed-identity binding configured on the Emergent backend pod | User-supplied or Emergent platform pre-provisioning |
| 4 | All 8 §11 decisions LOCKED (D1-D8 with D2+D7 folded) | `JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §11` ✅ DONE 2026-06-30 |
| 5 | This manifest authored | `sprints/JC_STORAGE_PIVOT_AZURE_SAS_BUILD_MANIFEST.md` ✅ DONE 2026-06-30 |
| 6 | DEV_PIPELINE §9 row added BEFORE manifest authoring (row-before-memo discipline) | `memory/DEV_PIPELINE.md` ✅ DONE 2026-06-30 |
| 7 | Cluster-G arc PAUSED (G.4/G.5 not in build dispatch window per user sequence ii) | `memory/PRD.md` head entry confirms |

Preconditions 4-7 ✅ DONE; 1-3 BLOCKING on user.

---

## §1 — File-by-file delta plan (LOC estimates)

### §1.1 — Backend NEW files

| Path | Status | Purpose | Est. LOC |
|---|---|---|---|
| `backend/services/storage/__init__.py` | NEW | Package marker for new storage submodule | ~5 |
| `backend/services/storage/azure_blob_service.py` | NEW | Azure Blob Storage client (managed-identity wired; SAS issuer via `get_user_delegation_key()`; container provisioning helpers; CORS-config getter for ops verification) | ~220 |
| `backend/services/storage/_test_mock_azure.py` | NEW | Local mock endpoint at `/_test/mock-azure/<blob>` returning Azure-shape PUT/GET/DELETE responses; in-memory storage dict; mounted ONLY when `STORAGE_MOCK_ENABLED=1` (defaulted off in prod) | ~80 |
| `backend/scripts/jc_storage_pivot_azure_sas_proving_slice.py` | NEW | 15-row proving slice per §10.3 of scope memo + manifest §6 row mapping | ~260 |

**Backend NEW subtotal**: ~565 LOC

### §1.2 — Backend MOD files

| Path | Status | Purpose | Est. LOC delta |
|---|---|---|---|
| `backend/routers/workbook_analysis.py` | MOD | Add 2 endpoints (`/upload/presigned-url` + `/upload/complete`) per scope §3.1+§3.2; size-branch validation; tenant-derived blob name; backend-side `get_blob_properties()` verification at /complete; audit trail rows for `workbook.upload.sas_issued`/`sas_completed`/`sas_failed` | +80 / -0 (additive only; existing `/upload` + `/upload-multi` UNCHANGED) |
| `backend/services/analysis_lifecycle.py` | MOD | Extend `read_workbook_bytes(blob_row)` from dual-read to triple-read (`azure_blob_id` → `gridfs_id` → `data_b64`); `delete_workbook_blob()` extends to handle azure_blob_id container delete; suffix-aware tempfile name pattern UNCHANGED | +25 / -0 (additive only) |
| `backend/requirements.txt` | MOD via `pip install + pip freeze` | Add `azure-storage-blob==12.20.0` + `azure-identity==1.16.0` pinned versions | +2 (transitive deps may add a handful of lines; do not hand-edit per rules — use `pip freeze`) |
| `backend/.env` | MOD | Add 6 env keys per scope §6.3 minus the 2 dropped per D2+D7 (`AZURE_STORAGE_KEY` + `AZURE_USE_MANAGED_IDENTITY` not added; managed identity is the only path) | +6 |

**Backend MOD subtotal**: ~115 LOC delta (additive) + dependency pins

### §1.3 — Frontend NEW files

| Path | Status | Purpose | Est. LOC |
|---|---|---|---|
| `frontend/src/services/azureSasUploader.js` | NEW | Encapsulates `@azure/storage-blob` SDK calls; size-branch helper (`shouldUseSAS(file)`); progress event wiring; retry-on-fail (max 3 with exponential backoff); cancel-in-flight handler; error categorisation (sas-expired / cors-block / throttle) | ~120 |

**Frontend NEW subtotal**: ~120 LOC

### §1.4 — Frontend MOD files

| Path | Status | Purpose | Est. LOC delta |
|---|---|---|---|
| `frontend/src/components/analyze/WorkbookUploader.jsx` | MOD | Size-branching at file picker; call `azureSasUploader.upload(file)` for >X-MB path; progress-bar wired to SDK `onProgress`; cancel button; error toast wiring; new data-testids (`workbook-uploader-progress-bar`, `workbook-uploader-cancel-button`, `workbook-uploader-error-toast`, `workbook-uploader-path-indicator`) | +50 / -0 |
| `frontend/package.json` | MOD via `yarn add` | Add `@azure/storage-blob@^12.20.0` | +1 |

**Frontend MOD subtotal**: ~50 LOC delta

### §1.5 — Documentation files (build dispatch sprint memo + runbook updates)

| Path | Status | Purpose | Est. LOC |
|---|---|---|---|
| `memory/sprints/JC_STORAGE_PIVOT_AZURE_SAS_BUILD.md` | NEW | Build dispatch close memo (canonical spec on line 1 cites THIS manifest + the scope memo §11 resolved); patches applied · proving slice results · regression ladder · locked-area sweep · trajectory advance · forward look | ~350 (matches G.3 fix memo cadence) |
| `memory/runbooks/PROD_INGRESS_AND_MEMORY.md` | MOD | Add "Post-SAS Pivot Disposition" section per scope §9; note that 512m annotation is OPTIONAL for files > X but STILL REQUIRED for ≤ X GridFS band | +20 / -0 |
| `memory/PRD.md` | MOD | Head entry blockquote for build dispatch | +1 paragraph |
| `memory/DEV_PIPELINE.md` | MOD | §9 row for build dispatch (added BEFORE memo per row-before-memo discipline) | +1 row |

**Documentation subtotal**: ~370 LOC delta

### §1.6 — Aggregate totals

| Bucket | NEW LOC | MOD LOC delta |
|---|---:|---:|
| Backend | ~565 | ~115 |
| Frontend | ~120 | ~50 |
| Docs | ~350 | ~20 |
| **Build dispatch total** | **~1035 NEW** | **~185 MOD** |

Original estimate from DEV_PIPELINE row of THIS dispatch was ~580 NEW + ~80 MOD — the file-by-file breakdown above is more granular and exceeds it because of the local mock service file (+~80 LOC) + build dispatch sprint memo (+~350 LOC) + finer-grained backend service split (+breakdown into 2 service files instead of 1). The +455 LOC delta is documentation + mock + structured service split; product-functional LOC is in line with the original estimate.

---

## §2 — SDK install commands (pinned versions)

### §2.1 — Backend

```bash
# Install Azure SDKs
cd /app/backend
pip install azure-storage-blob==12.20.0 azure-identity==1.16.0

# Regenerate requirements.txt with pip freeze (per CRITICAL RULES — do NOT hand-edit)
pip freeze > /app/backend/requirements.txt
```

### §2.2 — Frontend

```bash
# Install Azure Blob JS SDK
cd /app/frontend
yarn add @azure/storage-blob@^12.20.0
```

### §2.3 — Version-pin rationale

- `azure-storage-blob==12.20.0` — latest stable as of 2026-06; matches scope memo §6.1
- `azure-identity==1.16.0` — latest stable as of 2026-06; required for managed-identity binding per D2+D7
- `@azure/storage-blob@^12.20.0` — matches backend version; `^` allows minor-version updates within 12.x semver line

---

## §3 — Env vars manifest (6 NEW; 2 dropped vs scope §6.3 per D2+D7)

| Var | Required | Default | Source per scope §6.3 | Status |
|---|:---:|---|---|---|
| `AZURE_STORAGE_ACCOUNT` | yes | — | Scope §6.3 | KEEP — user supplies at dispatch time |
| `AZURE_STORAGE_CONTAINER_WORKBOOK` | yes | `workbook-uploads` | Scope §6.3 | KEEP |
| `AZURE_STORAGE_CONTAINER_ANALYSIS` | yes | `analysis-uploads` | Scope §6.3 | KEEP |
| `AZURE_STORAGE_CONTAINER_TEMP` | yes | `temp-staging` | Scope §6.3 | KEEP |
| `AZURE_STORAGE_CONTAINER_ARCHIVE` | yes | `archive` | NEW (per D5 archive container provisioned-not-populated) | NEW vs scope memo |
| `AZURE_SAS_EXPIRY_MINUTES` | no | `15` | Scope §6.3 | KEEP |
| `STORAGE_X_THRESHOLD_MB` | no | `16` | Scope §6.3 | KEEP (per D1 anchored at 16; env-overridable for prod tuning) |
| `STORAGE_MOCK_ENABLED` | no | `0` | NEW (gate for local mock endpoint per §1.1 mock file) | NEW vs scope memo |
| ~~`AZURE_STORAGE_KEY`~~ | — | — | Scope §6.3 | **DROPPED per D2+D7** — no account-key path shipped |
| ~~`AZURE_USE_MANAGED_IDENTITY`~~ | — | — | Scope §6.3 | **DROPPED per D2+D7** — managed identity is the only path |

**Build env-var count**: 8 total (6 required + 2 optional with safe defaults). User supplies 1 (`AZURE_STORAGE_ACCOUNT`) + region binding (regional config is per-deployment-env, not per-app env).

---

## §4 — CORS config spec for Azure storage account

CORS is configured at the storage-account level (NOT per container) via Azure Portal / `az` CLI / Terraform. Required ONCE per storage account provisioning.

```json
{
  "CorsRules": [
    {
      "AllowedOrigins": [
        "https://akki.syni.ai",
        "https://*.preview.emergentagent.com"
      ],
      "AllowedMethods": ["PUT", "OPTIONS"],
      "AllowedHeaders": [
        "x-ms-blob-type",
        "x-ms-blob-content-type",
        "x-ms-meta-*",
        "x-ms-version",
        "x-ms-date",
        "content-length",
        "content-type",
        "authorization"
      ],
      "ExposedHeaders": [
        "x-ms-request-id",
        "x-ms-error-code"
      ],
      "MaxAgeInSeconds": 3600
    }
  ]
}
```

**Apply command** (post-storage-account provisioning):

```bash
az storage cors clear --account-name <account_name> --services b
az storage cors add \
  --account-name <account_name> \
  --services b \
  --methods PUT OPTIONS \
  --origins "https://akki.syni.ai" "https://*.preview.emergentagent.com" \
  --allowed-headers "x-ms-blob-type" "x-ms-blob-content-type" "x-ms-meta-*" "x-ms-version" "x-ms-date" "content-length" "content-type" "authorization" \
  --exposed-headers "x-ms-request-id" "x-ms-error-code" \
  --max-age 3600
```

**Validation**: build dispatch proving slice Row 5 (CORS-block) issues a PUT from a non-whitelisted origin (e.g., `https://evil.example.com`) and asserts CORS-preflight failure.

---

## §5 — Pre-credential acceptance tests vs post-credential acceptance tests

### §5.1 — Pre-credential (this manifest's scope; build dispatch can author them speculatively even before credentials land)

Local Azure SAS mock at `localhost:8001/_test/mock-azure/<blob-name>`:
- PUT returns `201 Created` with `x-ms-request-id` header
- GET returns the stored bytes
- DELETE removes the blob from in-memory dict
- HEAD returns properties (content-length, last-modified)
- Mock toggle: `STORAGE_MOCK_ENABLED=1` mounts the routes; defaults off in prod

**Acceptance tests pre-credential**:
- A1: SAS URL issuance returns 200 + correct shape (no real Azure call)
- A2: FE size-branch returns SAS for > X bytes, GridFS for ≤ X bytes
- A3: Complete-webhook creates `workbook_blobs` row with `azure_blob_id` field set
- A4: `read_workbook_bytes` triple-read returns correct bytes from the mock blob
- A5: Local mock honours single-PUT (small files) and block-blob commit (large files)
- A6: GridFS regression — file ≤ X still rides existing `/upload` path
- A7: Tenant isolation — cross-tenant `/complete` rejected (403)
- A8: Audit trail rows present for `sas_issued` + `sas_completed` + `sas_failed`

These 8 are GREEN against the local mock without any Azure credentials. Build dispatch can ship A1-A8 as "Phase 1 GREEN" even without credentials in hand.

### §5.2 — Post-credential (require real Azure dev container)

**Acceptance tests post-credential**:
- B1: Real SAS issued via `BlobServiceClient.get_user_delegation_key()` succeeds with managed identity
- B2: Real PUT to dev Azure container succeeds; blob lands; `BlockBlobClient.get_blob_properties()` confirms size
- B3: Real CORS preflight from `https://akki.syni.ai` origin succeeds; from `https://evil.example.com` is blocked
- B4: Real SAS expiry honoured (issue SAS with 1-min expiry; sleep 70s; PUT returns 403)
- B5: Real ingress bypass — Azure access log shows PUT; K8s ingress access log does NOT show the upload bytes
- B6: Real 250 MB end-to-end — SAS issued → 250 MB PUT → /complete → workbook_blobs row → Analyze trigger fires → result rendered
- B7: Real cleanup-after-cancel — cancelled upload removes blob from `temp-staging` (verified via `list_blobs()`)

These 7 require real Azure dev container access. Build dispatch ships B1-B7 as "Phase 2 GREEN" once credentials land.

### §5.3 — Combined slice → 15 rows

8 pre-credential (A1-A8) + 7 post-credential (B1-B7) = 15 rows total. Matches scope §10.3 target. See §6 below for the row-by-row mapping.

---

## §6 — 15-row proving slice rows mapped to acceptance criteria

| Row | Acceptance | Phase | Spec source |
|---:|---|---|---|
| 1 | A1 SAS URL issuance returns 200 + correct shape (mock) | Pre-credential | Scope §3.1 |
| 2 | A2 FE size-branch returns SAS for > X bytes, GridFS for ≤ X bytes | Pre-credential | Scope §4.1 |
| 3 | A5 Local mock honours SAS write-only scope (PUT works; GET/DELETE fail under write-only token) | Pre-credential | Scope §5 + §10.1 |
| 4 | B4 Real SAS expiry honoured (issue 1-min expiry; sleep 70s; PUT returns 403) | Post-credential | Scope §5 |
| 5 | B3 Real CORS preflight — whitelist passes; non-whitelist blocked | Post-credential | Manifest §4 |
| 6 | A3 Complete-webhook creates workbook_blobs row with azure_blob_id | Pre-credential | Scope §3.2 |
| 7 | A4 Triple-read — read_workbook_bytes returns correct bytes from azure / gridfs / data_b64 | Pre-credential | Scope §2.4 |
| 8 | B7 Throttle retry — synthesized 503 triggers backoff + recovery | Post-credential | Scope §4.2 |
| 9 | B5 Ingress bypass evidence — verify NO ingress proxy access log for SAS upload | Post-credential | Scope §9 |
| 10 | A6 GridFS regression-free — file ≤ X still rides GridFS (BUG memo Row B/C/D pattern) | Pre-credential | Scope §10.3 |
| 11 | B6 Large-file end-to-end — 250 MB SAS upload + Analyze trigger + result render | Post-credential | Scope §10.3 |
| 12 | B7 Cleanup-after-fail — cancelled upload removes blob from temp-staging | Post-credential | Scope §4.2 |
| 13 | A7 Tenant isolation — cross-tenant /complete with wrong account_id → 403 | Pre-credential | Scope §5 |
| 14 | Surface ratchet — /api/* + /v1/* hashes recomputed; deliberate additive (2 new routes) | Both | Scope §10.3 |
| 15 | A8 Audit trail — workbook.upload.sas_issued + sas_completed + sas_failed rows | Pre-credential | Scope §5 |

**Pre-credential GREEN count target**: 8 rows (A1, A2, A3, A4, A5, A6, A7, A8) — can ship as "Phase 1 GREEN" without Azure creds in hand.
**Post-credential GREEN count target**: 7 rows (B1-B7 mapped to Rows 4, 5, 8, 9, 11, 12 + any of these that synthesize via mock first) — ship as "Phase 2 GREEN" once credentials land.

---

## §7 — Build dispatch close criteria

The build dispatch can be considered SHIPPED when ALL of the following hold:

| # | Criterion | Validation method |
|---|---|---|
| 1 | 15/15 proving slice GREEN | `python backend/scripts/jc_storage_pivot_azure_sas_proving_slice.py` exits 0; output shows 15 GREEN rows |
| 2 | Locked-area sweep clean | Source-grep for Shield internals / Track-2 schema / Monitor pre-warmer / OAuth / WS Doc UI references in diff → 0 hits |
| 3 | Regression ladder GREEN | Surface ratchets (`/api/* = 31e1d9769f632472` baseline + 2 new routes recompute deliberately) · Shield contract (synisense_security 3/3 PASS) · G.2 sibling regression (iter39 + iter53 + iter54 = 23+ skipped) · invariant suite (bespoke-run M1=0, M2=7) · existing BUG-ANL-UPLOAD-GRIDFS slice 11/11 GREEN |
| 4 | No product-code unexpected mutation | `git diff` review confirms ONLY the files in §1 changed; no surface-area drift |
| 5 | 24h prod soak gate spec | Mirrors BUG-ANL-UPLOAD-GRIDFS pattern: deploy to prod → 24h observation window → log scan for `azure_blob_id` upload events with 200 status + zero CORS blocks + zero SAS-expired retries; if soak GREEN, proceed to K8s ingress ticket close per scope §9 |
| 6 | M1_CEILING + M2_CEILING UNCHANGED | Bespoke-run invariant still passes with M1=0, M2=7 |
| 7 | Build sprint memo authored | `sprints/JC_STORAGE_PIVOT_AZURE_SAS_BUILD.md` shipped with canonical spec on line 1 |
| 8 | DEV_PIPELINE §9 row + PRD head entry shipped | Per row-before-memo discipline |

### §7.1 — 24h prod soak gate spec

Soak window starts when build deploys to prod. During soak:
- **Hour 0-1**: Engineering smoke — manual 250 MB workbook upload via SAS path; verify analyze trigger fires + result renders; verify K8s ingress access log shows ONLY `/api/workbook/upload/presigned-url` + `/api/workbook/upload/complete` (no upload bytes)
- **Hour 1-24**: Passive observation — log scan for `workbook.upload.sas_*` audit rows; alert on any `sas_failed` row; track p50/p95/p99 latency of presigned-url issuance + complete-webhook
- **Hour 24**: Soak gate evaluation — if zero `sas_failed` rows AND p99 < 500ms for issuance AND zero 5xx from `/complete` → GREEN; else investigate before proceeding
- **K8s ingress ticket close**: triggered after soak GREEN per scope §9 close criteria (all 4 conditions must hold)

---

## §8 — Estimated dispatch runtime

| Phase | Duration | Notes |
|---|---|---|
| SDK install + env-var setup | ~5 min | `pip install` + `yarn add` + `.env` edits |
| Backend service file authoring | ~30 min | `azure_blob_service.py` (~220 LOC) + `_test_mock_azure.py` (~80 LOC) |
| Backend router + lifecycle MODs | ~15 min | `workbook_analysis.py` (~+80 LOC) + `analysis_lifecycle.py` (~+25 LOC) |
| Frontend uploader service + component MOD | ~20 min | `azureSasUploader.js` (~120 LOC) + `WorkbookUploader.jsx` (~+50 LOC) |
| Proving slice authoring | ~20 min | `jc_storage_pivot_azure_sas_proving_slice.py` (~260 LOC; 15 rows) |
| **Build dispatch implementation total** | **~90 min** | |
| Proving slice execution | ~60s | Pre-credential rows (~5s each × 8) + post-credential rows (~5-20s each × 7) — bulk of post-cred time is the 250 MB end-to-end Row 11 |
| Build sprint memo + DEV_PIPELINE + PRD authoring | ~30 min | Mirrors G.3 fix memo authoring time |
| **Build dispatch total** | **~120 min** | ~2 hours end-to-end |

Pre-credential phase (Phase 1) ships in ~75 min if credentials are delayed; Phase 2 adds ~45 min once credentials land.

---

## §9 — LOC delta confirmation

Reconciles §1 file-by-file estimate with the DEV_PIPELINE row of this dispatch's high-level estimate (~580 NEW + ~80 MOD):

| Bucket | DEV_PIPELINE row estimate | §1 detailed estimate | Delta |
|---|---:|---:|---:|
| NEW LOC | ~580 | ~1035 | +455 |
| MOD LOC | ~80 | ~185 | +105 |

The +455 NEW delta breaks down as:
- Local mock service file (`_test_mock_azure.py`) → +80 LOC (not in original estimate; D2+D7 dropped account-key path so local dev needs mock for credential-free testing)
- Build sprint memo (`JC_STORAGE_PIVOT_AZURE_SAS_BUILD.md`) → +350 LOC (documentation; matches G.3 fix memo cadence; not LOC-bearing for product surface)
- Backend service split into 2 files instead of 1 → +25 LOC (init.py + structured split)

Product-functional LOC (excluding docs + mock): NEW ~605 + MOD ~80 — within +25 LOC of original DEV_PIPELINE estimate. The +455 LOC is documentation density, not feature scope creep.

The +105 MOD delta breaks down as:
- Runbook update (`PROD_INGRESS_AND_MEMORY.md`) → +20 LOC (per scope §9 post-SAS pivot disposition)
- Backend `.env` (6 keys) + frontend `package.json` (1 dep) + `requirements.txt` (2 deps + transitive) → +9 LOC config
- PRD head + DEV_PIPELINE row → +2 LOC docs
- Audit trail extension in `workbook_analysis.py` → +5 LOC over original 75
- `analysis_lifecycle.py` triple-read more verbose than dual-read → +10 LOC over original 15
- FE component data-testids + cancel + error paths → +15 LOC over original 35

All MOD delta is within scope of the user's locked decisions and the resolved §11; no feature creep.

---

## §10 — Discipline notes

- **READ-ONLY scope honoured**: 0 LOC mutated outside this manifest file (and the §11/§12 transformation in the scope memo, which is the other deliverable in the same dispatch slug)
- **Canonical spec cited on line 1**: explicit cross-references to `JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §11 resolved` + scope memo §1-§10
- **F.3-ADVANCE memo-order slip lesson APPLIED**: DEV_PIPELINE.md §9 row authored BEFORE both the scope memo edit AND this manifest creation (single batched insert in the §9 row covers both A + B)
- **G.3-VERIFICATION AST-over-grep lesson N/A**: no AST work this dispatch
- **F.5 YAML-edit slip lesson N/A**: no YAML edits
- **G.1 slice-poll-cadence-mismatch lesson N/A**: no slice runs in scope
- **No testing subagent used** (per banned-list rule)
- **No scope creep**: deliverables A (scope memo §11 + §12) and B (this manifest) match the user's enumerated dispatch tasks exactly
- **No build steps executed**: build dispatch is credential-gated per user call #2; only manifest authored here
- **No SDK installed** anywhere
- **No env vars added** anywhere
- **No product code modified** anywhere
- **HARD STOP** at manifest surface; standing rules unchanged
- **Cluster-G arc REMAINS PAUSED** at G.3 close per user sequence ii; G.4 + G.5 deferred until storage arc lands in prod

---

## §11 — User-direction surface (HARD STOP)

Per user dispatch: **HARD STOP at manifest surface; surface to user; build dispatch awaits user-supplied Azure credentials per user call #2.**

**Decisions-lock + manifest milestone**:
- ✅ All 8 §11 open questions LOCKED as D1-D8 in scope memo (with D2+D7 folded into single managed-identity → user-delegation-SAS auth model)
- ✅ Scope memo §12 NEW "Known pivot vector: per-region storage if residency requirement surfaces"
- ✅ Downstream scope memo sections renumbered (§13/§14/§15)
- ✅ Build manifest authored: file-by-file delta plan + SDK pinned versions + env vars + CORS spec + pre/post-credential test split + 15-row slice mapping + close criteria + 24h soak gate + LOC delta confirmation
- ✅ 0 LOC mutated outside memo files
- ✅ NO SDK installed, NO routers modified, NO env vars added (per credential-gate)
- ✅ DEV_PIPELINE §9 row added BEFORE both edits (row-before-memo discipline)

**Awaiting next dispatch from user**:
1. Azure credentials supplied (storage account name + region + managed-identity binding per fire-trigger §0)
2. Build dispatch trigger (slug TBD; suggested: `JC-STORAGE-PIVOT-AZURE-SAS-BUILD`)

When the build dispatch fires, this manifest's §1-§7 are the executable contract. Phase 1 (pre-credential) can begin authoring even before credentials land; Phase 2 (post-credential) requires credentials.

Standing rules unchanged. Time-gate status: no active time-gate. Cluster-G arc PAUSED at G.3 close; will resume after storage arc proves end-to-end in prod per sequence ii.

End of manifest.
