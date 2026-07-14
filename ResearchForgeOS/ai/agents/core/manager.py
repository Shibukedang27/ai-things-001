from ai.agents.core.registry import AgentRegistry, build_default_registry
from ai.agents.core.types import AgentRole, AgentStatus


class AgentManager:
    def __init__(self, registry: AgentRegistry | None = None) -> None:
        self.registry = registry or build_default_registry()

    def status(self) -> list[dict[str, object]]:
        return [
            {
                "role": agent.role.value,
                "name": agent.name,
                "description": agent.description,
                "status": AgentStatus.ACTIVE.value,
                "default_priority": agent.default_priority,
                "timeout_seconds": agent.timeout_seconds,
                "max_retries": agent.max_retries,
            }
            for agent in self.registry.list()
        ]

    def roles(self) -> list[AgentRole]:
        return self.registry.roles()
