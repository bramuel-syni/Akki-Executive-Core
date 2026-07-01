**Canonical Spec**: User platform-side direction (verbatim in `JC-STORAGE-PIVOT-TIGRIS-RESCOPE` dispatch 2026-06-30): "Emergent Object Store (Tigris, S3-compatible) built-in, 5 GB per-org quota. Supports upload/download/list. BYO S3/GCS available with user's own keys if we exceed 5 GB quota or need extra features. Direct-from-browser presigned pattern (browser PUT to object store, backend only sees object reference). K8s ingress annotations are NOT available through the platform. Drop the ingress ticket. Presigned-only, no fallback." + `sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md` (predecessor Azure Blob scope; 8 locked §11 decisions D1-D8; §12 pivot-vector) + `sprints/JC_STORAGE_PIVOT_AZURE_SAS_BUILD_MANIFEST.md` (predecessor manifest, now superseded) + Emergent Object Store integration playbook (retrieved via `integration_playbook_expert_v2` 2026-06-30).

# JC_STORAGE_PIVOT_TIGRIS_RESCOPE — Emergent Object Store rescope + escalation

> **🅾️ ON-HOLD 2026-06-30 · pending Emergent support clarification on browser-direct-presigned URL support in the Object Store integration.** If support confirms presigned works via their wrapper, this pivot resumes (Tigris becomes primary again — cheaper path). If support confirms no presigned, this pivot stays on-hold and Azure path stays primary. **Azure path (see `sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md`) is primary meanwhile.** This memo is preserved for audit trail + potential resume; do NOT delete.

**Status**: SHIPPED (rescope memo only) · READ-ONLY · HARD STOP at rescope surface · **1 CRITICAL escalation surfaced** (architectural mismatch between user's dispatch assumption and integration playbook reality) · 3-path decomposition surfaced for user decision · quota check GREEN
**Date**: 2026-06-30
**Predecessor**: `sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md` (Azure Blob scope) · `sprints/JC_STORAGE_PIVOT_AZURE_SAS_BUILD_MANIFEST.md` (Azure manifest — now SUPERSEDED by this pivot; retained for audit history)

---

## §1 — Quota headroom check (GREEN — Path A viable from quota dimension)

Motor query on local `fs.files` (2026-06-30 · via `MONGO_URL` from `backend/.env`):

| Metric | Value |
|---|---:|
| Total `fs.files` count | 3624 |
| Total `fs.files` aggregate bytes | 1010.6 MB |
| Files **> 16 MB** (Tigris eligibility per D1 threshold) | **4** |
| Aggregate bytes of files > 16 MB | 1,048,591,136 (0.977 GB) |
| Files ≤ 1 MB | 3620 |
| Files 1-16 MB | 0 |
| Files 16-100 MB | 0 |
| Files 100-512 MB | 4 |

**Top 4 files > 16 MB** (all test fixtures):
```
262,147,784 | row_f_first.csv
262,147,784 | row_f_second.csv
262,147,784 | row_f_first.csv     (duplicate; proving-slice re-runs)
262,147,784 | row_f_second.csv    (duplicate; proving-slice re-runs)
```

**Verdict**:
- **Under 5 GB Tigris quota**: 0.977 GB is ~20% of 5 GB. Comfortable ~5× headroom.
- **Under 3 GB safe operating margin**: 0.977 GB is ~33% of 3 GB. Comfortable ~3× headroom.
- **Prod extrapolation**: 4 large files are proving-slice test artifacts (`row_f_first/second.csv` from `BUG_ANALYZE_UPLOAD.md` Row F 250 MB regression test), unlikely present in prod. Prod usage of files > 16 MB probably < 100 MB.
- **Path A viable from quota dimension**: ✅

---

## §2 — CRITICAL ESCALATION: architectural mismatch surfaced by integration playbook

### §2.1 — User dispatch assumption

User's dispatch text (verbatim): "Direct-from-browser presigned pattern (browser PUT to object store, backend only sees object reference). K8s ingress annotations are NOT available through the platform. Drop the ingress ticket. Presigned-only, no fallback."

### §2.2 — Integration playbook reality (via `integration_playbook_expert_v2`)

Emergent Object Store built-in Tigris is a **wrapped Emergent-managed API**, not a raw S3-compatible service. Key constraints from the playbook:

- **`"No presigned URLs — all access must go through your backend."`** — CONTRADICTS user dispatch
- **`"No delete API — implement soft-delete in your DB."`**
- **`"No rename API — upload to new path, update DB reference."`**
- **`"One bucket per user — use app-name prefix to isolate."`** — CONTRADICTS user's 4-container structure
- **API surface**: `PUT/GET /objects/{path}` via `X-Storage-Key` session token issued by `POST /init` with `EMERGENT_LLM_KEY`
- **Endpoint**: `https://integrations.emergentagent.com/objstore/api/v1/storage`
- **Auth env var**: `EMERGENT_LLM_KEY` (already present in `backend/.env`; name-only confirmed via `grep -c` without value log)
- **Path convention**: `{app_name}/uploads/{user_id}/{uuid}.{ext}` (no leading slash)
- **Max list results**: 1000 (prefix-filter)
- **Init pattern**: `init_storage()` called ONCE at startup; `storage_key` module-global, reused across requests

### §2.3 — Impact on locked decisions D1-D8 from Azure scope

| Decision | Azure state | Tigris built-in reality |
|---|---|---|
| D1 X = 16 MB threshold | Files > 16 MB → Azure presigned | Files > 16 MB → backend PUT to Tigris (NOT browser-direct) — **threshold still valid but flow different** |
| D2+D7 folded auth | Managed identity → user-delegation SAS | `EMERGENT_LLM_KEY` → `storage_key` session token; SAS concept doesn't exist in Tigris |
| D3 single account | Single Azure storage account | Single Tigris "bucket" per app (path-prefix isolation); consistent |
| D4 24h staging retention | Azure lifecycle rule on `-uploads` containers | **NO native lifecycle** — must implement backend cron sweep |
| D5 archive containers provisioned-not-populated | 2 archive Azure containers | Path-prefix pattern (`myapp/archive/...`) — no separate container |
| D6 JS SDK for browser upload | `@azure/storage-blob` SAS PUT | **CANNOT DO BROWSER-DIRECT** — no presigned URLs available. Frontend uploads to backend endpoint; backend PUTs to Tigris |
| D8 region = app-region default | Azure region user-supplied | Region handled by Emergent platform; not agent-configurable |

**5 of 8 decisions materially change or lose applicability** under Tigris built-in.

### §2.4 — Ingress annotation dependency INVERSION

- **Under Azure scope**: browser-direct-presigned bypasses backend for large files; ingress annotations were fallback-only.
- **Under Tigris built-in**: ALL uploads traverse backend (backend receives full body, then PUTs to Tigris). **Ingress annotations become LOAD-BEARING for ALL files > 8 MB** (stock nginx-ingress default). Contradicts user's "Drop the ingress ticket" instruction.

---

## §3 — Three-path decomposition for user decision

| Path | Description | Ingress ticket | User creds needed | Delivery timeline |
|---|---|---|---|---|
| **A'** | Built-in Tigris backend-mediated | STAYS OPEN — annotations load-bearing for > 8 MB | 0 | Build ready immediately (§4 manifest applies) |
| **B'** | BYO S3/GCS with user creds | Can close on presigned prod-evidence | User provides AWS/GCS access keys + region + bucket name | Blocked on user creds |
| **C'** | Hybrid: built-in Tigris backend-mediated for small band + BYO S3/GCS presigned for large band | Depends on band cutoff | User provides BYO creds for large-band | Blocked on user creds + band-cutoff decision |

**Agent recommendation**: given quota comfort + zero-creds-needed + user's "close with items you have" directive, **Path A'** is the low-friction path — but requires user to accept that the ingress annotation dependency comes back (contradicting the user's "drop ingress ticket" instruction). Path B' honours the original browser-direct-presigned architecture but blocks on user credentials.

**Decision required from user**: choose A' / B' / C'.

---

## §4 — Path A' assumed for the pre-staged build manifest

Manifest lives at `sprints/JC_STORAGE_PIVOT_TIGRIS_BUILD_MANIFEST.md` (this dispatch also ships it). Design overview:

- **Backend Tigris client**: wraps `requests.put(f"{STORAGE_URL}/objects/{path}", headers={"X-Storage-Key": key, "Content-Type": ct}, data=data)` per playbook; `init_storage()` at FastAPI startup; module-global `storage_key`
- **Upload endpoint**: `POST /api/workbook/upload/large-file` accepts multipart; streams-through to Tigris `put_object(...)`; returns `{"object_ref": path, "size": bytes}`
- **Read helper**: `read_workbook_bytes_tigris(object_ref)` calls `get_object(path)`; returns `(bytes, content_type)`
- **Storage-path convention**: `akki/{context_id}/{account_id}/{uuid}.{ext}` (context+account prefix for tenancy isolation via prefix-filter on list)
- **No lifecycle cron in v1**: 24h staging retention DEFERRED to v1.1 (backend cron sweep). Test-fixture cleanup manual.
- **No CORS on storage** (backend-mediated; ingress + FastAPI CORS govern)
- **F.6 Shield-contract discipline-pay APPLIES**: Tigris client itself is not Shield-routed, but the workbook analyzer chain (analyze pipeline) routes through Shield unchanged; defensive `synisense_security` + `phase_a` regression rows in proving slice
- **Proving slice**: 14 rows target — Tigris init + PUT + GET + list + soft-delete + tenancy prefix isolation + F.6 defensive + surface ratchets + invariants + AST source-check + log scan

If user picks Path B' or C' instead, the manifest gets rewritten for `boto3` + `@aws-sdk/client-s3` + real presigned URLs (much closer to the Azure manifest predecessor pattern).

---

## §5 — Locked-area sweep (CLEAN)

| Area | Touched at build (Path A')? | Touched at rescope? |
|---|:---:|:---:|
| Shield internals | NO | NO |
| Track-2 schema | NO | NO |
| Monitor pre-warmer | NO | NO |
| OAuth | NO | NO |
| WS Doc UI | NO | NO |
| Product code | NO (rescope is memo-only) | NO |
| Existing GridFS upload path | NO (small files stay on GridFS per D1) | NO |
| Backfilled 3068 rows | NO | NO |
| M1+M2 ceilings | NO (storage is NOT in M1+M2 family) | NO |
| FTT registry | NO | NO |
| Byte-identity ratchets | NO | NO |

Only new memo contents + DEV_PIPELINE §9 row.

---

## §6 — Discipline notes

- **F.3-ADVANCE memo-order APPLIED**: DEV_PIPELINE §9 row authored BEFORE this memo file
- **F.5 YAML-edit single-batch N/A**: no YAML edits
- **G.1 slice-poll-cadence N/A**: no slice runs (READ-ONLY rescope)
- **G.3-VERIFICATION AST-over-grep APPLIED**: motor DB query for quota check + integration playbook subagent for architecture verification + name-only env-var presence check (no value log)
- **NEW lesson #5 UNQUARANTINED runtime PASS N/A at rescope**: no conversion; applies at build dispatch
- **NEW lesson #6 file-names-from-disk APPLIED**: motor query returns live values (not memo prose); playbook content pulled via subagent (not stale memory); `EMERGENT_LLM_KEY` presence sourced from live `grep -c` on `backend/.env`
- **Credential-hygiene discipline honoured**: 0 raw credentials in memo; `EMERGENT_LLM_KEY` referenced as env var name only; storage_key referenced as session concept only
- **No testing subagent used** (per user explicit ban)
- **HARD STOP at rescope surface**; standing rules unchanged

---

## §7 — Cross-references

- Azure predecessor scope: `sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md`
- Azure predecessor manifest (SUPERSEDED): `sprints/JC_STORAGE_PIVOT_AZURE_SAS_BUILD_MANIFEST.md`
- Tigris built-in build manifest: `sprints/JC_STORAGE_PIVOT_TIGRIS_BUILD_MANIFEST.md` (Path A' assumption)
- K8s ingress recontextualization: `user_actions/K8S_INGRESS_STATUS.md` (updated with Path A'/B'/C' recontextualization; NOT closed)
- Sunset eval Gate B: `sprints/JC_INLINE_BLOB_SUNSET_EVALUATION.md §8.2 Gate B` (updated with playbook finding; NOT closed)
- Azure engineer request addendum: `user_actions/AZURE_ENGINEER_REQUEST_ADDENDUM.md` (Tasks 1+2+4 dropped; Task 3 stands)
- BUG-ANL-UPLOAD-GRIDFS closure: `sprints/BUG_ANALYZE_UPLOAD.md`
- Emergent Object Store integration: playbook via `integration_playbook_expert_v2` (2026-06-30)

---

## §8 — User-direction surface (HARD STOP · escalation)

**Open questions requiring user direction**:
1. **Path A' / B' / C' choice** (see §3). Load-bearing decision.
2. If A': accept K8s ingress ticket stays OPEN (annotations become load-bearing, contradicting user's "drop it" instruction). Coordinate with Emergent platform side on ingress annotation applicability (user previously said platform doesn't expose ingress annotations — reconfirm under Path A' pressure).
3. If B' or C': agent needs AWS/GCS credentials (access key ID + secret + region + bucket name) via mounted secret path or env-var injection.
4. Path A' architectural trade-off: no browser-direct upload (all uploads traverse backend). Acceptable for the workload (< 100 MB typical files) but changes the mental model from the Azure design.

**Per autonomous-mandate escalation trigger**: "Any other user-dep dependency surfaces → escalate" — path selection IS a user-dep dependency. Do NOT auto-dispatch build.

**HARD STOP at rescope surface** per dispatch shape.
