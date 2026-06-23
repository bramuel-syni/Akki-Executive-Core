# syntax=docker/dockerfile:1
# Phase 5 — Akki standalone deployment.
# Builds the public-facing Akki FastAPI app (`akki_app:app`) under
# uvicorn on port 8001. Sibling to `synisense.Dockerfile` and
# `solva.Dockerfile`. Akki is the orchestrator + user-facing surface;
# it composes the cross-context typed contracts to call SyniSense and
# Solva over the Phase 4.2 HTTP transport.

FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    AKKI_PROCESS_NAME=akki_app \
    BOUNDED_CONTEXT_TRANSPORT=http

WORKDIR /app/backend

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
        build-essential \
        ca-certificates \
        curl \
 && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt /app/backend/requirements.txt
RUN pip install --upgrade pip \
 && pip install -r /app/backend/requirements.txt

COPY backend/ /app/backend/

EXPOSE 8001
HEALTHCHECK --interval=15s --timeout=3s --start-period=20s \
    CMD curl -fsS http://localhost:8001/api/healthz/composite || exit 1

CMD ["uvicorn", "akki_app:app", \
     "--host", "0.0.0.0", \
     "--port", "8001", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*", \
     "--log-level", "info"]
