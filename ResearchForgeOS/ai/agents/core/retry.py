import asyncio
from collections.abc import Awaitable, Callable
from typing import TypeVar

T = TypeVar("T")


class RetrySystem:
    def __init__(self, base_delay_seconds: float = 0.05) -> None:
        self.base_delay_seconds = base_delay_seconds

    async def run(self, operation: Callable[[], Awaitable[T]], *, max_retries: int) -> tuple[T, int]:
        attempts = 0
        while True:
            attempts += 1
            try:
                result = await operation()
                return result, attempts
            except Exception:
                if attempts > max_retries:
                    raise
                await asyncio.sleep(self.base_delay_seconds * attempts)
