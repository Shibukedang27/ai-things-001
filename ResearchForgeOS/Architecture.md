# Architecture

ResearchForge OS is planned as a modular AI knowledge platform. The architecture separates ingestion, storage, retrieval, reasoning, synthesis, and presentation so each part can evolve without turning the product into a fragile chatbot wrapper.

## Architectural Goals

- Preserve source traceability for every generated artifact.
- Support heterogeneous inputs without coupling parsers to UI flows.
- Build durable knowledge structures beyond transient chat history.
- Keep AI outputs reviewable, explainable, and auditable.
- Allow local development while keeping a clean path to production deployment.

## System Layers

```text
Client Experience
  Landing Page
  Research Dashboard
  Knowledge Graph
  Document Viewer
  AI Workspace
  Mind Map
  Timeline
  Notebook
  Flashcards
  Quiz
  Analytics

API and Orchestration
  Authentication
  Workspace API
  Source API
  Artifact API
  Search API
  Graph API
  Agent API
  Analytics API

Knowledge Intelligence
  Document Parser
  Embedding Engine
  RAG Engine
  Knowledge Graph Engine
  Citation Engine
  Reasoning Engine
  Memory Engine
  Recommendation Engine

Data Platform
  PostgreSQL for application records
  Qdrant for vector retrieval
  Neo4j for graph relationships
  Redis for queues, caching, and coordination
  Object storage for original files and extracted assets
```

## Core Modules

### Knowledge Engine

The Knowledge Engine is the center of the platform. It transforms parsed sources into concepts, claims, relationships, artifacts, and learning objects. It should own ontology design, entity resolution, graph enrichment, source attribution, and artifact dependency tracking.

### Document Parser

The parser layer normalizes raw files and external sources into canonical chunks, metadata, extracted media, tables, references, and citations. It should never make product-level reasoning decisions.

### RAG Engine

The RAG Engine retrieves source-grounded context, ranks evidence, builds answer packs, and returns citation-ready material to agents and product flows.

### Research Agent

The Research Agent coordinates multi-step research workflows such as comparing papers, extracting implementation plans, generating learning paths, and finding contradictions between sources.

### Memory Engine

The Memory Engine tracks user interests, repeated concepts, saved artifacts, revision history, and learning progress. It should improve personalization without silently contaminating source-grounded answers.

### Reasoning Engine

The Reasoning Engine performs structured transformations: argument maps, causal chains, tradeoff matrices, architecture diagrams, implementation guides, and critique passes.

### Artifact Generators

Artifact generators produce flashcards, quizzes, diagrams, timelines, roadmaps, summaries, notebooks, and interview questions. They depend on source-grounded context and store artifact provenance.

## Data Flow

1. User uploads or connects a source.
2. The ingestion service stores the original source in object storage.
3. The parser extracts text, structure, metadata, references, images, tables, and sections.
4. The embedding engine chunks and embeds normalized content.
5. The knowledge engine extracts entities, claims, topics, and relationships.
6. The graph engine writes relationships to the graph store.
7. The RAG engine indexes chunks for semantic retrieval.
8. Product modules generate artifacts with citations and provenance.
9. Users save, edit, connect, review, quiz, and revisit artifacts.

## Folder Responsibilities

| Folder | Responsibility |
| --- | --- |
| `frontend/` | Future product interface, routes, components, interactions, and design-system implementation |
| `backend/` | Future API, domain services, auth, queues, and orchestration |
| `database/` | Future migrations, seeds, schemas, graph models, and storage policies |
| `ai/` | Future prompts, agent policy, model adapters, evaluations, and safety checks |
| `rag/` | Future chunking, embeddings, retrieval, reranking, answer assembly, and citation packing |
| `knowledge_engine/` | Future ontology, graph construction, entity resolution, and artifact synthesis |
| `analytics/` | Future product analytics, learning analytics, and quality measurement |
| `assets/` | Brand assets, design tokens, visual language, and exportable media |
| `docs/` | Extended documentation beyond the root project guides |
| `scripts/` | Future developer, migration, ingestion, and deployment scripts |
| `tests/` | Future unit, integration, evaluation, contract, and visual tests |
| `public/` | Future public static assets |
| `screenshots/` | Future screenshots for README, case studies, and launch materials |

## Phase 0 Non-Goals

- No frontend application code.
- No backend application code.
- No AI workflow implementation.
- No database migrations.
- No production deployment.

Phase 0 exists to make the project feel inevitable before code starts.
