from __future__ import annotations

from adaptive_learning.achievements import AchievementEngine
from adaptive_learning.analytics import LearningAnalyticsEngine
from adaptive_learning.coding import CodingChallengeEngine
from adaptive_learning.flashcards import FlashcardEngine
from adaptive_learning.interviews import InterviewPreparationEngine
from adaptive_learning.quizzes import QuizEngine
from adaptive_learning.revision import RevisionEngine
from adaptive_learning.types import AdaptiveLearningBundle, LearningSource


class AdaptiveLearningEngine:
    def __init__(
        self,
        flashcards: FlashcardEngine | None = None,
        quizzes: QuizEngine | None = None,
        interviews: InterviewPreparationEngine | None = None,
        coding: CodingChallengeEngine | None = None,
        revision: RevisionEngine | None = None,
        analytics: LearningAnalyticsEngine | None = None,
        achievements: AchievementEngine | None = None,
    ) -> None:
        self.flashcards = flashcards or FlashcardEngine()
        self.quizzes = quizzes or QuizEngine()
        self.interviews = interviews or InterviewPreparationEngine()
        self.coding = coding or CodingChallengeEngine()
        self.revision = revision or RevisionEngine()
        self.analytics = analytics or LearningAnalyticsEngine()
        self.achievements = achievements or AchievementEngine()

    def build(self, source: LearningSource) -> AdaptiveLearningBundle:
        flashcards = self.flashcards.generate(source)
        quiz = self.quizzes.generate(source)
        interview_questions = self.interviews.generate(source)
        coding_challenges = self.coding.generate(source)
        revision_plans = self.revision.generate(source)
        analytics = self.analytics.summarize(
            source,
            quiz_accuracy=0.0,
            study_time_minutes=0,
            completed_items=0,
            total_items=len(flashcards) + len(quiz.questions) + len(coding_challenges),
        )
        achievements = self.achievements.initial_achievements(source, analytics)
        return AdaptiveLearningBundle(
            flashcards=flashcards,
            quiz=quiz,
            interview_questions=interview_questions,
            coding_challenges=coding_challenges,
            revision_plans=revision_plans,
            analytics=analytics,
            achievements=achievements,
        )
