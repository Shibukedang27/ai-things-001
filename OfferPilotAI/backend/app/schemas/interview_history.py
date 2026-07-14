"""Interview history API schemas."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.domain.enums import InterviewHistoryEvent
from app.schemas.common import ORMModel


class InterviewHistoryCreate(BaseModel):
    """Request body for interview history creation."""

    user_id: str
    interview_id: str
    event_type: InterviewHistoryEvent = InterviewHistoryEvent.CREATED
    event_payload: dict[str, Any] = Field(default_factory=dict)
    occurred_at: datetime


class InterviewHistoryUpdate(BaseModel):
    """Request body for interview history updates."""

    event_type: InterviewHistoryEvent | None = None
    event_payload: dict[str, Any] | None = None
    occurred_at: datetime | None = None


class InterviewHistoryRead(ORMModel):
    """Persisted interview history response."""

    id: str
    user_id: str
    interview_id: str
    event_type: InterviewHistoryEvent
    event_payload: dict[str, Any]
    occurred_at: datetime
    created_at: datetime
    updated_at: datetime
