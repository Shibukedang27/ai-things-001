# OfferPilot AI Installation

This guide explains how to run OfferPilot AI locally, verify the environment, and use the developer tooling.

## Prerequisites

- Docker Desktop or Docker Engine with Docker Compose.
- Git.
- Python 3.11 or newer, only needed for running backend tests outside Docker.
- Node.js LTS, only needed for running frontend tooling outside Docker.

## Quick Start

From the project root:

```bash
./scripts/start.sh
```

This starts the full development stack:

| Service | URL |
| --- | --- |
| Frontend | `http://localhost:5173` |
| API | `http://localhost:8000` |
| Swagger UI | `http://localhost:8000/docs` |
| Health | `http://localhost:8000/api/v1/health` |
| PostgreSQL | `localhost:5432` |
| Redis | `localhost:6379` |

The development startup runs database migrations and seed data automatically.

## Demo Account

After seed data is loaded:

- Email: `candidate@example.com`
- Password: `OfferPilotAI!2026`

## Docker Commands

| Command | Purpose |
| --- | --- |
| `./scripts/start.sh` | Start development stack with build |
| `./scripts/dev.sh` | Start development stack and pass extra Docker Compose args |
| `./scripts/logs.sh` | Follow development logs |
| `./scripts/stop.sh` | Stop development stack |
| `./scripts/stop.sh -v` | Stop stack and remove volumes |

## Environment Files

| File | Purpose |
| --- | --- |
| `config/env/development.env` | Local development defaults |
| `config/env/test.env` | Isolated Docker verification ports |
| `config/env/production.env.example` | Production template with placeholders |
| `backend/.env.example` | Backend-only local template |

## Local Backend Tooling

Create a Python virtual environment when running tests or scripts outside Docker:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run backend tests and generate reports:

```bash
.venv/bin/python tests/run_reports.py
```

Run the API directly:

```bash
source .venv/bin/activate
export OFFERPILOT_AI_DATABASE_URL="postgresql+asyncpg://offerpilotai:offerpilotai_change_me@localhost:5432/offerpilotai"
python -m uvicorn app.main:app --app-dir backend --reload
```

Apply migrations directly:

```bash
alembic -c backend/alembic.ini upgrade head
```

Seed development data directly:

```bash
python backend/scripts/seed_data.py
```

## Local Frontend Tooling

```bash
cd frontend
npm install
npm run dev
npm run build
```

The Vite dev server proxies `/api` to the backend. In Docker, it proxies to `http://api:8000`; outside Docker, it defaults to `http://localhost:8000`.

## Verification Checklist

Run these checks after setup:

```bash
.venv/bin/python tests/run_reports.py
cd frontend && npm run build
docker compose --env-file config/env/development.env -f docker-compose.yml -f docker-compose.dev.yml config
```

Expected result:

- Backend tests pass.
- Frontend TypeScript and Vite build pass.
- Docker Compose configuration renders without errors.

## Common Issues

| Issue | Resolution |
| --- | --- |
| Docker daemon not running | Start Docker Desktop or the Docker service |
| Port already in use | Use `config/env/test.env` or edit published ports |
| Database healthcheck fails | Restart stack with `./scripts/stop.sh -v` then `./scripts/start.sh` |
| Frontend cannot reach API | Confirm `/api/v1/health/live` works through the frontend port |
| Auth requests fail locally | Confirm seed data ran and the JWT secret is configured |
