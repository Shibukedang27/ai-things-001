"""Learning recommendation service."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.domain.enums import RoadmapStatus
from app.models import LearningRoadmap
from app.repositories import LearningRecommendationRepository
from app.schemas.learning_roadmap import LearningRoadmapRead
from app.schemas.recommendation import (
    GenerateRoadmapRequest,
    LearningRecommendationOptions,
    LearningRecommendationResponse,
)
from app.services.auth import AuthenticatedPrincipal
from app.services.recommendation_provider import CatalogLearningRecommendationProvider, LearningRecommendationProvider
from app.utils.time import utc_now


class LearningRecommendationService:
    """Application service for personalized learning recommendations."""

    def __init__(
        self,
        session: AsyncSession,
        provider: LearningRecommendationProvider | None = None,
    ) -> None:
        self.session = session
        self.repository = LearningRecommendationRepository(session)
        self.provider = provider or CatalogLearningRecommendationProvider()

    def options(self) -> LearningRecommendationOptions:
        return LearningRecommendationOptions(
            resource_types=[
                "leetcode_problems",
                "hackerrank_problems",
                "books",
                "courses",
                "youtube_videos",
            ],
            roadmap_types=["daily_practice_plan", "weekly_roadmap", "monthly_roadmap"],
            generated_from=["answer_evaluations", "questions", "interviews", "interview_history"],
            supported_outputs=[
                "weak_topics",
                "recommended_topics",
                "leetcode_problems",
                "hackerrank_problems",
                "books",
                "courses",
                "youtube_videos",
                "daily_practice_plan",
                "weekly_roadmap",
                "monthly_roadmap",
            ],
        )

    async def generate_roadmap(
        self,
        *,
        principal: AuthenticatedPrincipal,
        payload: GenerateRoadmapRequest,
    ) -> LearningRecommendationResponse:
        evaluation_context = list(
            await self.repository.list_evaluation_context(
                user_id=principal.user.id,
                interview_id=payload.interview_id,
            )
        )
        history = list(
            await self.repository.list_history(
                user_id=principal.user.id,
                interview_id=payload.interview_id,
            )
        )
        target_role = payload.target_role or self._infer_target_role(evaluation_context)
        plan = await self.provider.generate(
            payload=self.provider_input(
                target_role=target_role,
                estimated_weeks=payload.estimated_weeks,
                evaluation_context=evaluation_context,
                history=history,
            )
        )

        roadmap = await self.repository.create_roadmap(
            {
                "user_id": principal.user.id,
                "report_id": None,
                "title": f"{target_role} Personalized Learning Roadmap",
                "target_role": target_role,
                "status": RoadmapStatus.ACTIVE.value,
                "estimated_weeks": payload.estimated_weeks,
                "recommended_topics": plan.recommended_topics,
                "milestones": plan.milestones,
                "weak_topics": [topic.model_dump(mode="json") for topic in plan.weak_topics],
                "leetcode_problems": plan.leetcode_problems,
                "hackerrank_problems": plan.hackerrank_problems,
                "books": plan.books,
                "courses": plan.courses,
                "youtube_videos": plan.youtube_videos,
                "daily_practice_plan": plan.daily_practice_plan,
                "weekly_roadmap": plan.weekly_roadmap,
                "monthly_roadmap": plan.monthly_roadmap,
                "source_summary": plan.source_summary,
            }
        )
        await self.session.commit()
        await self.session.refresh(roadmap)
        return self._response(roadmap)

    async def latest_roadmap(self, *, principal: AuthenticatedPrincipal) -> LearningRecommendationResponse:
        roadmap = await self.repository.latest_roadmap(user_id=principal.user.id)
        if not roadmap:
            raise NotFoundError("Learning roadmap not found.")
        return self._response(roadmap)

    def provider_input(self, *, target_role, estimated_weeks, evaluation_context, history):
        from app.services.recommendation_provider import RecommendationInput

        return RecommendationInput(
            target_role=target_role,
            estimated_weeks=estimated_weeks,
            evaluation_context=evaluation_context,
            history=history,
        )

    def _infer_target_role(self, evaluation_context) -> str:
        for _evaluation, _question, interview in evaluation_context:
            if interview.role_title:
                return interview.role_title
        return "Interview Candidate"

    def _response(self, roadmap: LearningRoadmap) -> LearningRecommendationResponse:
        return LearningRecommendationResponse(
            roadmap=LearningRoadmapRead.model_validate(roadmap),
            weak_topics=roadmap.weak_topics,
            generated_at=utc_now(),
            source_summary=roadmap.source_summary,
        )
