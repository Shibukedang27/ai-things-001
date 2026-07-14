"""Analytics aggregation service."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import AnswerEvaluation, Interview
from app.repositories import AnalyticsRepository
from app.schemas.analytics import (
    AnalyticsOverview,
    AnalyticsSummary,
    HeatMapCell,
    InterviewHistoryAnalyticsItem,
    PerformanceGraphPoint,
    ProgressPoint,
    RadarMetric,
    TopicAccuracyPoint,
    TrendPoint,
)
from app.services.auth import AuthenticatedPrincipal
from app.utils.time import utc_now


@dataclass(frozen=True)
class EvaluationAnalyticsRecord:
    """Flat evaluation record for analytics aggregation."""

    category: str
    created_at: datetime
    overall_score: Decimal
    technical_accuracy: Decimal
    communication: Decimal
    problem_solving: Decimal
    explanation_quality: Decimal


class AnalyticsAggregationService:
    """Generate analytics payloads from interviews and answer evaluations."""

    radar_benchmark = Decimal("80.00")

    def __init__(self, session: AsyncSession) -> None:
        self.repository = AnalyticsRepository(session)

    async def overview(self, *, principal: AuthenticatedPrincipal) -> AnalyticsOverview:
        evaluation_rows = await self.repository.list_evaluation_rows(user_id=principal.user.id)
        interviews = list(await self.repository.list_interviews(user_id=principal.user.id, limit=20))
        records = [
            EvaluationAnalyticsRecord(
                category=category,
                created_at=evaluation.created_at,
                overall_score=evaluation.overall_score,
                technical_accuracy=evaluation.technical_accuracy,
                communication=evaluation.communication,
                problem_solving=evaluation.problem_solving,
                explanation_quality=evaluation.explanation_quality,
            )
            for evaluation, category, _interview in evaluation_rows
        ]
        return self.build_overview(records=records, interviews=interviews)

    def build_overview(
        self,
        *,
        records: list[EvaluationAnalyticsRecord],
        interviews: list[Interview],
    ) -> AnalyticsOverview:
        topic_accuracy = self._topic_accuracy(records)
        return AnalyticsOverview(
            summary=self._summary(records=records, interviews=interviews, topic_accuracy=topic_accuracy),
            topic_wise_accuracy=topic_accuracy,
            weekly_progress=self._progress(records, period="week"),
            monthly_progress=self._progress(records, period="month"),
            heat_map=self._heat_map(records),
            radar_chart=self._radar(records),
            weakness_trends=self._weakness_trends(topic_accuracy),
            strength_trends=self._strength_trends(topic_accuracy),
            interview_history=self._interview_history(interviews),
            performance_graphs=self._performance_graphs(records),
            generated_at=utc_now(),
        )

    def _topic_accuracy(self, records: list[EvaluationAnalyticsRecord]) -> list[TopicAccuracyPoint]:
        buckets: dict[str, list[EvaluationAnalyticsRecord]] = defaultdict(list)
        for record in records:
            buckets[self._topic_label(record.category)].append(record)

        points: list[TopicAccuracyPoint] = []
        for topic, topic_records in buckets.items():
            scores = [record.technical_accuracy for record in topic_records]
            overall_scores = [record.overall_score for record in topic_records]
            trend = self._trend(scores)
            points.append(
                TopicAccuracyPoint(
                    topic=topic,
                    accuracy=self._average(scores),
                    attempts=len(topic_records),
                    average_score=self._average(overall_scores),
                    trend=trend,
                )
            )
        return sorted(points, key=lambda point: point.accuracy, reverse=True)

    def _progress(self, records: list[EvaluationAnalyticsRecord], *, period: str) -> list[ProgressPoint]:
        buckets: dict[str, list[EvaluationAnalyticsRecord]] = defaultdict(list)
        for record in records:
            if period == "week":
                year, week, _ = record.created_at.isocalendar()
                label = f"{year}-W{week:02d}"
            else:
                label = record.created_at.strftime("%Y-%m")
            buckets[label].append(record)

        points = [
            ProgressPoint(
                label=label,
                average_score=self._average([record.overall_score for record in bucket]),
                interview_count=len({record.created_at.date().isoformat() for record in bucket}),
                accuracy=self._average([record.technical_accuracy for record in bucket]),
            )
            for label, bucket in buckets.items()
        ]
        return sorted(points, key=lambda point: point.label)

    def _heat_map(self, records: list[EvaluationAnalyticsRecord]) -> list[HeatMapCell]:
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        hours = [9, 12, 15, 18, 21]
        counts: dict[tuple[str, int], int] = {(day, hour): 0 for day in days for hour in hours}
        for record in records:
            day = days[record.created_at.weekday()]
            hour = min(hours, key=lambda candidate: abs(candidate - record.created_at.hour))
            counts[(day, hour)] += 1

        max_value = max(counts.values(), default=0) or 1
        return [
            HeatMapCell(
                day=day,
                hour=hour,
                value=counts[(day, hour)],
                intensity=(Decimal(counts[(day, hour)]) / Decimal(max_value)).quantize(Decimal("0.01")),
            )
            for day in days
            for hour in hours
        ]

    def _radar(self, records: list[EvaluationAnalyticsRecord]) -> list[RadarMetric]:
        dimensions = [
            ("Technical", [record.technical_accuracy for record in records]),
            ("Communication", [record.communication for record in records]),
            ("Problem Solving", [record.problem_solving for record in records]),
            ("Explanation", [record.explanation_quality for record in records]),
            ("Overall", [record.overall_score for record in records]),
        ]
        return [
            RadarMetric(metric=metric, score=self._average(scores), benchmark=self.radar_benchmark)
            for metric, scores in dimensions
        ]

    def _weakness_trends(self, topic_accuracy: list[TopicAccuracyPoint]) -> list[TrendPoint]:
        return [
            TrendPoint(label=point.topic, score=Decimal("100.00") - point.accuracy, topic=point.topic)
            for point in sorted(topic_accuracy, key=lambda item: item.accuracy)[:6]
        ]

    def _strength_trends(self, topic_accuracy: list[TopicAccuracyPoint]) -> list[TrendPoint]:
        return [
            TrendPoint(label=point.topic, score=point.accuracy, topic=point.topic)
            for point in sorted(topic_accuracy, key=lambda item: item.accuracy, reverse=True)[:6]
        ]

    def _interview_history(self, interviews: list[Interview]) -> list[InterviewHistoryAnalyticsItem]:
        return [
            InterviewHistoryAnalyticsItem(
                id=interview.id,
                title=interview.title,
                role_title=interview.role_title,
                status=interview.status,
                score=interview.overall_score,
                duration_minutes=interview.duration_minutes,
                completed_at=interview.completed_at,
            )
            for interview in interviews[:12]
        ]

    def _performance_graphs(self, records: list[EvaluationAnalyticsRecord]) -> list[PerformanceGraphPoint]:
        recent_records = records[-12:]
        return [
            PerformanceGraphPoint(
                label=record.created_at.strftime("%b %d"),
                overall_score=record.overall_score,
                technical_accuracy=record.technical_accuracy,
                communication=record.communication,
                problem_solving=record.problem_solving,
                explanation_quality=record.explanation_quality,
            )
            for record in recent_records
        ]

    def _summary(
        self,
        *,
        records: list[EvaluationAnalyticsRecord],
        interviews: list[Interview],
        topic_accuracy: list[TopicAccuracyPoint],
    ) -> AnalyticsSummary:
        scores = [record.overall_score for record in records]
        interview_scores = [interview.overall_score for interview in interviews if interview.overall_score is not None]
        combined_scores = scores or interview_scores
        weakest = min(topic_accuracy, key=lambda point: point.accuracy).topic if topic_accuracy else None
        strongest = max(topic_accuracy, key=lambda point: point.accuracy).topic if topic_accuracy else None
        return AnalyticsSummary(
            average_score=self._average(combined_scores),
            highest_score=max(combined_scores) if combined_scores else Decimal("0.00"),
            interview_count=len(interviews),
            strongest_topic=strongest,
            weakest_topic=weakest,
        )

    def _trend(self, values: list[Decimal]) -> Decimal:
        if len(values) < 2:
            return Decimal("0.00")
        midpoint = max(1, len(values) // 2)
        first = self._average(values[:midpoint])
        second = self._average(values[midpoint:])
        return (second - first).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _average(self, values: list[Decimal]) -> Decimal:
        if not values:
            return Decimal("0.00")
        return (sum(values) / Decimal(len(values))).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def _topic_label(self, value: str) -> str:
        return value.replace("_", " ").title()
