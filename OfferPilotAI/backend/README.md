# OfferPilot AI Backend

FastAPI backend for OfferPilot AI.

## Structure

```text
backend/
├── app/
│   ├── api/          # Versioned REST routers and dependencies
│   ├── core/         # Configuration, logging, middleware, errors, OpenAPI
│   ├── db/           # SQLAlchemy async engine/session setup
│   ├── domain/       # Domain enums and shared concepts
│   ├── models/       # SQLAlchemy ORM models
│   ├── repositories/ # Persistence adapter contracts
│   ├── schemas/      # Pydantic request/response schemas
│   ├── services/     # Application service layer
│   └── utils/        # Shared helpers
├── config/
├── migrations/
└── scripts/
```

## Local Run

From the repository root:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp backend/.env.example .env
python -m uvicorn app.main:app --app-dir backend --reload
```

## Database

Start Postgres and Redis:

```bash
docker compose up -d postgres redis
```

Apply migrations:

```bash
alembic -c backend/alembic.ini upgrade head
```

Seed development data:

```bash
python backend/scripts/seed_data.py
```

## API

- Swagger UI: `http://localhost:8000/docs`
- OpenAPI JSON: `http://localhost:8000/openapi.json`
- Health: `GET /api/v1/health`
- Liveness: `GET /api/v1/health/live`
- Readiness: `GET /api/v1/health/ready`
- Question catalog: `GET /api/v1/questions/categories`
- Difficulty levels: `GET /api/v1/questions/difficulty-levels`
- Interview templates: `GET /api/v1/interviews/templates`
- Session draft creation: `POST /api/v1/interviews/sessions`

Auth:

- Signup: `POST /api/v1/auth/signup`
- Login: `POST /api/v1/auth/login`
- Logout: `POST /api/v1/auth/logout`
- Refresh: `POST /api/v1/auth/refresh`
- Forgot password: `POST /api/v1/auth/forgot-password`
- Reset password: `POST /api/v1/auth/reset-password`
- Profile: `GET /api/v1/auth/me`
- Sessions: `GET /api/v1/auth/sessions`
- Roles: `GET /api/v1/auth/roles`

Analytics:

- Overview: `GET /api/v1/analytics/overview`

Interview engine:

- Options: `GET /api/v1/interview-engine/options`
- Start session: `POST /api/v1/interview-engine/sessions`
- Session state: `GET /api/v1/interview-engine/sessions/{id}`
- Current question: `GET /api/v1/interview-engine/sessions/{id}/current-question`
- Submit answer: `POST /api/v1/interview-engine/sessions/{id}/answers`
- Complete session: `POST /api/v1/interview-engine/sessions/{id}/complete`

AI evaluation:

- Options: `GET /api/v1/evaluations/options`
- Evaluate answer: `POST /api/v1/evaluations/answers/{id}`
- Get answer evaluation: `GET /api/v1/evaluations/answers/{id}`
- Evaluate interview answers: `POST /api/v1/evaluations/interviews/{id}`
- List interview evaluations: `GET /api/v1/evaluations/interviews/{id}`

Learning recommendations:

- Options: `GET /api/v1/recommendations/options`
- Generate roadmap: `POST /api/v1/recommendations/roadmaps`
- Latest roadmap: `GET /api/v1/recommendations/roadmaps/latest`

Live coding:

- Options: `GET /api/v1/live-coding/options`
- Run code: `POST /api/v1/live-coding/run`
- Analyze code: `POST /api/v1/live-coding/analyze`
- Store submission: `POST /api/v1/live-coding/submissions`
- List submissions: `GET /api/v1/live-coding/submissions`
- Get submission: `GET /api/v1/live-coding/submissions/{id}`

Resume analyzer:

- Options: `GET /api/v1/resume-analyzer/options`
- Upload PDF and analyze: `POST /api/v1/resume-analyzer/analyze`
- Analyze text: `POST /api/v1/resume-analyzer/analyze-text`
- List analyses: `GET /api/v1/resume-analyzer/analyses`
- Get analysis: `GET /api/v1/resume-analyzer/analyses/{id}`

CRUD resources:

- `/api/v1/users`
- `/api/v1/interviews`
- `/api/v1/questions`
- `/api/v1/answers`
- `/api/v1/reports`
- `/api/v1/learning-roadmaps`
- `/api/v1/leaderboard`
- `/api/v1/sessions`
- `/api/v1/interview-history`
