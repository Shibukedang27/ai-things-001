# OfferPilot AI

OfferPilot AI is a production-oriented AI interview preparation platform for technical interviews, live coding, resume analysis, answer evaluation, analytics, and personalized learning plans.

The product is organized as a startup-ready monorepo with a FastAPI backend, React frontend, PostgreSQL persistence layer, Alembic migrations, Dockerized runtime, test reports, and professional documentation.

## Product Capabilities

- User authentication with signup, login, logout, refresh tokens, forgot password, reset password, roles, profiles, and session management.
- Interview Engine for role, difficulty, duration, and category-based interview sessions.
- AI Evaluation Engine for technical accuracy, communication, completeness, confidence, problem solving, explanation quality, and overall score.
- Learning Recommendation Engine with weak-topic analysis, LeetCode, HackerRank, books, courses, YouTube videos, daily plans, weekly plans, and monthly roadmaps.
- Modern dashboard with performance metrics, charts, weak topics, strong topics, recent interviews, streaks, learning progress, and leaderboard.
- Live Coding Module with Python, Java, SQL, code execution, static analysis, complexity analysis, bug detection, optimized code, and improvement explanations.
- Resume Analyzer with PDF upload, skills extraction, job description comparison, ATS score, suggestions, interview questions, and skill gap report.
- Analytics for topic accuracy, weekly progress, monthly progress, heat maps, radar charts, weakness trends, strength trends, and interview history.

## One-Command Startup

```bash
./scripts/start.sh
```

The development stack starts:

- Frontend: `http://localhost:5173`
- API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

The development Docker profile runs database migrations and seed data automatically.

## Demo Login

After the development seed script runs:

- Email: `candidate@example.com`
- Password: `OfferPilotAI!2026`

## Documentation

- [Documentation Index](docs/README.md)
- [Architecture](docs/Architecture.md)
- [API](docs/API.md)
- [Database](docs/Database.md)
- [Installation](docs/Installation.md)
- [Deployment](docs/Deployment.md)
- [Brand Guidelines](BrandGuidelines.md)
- [Security](docs/Security.md)
- [Folder Structure](docs/FolderStructure.md)
- [Tech Stack](docs/TechStack.md)
- [Future Scope](docs/FutureScope.md)
- [Commercial Applications](docs/CommercialApplications.md)
- [Screenshots Placeholder](docs/Screenshots.md)

## Repository Layout

```text
OfferPilotAI/
├── assets/                 # OfferPilot AI logo, brand, image, icon, and mockup placeholders
├── backend/                # FastAPI backend, services, repositories, models, migrations
├── config/                 # Environment files for Dockerized runtime
├── database/               # Database init scripts, schemas, seed notes, backups
├── docs/                   # Product, engineering, security, deployment documentation
├── frontend/               # React, Vite, TypeScript frontend application
├── screenshots/            # Product, architecture, QA, and release screenshot placeholders
├── scripts/                # Docker startup, deployment, logs, stop scripts
├── tests/                  # Unit, integration, API, database, auth tests and reports
├── BrandGuidelines.md      # Brand system, palette, UI style, and theme guidance
├── docker-compose.yml      # Shared Docker Compose services
├── docker-compose.dev.yml  # Development overrides
├── docker-compose.prod.yml # Production overrides
├── requirements.txt        # Python backend dependencies
└── README.md
```

## Technology Snapshot

- Frontend: React, TypeScript, Vite, Recharts, CodeMirror, lucide-react.
- Backend: FastAPI, Pydantic, SQLAlchemy, Alembic, JWT, Argon2.
- Database: PostgreSQL with JSONB support.
- Cache and future job coordination: Redis.
- Runtime: Docker Compose, Nginx, Uvicorn.
- Tests: pytest, pytest-asyncio, httpx, JUnit XML, Markdown and JSON reports.

## Branding and UI

The frontend now starts with a secure OfferPilot AI login/signup flow, includes a premium public SaaS landing page, and opens the responsive product dashboard after authentication. Brand placeholders are stored in `assets/brand/` and `frontend/public/favicon.svg`.

The complete brand system is documented in [BrandGuidelines.md](BrandGuidelines.md).

## Quality Status

Current verification suite:

```bash
.venv/bin/python tests/run_reports.py
(cd frontend && npm run build)
docker compose --env-file config/env/development.env -f docker-compose.yml -f docker-compose.dev.yml config
docker compose --env-file config/env/production.env.example -f docker-compose.yml -f docker-compose.prod.yml build api frontend
```

Latest backend report: `69 passed`, `0 failed`, `0 errors`.

## Deployment Summary

Development:

```bash
./scripts/start.sh
```

Production template:

```bash
cp config/env/production.env.example config/env/production.env
./scripts/deploy.sh config/env/production.env
```

Production deployments must replace placeholder secrets, configure real domains, enable TLS at the edge, and use managed data services or hardened container volumes.

## License

This project is licensed under the terms in [LICENSE](LICENSE).
