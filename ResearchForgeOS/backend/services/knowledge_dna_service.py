from uuid import uuid4

from knowledge_engine.dna import KnowledgeDNAEngine
from knowledge_engine.dna.types import (
    DNAConceptInput,
    DNADocumentInput,
    DNATechnologyInput,
    KnowledgeDNAResult,
    RelatedDocumentCandidate,
)
from sqlalchemy.orm import Session

from backend.exceptions import NotFoundError
from backend.models.document import Document
from backend.models.knowledge_dna import (
    KnowledgeDNA,
    KnowledgeEdge,
    KnowledgeHierarchy,
    KnowledgeNode,
    LearningPath,
    Prerequisite,
    RelatedDocument,
)
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.knowledge_dna_repository import KnowledgeDNARepository
from backend.schemas.knowledge_dna import KnowledgeDNAUpdate, RelatedTopicRead
from backend.services.graph_service import InteractiveKnowledgeGraphService


class KnowledgeDNAService:
    def __init__(self, session: Session, engine: KnowledgeDNAEngine | None = None) -> None:
        self.session = session
        self.documents = DocumentRepository(session)
        self.dna = KnowledgeDNARepository(session)
        self.engine = engine or KnowledgeDNAEngine()

    def generate_for_document(self, document_id: str) -> KnowledgeDNA:
        document = self._document(document_id)
        candidates = self._related_document_candidates(document.id)
        result = self.engine.generate(self._input_from_document(document, candidates))

        existing = self.dna.get_by_document_id(document_id)
        if existing is not None:
            self.dna.delete(existing)
            self.session.flush()

        model = self._model_from_result(document, result)
        self.dna.add(model)
        self.session.flush()
        InteractiveKnowledgeGraphService(self.session).sync_document_graph(document)
        self.session.commit()
        loaded = self.dna.get_full(model.id)
        if loaded is None:
            raise NotFoundError("Knowledge DNA was generated but could not be loaded.")
        return loaded

    def get_by_document(self, document_id: str) -> KnowledgeDNA:
        model = self.dna.get_by_document_id(document_id)
        if model is None:
            raise NotFoundError("Knowledge DNA has not been generated for this document.")
        return model

    def get(self, dna_id: str) -> KnowledgeDNA:
        model = self.dna.get_full(dna_id)
        if model is None:
            raise NotFoundError("Knowledge DNA was not found.")
        return model

    def update(self, dna_id: str, payload: KnowledgeDNAUpdate) -> KnowledgeDNA:
        model = self.get(dna_id)
        update_data = payload.model_dump(exclude_unset=True)
        for field_name, value in update_data.items():
            setattr(model, field_name, value)
        document = self._document(model.document_id)
        InteractiveKnowledgeGraphService(self.session).sync_document_graph(document)
        self.session.commit()
        return self.get(dna_id)

    def delete(self, dna_id: str) -> None:
        model = self.get(dna_id)
        document_id = model.document_id
        self.dna.delete(model)
        self.session.flush()
        InteractiveKnowledgeGraphService(self.session).sync_document_graph(self._document(document_id))
        self.session.commit()

    def learning_path(self, document_id: str) -> list[LearningPath]:
        model = self.get_by_document(document_id)
        return sorted(model.learning_path_steps, key=lambda step: step.order_index)

    def prerequisites(self, document_id: str) -> list[Prerequisite]:
        model = self.get_by_document(document_id)
        return sorted(model.prerequisite_items, key=lambda item: (-item.importance_score, item.topic))

    def related_topics(self, document_id: str) -> list[RelatedTopicRead]:
        model = self.get_by_document(document_id)
        topics: list[RelatedTopicRead] = []
        for topic in model.parent_topics:
            topics.append(
                RelatedTopicRead(topic=topic, relationship_type="parent", confidence_score=0.72, source="dna")
            )
        for topic in model.child_topics:
            topics.append(
                RelatedTopicRead(topic=topic, relationship_type="child", confidence_score=0.66, source="dna")
            )
        for topic in model.sibling_topics:
            topics.append(
                RelatedTopicRead(topic=topic, relationship_type="sibling", confidence_score=0.62, source="dna")
            )
        for topic in model.future_learning_topics:
            topics.append(
                RelatedTopicRead(topic=topic, relationship_type="next_learn", confidence_score=0.68, source="dna")
            )
        return topics

    def _document(self, document_id: str) -> Document:
        document = self.documents.get_full(document_id)
        if document is None:
            raise NotFoundError("Document was not found.")
        return document

    def _related_document_candidates(self, document_id: str) -> list[RelatedDocumentCandidate]:
        candidates: list[RelatedDocumentCandidate] = []
        for document in self.documents.list_documents(offset=0, limit=100):
            if document.id == document_id:
                continue
            candidates.append(
                RelatedDocumentCandidate(
                    id=document.id,
                    title=document.title,
                    category=document.category,
                    topics=document.topics,
                    concepts=[concept.name for concept in document.concepts],
                    technologies=[technology.name for technology in document.technologies],
                )
            )
        return candidates

    def _input_from_document(
        self,
        document: Document,
        candidates: list[RelatedDocumentCandidate],
    ) -> DNADocumentInput:
        return DNADocumentInput(
            id=document.id,
            title=document.title,
            category=document.category,
            difficulty=document.difficulty,
            estimated_reading_time_minutes=document.estimated_reading_time_minutes,
            word_count=document.word_count,
            topics=document.topics,
            keywords=[keyword.value for keyword in document.keywords],
            concepts=[
                DNAConceptInput(
                    id=concept.id,
                    name=concept.name,
                    concept_type=concept.concept_type,
                    description=concept.description,
                    prerequisites=concept.prerequisites,
                    dependencies=concept.dependencies,
                    difficulty_level=concept.difficulty_level,
                    confidence_score=concept.confidence_score,
                )
                for concept in document.concepts
            ],
            technologies=[
                DNATechnologyInput(
                    id=technology.id,
                    name=technology.name,
                    category=technology.category,
                    confidence_score=technology.confidence_score,
                    evidence=technology.evidence,
                )
                for technology in document.technologies
            ],
            algorithms=[algorithm.get("name", "") for algorithm in document.algorithms if algorithm.get("name")],
            definitions=[definition.get("term", "") for definition in document.definitions if definition.get("term")],
            equations=[equation.get("expression", "") for equation in document.equations if equation.get("expression")],
            code_snippet_count=len(document.code_snippets),
            references=[
                reference.title or reference.citation_text
                for reference in document.references
                if reference.title or reference.citation_text
            ],
            cleaned_text=document.cleaned_text,
            related_document_candidates=candidates,
        )

    def _model_from_result(self, document: Document, result: KnowledgeDNAResult) -> KnowledgeDNA:
        model = KnowledgeDNA(
            document_id=document.id,
            document_title=result.document_title,
            difficulty_level=result.difficulty_level,
            estimated_reading_time_minutes=result.estimated_reading_time_minutes,
            knowledge_score=result.knowledge_score,
            interview_importance=result.interview_importance,
            industry_relevance=result.industry_relevance,
            implementation_complexity=result.implementation_complexity,
            research_category=result.research_category,
            primary_concepts=result.primary_concepts,
            secondary_concepts=result.secondary_concepts,
            prerequisites=result.prerequisites,
            advanced_topics=result.advanced_topics,
            future_learning_topics=result.future_learning_topics,
            technologies_used=result.technologies_used,
            programming_languages=result.programming_languages,
            frameworks=result.frameworks,
            libraries=result.libraries,
            algorithms=result.algorithms,
            datasets=result.datasets,
            research_papers=result.research_papers,
            learning_order=result.learning_order,
            estimated_mastery_time_hours=result.estimated_mastery_time_hours,
            mathematical_topics=result.mathematical_topics,
            parent_topics=result.parent_topics,
            child_topics=result.child_topics,
            sibling_topics=result.sibling_topics,
            knowledge_chains=result.knowledge_chains,
            research_evolution=result.research_evolution,
            metadata_json=result.metadata,
        )
        node_lookup = self._attach_nodes(model, result)
        self._attach_edges(model, result, node_lookup)
        self._attach_hierarchy(model, result)
        self._attach_learning_path(model, result)
        self._attach_prerequisites(model, result)
        self._attach_related_documents(model, result)
        return model

    def _attach_nodes(self, model: KnowledgeDNA, result: KnowledgeDNAResult) -> dict[str, KnowledgeNode]:
        node_lookup: dict[str, KnowledgeNode] = {}
        for node in result.nodes:
            item = KnowledgeNode(
                id=str(uuid4()),
                stable_key=node.stable_key,
                node_type=node.node_type,
                name=node.name,
                label=node.label,
                description=node.description,
                importance_score=node.importance_score,
                metadata_json=node.metadata,
            )
            model.nodes.append(item)
            node_lookup[node.stable_key] = item
        return node_lookup

    def _attach_edges(
        self,
        model: KnowledgeDNA,
        result: KnowledgeDNAResult,
        node_lookup: dict[str, KnowledgeNode],
    ) -> None:
        for edge in result.edges:
            model.edges.append(
                KnowledgeEdge(
                    source_node_id=node_lookup[edge.source_key].id if edge.source_key in node_lookup else None,
                    target_node_id=node_lookup[edge.target_key].id if edge.target_key in node_lookup else None,
                    source_key=edge.source_key,
                    target_key=edge.target_key,
                    edge_type=edge.edge_type,
                    weight=edge.weight,
                    confidence_score=edge.confidence_score,
                    description=edge.description,
                    metadata_json=edge.metadata,
                )
            )

    def _attach_hierarchy(self, model: KnowledgeDNA, result: KnowledgeDNAResult) -> None:
        for item in result.hierarchy:
            model.hierarchy_items.append(
                KnowledgeHierarchy(
                    parent_topic=item.parent_topic,
                    child_topic=item.child_topic,
                    hierarchy_type=item.hierarchy_type,
                    confidence_score=item.confidence_score,
                    evidence=item.evidence,
                )
            )

    def _attach_learning_path(self, model: KnowledgeDNA, result: KnowledgeDNAResult) -> None:
        for step in result.learning_path:
            model.learning_path_steps.append(
                LearningPath(
                    order_index=step.order_index,
                    topic=step.topic,
                    reason=step.reason,
                    estimated_hours=step.estimated_hours,
                    difficulty_level=step.difficulty_level,
                    resource_hint=step.resource_hint,
                )
            )

    def _attach_prerequisites(self, model: KnowledgeDNA, result: KnowledgeDNAResult) -> None:
        for index, topic in enumerate(result.prerequisites):
            model.prerequisite_items.append(
                Prerequisite(
                    topic=topic,
                    prerequisite_type="inferred",
                    importance_score=max(0.4, 0.9 - index * 0.04),
                    source_concept=result.primary_concepts[0] if result.primary_concepts else None,
                )
            )

    def _attach_related_documents(self, model: KnowledgeDNA, result: KnowledgeDNAResult) -> None:
        for item in result.related_documents:
            model.related_documents.append(
                RelatedDocument(
                    related_document_id=item.id,
                    title=item.title,
                    similarity_score=item.similarity_score,
                    shared_signals=item.shared_signals,
                    relationship_reason=f"Shares {', '.join(item.shared_signals[:5])}.",
                )
            )
