# syntax=docker/dockerfile:1
# Phase 5 — SyniSense standalone deployment.
#
# Builds a slim image running ONLY the SyniSense FastAPI app
# (`synisense_app:app`) under uvicorn. Designed to be paired with the
# Akki + Solva images via `deploy/docker-compose.yml`, OR deployed as
# its own pod in K8s using the manifests under `deploy/k8s/synisense/`.
#
# Standalone runnability has been verified by Phase 4.3 — see sprint
# memo `/app/memory/sprints/PHASE_4_3_TOPOLOGY.md` §1.
#
# When this image runs alone (or alongside Akki/Solva in compose),
# cross-context contract calls automatically route via the Phase 4.2
# HTTP transport once `BOUNDED_CONTEXT_TRANSPORT=http` plus the
# per-context base URLs (`INTERNAL_TRANSPORT_BASE_URL_AKKI`,
# `INTERNAL_TRANSPORT_BASE_URL_SOLVA`) are set in the environment.

FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    AKKI_PROCESS_NAME=synisense_app \
    BOUNDED_CONTEXT_TRANSPORT=http

WORKDIR /app/backend

# System deps: only what spaCy + Motor + httpx need at runtime.
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
 && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --upgrade pip \
 && pip install -r /app/backend/requirements.txt

# Bring in the full backend tree. Each *_app.py imports only its own
# routers, so the unused product code is dead weight on disk but never
# touched at runtime — acceptable tradeoff for a single shared image.
COPY backend/ /app/backend/

EXPOSE 8011
HEALTHCHECK --interval=15s --timeout=3s --start-period=20s \
    CMD curl -fsS http://localhost:8011/api/healthz/synisense || exit 1

CMD ["uvicorn", "synisense_app:app", \
     "--host", "0.0.0.0", \
     "--port", "8011", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*", \
     "--log-level", "info"]
