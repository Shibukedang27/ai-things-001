from knowledge_engine.dna.types import DNADocumentInput
from knowledge_engine.dna.utils import score_from_signals


class KnowledgeDNAScorer:
    DIFFICULTY_WEIGHTS = {
        "beginner": 0.12,
        "intermediate": 0.28,
        "advanced": 0.44,
        "expert": 0.58,
    }
    INTERVIEW_MARKERS = {
        "algorithm",
        "architecture",
        "database",
        "api",
        "security",
        "embedding",
        "system design",
        "complexity",
        "transformer",
        "neural",
    }
    INDUSTRY_MARKERS = {
        "production",
        "deployment",
        "api",
        "database",
        "cloud",
        "security",
        "latency",
        "scale",
        "monitoring",
        "framework",
    }

    def knowledge_score(self, document: DNADocumentInput, mathematical_topics: list[str]) -> float:
        return score_from_signals(
            min(0.22, len(document.concepts) * 0.012),
            min(0.16, len(document.technologies) * 0.018),
            min(0.14, len(document.algorithms) * 0.035),
            min(0.12, len(mathematical_topics) * 0.03),
            min(0.12, document.word_count / 12000),
            self.DIFFICULTY_WEIGHTS.get(document.difficulty, 0.24),
            base=0.12,
        )

    def interview_importance(self, document: DNADocumentInput) -> float:
        text = self._signal_text(document)
        hits = sum(1 for marker in self.INTERVIEW_MARKERS if marker in text)
        return score_from_signals(min(0.54, hits * 0.07), min(0.22, len(document.algorithms) * 0.05), base=0.18)

    def industry_relevance(self, document: DNADocumentInput) -> float:
        text = self._signal_text(document)
        hits = sum(1 for marker in self.INDUSTRY_MARKERS if marker in text)
        return score_from_signals(min(0.5, hits * 0.065), min(0.22, len(document.technologies) * 0.035), base=0.2)

    def implementation_complexity(self, document: DNADocumentInput) -> float:
        return score_from_signals(
            min(0.2, document.code_snippet_count * 0.055),
            min(0.2, len(document.algorithms) * 0.06),
            min(0.2, len(document.technologies) * 0.025),
            self.DIFFICULTY_WEIGHTS.get(document.difficulty, 0.24),
            base=0.1,
        )

    def mastery_hours(self, document: DNADocumentInput, knowledge_score: float) -> int:
        base_hours = max(2, round(document.estimated_reading_time_minutes / 10))
        concept_hours = len(document.concepts) * 2
        implementation_hours = 6 if document.code_snippet_count else 0
        difficulty_multiplier = 1 + self.DIFFICULTY_WEIGHTS.get(document.difficulty, 0.24)
        return max(
            4,
            round((base_hours + concept_hours + implementation_hours) * difficulty_multiplier * knowledge_score),
        )

    def _signal_text(self, document: DNADocumentInput) -> str:
        return " ".join(
            [
                document.title,
                document.category,
                " ".join(document.topics),
                " ".join(document.keywords),
                " ".join(concept.name for concept in document.concepts),
                " ".join(technology.name for technology in document.technologies),
                document.cleaned_text[:4000],
            ]
        ).lower()
