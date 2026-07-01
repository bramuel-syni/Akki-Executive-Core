**Canonical Spec**: `sprints/BUG_ANALYZE_UPLOAD.md §USER_ACTION_CHECKLIST 🔴 #1` (original ingress annotation ask) + `sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §9 K8s ingress ticket disposition` (Azure presigned model = fallback-open) + user locked call #5 ("Keep K8s ingress ticket open until presigned proven in prod") + `sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §13` (Tigris pivot on-hold 2026-06-30) + Emergent-support-question in flight on presigned wrapper.

# K8s ingress status — FALLBACK-OPEN (Azure presigned model reinstated 2026-06-30)

**Status**: FALLBACK-OPEN. Azure Blob presigned architecture is primary again per user reinstate direction 2026-06-30. Annotations serve as fallback insurance; ticket stays open until first prod large-file upload lands end-to-end through the presigned flow (locked call #5). Tigris rescope is on-hold pending Emergent support clarification on presigned-URL support.

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

**Why originally asked**: GridFS migration (BUG-ANL-UPLOAD-GRIDFS) removed inline base-64 upload but kept the ingress → nginx → FastAPI upload flow for files up to 512 MB. Without annotations, ingress 413s on files above stock default (~1-8 MB).

---

## 2. Current disposition (2026-06-30 reinstate)

Azure Blob presigned architecture (per `sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md`) is primary again. Layered architecture:

| File size band | Path | Ingress dependency |
|---|---|---|
| ≤ 16 MB (per D1 threshold) | GridFS via in-band upload → K8s ingress → FastAPI → GridFS | Annotations REQUIRED for 8-16 MB band |
| > 16 MB | Presigned direct-to-Azure-Blob (SAS-authenticated PUT from browser → Azure Blob) | Ingress NOT traversed for the upload body itself |

**Under this architecture, ingress annotations are**:
- **Load-bearing** for the 8-16 MB in-band GridFS band
- **NOT required** for files > 16 MB (browser bypasses ingress via presigned)
- **Fallback insurance** if the presigned flow itself fails (Azure outage, SAS-signing failure, CORS misconfig, MI-binding revoked). Fallback path is in-band GridFS for any file ≤ 512 MB — requires annotations.

**Ticket disposition**: OPEN as fallback-insurance until first prod large-file upload lands end-to-end through presigned per locked call #5.

---

## 3. Explicit ask to user (unchanged from earlier state)

**Q1**: Are the 3 ingress annotations already applied to the `akki.syni.ai` ingress by your team?

- **Yes**: keep ticket open until presigned proves in prod (per locked call #5), then consider narrowing or leaving at 512m fallback insurance.
- **No**:
  - Option A: Apply now — restores 8-16 MB in-band GridFS band + gives fallback insurance against Azure outages. Recommended.
  - Option B: Skip permanently — accept 8-16 MB files fail on ingress until presigned lights up + no fallback if presigned flow fails post-launch.

**Q2**: If Yes, share the current `proxy-body-size` value so we can verify it's ≥ 512m.

---

## 4. Testable curl command (user can run against prod)

Same shape as prior versions — verify ingress limit at 1 MB / 12 MB / 100 MB body sizes.

```bash
# 1 MB — should always work
dd if=/dev/urandom of=/tmp/test_1mb.bin bs=1M count=1 2>/dev/null
curl -s -o /dev/null -w "HTTP=%{http_code}\n" -X POST https://akki.syni.ai/api/health/echo \
  -H "Content-Type: application/octet-stream" --data-binary @/tmp/test_1mb.bin

# 12 MB — 8-16 MB band that annotation gates
dd if=/dev/urandom of=/tmp/test_12mb.bin bs=1M count=12 2>/dev/null
curl -s -o /dev/null -w "HTTP=%{http_code}\n" -X POST https://akki.syni.ai/api/health/echo \
  -H "Content-Type: application/octet-stream" --data-binary @/tmp/test_12mb.bin

# 100 MB — well above stock defaults; needs 512m annotation
dd if=/dev/urandom of=/tmp/test_100mb.bin bs=1M count=100 2>/dev/null
curl -s -o /dev/null -w "HTTP=%{http_code}\n" -X POST https://akki.syni.ai/api/health/echo \
  -H "Content-Type: application/octet-stream" --data-binary @/tmp/test_100mb.bin

rm -f /tmp/test_*mb.bin
```

Interpretation:
- All 3 return 401/405/etc. (not 413) → annotations applied correctly ≥ 512m
- 12 MB or 100 MB returns 413 → annotations NOT applied
- All 3 return 413 → ingress default unusually low; investigate

---

## 5. Ticket disposition history

| Date | Event |
|---|---|
| 2026-06-26 | BUG-ANL-UPLOAD-GRIDFS closed; ingress ticket opened at value `proxy-body-size: 512m` |
| 2026-06-30 (Azure Blob rescope) | Ticket recontextualized as FALLBACK-only after Azure Blob presigned pivot; stays open until presigned prod-evidence per locked call #5 |
| 2026-06-30 (Tigris rescope attempted) | Ticket briefly flipped to LOAD-BEARING under Tigris backend-mediated architecture (playbook contradicted browser-direct-presigned assumption); escalation surfaced |
| **2026-06-30 (Azure reinstate)** | Azure Blob presigned reinstated as primary path per user direction. Ticket reverts to FALLBACK-OPEN (Azure presigned model). Tigris ON-HOLD pending Emergent support clarification on presigned wrapper support. |

---

## 6. Cross-references

- Original ask: `sprints/BUG_ANALYZE_UPLOAD.md §USER_ACTION_CHECKLIST 🔴 #1` (lines 116-134)
- Primary storage scope (reinstated): `sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md` §9 (ingress disposition) + §13 (Tigris on-hold note)
- Primary build manifest: `sprints/JC_STORAGE_PIVOT_AZURE_SAS_BUILD_MANIFEST.md`
- Tigris rescope (ON-HOLD; pending Emergent support): `sprints/JC_STORAGE_PIVOT_TIGRIS_RESCOPE.md`
- Emergent support question in flight: whether the Emergent Object Store wrapper supports browser-direct-presigned URLs (integration playbook 2026-06-30 said no; user's platform-side pursuing clarification)
- Runbook: `memory/runbooks/PROD_INGRESS_AND_MEMORY.md` lines 68-73
