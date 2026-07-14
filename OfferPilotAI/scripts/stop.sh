#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

ENV_FILE="${OFFERPILOT_AI_ENV_FILE:-config/env/development.env}"
export OFFERPILOT_AI_ENV_FILE="$ENV_FILE"

docker compose \
  --env-file "$ENV_FILE" \
  -f docker-compose.yml \
  -f docker-compose.dev.yml \
  down "$@"
