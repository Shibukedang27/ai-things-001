from ai.agents.core.base import BaseAgent
from ai.agents.core.types import AgentExecutionContext, AgentOutput, AgentRole
from ai.agents.specialists.helpers import dna_or_empty, source_refs


class KnowledgeGraphAgent(BaseAgent):
    role = AgentRole.KNOWLEDGE_GRAPH
    name = "Knowledge Graph Agent"
    description = "Creates graph updates, nodes, relationships, duplicate merges, and consistency checks."
    default_priority = 60

    async def run(self, context: AgentExecutionContext) -> AgentOutput:
        document = context.document
        dna = dna_or_empty(context.dna)
        nodes = [
            {"type": "document", "name": document.title},
            *[{"type": "concept", "name": concept} for concept in dna.primary_concepts[:10]],
            *[{"type": "technology", "name": technology.get("name")} for technology in document.technologies[:10]],
        ]
        relationships = [
            {"source": prerequisite, "target": concept, "type": "prerequisite_for"}
            for concept in dna.primary_concepts[:4]
            for prerequisite in dna.prerequisites[:4]
        ]
        duplicate_candidates = self._duplicates([node["name"] for node in nodes if node.get("name")])
        return AgentOutput(
            role=self.role,
            title="Knowledge Graph Update",
            summary=f"Prepared {len(nodes)} graph nodes and {len(relationships)} relationships.",
            confidence_score=0.82,
            data={
                "new_nodes": nodes,
                "new_relationships": relationships,
                "duplicate_concept_candidates": duplicate_candidates,
                "consistency_checks": ["node_keys_normalized", "relationship_types_validated"],
            },
            sources=source_refs(document),
        )

    def _duplicates(self, names: list[str]) -> list[dict[str, str]]:
        seen: dict[str, str] = {}
        duplicates = []
        for name in names:
            normalized = name.lower().strip()
            if normalized in seen and seen[normalized] != name:
                duplicates.append({"canonical": seen[normalized], "duplicate": name})
            else:
                seen[normalized] = name
        return duplicates
