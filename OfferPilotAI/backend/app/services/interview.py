"""Interview planning service."""

from app.domain.enums import InterviewSessionStatus, InterviewType
from app.schemas.interview import InterviewSessionCreate, InterviewSessionRead, InterviewTemplateRead
from app.utils.ids import create_prefixed_id


class InterviewService:
    """Application service for interview session planning."""

    def list_templates(self) -> list[InterviewTemplateRead]:
        return [
            InterviewTemplateRead(
                id="technical-backend",
                name="Technical Backend Interview",
                interview_type=InterviewType.TECHNICAL,
                recommended_duration_minutes=60,
                description="Backend engineering fundamentals, APIs, data modeling, and operational thinking.",
            ),
            InterviewTemplateRead(
                id="system-design",
                name="System Design Interview",
                interview_type=InterviewType.SYSTEM_DESIGN,
                recommended_duration_minutes=60,
                description="Architecture tradeoffs, scalability, reliability, and communication structure.",
            ),
            InterviewTemplateRead(
                id="behavioral",
                name="Behavioral Interview",
                interview_type=InterviewType.BEHAVIORAL,
                recommended_duration_minutes=45,
                description="Experience narratives, collaboration, conflict resolution, and leadership signals.",
            ),
        ]

    def create_session(self, payload: InterviewSessionCreate) -> InterviewSessionRead:
        question_count = max(3, min(12, payload.duration_minutes // 8))
        return InterviewSessionRead(
            id=create_prefixed_id("int"),
            role_title=payload.role_title,
            company_name=payload.company_name,
            seniority=payload.seniority,
            interview_type=payload.interview_type,
            status=InterviewSessionStatus.DRAFT,
            focus_areas=payload.focus_areas,
            duration_minutes=payload.duration_minutes,
            question_count=question_count,
        )
