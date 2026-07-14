from dataclasses import replace

from retrieval.types import QueryProfile, RetrievalCandidate
from retrieval.utils import compress_text


class ContextCompressionService:
    def compress(
        self,
        profile: QueryProfile,
        candidates: list[RetrievalCandidate],
        *,
        max_characters_per_section: int,
    ) -> list[RetrievalCandidate]:
        compressed: list[RetrievalCandidate] = []
        for candidate in candidates:
            section = replace(
                candidate.section,
                content=compress_text(
                    candidate.section.content,
                    profile.keywords,
                    max_characters=max_characters_per_section,
                ),
            )
            compressed.append(replace(candidate, section=section))
        return compressed
