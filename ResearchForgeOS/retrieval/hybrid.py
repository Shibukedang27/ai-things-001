from dataclasses import replace

from retrieval.deduplication import DuplicateRemovalService
from retrieval.keyword_search import KeywordSearchEngine
from retrieval.metadata_search import MetadataSearchEngine
from retrieval.reranker import ReRankingService
from retrieval.semantic_search import SemanticSearchEngine
from retrieval.types import KnowledgeSection, QueryProfile, RetrievalCandidate, SearchMode
from retrieval.utils import clamp


class HybridRankingEngine:
    def __init__(
        self,
        keyword_search: KeywordSearchEngine | None = None,
        semantic_search: SemanticSearchEngine | None = None,
        metadata_search: MetadataSearchEngine | None = None,
        deduplicator: DuplicateRemovalService | None = None,
        reranker: ReRankingService | None = None,
    ) -> None:
        self.keyword_search = keyword_search or KeywordSearchEngine()
        self.semantic_search = semantic_search or SemanticSearchEngine()
        self.metadata_search = metadata_search or MetadataSearchEngine()
        self.deduplicator = deduplicator or DuplicateRemovalService()
        self.reranker = reranker or ReRankingService()

    def search(
        self,
        profile: QueryProfile,
        sections: list[KnowledgeSection],
        vectors: dict[str, list[float]],
        *,
        top_k: int,
        mode: SearchMode,
    ) -> list[RetrievalCandidate]:
        if mode == SearchMode.KEYWORD:
            candidates = self.keyword_search.search(profile, sections, top_k=top_k * 3)
        elif mode == SearchMode.SEMANTIC:
            candidates = self.semantic_search.search(profile, sections, vectors, top_k=top_k * 3)
        else:
            candidates = self._hybrid(profile, sections, vectors, top_k=top_k * 3)
        candidates = self.deduplicator.remove_duplicates(candidates)
        return self.reranker.rerank(profile, candidates)[:top_k]

    def _hybrid(
        self,
        profile: QueryProfile,
        sections: list[KnowledgeSection],
        vectors: dict[str, list[float]],
        *,
        top_k: int,
    ) -> list[RetrievalCandidate]:
        merged: dict[str, RetrievalCandidate] = {}
        for candidate in self.keyword_search.search(profile, sections, top_k=top_k):
            merged[candidate.section.section_id] = candidate
        for candidate in self.semantic_search.search(profile, sections, vectors, top_k=top_k):
            current = merged.get(candidate.section.section_id)
            merged[candidate.section.section_id] = self._merge(current, candidate) if current else candidate
        for section in sections:
            metadata_candidate = self.metadata_search.as_candidate(profile, section)
            if metadata_candidate is None:
                continue
            current = merged.get(section.section_id)
            merged[section.section_id] = self._merge(current, metadata_candidate) if current else metadata_candidate
        return sorted(merged.values(), key=lambda candidate: candidate.score, reverse=True)[:top_k]

    def _merge(self, left: RetrievalCandidate | None, right: RetrievalCandidate) -> RetrievalCandidate:
        if left is None:
            left = right
        keyword_score = max(left.keyword_score, right.keyword_score)
        semantic_score = max(left.semantic_score, right.semantic_score)
        metadata_score = max(left.metadata_score, right.metadata_score)
        score = clamp(keyword_score * 0.36 + semantic_score * 0.49 + metadata_score * 0.15)
        return replace(
            left,
            score=score,
            keyword_score=keyword_score,
            semantic_score=semantic_score,
            metadata_score=metadata_score,
            reasons=list(dict.fromkeys([*left.reasons, *right.reasons])),
        )
