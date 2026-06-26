# EMERGENT_SUPPORT_TICKET_INGRESS — Copy-paste draft for Emergent Support

**Canonical spec:** `/app/memory/JC_WS_CANONICAL_SPEC.md` (Analyze
submodule of JC-WS — load-bearing for the BUG-ANL-UPLOAD-GRIDFS
deployment gate per `sprints/BUG_ANALYZE_UPLOAD.md`).

> **For the user (Akki):** copy the block under `--- TICKET START ---`
> into Emergent Support. Save the support-ticket reply when you get
> one and I'll close the loop on this runbook.

## What this ticket is asking for

Three Kubernetes ingress annotations on the production ingress that
fronts `akki.syni.ai`. Without them, the new GridFS upload backend
that just shipped (Phase 3, 11/11 GREEN, 60× memory improvement) is
blocked at the edge for any upload > 50 MB.

The backend already supports streaming workbook uploads up to
500 MB. The current 50 MB edge cap is the only remaining block.

## --- TICKET START ---

**Subject:** Raise nginx-ingress body-size + timeouts on `akki.syni.ai`
for 500 MB workbook upload support

Hi Emergent Support,

We've shipped a new streaming-GridFS storage path on the backend
that supports workbook uploads up to **500 MB raw bytes** (Analyze
drawer use case — bank-grade quarterly workbooks). The backend has
been proven 11/11 GREEN against this ceiling, with a **+20.85 MB
RSS-peak delta at the 500 MB upload band** (≈ 60× improvement over
the prior inline-base64 path that used to peak at ~1.2 GB).

The remaining block is the K8s ingress that fronts `akki.syni.ai`.
Currently its default body-size + timeouts reject uploads > 50 MB
at the edge before they reach FastAPI.

Could you please apply these three annotations to the Ingress
resource for our deployment? Each is a single `kubectl annotate
ingress … --overwrite` call. They are idempotent and non-disruptive.

```
nginx.ingress.kubernetes.io/proxy-body-size:    "512m"
nginx.ingress.kubernetes.io/proxy-read-timeout: "300"
nginx.ingress.kubernetes.io/proxy-send-timeout: "300"
```

- **proxy-body-size: 512m** — 500 MB ceiling + 12 MB headroom (the
  backend rejects > 500 MB at the FastAPI layer with a clean HTTP
  413 + `workbook_over_500mb_ceiling` detail, so the proxy should
  never reject something the backend would accept).
- **proxy-read-timeout: 300** + **proxy-send-timeout: 300** — 500 MB
  upload completes under 300 s on ≥ 14 Mbps client bandwidth, which
  covers our customer base. The Mongo streaming write itself is on
  the order of 5–10 s; the timeout budget is for the network leg.

After applying, smoke verification on our side will be: sign in as
a real user → upload a 250 MB CSV via the Analyze drawer → expect
200, not 413.

If you'd prefer we land a new pod-memory floor at the same time,
the recommended floor is **≥ 1 GiB** request / **2 GiB** limit on
the backend container — generous headroom for two concurrent
500 MB uploads plus the rest of the request pipeline. The
streaming path peaks at ~50 MB per upload so 1 GiB is overkill in
the steady state, but it gives a clean operating margin.

Thanks!

— Akki

## --- TICKET END ---

## Impact summary — what happens until the ticket lands

| Scenario | Behaviour |
|---|---|
| Customer uploads workbook ≤ 50 MB | ✅ Works normally. The new streaming-GridFS backend accepts the file, stores it via GridFS, returns 200. |
| Customer uploads workbook > 50 MB and ≤ 500 MB | ❌ HTTP 413 at the K8s ingress edge. Backend never sees the request. UI surface should show a clean error; this is what the support ticket unblocks. |
| Customer uploads workbook > 500 MB | ❌ HTTP 413 — but this is correct behaviour. The 500 MB ceiling is the new ship's hard cap. |
| Reads of any existing workbook (any size, any storage backend) | ✅ Works normally. The dual-read helper (`read_workbook_bytes`) handles legacy `data_b64` rows AND new GridFS rows transparently. No regression on the read side. |
| Customer hits an upload error mid-stream (slow connection) | If under 120 s — works. If over 120 s — gateway timeout. The 300 s timeout in the ticket fixes this. |

**No data path regressions** are gated on this ticket. The ticket
only unblocks the > 50 MB write band.

## How we verify the ticket was applied

After Emergent Support replies "done":

1. Open the Analyze drawer in the production app.
2. Upload a 250 MB CSV (we can prepare one if needed).
3. Expect 200 + the analysis row appears.

If step 3 succeeds, the ticket is closed and we can start the 24 h
soak clock for the optional GridFS backfill `--commit` step.

## Why we cannot apply these annotations ourselves

The ingress on `akki.syni.ai` is managed by Emergent's hosting
infrastructure. We have backend-pod kubectl access (for our own
deployment), but the ingress + edge proxy live in Emergent's
cluster control plane — outside our reach.

## Last-touched

2026-06-26 — initial write per AUTONOMOUS BACKLOG RUN user
direction (user said "only memory bump — dont know how to do the K8…",
meaning the kubectl-on-prod path is not available to them).
