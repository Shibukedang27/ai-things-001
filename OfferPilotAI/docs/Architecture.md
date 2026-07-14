# OfferPilot AI Architecture

OfferPilot AI follows a modular product architecture with clear separation between frontend experience, backend application services, persistence, runtime infrastructure, and future AI provider integrations.

## Architecture Goals

- Keep product modules independently testable and replaceable.
- Isolate business workflows in services rather than route handlers.
- Use repositories for database access and SQLAlchemy models for persistence.
- Keep AI generation and analysis behind provider interfaces.
- Support local development and production deployment through Docker.
- Preserve a path toward managed Postgres, managed Redis, external AI providers, workers, and observability.

## System Context

```mermaid
flowchart LR
    Candidate["Candidate"] --> Web["React Web App"]
    Admin["Admin or Operator"] --> Web
    Web --> API["FastAPI Backend"]
    API --> Postgres[("PostgreSQL")]
    API --> Redis[("Redis")]
    API --> CodeRunner["Live Code Runner"]
    API --> AIProvider["Future AI Provider"]
    API --> Observability["Logs, Metrics, Traces"]
    API --> Storage["Future Object Storage"]
```

## Container Topology

```mermaid
flowchart TB
    Browser["Browser"] --> Frontend["frontend container: Nginx or Vite"]
    Frontend --> API["api container: FastAPI and Uvicorn"]
    API --> DB[("postgres container")]
    API --> Cache[("redis container")]
    API --> Migrations["Alembic migrations"]
    API --> Seeds["Optional seed data"]
```

## Backend Layering

```mermaid
flowchart TB
    Routers["API Routers"] --> Schemas["Pydantic Schemas"]
    Routers --> Services["Application Services"]
    Services --> Providers["AI and Analysis Providers"]
    Services --> Repositories["Repositories"]
    Repositories --> Models["SQLAlchemy Models"]
    Models --> Database[("PostgreSQL")]
    Core["Core: Config, Logging, Middleware, Errors"] --> Routers
    Core --> Services
```

## Frontend Layering

```mermaid
flowchart TB
    App["App Shell"] --> Components["Reusable Components"]
    App --> Features["Feature Workspaces"]
    Features --> Services["API Services"]
    Features --> Styles["Dashboard Styles"]
    Services --> API["FastAPI API"]
```

## Domain Modules

| Module | Responsibility |
| --- | --- |
| Authentication | Signup, login, logout, refresh tokens, reset password, roles, sessions, user profile |
| Interview Engine | Timed interviews, generated questions, current-question sequence, answer storage |
| AI Evaluation | Per-answer scoring, model answers, suggestions, related topics, difficulty analysis |
| Learning Recommendations | Weak topic detection, resource suggestions, daily, weekly, monthly roadmaps |
| Analytics | Topic accuracy, progress, heat maps, radar charts, trends, interview history |
| Live Coding | Run code, analyze code, complexity estimation, bug detection, optimized code |
| Resume Analyzer | PDF/text analysis, skills, missing skills, ATS score, questions, gap report |
| CRUD Resources | Users, interviews, questions, answers, reports, roadmaps, leaderboard, sessions, history |

## Request Lifecycle

```mermaid
sequenceDiagram
    actor User
    participant UI as React UI
    participant API as FastAPI Router
    participant Auth as Auth Dependency
    participant Service as Application Service
    participant Repo as Repository
    participant DB as PostgreSQL

    User->>UI: Performs action
    UI->>API: HTTP request
    API->>Auth: Validate bearer token when required
    Auth-->>API: Principal or error
    API->>Service: Execute workflow
    Service->>Repo: Read or write data
    Repo->>DB: SQLAlchemy operation
    DB-->>Repo: Result
    Repo-->>Service: Domain data
    Service-->>API: Response model
    API-->>UI: Standard API envelope
```

## Authentication Flow

```mermaid
sequenceDiagram
    actor User
    participant Client
    participant AuthAPI as Auth API
    participant AuthService as Auth Service
    participant DB as PostgreSQL

    User->>Client: Submit credentials
    Client->>AuthAPI: POST /api/v1/auth/login
    AuthAPI->>AuthService: Validate login request
    AuthService->>DB: Load user, credential, roles
    DB-->>AuthService: User data
    AuthService->>AuthService: Verify Argon2 password
    AuthService->>DB: Store session and refresh token fingerprint
    AuthService-->>AuthAPI: Access and refresh token pair
    AuthAPI-->>Client: Auth response
```

## Interview Engine Flow

```mermaid
sequenceDiagram
    actor Candidate
    participant UI
    participant Engine as Interview Engine API
    participant Generator as Question Generator
    participant DB as PostgreSQL

    Candidate->>UI: Choose role, difficulty, duration, categories
    UI->>Engine: Start interview
    Engine->>Generator: Generate questions
    Generator-->>Engine: Question list
    Engine->>DB: Save interview, questions, history
    Engine-->>UI: Session state and first question
    loop One question at a time
        UI->>Engine: Submit answer
        Engine->>DB: Save answer and history
        Engine-->>UI: Next question or completion state
    end
```

## Evaluation and Recommendation Flow

```mermaid
sequenceDiagram
    actor Candidate
    participant UI
    participant EvalAPI as Evaluation API
    participant Evaluator as Evaluation Provider
    participant RecAPI as Recommendation API
    participant Recommender as Recommendation Provider
    participant DB as PostgreSQL

    Candidate->>UI: Request evaluation
    UI->>EvalAPI: Evaluate interview
    EvalAPI->>DB: Load answers and questions
    EvalAPI->>Evaluator: Score each answer
    Evaluator-->>EvalAPI: Scores and feedback
    EvalAPI->>DB: Persist evaluations
    Candidate->>UI: Request roadmap
    UI->>RecAPI: Generate roadmap
    RecAPI->>DB: Load evaluations and history
    RecAPI->>Recommender: Analyze weak topics
    Recommender-->>RecAPI: Plan and resources
    RecAPI->>DB: Persist learning roadmap
```

## Database ER Diagram

```mermaid
erDiagram
    USERS ||--|| AUTH_CREDENTIALS : has
    USERS ||--o{ USER_ROLES : assigned
    ROLES ||--o{ USER_ROLES : grants
    USERS ||--o{ INTERVIEWS : owns
    INTERVIEWS ||--o{ QUESTIONS : contains
    USERS ||--o{ ANSWERS : submits
    INTERVIEWS ||--o{ ANSWERS : collects
    QUESTIONS ||--o{ ANSWERS : receives
    ANSWERS ||--|| ANSWER_EVALUATIONS : evaluated_by
    USERS ||--o{ REPORTS : receives
    INTERVIEWS ||--o{ REPORTS : generates
    REPORTS ||--o{ LEARNING_ROADMAPS : informs
    USERS ||--o{ LEARNING_ROADMAPS : follows
    USERS ||--o{ LEADERBOARD : ranks
    USERS ||--o{ SESSIONS : authenticates
    SESSIONS ||--o{ REFRESH_TOKENS : rotates
    USERS ||--o{ PASSWORD_RESET_TOKENS : requests
    USERS ||--o{ INTERVIEW_HISTORY : records
    INTERVIEWS ||--o{ INTERVIEW_HISTORY : records
    USERS ||--o{ CODE_SUBMISSIONS : submits
    INTERVIEWS ||--o{ CODE_SUBMISSIONS : includes
    USERS ||--o{ RESUME_ANALYSES : uploads
```

## Runtime Configuration

Configuration is environment-driven through `OFFERPILOT_AI_` variables. The application uses typed settings, explicit environment modes, CORS allowlists, trusted-host checks, request IDs, health checks, and structured logging.

## Production Architecture Direction

The Docker Compose stack is production-capable for small deployments and preview environments. Larger deployments should move toward:

- Managed PostgreSQL.
- Managed Redis.
- CDN and TLS termination at the edge.
- Separate worker services for heavy AI, PDF, and code execution tasks.
- Centralized logs, metrics, traces, and alerting.
- Object storage for resume files and generated artifacts.
