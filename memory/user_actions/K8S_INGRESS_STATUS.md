**Canonical Spec**: `/app/memory/sprints/BUG_ANALYZE_UPLOAD.md §USER_ACTION_CHECKLIST 🔴 #1` (original ingress annotation ask) + `/app/memory/sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §9 K8s ingress ticket disposition` (post-pivot ingress recontextualization) + user locked call #5 ("Keep K8s ingress ticket open until presigned proven in prod").

# K8s ingress status — precise ask + fallback disposition

**Status**: FALLBACK-ONLY after Azure Blob presigned architecture pivot. NOT a hard blocker for storage arc if presigned proves in prod. Explicit user ask below.

---

## 1. Original ask (BUG-ANL-UPLOAD-GRIDFS closure 2026-06-26)

Three annotations on the K8s ingress serving `akki.syni.ai`:

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size:    "512m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
```

**Why originally asked**: GridFS migration (BUG-ANL-UPLOAD-GRIDFS) removed the inline base-64 upload path but kept the ingress → nginx → FastAPI upload flow for files up to 512 MB. Without the annotations, the K8s ingress would 413/504 on files above whatever the cluster default is (typically 1-8 MB on stock nginx-ingress; higher on managed K8s but still below 512 MB).

---

## 2. Current recontextualization after Azure Blob presigned pivot

Per `JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §9`, the storage arc introduces a **layered architecture**:

| File size band | Path | Ingress dependency |
|---|---|---|
| ≤ X MB (X = 16 MB recommended per §1.1 row 4) | GridFS via in-band upload → K8s ingress → FastAPI → GridFS | **Ingress annotations REQUIRED** for 8-16 MB band on stock nginx-ingress |
| > X MB | Presigned direct-to-Azure-Blob (SAS-authenticated PUT from browser → Azure Blob) | **Ingress NOT traversed** for the upload body itself; only the SAS-issuer round-trip goes through ingress (small JSON, ~1 KB) |

**So the ingress annotations are now**:
- **Load-bearing** for the 8-16 MB in-band GridFS band. If a user uploads a 12 MB file and the annotations are NOT applied, the ingress 413s and the file never reaches GridFS.
- **NOT required** for files > 16 MB — those bypass the ingress via presigned direct-to-Azure.
- **Fallback insurance** if the presigned flow itself fails mid-upload (Azure outage, SAS-signing failure, CORS misconfig on the storage account, managed-identity binding revoked). In those cases the FE would fall back to in-band GridFS for any file ≤ 512 MB — requiring the annotations to accept up to 512m.

---

## 3. Explicit ask to user

**Q1**: Are the 3 ingress annotations already applied to the `akki.syni.ai` ingress by your team?

- **Yes → excellent**. We keep the ticket open until presigned proves in prod (per user locked call #5), then can consider narrowing the annotation to a smaller value if you prefer, or leave at 512m as fallback insurance.
- **No → decision point**:
  - Option A: **Apply now** — restores the 8-16 MB in-band GridFS band + gives you fallback insurance against Azure outages. Recommended.
  - Option B: **Skip permanently** — accept that (a) 8-16 MB files fail on the ingress until presigned lights up + Azure engineer finishes provisioning; (b) if the presigned flow fails post-launch, there's no fallback path for large files. Only viable if you're willing to run presigned-only with no fallback.

**Q2**: If Yes, can you share the current `proxy-body-size` value so we can verify it's ≥ 512m? A `kubectl` command from your team would be enough.

---

## 4. Testable curl command (user can run against prod)

Send a POST to `akki.syni.ai` with a known body size and observe response codes:

```bash
# Test 1 MB body — should always work
dd if=/dev/urandom of=/tmp/test_1mb.bin bs=1M count=1 2>/dev/null
curl -s -o /dev/null -w "HTTP=%{http_code} size=%{size_upload}\n" \
  -X POST https://akki.syni.ai/api/health/echo \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/tmp/test_1mb.bin
# Expected: HTTP=401 or 405 (auth/method mismatch is fine; means the ingress DID accept the body)
# Failure mode: HTTP=413 → ingress rejected before FastAPI saw it

# Test 12 MB body — the 8-16 MB in-band band that the annotation directly gates
dd if=/dev/urandom of=/tmp/test_12mb.bin bs=1M count=12 2>/dev/null
curl -s -o /dev/null -w "HTTP=%{http_code} size=%{size_upload}\n" \
  -X POST https://akki.syni.ai/api/health/echo \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/tmp/test_12mb.bin
# Expected if annotations applied: HTTP=401 or 405 (body accepted, backend rejected on auth)
# Expected if annotations NOT applied on stock nginx-ingress: HTTP=413 (Payload Too Large)

# Test 100 MB body — well above stock defaults, needs 512m annotation
dd if=/dev/urandom of=/tmp/test_100mb.bin bs=1M count=100 2>/dev/null
curl -s -o /dev/null -w "HTTP=%{http_code} size=%{size_upload}\n" \
  -X POST https://akki.syni.ai/api/health/echo \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/tmp/test_100mb.bin
# Expected if annotations applied: HTTP=401 or 405
# Expected if annotations NOT applied: HTTP=413 (definitively fails)
```

**Interpretation**:
- All three return 401/405/etc. (not 413) → annotations applied correctly, ≥ 512m in place. **DONE**.
- The 1 MB works but 12 MB or 100 MB return 413 → annotations NOT applied (or applied at a lower value). Please apply per §1.
- All three return 413 → ingress default is unusually low. Please investigate.

**Cleanup**: `rm -f /tmp/test_*mb.bin` after testing.

---

## 5. Ticket disposition per user locked call #5

Per user call #5 in `JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md`:
> "Keep K8s ingress ticket open until a real large-file upload lands end-to-end through the presigned flow in prod. Close on evidence, then."

**Current state**: Ticket OPEN. Closure evidence expected from `JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §9` closure checklist:
1. First 100 MB file successfully uploaded end-to-end via `POST /api/workbook/upload/presigned-url` → browser PUT to Azure Blob → analyze completes
2. NO 413/502/504 at the K8s ingress for that upload (verified via ingress access logs)
3. NO SAS-signing failure surfaced in backend logs

Until then, annotations remain at `512m` + `300s` timeouts.

---

## 6. Cross-references

- Original ask: `sprints/BUG_ANALYZE_UPLOAD.md §USER_ACTION_CHECKLIST 🔴 #1` (lines 116-134)
- Post-pivot ingress recontextualization: `sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §9` (lines 330-346)
- Locked user call #5: same memo `§11 D8` (region locked; ingress ticket stays open until presigned proves)
- Runbook: `memory/runbooks/PROD_INGRESS_AND_MEMORY.md` lines 68-73 (default ingress body limits + historical `akki.syni.ai` value)
- BUG memo comment block: `nginx/frontend.conf` at internal proxy (`client_max_body_size 50m → 512m`) — the OUTER K8s ingress is what we're asking about here, not the inner nginx that BUG closure did fix
