from graph_engine.types import GraphNodeType, GraphRelationshipType
from graph_engine.utils import clamp, node_size


class NodeScorer:
    TYPE_BASE = {
        GraphNodeType.DOCUMENT.value: 0.9,
        GraphNodeType.CONCEPT.value: 0.72,
        GraphNodeType.RESEARCH_PAPER.value: 0.68,
        GraphNodeType.ALGORITHM.value: 0.7,
        GraphNodeType.TECHNOLOGY.value: 0.66,
        GraphNodeType.PROGRAMMING_LANGUAGE.value: 0.64,
        GraphNodeType.FRAMEWORK.value: 0.62,
        GraphNodeType.LIBRARY.value: 0.6,
        GraphNodeType.DATASET.value: 0.58,
        GraphNodeType.AUTHOR.value: 0.54,
        GraphNodeType.COMPANY.value: 0.55,
        GraphNodeType.UNIVERSITY.value: 0.55,
        GraphNodeType.INTERVIEW_TOPIC.value: 0.62,
    }

    def score(self, node_type: str, *, confidence: float, signal_count: int = 1, dna_boost: float = 0.0) -> float:
        base = self.TYPE_BASE.get(node_type, 0.5)
        signal_boost = min(0.16, signal_count * 0.025)
        return round(clamp(base * 0.62 + confidence * 0.28 + signal_boost + dna_boost), 4)

    def size(self, node_type: str, importance_score: float) -> float:
        return node_size(importance_score, node_type)


class EdgeScorer:
    TYPE_BASE = {
        GraphRelationshipType.PREREQUISITE.value: 0.86,
        GraphRelationshipType.DEPENDS_ON.value: 0.82,
        GraphRelationshipType.REQUIRES.value: 0.8,
        GraphRelationshipType.EXPLAINS.value: 0.76,
        GraphRelationshipType.USES.value: 0.7,
        GraphRelationshipType.IMPLEMENTS.value: 0.72,
        GraphRelationshipType.REFERENCED_BY.value: 0.66,
        GraphRelationshipType.RELATED_TO.value: 0.58,
        GraphRelationshipType.SUPPORTS.value: 0.68,
        GraphRelationshipType.CONTRADICTS.value: 0.74,
    }

    def score(self, relationship_type: str, *, confidence: float, evidence_count: int = 1) -> float:
        base = self.TYPE_BASE.get(relationship_type, 0.56)
        evidence_boost = min(0.14, evidence_count * 0.025)
        return round(clamp(base * 0.58 + confidence * 0.34 + evidence_boost), 4)
