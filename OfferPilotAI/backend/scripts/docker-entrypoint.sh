#!/usr/bin/env bash
set -euo pipefail

cd /app/backend

if [[ "${OFFERPILOT_AI_WAIT_FOR_DATABASE:-true}" == "true" ]]; then
  python - <<'PY'
import asyncio
import os
import sys
import time

from app.db.session import check_database_connection

timeout_seconds = int(os.getenv("OFFERPILOT_AI_DATABASE_WAIT_TIMEOUT_SECONDS", "60"))
deadline = time.monotonic() + timeout_seconds

async def wait_for_database() -> bool:
    while time.monotonic() < deadline:
        if await check_database_connection():
            return True
        await asyncio.sleep(1)
    return False

if not asyncio.run(wait_for_database()):
    print(f"Database was not reachable within {timeout_seconds}s.", file=sys.stderr)
    raise SystemExit(1)
PY
fi

if [[ "${OFFERPILOT_AI_RUN_MIGRATIONS:-false}" == "true" ]]; then
  alembic -c alembic.ini upgrade head
fi

if [[ "${OFFERPILOT_AI_RUN_SEED:-false}" == "true" ]]; then
  python scripts/seed_data.py
fi

exec "$@"
