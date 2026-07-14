from graph_engine.scoring import EdgeScorer
from graph_engine.types import GraphBuildInput, GraphEdgeDraft, GraphNodeType, GraphRelationshipType
from graph_engine.utils import stable_edge_key, stable_node_key


class RelationshipGenerator:
    def __init__(self, scorer: EdgeScorer | None = None) -> None:
        self.scorer = scorer or EdgeScorer()

    def generate(self, graph_input: GraphBuildInput) -> list[GraphEdgeDraft]:
        document = graph_input.document
        dna = document.dna
        document_key = stable_node_key(GraphNodeType.DOCUMENT.value, document.title, document_id=document.id)
        edges: list[GraphEdgeDraft] = []

        if document.author:
            edges.append(
                self._edge(
                    stable_node_key(GraphNodeType.AUTHOR.value, document.author),
                    document_key,
                    GraphRelationshipType.INTRODUCED_BY.value,
                    f"{document.author} introduced or authored {document.title}.",
                    confidence=0.72,
                    source_document_id=document.id,
                )
            )

        for concept in document.concepts:
            concept_key = stable_node_key(GraphNodeType.CONCEPT.value, concept.name)
            edges.append(
                self._edge(
                    document_key,
                    concept_key,
                    GraphRelationshipType.EXPLAINS.value,
                    f"{document.title} explains {concept.name}.",
                    confidence=concept.confidence_score,
                    source_document_id=document.id,
                )
            )
            for prerequisite in concept.prerequisites:
                edges.append(
                    self._edge(
                        stable_node_key(GraphNodeType.CONCEPT.value, prerequisite),
                        concept_key,
                        GraphRelationshipType.PREREQUISITE.value,
                        f"{prerequisite} is a prerequisite for {concept.name}.",
                        confidence=0.72,
                        source_document_id=document.id,
                    )
                )
            for dependency in concept.dependencies:
                edges.append(
                    self._edge(
                        concept_key,
                        stable_node_key(GraphNodeType.CONCEPT.value, dependency),
                        GraphRelationshipType.DEPENDS_ON.value,
                        f"{concept.name} depends on {dependency}.",
                        confidence=0.68,
                        source_document_id=document.id,
                    )
                )

        for topic in document.topics:
            edges.append(
                self._edge(
                    document_key,
                    stable_node_key(GraphNodeType.CONCEPT.value, topic),
                    GraphRelationshipType.RELATED_TO.value,
                    f"{document.title} is related to {topic}.",
                    confidence=0.62,
                    source_document_id=document.id,
                )
            )

        for keyword in document.keywords[:16]:
            edges.append(
                self._edge(
                    document_key,
                    stable_node_key(GraphNodeType.INTERVIEW_TOPIC.value, keyword),
                    GraphRelationshipType.SUPPORTS.value,
                    f"{document.title} supports interview preparation for {keyword}.",
                    confidence=0.56,
                    source_document_id=document.id,
                )
            )

        for technology in document.technologies:
            technology_key = stable_node_key(
                self._technology_node_type(technology.category, technology.name),
                technology.name,
            )
            edges.append(
                self._edge(
                    document_key,
                    technology_key,
                    GraphRelationshipType.USES.value,
                    f"{document.title} uses or discusses {technology.name}.",
                    confidence=technology.confidence_score,
                    source_document_id=document.id,
                )
            )

        for algorithm in document.algorithms:
            edges.append(
                self._edge(
                    document_key,
                    stable_node_key(GraphNodeType.ALGORITHM.value, algorithm),
                    GraphRelationshipType.IMPLEMENTS.value,
                    f"{document.title} implements or discusses {algorithm}.",
                    confidence=0.7,
                    source_document_id=document.id,
                )
            )

        for reference in document.references:
            reference_name = reference.title or reference.citation_text[:120]
            reference_key = stable_node_key(self._reference_node_type(reference.reference_type), reference_name)
            edges.append(
                self._edge(
                    reference_key,
                    document_key,
                    GraphRelationshipType.REFERENCED_BY.value,
                    f"{reference_name} is referenced by {document.title}.",
                    confidence=reference.confidence_score,
                    source_document_id=document.id,
                )
            )
            for author in reference.authors[:6]:
                edges.append(
                    self._edge(
                        stable_node_key(GraphNodeType.AUTHOR.value, author),
                        reference_key,
                        GraphRelationshipType.INTRODUCED_BY.value,
                        f"{author} is connected to {reference_name}.",
                        confidence=0.62,
                        source_document_id=document.id,
                    )
                )

        for relationship in document.relationships:
            edges.append(
                self._edge(
                    self._best_entity_key(relationship.source_name),
                    self._best_entity_key(relationship.target_name),
                    self._relationship_type(relationship.relationship_type),
                    relationship.description,
                    confidence=relationship.confidence_score,
                    source_document_id=document.id,
                )
            )

        if dna:
            edges.extend(self._dna_edges(document.id, document.title, dna))

        return edges

    def _dna_edges(self, document_id: str, document_title: str, dna: object) -> list[GraphEdgeDraft]:
        document_key = stable_node_key(GraphNodeType.DOCUMENT.value, document_title, document_id=document_id)
        edges: list[GraphEdgeDraft] = []
        for concept in dna.primary_concepts:
            edges.append(
                self._edge(
                    document_key,
                    stable_node_key(GraphNodeType.CONCEPT.value, concept),
                    GraphRelationshipType.EXPLAINS.value,
                    f"{document_title} has {concept} as a primary concept.",
                    confidence=0.84,
                    source_document_id=document_id,
                )
            )
        for concept in dna.secondary_concepts:
            edges.append(
                self._edge(
                    document_key,
                    stable_node_key(GraphNodeType.CONCEPT.value, concept),
                    GraphRelationshipType.RELATED_TO.value,
                    f"{document_title} has {concept} as a secondary concept.",
                    confidence=0.68,
                    source_document_id=document_id,
                )
            )
        focus = dna.primary_concepts[0] if dna.primary_concepts else document_title
        focus_key = stable_node_key(GraphNodeType.CONCEPT.value, focus)
        for prerequisite in dna.prerequisites:
            edges.append(
                self._edge(
                    stable_node_key(GraphNodeType.CONCEPT.value, prerequisite),
                    focus_key,
                    GraphRelationshipType.PREREQUISITE.value,
                    f"{prerequisite} is required before {focus}.",
                    confidence=0.76,
                    source_document_id=document_id,
                )
            )
        for advanced_topic in dna.advanced_topics:
            edges.append(
                self._edge(
                    focus_key,
                    stable_node_key(GraphNodeType.CONCEPT.value, advanced_topic),
                    GraphRelationshipType.EXTENDS.value,
                    f"{advanced_topic} extends {focus}.",
                    confidence=0.68,
                    source_document_id=document_id,
                )
            )
        for future_topic in dna.future_learning_topics:
            edges.append(
                self._edge(
                    focus_key,
                    stable_node_key(GraphNodeType.CONCEPT.value, future_topic),
                    GraphRelationshipType.IMPROVES.value,
                    f"Learning {future_topic} improves mastery after {focus}.",
                    confidence=0.66,
                    source_document_id=document_id,
                )
            )
        for parent in dna.parent_topics:
            edges.append(
                self._edge(
                    stable_node_key(GraphNodeType.CONCEPT.value, parent),
                    focus_key,
                    GraphRelationshipType.PARENT_TOPIC.value,
                    f"{parent} is a parent topic of {focus}.",
                    confidence=0.7,
                    source_document_id=document_id,
                )
            )
        for child in dna.child_topics:
            edges.append(
                self._edge(
                    focus_key,
                    stable_node_key(GraphNodeType.CONCEPT.value, child),
                    GraphRelationshipType.CHILD_TOPIC.value,
                    f"{child} is a child topic of {focus}.",
                    confidence=0.68,
                    source_document_id=document_id,
                )
            )
        for technology in dna.technologies_used:
            edges.append(
                self._edge(
                    document_key,
                    stable_node_key(GraphNodeType.TECHNOLOGY.value, technology),
                    GraphRelationshipType.USES.value,
                    f"{document_title} uses {technology}.",
                    confidence=0.7,
                    source_document_id=document_id,
                )
            )
        for language in dna.programming_languages:
            edges.append(
                self._edge(
                    document_key,
                    stable_node_key(GraphNodeType.PROGRAMMING_LANGUAGE.value, language),
                    GraphRelationshipType.BUILT_WITH.value,
                    f"{document_title} is built with or discusses {language}.",
                    confidence=0.68,
                    source_document_id=document_id,
                )
            )
        for framework in dna.frameworks:
            edges.append(
                self._edge(
                    document_key,
                    stable_node_key(GraphNodeType.FRAMEWORK.value, framework),
                    GraphRelationshipType.BUILT_WITH.value,
                    f"{document_title} is built with or discusses {framework}.",
                    confidence=0.66,
                    source_document_id=document_id,
                )
            )
        for library in dna.libraries:
            edges.append(
                self._edge(
                    document_key,
                    stable_node_key(GraphNodeType.LIBRARY.value, library),
                    GraphRelationshipType.BUILT_WITH.value,
                    f"{document_title} is built with or discusses {library}.",
                    confidence=0.64,
                    source_document_id=document_id,
                )
            )
        for paper in dna.research_papers:
            edges.append(
                self._edge(
                    stable_node_key(GraphNodeType.RESEARCH_PAPER.value, paper),
                    document_key,
                    GraphRelationshipType.REFERENCED_BY.value,
                    f"{paper} is referenced by {document_title}.",
                    confidence=0.64,
                    source_document_id=document_id,
                )
            )
        for related in dna.related_documents:
            related_id = str(
                related.get("id")
                or related.get("related_document_id")
                or related.get("document_id")
                or ""
            )
            related_title = str(related.get("title") or related.get("document_title") or "")
            if related_id and related_title:
                edges.append(
                    self._edge(
                        document_key,
                        stable_node_key(GraphNodeType.DOCUMENT.value, related_title, document_id=related_id),
                        GraphRelationshipType.RELATED_TO.value,
                        f"{document_title} is related to {related_title}.",
                        confidence=float(related.get("similarity_score", 0.62)),
                        source_document_id=document_id,
                    )
                )
        return edges

    def _edge(
        self,
        source_key: str,
        target_key: str,
        relationship_type: str,
        description: str,
        *,
        confidence: float,
        source_document_id: str,
    ) -> GraphEdgeDraft:
        weight = self.scorer.score(relationship_type, confidence=confidence)
        label = relationship_type.replace("_", " ").title()
        return GraphEdgeDraft(
            stable_key=stable_edge_key(source_key, target_key, relationship_type),
            source_key=source_key,
            target_key=target_key,
            relationship_type=relationship_type,
            label=label,
            description=description.strip(),
            weight=weight,
            confidence_score=confidence,
            metadata={"source_document_ids": [source_document_id]},
        )

    def _best_entity_key(self, name: str) -> str:
        return stable_node_key(GraphNodeType.CONCEPT.value, name)

    def _relationship_type(self, value: str) -> str:
        normalized = value.casefold().replace(" ", "_").replace("-", "_")
        allowed = {relationship.value for relationship in GraphRelationshipType}
        if normalized in allowed:
            return normalized
        if "prereq" in normalized:
            return GraphRelationshipType.PREREQUISITE.value
        if "depend" in normalized:
            return GraphRelationshipType.DEPENDS_ON.value
        if "support" in normalized:
            return GraphRelationshipType.SUPPORTS.value
        if "contradict" in normalized:
            return GraphRelationshipType.CONTRADICTS.value
        return GraphRelationshipType.RELATED_TO.value

    def _technology_node_type(self, category: str, name: str) -> str:
        normalized = f"{category} {name}".casefold()
        if "language" in normalized or name in {"Python", "Java", "JavaScript", "TypeScript", "SQL"}:
            return GraphNodeType.PROGRAMMING_LANGUAGE.value
        if "framework" in normalized:
            return GraphNodeType.FRAMEWORK.value
        if "library" in normalized:
            return GraphNodeType.LIBRARY.value
        if "api" in normalized:
            return GraphNodeType.API.value
        if "tool" in normalized:
            return GraphNodeType.TOOL.value
        if "model" in normalized:
            return GraphNodeType.MODEL.value
        return GraphNodeType.TECHNOLOGY.value

    def _reference_node_type(self, reference_type: str) -> str:
        return GraphNodeType.BOOK.value if "book" in reference_type.casefold() else GraphNodeType.RESEARCH_PAPER.value
