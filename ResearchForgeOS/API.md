# API

This document defines the planned API shape for ResearchForge OS. It is a product contract, not an implementation.

## API Principles

- Every AI-generated artifact must expose provenance.
- Long-running work should use jobs and events, not blocking requests.
- Search, graph, notebook, and artifact APIs should share source identifiers.
- User-facing responses should distinguish source facts from model inferences.
- API names should reflect product concepts, not infrastructure details.

## Base Path

```text
/api/v1
```

## Planned Resource Model

| Resource | Purpose |
| --- | --- |
| `workspaces` | Team or personal knowledge spaces |
| `collections` | Organized groups of sources and artifacts |
| `sources` | Uploaded or connected files, pages, repos, videos, notes, and transcripts |
| `chunks` | Normalized retrievable source segments |
| `entities` | People, concepts, papers, systems, topics, libraries, and claims |
| `relationships` | Graph edges between entities and artifacts |
| `artifacts` | Summaries, flashcards, quizzes, timelines, diagrams, notes, and guides |
| `queries` | Search and research requests |
| `jobs` | Long-running ingestion, parsing, indexing, and generation work |
| `citations` | Source references attached to generated outputs |
| `memory` | User learning preferences, progress, and durable context |

## Planned Endpoints

### Workspaces

```http
GET    /api/v1/workspaces
POST   /api/v1/workspaces
GET    /api/v1/workspaces/{workspace_id}
PATCH  /api/v1/workspaces/{workspace_id}
DELETE /api/v1/workspaces/{workspace_id}
```

### Sources

```http
POST   /api/v1/workspaces/{workspace_id}/sources
GET    /api/v1/workspaces/{workspace_id}/sources
GET    /api/v1/sources/{source_id}
PATCH  /api/v1/sources/{source_id}
DELETE /api/v1/sources/{source_id}
POST   /api/v1/sources/{source_id}/reindex
```

### Search

```http
POST /api/v1/search/semantic
POST /api/v1/search/hybrid
POST /api/v1/search/graph
POST /api/v1/search/citations
```

### Knowledge Graph

```http
GET  /api/v1/workspaces/{workspace_id}/graph
GET  /api/v1/entities/{entity_id}
GET  /api/v1/entities/{entity_id}/neighbors
POST /api/v1/relationships
```

### Artifacts

```http
POST /api/v1/artifacts/summaries
POST /api/v1/artifacts/flashcards
POST /api/v1/artifacts/quizzes
POST /api/v1/artifacts/mind-maps
POST /api/v1/artifacts/roadmaps
POST /api/v1/artifacts/timelines
POST /api/v1/artifacts/diagrams
GET  /api/v1/artifacts/{artifact_id}
PATCH /api/v1/artifacts/{artifact_id}
```

### Research Agent

```http
POST /api/v1/agents/analyze
GET  /api/v1/agents/status
GET  /api/v1/agents/history
GET  /api/v1/agents/pipelines/{pipeline_id}/status
POST /api/v1/agents/tasks/{task_id}/cancel
POST /api/v1/agents/tasks/{task_id}/retry
```

### Hybrid Retrieval And Reasoning

```http
POST /api/v1/retrieval/ask
POST /api/v1/retrieval/ask/stream
POST /api/v1/retrieval/search/hybrid
POST /api/v1/retrieval/search/semantic
POST /api/v1/retrieval/search/keyword
POST /api/v1/retrieval/related-concepts
GET  /api/v1/retrieval/history
GET  /api/v1/retrieval/citations/{history_id}
```

### Interactive Knowledge Graph

```http
GET    /api/v1/graph
POST   /api/v1/graph/documents/{document_id}/generate
GET    /api/v1/graph/nodes/search
GET    /api/v1/graph/nodes/{node_id}
PATCH  /api/v1/graph/nodes/{node_id}
DELETE /api/v1/graph/nodes/{node_id}
GET    /api/v1/graph/nodes/{node_id}/expand
POST   /api/v1/graph/nodes/{node_id}/collapse
GET    /api/v1/graph/export?format=json
GET    /api/v1/graph/export?format=svg
GET    /api/v1/graph/export?format=png
POST   /api/v1/graph/snapshots
GET    /api/v1/graph/snapshots
```

### AI Workspace And Second Brain

```http
GET    /api/v1/workspace
GET    /api/v1/workspace/settings
PATCH  /api/v1/workspace/settings
POST   /api/v1/workspace/notes
GET    /api/v1/workspace/notes
POST   /api/v1/workspace/notes/search
GET    /api/v1/workspace/notes/{note_id}
PATCH  /api/v1/workspace/notes/{note_id}
DELETE /api/v1/workspace/notes/{note_id}
POST   /api/v1/workspace/notes/{note_id}/improve
POST   /api/v1/workspace/writing/assist
POST   /api/v1/workspace/bookmarks
GET    /api/v1/workspace/bookmarks
PATCH  /api/v1/workspace/bookmarks/{bookmark_id}
DELETE /api/v1/workspace/bookmarks/{bookmark_id}
POST   /api/v1/workspace/collections
GET    /api/v1/workspace/collections
PATCH  /api/v1/workspace/collections/{collection_id}
DELETE /api/v1/workspace/collections/{collection_id}
POST   /api/v1/workspace/projects
GET    /api/v1/workspace/projects
GET    /api/v1/workspace/projects/{project_id}
PATCH  /api/v1/workspace/projects/{project_id}
DELETE /api/v1/workspace/projects/{project_id}
POST   /api/v1/workspace/tasks
GET    /api/v1/workspace/tasks
PATCH  /api/v1/workspace/tasks/{task_id}
DELETE /api/v1/workspace/tasks/{task_id}
POST   /api/v1/workspace/tasks/assistant
POST   /api/v1/workspace/sessions
GET    /api/v1/workspace/sessions
PATCH  /api/v1/workspace/sessions/{research_session_id}
POST   /api/v1/workspace/canvas/objects
GET    /api/v1/workspace/canvas/objects
PATCH  /api/v1/workspace/canvas/objects/{object_id}
POST   /api/v1/workspace/canvas/objects/{object_id}/connect
DELETE /api/v1/workspace/canvas/objects/{object_id}
GET    /api/v1/workspace/timeline
```

### Adaptive Learning

```http
POST   /api/v1/learning/documents/{document_id}/generate
GET    /api/v1/learning/documents/{document_id}
POST   /api/v1/learning/documents/{document_id}/flashcards/generate
GET    /api/v1/learning/documents/{document_id}/flashcards
POST   /api/v1/learning/documents/{document_id}/quizzes/generate
GET    /api/v1/learning/documents/{document_id}/quizzes
POST   /api/v1/learning/quizzes/{quiz_id}/start
POST   /api/v1/learning/quiz-attempts/{attempt_id}/submit
POST   /api/v1/learning/flashcards/review
GET    /api/v1/learning/progress
GET    /api/v1/learning/achievements
GET    /api/v1/learning/certificates
POST   /api/v1/learning/documents/{document_id}/revision-plan
GET    /api/v1/learning/documents/{document_id}/revision-plans
GET    /api/v1/learning/documents/{document_id}/coding-challenges
GET    /api/v1/learning/documents/{document_id}/interview-questions
```

### Jobs

```http
GET  /api/v1/jobs/{job_id}
POST /api/v1/jobs/{job_id}/cancel
GET  /api/v1/jobs/{job_id}/events
```

## Response Standards

All generated responses should include:

- `id`
- `type`
- `created_at`
- `source_ids`
- `citation_ids`
- `confidence`
- `model`
- `reasoning_summary`
- `review_status`

## Error Model

```json
{
  "error": {
    "code": "source_parse_failed",
    "message": "The source could not be parsed.",
    "request_id": "req_123",
    "details": {
      "source_id": "src_123"
    }
  }
}
```

## Future API Standards

- Publish OpenAPI documentation before implementation.
- Use idempotency keys for upload, ingestion, and generation requests.
- Support streaming events for long-running agent workflows.
- Require workspace-scoped authorization on every resource.
- Track request IDs across frontend, backend, workers, and model calls.
