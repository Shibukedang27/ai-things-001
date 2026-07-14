from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from adaptive_learning import LearningAnalyticsEngine
from adaptive_learning.scheduling import SpacedRepetitionScheduler
from adaptive_learning.types import LearningSource, MemoryState

from backend.models.learning import LearningSession, MemoryTracking, Progress, RevisionPlan
from backend.utils.datetime import utc_now


@dataclass(frozen=True)
class LearningMaintenanceResult:
    progress: Progress
    due_review_count: int
    overdue_review_count: int
    active_revision_count: int


class LearningBackgroundService:
    """Deterministic jobs that can be run by API calls, workers, or schedulers."""

    def __init__(
        self,
        scheduler: SpacedRepetitionScheduler | None = None,
        analytics: LearningAnalyticsEngine | None = None,
    ) -> None:
        self.scheduler = scheduler or SpacedRepetitionScheduler()
        self.analytics = analytics or LearningAnalyticsEngine()

    def schedule_revision_reviews(self, plans: Sequence[RevisionPlan]) -> list[RevisionPlan]:
        now = utc_now()
        for plan in plans:
            if plan.due_at is not None:
                continue
            first_step = plan.schedule[0] if plan.schedule else {}
            day_offset = int(first_step.get("day_offset", 1)) if isinstance(first_step, dict) else 1
            plan.due_at = now + timedelta(days=max(1, day_offset))
        return list(plans)

    def schedule_reminders(self, memory_records: Sequence[MemoryTracking]) -> list[dict[str, object]]:
        now = utc_now()
        reminders: list[dict[str, object]] = []
        for record in memory_records:
            next_review_at = self._aware(record.next_review_at)
            if next_review_at is None:
                continue
            hours_until_due = (next_review_at - now).total_seconds() / 3600
            if hours_until_due <= 24:
                reminders.append(
                    {
                        "flashcard_id": record.flashcard_id,
                        "concept": record.concept,
                        "due_at": next_review_at.isoformat(),
                        "urgency": "overdue" if hours_until_due < 0 else "due_soon",
                    }
                )
        return reminders

    def calculate_progress(
        self,
        *,
        source: LearningSource,
        progress: Progress,
        memory_records: Sequence[MemoryTracking],
        quiz_accuracy: float,
        sessions: Sequence[LearningSession],
        total_items: int,
    ) -> Progress:
        memory_states = [self._memory_state(record) for record in memory_records]
        completed_items = sum(1 for record in memory_records if record.review_count > 0)
        study_time_minutes = sum(max(0, session.duration_seconds // 60) for session in sessions)
        analytics = self.analytics.summarize(
            source,
            memory_states=memory_states,
            quiz_accuracy=quiz_accuracy,
            study_time_minutes=study_time_minutes,
            completed_items=completed_items,
            total_items=total_items,
        )
        progress.knowledge_score = analytics.knowledge_score
        progress.retention_score = analytics.retention_score
        progress.weak_concepts = analytics.weak_concepts
        progress.strong_concepts = analytics.strong_concepts
        progress.learning_velocity = analytics.learning_velocity
        progress.quiz_accuracy = analytics.quiz_accuracy
        progress.memory_heatmap = analytics.memory_heatmap
        progress.study_time_minutes = analytics.study_time_minutes
        progress.completion_rate = analytics.completion_rate
        progress.mastery_graph = analytics.mastery_graph
        progress.mastered_items = sum(1 for record in memory_records if record.mastery_percentage >= 80)
        progress.total_items = total_items
        progress.last_activity_at = utc_now()
        progress.metadata_json = {
            **progress.metadata_json,
            "background_jobs": {
                "progress_calculation": utc_now().isoformat(),
                "analytics_update": utc_now().isoformat(),
                "mastery_update": utc_now().isoformat(),
            },
        }
        return progress

    def update_analytics(
        self,
        *,
        source: LearningSource,
        progress: Progress,
        memory_records: Sequence[MemoryTracking],
        quiz_accuracy: float,
        sessions: Sequence[LearningSession],
        total_items: int,
    ) -> Progress:
        return self.calculate_progress(
            source=source,
            progress=progress,
            memory_records=memory_records,
            quiz_accuracy=quiz_accuracy,
            sessions=sessions,
            total_items=total_items,
        )

    def update_mastery(self, memory_records: Sequence[MemoryTracking]) -> list[MemoryTracking]:
        now = utc_now()
        for record in memory_records:
            last_review_at = self._aware(record.last_review_at)
            if last_review_at is None:
                record.retention_score = self.scheduler.retention_probability(record.memory_strength, 1)
                continue
            elapsed_days = max(0.0, (now - last_review_at).total_seconds() / 86_400)
            record.retention_score = round(
                self.scheduler.retention_probability(record.memory_strength, elapsed_days),
                4,
            )
            record.mastery_percentage = round(
                min(100.0, (record.memory_strength / 6.0) * 70 + record.success_rate * 30),
                2,
            )
        return list(memory_records)

    def run_document_maintenance(
        self,
        *,
        source: LearningSource,
        progress: Progress,
        memory_records: Sequence[MemoryTracking],
        revision_plans: Sequence[RevisionPlan],
        sessions: Sequence[LearningSession],
        quiz_accuracy: float,
        total_items: int,
    ) -> LearningMaintenanceResult:
        self.schedule_revision_reviews(revision_plans)
        self.update_mastery(memory_records)
        self.calculate_progress(
            source=source,
            progress=progress,
            memory_records=memory_records,
            quiz_accuracy=quiz_accuracy,
            sessions=sessions,
            total_items=total_items,
        )
        now = utc_now()
        due_count = sum(
            1
            for record in memory_records
            if (next_review_at := self._aware(record.next_review_at)) is not None and next_review_at <= now
        )
        overdue_count = sum(
            1
            for record in memory_records
            if (next_review_at := self._aware(record.next_review_at)) is not None
            and next_review_at < now - timedelta(days=1)
        )
        active_revision_count = sum(1 for plan in revision_plans if plan.status == "active")
        return LearningMaintenanceResult(
            progress=progress,
            due_review_count=due_count,
            overdue_review_count=overdue_count,
            active_revision_count=active_revision_count,
        )

    def _memory_state(self, record: MemoryTracking) -> MemoryState:
        return MemoryState(
            memory_strength=record.memory_strength,
            confidence=record.confidence,
            retention_score=record.retention_score,
            review_count=record.review_count,
            success_rate=record.success_rate,
            last_review_at=record.last_review_at,
            next_review_at=record.next_review_at,
            forgetting_curve=record.forgetting_curve,
            mastery_percentage=record.mastery_percentage,
        )

    def _aware(self, value: datetime | None) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            return value.replace(tzinfo=UTC)
        return value
