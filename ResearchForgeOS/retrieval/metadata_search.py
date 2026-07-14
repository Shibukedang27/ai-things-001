from typing import Any

from retrieval.types import KnowledgeSection, QueryProfile, RetrievalCandidate
from retrieval.utils import clamp, normalize_text


class MetadataSearchEngine:
    def score(self, profile: QueryProfile, section: KnowledgeSection) -> float:
        score = 0.0
        score += self._filter_score(profile.filters, section.metadata)
        joined_signals = normalize_text(
            " ".join(
                [
                    section.document_title,
                    section.category or "",
                    " ".join(section.topics),
                    " ".join(section.keywords),
                    " ".join(section.technologies),
                ]
            )
        )
        for term in profile.keywords:
            if term in joined_signals:
                score += 0.08
        return clamp(score)

    def as_candidate(self, profile: QueryProfile, section: KnowledgeSection) -> RetrievalCandidate | None:
        score = self.score(profile, section)
        if score <= 0:
            return None
        return RetrievalCandidate(
            section=section,
            score=score,
            keyword_score=0.0,
            semantic_score=0.0,
            metadata_score=score,
            reasons=["Metadata match"],
        )

    def _filter_score(self, filters: dict[str, Any], metadata: dict[str, Any]) -> float:
        if not filters:
            return 0.0
        matched = 0
        for key, expected in filters.items():
            current = metadata.get(key)
            if isinstance(expected, list | tuple | set):
                matched += int(current in expected)
            else:
                matched += int(current == expected)
        return matched / max(1, len(filters)) * 0.35
