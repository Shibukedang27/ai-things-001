# OfferPilot AI API

The OfferPilot AI API is a versioned REST API built with FastAPI. It uses OpenAPI documentation, Pydantic validation, structured response envelopes, JWT authentication, and modular routers.

## API Basics

| Item | Value |
| --- | --- |
| Base URL | `http://localhost:8000` in local development |
| Version prefix | `/api/v1` |
| Swagger UI | `/docs` |
| OpenAPI JSON | `/openapi.json` |
| Data format | JSON |
| Auth scheme | `Authorization: Bearer <access_token>` |
| Standard response | `{ "data": ..., "meta": ..., "errors": [...] }` |

## Standard Response

```json
{
  "data": {},
  "meta": {
    "request_id": "optional-request-id",
    "timestamp": "2026-07-14T00:00:00Z"
  },
  "errors": []
}
```

## Standard Error

```json
{
  "data": null,
  "meta": {
    "request_id": "request-id"
  },
  "errors": [
    {
      "code": "VALIDATION_ERROR",
      "message": "Input should be valid.",
      "field": "email"
    }
  ]
}
```

## Authentication Endpoints

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| POST | `/api/v1/auth/signup` | Public | Create account and issue tokens |
| POST | `/api/v1/auth/login` | Public | Authenticate and issue tokens |
| POST | `/api/v1/auth/refresh` | Public | Rotate refresh token and issue new access token |
| POST | `/api/v1/auth/logout` | Bearer | Revoke current session |
| POST | `/api/v1/auth/forgot-password` | Public | Create reset instructions |
| POST | `/api/v1/auth/reset-password` | Public | Reset password with token |
| GET | `/api/v1/auth/me` | Bearer | Read current profile |
| PATCH | `/api/v1/auth/me` | Bearer | Update current profile |
| GET | `/api/v1/auth/sessions` | Bearer | List current sessions |
| DELETE | `/api/v1/auth/sessions/{session_id}` | Bearer | Revoke a session |
| GET | `/api/v1/auth/roles` | Admin | List roles |
| POST | `/api/v1/auth/roles` | Admin | Create role |
| POST | `/api/v1/auth/users/{user_id}/roles` | Admin | Assign role |
| DELETE | `/api/v1/auth/users/{user_id}/roles/{role_name}` | Admin | Remove role |

## Health Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/health` | Service health |
| GET | `/api/v1/health/live` | Liveness probe |
| GET | `/api/v1/health/ready` | Readiness probe with dependency checks |

## Interview Engine

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/api/v1/interview-engine/options` | Public | Supported roles, durations, difficulties, categories |
| POST | `/api/v1/interview-engine/sessions` | Bearer | Start timed interview |
| GET | `/api/v1/interview-engine/sessions/{interview_id}` | Bearer | Get session state |
| GET | `/api/v1/interview-engine/sessions/{interview_id}/current-question` | Bearer | Get current question |
| POST | `/api/v1/interview-engine/sessions/{interview_id}/answers` | Bearer | Submit answer |
| POST | `/api/v1/interview-engine/sessions/{interview_id}/complete` | Bearer | Complete interview |

Supported categories:

- `python`
- `java`
- `sql`
- `dsa`
- `system_design`
- `machine_learning`
- `deep_learning`
- `nlp`
- `prompt_engineering`
- `behavioral`
- `hr`

## AI Evaluation

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/api/v1/evaluations/options` | Bearer | List score dimensions and generated outputs |
| POST | `/api/v1/evaluations/answers/{answer_id}` | Bearer | Evaluate one answer |
| GET | `/api/v1/evaluations/answers/{answer_id}` | Bearer | Get answer evaluation |
| POST | `/api/v1/evaluations/interviews/{interview_id}` | Bearer | Evaluate full interview |
| GET | `/api/v1/evaluations/interviews/{interview_id}` | Bearer | List interview evaluations |

Evaluation dimensions:

- Technical Accuracy
- Communication
- Completeness
- Confidence Score
- Problem Solving
- Explanation Quality
- Overall Score

## Learning Recommendations

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/api/v1/recommendations/options` | Bearer | List recommendation outputs |
| POST | `/api/v1/recommendations/roadmaps` | Bearer | Generate personalized roadmap |
| GET | `/api/v1/recommendations/roadmaps/latest` | Bearer | Get latest roadmap |

## Analytics

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/api/v1/analytics/overview` | Bearer | Generate full performance analytics overview |

Analytics output includes topic-wise accuracy, weekly progress, monthly progress, heat map, radar chart, weakness trends, strength trends, interview history, and performance graphs.

## Live Coding

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/api/v1/live-coding/options` | Bearer | List languages and analysis outputs |
| POST | `/api/v1/live-coding/run` | Bearer | Run Python, Java, or SQL |
| POST | `/api/v1/live-coding/analyze` | Bearer | Analyze complexity, bugs, and optimizations |
| POST | `/api/v1/live-coding/submissions` | Bearer | Store live coding submission |
| GET | `/api/v1/live-coding/submissions` | Bearer | List submissions |
| GET | `/api/v1/live-coding/submissions/{submission_id}` | Bearer | Get submission |

Supported languages:

- Python
- Java
- SQL

## Resume Analyzer

| Method | Path | Auth | Purpose |
| --- | --- | --- | --- |
| GET | `/api/v1/resume-analyzer/options` | Bearer | List analyzer capabilities |
| POST | `/api/v1/resume-analyzer/analyze` | Bearer | Upload and analyze PDF resume |
| POST | `/api/v1/resume-analyzer/analyze-text` | Bearer | Analyze pasted resume text |
| GET | `/api/v1/resume-analyzer/analyses` | Bearer | List analyses |
| GET | `/api/v1/resume-analyzer/analyses/{analysis_id}` | Bearer | Get analysis |

## Public Catalog Endpoints

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/api/v1/questions/categories` | Supported question categories |
| GET | `/api/v1/questions/difficulty-levels` | Supported difficulty levels |
| GET | `/api/v1/interviews/templates` | Interview template metadata |
| POST | `/api/v1/interviews/sessions` | Create legacy draft interview session |

## Protected CRUD Resources

The following resources support conventional list, create, read, update, and delete patterns and require Bearer authentication:

| Resource | Base Path |
| --- | --- |
| Users | `/api/v1/users` |
| Interviews | `/api/v1/interviews` |
| Questions | `/api/v1/questions` |
| Answers | `/api/v1/answers` |
| Reports | `/api/v1/reports` |
| Learning Roadmaps | `/api/v1/learning-roadmaps` |
| Leaderboard | `/api/v1/leaderboard` |
| Sessions | `/api/v1/sessions` |
| Interview History | `/api/v1/interview-history` |

## Example Login Request

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"candidate@example.com","password":"OfferPilotAI!2026"}'
```

## Example Protected Request

```bash
curl http://localhost:8000/api/v1/analytics/overview \
  -H "Authorization: Bearer <access_token>"
```
