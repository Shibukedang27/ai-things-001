from knowledge_engine.dna.types import (
    DNADocumentInput,
    DNAGraphEdge,
    DNAGraphNode,
    KnowledgeDNAResult,
)
from knowledge_engine.dna.utils import normalize_key


class KnowledgeGraphBuilder:
    def build_nodes(self, document: DNADocumentInput, partial: KnowledgeDNAResult) -> list[DNAGraphNode]:
        nodes = [
            DNAGraphNode(
                stable_key=f"document:{document.id}",
                node_type="document",
                name=document.title,
                label=document.title,
                description=f"Knowledge DNA profile for {document.title}.",
                importance_score=partial.knowledge_score,
                metadata={"category": partial.research_category, "difficulty": partial.difficulty_level},
            )
        ]

        for name in partial.primary_concepts:
            nodes.append(self._node("concept", name, 0.88, "Primary concept"))
        for name in partial.secondary_concepts:
            nodes.append(self._node("concept", name, 0.68, "Secondary concept"))
        for name in partial.algorithms:
            nodes.append(self._node("algorithm", name, 0.76, "Detected algorithm"))
        for name in partial.technologies_used:
            nodes.append(self._node("technology", name, 0.74, "Detected technology"))
        for name in partial.programming_languages:
            nodes.append(self._node("programming_language", name, 0.72, "Programming language"))
        for name in partial.frameworks:
            nodes.append(self._node("framework", name, 0.72, "Framework"))
        for name in partial.libraries:
            nodes.append(self._node("library", name, 0.7, "Library"))
        for name in partial.research_papers:
            nodes.append(self._node("research_paper", name, 0.66, "Referenced research paper"))
        for name in partial.datasets:
            nodes.append(self._node("dataset", name, 0.6, "Detected dataset"))
        for related in partial.related_documents:
            nodes.append(
                DNAGraphNode(
                    stable_key=f"document:{related.id}",
                    node_type="document",
                    name=related.title,
                    label=related.title,
                    description=f"Related document in {related.category}.",
                    importance_score=related.similarity_score,
                    metadata={"shared_signals": related.shared_signals},
                )
            )

        deduped: dict[str, DNAGraphNode] = {}
        for node in nodes:
            deduped[node.stable_key] = node
        return list(deduped.values())

    def build_edges(self, document: DNADocumentInput, partial: KnowledgeDNAResult) -> list[DNAGraphEdge]:
        document_key = f"document:{document.id}"
        edges: list[DNAGraphEdge] = []
        for concept in partial.primary_concepts:
            edges.append(self._edge(document_key, self._key("concept", concept), "has_primary_concept", 0.9))
        for concept in partial.secondary_concepts:
            edges.append(self._edge(document_key, self._key("concept", concept), "has_secondary_concept", 0.72))
        for prerequisite in partial.prerequisites:
            target = partial.primary_concepts[0] if partial.primary_concepts else document.title
            edges.append(
                self._edge(
                    self._key("concept", prerequisite),
                    self._key("concept", target),
                    "prerequisite_for",
                    0.7,
                )
            )
        for topic in partial.future_learning_topics:
            source = partial.primary_concepts[0] if partial.primary_concepts else document.title
            edges.append(self._edge(self._key("concept", source), self._key("concept", topic), "next_learn", 0.66))
        for technology in partial.technologies_used:
            edges.append(self._edge(document_key, self._key("technology", technology), "uses_technology", 0.74))
        for algorithm in partial.algorithms:
            edges.append(self._edge(document_key, self._key("algorithm", algorithm), "discusses_algorithm", 0.72))
        for related in partial.related_documents:
            edges.append(
                DNAGraphEdge(
                    source_key=document_key,
                    target_key=f"document:{related.id}",
                    edge_type="related_document",
                    weight=related.similarity_score,
                    confidence_score=related.similarity_score,
                    description=f"{document.title} is related to {related.title}.",
                    metadata={"shared_signals": related.shared_signals},
                )
            )
        return edges[:120]

    def _node(self, node_type: str, name: str, score: float, description: str) -> DNAGraphNode:
        return DNAGraphNode(
            stable_key=self._key(node_type, name),
            node_type=node_type,
            name=name,
            label=name,
            description=description,
            importance_score=score,
        )

    def _edge(self, source_key: str, target_key: str, edge_type: str, weight: float) -> DNAGraphEdge:
        return DNAGraphEdge(
            source_key=source_key,
            target_key=target_key,
            edge_type=edge_type,
            weight=weight,
            confidence_score=weight,
            description=f"{source_key} {edge_type.replace('_', ' ')} {target_key}.",
        )

    def _key(self, node_type: str, name: str) -> str:
        return f"{node_type}:{normalize_key(name)}"
