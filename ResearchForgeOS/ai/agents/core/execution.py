import asyncio
import time

from ai.agents.core.error_recovery import ErrorRecovery
from ai.agents.core.registry import AgentRegistry
from ai.agents.core.retry import RetrySystem
from ai.agents.core.types import AgentOutput, AgentTaskPayload, AgentTaskResult, TaskStatus


class ExecutionPipeline:
    def __init__(
        self,
        registry: AgentRegistry,
        retry_system: RetrySystem | None = None,
        error_recovery: ErrorRecovery | None = None,
    ) -> None:
        self.registry = registry
        self.retry_system = retry_system or RetrySystem()
        self.error_recovery = error_recovery or ErrorRecovery()

    async def execute_task(self, payload: AgentTaskPayload) -> AgentTaskResult:
        agent = self.registry.get(payload.role)
        started_at = time.perf_counter()

        async def run_agent() -> AgentOutput:
            return await asyncio.wait_for(agent.run(payload.context), timeout=payload.timeout_seconds)

        try:
            output, attempts = await self.retry_system.run(run_agent, max_retries=payload.max_retries)
            status = TaskStatus.COMPLETED
            error_message = None
        except Exception as exc:
            output = None
            attempts = payload.max_retries + 1
            recovery = self.error_recovery.evaluate(exc, attempts=attempts, max_retries=payload.max_retries)
            status = TaskStatus.FAILED
            error_message = f"{recovery.error_type}: {recovery.message}"

        duration_ms = round((time.perf_counter() - started_at) * 1000)
        return AgentTaskResult(
            task_id=payload.task_id,
            role=payload.role,
            status=status,
            output=output,
            attempts=attempts,
            duration_ms=duration_ms,
            error_message=error_message,
        )
