"""Validation helpers shared by schemas and services."""

import re

SLUG_PATTERN = re.compile(r"[^a-z0-9-]+")


def to_slug(value: str) -> str:
    """Normalize a human-readable string into a URL-friendly slug."""

    lowered = value.strip().lower().replace("_", "-").replace(" ", "-")
    return SLUG_PATTERN.sub("", lowered).strip("-")
