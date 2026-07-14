# Retrieval And Reasoning

ResearchForge OS now uses a Hybrid Knowledge Retrieval and Reasoning Engine
instead of a simple chunk-retrieval RAG flow.

Current contents live in `retrieval/` and include:

- Intent detection
- Query expansion
- Keyword, semantic, metadata, and hybrid search
- Re-ranking and duplicate removal
- Context compression
- Knowledge validation
- Reasoning path generation
- Citation generation
- Confidence scoring
- Embedding cache and vector-store abstraction
- ChromaDB-compatible vector adapter

Current status: Phase 6 implemented.
