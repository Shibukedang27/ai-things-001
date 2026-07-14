from __future__ import annotations

import math
from datetime import UTC, datetime, timedelta

from adaptive_learning.types import MemoryState, ReviewRating
from adaptive_learning.utils import clamp


class SpacedRepetitionScheduler:
    """FSRS-inspired scheduler using stability, difficulty, and retrievability."""

    TARGET_RETENTION = 0.9

    def initial_state(self, *, now: datetime | None = None) -> MemoryState:
        current_time = now or datetime.now(UTC)
        return MemoryState(
            memory_strength=0.28,
            confidence=0.5,
            retention_score=self.TARGET_RETENTION,
            review_count=0,
            success_rate=0.0,
            last_review_at=None,
            next_review_at=current_time + timedelta(days=1),
            forgetting_curve=self._forgetting_curve(0.28, current_time),
            mastery_percentage=0.0,
        )

    def schedule(
        self,
        state: MemoryState,
        rating: ReviewRating,
        *,
        confidence: float,
        now: datetime | None = None,
    ) -> MemoryState:
        current_time = now or datetime.now(UTC)
        quality = {
            ReviewRating.AGAIN: 0.0,
            ReviewRating.HARD: 0.45,
            ReviewRating.GOOD: 0.78,
            ReviewRating.EASY: 1.0,
        }[rating]
        previous_strength = max(0.05, state.memory_strength)
        confidence = clamp(confidence)
        success_count = state.success_rate * state.review_count
        is_success = rating != ReviewRating.AGAIN
        review_count = state.review_count + 1
        success_rate = (success_count + (1 if is_success else 0)) / review_count
        difficulty_penalty = {
            ReviewRating.AGAIN: 0.42,
            ReviewRating.HARD: 0.82,
            ReviewRating.GOOD: 1.22,
            ReviewRating.EASY: 1.68,
        }[rating]
        memory_strength = clamp(
            previous_strength * difficulty_penalty + quality * 0.22 + confidence * 0.12,
            minimum=0.05,
            maximum=6.0,
        )
        interval_days = self._interval_days(memory_strength, rating)
        next_review = current_time + timedelta(days=interval_days)
        retention = self.retention_probability(memory_strength, interval_days)
        mastery = clamp((memory_strength / 6.0) * 0.72 + success_rate * 0.28) * 100
        return MemoryState(
            memory_strength=round(memory_strength, 4),
            confidence=round(confidence, 4),
            retention_score=round(retention, 4),
            review_count=review_count,
            success_rate=round(success_rate, 4),
            last_review_at=current_time,
            next_review_at=next_review,
            forgetting_curve=self._forgetting_curve(memory_strength, current_time),
            mastery_percentage=round(mastery, 2),
        )

    def retention_probability(self, memory_strength: float, elapsed_days: float) -> float:
        if memory_strength <= 0:
            return 0.0
        retrievability = math.exp(-elapsed_days / max(0.05, memory_strength * 3.0))
        return clamp(retrievability)

    def _interval_days(self, memory_strength: float, rating: ReviewRating) -> int:
        multiplier = {
            ReviewRating.AGAIN: 0.08,
            ReviewRating.HARD: 0.55,
            ReviewRating.GOOD: 1.65,
            ReviewRating.EASY: 2.7,
        }[rating]
        return max(1, min(180, round(memory_strength * multiplier * 3)))

    def _forgetting_curve(self, memory_strength: float, now: datetime) -> list[dict[str, float | str]]:
        checkpoints = [1, 3, 7, 14, 30, 60, 120]
        return [
            {
                "day": day,
                "date": (now + timedelta(days=day)).date().isoformat(),
                "retention": round(self.retention_probability(memory_strength, day), 4),
            }
            for day in checkpoints
        ]
