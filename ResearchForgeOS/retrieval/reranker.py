from dataclasses import replace

from retrieval.types import QueryProfile, RetrievalCandidate
from retrieval.utils import clamp, normalize_text


class ReRankingService:
    def rerank(self, profile: QueryProfile, candidates: list[RetrievalCandidate]) -> list[RetrievalCandidate]:
        ranked: list[RetrievalCandidate] = []
        for candidate in candidates:
            phrase_boost = 0.08 if profile.normalized_query in normalize_text(candidate.section.content) else 0.0
            normalized_title = normalize_text(candidate.section.document_title)
            title_boost = 0.05 if any(term in normalized_title for term in profile.keywords) else 0.0
            diversity_penalty = self._source_repeat_penalty(candidate, ranked)
            adjusted_score = clamp(candidate.score + phrase_boost + title_boost - diversity_penalty)
            reasons = [
                *candidate.reasons,
                *(["Exact phrase boost"] if phrase_boost else []),
                *(["Title relevance boost"] if title_boost else []),
                *(["Source diversity penalty"] if diversity_penalty else []),
            ]
            ranked.append(
                replace(
                    candidate,
                    score=adjusted_score,
                    reasons=reasons,
                    metadata_score=candidate.metadata_score,
                )
            )
        return sorted(ranked, key=lambda candidate: candidate.score, reverse=True)

    def _source_repeat_penalty(self, candidate: RetrievalCandidate, selected: list[RetrievalCandidate]) -> float:
        repeats = sum(1 for item in selected if item.section.document_id == candidate.section.document_id)
        return min(0.06, repeats * 0.02)
