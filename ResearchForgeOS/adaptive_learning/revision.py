from __future__ import annotations

from adaptive_learning.types import LearningSource, RevisionPlanDraft, RevisionPlanType


class RevisionEngine:
    def generate(self, source: LearningSource) -> list[RevisionPlanDraft]:
        concepts = [concept.name for concept in source.concepts[:10]] or source.topics[:10]
        return [
            self._plan(RevisionPlanType.DAILY, source, concepts, [1, 2, 3], 20),
            self._plan(RevisionPlanType.WEEKLY, source, concepts, [7, 14, 21], 45),
            self._plan(RevisionPlanType.MONTHLY, source, concepts, [30, 60, 90], 90),
            self._plan(RevisionPlanType.QUICK, source, concepts[:5], [1], 10),
            self._plan(RevisionPlanType.EXAM, source, concepts, [3, 2, 1], 120),
            self._plan(RevisionPlanType.INTERVIEW, source, concepts, [5, 3, 1], 75),
            self._plan(RevisionPlanType.CODING, source, concepts, [2, 5, 10], 60),
        ]

    def _plan(
        self,
        plan_type: RevisionPlanType,
        source: LearningSource,
        concepts: list[str],
        days: list[int],
        minutes: int,
    ) -> RevisionPlanDraft:
        schedule = [
            {
                "step": index,
                "day_offset": day,
                "duration_minutes": max(8, minutes // len(days)),
                "activity": self._activity(plan_type, concepts, index),
                "concepts": concepts[(index - 1) :: len(days)][:4] or concepts[:4],
            }
            for index, day in enumerate(days, start=1)
        ]
        return RevisionPlanDraft(
            plan_type=plan_type,
            title=f"{source.title} {plan_type.value.title()} Revision",
            schedule=schedule,
            focus_concepts=concepts,
            estimated_minutes=minutes,
            metadata={"document_id": source.document_id, "engine": "revision_engine_v1"},
        )

    def _activity(self, plan_type: RevisionPlanType, concepts: list[str], index: int) -> str:
        if plan_type == RevisionPlanType.CODING:
            return "Solve one coding challenge and review edge cases."
        if plan_type == RevisionPlanType.INTERVIEW:
            return "Answer interview questions aloud and refine follow-ups."
        if plan_type == RevisionPlanType.EXAM:
            return "Run a timed quiz and correct every missed concept."
        if plan_type == RevisionPlanType.QUICK:
            return "Review summary, weak concepts, and high-priority flashcards."
        concept = concepts[(index - 1) % len(concepts)] if concepts else "core concept"
        return f"Review flashcards, quiz questions, and notes for {concept}."
