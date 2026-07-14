from ai.agents.core.base import BaseAgent
from ai.agents.core.types import AgentExecutionContext, AgentOutput, AgentRole
from ai.agents.specialists.helpers import dna_or_empty, source_refs


class RoadmapAgent(BaseAgent):
    role = AgentRole.ROADMAP
    name = "Roadmap Agent"
    description = "Generates learning roadmaps, next topics, duration estimates, and project recommendations."
    default_priority = 55

    async def run(self, context: AgentExecutionContext) -> AgentOutput:
        document = context.document
        dna = dna_or_empty(context.dna)
        roadmap = [
            {"order": index + 1, "topic": topic, "goal": f"Master {topic} enough to apply it."}
            for index, topic in enumerate(dna.learning_order[:12])
        ]
        projects = [
            f"Build a mini project demonstrating {topic}."
            for topic in (dna.primary_concepts or document.topics)[:4]
        ]
        return AgentOutput(
            role=self.role,
            title="Learning Roadmap",
            summary=f"Estimated mastery time: {dna.estimated_mastery_time_hours or 'unknown'} hours.",
            confidence_score=0.84,
            data={
                "roadmap": roadmap,
                "next_topics": dna.future_learning_topics,
                "estimated_learning_duration_hours": dna.estimated_mastery_time_hours,
                "recommended_projects": projects,
                "recommended_books": self._books(dna.research_category or document.category),
                "recommended_courses": self._courses(dna.research_category or document.category),
            },
            sources=source_refs(document),
        )

    def _books(self, category: str) -> list[str]:
        if "Artificial Intelligence" in category:
            return ["Deep Learning", "Speech and Language Processing"]
        if "Software" in category:
            return ["Designing Data-Intensive Applications", "Clean Architecture"]
        return ["How to Read a Book", "The Craft of Research"]

    def _courses(self, category: str) -> list[str]:
        if "Artificial Intelligence" in category:
            return ["Machine Learning Specialization", "Deep Learning Specialization"]
        return ["Research Methods", "Technical Writing"]
