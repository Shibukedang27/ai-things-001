# AI Workspace And Second Brain Engine

`workspace_engine` contains the backend-only intelligence layer for the ResearchForge OS thinking environment. It is not a note-taking UI package. It analyzes workspace material, improves writing, searches notes, generates research plans, and produces structured signals that the backend can persist and link into the knowledge graph.

## Responsibilities

- Generate smart note metadata: titles, summaries, keywords, tags, categories, concepts, action items, duplicate signatures, and confidence scores.
- Detect related notes and duplicate candidates from existing workspace memory.
- Provide writing modes for rewrite, expand, simplify, professional tone, academic tone, ELI5, technical explanation, grammar improvement, citation generation, and Markdown formatting.
- Search notes using semantic, keyword, fuzzy, tag, date, project, author, concept, and hybrid scoring.
- Generate research, learning, implementation, reading, coding, and revision checklists.

## Main Modules

- `note_intelligence.py` analyzes notes and detects duplicates or related notes.
- `writing_assistant.py` performs deterministic writing transformations and citation formatting.
- `search.py` ranks workspace notes across multiple search modes.
- `task_assistant.py` creates structured plans and checklists.
- `types.py` defines shared enums and dataclasses.
- `utils.py` contains text normalization, tokenization, summarization, action extraction, and similarity helpers.

## Persistence Boundary

The engine is database-independent. Persistence and API orchestration live in:

- `backend.models.workspace`
- `backend.repositories.workspace_repository`
- `backend.services.workspace_service`
- `backend.routers.workspace`

Workspace notes and projects are linked into the interactive knowledge graph by `WorkspaceService`, while the graph engine remains responsible for global layout, analytics, and graph reads.
