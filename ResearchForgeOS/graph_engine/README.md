# Interactive Knowledge Graph Engine

`graph_engine` converts processed ResearchForge OS knowledge into a scored, deduplicated, layout-ready graph. It is backend-only and produces payloads that a future frontend can render with a production graph visualization library such as Cytoscape.js.

## Responsibilities

- Generate graph nodes for documents, concepts, technologies, languages, frameworks, libraries, algorithms, research papers, authors, companies, universities, datasets, APIs, tools, models, courses, projects, and interview topics.
- Generate graph relationships for prerequisites, dependencies, parent and child topics, related topics, references, implementations, technology usage, authorship, support, extension, alternatives, and research evolution.
- Score nodes and edges using confidence, importance, evidence density, relationship type, and knowledge role.
- Detect duplicates, merge nodes, merge relationships, and retain source document provenance.
- Generate scalable layouts with NetworkX spring layout for normal graphs and deterministic radial layout for large graphs.
- Produce graph analytics, knowledge insights, export payloads, and interaction capabilities for zoom, pan, drag, search, filtering, grouping, path highlighting, minimap, legend, lazy loading, and virtual rendering.

## Main Modules

- `engine.py` orchestrates node generation, relationship generation, scoring, merging, layout, analytics, and interaction payloads.
- `node_generator.py` transforms document and Knowledge DNA data into typed node drafts.
- `relationship_generator.py` transforms concepts, metadata, references, and DNA signals into typed edge drafts.
- `merge.py` handles duplicate detection plus node and relationship consolidation.
- `scoring.py` calculates node importance and edge weight.
- `layout.py` creates visual positions and frontend interaction metadata.
- `analytics.py` calculates graph metrics, clusters, weak areas, missing prerequisites, research trends, and learning insights.
- `exporter.py` serializes graph payloads to JSON, SVG, and PNG.
- `cache.py` provides TTL caching for graph reads.
- `types.py` contains typed dataclasses and enums shared across the engine.

## Persistence Boundary

The engine itself is pure Python and database-independent. Persistence is handled by:

- `backend.models.interactive_graph`
- `backend.repositories.graph_repository`
- `backend.services.graph_service`
- `backend.routers.graph`

This keeps graph intelligence reusable while allowing FastAPI, SQLAlchemy, Alembic, authentication, and permissions to remain in the backend layer.
