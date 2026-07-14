"""Session API schemas."""

from datetime import datetime

from pydantic import BaseModel, Field

from app.domain.enums import SessionStatus
from app.schemas.common import ORMModel


class SessionCreate(BaseModel):
    """Request body for session creation."""

    user_id: str
    token_jti: str = Field(..., min_length=8, max_length=128)
    status: SessionStatus = SessionStatus.ACTIVE
    ip_address: str | None = Field(default=None, max_length=64)
    user_agent: str | None = Field(default=None, max_length=512)
    expires_at: datetime
    revoked_at: datetime | None = None


class SessionUpdate(BaseModel):
    """Request body for session updates."""

    status: SessionStatus | None = None
    ip_address: str | None = Field(default=None, max_length=64)
    user_agent: str | None = Field(default=None, max_length=512)
    expires_at: datetime | None = None
    revoked_at: datetime | None = None


class SessionRead(ORMModel):
    """Persisted session response."""

    id: str
    user_id: str
    token_jti: str
    status: SessionStatus
    ip_address: str | None
    user_agent: str | None
    expires_at: datetime
    revoked_at: datetime | None
    created_at: datetime
    updated_at: datetime
