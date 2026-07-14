from ai.agents.core.types import AgentRole


class PriorityManager:
    PIPELINE_PRIORITIES: dict[AgentRole, int] = {
        AgentRole.RESEARCH: 10,
        AgentRole.CONCEPT: 20,
        AgentRole.TEACHER: 30,
        AgentRole.CODE: 35,
        AgentRole.QUIZ: 40,
        AgentRole.SUMMARY: 45,
        AgentRole.CITATION: 50,
        AgentRole.ROADMAP: 55,
        AgentRole.KNOWLEDGE_GRAPH: 60,
        AgentRole.QUALITY_ASSURANCE: 100,
    }

    def priority_for(self, role: AgentRole) -> int:
        return self.PIPELINE_PRIORITIES[role]

    def ordered_roles(self) -> list[AgentRole]:
        return [
            role
            for role, _ in sorted(self.PIPELINE_PRIORITIES.items(), key=lambda item: item[1])
        ]
