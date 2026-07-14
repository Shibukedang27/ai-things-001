# Hybrid Knowledge Retrieval And Reasoning

Phase 6 retrieval intelligence for ResearchForge OS.

This layer is not a normal RAG module. It retrieves candidate knowledge, expands
the query, ranks by keyword, semantic, and metadata signals, compresses context,
validates source coverage, reasons over evidence, generates citations, and
returns a confidence-scored answer.

## Pipeline

```text
User Query
Intent Detection
Query Expansion
Keyword + Semantic + Metadata Search
Hybrid Ranking
Duplicate Removal
Re-ranking
Context Compression
Knowledge Validation
Reasoning
Citation Generation
Final Response
```

## Modules

- `query_understanding.py` detects intent and expands queries.
- `keyword_search.py` scores lexical matches.
- `semantic_search.py` scores embedding similarity.
- `metadata_search.py` uses topics, keywords, technologies, source metadata, and filters.
- `hybrid.py` merges search modes into a single ranked result set.
- `compression.py` trims context to the most relevant sentences.
- `validation.py` checks missing information and contradiction signals.
- `reasoning.py` synthesizes answers with reasoning steps.
- `citations.py` generates source citations.
- `confidence.py` computes answer confidence.
- `vector_store/` contains in-memory and ChromaDB-compatible vector backends.

The durable backend schema stores retrieval embeddings, queries, retrieval
history, knowledge cache records, reasoning logs, and citation history.
