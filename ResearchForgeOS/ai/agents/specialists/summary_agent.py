from ai.agents.core.base import BaseAgent
from ai.agents.core.types import AgentExecutionContext, AgentOutput, AgentRole
from ai.agents.specialists.helpers import source_refs, summary_by_type


class SummaryAgent(BaseAgent):
    role = AgentRole.SUMMARY
    name = "Summary Agent"
    description = "Generates executive, technical, detailed, one-minute, and five-minute summaries."
    default_priority = 45

    async def run(self, context: AgentExecutionContext) -> AgentOutput:
        document = context.document
        summaries = {
            "executive": summary_by_type(document, "executive"),
            "technical": summary_by_type(document, "technical"),
            "detailed": summary_by_type(document, "detailed"),
            "one_minute": summary_by_type(document, "one_minute"),
            "five_minute": summary_by_type(document, "five_minute"),
        }
        return AgentOutput(
            role=self.role,
            title="Summary Set",
            summary=summaries["executive"][:600],
            confidence_score=0.9,
            data={"summaries": summaries},
            sources=source_refs(document),
        )
