FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates default-jdk-headless \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system offerpilotai \
    && adduser --system --ingroup offerpilotai offerpilotai

COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \
    && pip install -r /app/requirements.txt

COPY backend /app/backend
RUN chmod +x /app/backend/scripts/*.sh

WORKDIR /app/backend

EXPOSE 8000

ENTRYPOINT ["/app/backend/scripts/docker-entrypoint.sh"]

FROM base AS development

ENV OFFERPILOT_AI_ENVIRONMENT=local \
    OFFERPILOT_AI_DEBUG=true \
    OFFERPILOT_AI_DOCS_ENABLED=true

USER offerpilotai

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

FROM base AS production

ENV OFFERPILOT_AI_ENVIRONMENT=production \
    OFFERPILOT_AI_DEBUG=false

USER offerpilotai

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
