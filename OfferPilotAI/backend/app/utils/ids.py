"""Identifier helpers."""

from uuid import uuid4


def create_id() -> str:
    """Create a generic UUID string."""

    return str(uuid4())


def create_prefixed_id(prefix: str) -> str:
    """Create a readable prefixed identifier."""

    safe_prefix = prefix.strip().lower().replace("_", "-")
    return f"{safe_prefix}_{uuid4().hex}"
