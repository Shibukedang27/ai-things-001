from __future__ import annotations

from adaptive_learning.types import LearningAnalytics, LearningSource, MemoryState
from adaptive_learning.utils import clamp


class LearningAnalyticsEngine:
    def summarize(
        self,
        source: LearningSource,
        *,
        memory_states: list[MemoryState] | None = None,
        quiz_accuracy: float = 0.0,
        study_time_minutes: int = 0,
        completed_items: int = 0,
        total_items: int = 0,
    ) -> LearningAnalytics:
        states = memory_states or []
        retention = (
            sum(state.retention_score for state in states) / len(states)
            if states
            else self._initial_retention(source)
        )
        mastery_lookup = {
            concept.name: (
                states[index].mastery_percentage
                if index < len(states)
                else self._concept_mastery(concept.difficulty.value)
            )
            for index, concept in enumerate(source.concepts[:20])
        }
        weak = [concept for concept, mastery in mastery_lookup.items() if mastery < 45]
        strong = [concept for concept, mastery in mastery_lookup.items() if mastery >= 75]
        completion = 0.0 if total_items == 0 else completed_items / total_items
        knowledge_score = clamp((retention * 0.35) + (quiz_accuracy * 0.35) + (completion * 0.3))
        velocity = round((completed_items / max(1, study_time_minutes)) * 60, 4) if study_time_minutes else 0.0
        return LearningAnalytics(
            knowledge_score=round(knowledge_score, 4),
            retention_score=round(retention, 4),
            weak_concepts=weak[:12],
            strong_concepts=strong[:12],
            learning_velocity=velocity,
            quiz_accuracy=round(quiz_accuracy, 4),
            memory_heatmap={concept: round(mastery / 100, 4) for concept, mastery in mastery_lookup.items()},
            study_time_minutes=study_time_minutes,
            completion_rate=round(completion, 4),
            mastery_graph=[
                {"concept": concept, "mastery": round(mastery, 2)}
                for concept, mastery in sorted(mastery_lookup.items(), key=lambda item: item[0])
            ],
        )

    def _initial_retention(self, source: LearningSource) -> float:
        if source.difficulty.casefold() in {"advanced", "expert"}:
            return 0.42
        if source.difficulty.casefold() == "beginner":
            return 0.62
        return 0.52

    def _concept_mastery(self, difficulty: str) -> float:
        return {
            "easy": 58.0,
            "medium": 44.0,
            "hard": 32.0,
            "expert": 22.0,
        }.get(difficulty, 40.0)
