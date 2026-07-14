"""Leaderboard API schemas."""

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.enums import LeaderboardPeriod
from app.schemas.common import ORMModel


class LeaderboardCreate(BaseModel):
    """Request body for leaderboard entry creation."""

    user_id: str
    period: LeaderboardPeriod = LeaderboardPeriod.WEEKLY
    rank: int = Field(..., ge=1)
    score: Decimal = Field(default=0, ge=0)
    percentile: Decimal | None = Field(default=None, ge=0, le=100)
    interviews_completed: int = Field(default=0, ge=0)


class LeaderboardUpdate(BaseModel):
    """Request body for leaderboard entry updates."""

    period: LeaderboardPeriod | None = None
    rank: int | None = Field(default=None, ge=1)
    score: Decimal | None = Field(default=None, ge=0)
    percentile: Decimal | None = Field(default=None, ge=0, le=100)
    interviews_completed: int | None = Field(default=None, ge=0)


class LeaderboardRead(ORMModel):
    """Persisted leaderboard entry response."""

    id: str
    user_id: str
    period: LeaderboardPeriod
    rank: int
    score: Decimal
    percentile: Decimal | None
    interviews_completed: int
    created_at: datetime
    updated_at: datetime
