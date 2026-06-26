# BUG · "Analyze file upload failing" — Phase 2 diagnosis

> **Source of truth:** `/app/memory/JC_WS_CANONICAL_SPEC.md` (referenced
> per dispatch — Analyze drawer is JC-WS Phase 2 surface).

**Produced:** 2026-06-26 (preview env, post Track-2 close).
**Status:** **CANNOT REPRODUCE in preview · awaiting environment clarification.**
**Recommendation:** HALT and surface — do NOT patch until user confirms
which environment + which failure mode.

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
