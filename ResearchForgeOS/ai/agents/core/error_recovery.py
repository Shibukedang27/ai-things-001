import asyncio
from dataclasses import dataclass


@dataclass(frozen=True)
class RecoveryDecision:
    error_type: str
    message: str
    recoverable: bool
    retry_recommended: bool


class ErrorRecovery:
    def evaluate(self, error: Exception, *, attempts: int, max_retries: int) -> RecoveryDecision:
        recoverable = self._is_recoverable(error)
        return RecoveryDecision(
            error_type=error.__class__.__name__,
            message=str(error) or error.__class__.__name__,
            recoverable=recoverable,
            retry_recommended=recoverable and attempts <= max_retries,
        )

    def _is_recoverable(self, error: Exception) -> bool:
        return isinstance(error, TimeoutError | asyncio.TimeoutError | ConnectionError)
