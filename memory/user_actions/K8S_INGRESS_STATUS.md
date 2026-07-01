**Canonical Spec**: `sprints/JC_STORAGE_PIVOT_TIGRIS_RESCOPE.md §2 CRITICAL ESCALATION` + `sprints/JC_STORAGE_PIVOT_TIGRIS_BUILD_MANIFEST.md §2 Architecture` + user's `JC-INLINE-BLOB-SUNSET-PROD-COUNT-RESUME` dispatch (Path A'/B'/C' clarification pending) + user directive from `JC-STORAGE-PIVOT-TIGRIS-RESCOPE` dispatch: "close the matter with the items you have."

**⚠️ 2026-06-30 UPDATE — DO NOT CLOSE ⚠️**: user's platform-side direction to "drop the ingress ticket" was based on the assumption that Emergent Object Store supports browser-direct-presigned uploads (bypassing the ingress for large files). Integration playbook retrieved 2026-06-30 revealed Tigris built-in is BACKEND-MEDIATED (playbook: "No presigned URLs — all access must go through your backend"). Under Path A' (built-in Tigris), the K8s ingress annotation dependency FLIPS from FALLBACK back to LOAD-BEARING for all files > 8 MB (stock nginx-ingress default). See §7 Escalation surface below.

# K8s ingress status — Path A'/B'/C' recontextualization

**Status**: NOT CLOSED (escalation surface open) · disposition depends on user's Path A'/B'/C' choice per `JC_STORAGE_PIVOT_TIGRIS_RESCOPE.md §3`
**Prior status** (pre-2026-06-30 rescope): FALLBACK-ONLY after Azure Blob presigned pivot
**Ticket age**: Open since BUG-ANL-UPLOAD-GRIDFS closure 2026-06-26

---

## 1. Original ask (BUG-ANL-UPLOAD-GRIDFS closure 2026-06-26) — UNCHANGED

Three annotations on the K8s ingress serving `akki.syni.ai`:

```yaml
metadata:
  annotations:
    nginx.ingress.kubernetes.io/proxy-body-size:    "512m"
    nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
    nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
```

---

## 2. Disposition matrix (dependent on rescope Path choice)

| Path | Ingress annotations | Ticket disposition | Rationale |
|---|---|---|---|
| **A'** (built-in Tigris backend-mediated) | LOAD-BEARING for ALL files > 8 MB | **STAYS OPEN** · elevated priority | Backend receives full body before PUTting to Tigris; > 8 MB uploads 413 at ingress without annotations. Contradicts user's "drop the ticket" instruction — this is the escalation trigger |
| **B'** (BYO S3/GCS with user creds, browser-direct-presigned) | FALLBACK only | Can close on presigned prod-evidence per original locked call #5 | Browser bypasses backend for > 16 MB uploads; annotations only insure against Azure/S3 outage |
| **C'** (hybrid: built-in Tigris for small band + BYO S3/GCS presigned for large band) | LOAD-BEARING for the built-in-Tigris band only | STAYS OPEN with band-scoped disposition | Band cutoff determines which flows traverse ingress; annotations govern the built-in-Tigris band exclusively |

**Current state**: Path choice pending. Ticket held open with **escalation-level surface** until user chooses.

---

## 3. Explicit ask to user (recontextualized)

**Q1 (LOAD-BEARING)**: Which path does the user pick? A' (built-in) / B' (BYO creds) / C' (hybrid)?

- **If A'**: user needs to reconcile "drop the ingress ticket" instruction with the reality that ingress annotations become load-bearing for > 8 MB in-band flows. Options:
  - **Option A'-i**: coordinate with Emergent platform to expose ingress annotations after all (annotations are a K8s-level primitive; platform side previously said "not available"; ask to reconfirm under Path A' pressure — the presigned assumption no longer holds so the trade-off is different)
  - **Option A'-ii**: keep files ≤ 8 MB via a stricter threshold `X = 8 MB` (below stock ingress default); files 8-16 MB become unreachable — surfaces as user-visible upload-size cap
  - **Option A'-iii**: accept ingress-limit failure as a soft-launch limitation; solve later
- **If B'**: user provides AWS/GCS credentials via mounted secret path. Ingress annotations remain fallback. Ticket can close per original locked call #5 on presigned prod-evidence.
- **If C'**: user picks band cutoff. Ingress annotations govern built-in-Tigris band. Similar disposition to A' but scoped.

**Q2**: If user picks A' and platform doesn't expose annotations at any tier → is X = 8 MB (below stock ingress default) acceptable as a soft upload cap?

---

## 4. Testable curl command (user can run against prod)

Same as prior version — testing whether the ingress accepts bodies at 1 MB / 12 MB / 100 MB. Interpretation now depends on Path:

- **Under Path A'**: 12 MB and 100 MB tests MUST return 401/405 (not 413). If any return 413, Path A' cannot ship files above whatever the current ingress limit is.
- **Under Path B'**: all three tests can 413 harmlessly — browser-direct-presigned bypasses the ingress; annotations are pure fallback.

```bash
# Test 1 MB — should always work (any Path)
dd if=/dev/urandom of=/tmp/test_1mb.bin bs=1M count=1 2>/dev/null
curl -s -o /dev/null -w "HTTP=%{http_code}\n" \
  -X POST https://akki.syni.ai/api/health/echo \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/tmp/test_1mb.bin

# Test 12 MB — Path A' critical band; Path B' don't-care
dd if=/dev/urandom of=/tmp/test_12mb.bin bs=1M count=12 2>/dev/null
curl -s -o /dev/null -w "HTTP=%{http_code}\n" \
  -X POST https://akki.syni.ai/api/health/echo \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/tmp/test_12mb.bin

# Test 100 MB — Path A' catastrophic if ingress caps below 512m; Path B' don't-care
dd if=/dev/urandom of=/tmp/test_100mb.bin bs=1M count=100 2>/dev/null
curl -s -o /dev/null -w "HTTP=%{http_code}\n" \
  -X POST https://akki.syni.ai/api/health/echo \
  -H "Content-Type: application/octet-stream" \
  --data-binary @/tmp/test_100mb.bin

# Cleanup
rm -f /tmp/test_*mb.bin
```

---

## 5. Ticket disposition history

| Date | Event |
|---|---|
| 2026-06-26 | BUG-ANL-UPLOAD-GRIDFS closed; ingress ticket opened at value `proxy-body-size: 512m` (pending user/platform apply) |
| 2026-06-30 (Azure rescope) | Ticket recontextualized as FALLBACK-only after Azure Blob presigned architecture pivot; stays open until presigned prod-evidence per user locked call #5 |
| 2026-06-30 (user platform-side direction) | User said "K8s ingress annotations are NOT available through the platform. Drop the ingress ticket. Presigned-only, no fallback." — instruction predicated on browser-direct-presigned architecture |
| 2026-06-30 (Tigris rescope) | Integration playbook revealed built-in Tigris is BACKEND-MEDIATED (no presigned). Ingress annotation dependency FLIPS back to LOAD-BEARING under Path A'. Ticket disposition escalated to user for A'/B'/C' resolution. **Ticket NOT CLOSED.** |

---

## 6. Cross-references

- Original ask: `sprints/BUG_ANALYZE_UPLOAD.md §USER_ACTION_CHECKLIST 🔴 #1`
- Azure pivot recontextualization: `sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §9`
- Tigris rescope + escalation: `sprints/JC_STORAGE_PIVOT_TIGRIS_RESCOPE.md §2 + §3`
- Tigris build manifest (Path A' assumption): `sprints/JC_STORAGE_PIVOT_TIGRIS_BUILD_MANIFEST.md §2 Architecture`
- Sunset eval Gate B (updated with Tigris finding): `sprints/JC_INLINE_BLOB_SUNSET_EVALUATION.md §Gate B`
- Runbook: `memory/runbooks/PROD_INGRESS_AND_MEMORY.md` lines 68-73

---

## 7. Escalation surface (HARD STOP)

**User direction needed** to resolve the ticket disposition:

1. Pick Path A' / B' / C' (per `JC_STORAGE_PIVOT_TIGRIS_RESCOPE.md §3`)
2. If A': confirm Q2 above (accept 8 MB soft cap? OR reconfirm with Emergent platform side on annotation availability under Tigris backend-mediated pressure?)
3. Once path is chosen: this ticket status flips to CLOSED (Path B') / STAYS OPEN with band-scoped disposition (Path C') / STAYS OPEN at elevated priority (Path A')

Ticket does NOT auto-close per user's earlier "drop the ticket" instruction because that instruction was predicated on an architectural assumption that the platform-built-in Tigris does not satisfy.
