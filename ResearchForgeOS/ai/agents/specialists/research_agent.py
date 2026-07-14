from ai.agents.core.base import BaseAgent
from ai.agents.core.types import AgentExecutionContext, AgentOutput, AgentRole
from ai.agents.specialists.helpers import concept_names, dna_or_empty, first_items, source_refs, summary_by_type


class ResearchAgent(BaseAgent):
    role = AgentRole.RESEARCH
    name = "Research Agent"
    description = "Understands overall document context, purpose, and important sections."
    default_priority = 10

    async def run(self, context: AgentExecutionContext) -> AgentOutput:
        document = context.document
        dna = dna_or_empty(context.dna)
        overview = summary_by_type(document, "executive", document.cleaned_text[:700])
        purpose = self._purpose(document, dna)
        important_sections = first_items([*document.topics, *concept_names(document, 8)], 10)
        return AgentOutput(
            role=self.role,
            title="Research Overview",
            summary=f"{document.title} is a {document.category} source focused on {', '.join(important_sections[:4])}.",
            confidence_score=0.88,
            data={
                "document_purpose": purpose,
                "overview": overview,
                "important_sections": important_sections,
                "research_category": dna.research_category or document.category,
                "difficulty": document.difficulty,
                "estimated_reading_time_minutes": document.estimated_reading_time_minutes,
            },
            sources=source_refs(document),
        )

    def _purpose(self, document, dna) -> str:
        if dna.primary_concepts:
            return f"Explain and organize the knowledge around {', '.join(dna.primary_concepts[:4])}."
        if document.topics:
            return f"Introduce and connect the topics {', '.join(document.topics[:4])}."
        return "Provide structured understanding of the uploaded knowledge source."
