# OfferPilot AI Folder Structure

OfferPilot AI is organized as a monorepo with clear product, runtime, data, documentation, and test boundaries.

## Root Layout

```text
OfferPilotAI/
├── assets/
├── backend/
├── config/
├── database/
├── docs/
├── frontend/
├── screenshots/
├── scripts/
├── tests/
├── BrandGuidelines.md
├── docker-compose.yml
├── docker-compose.dev.yml
├── docker-compose.prod.yml
├── requirements.txt
└── README.md
```

## Backend Structure

```text
backend/
├── app/
│   ├── api/              # FastAPI routers, dependencies, CRUD router helpers
│   ├── core/             # Config, logging, middleware, exceptions, OpenAPI metadata
│   ├── db/               # SQLAlchemy base, engine, session factory
│   ├── domain/           # Shared enums and domain constants
│   ├── models/           # SQLAlchemy ORM models
│   ├── repositories/     # Database access layer
│   ├── schemas/          # Pydantic request and response models
│   ├── services/         # Application services and provider abstractions
│   ├── utils/            # Security, IDs, time, validation helpers
│   └── workers/          # Reserved for background worker modules
├── migrations/           # Alembic migration environment and versions
├── scripts/              # Migration, seed, dev, Docker entrypoint scripts
├── Dockerfile
└── alembic.ini
```

## Frontend Structure

```text
frontend/
├── src/
│   ├── app/              # App shell, dashboard data, app types
│   ├── components/       # Reusable dashboard components
│   ├── features/         # Analytics, live coding, resume analyzer workspaces
│   ├── hooks/            # Shared React hooks
│   ├── pages/            # Public landing page and future route-level pages
│   ├── services/         # API client modules
│   └── styles/           # Dashboard CSS
├── public/               # Browser favicon and public static placeholders
├── Dockerfile
├── nginx.conf
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Database Structure

```text
database/
├── backups/              # Placeholder for local backup exports
├── init/                 # Postgres container initialization SQL
├── migrations/           # Reserved database migration notes
├── schemas/              # Schema documentation placeholder
└── seeds/                # Seed documentation placeholder
```

Authoritative migrations live in `backend/migrations`.

## Documentation Structure

```text
docs/
├── README.md
├── API.md
├── Architecture.md
├── CommercialApplications.md
├── Database.md
├── Deployment.md
├── FolderStructure.md
├── FutureScope.md
├── Installation.md
├── Screenshots.md
├── Security.md
└── TechStack.md
```

Brand guidance lives at the project root in `BrandGuidelines.md`, and current logo placeholders live in `assets/brand`.

## Tests Structure

```text
tests/
├── backend/
│   ├── api/
│   ├── auth/
│   ├── database/
│   ├── integration/
│   └── unit/
├── reports/
├── run_reports.py
└── README.md
```

## Ownership Rules

- Backend application logic belongs in `backend/app`.
- Database schema changes belong in Alembic migrations.
- Frontend feature code belongs in `frontend/src/features`.
- Public marketing surfaces belong in `frontend/src/pages`.
- Brand assets belong in `assets/brand` and must align with `BrandGuidelines.md`.
- Runtime environment files belong in `config/env`.
- User-facing documentation belongs in `docs`.
- Generated test reports belong in `tests/reports`.
- Product screenshots belong in `screenshots`.
