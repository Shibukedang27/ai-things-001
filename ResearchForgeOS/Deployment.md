# Deployment

This document describes the intended deployment strategy for ResearchForge OS. It is a planning document for future implementation.

## Deployment Goals

- Keep AI, retrieval, graph, and application services independently scalable.
- Store user source material securely with strong access boundaries.
- Make ingestion and generation resilient through background jobs.
- Support observability across API requests, worker jobs, retrieval calls, and model calls.
- Maintain a clean path from local development to staging and production.

## Target Environments

| Environment | Purpose |
| --- | --- |
| Local | Developer iteration and infrastructure validation |
| Preview | Pull request deployments and design review |
| Staging | Production-like validation with realistic workloads |
| Production | User-facing application |

## Planned Production Topology

```text
CDN
  Frontend Application

API Gateway
  Backend API
  Auth Middleware
  Rate Limiting

Workers
  Ingestion Workers
  Parsing Workers
  Embedding Workers
  Agent Workers
  Artifact Generation Workers

Data Services
  PostgreSQL
  Redis
  Vector Database
  Graph Database
  Object Storage

Observability
  Logs
  Metrics
  Traces
  Model Evaluation Reports
```

## CI/CD Expectations

- Run linting, type checks, unit tests, and contract tests before merge.
- Build immutable artifacts for frontend, backend, and workers.
- Run database migrations through a controlled deployment step.
- Run smoke tests after deployment.
- Block production deploys on failed security checks.

## Secrets

Secrets must not be committed. Future environments should use a managed secret store for:

- Database credentials
- Object storage credentials
- OAuth credentials
- Model provider API keys
- Signing keys
- Webhook secrets

## Deployment Gates

Before production:

- Authentication and workspace authorization are implemented.
- Upload scanning and file validation are implemented.
- Database migrations are reversible or forward-fixable.
- Observability dashboards exist for ingestion, retrieval, generation, and errors.
- AI output evaluation has baseline quality thresholds.
- Privacy and deletion flows are tested.
