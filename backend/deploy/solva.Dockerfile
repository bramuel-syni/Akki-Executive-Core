# syntax=docker/dockerfile:1
# Phase 5 — Solva standalone deployment.
# Builds a slim image running ONLY the Solva FastAPI app
# (`solva_app:app`) under uvicorn. Sibling to `synisense.Dockerfile`
# and `akki.Dockerfile`. See those files + `docker-compose.yml` for the
# triad-wide deployment topology.

FROM python:3.11-slim AS runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    AKKI_PROCESS_NAME=solva_app \
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

EXPOSE 8012
HEALTHCHECK --interval=15s --timeout=3s --start-period=20s \
    CMD curl -fsS http://localhost:8012/api/healthz/solva || exit 1

CMD ["uvicorn", "solva_app:app", \
     "--host", "0.0.0.0", \
     "--port", "8012", \
     "--proxy-headers", \
     "--forwarded-allow-ips", "*", \
     "--log-level", "info"]
