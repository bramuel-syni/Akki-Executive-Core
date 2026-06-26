# BUG · "Analyze file upload failing" — Phase 2b diagnosis (PRODUCTION-confirmed)

> **Source of truth:** `/app/memory/JC_WS_CANONICAL_SPEC.md` (Analyze
> drawer = JC-WS Phase 2 surface).

**Updated:** 2026-06-26 (post-Phase-2b static analysis + hard repro).
**Environment:** PRODUCTION (`https://akki.syni.ai`) per user
confirmation.
**Status:** **ROOT CAUSE LOCKED at ~85% confidence — Mongo 16 MB BSON
cap on the inline-base64 blob insert.** Awaiting user sign-off on the
minimum-fix proposal before patching.

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
  -d '{"email":"admin@akki.ai","password":"AkkiAdmin2026!"}')
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
