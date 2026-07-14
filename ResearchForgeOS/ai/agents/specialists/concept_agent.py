from ai.agents.core.base import BaseAgent
from ai.agents.core.types import AgentExecutionContext, AgentOutput, AgentRole
from ai.agents.specialists.helpers import dna_or_empty, source_refs


class ConceptAgent(BaseAgent):
    role = AgentRole.CONCEPT
    name = "Concept Agent"
    description = "Extracts concepts, definitions, prerequisites, and concept hierarchy."
    default_priority = 20

    async def run(self, context: AgentExecutionContext) -> AgentOutput:
        document = context.document
        dna = dna_or_empty(context.dna)
        hierarchy = [
            {"parent": parent, "children": dna.primary_concepts[:4]}
            for parent in dna.parent_topics[:5]
        ]
        concept_details = [
            {
                "name": concept.get("name"),
                "type": concept.get("concept_type"),
                "difficulty": concept.get("difficulty_level"),
                "prerequisites": concept.get("prerequisites", []),
                "dependencies": concept.get("dependencies", []),
            }
            for concept in document.concepts[:16]
        ]
        return AgentOutput(
            role=self.role,
            title="Concept Map",
            summary=f"Found {len(document.concepts)} concepts and {len(dna.prerequisites)} prerequisite signals.",
            confidence_score=0.87,
            data={
                "core_concepts": dna.primary_concepts or [item["name"] for item in concept_details[:8]],
                "secondary_concepts": dna.secondary_concepts,
                "definitions": document.definitions[:12],
                "relationships": document.concepts[:12],
                "hierarchy": hierarchy,
                "prerequisites": dna.prerequisites,
            },
            sources=source_refs(document),
        )
