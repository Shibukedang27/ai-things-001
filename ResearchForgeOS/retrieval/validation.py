from retrieval.types import QueryProfile, RetrievalCandidate
from retrieval.utils import normalize_text


class KnowledgeValidationService:
    CONTRADICTION_SIGNALS = ("however", "contradicts", "opposes", "unlike", "in contrast")

    def validate(self, profile: QueryProfile, candidates: list[RetrievalCandidate]) -> dict[str, object]:
        source_documents = {candidate.section.document_id for candidate in candidates}
        combined_content = " ".join(normalize_text(candidate.section.content) for candidate in candidates)
        missing_terms = [term for term in profile.keywords[:8] if term not in combined_content]
        contradictions = [
            candidate.section.document_title
            for candidate in candidates
            if any(signal in normalize_text(candidate.section.content) for signal in self.CONTRADICTION_SIGNALS)
        ]
        return {
            "source_count": len(source_documents),
            "retrieved_section_count": len(candidates),
            "missing_information": missing_terms,
            "has_contradictions": bool(contradictions),
            "contradiction_sources": contradictions[:5],
            "is_answerable": bool(candidates) and len(missing_terms) < max(2, len(profile.keywords)),
        }
