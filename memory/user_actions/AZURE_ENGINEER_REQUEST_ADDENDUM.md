**Canonical Spec**: `sprints/JC_STORAGE_PIVOT_TIGRIS_RESCOPE.md` (Tigris storage pivot 2026-06-30) + `sprints/JC_STORAGE_PIVOT_TIGRIS_BUILD_MANIFEST.md` (Path A' manifest) + predecessor `user_actions/AZURE_ENGINEER_REQUEST.md` (Azure-scoped brief now partially superseded).

# Azure engineer request — addendum

**Purpose**: single-page follow-up note for the Azure/DevOps engineer who received the earlier `AZURE_ENGINEER_REQUEST.md` brief. Storage architecture has pivoted from Azure Blob presigned → Emergent Object Store (Tigris, built-in). **3 of 4 tasks are DROPPED**. Only Task 3 (prod Atlas mount) remains.

---

## Summary

| Task | Status | Reason |
|---|---|---|
| Task 1 — Provision Azure Blob storage account (containers, CORS, lifecycle, versioning, soft-delete) | ❌ **DROPPED** | Emergent platform provides built-in Tigris object storage; no user-side Azure provisioning needed |
| Task 2 — Managed identity binding + Storage Blob Data Contributor role | ❌ **DROPPED** | Tigris built-in uses `EMERGENT_LLM_KEY` (already provisioned); no managed identity needed |
| **Task 3 — k8s secret mount for prod Atlas connection string at `/var/run/secrets/prod-mongo`** | ✅ **STILL NEEDED** | Unrelated to storage pivot; still gates inline-blob sunset row-count query per `sprints/JC_INLINE_BLOB_SUNSET_EVALUATION.md §Gate A` |
| Task 4 — K8s ingress annotations (`proxy-body-size: 512m` + timeouts) | ⚠️ **DISPOSITION IN FLUX** | User's platform-side previously said annotations not exposed. Under Tigris built-in backend-mediated architecture (not browser-direct-presigned), the annotations are load-bearing again for > 8 MB uploads. Awaiting user direction on Path A'/B'/C' (see `user_actions/K8S_INGRESS_STATUS.md`). If path resolves to needing annotations, this task re-opens. |

---

## What remains for the engineer

### Task 3 (unchanged from earlier brief)

**k8s secret mount for prod Atlas connection string.**

```bash
# Placeholders:
#   <K8S_NAMESPACE>       e.g., akki-prod
#   <PROD_ATLAS_URI>      the prod Atlas connection string (mongodb+srv://...)

kubectl create secret generic prod-mongo \
  --namespace "<K8S_NAMESPACE>" \
  --from-literal=connection-string="<PROD_ATLAS_URI>"
```

Mount into backend pod (coordinate with Emergent platform side):

```yaml
spec:
  containers:
    - name: backend
      volumeMounts:
        - name: prod-mongo
          mountPath: /var/run/secrets/prod-mongo
          readOnly: true
  volumes:
    - name: prod-mongo
      secret:
        secretName: prod-mongo
        defaultMode: 0400
        items:
          - key: connection-string
            path: connection-string
```

**Contract**: mount for one-shot row-count query; agent reads once + disconnects + reports counts; engineer/platform unmounts immediately after.

**Timing**: ~5-minute window. Sequence: engineer applies mount → notifies user → user dispatches `JC-INLINE-BLOB-SUNSET-PROD-COUNT-RESUME-2` in AKKI → agent reads + queries + reports + surfaces "please unmount" → engineer removes mount + secret.

---

## What the engineer no longer needs to do (from earlier brief)

- ❌ `az storage account create` (Task 1.1)
- ❌ Blob versioning + soft-delete config (Task 1.2)
- ❌ 4-container creation (Task 1.3)
- ❌ Lifecycle rules JSON + apply (Task 1.4)
- ❌ CORS rules on the storage account (Task 1.5)
- ❌ User-assigned managed identity (Task 2.1)
- ❌ Storage Blob Data Contributor role assignment (Task 2.2)
- ❌ Federated credential / MI-to-pod binding (Task 2.3)

The Azure work becomes relevant again ONLY if user pivots to Path B' (BYO S3/GCS with user creds) or C' (hybrid) — in which case the target moves from Azure Blob to AWS S3 or GCP GCS (playbook TBD; separate brief will follow).

---

## Deliverables checklist (reduced)

| # | Deliverable | Format |
|---|---|---|
| 1 | Confirmation of **prod Atlas creds mount** (with timing) | Approx window when mount will be applied + notification to user when live |
| 2 | (Optional) Confirmation on **ingress annotation availability** re-check under Tigris backend-mediated pressure | "Available at value X" / "Not available; user must accept X MB soft cap" |

**Do NOT send**: raw prod Atlas connection string · any password/secret material.

---

## Cross-references

- Original Azure brief (partially superseded): `user_actions/AZURE_ENGINEER_REQUEST.md`
- Storage pivot rescope: `sprints/JC_STORAGE_PIVOT_TIGRIS_RESCOPE.md`
- Tigris build manifest (Path A'): `sprints/JC_STORAGE_PIVOT_TIGRIS_BUILD_MANIFEST.md`
- Gate A (prod Atlas creds — this addendum's Task 3): `sprints/JC_INLINE_BLOB_SUNSET_EVALUATION.md §Gate A`
- Ingress status (Task 4 disposition): `user_actions/K8S_INGRESS_STATUS.md`
