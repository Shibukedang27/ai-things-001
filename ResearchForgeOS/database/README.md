# Database

Database assets for ResearchForge OS.

Current contents:

- Alembic configuration
- Identity and access-control migration
- Knowledge Engine document schema migration
- Knowledge DNA graph, hierarchy, learning path, prerequisite, and related-document schema migration
- Multi-agent research schema migration for agents, tasks, responses, execution logs, and pipeline history
- Hybrid retrieval schema migration for retrieval embeddings, queries, history, cache records, reasoning logs, and citations
- Interactive knowledge graph schema migration for graph nodes, graph edges, node metadata, relationship metadata, layouts, and snapshots
- AI workspace schema migration for notes, collections, bookmarks, projects, tasks, research sessions, canvas objects, and workspace settings
- Adaptive learning schema migration for flashcards, quizzes, quiz attempts, reviews, learning sessions, achievements, certificates, memory tracking, progress, coding challenges, and revision plans

Run migrations from the project root:

```bash
alembic -c database/alembic.ini upgrade head
```

Future contents:

- Seed data
- Schema diagrams
- Data retention policies
