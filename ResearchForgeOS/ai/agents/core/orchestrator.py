from __future__ import annotations

from uuid import uuid4

from ai.agents.core.aggregator import ResponseAggregator
from ai.agents.core.execution import ExecutionPipeline
from ai.agents.core.priority import PriorityManager
from ai.agents.core.registry import AgentRegistry, build_default_registry
from ai.agents.core.task_queue import AgentTaskQueue
from ai.agents.core.types import (
    AgentExecutionContext,
    AgentOutput,
    AgentRole,
    AgentRunResult,
    AgentTaskPayload,
    AgentTaskResult,
    PipelineStatus,
    TaskStatus,
)


class AgentOrchestrator:
    def __init__(
        self,
        *,
        registry: AgentRegistry | None = None,
        priority_manager: PriorityManager | None = None,
        aggregator: ResponseAggregator | None = None,
        execution_pipeline: ExecutionPipeline | None = None,
    ) -> None:
        self.registry = registry or build_default_registry()
        self.priority_manager = priority_manager or PriorityManager()
        self.aggregator = aggregator or ResponseAggregator()
        self.execution_pipeline = execution_pipeline or ExecutionPipeline(self.registry)

    async def run(
        self,
        context: AgentExecutionContext,
        *,
        pipeline_id: str | None = None,
        roles: list[AgentRole] | None = None,
    ) -> AgentRunResult:
        resolved_pipeline_id = pipeline_id or str(uuid4())
        requested_roles = roles or self.priority_manager.ordered_roles()
        queue = AgentTaskQueue()
        task_results: list[AgentTaskResult] = []
        execution_log: list[dict[str, object]] = []
        outputs_by_role: dict[AgentRole, AgentOutput] = {}

        for role in requested_roles:
            agent = self.registry.get(role)
            await queue.put(
                AgentTaskPayload(
                    pipeline_id=resolved_pipeline_id,
                    task_id=str(uuid4()),
                    role=role,
                    priority=self.priority_manager.priority_for(role),
                    timeout_seconds=agent.timeout_seconds,
                    max_retries=agent.max_retries,
                    context=context,
                )
            )

        while not queue.empty():
            payload = await queue.get()
            agent_context = AgentExecutionContext(
                document=context.document,
                dna=context.dna,
                previous_outputs=outputs_by_role,
                request_options=context.request_options,
            )
            payload = AgentTaskPayload(
                pipeline_id=payload.pipeline_id,
                task_id=payload.task_id,
                role=payload.role,
                priority=payload.priority,
                timeout_seconds=payload.timeout_seconds,
                max_retries=payload.max_retries,
                context=agent_context,
            )
            execution_log.append({"event": "task_started", "task_id": payload.task_id, "agent": payload.role.value})
            result = await self.execution_pipeline.execute_task(payload)
            task_results.append(result)
            execution_log.append(
                {
                    "event": "task_finished",
                    "task_id": result.task_id,
                    "agent": result.role.value,
                    "status": result.status.value,
                    "attempts": result.attempts,
                    "duration_ms": result.duration_ms,
                }
            )
            if result.output is not None:
                outputs_by_role[result.role] = result.output

        outputs = list(outputs_by_role.values())
        status = PipelineStatus.COMPLETED
        if any(result.status == TaskStatus.FAILED for result in task_results):
            status = PipelineStatus.FAILED
        final_response = self.aggregator.aggregate(outputs)
        return AgentRunResult(
            pipeline_id=resolved_pipeline_id,
            status=status,
            outputs=outputs,
            final_response=final_response,
            task_results=task_results,
            execution_log=execution_log,
        )
