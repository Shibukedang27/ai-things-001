import time

from retrieval import HybridKnowledgeRetrievalEngine
from retrieval.embedding import RetrievalEmbeddingService
from retrieval.types import KnowledgeSection, SearchMode, SearchOptions


def test_hybrid_search_performance_on_medium_corpus() -> None:
    engine = HybridKnowledgeRetrievalEngine()
    embedding_service = RetrievalEmbeddingService()
    sections = [
        KnowledgeSection(
            section_id=f"doc-{index}:chunk-1",
            document_id=f"doc-{index}",
            document_title=f"Research Note {index}",
            content=(
                "Hybrid retrieval combines keyword search semantic search citations reasoning validation "
                f"and context compression for topic{index}."
            ),
            section_label="chunk-1",
            chunk_id=f"chunk-{index}",
            topics=["Hybrid Retrieval", "Reasoning"],
            keywords=["retrieval", "reasoning", "citations"],
            technologies=["PostgreSQL", "ChromaDB"],
        )
        for index in range(250)
    ]
    vectors = {section.section_id: embedding_service.embed_text(section.content) for section in sections}
    profile = engine.understand("How does hybrid retrieval validate citations and reasoning?")

    started_at = time.perf_counter()
    results = engine.search(
        profile,
        sections,
        vectors,
        mode=SearchMode.HYBRID,
        options=SearchOptions(top_k=10),
    )
    duration = time.perf_counter() - started_at

    assert len(results) == 10
    assert duration < 3.0
