from retrieval.types import RetrievalCandidate
from retrieval.utils import content_signature


class DuplicateRemovalService:
    def remove_duplicates(self, candidates: list[RetrievalCandidate]) -> list[RetrievalCandidate]:
        selected: dict[str, RetrievalCandidate] = {}
        for candidate in candidates:
            signature = content_signature(candidate.section.content)
            current = selected.get(signature)
            if current is None or candidate.score > current.score:
                selected[signature] = candidate
        return sorted(selected.values(), key=lambda candidate: candidate.score, reverse=True)
