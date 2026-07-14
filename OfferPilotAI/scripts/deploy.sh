#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

ENV_FILE="${1:-config/env/production.env}"

if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing production env file: $ENV_FILE" >&2
  echo "Create it from config/env/production.env.example and replace every placeholder secret." >&2
  exit 1
fi

if grep -Eq "replace-with|example.com|change_me" "$ENV_FILE"; then
  echo "Production env file still contains placeholder values: $ENV_FILE" >&2
  exit 1
fi

export OFFERPILOT_AI_ENV_FILE="$ENV_FILE"

docker compose --env-file "$ENV_FILE" -f docker-compose.yml -f docker-compose.prod.yml build
docker compose --env-file "$ENV_FILE" -f docker-compose.yml -f docker-compose.prod.yml run --rm --entrypoint alembic api -c alembic.ini upgrade head
docker compose --env-file "$ENV_FILE" -f docker-compose.yml -f docker-compose.prod.yml up -d
