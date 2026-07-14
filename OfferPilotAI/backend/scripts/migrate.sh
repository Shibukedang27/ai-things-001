#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/../.."

alembic -c backend/alembic.ini upgrade head
