from ai.agents.core.base import BaseAgent
from ai.agents.core.types import AgentExecutionContext, AgentOutput, AgentRole
from ai.agents.specialists.helpers import concept_names, dna_or_empty, source_refs


class QuizAgent(BaseAgent):
    role = AgentRole.QUIZ
    name = "Quiz Agent"
    description = "Creates MCQs, coding questions, interview questions, flashcards, and exercises."
    default_priority = 40

    async def run(self, context: AgentExecutionContext) -> AgentOutput:
        document = context.document
        dna = dna_or_empty(context.dna)
        concepts = dna.primary_concepts or concept_names(document, 8)
        mcqs = [
            {
                "question": f"What is the role of {concept} in this document?",
                "options": ["Core concept", "Unrelated detail", "Formatting artifact", "Citation only"],
                "answer": "Core concept",
            }
            for concept in concepts[:6]
        ]
        flashcards = [
            {"front": f"Explain {concept}", "back": f"{concept} is part of the source's knowledge DNA."}
            for concept in concepts[:8]
        ]
        return AgentOutput(
            role=self.role,
            title="Practice Layer",
            summary=f"Generated {len(mcqs)} MCQs and {len(flashcards)} flashcards.",
            confidence_score=0.82,
            data={
                "mcqs": mcqs,
                "coding_questions": [f"Implement a small example that demonstrates {concepts[0]}." if concepts else ""],
                "interview_questions": [
                    f"How would you explain {concept} in an interview?" for concept in concepts[:6]
                ],
                "flashcards": flashcards,
                "practice_exercises": [
                    f"Draw a relationship map for {concepts[0]}." if concepts else "Summarize the source."
                ],
            },
            sources=source_refs(document),
        )
