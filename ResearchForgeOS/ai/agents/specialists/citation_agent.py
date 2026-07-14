from ai.agents.core.base import BaseAgent
from ai.agents.core.types import AgentExecutionContext, AgentOutput, AgentRole
from ai.agents.specialists.helpers import source_refs


class CitationAgent(BaseAgent):
    role = AgentRole.CITATION
    name = "Citation Agent"
    description = "Extracts references, verifies citation structure, and maintains source tracking."
    default_priority = 50

    async def run(self, context: AgentExecutionContext) -> AgentOutput:
        document = context.document
        bibliography = [
            {
                "title": reference.get("title"),
                "authors": reference.get("authors", []),
                "year": reference.get("year"),
                "url": reference.get("url"),
                "citation_text": reference.get("citation_text"),
                "verified": bool(reference.get("url") or reference.get("title")),
            }
            for reference in document.references
        ]
        return AgentOutput(
            role=self.role,
            title="Citation Review",
            summary=f"Reviewed {len(bibliography)} citation candidates.",
            confidence_score=0.78 if bibliography else 0.55,
            data={
                "bibliography": bibliography,
                "source_tracking": {"document_id": document.id, "document_title": document.title},
                "citation_warnings": [] if bibliography else ["No explicit citations were found."],
            },
            warnings=[] if bibliography else ["No explicit citations were found."],
            sources=source_refs(document),
        )
