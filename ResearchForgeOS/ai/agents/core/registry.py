from ai.agents.core.base import BaseAgent
from ai.agents.core.types import AgentRole
from ai.agents.specialists.citation_agent import CitationAgent
from ai.agents.specialists.code_agent import CodeAgent
from ai.agents.specialists.concept_agent import ConceptAgent
from ai.agents.specialists.knowledge_graph_agent import KnowledgeGraphAgent
from ai.agents.specialists.quality_assurance_agent import QualityAssuranceAgent
from ai.agents.specialists.quiz_agent import QuizAgent
from ai.agents.specialists.research_agent import ResearchAgent
from ai.agents.specialists.roadmap_agent import RoadmapAgent
from ai.agents.specialists.summary_agent import SummaryAgent
from ai.agents.specialists.teacher_agent import TeacherAgent


class AgentRegistry:
    def __init__(self) -> None:
        self._agents: dict[AgentRole, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        self._agents[agent.role] = agent

    def get(self, role: AgentRole) -> BaseAgent:
        return self._agents[role]

    def list(self) -> list[BaseAgent]:
        return list(self._agents.values())

    def roles(self) -> list[AgentRole]:
        return list(self._agents.keys())


def build_default_registry() -> AgentRegistry:
    registry = AgentRegistry()
    for agent in (
        ResearchAgent(),
        ConceptAgent(),
        TeacherAgent(),
        CodeAgent(),
        QuizAgent(),
        SummaryAgent(),
        CitationAgent(),
        RoadmapAgent(),
        KnowledgeGraphAgent(),
        QualityAssuranceAgent(),
    ):
        registry.register(agent)
    return registry
