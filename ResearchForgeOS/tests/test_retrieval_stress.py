from retrieval import HybridKnowledgeRetrievalEngine
from retrieval.embedding import RetrievalEmbeddingService
from retrieval.types import KnowledgeSection, SearchOptions


def test_reasoning_engine_handles_repeated_queries() -> None:
    engine = HybridKnowledgeRetrievalEngine()
    embedding_service = RetrievalEmbeddingService()
    sections = [
        KnowledgeSection(
            section_id=f"doc-{index}:chunk-1",
            document_id=f"doc-{index}",
            document_title=f"Knowledge Source {index}",
            content=(
                "ResearchForge retrieval reasons over source documents, compares algorithms, validates evidence, "
                f"and explains implementation strategy for source {index}."
            ),
            section_label="chunk-1",
            chunk_id=f"chunk-{index}",
            topics=["Knowledge Retrieval", "Implementation Strategy"],
            keywords=["algorithms", "evidence", "implementation"],
            technologies=["FastAPI", "SQLAlchemy"],
        )
        for index in range(80)
    ]
    vectors = {section.section_id: embedding_service.embed_text(section.content) for section in sections}

    for index in range(40):
        profile = engine.understand(f"Explain implementation strategy and evidence validation number {index}")
        answer = engine.answer(profile, sections, vectors, options=SearchOptions(top_k=6))
        assert answer.answer
        assert answer.citations
        assert answer.confidence_score > 0
