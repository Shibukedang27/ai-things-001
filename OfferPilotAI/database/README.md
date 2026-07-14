# Database Assets

This folder contains database-adjacent assets for local PostgreSQL development and deployment support.

Authoritative schema documentation is maintained in [docs/Database.md](../docs/Database.md).

## Contents

| Path | Purpose |
| --- | --- |
| `init/` | SQL scripts executed by the local Postgres container at first startup |
| `schemas/` | Reserved for exported schema documentation |
| `seeds/` | Reserved for seed data notes and fixtures |
| `backups/` | Reserved for local backup artifacts |

## Source of Truth

- SQLAlchemy models live in `backend/app/models`.
- Alembic migrations live in `backend/migrations/versions`.
- Development seed data lives in `backend/scripts/seed_data.py`.

Run migrations:

```bash
alembic -c backend/alembic.ini upgrade head
```

Run seed data:

```bash
python backend/scripts/seed_data.py
```
