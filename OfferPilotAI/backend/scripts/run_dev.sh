#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

python -m uvicorn app.main:app --app-dir backend --host "${OFFERPILOT_AI_HOST:-0.0.0.0}" --port "${OFFERPILOT_AI_PORT:-8000}" --reload
