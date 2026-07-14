from retrieval.types import RetrievalCandidate
from retrieval.utils import clamp


class ConfidenceCalculator:
    def calculate(self, candidates: list[RetrievalCandidate], validation: dict[str, object]) -> float:
        if not candidates:
            return 0.0
        top_scores = [candidate.score for candidate in candidates[:5]]
        score_signal = sum(top_scores) / len(top_scores)
        source_count = len({candidate.section.document_id for candidate in candidates})
        source_signal = min(0.2, source_count * 0.05)
        validation_penalty = 0.15 if validation.get("has_contradictions") else 0.0
        missing_penalty = 0.1 if validation.get("missing_information") else 0.0
        return round(clamp(score_signal * 0.72 + source_signal + 0.08 - validation_penalty - missing_penalty), 4)
