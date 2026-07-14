from typing import Any

from ai.agents.core.types import AgentOutput, AgentRole


class ResponseAggregator:
    def aggregate(self, outputs: list[AgentOutput]) -> dict[str, Any]:
        output_by_role = {output.role: output for output in outputs}
        qa = output_by_role.get(AgentRole.QUALITY_ASSURANCE)
        ordered_sections = [
            output
            for output in outputs
            if output.role != AgentRole.QUALITY_ASSURANCE
        ]
        confidence_values = [output.confidence_score for output in outputs if output.confidence_score >= 0]
        final_confidence = round(sum(confidence_values) / max(1, len(confidence_values)), 4)
        return {
            "title": "Multi-Agent Research Analysis",
            "final_confidence": final_confidence,
            "executive_answer": qa.summary if qa else self._fallback_summary(ordered_sections),
            "sections": [
                {
                    "agent": output.role.value,
                    "title": output.title,
                    "summary": output.summary,
                    "confidence_score": output.confidence_score,
                    "data": output.data,
                    "warnings": output.warnings,
                    "sources": output.sources,
                }
                for output in ordered_sections
            ],
            "quality_review": qa.data if qa else {"status": "not_run"},
        }

    def _fallback_summary(self, outputs: list[AgentOutput]) -> str:
        if not outputs:
            return "No agent outputs were produced."
        return " ".join(output.summary for output in outputs[:3])
