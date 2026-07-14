from functools import lru_cache

from passlib.context import CryptContext

from backend.config import get_settings


@lru_cache(maxsize=1)
def get_password_context() -> CryptContext:
    settings = get_settings()
    return CryptContext(
        schemes=["bcrypt"],
        deprecated="auto",
        bcrypt__rounds=settings.password_hash_rounds,
    )


def hash_password(password: str) -> str:
    return get_password_context().hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return get_password_context().verify(password, hashed_password)
