from retrieval.embedding import RetrievalEmbeddingService
from retrieval.types import KnowledgeSection, QueryProfile, RetrievalCandidate
from retrieval.utils import cosine_similarity


class SemanticSearchEngine:
    def __init__(self, embedding_service: RetrievalEmbeddingService | None = None) -> None:
        self.embedding_service = embedding_service or RetrievalEmbeddingService()

    def search(
        self,
        profile: QueryProfile,
        sections: list[KnowledgeSection],
        vectors: dict[str, list[float]],
        *,
        top_k: int,
    ) -> list[RetrievalCandidate]:
        query_vector = self.embedding_service.embed_text(" ".join(profile.expanded_queries))
        candidates: list[RetrievalCandidate] = []
        for section in sections:
            vector = vectors.get(section.section_id)
            if vector is None:
                vector = self.embedding_service.embed_text(section.content)
            score = cosine_similarity(query_vector, vector)
            if score <= 0:
                continue
            candidates.append(
                RetrievalCandidate(
                    section=section,
                    score=score,
                    keyword_score=0.0,
                    semantic_score=score,
                    metadata_score=0.0,
                    reasons=["Semantic similarity"],
                )
            )
        return sorted(candidates, key=lambda candidate: candidate.score, reverse=True)[:top_k]
