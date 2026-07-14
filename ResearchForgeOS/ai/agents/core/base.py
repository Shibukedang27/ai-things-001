from abc import ABC, abstractmethod

from ai.agents.core.types import AgentExecutionContext, AgentOutput, AgentRole


class BaseAgent(ABC):
    role: AgentRole
    name: str
    description: str
    default_priority: int = 50
    timeout_seconds: float = 8.0
    max_retries: int = 2

    @abstractmethod
    async def run(self, context: AgentExecutionContext) -> AgentOutput:
        raise NotImplementedError
