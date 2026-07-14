# Database

ResearchForge OS is planned around multiple storage systems because a knowledge operating system needs relational integrity, semantic retrieval, graph traversal, and durable object storage.

## Storage Responsibilities

| Store | Responsibility |
| --- | --- |
| PostgreSQL | Users, workspaces, collections, source metadata, artifacts, jobs, permissions |
| Qdrant | Vector embeddings and semantic retrieval payloads |
| Neo4j | Knowledge graph, entity relationships, citation graph, concept maps |
| Redis | Queues, cache, locks, streaming job state |
| Object Storage | Original files, extracted images, parsed assets, exports |

## Planned Relational Domains

### Identity and Access

- `users`
- `organizations`
- `workspaces`
- `workspace_members`
- `roles`
- `permissions`

### Source Management

- `sources`
- `source_versions`
- `source_files`
- `source_metadata`
- `source_parse_runs`
- `chunks`
- `citations`

### Knowledge and Artifacts

- `artifacts`
- `artifact_versions`
- `artifact_sources`
- `notes`
- `notebooks`
- `flashcards`
- `quizzes`
- `roadmaps`
- `timelines`

### Jobs and Observability

- `jobs`
- `job_events`
- `model_calls`
- `retrieval_runs`
- `evaluation_runs`
- `audit_logs`

## Graph Model

Planned node types:

- `Source`
- `Chunk`
- `Author`
- `Paper`
- `Concept`
- `Claim`
- `Method`
- `Tool`
- `Repository`
- `Function`
- `Framework`
- `Artifact`
- `Question`
- `LearningObjective`

Planned relationship types:

- `CITES`
- `SUPPORTS`
- `CONTRADICTS`
- `EXTENDS`
- `MENTIONS`
- `IMPLEMENTS`
- `DEPENDS_ON`
- `EXPLAINS`
- `DERIVED_FROM`
- `RECOMMENDED_AFTER`
- `TESTS_KNOWLEDGE_OF`

## Vector Payload Standards

Each vector payload should include:

- `workspace_id`
- `source_id`
- `chunk_id`
- `source_type`
- `title`
- `section_path`
- `page_number`
- `created_at`
- `content_hash`
- `citation_key`
- `access_policy`

## Data Integrity Rules

- Never store generated artifacts without source references when the artifact claims to be source-grounded.
- Preserve original uploaded files unless deleted by the user or retention policy.
- Store parser outputs as versioned records.
- Separate user memory from source truth.
- Keep deletion workflows consistent across relational, vector, graph, and object stores.

## Migration Strategy

- Use migrations for relational schema changes.
- Version graph ontology changes.
- Rebuild vector indexes through controlled background jobs.
- Keep backfills idempotent and observable.
- Test deletion and rollback paths before production use.
