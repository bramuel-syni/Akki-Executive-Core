# PROD_INGRESS_AND_MEMORY — Runbook for the GridFS upload migration

**Canonical spec:** `/app/memory/JC_WS_CANONICAL_SPEC.md` (Analyze
submodule of JC-WS). Closes the BUG-ANL-UPLOAD-GRIDFS dispatch
deployment gate per `sprints/BUG_ANALYZE_UPLOAD.md`.

This runbook covers the **two infra knobs** that must be tightened
in the production cluster before users can upload workbooks ≥ 50 MB.
Without them, the new GridFS path on the backend works correctly,
but uploads ≥ 50 MB will be rejected at the K8s ingress (HTTP 413)
BEFORE the request ever reaches FastAPI.

## The three commands

Set these once per ingress + per deployment. Re-running is safe
(annotations + resource limits are idempotent in `kubectl`).

```bash
# 1. Raise ingress body-size limit  (50 MB → 512 MB)
kubectl annotate ingress <ingress-name> \
  nginx.ingress.kubernetes.io/proxy-body-size=512m \
  --overwrite

# 2. Raise ingress read+send timeouts  (120s → 300s)
kubectl annotate ingress <ingress-name> \
  nginx.ingress.kubernetes.io/proxy-read-timeout=300 \
  nginx.ingress.kubernetes.io/proxy-send-timeout=300 \
  --overwrite

# 3. Bump backend pod memory request/limit  (≥ 1 GiB / 2 GiB)
kubectl patch deployment <deployment-name> -p '{
  "spec": {"template": {"spec": {"containers": [
    {
      "name": "<container-name>",
      "resources": {
        "requests": {"memory": "1Gi"},
        "limits":   {"memory": "2Gi"}
      }
    }
  ]}}}
}'
```

Replace `<ingress-name>`, `<deployment-name>`, `<container-name>`
with the production values. The expected ingress name on
`akki.syni.ai` is the one fronting the backend service.

## How to verify

```bash
# Ingress annotations applied — check the proxy-body-size + timeouts
kubectl describe ingress <ingress-name> | grep -E "proxy-body-size|proxy-read-timeout|proxy-send-timeout"

# Pod memory limits applied — check Limits + Requests on the running pod
kubectl describe pod -l app=<deployment-name> | grep -E "Limits|Requests|memory"

# End-to-end smoke (after annotations propagate, ~30s):
#   - Sign in as a real user
#   - Upload a 250 MB CSV via the Analyze drawer
#   - Expect 200, NOT 413
```

## What happens if these are NOT applied

The backend code change (GridFS migration) is fully forward-compatible.
The user will see degraded behaviour, not breakage:

- **Uploads > 50 MB**: HTTP 413 from the ingress (the default
  nginx-ingress `proxy-body-size` is `1m` or `8m` depending on
  cluster defaults; production `akki.syni.ai` was set to a higher
  value historically but is below the 512 MB the new code expects).
  Symptom: "Request Entity Too Large" before any backend log line
  emits.
- **Uploads of any size on slow connections**: timeout at the
  ingress after 120s. Symptom: connection reset, no FastAPI log.
- **Reads (no change)**: All reads — including LEGACY `data_b64`
  rows — continue to work because `read_workbook_bytes` dual-reads.
  Nothing user-facing breaks on the read side, ever.

## After applying — the 24-hour dual-read soak window

Per the AUTONOMOUS BACKLOG RUN contract, the optional backfill
(`scripts/jc_bug_analyze_upload_backfill.py --commit`) runs ONLY
AFTER:

1. The new GridFS code has soaked in production for 24 hours
2. The dry-run report against prod Atlas is clean (no decode failures)
3. Pod memory is verified ≥ 1 GiB

The dual-read helper makes the legacy `data_b64` rows non-blocking —
they continue to work indefinitely without the backfill. The
backfill is a storage-consolidation step, not a correctness step.

## Rollback if anything goes sideways

The backend code is dual-read; the ingress changes are reversible
in one command:

```bash
# Roll the ingress body-size back to the prior value (e.g. 50m):
kubectl annotate ingress <ingress-name> \
  nginx.ingress.kubernetes.io/proxy-body-size=50m \
  --overwrite

# Roll the deployment memory back if necessary:
kubectl rollout undo deployment <deployment-name>
```

Backend code rollback (if the GridFS migration itself misbehaves)
is `git revert` of the BUG-ANL-UPLOAD-GRIDFS commits + redeploy.
Existing GridFS-stored rows would NOT be re-read by the reverted
code — they'd appear empty. So roll back ingress FIRST, then
backend code AFTER a clean dry-run shows no new rows landed on
GridFS during the soak.

## Last-touched

2026-06-26 — initial write per BUG-ANL-UPLOAD-GRIDFS Phase 3 close.
