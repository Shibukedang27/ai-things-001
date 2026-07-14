from ai.agents.core.base import BaseAgent
from ai.agents.core.types import AgentExecutionContext, AgentOutput, AgentRole
from ai.agents.specialists.helpers import source_refs


class QualityAssuranceAgent(BaseAgent):
    role = AgentRole.QUALITY_ASSURANCE
    name = "Quality Assurance Agent"
    description = "Reviews all agent outputs, removes duplicates, detects inconsistencies, and validates clarity."
    default_priority = 100

    async def run(self, context: AgentExecutionContext) -> AgentOutput:
        document = context.document
        outputs = list(context.previous_outputs.values())
        warnings = [warning for output in outputs for warning in output.warnings]
        duplicate_titles = self._duplicates([output.title for output in outputs])
        average_confidence = round(
            sum(output.confidence_score for output in outputs) / max(1, len(outputs)),
            4,
        )
        validation_status = "passed" if average_confidence >= 0.65 and not duplicate_titles else "review_needed"
        summary = (
            f"Reviewed {len(outputs)} agent outputs for {document.title}. "
            f"Validation status: {validation_status}."
        )
        return AgentOutput(
            role=self.role,
            title="Quality Review",
            summary=summary,
            confidence_score=max(0.6, average_confidence),
            data={
                "validation_status": validation_status,
                "average_confidence": average_confidence,
                "duplicate_sections": duplicate_titles,
                "warnings": warnings,
                "clarity_improvements": self._clarity_improvements(outputs),
            },
            warnings=warnings,
            sources=source_refs(document),
        )

    def _duplicates(self, values: list[str]) -> list[str]:
        seen: set[str] = set()
        duplicates: list[str] = []
        for value in values:
            key = value.lower()
            if key in seen:
                duplicates.append(value)
            seen.add(key)
        return duplicates

    def _clarity_improvements(self, outputs) -> list[str]:
        improvements = []
        if not any(output.role == AgentRole.CITATION for output in outputs):
            improvements.append("Run citation review before using claims externally.")
        if not any(output.role == AgentRole.QUIZ for output in outputs):
            improvements.append("Add practice questions to improve retention.")
        return improvements
