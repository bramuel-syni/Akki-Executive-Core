# Deployment — Sell-Ready Topology

This directory contains the artefacts that make Akki / SyniSense / Solva deployable as **three independent processes** (Docker Compose locally, K8s in production). The intent is to prove the multi-process topology is buildable + bootable today, gated only on the platform supervisor unlock noted in `/app/memory/sprints/PHASE_4_3_TOPOLOGY.md` §1.

## What's here

```
deploy/
├── synisense.Dockerfile      ← uvicorn synisense_app:app on :8011
├── solva.Dockerfile          ← uvicorn solva_app:app    on :8012
├── akki.Dockerfile           ← uvicorn akki_app:app     on :8001
├── docker-compose.yml        ← triad + MongoDB; healthchecks green at boot
└── k8s/
    ├── synisense/{deployment,service}.yaml
    ├── solva/{deployment,service}.yaml
    └── akki/{deployment,service}.yaml
```

Each app file (`<ctx>_app.py`) is independently runnable as verified in Phase 4.3 Part A. The Dockerfiles wrap that runnability into a slim image.

## Running locally (docker compose)

```bash
cd /app/backend/deploy

# Required env vars
export INTERNAL_TRANSPORT_SECRET="$(openssl rand -hex 32)"
export EMERGENT_LLM_KEY="..."   # see /app/memory/INTEGRATIONS.md

docker compose up --build
```

What happens:
1. `mongo` starts and reports healthy.
2. `synisense` + `solva` build (sharing the same base image layers) and start.
3. Each runs its `/api/healthz/<context>` probe and reports healthy once db connectivity is verified.
4. `akki` waits on both sibling services to be healthy, then boots and exposes `:8001` to the host.
5. Compose stays running with all four services green. Hit `http://localhost:8001/api/healthz/composite` to verify.

Tear down with `docker compose down -v` (the `-v` drops the Mongo volume).

## Running on Kubernetes

The manifest skeletons are intentionally minimal — they document the surface, not the production posture. Tune before applying:

| Knob | Default | Recommendation |
|---|---|---|
| `replicas` | 1 (akki=2) | Right-size per traffic. Akki ≥ 2 always (rolling-update safety). |
| `resources.requests` | `250m / 512Mi` (synisense), `500m / 1Gi` (solva, akki) | Profile under real Shield-invocation traffic before committing. |
| `image` | `registry.example.com/akki/<ctx>:latest` | Replace with your registry / tag. |
| `secretKeyRef` names | `akki-mongo`, `akki-llm`, `akki-internal-transport` | Wire to your secret backend. |
| `HPA target CPU %` | 70% (60% for akki) | Tune once you have real telemetry. |

Apply order:
```bash
kubectl apply -f k8s/synisense/
kubectl apply -f k8s/solva/
kubectl apply -f k8s/akki/
```

The `akki` deployment depends on the `synisense` and `solva` Services being resolvable via DNS — Kubernetes does this automatically once the Services exist.

## Environment variables — quick reference

Every service needs the same six env vars:

| Var | Purpose |
|---|---|
| `MONGO_URL` | Motor connection URL |
| `DB_NAME` | Mongo db name (default `akki`) |
| `AKKI_PROCESS_NAME` | Identifies the process to healthchecks (`akki_app` / `synisense_app` / `solva_app`) |
| `BOUNDED_CONTEXT_TRANSPORT` | `http` for cross-context HTTP calls (Phase 4.3 default) |
| `INTERNAL_TRANSPORT_BASE_URL_{AKKI,SYNISENSE,SOLVA}` | Per-context base URLs for cross-context calls |
| `INTERNAL_TRANSPORT_SECRET` | HMAC secret for the internal transport (must match across pods) |
| `EMERGENT_LLM_KEY` | LLM provider key for Shield-wrapped calls |

## What's verified

| Check | Status |
|---|---|
| `<ctx>_app:app` imports cleanly in isolation | ✅ Phase 4.3 |
| `/api/healthz/<ctx>` returns 200 from a standalone process | ✅ Phase 4.3 |
| HTTP transport round-trips DTOs correctly under load | ✅ Phase 4.2 + Phase 4.3 (PEP-563 fix) |
| Per-context OpenAPI slice → consumer SDK | ✅ Phase 5 Part B |
| Dockerfiles build and boot in compose | ⏳ Build artefact ready; bake on the deploy lane |
| K8s manifests apply cleanly with healthchecks green | ⏳ Manifest skeletons ready; bake on the deploy lane |
| Live multi-process deployment in the bundled platform | ❌ External blocker: supervisor.conf is `READONLY` in the platform |

The two `⏳` items require running docker/kubectl on a lane outside this environment. The `❌` item is the standing external blocker.
