# Development Guide

This guide defines how ResearchForge OS should be built once implementation begins.

## Engineering Principles

- Build domain modules around product concepts, not framework convenience.
- Keep source provenance attached to every generated object.
- Prefer small, testable services over large orchestration functions.
- Make long-running workflows observable.
- Treat prompts, evaluations, and retrieval logic as production code.
- Keep the UI calm, readable, and responsive.

## Branching

Recommended branch names:

```text
feature/product-shell
feature/source-ingestion
feature/knowledge-graph
feature/rag-engine
fix/citation-provenance
docs/api-contract
```

## Commit Style

Use concise commits with a clear scope:

```text
docs: define knowledge graph architecture
frontend: add research dashboard shell
backend: add source metadata model
rag: add chunking contract
ai: add summary evaluation rubric
```

## Code Quality Gates

Future pull requests should pass:

- Formatting
- Linting
- Type checks
- Unit tests
- Integration tests for API contracts
- Retrieval quality tests for RAG changes
- Visual checks for major UI changes
- Accessibility checks for user-facing views

## AI Quality Gates

AI features require:

- A clear prompt contract
- Source attribution requirements
- Failure mode documentation
- Evaluation examples
- Regression checks against hallucinated citations
- Confidence and uncertainty handling

## Frontend Standards

- Light theme only.
- No generic AI dashboards.
- No oversized glassmorphism.
- No decorative gradient backgrounds.
- Use real product structure on the first screen.
- Keep typography readable and restrained.
- Use reusable components with clear ownership.
- Validate responsive layouts before merge.

## Backend Standards

- Use workspace-scoped authorization for every resource.
- Use background jobs for ingestion, parsing, indexing, and generation.
- Keep provider-specific AI logic behind adapters.
- Store request IDs and job IDs for traceability.
- Separate domain logic from transport handlers.

## Documentation Standards

Every significant module should include:

- Purpose
- Ownership boundaries
- Public interfaces
- Failure modes
- Test strategy
- Security considerations

## Definition of Done

A feature is done when it is implemented, documented, tested, accessible, observable, and reviewed against product quality standards.
