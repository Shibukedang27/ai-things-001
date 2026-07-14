# Knowledge Engine

Core AI Knowledge Engine for ResearchForge OS.

This package turns uploaded knowledge sources into structured knowledge objects. It is deterministic, modular, and source-grounded, so it can run without external model calls while still providing the production architecture needed for future AI providers.

## Modules

- `document_parser/` - file type detection and text extraction for PDFs, DOCX, TXT, Markdown, PowerPoint, websites, GitHub repositories, transcripts, and notes
- `preprocessing/` - content cleaning and normalization
- `chunk_manager/` - stable chunk generation
- `metadata_generator/` - title, category, topics, difficulty, reading time, and content hash generation
- `keyword_extractor/` - keyword and keyphrase extraction
- `technology_extractor/` - technology detection
- `concept_extractor/` - concepts, prerequisites, dependencies, difficulty, and confidence
- `summary_generator/` - executive, beginner, technical, detailed, one-minute, and five-minute summaries
- `code_block_extractor/` - fenced and indented code extraction
- `reference_extractor/` - URL, DOI, and bibliography extraction
- `embedding_service/` - deterministic local embedding metadata generation
- `learning_asset_generator/` - objectives, flashcards, quiz prompts, interview questions, and revision plans
- `relationships/` - concept and technology relationship extraction
- `dna/` - Knowledge DNA profiling, domain classification, graph construction, relationship discovery, and learning path generation

## Entry Point

```python
from knowledge_engine import KnowledgeEnginePipeline
from knowledge_engine import KnowledgeDNAEngine
```

The backend document service persists the resulting knowledge object into normalized database tables.

The Knowledge DNA engine reads processed documents and generates document identity, difficulty, knowledge score, interview importance, industry relevance, implementation complexity, research category, concepts, prerequisites, successor topics, related documents, graph nodes, graph edges, hierarchy, and future learning paths.
