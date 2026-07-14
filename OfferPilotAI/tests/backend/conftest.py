"""Backend test configuration."""

from pathlib import Path
import sys

import pytest_asyncio
from httpx import ASGITransport, AsyncClient

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_PATH = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_PATH))

from app.core.config import Environment, LogFormat, Settings  # noqa: E402
from app.main import create_app  # noqa: E402


@pytest_asyncio.fixture
async def client() -> AsyncClient:
    settings = Settings(
        environment=Environment.TEST,
        log_format=LogFormat.CONSOLE,
        trusted_hosts=["testserver"],
        readiness_database_check_enabled=False,
    )
    app = create_app(settings)
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as async_client:
        yield async_client
