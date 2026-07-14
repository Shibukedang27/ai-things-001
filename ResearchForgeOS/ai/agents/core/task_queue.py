import asyncio
from dataclasses import dataclass, field

from ai.agents.core.types import AgentTaskPayload


@dataclass(order=True)
class PrioritizedTask:
    priority: int
    sequence: int
    payload: AgentTaskPayload = field(compare=False)


class AgentTaskQueue:
    def __init__(self) -> None:
        self._queue: asyncio.PriorityQueue[PrioritizedTask] = asyncio.PriorityQueue()
        self._sequence = 0

    async def put(self, payload: AgentTaskPayload) -> None:
        self._sequence += 1
        await self._queue.put(PrioritizedTask(payload.priority, self._sequence, payload))

    async def get(self) -> AgentTaskPayload:
        item = await self._queue.get()
        return item.payload

    def empty(self) -> bool:
        return self._queue.empty()
