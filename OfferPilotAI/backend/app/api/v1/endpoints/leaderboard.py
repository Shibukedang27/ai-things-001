"""Leaderboard CRUD endpoints."""

from app.api.crud_router import create_crud_router
from app.schemas.leaderboard import LeaderboardCreate, LeaderboardRead, LeaderboardUpdate
from app.services.resources import LeaderboardCRUDService

router = create_crud_router(
    service_cls=LeaderboardCRUDService,
    create_schema=LeaderboardCreate,
    update_schema=LeaderboardUpdate,
    read_schema=LeaderboardRead,
    resource_name="leaderboard entries",
)
