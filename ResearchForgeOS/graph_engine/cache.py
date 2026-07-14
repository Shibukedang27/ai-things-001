from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any


@dataclass
class GraphCacheEntry:
    payload: dict[str, Any]
    expires_at: datetime


class GraphCache:
    def __init__(self, ttl_seconds: int = 120) -> None:
        self.ttl_seconds = ttl_seconds
        self._entries: dict[str, GraphCacheEntry] = {}

    def get(self, key: str) -> dict[str, Any] | None:
        entry = self._entries.get(key)
        if entry is None:
            return None
        if entry.expires_at < datetime.now(UTC):
            self._entries.pop(key, None)
            return None
        return dict(entry.payload)

    def set(self, key: str, payload: dict[str, Any]) -> None:
        self._entries[key] = GraphCacheEntry(
            payload=dict(payload),
            expires_at=datetime.now(UTC) + timedelta(seconds=self.ttl_seconds),
        )

    def invalidate(self, prefix: str | None = None) -> None:
        if prefix is None:
            self._entries.clear()
            return
        for key in [entry_key for entry_key in self._entries if entry_key.startswith(prefix)]:
            self._entries.pop(key, None)
