from retrieval import HybridKnowledgeRetrievalEngine
from retrieval.embedding import RetrievalEmbeddingService
from retrieval.types import KnowledgeSection, QueryIntent, SearchMode, SearchOptions


def test_hybrid_retrieval_engine_reasons_across_sources() -> None:
    engine = HybridKnowledgeRetrievalEngine()
    embedding_service = RetrievalEmbeddingService()
    sections = [
        KnowledgeSection(
            section_id="doc-1:chunk-1",
            document_id="doc-1",
            document_title="Attention Is All You Need",
            content="Transformer attention compares token relationships and improves sequence modeling.",
            section_label="chunk-1",
            chunk_id="chunk-1",
            topics=["Attention", "Transformers"],
            keywords=["attention", "sequence modeling"],
            technologies=["PyTorch"],
        ),
        KnowledgeSection(
            section_id="doc-2:chunk-1",
            document_id="doc-2",
            document_title="Retrieval Augmented Generation",
            content="Retrieval augmented generation uses vector search to add source evidence before generation.",
            section_label="chunk-1",
            chunk_id="chunk-2",
            topics=["RAG", "Vector Search"],
            keywords=["retrieval", "generation", "evidence"],
            technologies=["ChromaDB"],
        ),
    ]
    vectors = {section.section_id: embedding_service.embed_text(section.content) for section in sections}

    profile = engine.understand("Compare transformer attention and retrieval augmented generation trade-offs")
    results = engine.search(
        profile,
        sections,
        vectors,
        mode=SearchMode.HYBRID,
        options=SearchOptions(top_k=2),
    )
    answer = engine.answer(profile, sections, vectors, options=SearchOptions(top_k=2))

    assert profile.intent == QueryIntent.COMPARISON
    assert len(results) == 2
    assert answer.confidence_score > 0
    assert answer.citations
    assert answer.reasoning_path
    assert "Comparison:" in answer.answer
