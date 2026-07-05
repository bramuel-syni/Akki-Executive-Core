# BUG · "Analyze file upload failing" — Phase 2c re-design (GridFS migration)

> **Source of truth:** `/app/memory/JC_WS_CANONICAL_SPEC.md` (Analyze
> submodule is JC-WS; spec rule: "Reuse the existing engines
> (generators, exporters, solva_v2, workbook_analyzer) — do not
> rebuild." This migration honours that — only the storage backend
> under the workbook_analyzer changes.).

**Updated:** 2026-06-26 (post-user-pivot from 11 MB stopgap to
GridFS migration).
**Environment:** PRODUCTION (`https://akki.syni.ai`) per user
confirmation.
**Status:** **Phase 2c design surface — HARD STOP for user sign-off
before Phase 3 implementation.**

## What changed

User pivoted off the 11 MB stopgap:

> "needs to accept large files as its analysis 250MB+"

The 11 MB guard would block real Analyze workflows. **GridFS migration
is now the actual fix.** Target: accept **500 MB** uploads end-to-end
with a fail-clean 413 above the ceiling. The in-flight 11 MB patch +
proving slice were **discarded** (uncommitted, fully reverted at
`routers/workbook_analysis.py`).

## Section 1 · GridFS migration scope

Two insert sites swap their persistence backend from
inline-base64-in-doc to GridFS-streamed-chunks:

| Path | Insert site (today) | New behaviour |
|---|---|---|
| `POST /api/workbook/upload` | `routers/workbook_analysis.py:336` — `db.workbook_blobs.insert_one({..., "data_b64": base64.b64encode(data)...})` | Stream `UploadFile.file` (FastAPI's `SpooledTemporaryFile` — auto-spills to disk above 1 MB) → `AsyncIOMotorGridFSBucket.upload_from_stream(filename, source, metadata={...})`. Persist the returned `file_id` on `workbook_blobs.gridfs_id`. **Stop writing `data_b64`** for new rows. |
| `POST /api/workbook/upload-multi` | `routers/workbook_analysis.py:767` via `services/analysis_lifecycle.py:79` — `db.analysis_blobs.insert_many(blob_docs)` with each `blob_docs[i]["data_b64"]` carrying the base64 | Per source: stream `UploadFile.file` → GridFS bucket → set `analysis_blobs[i].gridfs_id`. `data_b64` no longer set on new rows. |

**Single GridFS bucket** for both collections (`fs` default bucket
name in Motor), with bucket metadata carrying the disambiguator
(`{"kind": "workbook_blob"|"analysis_blob", "analysis_id": ..., "account_id": ..., "context_id": ..., "filename": ..., "file_format": ...}`).
Reads filter by `metadata.analysis_id` + tenancy keys.

## Section 2 · Streaming upload (no 500 MB in memory)

FastAPI's `UploadFile` is backed by Starlette's `SpooledTemporaryFile`
(auto-spills to disk above 1 MB) — **the receive path is already
disk-spooled.** What changes:

- **Today (memory-hog):** handler calls `data = await file.read()` →
  loads the full 500 MB into a single Python `bytes` object, then
  `base64.b64encode(data)` doubles peak memory to ~1.2 GB before the
  Mongo wire send. That's the memory cliff for big workbooks.
- **GridFS path (streaming):**
  - The handler does NOT call `file.read()` on the full payload.
  - It calls `await bucket.upload_from_stream(filename, file.file, metadata={...})`
    — Motor reads the spooled file in 255 KB GridFS-chunk-sized blocks,
    writes each block as a separate BSON doc in `fs.chunks`. Peak
    memory ~ a few hundred KB per chunk + Motor buffering, NOT 500 MB.
  - For `parse_workbook` (which still needs to read the file to
    extract `sheets` + `matrices`), we stream the GridFS file BACK
    into a `tempfile.NamedTemporaryFile(delete=False)` and pass the
    path to openpyxl. openpyxl's `read_only=True` mode is row-iterator
    based and stays in the low-MB band; the temp file gets `os.unlink`-ed
    in a `finally`. Net peak memory for upload+parse: ~30-50 MB, not 1 GB.

**Confirmation needed for Motor:** `AsyncIOMotorGridFSBucket.upload_from_stream(filename, source, ...)`
accepts any file-like object exposing `.read(N)`. Starlette's
`UploadFile.file` is a `SpooledTemporaryFile` which satisfies this
contract. Confirmed import + sync-OK at `python3 -c "from motor.motor_asyncio import AsyncIOMotorGridFSBucket; print('OK')"`.

## Section 3 · Dual-read transition

**Reader contract** (additive, not replacing):

```python
# pseudo — actual implementation in helpers below
async def read_workbook_bytes(blob_row: dict) -> bytes:
    """Reader for any inline-or-GridFS-stored workbook blob.

    - If row carries `gridfs_id`: stream GridFS chunks to a
      tempfile, return path (or yield bytes via generator).
    - Else if row carries `data_b64`: decode base64 inline (legacy).
    - Else: raise.
    """
    gridfs_id = blob_row.get("gridfs_id")
    if gridfs_id:
        # streaming read — temp file pattern (see Section 6)
        ...
    legacy_b64 = blob_row.get("data_b64")
    if legacy_b64:
        return base64.b64decode(legacy_b64)
    raise RuntimeError(f"blob row {blob_row.get('analysis_id')} carries neither gridfs_id nor data_b64")
```

**Two reader call sites to migrate** (both in
`routers/workbook_analysis.py`):

1. Line 141 — lazy re-parse for citation resolver:
   ```python
   blob_row = await db.workbook_blobs.find_one({"analysis_id": analysis_id})
   blob = base64.b64decode(blob_row["data_b64"])    # ← becomes read_workbook_bytes(blob_row)
   _sheets, matrices = parse_workbook(blob=blob, file_format=fmt)
   ```
2. Line 884 — synthesize_v2 reads each source:
   ```python
   for blob in blobs[:MAX_BLOBS]:
       raw_bytes = base64.b64decode(blob["data_b64"])    # ← becomes read_workbook_bytes(blob)
       sheets, matrices = parse_workbook(blob=raw_bytes, file_format=fmt)
   ```

**Both call sites must be updated** to the dual-read helper. The
new helper lives in `services/analysis_lifecycle.py` (already the
home of the per-analysis blob lifecycle) — keeps the GridFS dance in
one place.

## Section 4 · Backfill plan for existing inline `data_b64` docs

Existing rows carrying `data_b64` (no `gridfs_id`) keep working
indefinitely via the dual-read helper. **No forced backfill required**
— but a one-shot migration helper is provided so the user can choose
to consolidate.

**Script:** `backend/scripts/jc_bug_analyze_upload_backfill.py` (NEW).

**Behaviour:**
- Walks `workbook_blobs` then `analysis_blobs`, finds rows with
  `data_b64` set AND no `gridfs_id`.
- For each row: base64-decodes the inline payload, streams to GridFS,
  sets `gridfs_id` on the row, **unsets `data_b64`** in a single
  atomic `update_one({_id: ..., data_b64: {$exists: true}}, {$set: {gridfs_id: ...}, $unset: {data_b64: ""}})`.
- Idempotent: skips rows that already have `gridfs_id`.
- Resumable: each row is independently committed; an interrupted run
  resumes by skipping already-converted rows.
- Logs `[backfill] migrated N rows · X MB → GridFS · Y rows skipped`.
- **Defaults to DRY-RUN** (counts only, no writes) unless invoked
  with `--commit`.
- Optional `--collection workbook_blobs` / `--collection analysis_blobs`
  to scope.
- Runs ON the same Mongo URI the backend uses (preview or production —
  user controls which by exporting `MONGO_URL`).

**For Atlas prod:** user runs the script against the production
Atlas URI with `--commit`. The script is fully read-then-write-then-
verify per row — no batch destructive ops. Each row is independently
recoverable via the `data_b64` value still in memory at the moment
of insert, so even if the script crashes mid-run the data is not
lost.

## Section 5 · Infra changes required (USER MUST APPLY — out of code scope)

These are NOT code changes. Surfacing as a discrete checklist:

| Layer | Current | Required | Where |
|---|---|---|---|
| **nginx (frontend.conf)** | `client_max_body_size 50m;` | `client_max_body_size 512m;` (and consider `client_body_timeout 300s;`) | `/app/nginx/frontend.conf:60` — comment says "Keep at 50m unless the upload size limit is raised in backend ACCEPT/MAX_BYTES" → that condition is now true |
| **K8s ingress** | unknown (not in repo) | `nginx.ingress.kubernetes.io/proxy-body-size: "512m"` + `nginx.ingress.kubernetes.io/proxy-read-timeout: "300"` annotations on the Ingress resource for `akki.syni.ai` | Production ingress controller (Emergent platform side — likely needs Emergent support if not in user's hands) |
| **FastAPI handler cap** | `MAX_BYTES = 250 * 1024 * 1024` (250 MB) | `MAX_BYTES = 500 * 1024 * 1024` (500 MB) — set the new ceiling | `routers/workbook_analysis.py:102` — CODE CHANGE, part of Phase 3 |
| **Atlas** | Default | No change — GridFS handles 500 MB natively; chunks at 255 KB → ~2000 chunks per file → BSON-protocol-clean | None |
| **Pod memory limits** | unknown (Emergent platform side) | At ≥ 1 GB per pod the streaming GridFS path is comfortable. Current preview pod has 32 GB total free — sustainable. If prod pods are tight (≤ 512 MB), surface to user to bump | Emergent platform side |

**HALT-AND-SURFACE if:** the user reports K8s ingress cannot be
bumped, OR pod memory limit < 1 GB. In those cases the code lands
but the user still cannot upload >50 MB (proxy rejects first).

## Section 6 · Downstream reader audit (CONFIRMED — zero coupling to locked areas)

Full grep over the codebase:

**Insert sites (2)** — both in `routers/workbook_analysis.py`:
- L336: `db.workbook_blobs.insert_one({..., "data_b64": ...})` → MIGRATE
- L767 (via `services/analysis_lifecycle.py:79`): `db.analysis_blobs.insert_many(blob_docs)` with each blob's `data_b64` set → MIGRATE

**Read sites (2)** — both in `routers/workbook_analysis.py`:
- L141: lazy re-parse for cell-citation resolver → MIGRATE to dual-read helper
- L884: synthesize_v2 reads each source for parse_workbook → MIGRATE to dual-read helper

**Delete sites (1, +2 test-only)**:
- `services/analysis_lifecycle.py:118`: `db.analysis_blobs.delete_many({"analysis_id": ...})` → must ALSO delete GridFS chunks via `bucket.delete(file_id)`. Refactor to fetch the `gridfs_id`s first, then delete chunks, then delete metadata rows.
- `tests/invariants/test_invariant_shield_no_leak.py:265` + `tests/characterisation/test_solva_analyze_golden.py:224`: test-only cleanups — additive, update to also drop the GridFS file_ids.

**Tenancy invariant** — `tests/invariants/test_invariant_tenancy.py:119,182,189`:
- `workbook_blobs` and `analysis_blobs` already declared tenancy-keyed. GridFS chunks (`fs.chunks`) are auto-keyed by file_id (not directly tenancy-leakable). `fs.files` carries `metadata.account_id + metadata.context_id` — must be added to the tenancy invariant collection list, OR documented as off-list with rationale ("`fs.files` is a GridFS metadata sidecar; tenancy enforcement happens on the parent `workbook_blobs`/`analysis_blobs` row that references the file_id; orphan `fs.files` entries are pruned by the lifecycle delete path"). **Recommend the second approach** — additive, no test churn.

**Lifecycle hooks** — `services/analysis_lifecycle.py`:
- `delete_analysis_blobs(...)` — must be extended to also call `bucket.delete(file_id)` for each blob's `gridfs_id`. Backward-compatible (legacy inline rows have no `gridfs_id` and skip the GridFS delete).

**Zero coupling to locked areas — confirmed:**
- ❌ JC-WS Generate Document UI: no reader/writer in FE generate-doc surfaces touches `workbook_blobs` / `analysis_blobs`.
- ❌ Shield path: zero `clamav_service.scan` / shield-routed call in the workbook upload chain.
- ❌ Monitor `tasks` discriminator: completely separate domain; no shared collection.
- ❌ pptx_exporter: produces decks, never reads workbook blobs.
- ❌ Track-2 schema (`ArtefactPayload.perspective_spread`): not in workbook domain.

**No new routes.** Surface ratchet unchanged.

## Section 7 · Library compatibility

| Library | Today | GridFS path | Compatible? |
|---|---|---|---|
| `openpyxl.load_workbook(filename=..., read_only=True)` | takes BytesIO(blob) — needs full bytes in memory | accepts filesystem path OR a file-like object with `seek()`+`read()`. We stream GridFS chunks into a `tempfile.NamedTemporaryFile()`, close it, pass the path. openpyxl's read_only mode then row-iterates lazily — low memory footprint. | ✅ YES |
| `csv.reader(io.StringIO(blob.decode('utf-8')))` (in `_parse_csv`) | needs full bytes (decoded to str) | Stream GridFS chunks into a tempfile, open it as text-mode file, pass to csv.reader as a row iterator. OR for CSV-only path, accept full-bytes pattern since CSV inflation is minimal. | ✅ YES (CSV ceiling is small enough that full-bytes is still acceptable up to 500 MB; we use the tempfile-path uniformly for parity) |
| `motor.motor_asyncio.AsyncIOMotorGridFSBucket` | not used today | New dependency on the bucket API. Imports clean (verified: `from motor.motor_asyncio import AsyncIOMotorGridFSBucket; print('OK')`). | ✅ YES |

**Implementation helper signature (new, in `services/analysis_lifecycle.py`):**

```python
async def upload_to_gridfs(*, source, filename: str, metadata: dict) -> str:
    """Stream `source` (file-like) into GridFS; return the file_id (str)."""
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="fs")
    file_id = await bucket.upload_from_stream(filename, source, metadata=metadata)
    return str(file_id)


async def download_to_tempfile(file_id: str) -> str:
    """Stream a GridFS file by id to a NamedTemporaryFile; return path."""
    bucket = AsyncIOMotorGridFSBucket(db, bucket_name="fs")
    tmp = tempfile.NamedTemporaryFile(suffix=".gridfs", delete=False)
    try:
        await bucket.download_to_stream(ObjectId(file_id), tmp)
    finally:
        tmp.close()
    return tmp.name


async def read_workbook_bytes(blob_row: dict) -> tuple[bytes | None, str | None]:
    """Dual-read: returns (bytes, None) for legacy inline blobs;
    (None, tempfile_path) for GridFS blobs. Caller passes whichever
    is non-None to parse_workbook (we extend parse_workbook to
    accept either) AND must cleanup tempfile_path when done."""
    if blob_row.get("gridfs_id"):
        path = await download_to_tempfile(blob_row["gridfs_id"])
        return None, path
    if blob_row.get("data_b64"):
        return base64.b64decode(blob_row["data_b64"]), None
    raise RuntimeError(f"blob_row carries neither gridfs_id nor data_b64: {blob_row.get('analysis_id')}")
```

`parse_workbook` gets a thin signature extension: `parse_workbook(*, blob=None, file_path=None, file_format)` — exactly one must be set. Backwards-compatible (`blob=` keyword still works for all existing callers; new GridFS path passes `file_path=`).

## Section 8 · Memory pressure analysis

At 500 MB upload, peak memory expectations per phase:

| Phase | Today (inline base64) | GridFS path |
|---|---|---|
| Receive (FastAPI multipart) | ~500 MB raw (UploadFile auto-spills > 1 MB) | same — auto-spool to disk |
| Persist to Mongo | ~500 MB raw + ~700 MB base64 = ~1.2 GB peak | ~ 1 GridFS chunk (255 KB) + Motor buffering — ~5-20 MB peak |
| Parse (openpyxl) | ~500 MB bytes + openpyxl row-iter ~20-100 MB = ~600 MB peak | ~500 MB on disk (tempfile) + openpyxl row-iter ~20-100 MB = ~100 MB peak in RAM (disk holds the bulk) |
| Delete (lifecycle) | ~zero | ~zero (Motor `bucket.delete(file_id)` issues N chunk-deletes) |

**Pod limits:** preview pod sees 32 GB total memory (`/proc/meminfo`),
~28 GB available. Production pod size unknown — recommend ≥ 1 GB
guaranteed. If prod pod < 1 GB, surface to user to bump.

## Section 9 · Proving slice scope

`backend/scripts/jc_bug_analyze_upload_slice.py` (NEW, replaces the
discarded stopgap slice):

| Row | Test | Expected |
|---|---|---|
| A | 5 MB CSV `/upload` | 200 — regression on the small-file path |
| B | 50 MB XLSX `/upload` | 200 — exercises the band that broke before; round-trip via GridFS |
| C | 250 MB XLSX `/upload` | 200 — user's stated minimum |
| D | 500 MB XLSX `/upload` | 200 — ceiling |
| E | 600 MB XLSX `/upload` | 413 clean rejection (`workbook_over_500mb_ceiling: <fname> is X.X MB; max is 500 MB`) |
| F | Multi-file with two ~250 MB files | 200 — multi-file batch under aggregate; each GridFS-stored independently |
| G | Round-trip read-back: a 100 MB blob written via GridFS reads back byte-identical via `read_workbook_bytes` | bytes equality |
| H | Legacy inline blob (synthetic — write a `data_b64` row directly to mongo) reads back correctly via `read_workbook_bytes` | dual-read confirmed |
| I | Backfill script: seed 2 inline rows + 1 GridFS row in a test collection; run with `--commit`; verify all 3 end up as GridFS rows with `data_b64` unset, idempotent (re-run = no-op) | backfill confirmed |
| J | Lifecycle delete: an analysis with GridFS-backed blobs is deleted via `delete_analysis_blobs(...)`; verify GridFS chunks are gone too (no orphan `fs.chunks` rows) | lifecycle confirmed |

10 acceptance rows. Disk required ~2 GB for the 600 MB+ tests; preview
container has ~28 GB free per `/proc/meminfo`. Synthesized files use
the same `_make_xlsx` deterministic-padding pattern from the discarded
stopgap slice (kept).

**Optional row K** (only if pod memory > 1 GB):
- K. Memory ceiling: pin RSS during a 500 MB upload. Expect ≤ 200 MB peak.

## Section 10 · Blast-radius re-check (comprehensive, since this is a real architecture change)

| Locked area | Touched by GridFS migration? |
|---|---|
| JC-WS Generate Document UI | NO — FE generate-doc paths do not touch `workbook_blobs` / `analysis_blobs` |
| Shield path internals | NO — workbook upload doesn't route through Shield |
| Monitor's `tasks` discriminator | NO — different collection family, different surface |
| Monitor additive contract | NO — Monitor + workbook are independent domains |
| pptx_exporter | NO — exporter consumes `ArtefactPayload`, not workbook blobs |
| Track-2 schema (`perspective_spread`) | NO — Solva v2 schema unchanged |
| Convergent deck | NO — Stage 1 deck regression-check stays at 76555 bytes |
| 450 Solva v2 schema tests | NO — no Solva schema change |
| 3 ratchet hash tests (`/api/*` + `/v1/*` + combined) | NO — no new routes; existing routes change internal behaviour only |
| JC-TM email path | NO — uploads via email attachment go through `documents.py` clamav-scanned upload; never touch `workbook_blobs`/`analysis_blobs` |

## Section 11 · Rollback path

**Forward-only deployment recommended.** Rollback semantics:

| Scenario | Behaviour |
|---|---|
| GridFS code rolled back to pre-Phase-3 commit | New analyses uploaded after Phase 3 deploy: GridFS-stored, NO `data_b64` field. Reverted code reads only `data_b64` → those analyses become unreadable until forward-rolled again. **DATA IS NOT LOST** — the GridFS chunks remain in Atlas. |
| Need to recover analyses uploaded during the GridFS window | Forward-roll the dual-read helper. No backfill required (data was always in GridFS, the reader just couldn't find it during the rollback window). |
| Need to abandon GridFS entirely | One-shot script: walk `fs.files`, re-inline as `data_b64` on the parent blob row (would re-introduce the 16 MB cap; only viable if user accepts the cap and the affected analyses are all < 12 MB). |

**Roll-forward fix during outage:** Phase 3 patch is additive — the
dual-read helper is invoked on read; old code paths still read
`data_b64`. The ONLY breaking change is the new write path's omission
of `data_b64`. To keep rollback safe AT THE COST of double-writing:
add an env flag `GRIDFS_DUAL_WRITE=1` that ALSO sets `data_b64` for
new rows (only safe for files under 12 MB — flag-gated, default OFF).
**RECOMMEND OMITTING** the dual-write flag — defeats the purpose.

## Decision points for sign-off

1. **Approve the 11-section design above?** (Y/N)
2. **Confirm 500 MB ceiling?** (Y / OR specify different)
3. **Atlas backfill via the new helper script?** (defaults to DRY-RUN; user invokes `--commit` against prod Atlas at the time of their choosing)
4. **Sequence Phase 3 implementation now, OR run an additional design review first?**

## HARD STOP

Surfacing for sign-off. Phase 3 will NOT begin until you reply.

---

# Phase 2b — previous design (stopgap, DISCARDED)

(11 MB inline-storage guard memo kept below for the audit trail —
this is the design that was approved THEN superseded by the GridFS
dispatch. The 11 MB ceiling is no longer the resolution. References
to "minimum-scope fix" below refer to the stopgap, not the GridFS
migration.)



## Root cause (locked)

The Analyze drawer's upload path persists the raw file bytes
**base64-inlined into a Mongo document** (`analysis_blobs` for the
multi-file path; `workbook_blobs` for the single-file path). The
Mongo wire protocol caps a single BSON document at **16,793,598
bytes**. Base64 inflates raw bytes by 4/3. Therefore the cliff is:

> **~12.00 MB raw input → BSON doc exceeds 16 MB → `DocumentTooLarge`
> → uncaught 500 from the upload handler → user-facing
> "upload failed" toast.**

### Hard repro in preview (deterministic — fires every time)

```python
raw = b'X' * int(12.5 * 1024 * 1024)            # 12.5 MB
doc = {
    "analysis_id": "ana-...", "source_id": "src-...",
    "account_id": "...", "context_id": "...",
    "filename": "cap_repro.xlsx", "file_format": "xlsx",
    "data_b64": base64.b64encode(raw).decode("ascii"),    # ← 17,476,268 bytes
    "created_at": datetime.now(timezone.utc).isoformat(),
}
await db.analysis_blobs.insert_one(doc)
# pymongo.errors.DocumentTooLarge: BSON document too large (17476687 bytes)
#   — the connected server supports BSON document sizes up to 16793598 bytes.
```

Same script with `raw = b'X' * (11 * 1024 * 1024)` → INSERT OK.

This bug **manifests on both preview and production** — but preview
users rarely upload 12 MB+ workbooks during testing (CSV samples /
small XLSX are typical preview shapes), so the bug is invisible in
preview QA and routinely fires in production where real users upload
real workbooks (multi-quarter financials, full-year sheets with
hundreds of rows × 50+ cols).

### Why preview's initial probe passed

My Phase 2a probe uploaded a 93-byte CSV + 4964-byte XLSX. Both
under the cap by 5+ orders of magnitude → false-pass. Only a
≥ 12 MB payload triggers the cap. Hard lesson: ALWAYS reproduce upload
bugs at the user's actual file size.

## Confirmed insert paths (both share the same exposure)

| Endpoint | Insert site | Encoding | Exposed? |
|---|---|---|---|
| `POST /api/workbook/upload` (legacy WorkStudio Analyze tab single-file) | `routers/workbook_analysis.py:336` — `db.workbook_blobs.insert_one({..., "data_b64": base64.b64encode(data).decode("ascii"), ...})` | base64-inline | ✅ YES — > 12 MB raw fails |
| `POST /api/workbook/upload-multi` (AnalyzeJournal Analyze drawer multi-file) | `routers/workbook_analysis.py:767` — `db.analysis_blobs.insert_many(blob_docs)` where each blob from `services/analysis_lifecycle.py:79`: `"data_b64": base64.b64encode(raw).decode("ascii")` | base64-inline | ✅ YES — any file in batch > 12 MB fails the whole batch |

**No pre-insert size guard** on either path. The existing handler caps
at 250 MB per file (`MAX_BYTES = 250 * 1024 * 1024` at line 102), but
this is 20× larger than what Mongo's BSON protocol allows for an inline
blob — i.e., the 250 MB cap is a load-bearing footgun.

## Secondary suspect (still real, but fires LATER than the 12 MB cap)

**nginx `client_max_body_size 50m`** in `/app/nginx/frontend.conf:60`.
Files > 50 MB hit the proxy reject before nginx forwards to uvicorn
— 413 immediate fail. But this only matters for files > 50 MB. The
Atlas cap fires FIRST at 12 MB for all files in the 12-50 MB band,
which is the most common "real workbook" size band.

The K8s production ingress may or may not have its own body-size
annotation — not visible from the repo. If the user's file is
> 50 MB, both nginx AND Atlas would fail it; nginx fails earlier
(at the proxy) so the user would see a slightly different error
shape (HTML 413 page vs JSON 500 from FastAPI).

## Suspects RULED OUT (concrete reasons)

| Suspect | Verdict | Evidence |
|---|---|---|
| Clamav unreachable in prod (#1 from Phase 2a) | RULED OUT | Workbook upload paths do NOT call `clamav_service.scan(...)` — verified by grep across `routers/workbook_analysis.py` |
| CSRF cookie domain mismatch (#3 from Phase 2a) | RULED OUT | `services/csrf.py:179` uses default cookie domain (binds to exact origin = `akki.syni.ai` in prod), SameSite=Lax, path=/. Cookie WILL ride on POSTs to `/api/workbook/*` |
| Atlas connection / driver timeout (#4 from Phase 2a) | UNLIKELY | The bug would be intermittent + slow-fail (10-30s delay). User's report implies a clean fast-fail. Atlas cap fails at insert-time, fast |

## Confidence ranking

| Cause | Confidence | Evidence quality |
|---|---|---|
| **Mongo 16 MB BSON cap on inline blob** | **~85%** | Hard repro in preview + insert site identified + size math confirmed + matches "fast-fail on moderately-sized files" pattern |
| nginx 50 MB cap | ~10% | Real but fires later than Atlas; only relevant if file > 50 MB |
| Other | ~5% | Unknown failure mode user didn't share |

## Proposed minimum-fix scope (Phase 3 — awaiting user sign-off)

**Per the user's hard rule** ("at 70%+ confidence … the proposal still
surfaces for user sign-off before patching"), surfacing here before
any code change.

### Item 1 — Pre-insert size guard returning a clean 413 (BACKEND)

Add a single constant + 1 check per upload handler.

```python
# routers/workbook_analysis.py
# Mongo 16 MB BSON cap → max raw bytes that fit an inline base64 blob
# after metadata overhead. 11 MB is a safe ceiling (11 MB raw → ~14.7 MB
# base64 → ~14.7 MB BSON + ~50 KB doc overhead → well under 16 MB).
MAX_INLINE_RAW_BYTES = 11 * 1024 * 1024

# In `upload_workbook` AND `upload_workbook_multi`, AFTER the existing
# extension + MAX_BYTES + parse checks, BEFORE the insert:
if len(raw) > MAX_INLINE_RAW_BYTES:
    raise HTTPException(
        413,
        f"workbook_too_large_for_inline_storage: "
        f"{fname} is {len(raw) / 1024 / 1024:.1f}MB; "
        f"inline-storage limit is {MAX_INLINE_RAW_BYTES // 1024 // 1024}MB. "
        f"Reduce the file size or contact support to enable large-file storage."
    )
```

**Estimate:** +12 LOC in `routers/workbook_analysis.py` (2 sites × ~6
LOC each, including comment). Zero schema change. Zero new dependency.

### Item 2 — DocumentTooLarge handler (BACKEND, defensive)

If somehow the size guard misses (e.g., a future caller bypasses the
guard), catch `pymongo.errors.DocumentTooLarge` around the `insert_one`
/ `insert_many` calls and convert to 413 with the same clean message.

```python
from pymongo.errors import DocumentTooLarge
try:
    await db.analysis_blobs.insert_many(blob_docs)
except DocumentTooLarge as exc:
    raise HTTPException(
        413,
        "workbook_too_large_for_inline_storage: inline blob exceeds Mongo 16MB doc cap. "
        "Reduce the file size or contact support to enable large-file storage."
    ) from exc
```

**Estimate:** +14 LOC (2 sites × ~7 LOC each). Defensive — the size
guard above should make this branch unreachable; the catch is purely
to convert raw `DocumentTooLarge` into a clean 413 if a developer adds
a third upload path and forgets the guard.

### Item 3 — Proving slice (BACKEND)

`backend/scripts/jc_bug_analyze_upload_slice.py` — exercises:
- (A) 11 MB upload → succeeds (under cap, returns analysis row).
- (B) 13 MB upload → 413 with clean `workbook_too_large_for_inline_storage` message (pre-fix would be 500 with raw `DocumentTooLarge`).
- (C) Multi-file with one 13 MB file + one 1 MB file → 413 with the offending filename in the message.
- (D) The existing 5-row CSV + 5-row XLSX paths still return 200 (regression check on the small-file path).

**Estimate:** +180 LOC (new file).

### What is OUT of this minimum-scope fix

- ❌ **GridFS migration** — the canonical long-term fix for large
  workbook storage. Out of scope per user's "minimum scope" rule.
  Surface as backlog after this fix lands.
- ❌ **nginx 50 MB cap** — infra config, not code. Document only.
- ❌ **K8s ingress body-size annotation** — also infra. Document only.

## Blast-radius re-check

| Locked area | Touched by this fix? |
|---|---|
| JC-WS Generate Document UI | NO |
| Shield path internals | NO |
| Monitor's additive contract | NO |
| pptx_exporter | NO |
| Track-2 schema/builder | NO |
| Convergent / divergent decks | NO |
| Existing tests | NO (additive — new tests pass before & after the small-file path) |

## HALT-AND-SURFACE decision

**Surfacing for sign-off** before Phase 3 patch. Two go/no-go knobs:

1. **Confirm Item 1+2+3 minimum-fix scope is acceptable** (returns
   413 with clean message at the 11 MB cliff; defers GridFS to
   backlog).
2. **OR confirm a different file-size threshold** (default 11 MB; the
   theoretical safe-max is ~12 MB but 11 MB gives a 1 MB safety margin
   for metadata overhead variance).

## TL;DR (the original)

(see Phase 2a section below — preview probe showed PASS on small
files; that probe was insufficient because it didn't exercise the
12 MB+ band where the Atlas / Mongo BSON cap fires.)

---

# Phase 2a — original diagnosis note (kept for record)



## TL;DR

All four Analyze-related upload paths (the new `/workbook/upload-multi`
multi-file path the AnalyzeJournal page calls, the legacy
`/workbook/upload` single-file path the WorkStudioAnalyze page calls,
both with CSV + XLSX, plus the bad-extension rejection probe) **return
HTTP 200 (or correct 415 on bad ext)** in preview against
`https://akki-executive.preview.emergentagent.com`. **No upload-related
errors in backend logs.** The server.py deployment-fix did not touch
any upload code path (it added an `asyncio.sleep` around the engine
backfill task — fully unrelated to uploads).

## Repro recipe (run from /app)

```bash
API_URL="https://akki-executive.preview.emergentagent.com"
CJ=$(mktemp)
CSRF=$(curl -s -c "$CJ" "$API_URL/api/csrf" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['csrf_token'])")
LJ=$(curl -s -b "$CJ" -c "$CJ" -X POST "$API_URL/api/auth/login" \
  -H "Content-Type: application/json" -H "X-CSRF-Token: $CSRF" \
  -d '{"email":"admin@akki.ai","password":"<redacted:ADMIN_SEED_PASSWORD>"}')
TOKEN=$(echo "$LJ" | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")
CTX=$(echo "$LJ" | python3 -c "import sys,json; print(json.load(sys.stdin)['contexts'][0]['id'])")

# 5-row CSV
printf 'date,revenue\n2026-01-01,1000\n2026-01-02,1100\n2026-01-03,1200\n2026-01-04,1180\n2026-01-05,1250\n' > /tmp/tiny.csv

# AnalyzeJournal path (the user-facing "Analyze" drawer trigger)
curl -s -b "$CJ" -X POST "$API_URL/api/workbook/upload-multi" \
  -H "Authorization: Bearer $TOKEN" -H "X-CSRF-Token: $CSRF" \
  -F "files=@/tmp/tiny.csv;type=text/csv" \
  -F "context_id=$CTX" -F "objective=test"
```

## Probe results in preview

| Path | Body | Result | Status |
|---|---|---|---|
| `POST /api/workbook/upload-multi` | CSV (5 rows) | `{"id":"ana-87c15586339c", "status":"draft", "sources":[...] }` | ✅ HTTP 200 |
| `POST /api/workbook/upload-multi` | XLSX (3 cols, 5 rows) | `{"id":"ana-5e20c7c9d8f4", ...}` | ✅ HTTP 200 |
| `POST /api/workbook/upload` | XLSX | Full parsed sheet metadata returned | ✅ HTTP 200 |
| `POST /api/workbook/upload-multi` | `.txt` (bad ext) | `{"detail":"workbook_format_unsupported: .txt"}` | ✅ HTTP 415 |

## Logs

`grep -E "Error|Exception|Traceback|500" /var/log/supervisor/backend.err.log | grep -iE "workbook|upload|analyses"` returns **0 lines**.

The only upload-relevant log lines are clamav warnings —
`clamav: dev escape hatch ARMED — uploads will bypass scan if clamd
unreachable (AKKI_ENV='(unset)')`. **These are NOT errors and they do
NOT affect the workbook upload path** (the `/workbook/upload*`
endpoints don't call `clamav_service.scan(...)`; only document/chat/
solva/work_studio_export/studio_blocks uploads route through clamav).

## Surface map of upload paths (confirmed)

- **FE (AnalyzeJournal page · the JC-WS Phase 2 Analyze drawer trigger):**
  `/app/frontend/src/pages/AnalyzeJournal.jsx:131` calls
  `POST /workbook/upload-multi` with multipart fields
  `files[]` (1..N) + `context_id` (required) + `objective` (optional)
  + `title` (optional).
- **FE (WorkStudioAnalyze page · legacy single-file Analyze tab):**
  `/app/frontend/src/pages/WorkStudioAnalyze.jsx:42` calls
  `POST /workbook/upload` with multipart field `file`.
- **FE (Monitor objective drawer citation upload):**
  `/app/frontend/src/components/monitor/ObjectivesProjectsPanel.jsx:359`
  — uploads a citation document; NOT a workbook upload, lives on a
  different surface entirely.
- **BE (the workbook handlers):**
  `/app/backend/routers/workbook_analysis.py:301` (`upload_workbook`,
  single-file `wba-*` analysis) and
  `/app/backend/routers/workbook_analysis.py:713`
  (`upload_workbook_multi`, multi-file `ana-*` analysis). Both accept
  `.xlsx` and `.csv` only (line 103: `ACCEPT_EXT = {".xlsx", ".csv"}`).
  Both cap each file at 250 MB. NEITHER calls clamav.

## Did the deployment-fix server.py change touch any upload path?

**No.** The fix at lines 477-525 added a `ENGINE_BACKFILL_BOOT_GRACE_S`
sleep around the synisense engine derivation backfill task. The upload
handlers are in `routers/workbook_analysis.py`, mounted by the routers
package — not touched by the server.py edit. Surface ratchet unchanged
(no new routes), 3/3 ratchet tests still pass.

## Suspected root causes (need user input to narrow)

In order of likelihood:

1. **PRODUCTION-ONLY symptom — the user is on `https://akki.syni.ai`.**
   - The clamav warning `(AKKI_ENV='(unset)')` is preview-only. In
     production `AKKI_ENV=production`, clamav enforce mode is ON. But
     workbook uploads DON'T route through clamav, so this would NOT
     affect AnalyzeJournal. It WOULD affect chat/document/solva-phase-d/
     studio_blocks/work_studio_export upload paths (those DO call
     `clamav_service.scan`). If the production cluster has no `clamd`
     service reachable on `CLAMAV_HOST` (default `clamd`), all
     non-workbook uploads would fail with 502/503.
   - Worth checking with the user whether the failing surface is the
     workbook Analyze drawer OR a different upload (chat attachment,
     document upload, solva upload, studio block upload).

2. **MongoDB Atlas in prod vs local MongoDB in preview.**
   - Atlas might be enforcing index keysize limits or document size
     limits differently. Workbook payloads can be sizeable
     (`workbook_blobs.data_b64` stores the base64 of the file inline,
     up to 250 MB). Atlas's 16 MB doc cap on inserts would HARD-FAIL
     `db.workbook_blobs.insert_one(...)` for any file > ~11 MB raw
     (after base64 inflation). Preview's local Mongo may be lenient.
   - Worth asking: how large is the file the user is trying to upload?

3. **CDN / ingress body-size cap.**
   - Some CDN/ingress configs cap multipart payloads at 1-50 MB at the
     proxy layer, returning 413 or 502 BEFORE the request reaches
     uvicorn. The backend cap is 250 MB but the K8s ingress may be
     smaller.
   - Worth asking: what was the file size? Did the upload error happen
     instantly (proxy reject) or after a long upload (parse / DB
     reject)?

4. **CSRF token or session cookie not flowing.**
   - The FE uses `api.post(...)` which goes through the axios wrapper
     that injects `X-CSRF-Token`. If the production domain
     `akki.syni.ai` is served via a different cookie domain than the
     preview, the CSRF cookie set on `/api/csrf` might not be sent
     with the upload POST. The response would be 403 with
     `csrf_token_missing` (the same error I saw initially when probing
     without a cookie jar).

## Proposed minimum-fix scope (only if a real failure is reproduced)

**None yet.** Cannot scope a fix without:
1. The environment (preview vs production)
2. The exact failure mode (HTTP status, error message, file size, file
   type, surface — Analyze drawer vs Work Studio Analyze tab vs a
   different upload entirely)
3. A repro recipe

## Blast-radius check (already locked areas)

If a fix were needed, the affected files would likely be:
- `routers/workbook_analysis.py` (Analyze upload handler) — **FAIR
  GAME** per user dispatch ("UPLOAD path is fair game — only the
  GENERATE DOCUMENT UI is locked").
- `services/clamav_service.py` (if the issue is clamav-related, only
  affects non-workbook uploads).
- `frontend/src/pages/AnalyzeJournal.jsx` (if it's a FE problem).

**Locked areas that would NOT be touched by any fix:**
- ❌ JC-WS Generate Document UI — not in upload path.
- ❌ Shield path internals — uploads don't route through Shield.
- ❌ Monitor's additive contract — Monitor uploads use a different
  endpoint (citation upload on the objective drawer); even there, a
  fix would be additive-only.
- ❌ pptx_exporter — not on the upload path.
- ❌ Track-2 schema/builder — not on the upload path.

## ASK to surface (one P0 clarification + four narrow ones)

P0:
- **Which environment**: preview (`akki-executive.preview.emergentagent.com`)
  or production (`https://akki.syni.ai`)?

If repro:
- Which surface clicks fired before the failure? (Pick: AnalyzeJournal
  "Upload" button · WorkStudio Analyze tab · Chat attachment · Document
  upload · Monitor objective citation upload · other)
- File type + size (xlsx? csv? .docx? .pdf? approx MB)
- Exact error message visible in the toast / drawer banner
- Browser DevTools Network tab: status code + response body for the
  failing request

## Decision

**HALT.** Do not patch. Surface this diagnosis to the user, ask the 5
questions above, and resume Phase 3 fix only after one or more
questions land on a reproducible failure mode.
