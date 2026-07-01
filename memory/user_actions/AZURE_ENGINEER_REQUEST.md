**Canonical Spec**: `/app/memory/sprints/JC_STORAGE_PIVOT_AZURE_SAS_BUILD_MANIFEST.md §0 Fire-trigger preconditions` (all 3 credential-gating preconditions user-provided at dispatch time) + `/app/memory/sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §7 Dependencies + §11 D3+D8` (managed-identity → user-delegation-SAS auth model · single storage account · app-region default) + `/app/memory/sprints/JC_INLINE_BLOB_SUNSET_EVALUATION.md §Gate A` (prod Atlas creds via k8s secret mount) + `/app/memory/user_actions/K8S_INGRESS_STATUS.md` (ingress annotations fallback disposition).

# Azure engineer request — forwardable ops brief

**How to use this doc**: forward to your Azure/DevOps engineer. Four tasks with `az cli` templates. Engineer fills placeholders, runs commands, sends 7 confirmations back.

**Coordination note**: Task 3 (k8s secret mount) may require **Emergent platform side involvement** for pod mount changes — surface if unsure.

---

## Task 1 — Provision Azure Blob storage account

### 1.1 Storage account

```bash
# Placeholders:
#   <STORAGE_ACCOUNT>   e.g., akkistorage
#   <REGION>            SAME AS APP REGION — user to specify (currently NOT set in AKKI env)
#   <RG>                target resource group

az storage account create \
  --name "<STORAGE_ACCOUNT>" \
  --resource-group "<RG>" \
  --location "<REGION>" \
  --sku Standard_LRS \
  --kind StorageV2 \
  --access-tier Hot \
  --enable-hierarchical-namespace false \
  --allow-blob-public-access false \
  --min-tls-version TLS1_2 \
  --default-action Allow
```

**Justifications**:
- **Standard general-purpose v2 (`StorageV2`)**: cheapest tier that supports blob versioning + soft delete + user-delegation SAS. Premium is 5-10× the cost with no functional benefit for our workload (workbook uploads are ≤ 512 MB, read a few times, then archived).
- **LRS vs ZRS**: **LRS recommended for launch**. ZRS is ~1.5× the cost and provides zone-redundancy within a single region. Our workload is workbook uploads (users can re-upload if a zone fails; not mission-critical hot data). Upgrade to ZRS later if audit/SOC-2 requires it.
- **`--allow-blob-public-access false`**: mandatory. All access via managed identity + SAS.
- **TLS 1.2 min**: standard hardening.

### 1.2 Enable blob versioning + soft-delete

```bash
az storage account blob-service-properties update \
  --account-name "<STORAGE_ACCOUNT>" \
  --resource-group "<RG>" \
  --enable-versioning true \
  --enable-delete-retention true \
  --delete-retention-days 7 \
  --enable-container-delete-retention true \
  --container-delete-retention-days 7
```

**Rationale**:
- **Versioning**: rollback safety. If a workbook upload gets corrupted or overwritten, the prior version is recoverable.
- **Soft delete 7 days**: deletes are recoverable for a week. Standard "oh sh*t" retention window.

### 1.3 Create 4 containers

```bash
for C in workbook-uploads analysis-uploads workbook-archive analysis-archive; do
  az storage container create \
    --account-name "<STORAGE_ACCOUNT>" \
    --name "$C" \
    --auth-mode login \
    --public-access off
done
```

### 1.4 Lifecycle rules (24h staging expiry for `-uploads` containers)

Create `lifecycle.json`:

```json
{
  "rules": [
    {
      "name": "expire-workbook-uploads-24h",
      "enabled": true,
      "type": "Lifecycle",
      "definition": {
        "filters": {"blobTypes": ["blockBlob"], "prefixMatch": ["workbook-uploads/"]},
        "actions": {"baseBlob": {"delete": {"daysAfterCreationGreaterThan": 1}}}
      }
    },
    {
      "name": "expire-analysis-uploads-24h",
      "enabled": true,
      "type": "Lifecycle",
      "definition": {
        "filters": {"blobTypes": ["blockBlob"], "prefixMatch": ["analysis-uploads/"]},
        "actions": {"baseBlob": {"delete": {"daysAfterCreationGreaterThan": 1}}}
      }
    }
  ]
}
```

Apply:
```bash
az storage account management-policy create \
  --account-name "<STORAGE_ACCOUNT>" \
  --resource-group "<RG>" \
  --policy @lifecycle.json
```

**Rationale**: `-uploads` containers are staging areas. Files are copied to `-archive` counterparts once analysis completes. 24 h grace covers async analysis latency + one retry.

### 1.5 CORS rules on the storage account

```bash
az storage cors add \
  --services b \
  --methods PUT GET DELETE HEAD OPTIONS \
  --origins "https://akki.syni.ai" \
  --allowed-headers "x-ms-blob-type,x-ms-blob-content-type,Content-Type,Content-Length,Authorization,x-ms-date,x-ms-version" \
  --exposed-headers "ETag,x-ms-request-id,Content-Length,Content-Type" \
  --max-age 3600 \
  --account-name "<STORAGE_ACCOUNT>"
```

**Origins**: `https://akki.syni.ai` for prod. If you have preview/staging origins, add them too (one `az storage cors add` per origin).
**Methods**: `PUT` for browser upload; `GET` for download; `DELETE` for lifecycle cleanup rehearsals; `HEAD` for existence checks; `OPTIONS` for CORS preflight (mandatory).
**Max-age 3600**: browsers cache the preflight for 1 hour, reducing OPTIONS chatter.

---

## Task 2 — Managed identity binding

### 2.1 Create user-assigned managed identity

```bash
# Placeholders:
#   <MI_NAME>   e.g., akki-backend-mi
#   <RG>        target resource group
#   <REGION>    same as storage account

az identity create \
  --name "<MI_NAME>" \
  --resource-group "<RG>" \
  --location "<REGION>"

# Capture:
export MI_CLIENT_ID=$(az identity show --name "<MI_NAME>" --resource-group "<RG>" --query clientId -o tsv)
export MI_PRINCIPAL_ID=$(az identity show --name "<MI_NAME>" --resource-group "<RG>" --query principalId -o tsv)
```

### 2.2 Grant `Storage Blob Data Contributor` on the storage account

```bash
STORAGE_ID=$(az storage account show --name "<STORAGE_ACCOUNT>" --resource-group "<RG>" --query id -o tsv)

az role assignment create \
  --assignee "$MI_PRINCIPAL_ID" \
  --role "Storage Blob Data Contributor" \
  --scope "$STORAGE_ID"
```

**Why this role**: the AKKI backend needs to (a) issue user-delegation SAS tokens (requires `Storage Blob Delegator` implicit; granted by `Data Contributor`); (b) read/write blobs directly for archive moves + backfill; (c) list containers for admin health checks. `Data Contributor` is the least-privilege role covering all three.

### 2.3 Bind managed identity to the Emergent backend pod

**COORDINATION NEEDED WITH EMERGENT PLATFORM SIDE** — the pod may already be running with a service-principal or system-assigned MI. If unsure, ask Emergent support to confirm the current identity model.

Two paths depending on Emergent platform posture:

**Path A — Azure AKS with workload identity federation** (recommended if available):
```bash
# Federate the MI to the k8s service account used by the backend pod
az identity federated-credential create \
  --identity-name "<MI_NAME>" \
  --resource-group "<RG>" \
  --name "akki-backend-federation" \
  --issuer "<OIDC_ISSUER_URL_from_AKS_cluster>" \
  --subject "system:serviceaccount:<K8S_NAMESPACE>:<K8S_SERVICE_ACCOUNT>" \
  --audience "api://AzureADTokenExchange"
```

**Path B — Static MI credentials mounted as env var** (fallback if federation not available):
Emergent platform mounts `AZURE_MANAGED_IDENTITY_CLIENT_ID` env var into the backend pod. Backend uses `DefaultAzureCredential` from `azure-identity` which picks up the client ID automatically.

Return to user: **`MI_CLIENT_ID`** (the client ID from step 2.1). The AKKI backend needs this env var name/value to connect.

---

## Task 3 — k8s secret mount for prod Atlas connection string (Gate A resume)

**Purpose**: one-shot mount so the AKKI backend can execute the prod Atlas row-count query for the inline-blob sunset gate. **Mount for the count query only; unmount immediately after report.**

### 3.1 Create the secret

```bash
# Placeholders:
#   <K8S_NAMESPACE>       e.g., akki-prod
#   <PROD_ATLAS_URI>      the prod Atlas connection string (mongodb+srv://...)

kubectl create secret generic prod-mongo \
  --namespace "<K8S_NAMESPACE>" \
  --from-literal=connection-string="<PROD_ATLAS_URI>"
```

### 3.2 Mount into the backend pod

Add to the backend pod's manifest (typically part of the Emergent platform pod spec — coordinate):

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
        defaultMode: 0400  # read-only, owner-only
        items:
          - key: connection-string
            path: connection-string   # yields file /var/run/secrets/prod-mongo/connection-string
```

**Permissions**: `0400` (read-only, owner). File `connection-string` inside the mount dir.

### 3.3 Contract for the AKKI agent

Per user contract in `JC_INLINE_BLOB_SUNSET_EVALUATION.md §Gate A` update note:
- Agent reads the mount file **once**, connects to prod Atlas, executes the row-count query, disconnects, reports counts only
- Agent NEVER logs the raw connection string, NEVER writes it to any file, NEVER echoes it
- Post-count, mount is UNMOUNTED by the Azure/platform engineer (agent will surface "count complete; please unmount")

### 3.4 Timing

Coordinate a ~5-minute window with Emergent platform side. Sequence: (1) engineer applies the mount → (2) engineer notifies user → (3) user dispatches `JC-INLINE-BLOB-SUNSET-PROD-COUNT-RESUME-2` in AKKI → (4) agent reads mount + runs query + reports counts + surfaces "please unmount" → (5) engineer removes the mount + secret.

---

## Task 4 — K8s ingress annotations (fallback per Gate B)

See `memory/user_actions/K8S_INGRESS_STATUS.md` §1 for the 3 annotations. Ask engineer to confirm one of:
- **Already applied** → send current `proxy-body-size` value (must be ≥ 512m) for our audit trail
- **Not applied** → apply per Task 1.1 of that doc, or explicitly decline (accepting presigned-only path)

Testable curl commands to verify are in `K8S_INGRESS_STATUS.md §4`.

---

## Deliverables checklist (what engineer sends back to user)

| # | Deliverable | Format |
|---|---|---|
| 1 | Storage account **name** | `<STORAGE_ACCOUNT>` (plain string; the account KEY is NOT needed — managed identity handles auth) |
| 2 | Storage account **region** | `<REGION>` (e.g., `westus2`, `eastus`) |
| 3 | Managed identity **client ID** | `<MI_CLIENT_ID>` (32-char GUID; the backend uses this to authenticate) |
| 4 | Confirmation of **`Storage Blob Data Contributor`** role granted | Screenshot of role assignment or `az role assignment list` output |
| 5 | Confirmation of **CORS rules** applied on the storage account | `az storage cors list --services b --account-name "<STORAGE_ACCOUNT>"` output |
| 6 | Confirmation of **prod Atlas creds mount** (with timing) | Approx window when the mount will be applied + notification to user when live |
| 7 | Confirmation of **ingress annotations** status | "Already applied at value X", "Applied per request", or "Declined — presigned-only" |

**Do NOT send**: raw storage account keys · raw prod Atlas connection string · any password/secret material. Use managed identity + mounted secret patterns exclusively.

---

## Cross-references

- Storage arc scope: `sprints/JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §7 Dependencies · §11 D3+D8 decisions · §12 pivot-vector`
- Build manifest fire-trigger preconditions: `sprints/JC_STORAGE_PIVOT_AZURE_SAS_BUILD_MANIFEST.md §0`
- Managed-identity → SAS auth model: `JC_STORAGE_PIVOT_AZURE_SAS_ADVANCE.md §11 D2+D7 folded`
- Prod Atlas creds gate: `sprints/JC_INLINE_BLOB_SUNSET_EVALUATION.md §8.1 Gate A` (with mount-absent halt update 2026-06-30)
- Ingress annotations context: `memory/user_actions/K8S_INGRESS_STATUS.md`
