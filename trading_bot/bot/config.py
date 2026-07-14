"""Application configuration loaded from environment variables."""

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

from bot.exceptions import AuthenticationError


DEFAULT_TESTNET_URL = "https://testnet.binancefuture.com/fapi"
PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = PROJECT_ROOT / "logs"


@dataclass(frozen=True, slots=True)
class Settings:
    """Runtime settings required to connect to Binance Futures Testnet."""

    api_key: str
    api_secret: str
    testnet_url: str = DEFAULT_TESTNET_URL
    request_timeout_seconds: int = 10
    max_retries: int = 3
    retry_backoff_seconds: float = 0.75


def load_settings(env_file: Path | None = None, require_credentials: bool = True) -> Settings:
    """Load bot settings from a .env file and process environment."""

    dotenv_path = env_file or PROJECT_ROOT / ".env"
    load_dotenv(dotenv_path=dotenv_path)

    api_key = os.getenv("API_KEY", "").strip()
    api_secret = os.getenv("API_SECRET", "").strip()
    testnet_url = os.getenv("TESTNET_URL", DEFAULT_TESTNET_URL).strip()
    if not testnet_url:
        testnet_url = DEFAULT_TESTNET_URL

    if require_credentials and (not api_key or not api_secret):
        raise AuthenticationError(
            "API credentials are missing. Add API_KEY and API_SECRET to trading_bot/.env."
        )

    return Settings(
        api_key=api_key,
        api_secret=api_secret,
        testnet_url=testnet_url.rstrip("/"),
    )
