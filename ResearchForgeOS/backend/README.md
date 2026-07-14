# Backend

Production-ready FastAPI foundation for ResearchForge OS.

## Architecture

```text
backend/
  config/          Settings and environment handling
  core/            App factory, database engine, shared core primitives
  routers/         Versioned REST API routes
  models/          SQLAlchemy ORM models
  schemas/         Pydantic request and response contracts
  repositories/    Database access layer
  services/        Domain and orchestration logic
  dependencies/    FastAPI dependency injection providers
  middleware/      Request ID, rate limiting, and security headers
  security/        JWT, password hashing, and permission checks
  exceptions/      Application errors and exception handlers
  logging/         Structured logging configuration
  utils/           Shared utilities
```

## Run Locally

```bash
cp .env.example .env
docker compose up --build
```

API entry point:

```text
backend.main:app
```

Useful endpoints:

- `GET /health/live`
- `GET /health/ready`
- `GET /api/v1/health/live`
- `GET /api/v1/health/ready`
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/documents`
- `GET /api/v1/documents`
- `GET /api/v1/documents/{document_id}`
- `GET /api/v1/documents/{document_id}/summary`
- `GET /api/v1/documents/{document_id}/concepts`
- `GET /api/v1/documents/{document_id}/keywords`
- `GET /api/v1/documents/{document_id}/technologies`
- `GET /api/v1/documents/{document_id}/metadata`
- `DELETE /api/v1/documents/{document_id}`
- `POST /api/v1/knowledge-dna/documents/{document_id}/generate`
- `GET /api/v1/knowledge-dna/documents/{document_id}`
- `PATCH /api/v1/knowledge-dna/{dna_id}`
- `DELETE /api/v1/knowledge-dna/{dna_id}`
- `GET /api/v1/knowledge-dna/documents/{document_id}/learning-path`
- `GET /api/v1/knowledge-dna/documents/{document_id}/related-topics`
- `GET /api/v1/knowledge-dna/documents/{document_id}/prerequisites`
- `POST /api/v1/agents/analyze`
- `GET /api/v1/agents/status`
- `GET /api/v1/agents/history`
- `GET /api/v1/agents/pipelines/{pipeline_id}/status`
- `POST /api/v1/agents/tasks/{task_id}/cancel`
- `POST /api/v1/agents/tasks/{task_id}/retry`
- `POST /api/v1/retrieval/ask`
- `POST /api/v1/retrieval/ask/stream`
- `POST /api/v1/retrieval/search/hybrid`
- `POST /api/v1/retrieval/search/semantic`
- `POST /api/v1/retrieval/search/keyword`
- `POST /api/v1/retrieval/related-concepts`
- `GET /api/v1/retrieval/history`
- `GET /api/v1/retrieval/citations/{history_id}`
- `GET /api/v1/graph`
- `POST /api/v1/graph/documents/{document_id}/generate`
- `GET /api/v1/graph/nodes/search`
- `GET /api/v1/graph/nodes/{node_id}`
- `PATCH /api/v1/graph/nodes/{node_id}`
- `DELETE /api/v1/graph/nodes/{node_id}`
- `GET /api/v1/graph/nodes/{node_id}/expand`
- `POST /api/v1/graph/nodes/{node_id}/collapse`
- `GET /api/v1/graph/export`
- `POST /api/v1/graph/snapshots`
- `GET /api/v1/graph/snapshots`
- `GET /api/v1/workspace`
- `GET /api/v1/workspace/settings`
- `PATCH /api/v1/workspace/settings`
- `POST /api/v1/workspace/notes`
- `GET /api/v1/workspace/notes`
- `POST /api/v1/workspace/notes/search`
- `GET /api/v1/workspace/notes/{note_id}`
- `PATCH /api/v1/workspace/notes/{note_id}`
- `DELETE /api/v1/workspace/notes/{note_id}`
- `POST /api/v1/workspace/notes/{note_id}/improve`
- `POST /api/v1/workspace/writing/assist`
- `POST /api/v1/workspace/bookmarks`
- `GET /api/v1/workspace/bookmarks`
- `POST /api/v1/workspace/collections`
- `GET /api/v1/workspace/collections`
- `POST /api/v1/workspace/projects`
- `GET /api/v1/workspace/projects`
- `POST /api/v1/workspace/tasks`
- `GET /api/v1/workspace/tasks`
- `POST /api/v1/workspace/tasks/assistant`
- `POST /api/v1/workspace/sessions`
- `GET /api/v1/workspace/sessions`
- `POST /api/v1/workspace/canvas/objects`
- `GET /api/v1/workspace/canvas/objects`
- `POST /api/v1/workspace/canvas/objects/{object_id}/connect`
- `GET /api/v1/workspace/timeline`
- `POST /api/v1/learning/documents/{document_id}/generate`
- `GET /api/v1/learning/documents/{document_id}`
- `POST /api/v1/learning/documents/{document_id}/flashcards/generate`
- `GET /api/v1/learning/documents/{document_id}/flashcards`
- `POST /api/v1/learning/documents/{document_id}/quizzes/generate`
- `GET /api/v1/learning/documents/{document_id}/quizzes`
- `POST /api/v1/learning/quizzes/{quiz_id}/start`
- `POST /api/v1/learning/quiz-attempts/{attempt_id}/submit`
- `POST /api/v1/learning/flashcards/review`
- `GET /api/v1/learning/progress`
- `GET /api/v1/learning/achievements`
- `GET /api/v1/learning/certificates`
- `POST /api/v1/learning/documents/{document_id}/revision-plan`
- `GET /api/v1/learning/documents/{document_id}/revision-plans`
- `GET /api/v1/learning/documents/{document_id}/coding-challenges`
- `GET /api/v1/learning/documents/{document_id}/interview-questions`

Swagger is available at `/api/v1/docs` outside production.

## Multi-Agent Research

The backend exposes the Phase 5 agent orchestration layer through
`backend.routers.agents` and `backend.services.agent_service`.

The service coordinates:

- Agent catalog synchronization
- Multi-agent document analysis
- Pipeline history persistence
- Agent task status tracking
- Structured agent responses
- Execution logs
- Cancel and retry workflows

## Hybrid Retrieval And Reasoning

The backend exposes the Phase 6 intelligence layer through
`backend.routers.retrieval`, `backend.services.retrieval_service`, and
`backend.services.retrieval_index_service`.

The service coordinates:

- Query intent detection and query expansion
- Keyword, semantic, metadata, and hybrid search
- Embedding lifecycle management for processed documents
- Context compression and duplicate removal
- Reasoning path generation
- Source validation, confidence scoring, and citation history
- Query and answer caching

## Interactive Knowledge Graph

The backend exposes the Phase 7 graph intelligence layer through
`backend.routers.graph`, `backend.services.graph_service`, and the
top-level `graph_engine` package.

The service coordinates:

- Document, concept, technology, author, paper, organization, dataset, and model nodes
- Knowledge relationships such as prerequisites, dependencies, related topics, implementations, and references
- Duplicate detection, node merge, relationship merge, scoring, clustering, and layout generation
- Incremental graph updates when documents or Knowledge DNA records change
- Search, expand, collapse, export, graph snapshots, analytics, and smart insights
- Cytoscape-compatible payloads for future zoom, pan, drag, minimap, filter, path highlighting, and virtual rendering UI work

## AI Workspace And Second Brain

The backend exposes the Phase 8 thinking environment through
`backend.routers.workspace`, `backend.services.workspace_service`, and
the top-level `workspace_engine` package.

The service coordinates:

- Smart notes, scratchpads, daily notes, pinned notes, collections, bookmarks, projects, tasks, sessions, and canvas objects
- Automatic title, summary, keyword, tag, concept, duplicate, related-note, related-document, and action-item generation
- Writing assistant modes for rewrite, expand, simplify, professional tone, academic tone, ELI5, technical explanation, grammar, citation, and Markdown formatting
- Semantic, keyword, fuzzy, tag, date, project, author, concept, and hybrid note search
- Research, learning, implementation, reading, coding, and revision checklist generation
- Session memory for recent research, frequently used concepts, favorite topics, reading history, search history, bookmarks, and recent AI conversations
- Automatic knowledge graph updates for workspace notes, note concepts, source-document links, related notes, and projects

## Adaptive Learning

The backend exposes the Phase 9 personalized learning layer through
`backend.routers.learning`, `backend.services.learning_service`,
`backend.services.learning_background_service`, and the top-level
`adaptive_learning` package.

The service coordinates:

- Automatic learning asset generation after document upload
- Flashcards, adaptive quizzes, interview questions, coding challenges, revision plans, learning paths, and knowledge tests
- FSRS-inspired spaced repetition with memory strength, confidence, retention score, review count, success rate, next review, forgetting curve, and mastery percentage
- Quiz attempts, grading, progress reports, achievements, streaks, skill levels, and completion certificates
- Background-ready jobs for revision scheduling, reminder scheduling, progress calculation, analytics updates, and mastery updates

## Migrations

Run Alembic from the project root:

```bash
alembic -c database/alembic.ini upgrade head
```
