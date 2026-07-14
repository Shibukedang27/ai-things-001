from retrieval.compression import ContextCompressionService
from retrieval.hybrid import HybridRankingEngine
from retrieval.query_understanding import QueryUnderstandingService
from retrieval.reasoning import ReasoningEngine
from retrieval.types import (
    KnowledgeSection,
    QueryProfile,
    ReasonedAnswer,
    RetrievalCandidate,
    SearchMode,
    SearchOptions,
)
from retrieval.utils import stable_hash


class HybridKnowledgeRetrievalEngine:
    def __init__(
        self,
        query_understanding: QueryUnderstandingService | None = None,
        ranking_engine: HybridRankingEngine | None = None,
        compressor: ContextCompressionService | None = None,
        reasoning_engine: ReasoningEngine | None = None,
    ) -> None:
        self.query_understanding = query_understanding or QueryUnderstandingService()
        self.ranking_engine = ranking_engine or HybridRankingEngine()
        self.compressor = compressor or ContextCompressionService()
        self.reasoning_engine = reasoning_engine or ReasoningEngine()

    def understand(self, query: str, *, filters: dict[str, object] | None = None) -> QueryProfile:
        return self.query_understanding.analyze(query, filters=filters)

    def search(
        self,
        profile: QueryProfile,
        sections: list[KnowledgeSection],
        vectors: dict[str, list[float]],
        *,
        mode: SearchMode,
        options: SearchOptions,
    ) -> list[RetrievalCandidate]:
        ranked = self.ranking_engine.search(profile, sections, vectors, top_k=options.top_k, mode=mode)
        return self.compressor.compress(
            profile,
            ranked,
            max_characters_per_section=options.max_context_characters,
        )

    def answer(
        self,
        profile: QueryProfile,
        sections: list[KnowledgeSection],
        vectors: dict[str, list[float]],
        *,
        options: SearchOptions,
    ) -> ReasonedAnswer:
        candidates = self.search(profile, sections, vectors, mode=SearchMode.HYBRID, options=options)
        cache_key = stable_hash(
            "ask",
            profile.normalized_query,
            profile.intent.value,
            profile.filters,
            options.top_k,
            options.namespace,
            options.collection_name,
        )
        return self.reasoning_engine.reason(profile, candidates, cache_key=cache_key)
