"""AI evaluation providers."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import re

from app.domain.enums import DifficultyLevel


@dataclass(frozen=True)
class EvaluationInput:
    """Evaluator input."""

    role: str
    question_prompt: str
    question_category: str
    question_difficulty: str
    answer_transcript: str


@dataclass(frozen=True)
class EvaluationResult:
    """Evaluator output."""

    technical_accuracy: Decimal
    communication: Decimal
    completeness: Decimal
    confidence_score: Decimal
    problem_solving: Decimal
    explanation_quality: Decimal
    overall_score: Decimal
    correct_answer: str
    better_answer: str
    industry_standard_answer: str
    improvement_suggestions: list[str]
    related_topics: list[str]
    difficulty_analysis: dict
    evaluator_version: str


class AnswerEvaluationProvider:
    """Evaluation provider interface."""

    evaluator_version = "provider-interface"

    async def evaluate(self, payload: EvaluationInput) -> EvaluationResult:
        raise NotImplementedError


class TemplateAIEvaluationProvider(AnswerEvaluationProvider):
    """Deterministic AI-style evaluator until an external model provider is configured."""

    evaluator_version = "template-ai-evaluator-v1"

    async def evaluate(self, payload: EvaluationInput) -> EvaluationResult:
        transcript = payload.answer_transcript.strip()
        words = self._words(transcript)
        unique_words = set(words)
        prompt_words = set(self._words(payload.question_prompt))

        word_count = len(words)
        prompt_overlap = len(unique_words.intersection(prompt_words))
        structure_markers = self._count_markers(transcript)
        uncertainty_markers = self._count_uncertainty(transcript)
        technical_terms = self._technical_terms(payload.question_category)
        technical_hits = len(unique_words.intersection(technical_terms))

        technical_accuracy = self._score(45 + technical_hits * 9 + prompt_overlap * 2 - uncertainty_markers * 2)
        communication = self._score(50 + min(word_count, 160) * 0.16 + structure_markers * 5 - uncertainty_markers * 3)
        completeness = self._score(40 + min(word_count, 220) * 0.18 + prompt_overlap * 2 + structure_markers * 4)
        confidence_score = self._score(68 - uncertainty_markers * 7 + structure_markers * 3 + min(word_count, 120) * 0.08)
        problem_solving = self._score(45 + technical_hits * 6 + structure_markers * 6 + prompt_overlap)
        explanation_quality = self._score(45 + structure_markers * 7 + min(word_count, 180) * 0.15)
        overall_score = self._weighted_average(
            [
                (technical_accuracy, Decimal("0.25")),
                (communication, Decimal("0.15")),
                (completeness, Decimal("0.15")),
                (confidence_score, Decimal("0.10")),
                (problem_solving, Decimal("0.20")),
                (explanation_quality, Decimal("0.15")),
            ]
        )

        return EvaluationResult(
            technical_accuracy=technical_accuracy,
            communication=communication,
            completeness=completeness,
            confidence_score=confidence_score,
            problem_solving=problem_solving,
            explanation_quality=explanation_quality,
            overall_score=overall_score,
            correct_answer=self._correct_answer(payload),
            better_answer=self._better_answer(payload),
            industry_standard_answer=self._industry_standard_answer(payload),
            improvement_suggestions=self._suggestions(
                word_count=word_count,
                structure_markers=structure_markers,
                uncertainty_markers=uncertainty_markers,
                technical_hits=technical_hits,
            ),
            related_topics=self._related_topics(payload.question_category),
            difficulty_analysis=self._difficulty_analysis(
                difficulty=payload.question_difficulty,
                word_count=word_count,
                technical_hits=technical_hits,
                structure_markers=structure_markers,
            ),
            evaluator_version=self.evaluator_version,
        )

    def _words(self, value: str) -> list[str]:
        return re.findall(r"[a-zA-Z][a-zA-Z0-9_+-]*", value.lower())

    def _score(self, value: float | int | Decimal) -> Decimal:
        raw_value = Decimal(str(value))
        bounded = max(Decimal("0"), min(Decimal("100"), raw_value))
        return bounded.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _weighted_average(self, weighted_scores: list[tuple[Decimal, Decimal]]) -> Decimal:
        total = sum(score * weight for score, weight in weighted_scores)
        return total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _count_markers(self, transcript: str) -> int:
        markers = ["first", "second", "third", "because", "therefore", "tradeoff", "for example", "then"]
        lowered = transcript.lower()
        return sum(1 for marker in markers if marker in lowered)

    def _count_uncertainty(self, transcript: str) -> int:
        markers = ["maybe", "not sure", "i guess", "probably", "kind of", "sort of"]
        lowered = transcript.lower()
        return sum(1 for marker in markers if marker in lowered)

    def _technical_terms(self, category: str) -> set[str]:
        base_terms = {
            "tradeoff",
            "complexity",
            "testing",
            "monitoring",
            "scalability",
            "latency",
            "reliability",
            "data",
        }
        category_terms = {
            "python": {"async", "typing", "pytest", "generator", "context", "package"},
            "java": {"jvm", "thread", "spring", "memory", "gc", "interface"},
            "sql": {"index", "transaction", "join", "query", "schema", "isolation"},
            "dsa": {"heap", "hash", "graph", "tree", "runtime", "space"},
            "system_design": {"cache", "queue", "database", "partition", "replica", "observability"},
            "machine_learning": {"model", "features", "validation", "training", "metrics", "leakage"},
            "deep_learning": {"transformer", "neural", "embedding", "fine-tune", "overfitting", "gradient"},
            "nlp": {"token", "embedding", "entity", "classification", "semantic", "transcript"},
            "prompt_engineering": {"prompt", "context", "retrieval", "grounding", "examples", "guardrails"},
            "behavioral": {"impact", "collaboration", "conflict", "ownership", "stakeholder", "reflection"},
            "hr": {"motivation", "fit", "expectations", "culture", "team", "growth"},
        }
        return base_terms.union(category_terms.get(category, set()))

    def _related_topics(self, category: str) -> list[str]:
        topics = {
            "python": ["Type hints", "Async IO", "Testing strategy", "Packaging"],
            "java": ["JVM performance", "Concurrency", "Spring architecture", "Memory management"],
            "sql": ["Indexing", "Transactions", "Query planning", "Schema design"],
            "dsa": ["Time complexity", "Space complexity", "Data structure selection", "Edge cases"],
            "system_design": ["Scalability", "Reliability", "Caching", "Observability"],
            "machine_learning": ["Feature engineering", "Model validation", "Data leakage", "Metrics"],
            "deep_learning": ["Fine-tuning", "Embeddings", "Transformers", "Overfitting"],
            "nlp": ["Tokenization", "Semantic extraction", "Classification", "Transcript processing"],
            "prompt_engineering": ["Prompt testing", "Grounding", "Few-shot examples", "Guardrails"],
            "behavioral": ["STAR method", "Conflict resolution", "Leadership signals", "Reflection"],
            "hr": ["Role fit", "Motivation", "Work style", "Career goals"],
        }
        return topics.get(category, ["Communication", "Structure", "Depth"])

    def _correct_answer(self, payload: EvaluationInput) -> str:
        return (
            f"A correct answer for this {payload.question_category.replace('_', ' ')} question should directly address "
            f"the prompt, state assumptions, explain the approach, cover tradeoffs, and connect the reasoning to the "
            f"{payload.role} role."
        )

    def _better_answer(self, payload: EvaluationInput) -> str:
        return (
            f"A stronger answer would begin with a concise thesis, then walk through the reasoning step by step. "
            f"For this prompt, mention concrete examples, risks, tradeoffs, and how you would validate the approach. "
            f"Keep the answer specific to {payload.role} responsibilities."
        )

    def _industry_standard_answer(self, payload: EvaluationInput) -> str:
        return (
            f"An industry-standard answer would combine correctness, operational judgment, clear communication, and "
            f"practical examples. It would describe the expected solution, explain why alternatives were rejected, "
            f"identify failure modes, and define measurable success criteria for a {payload.role} context."
        )

    def _suggestions(
        self,
        *,
        word_count: int,
        structure_markers: int,
        uncertainty_markers: int,
        technical_hits: int,
    ) -> list[str]:
        suggestions: list[str] = []
        if word_count < 60:
            suggestions.append("Expand the answer with concrete reasoning, examples, and tradeoffs.")
        if structure_markers < 2:
            suggestions.append("Use a clearer structure such as first, second, tradeoff, and conclusion.")
        if technical_hits < 3:
            suggestions.append("Add more domain-specific terms and explain how they apply to the prompt.")
        if uncertainty_markers:
            suggestions.append("Replace uncertain phrasing with explicit assumptions and confident reasoning.")
        if not suggestions:
            suggestions.append("Keep the strong structure and add one measurable success criterion.")
        return suggestions

    def _difficulty_analysis(
        self,
        *,
        difficulty: str,
        word_count: int,
        technical_hits: int,
        structure_markers: int,
    ) -> dict:
        expected_depth = {
            DifficultyLevel.EASY.value: "basic clarity and direct correctness",
            DifficultyLevel.MEDIUM.value: "structured reasoning with examples and tradeoffs",
            DifficultyLevel.HARD.value: "deep technical detail, edge cases, and operational awareness",
            DifficultyLevel.EXPERT.value: "senior judgment, strategic tradeoffs, and measurable outcomes",
        }.get(difficulty, "structured reasoning")
        return {
            "difficulty": difficulty,
            "expected_depth": expected_depth,
            "observed_word_count": word_count,
            "technical_signal_count": technical_hits,
            "structure_signal_count": structure_markers,
        }
