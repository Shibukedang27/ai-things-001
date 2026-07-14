from knowledge_engine.dna.types import DNAConceptInput, LearningPathStep
from knowledge_engine.utils import dedupe_preserve_order


class LearningPathGenerator:
    def generate(
        self,
        *,
        concepts: list[DNAConceptInput],
        prerequisites: list[str],
        future_topics: list[str],
        estimated_mastery_time_hours: int,
    ) -> list[LearningPathStep]:
        ordered_topics = dedupe_preserve_order(
            [
                *prerequisites,
                *[concept.name for concept in concepts if concept.concept_type == "core"],
                *[concept.name for concept in concepts if concept.concept_type != "core"],
                *future_topics,
            ]
        )
        if not ordered_topics:
            ordered_topics = ["Read Source", "Extract Concepts", "Practice Recall"]

        per_step_hours = max(1, round(estimated_mastery_time_hours / max(1, len(ordered_topics))))
        steps: list[LearningPathStep] = []
        for index, topic in enumerate(ordered_topics[:18], start=1):
            difficulty = self._difficulty_for_topic(topic, concepts)
            steps.append(
                LearningPathStep(
                    order_index=index,
                    topic=topic,
                    reason=self._reason(topic, prerequisites, future_topics, concepts),
                    estimated_hours=per_step_hours,
                    difficulty_level=difficulty,
                    resource_hint=self._resource_hint(topic, prerequisites, future_topics),
                )
            )
        return steps

    def _difficulty_for_topic(self, topic: str, concepts: list[DNAConceptInput]) -> str:
        for concept in concepts:
            if concept.name.lower() == topic.lower():
                return concept.difficulty_level
        return "beginner"

    def _reason(
        self,
        topic: str,
        prerequisites: list[str],
        future_topics: list[str],
        concepts: list[DNAConceptInput],
    ) -> str:
        if topic in prerequisites:
            return f"{topic} is a prerequisite that makes the document easier to understand."
        if topic in future_topics:
            return f"{topic} extends the document into the next useful learning area."
        if any(concept.name == topic for concept in concepts):
            return f"{topic} is part of the document's core knowledge DNA."
        return f"{topic} supports the learning path for this document."

    def _resource_hint(self, topic: str, prerequisites: list[str], future_topics: list[str]) -> str:
        if topic in prerequisites:
            return "Review a foundational article, lecture note, or short primer before returning to the source."
        if topic in future_topics:
            return "Use this as the next document, paper, or implementation project to study."
        return "Create notes, flashcards, and a small explanation for this topic."
