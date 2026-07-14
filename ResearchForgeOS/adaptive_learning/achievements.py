from __future__ import annotations

from adaptive_learning.types import AchievementDraft, LearningAnalytics, LearningSource


class AchievementEngine:
    def initial_achievements(self, source: LearningSource, analytics: LearningAnalytics) -> list[AchievementDraft]:
        achievements = [
            AchievementDraft(
                achievement_type="milestone",
                title="Learning Path Created",
                description=f"Generated a complete adaptive learning path for {source.title}.",
                badge="learning_path",
                skill_level="starter",
                points=25,
                metadata={"document_id": source.document_id},
            )
        ]
        if len(source.concepts) >= 5:
            achievements.append(
                AchievementDraft(
                    achievement_type="badge",
                    title="Concept Mapper",
                    description="Mapped at least five concepts into learning assets.",
                    badge="concept_mapper",
                    skill_level="apprentice",
                    points=40,
                    metadata={"concept_count": len(source.concepts), "document_id": source.document_id},
                )
            )
        if analytics.knowledge_score >= 0.7:
            achievements.append(
                AchievementDraft(
                    achievement_type="skill_level",
                    title="Strong Starting Knowledge",
                    description="Initial knowledge score is already high for this source.",
                    badge="strong_start",
                    skill_level="skilled",
                    points=60,
                    metadata={"knowledge_score": analytics.knowledge_score, "document_id": source.document_id},
                )
            )
        return achievements

    def review_achievements(
        self,
        *,
        streak_days: int,
        mastery_percentage: float,
        quiz_accuracy: float,
    ) -> list[AchievementDraft]:
        achievements: list[AchievementDraft] = []
        if streak_days >= 3:
            achievements.append(
                AchievementDraft(
                    achievement_type="learning_streak",
                    title=f"{streak_days}-Day Learning Streak",
                    description="Completed adaptive learning activity on consecutive days.",
                    badge="learning_streak",
                    skill_level="consistent",
                    points=streak_days * 10,
                    metadata={"streak_days": streak_days},
                )
            )
        if mastery_percentage >= 80:
            achievements.append(
                AchievementDraft(
                    achievement_type="milestone",
                    title="Mastery Milestone",
                    description="Reached high mastery on scheduled memory reviews.",
                    badge="mastery",
                    skill_level="advanced",
                    points=100,
                    metadata={"mastery_percentage": mastery_percentage},
                )
            )
        if quiz_accuracy >= 0.9:
            achievements.append(
                AchievementDraft(
                    achievement_type="badge",
                    title="Quiz Precision",
                    description="Scored at least 90 percent on a knowledge test.",
                    badge="quiz_precision",
                    skill_level="skilled",
                    points=75,
                    metadata={"quiz_accuracy": quiz_accuracy},
                )
            )
        return achievements
