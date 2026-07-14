from ai.agents.core.base import BaseAgent
from ai.agents.core.types import AgentExecutionContext, AgentOutput, AgentRole
from ai.agents.specialists.helpers import dna_or_empty, source_refs, technology_names


class CodeAgent(BaseAgent):
    role = AgentRole.CODE
    name = "Code Agent"
    description = "Generates implementation examples, API examples, SQL, and algorithm explanations."
    default_priority = 35

    async def run(self, context: AgentExecutionContext) -> AgentOutput:
        document = context.document
        dna = dna_or_empty(context.dna)
        main_concept = (dna.primary_concepts or document.topics or [document.title])[0]
        examples = {
            "python": self._python_example(main_concept),
            "java": self._java_example(main_concept),
            "sql": self._sql_example(document.title),
            "api": self._api_example(document.id),
            "algorithm_notes": [
                {"name": algorithm, "explanation": f"{algorithm} appears as an implementation-relevant algorithm."}
                for algorithm in document.algorithms[:6]
            ],
        }
        return AgentOutput(
            role=self.role,
            title="Implementation Layer",
            summary=f"Generated code and implementation guidance for {main_concept}.",
            confidence_score=0.8,
            data={
                "technologies": technology_names(document, 10),
                "implementation_complexity": dna.implementation_complexity,
                "examples": examples,
                "optimization_notes": self._optimization_notes(document, dna),
            },
            sources=source_refs(document),
        )

    def _python_example(self, concept: str) -> str:
        return f"def explain_{self._identifier(concept)}() -> str:\n    return 'Implement the core idea: {concept}'"

    def _java_example(self, concept: str) -> str:
        name = self._identifier(concept).title().replace("_", "")
        return f"public final class {name}Example {{ public String explain() {{ return \"{concept}\"; }} }}"

    def _sql_example(self, title: str) -> str:
        escaped_title = title.replace("'", "''")
        return f"SELECT * FROM documents WHERE title = '{escaped_title}';"

    def _api_example(self, document_id: str) -> str:
        return f"GET /api/v1/documents/{document_id}"

    def _optimization_notes(self, document, dna) -> list[str]:
        notes = []
        if document.code_snippets:
            notes.append("Review extracted code snippets for complexity, clarity, and error handling.")
        if dna.implementation_complexity and dna.implementation_complexity > 0.65:
            notes.append("Prototype the implementation in small modules before optimizing.")
        return notes or ["Start with a minimal implementation and add tests before optimizing."]

    def _identifier(self, value: str) -> str:
        return "_".join(part.lower() for part in value.split() if part.isalnum()) or "concept"
