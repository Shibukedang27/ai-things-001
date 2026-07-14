from ai.agents.core.base import BaseAgent
from ai.agents.core.types import AgentExecutionContext, AgentOutput, AgentRole
from ai.agents.specialists.helpers import concept_names, dna_or_empty, source_refs


class TeacherAgent(BaseAgent):
    role = AgentRole.TEACHER
    name = "Teacher Agent"
    description = "Explains difficult concepts at beginner, intermediate, and expert levels."
    default_priority = 30

    async def run(self, context: AgentExecutionContext) -> AgentOutput:
        document = context.document
        dna = dna_or_empty(context.dna)
        concepts = dna.primary_concepts or concept_names(document, 5)
        explanations = {
            concept: {
                "beginner": f"{concept} is one of the main ideas to understand before using this source well.",
                "intermediate": (
                    f"{concept} connects to {', '.join(dna.prerequisites[:3]) or 'the surrounding concepts'}."
                ),
                "expert": f"{concept} should be evaluated through tradeoffs, dependencies, and implementation limits.",
                "analogy": f"Think of {concept} as a structural beam in the document's knowledge architecture.",
            }
            for concept in concepts[:6]
        }
        return AgentOutput(
            role=self.role,
            title="Teaching Layer",
            summary=f"Generated layered explanations for {len(explanations)} important concepts.",
            confidence_score=0.84,
            data={"explanations": explanations, "recommended_teaching_order": dna.learning_order[:10]},
            sources=source_refs(document),
        )
