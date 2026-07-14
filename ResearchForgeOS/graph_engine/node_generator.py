from graph_engine.scoring import NodeScorer
from graph_engine.types import GraphBuildInput, GraphNodeDraft, GraphNodeType
from graph_engine.utils import node_color, stable_node_key, top_terms


class NodeGenerator:
    COMPANIES = ("OpenAI", "Google", "Microsoft", "Meta", "Amazon", "NVIDIA", "Anthropic")
    UNIVERSITIES = ("Stanford", "MIT", "Harvard", "Berkeley", "Carnegie Mellon", "Oxford", "Cambridge")

    def __init__(self, scorer: NodeScorer | None = None) -> None:
        self.scorer = scorer or NodeScorer()

    def generate(self, graph_input: GraphBuildInput) -> list[GraphNodeDraft]:
        document = graph_input.document
        dna = document.dna
        nodes: list[GraphNodeDraft] = [
            self._node(
                GraphNodeType.DOCUMENT.value,
                document.title,
                document.title,
                f"Uploaded {document.source_type} knowledge source in {document.category}.",
                confidence=0.96,
                signal_count=max(1, len(document.concepts) + len(document.technologies)),
                metadata={
                    "document_id": document.id,
                    "category": document.category,
                    "source_type": document.source_type,
                    "difficulty": document.difficulty,
                    "created_at": document.created_at,
                    "source_document_ids": [document.id],
                },
                document_id=document.id,
            )
        ]

        if document.author:
            nodes.append(
                self._node(
                    GraphNodeType.AUTHOR.value,
                    document.author,
                    document.author,
                    f"Author associated with {document.title}.",
                    confidence=0.72,
                    metadata={"source_document_ids": [document.id]},
                )
            )

        for concept in document.concepts:
            nodes.append(
                self._node(
                    GraphNodeType.CONCEPT.value,
                    concept.name,
                    concept.name,
                    concept.description or f"Concept detected in {document.title}.",
                    confidence=concept.confidence_score,
                    signal_count=2 + len(concept.prerequisites) + len(concept.dependencies),
                    dna_boost=0.08 if dna and concept.name in dna.primary_concepts else 0.0,
                    metadata={
                        "concept_type": concept.concept_type,
                        "difficulty": concept.difficulty_level,
                        "prerequisites": concept.prerequisites,
                        "dependencies": concept.dependencies,
                        "source_document_ids": [document.id],
                    },
                )
            )
            for related_concept in [*concept.prerequisites, *concept.dependencies]:
                nodes.append(
                    self._node(
                        GraphNodeType.CONCEPT.value,
                        related_concept,
                        related_concept,
                        f"Prerequisite or dependency connected to {concept.name}.",
                        confidence=0.62,
                        metadata={"source_document_ids": [document.id]},
                    )
                )

        topics = [
            *document.topics,
            *(dna.primary_concepts if dna else []),
            *(dna.secondary_concepts if dna else []),
        ]
        for topic in topics:
            nodes.append(
                self._node(
                    GraphNodeType.CONCEPT.value,
                    topic,
                    topic,
                    f"Knowledge topic connected to {document.title}.",
                    confidence=0.68,
                    signal_count=2,
                    dna_boost=0.08 if dna and topic in dna.primary_concepts else 0.0,
                    metadata={"source_document_ids": [document.id]},
                )
            )

        for keyword in document.keywords[:16]:
            nodes.append(
                self._node(
                    GraphNodeType.INTERVIEW_TOPIC.value,
                    keyword,
                    keyword,
                    f"Interview or revision topic extracted from {document.title}.",
                    confidence=0.58,
                    metadata={"source_document_ids": [document.id]},
                )
            )

        for technology in document.technologies:
            nodes.append(
                self._node(
                    self._technology_node_type(technology.category, technology.name),
                    technology.name,
                    technology.name,
                    f"{technology.category.title()} detected in {document.title}.",
                    confidence=technology.confidence_score,
                    signal_count=1 + len(technology.evidence),
                    metadata={
                        "technology_category": technology.category,
                        "evidence": technology.evidence,
                        "source_document_ids": [document.id],
                    },
                )
            )

        if dna:
            nodes.extend(self._dna_nodes(document.id, dna))

        for algorithm in document.algorithms:
            nodes.append(
                self._node(
                    GraphNodeType.ALGORITHM.value,
                    algorithm,
                    algorithm,
                    f"Algorithm mentioned in {document.title}.",
                    confidence=0.7,
                    metadata={"source_document_ids": [document.id]},
                )
            )

        for reference in document.references:
            reference_name = reference.title or reference.citation_text[:120]
            nodes.append(
                self._node(
                    self._reference_node_type(reference.reference_type),
                    reference_name,
                    reference_name,
                    reference.citation_text,
                    confidence=reference.confidence_score,
                    metadata={
                        "authors": reference.authors,
                        "year": reference.year,
                        "url": reference.url,
                        "source": reference.source,
                        "source_document_ids": [document.id],
                    },
                )
            )
            for author in reference.authors[:6]:
                nodes.append(
                    self._node(
                        GraphNodeType.AUTHOR.value,
                        author,
                        author,
                        f"Referenced author in {reference_name}.",
                        confidence=0.64,
                        metadata={"source_document_ids": [document.id]},
                    )
                )

        for company in self.COMPANIES:
            if company.casefold() in document.cleaned_text.casefold():
                nodes.append(
                    self._node(
                        GraphNodeType.COMPANY.value,
                        company,
                        company,
                        f"Company mentioned in {document.title}.",
                        confidence=0.62,
                        metadata={"source_document_ids": [document.id]},
                    )
                )

        for university in self.UNIVERSITIES:
            if university.casefold() in document.cleaned_text.casefold():
                nodes.append(
                    self._node(
                        GraphNodeType.UNIVERSITY.value,
                        university,
                        university,
                        f"University mentioned in {document.title}.",
                        confidence=0.62,
                        metadata={"source_document_ids": [document.id]},
                    )
                )

        for term in top_terms(document.cleaned_text, limit=8):
            if len(term) > 3:
                nodes.append(
                    self._node(
                        GraphNodeType.CONCEPT.value,
                        term,
                        term.title(),
                        f"Recurring concept signal in {document.title}.",
                        confidence=0.48,
                        metadata={"source_document_ids": [document.id]},
                    )
                )

        return nodes

    def _dna_nodes(self, document_id: str, dna: object) -> list[GraphNodeDraft]:
        nodes: list[GraphNodeDraft] = []
        categories = [
            (GraphNodeType.ALGORITHM.value, dna.algorithms, "Algorithm from Knowledge DNA."),
            (GraphNodeType.DATASET.value, dna.datasets, "Dataset from Knowledge DNA."),
            (GraphNodeType.RESEARCH_PAPER.value, dna.research_papers, "Research paper from Knowledge DNA."),
            (GraphNodeType.CONCEPT.value, dna.advanced_topics, "Advanced topic from Knowledge DNA."),
            (GraphNodeType.CONCEPT.value, dna.future_learning_topics, "Future learning topic from Knowledge DNA."),
            (GraphNodeType.PROGRAMMING_LANGUAGE.value, dna.programming_languages, "Programming language from DNA."),
            (GraphNodeType.FRAMEWORK.value, dna.frameworks, "Framework from Knowledge DNA."),
            (GraphNodeType.LIBRARY.value, dna.libraries, "Library from Knowledge DNA."),
            (GraphNodeType.TECHNOLOGY.value, dna.technologies_used, "Technology from Knowledge DNA."),
        ]
        for node_type, names, description in categories:
            for name in names:
                nodes.append(
                    self._node(
                        node_type,
                        name,
                        name,
                        description,
                        confidence=0.68,
                        dna_boost=0.07,
                        metadata={"source_document_ids": [document_id], "source": "knowledge_dna"},
                    )
                )
        return nodes

    def _node(
        self,
        node_type: str,
        name: str,
        label: str,
        description: str,
        *,
        confidence: float,
        signal_count: int = 1,
        dna_boost: float = 0.0,
        metadata: dict[str, object] | None = None,
        document_id: str | None = None,
    ) -> GraphNodeDraft:
        stable_key = stable_node_key(node_type, name, document_id=document_id)
        importance = self.scorer.score(
            node_type,
            confidence=confidence,
            signal_count=signal_count,
            dna_boost=dna_boost,
        )
        return GraphNodeDraft(
            stable_key=stable_key,
            node_type=node_type,
            name=name.strip(),
            label=label.strip(),
            description=description.strip(),
            importance_score=importance,
            confidence_score=confidence,
            size=self.scorer.size(node_type, importance),
            color=node_color(node_type),
            metadata=metadata or {},
        )

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
        normalized = reference_type.casefold()
        if "book" in normalized:
            return GraphNodeType.BOOK.value
        return GraphNodeType.RESEARCH_PAPER.value
