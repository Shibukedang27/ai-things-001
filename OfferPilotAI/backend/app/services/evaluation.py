"""AI evaluation service."""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError
from app.domain.enums import InterviewHistoryEvent
from app.models import Answer, AnswerEvaluation, Interview, Question
from app.repositories import AnswerEvaluationRepository
from app.repositories.interview_engine import InterviewEngineRepository
from app.schemas.evaluation import AnswerEvaluationRead, EvaluateAnswerResponse, EvaluateInterviewResponse, EvaluationOptions
from app.services.auth import AuthenticatedPrincipal
from app.services.evaluation_provider import EvaluationInput, EvaluationResult, TemplateAIEvaluationProvider
from app.utils.time import utc_now


class AIEvaluationService:
    """Application service for answer evaluation."""

    def __init__(
        self,
        session: AsyncSession,
        provider: TemplateAIEvaluationProvider | None = None,
    ) -> None:
        self.session = session
        self.repository = AnswerEvaluationRepository(session)
        self.history_repository = InterviewEngineRepository(session)
        self.provider = provider or TemplateAIEvaluationProvider()

    def options(self) -> EvaluationOptions:
        return EvaluationOptions(
            dimensions=[
                "technical_accuracy",
                "communication",
                "completeness",
                "confidence_score",
                "problem_solving",
                "explanation_quality",
                "overall_score",
            ],
            generated_outputs=[
                "correct_answer",
                "better_answer",
                "industry_standard_answer",
                "improvement_suggestions",
                "related_topics",
                "difficulty_analysis",
            ],
            evaluator_version=self.provider.evaluator_version,
        )

    async def get_answer_evaluation(
        self,
        *,
        principal: AuthenticatedPrincipal,
        answer_id: str,
    ) -> AnswerEvaluationRead:
        answer = await self.repository.get_answer_for_user(answer_id=answer_id, user_id=principal.user.id)
        if not answer:
            raise NotFoundError("Answer not found.")
        evaluation = await self.repository.get_existing_for_answer(answer.id)
        if not evaluation:
            raise NotFoundError("Answer evaluation not found.")
        return AnswerEvaluationRead.model_validate(evaluation)

    async def evaluate_answer(
        self,
        *,
        principal: AuthenticatedPrincipal,
        answer_id: str,
        force: bool = False,
    ) -> EvaluateAnswerResponse:
        answer = await self.repository.get_answer_for_user(answer_id=answer_id, user_id=principal.user.id)
        if not answer:
            raise NotFoundError("Answer not found.")
        evaluation = await self._evaluate_answer(answer=answer, role=None, force=force)
        await self.session.commit()
        await self.session.refresh(evaluation)
        return EvaluateAnswerResponse(evaluation=AnswerEvaluationRead.model_validate(evaluation))

    async def evaluate_interview(
        self,
        *,
        principal: AuthenticatedPrincipal,
        interview_id: str,
        force: bool = False,
    ) -> EvaluateInterviewResponse:
        interview = await self.repository.get_interview_for_user(interview_id=interview_id, user_id=principal.user.id)
        if not interview:
            raise NotFoundError("Interview not found.")

        answers = list(
            await self.repository.list_answers_for_interview(interview_id=interview.id, user_id=principal.user.id)
        )
        evaluations: list[AnswerEvaluation] = []
        skipped_count = 0
        for answer in answers:
            existing = await self.repository.get_existing_for_answer(answer.id)
            if existing and not force:
                evaluations.append(existing)
                skipped_count += 1
                continue
            evaluations.append(await self._evaluate_answer(answer=answer, role=interview.role_title, force=force))

        if evaluations:
            interview.overall_score = self._average_score([evaluation.overall_score for evaluation in evaluations])

        await self.history_repository.create_history(
            {
                "user_id": principal.user.id,
                "interview_id": interview.id,
                "event_type": InterviewHistoryEvent.REPORT_GENERATED.value,
                "event_payload": {
                    "source": "ai_evaluation_engine",
                    "evaluated_count": len(evaluations),
                    "skipped_count": skipped_count,
                },
                "occurred_at": utc_now(),
            }
        )
        await self.session.commit()

        return EvaluateInterviewResponse(
            interview_id=interview.id,
            evaluated_count=len(evaluations),
            skipped_count=skipped_count,
            evaluations=[AnswerEvaluationRead.model_validate(evaluation) for evaluation in evaluations],
        )

    async def list_interview_evaluations(
        self,
        *,
        principal: AuthenticatedPrincipal,
        interview_id: str,
    ) -> EvaluateInterviewResponse:
        interview = await self.repository.get_interview_for_user(interview_id=interview_id, user_id=principal.user.id)
        if not interview:
            raise NotFoundError("Interview not found.")
        evaluations = list(
            await self.repository.list_for_interview(interview_id=interview.id, user_id=principal.user.id)
        )
        return EvaluateInterviewResponse(
            interview_id=interview.id,
            evaluated_count=len(evaluations),
            skipped_count=0,
            evaluations=[AnswerEvaluationRead.model_validate(evaluation) for evaluation in evaluations],
        )

    async def _evaluate_answer(self, *, answer: Answer, role: str | None, force: bool) -> AnswerEvaluation:
        existing = await self.repository.get_existing_for_answer(answer.id)
        if existing and not force:
            return existing

        question = await self.repository.get_question(answer.question_id)
        if not question:
            raise NotFoundError("Question not found for answer.")

        interview = await self.repository.get_interview_for_user(
            interview_id=answer.interview_id,
            user_id=answer.user_id,
        )
        if not interview:
            raise NotFoundError("Interview not found for answer.")

        result = await self.provider.evaluate(
            EvaluationInput(
                role=role or interview.role_title,
                question_prompt=question.prompt,
                question_category=question.category,
                question_difficulty=question.difficulty,
                answer_transcript=answer.transcript,
            )
        )
        values = self._evaluation_values(answer=answer, result=result)

        if existing:
            evaluation = await self.repository.update(existing, values)
        else:
            evaluation = await self.repository.create(values)

        answer.score = result.overall_score
        answer.feedback = {
            "evaluation_id": evaluation.id,
            "overall_score": str(result.overall_score),
            "improvement_suggestions": result.improvement_suggestions,
            "related_topics": result.related_topics,
            "evaluator_version": result.evaluator_version,
        }
        return evaluation

    def _evaluation_values(self, *, answer: Answer, result: EvaluationResult) -> dict:
        return {
            "user_id": answer.user_id,
            "interview_id": answer.interview_id,
            "question_id": answer.question_id,
            "answer_id": answer.id,
            "technical_accuracy": result.technical_accuracy,
            "communication": result.communication,
            "completeness": result.completeness,
            "confidence_score": result.confidence_score,
            "problem_solving": result.problem_solving,
            "explanation_quality": result.explanation_quality,
            "overall_score": result.overall_score,
            "correct_answer": result.correct_answer,
            "better_answer": result.better_answer,
            "industry_standard_answer": result.industry_standard_answer,
            "improvement_suggestions": result.improvement_suggestions,
            "related_topics": result.related_topics,
            "difficulty_analysis": result.difficulty_analysis,
            "evaluator_version": result.evaluator_version,
        }

    def _average_score(self, scores: list[Decimal]) -> Decimal:
        if not scores:
            return Decimal("0.00")
        return (sum(scores) / Decimal(len(scores))).quantize(Decimal("0.01"))
