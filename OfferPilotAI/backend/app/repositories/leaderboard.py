"""Leaderboard repository."""

from app.models import Leaderboard
from app.repositories.base import SQLAlchemyRepository


class LeaderboardRepository(SQLAlchemyRepository[Leaderboard]):
    model = Leaderboard
