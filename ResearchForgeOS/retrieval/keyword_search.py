import math
from collections import Counter

from retrieval.types import KnowledgeSection, QueryProfile, RetrievalCandidate
from retrieval.utils import clamp, term_frequencies, tokenize


class KeywordSearchEngine:
    def search(
        self,
        profile: QueryProfile,
        sections: list[KnowledgeSection],
        *,
        top_k: int,
    ) -> list[RetrievalCandidate]:
        query_terms = profile.keywords
        if not query_terms:
            return []
        document_frequency = self._document_frequency(sections)
        total_sections = max(1, len(sections))
        candidates: list[RetrievalCandidate] = []
        for section in sections:
            frequencies = term_frequencies(self._searchable_text(section))
            score = self._bm25_like_score(query_terms, frequencies, document_frequency, total_sections)
            if score <= 0:
                continue
            normalized_score = clamp(score / (len(query_terms) * 2.5))
            reasons = [f"Matched keyword '{term}'" for term in query_terms if frequencies.get(term, 0) > 0]
            candidates.append(
                RetrievalCandidate(
                    section=section,
                    score=normalized_score,
                    keyword_score=normalized_score,
                    semantic_score=0.0,
                    metadata_score=0.0,
                    reasons=reasons[:5],
                )
            )
        return sorted(candidates, key=lambda candidate: candidate.score, reverse=True)[:top_k]

    def _document_frequency(self, sections: list[KnowledgeSection]) -> Counter[str]:
        counter: Counter[str] = Counter()
        for section in sections:
            counter.update(set(tokenize(self._searchable_text(section))))
        return counter

    def _bm25_like_score(
        self,
        query_terms: list[str],
        frequencies: Counter[str],
        document_frequency: Counter[str],
        total_sections: int,
    ) -> float:
        score = 0.0
        for term in query_terms:
            term_count = frequencies.get(term, 0)
            if term_count == 0:
                continue
            inverse_document_frequency = math.log((1 + total_sections) / (1 + document_frequency.get(term, 0))) + 1
            score += (1 + math.log(term_count)) * inverse_document_frequency
        return score

    def _searchable_text(self, section: KnowledgeSection) -> str:
        signals = [
            section.document_title,
            section.content,
            " ".join(section.topics),
            " ".join(section.keywords),
            " ".join(section.technologies),
            str(section.metadata),
        ]
        return " ".join(signal for signal in signals if signal)
