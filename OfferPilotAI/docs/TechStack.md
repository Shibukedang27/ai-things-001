# OfferPilot AI Tech Stack

This document records the technology choices used by OfferPilot AI and the reason each choice fits the product.

## Frontend

| Technology | Purpose |
| --- | --- |
| React | Component-based frontend application |
| TypeScript | Type-safe UI development |
| Vite | Fast development server and production build |
| Recharts | Dashboard charts and analytics visualization |
| CodeMirror | Integrated live coding editor |
| lucide-react | Icon system |
| CSS | Custom dashboard styling and responsive layout |
| Nginx | Production static serving and API proxy |

## Backend

| Technology | Purpose |
| --- | --- |
| FastAPI | REST API framework and OpenAPI docs |
| Pydantic | Request validation and response schemas |
| Pydantic Settings | Environment-driven configuration |
| SQLAlchemy Async ORM | Database models and async persistence |
| Alembic | Database migrations |
| asyncpg | PostgreSQL async driver |
| PyJWT | JWT access and refresh tokens |
| Argon2 | Password hashing |
| Uvicorn | ASGI server |
| python-multipart | Resume PDF upload support |
| pypdf | PDF text extraction |

## Data and Infrastructure

| Technology | Purpose |
| --- | --- |
| PostgreSQL | Primary relational database |
| JSONB | Flexible structured outputs for recommendations, analysis, metadata |
| Redis | Cache and future job coordination |
| Docker | Containerized development and deployment |
| Docker Compose | Multi-service orchestration |

## Testing and Quality

| Technology | Purpose |
| --- | --- |
| pytest | Backend unit and integration tests |
| pytest-asyncio | Async service and API tests |
| httpx | ASGI API testing client |
| JUnit XML | CI-compatible test reports |
| Markdown and JSON reports | Human-readable test summaries |
| TypeScript compiler | Frontend static verification |
| Vite build | Frontend production build verification |

## Architecture Patterns

| Pattern | Usage |
| --- | --- |
| Service layer | Business workflows and orchestration |
| Repository pattern | Database access boundary |
| Provider interface | AI, recommendation, resume, code analysis boundaries |
| Versioned API | `/api/v1` route prefix |
| Standard API envelope | Consistent success and error responses |
| Environment-based config | Local, test, staging, production readiness |
| Docker profiles | Development and production runtime separation |

## Future Technology Candidates

- Background workers with Celery, Dramatiq, or Arq.
- Managed object storage for resume files and exports.
- External LLM provider integration for production AI generation.
- OpenTelemetry for traces and metrics.
- Dedicated sandbox runtime for live code execution.
- CI/CD through GitHub Actions or another deployment platform.
