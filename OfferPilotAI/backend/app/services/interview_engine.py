"""Interview engine workflows."""

from datetime import timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from app.core.exceptions import AppError, NotFoundError
from app.domain.enums import DifficultyLevel, InterviewHistoryEvent, InterviewStatus, InterviewType, SeniorityLevel
from app.models import Answer, Interview, Question
from app.repositories import InterviewEngineRepository
from app.schemas.interview_engine import (
    CompleteInterviewResponse,
    EngineAnswerRead,
    EngineQuestion,
    EngineQuestionCategory,
    EngineSession,
    EngineTimer,
    StartInterviewRequest,
    StartInterviewResponse,
    SubmitAnswerRequest,
    SubmitAnswerResponse,
    SupportedEngineOptions,
)
from app.services.auth import AuthenticatedPrincipal
from app.services.question_generation import InterviewQuestionGenerator, TemplateAIQuestionGenerator
from app.utils.time import utc_now


class InterviewEngineService:
    """Application service for interview engine sessions."""

    def __init__(
        self,
        session: AsyncSession,
        question_generator: InterviewQuestionGenerator | None = None,
    ) -> None:
        self.session = session
        self.repository = InterviewEngineRepository(session)
        self.question_generator = question_generator or TemplateAIQuestionGenerator()

    def supported_options(self) -> SupportedEngineOptions:
        return SupportedEngineOptions(
            roles_note="Role is free-text so users can target any job title.",
            difficulties=list(DifficultyLevel),
            categories=list(EngineQuestionCategory),
            duration_minutes={"min": 5, "max": 180, "default": 45},
        )

    async def start_interview(
        self,
        *,
        principal: AuthenticatedPrincipal,
        payload: StartInterviewRequest,
    ) -> StartInterviewResponse:
        now = utc_now()
        question_count = self._question_count(payload.duration_minutes, len(payload.categories))
        generated_questions = await self.question_generator.generate(
            role=payload.role,
            difficulty=payload.difficulty,
            categories=payload.categories,
            question_count=question_count,
        )

        interview = await self.repository.create_interview(
            {
                "user_id": principal.user.id,
                "title": f"{payload.role} Interview Practice",
                "role_title": payload.role,
                "seniority": SeniorityLevel.MID.value,
                "interview_type": self._interview_type(payload.categories),
                "status": InterviewStatus.IN_PROGRESS.value,
                "focus_areas": [category.value for category in payload.categories],
                "duration_minutes": payload.duration_minutes,
                "started_at": now,
            }
        )

        questions = await self.repository.create_questions(
            [
                {
                    "interview_id": interview.id,
                    "category": question.category.value,
                    "difficulty": question.difficulty.value,
                    "prompt": question.prompt,
                    "expected_signal": question.expected_signal,
                    "tags": question.tags,
                    "order_index": index,
                    "is_active": True,
                    "rubric": {},
                }
                for index, question in enumerate(generated_questions)
            ]
        )

        await self._history(
            principal=principal,
            interview=interview,
            event_type=InterviewHistoryEvent.CREATED.value,
            payload={
                "role": payload.role,
                "difficulty": payload.difficulty.value,
                "duration_minutes": payload.duration_minutes,
                "categories": [category.value for category in payload.categories],
                "question_count": len(questions),
            },
        )
        await self._history(
            principal=principal,
            interview=interview,
            event_type=InterviewHistoryEvent.STARTED.value,
            payload={"started_at": now.isoformat()},
        )

        await self.session.commit()
        await self.session.refresh(interview)

        session_state = await self._session_state(interview=interview, user_id=principal.user.id)
        return StartInterviewResponse(
            **session_state.model_dump(),
            generated_questions=[self._question_schema(question) for question in questions],
        )

    async def get_session(self, *, principal: AuthenticatedPrincipal, interview_id: str) -> EngineSession:
        interview = await self._get_interview(principal=principal, interview_id=interview_id)
        await self._complete_if_expired(principal=principal, interview=interview)
        return await self._session_state(interview=interview, user_id=principal.user.id)

    async def get_current_question(self, *, principal: AuthenticatedPrincipal, interview_id: str) -> EngineQuestion | None:
        session_state = await self.get_session(principal=principal, interview_id=interview_id)
        return session_state.current_question

    async def submit_answer(
        self,
        *,
        principal: AuthenticatedPrincipal,
        interview_id: str,
        payload: SubmitAnswerRequest,
    ) -> SubmitAnswerResponse:
        interview = await self._get_interview(principal=principal, interview_id=interview_id)
        await self._ensure_answerable(principal=principal, interview=interview)

        questions = list(await self.repository.list_questions(interview.id))
        answers = list(await self.repository.list_answers(interview_id=interview.id, user_id=principal.user.id))
        current_question = self._current_question(questions=questions, answers=answers)

        if not current_question:
            raise AppError(
                "All questions have already been answered.",
                status_code=status.HTTP_409_CONFLICT,
                code="INTERVIEW_ALREADY_ANSWERED",
            )

        if payload.question_id and payload.question_id != current_question.id:
            raise AppError(
                "Answer must be submitted for the current question.",
                status_code=status.HTTP_409_CONFLICT,
                code="QUESTION_SEQUENCE_CONFLICT",
            )

        existing_answer = await self.repository.get_answer_for_question(
            interview_id=interview.id,
            user_id=principal.user.id,
            question_id=current_question.id,
        )
        if existing_answer:
            raise AppError(
                "The current question has already been answered.",
                status_code=status.HTTP_409_CONFLICT,
                code="QUESTION_ALREADY_ANSWERED",
            )

        stored_answer = await self.repository.create_answer(
            {
                "user_id": principal.user.id,
                "interview_id": interview.id,
                "question_id": current_question.id,
                "transcript": payload.answer,
                "duration_seconds": payload.duration_seconds,
                "feedback": {},
                "score": None,
            }
        )
        await self._history(
            principal=principal,
            interview=interview,
            event_type=InterviewHistoryEvent.ANSWER_SUBMITTED.value,
            payload={
                "question_id": current_question.id,
                "category": current_question.category,
                "duration_seconds": payload.duration_seconds,
            },
        )

        updated_answers = list(await self.repository.list_answers(interview_id=interview.id, user_id=principal.user.id))
        if len(updated_answers) >= len(questions):
            interview.status = InterviewStatus.COMPLETED.value
            interview.completed_at = utc_now()
            await self._history(
                principal=principal,
                interview=interview,
                event_type=InterviewHistoryEvent.COMPLETED.value,
                payload={"reason": "all_questions_answered"},
            )

        await self.session.commit()
        await self.session.refresh(stored_answer)
        await self.session.refresh(interview)

        session_state = await self._session_state(interview=interview, user_id=principal.user.id)
        return SubmitAnswerResponse(
            session=session_state,
            stored_answer=self._answer_schema(stored_answer),
            next_question=session_state.current_question,
        )

    async def complete_interview(
        self,
        *,
        principal: AuthenticatedPrincipal,
        interview_id: str,
    ) -> CompleteInterviewResponse:
        interview = await self._get_interview(principal=principal, interview_id=interview_id)
        if interview.status != InterviewStatus.COMPLETED.value:
            interview.status = InterviewStatus.COMPLETED.value
            interview.completed_at = utc_now()
            await self._history(
                principal=principal,
                interview=interview,
                event_type=InterviewHistoryEvent.COMPLETED.value,
                payload={"reason": "manual_completion"},
            )
            await self.session.commit()
            await self.session.refresh(interview)

        answers = list(await self.repository.list_answers(interview_id=interview.id, user_id=principal.user.id))
        return CompleteInterviewResponse(
            session=await self._session_state(interview=interview, user_id=principal.user.id),
            answers=[self._answer_schema(answer) for answer in answers],
        )

    async def _get_interview(self, *, principal: AuthenticatedPrincipal, interview_id: str) -> Interview:
        interview = await self.repository.get_interview_for_user(interview_id=interview_id, user_id=principal.user.id)
        if not interview:
            raise NotFoundError("Interview session not found.")
        return interview

    async def _ensure_answerable(self, *, principal: AuthenticatedPrincipal, interview: Interview) -> None:
        await self._complete_if_expired(principal=principal, interview=interview)
        if interview.status != InterviewStatus.IN_PROGRESS.value:
            raise AppError(
                "Interview is not accepting answers.",
                status_code=status.HTTP_409_CONFLICT,
                code="INTERVIEW_NOT_ACTIVE",
            )

    async def _complete_if_expired(self, *, principal: AuthenticatedPrincipal, interview: Interview) -> None:
        timer = self._timer(interview)
        if timer.expired and interview.status == InterviewStatus.IN_PROGRESS.value:
            interview.status = InterviewStatus.COMPLETED.value
            interview.completed_at = utc_now()
            await self._history(
                principal=principal,
                interview=interview,
                event_type=InterviewHistoryEvent.COMPLETED.value,
                payload={"reason": "timer_expired"},
            )
            await self.session.commit()
            await self.session.refresh(interview)

    async def _session_state(self, *, interview: Interview, user_id: str) -> EngineSession:
        questions = list(await self.repository.list_questions(interview.id))
        answers = list(await self.repository.list_answers(interview_id=interview.id, user_id=user_id))
        current_question = self._current_question(questions=questions, answers=answers)
        return EngineSession(
            id=interview.id,
            role=interview.role_title,
            difficulty=self._difficulty(questions),
            duration_minutes=interview.duration_minutes,
            categories=[EngineQuestionCategory(category) for category in interview.focus_areas],
            status=InterviewStatus(interview.status),
            timer=self._timer(interview),
            total_questions=len(questions),
            answered_questions=len({answer.question_id for answer in answers}),
            current_question=self._question_schema(current_question) if current_question else None,
        )

    def _timer(self, interview: Interview) -> EngineTimer:
        started_at = interview.started_at
        duration_seconds = interview.duration_minutes * 60
        if not started_at:
            return EngineTimer(
                duration_seconds=duration_seconds,
                elapsed_seconds=0,
                remaining_seconds=duration_seconds,
                expired=False,
                started_at=None,
                expires_at=None,
            )

        now = utc_now()
        expires_at = started_at + timedelta(seconds=duration_seconds)
        elapsed_seconds = max(0, int((now - started_at).total_seconds()))
        remaining_seconds = max(0, duration_seconds - elapsed_seconds)
        return EngineTimer(
            duration_seconds=duration_seconds,
            elapsed_seconds=elapsed_seconds,
            remaining_seconds=remaining_seconds,
            expired=remaining_seconds == 0,
            started_at=started_at,
            expires_at=expires_at,
        )

    def _current_question(self, *, questions: list[Question], answers: list[Answer]) -> Question | None:
        answered_question_ids = {answer.question_id for answer in answers}
        for question in questions:
            if question.id not in answered_question_ids:
                return question
        return None

    def _question_schema(self, question: Question) -> EngineQuestion:
        return EngineQuestion(
            id=question.id,
            category=EngineQuestionCategory(question.category),
            difficulty=question.difficulty,
            prompt=question.prompt,
            order_index=question.order_index,
        )

    def _answer_schema(self, answer: Answer) -> EngineAnswerRead:
        return EngineAnswerRead(
            id=answer.id,
            question_id=answer.question_id,
            transcript=answer.transcript,
            duration_seconds=answer.duration_seconds,
            submitted_at=answer.created_at,
        )

    def _difficulty(self, questions: list[Question]):
        if not questions:
            return DifficultyLevel.MEDIUM
        return questions[0].difficulty

    def _question_count(self, duration_minutes: int, category_count: int) -> int:
        duration_based_count = max(3, duration_minutes // 5)
        return max(category_count, min(20, duration_based_count))

    def _interview_type(self, categories: list[EngineQuestionCategory]) -> str:
        if categories == [EngineQuestionCategory.BEHAVIORAL]:
            return InterviewType.BEHAVIORAL.value
        if categories == [EngineQuestionCategory.SYSTEM_DESIGN]:
            return InterviewType.SYSTEM_DESIGN.value
        return InterviewType.MIXED.value

    async def _history(
        self,
        *,
        principal: AuthenticatedPrincipal,
        interview: Interview,
        event_type: str,
        payload: dict,
    ) -> None:
        await self.repository.create_history(
            {
                "user_id": principal.user.id,
                "interview_id": interview.id,
                "event_type": event_type,
                "event_payload": payload,
                "occurred_at": utc_now(),
            }
        )
