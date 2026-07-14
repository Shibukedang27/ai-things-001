import logging
from uuid import uuid4

from knowledge_engine import KnowledgeEnginePipeline, KnowledgeSourceRequest, SourceType
from knowledge_engine.exceptions import KnowledgeEngineError
from knowledge_engine.types import KnowledgeEngineResult
from knowledge_engine.utils import words
from sqlalchemy.orm import Session

from backend.exceptions import NotFoundError, ValidationError
from backend.models.document import (
    Document,
    DocumentChunk,
    DocumentConcept,
    DocumentEmbedding,
    DocumentKeyword,
    DocumentReference,
    DocumentSummary,
    DocumentTechnology,
    KnowledgeRelationship,
)
from backend.models.user import User
from backend.repositories.document_repository import DocumentRepository
from backend.services.graph_service import InteractiveKnowledgeGraphService
from backend.services.learning_service import AdaptiveLearningService
from backend.services.retrieval_index_service import RetrievalIndexService

logger = logging.getLogger(__name__)


class DocumentService:
    SUMMARY_FIELDS = {
        "executive": "executive_summary",
        "beginner": "beginner_summary",
        "technical": "technical_summary",
        "detailed": "detailed_summary",
        "one_minute": "one_minute_summary",
        "five_minute": "five_minute_summary",
    }

    def __init__(self, session: Session, pipeline: KnowledgeEnginePipeline | None = None) -> None:
        self.session = session
        self.documents = DocumentRepository(session)
        self.pipeline = pipeline or KnowledgeEnginePipeline()

    def ingest_document(
        self,
        *,
        current_user: User,
        file_content: bytes | None = None,
        filename: str | None = None,
        mime_type: str | None = None,
        source_text: str | None = None,
        source_url: str | None = None,
        source_type: str | None = None,
        title: str | None = None,
        author: str | None = None,
        category: str | None = None,
    ) -> Document:
        request = self._source_request(
            file_content=file_content,
            filename=filename,
            mime_type=mime_type,
            source_text=source_text,
            source_url=source_url,
            source_type=source_type,
            title=title,
            author=author,
            category=category,
        )
        try:
            result = self.pipeline.process(request)
        except KnowledgeEngineError as exc:
            raise ValidationError(str(exc)) from exc

        existing_document = self.documents.get_by_hash(result.metadata.content_hash)
        if existing_document is not None:
            RetrievalIndexService(self.session).index_document(existing_document)
            InteractiveKnowledgeGraphService(self.session).sync_document_graph(existing_document)
            AdaptiveLearningService(self.session).sync_document_learning(existing_document, current_user, commit=False)
            self.session.commit()
            return existing_document

        document = self._build_document(
            result,
            current_user=current_user,
            filename=filename,
            mime_type=mime_type,
            source_url=source_url,
        )
        self.documents.add(document)
        self.session.flush()
        RetrievalIndexService(self.session).index_document(document)
        InteractiveKnowledgeGraphService(self.session).sync_document_graph(document)
        AdaptiveLearningService(self.session).sync_document_learning(document, current_user, commit=False)
        self.session.commit()
        loaded_document = self.documents.get_full(document.id)
        if loaded_document is None:
            raise NotFoundError("Document was processed but could not be loaded.")
        logger.info("Knowledge document ingested", extra={"document_id": loaded_document.id})
        return loaded_document

    def list_documents(self, *, offset: int, limit: int) -> list[Document]:
        return list(self.documents.list_documents(offset=offset, limit=limit))

    def get_document(self, document_id: str) -> Document:
        document = self.documents.get_full(document_id)
        if document is None:
            raise NotFoundError("Document was not found.")
        return document

    def delete_document(self, document_id: str) -> None:
        document = self.get_document(document_id)
        RetrievalIndexService(self.session).delete_document_index(document.id)
        InteractiveKnowledgeGraphService(self.session).delete_document_graph(document.id)
        self.documents.delete(document)
        self.session.commit()

    def get_summary(self, document_id: str, summary_type: str | None = None) -> list[DocumentSummary]:
        document = self.get_document(document_id)
        if summary_type is None:
            return sorted(document.summaries, key=lambda summary: summary.summary_type)
        matching = [summary for summary in document.summaries if summary.summary_type == summary_type]
        if not matching:
            raise NotFoundError("Requested summary type was not found.")
        return matching

    def _source_request(
        self,
        *,
        file_content: bytes | None,
        filename: str | None,
        mime_type: str | None,
        source_text: str | None,
        source_url: str | None,
        source_type: str | None,
        title: str | None,
        author: str | None,
        category: str | None,
    ) -> KnowledgeSourceRequest:
        normalized_source_type = self._source_type(source_type)
        has_file = file_content is not None and len(file_content) > 0
        has_text = bool(source_text and source_text.strip())
        has_url = bool(source_url and source_url.strip())
        if sum([has_file, has_text, has_url]) != 1:
            raise ValidationError("Provide exactly one knowledge source: file, source_text, or source_url.")

        content: bytes | str | None
        if has_file:
            content = file_content
        elif has_text:
            content = source_text
        else:
            content = None

        return KnowledgeSourceRequest(
            source_type=normalized_source_type,
            filename=filename,
            mime_type=mime_type,
            content=content,
            source_url=source_url,
            title=title,
            author=author,
            category=category,
        )

    def _source_type(self, source_type: str | None) -> SourceType | None:
        if source_type is None or not source_type.strip():
            return None
        normalized = source_type.strip().lower()
        try:
            return SourceType(normalized)
        except ValueError as exc:
            valid_values = [value.value for value in SourceType]
            raise ValidationError("Unsupported source type.", details={"valid_source_types": valid_values}) from exc

    def _build_document(
        self,
        result: KnowledgeEngineResult,
        *,
        current_user: User,
        filename: str | None,
        mime_type: str | None,
        source_url: str | None,
    ) -> Document:
        document = Document(
            title=result.metadata.title,
            author=result.metadata.author,
            category=result.metadata.category,
            source_type=result.source_type.value,
            status="processed",
            original_filename=filename,
            mime_type=mime_type,
            source_url=source_url,
            language=result.metadata.language,
            difficulty=result.metadata.difficulty.value,
            estimated_reading_time_minutes=result.metadata.estimated_reading_time_minutes,
            word_count=result.metadata.word_count,
            character_count=result.metadata.character_count,
            content_hash=result.metadata.content_hash,
            cleaned_text=result.cleaned_text,
            topics=result.metadata.topics,
            definitions=result.definitions,
            algorithms=result.algorithms,
            equations=result.equations,
            code_snippets=result.code_snippets,
            learning_objectives=result.learning_assets.learning_objectives,
            learning_assets={
                "flashcards": result.learning_assets.flashcards,
                "quiz_questions": result.learning_assets.quiz_questions,
                "interview_questions": result.learning_assets.interview_questions,
                "daily_revision_plan": result.learning_assets.daily_revision_plan,
            },
            metadata_json={
                "pipeline": "knowledge_engine_v1",
                "embedding_model": result.embeddings[0].embedding_model if result.embeddings else None,
                "chunk_count": len(result.chunks),
            },
            created_by_user_id=current_user.id,
        )

        self._attach_summaries(document, result)
        chunk_lookup = self._attach_chunks(document, result)
        concept_lookup = self._attach_concepts(document, result)
        technology_lookup = self._attach_technologies(document, result)
        self._attach_keywords(document, result)
        self._attach_references(document, result)
        self._attach_embeddings(document, result, chunk_lookup)
        self._attach_relationships(document, result, concept_lookup, technology_lookup)
        return document

    def _attach_summaries(self, document: Document, result: KnowledgeEngineResult) -> None:
        for summary_type, field_name in self.SUMMARY_FIELDS.items():
            content = getattr(result.summaries, field_name)
            document.summaries.append(
                DocumentSummary(
                    summary_type=summary_type,
                    content=content,
                    word_count=len(words(content)),
                    confidence_score=0.86,
                )
            )

    def _attach_chunks(self, document: Document, result: KnowledgeEngineResult) -> dict[int, DocumentChunk]:
        chunk_lookup: dict[int, DocumentChunk] = {}
        for chunk in result.chunks:
            model = DocumentChunk(
                chunk_index=chunk.index,
                content=chunk.content,
                token_count=chunk.token_count,
                character_count=len(chunk.content),
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                content_hash=chunk.content_hash,
                metadata_json={"source": "chunk_manager_v1"},
            )
            document.chunks.append(model)
            chunk_lookup[chunk.index] = model
        return chunk_lookup

    def _attach_concepts(self, document: Document, result: KnowledgeEngineResult) -> dict[str, DocumentConcept]:
        concept_lookup: dict[str, DocumentConcept] = {}
        for concept in result.concepts:
            model = DocumentConcept(
                id=str(uuid4()),
                name=concept.name,
                normalized_name=self._normalize(concept.name),
                concept_type=concept.concept_type,
                description=concept.description,
                prerequisites=concept.prerequisites,
                dependencies=concept.dependencies,
                difficulty_level=concept.difficulty_level.value,
                confidence_score=concept.confidence_score,
            )
            document.concepts.append(model)
            concept_lookup[self._normalize(concept.name)] = model
        return concept_lookup

    def _attach_keywords(self, document: Document, result: KnowledgeEngineResult) -> None:
        for keyword in result.keywords:
            document.keywords.append(
                DocumentKeyword(
                    value=keyword.value,
                    normalized_value=self._normalize(keyword.value),
                    relevance_score=keyword.relevance_score,
                    occurrence_count=keyword.occurrence_count,
                )
            )

    def _attach_technologies(self, document: Document, result: KnowledgeEngineResult) -> dict[str, DocumentTechnology]:
        technology_lookup: dict[str, DocumentTechnology] = {}
        for technology in result.technologies:
            model = DocumentTechnology(
                id=str(uuid4()),
                name=technology.name,
                normalized_name=self._normalize(technology.name),
                category=technology.category,
                confidence_score=technology.confidence_score,
                evidence=technology.evidence,
            )
            document.technologies.append(model)
            technology_lookup[self._normalize(technology.name)] = model
        return technology_lookup

    def _attach_embeddings(
        self,
        document: Document,
        result: KnowledgeEngineResult,
        chunk_lookup: dict[int, DocumentChunk],
    ) -> None:
        for embedding in result.embeddings:
            document.embeddings.append(
                DocumentEmbedding(
                    chunk=chunk_lookup.get(embedding.chunk_index),
                    embedding_model=embedding.embedding_model,
                    embedding_dimensions=embedding.embedding_dimensions,
                    vector=embedding.vector,
                    content_hash=embedding.content_hash,
                    metadata_json=embedding.metadata,
                )
            )

    def _attach_references(self, document: Document, result: KnowledgeEngineResult) -> None:
        for reference in result.references:
            document.references.append(
                DocumentReference(
                    title=reference.title,
                    authors=reference.authors,
                    year=reference.year,
                    source=reference.source,
                    url=reference.url,
                    citation_text=reference.citation_text,
                    reference_type=reference.reference_type,
                    confidence_score=reference.confidence_score,
                )
            )

    def _attach_relationships(
        self,
        document: Document,
        result: KnowledgeEngineResult,
        concept_lookup: dict[str, DocumentConcept],
        technology_lookup: dict[str, DocumentTechnology],
    ) -> None:
        for relationship in result.relationships:
            source_type, source_id = self._entity_reference(relationship.source_name, concept_lookup, technology_lookup)
            target_type, target_id = self._entity_reference(relationship.target_name, concept_lookup, technology_lookup)
            document.relationships.append(
                KnowledgeRelationship(
                    source_entity_type=source_type,
                    source_entity_id=source_id,
                    source_name=relationship.source_name,
                    target_entity_type=target_type,
                    target_entity_id=target_id,
                    target_name=relationship.target_name,
                    relationship_type=relationship.relationship_type,
                    description=relationship.description,
                    confidence_score=relationship.confidence_score,
                    metadata_json=relationship.metadata,
                )
            )

    def _entity_reference(
        self,
        name: str,
        concept_lookup: dict[str, DocumentConcept],
        technology_lookup: dict[str, DocumentTechnology],
    ) -> tuple[str, str | None]:
        key = self._normalize(name)
        if key in concept_lookup:
            return "concept", concept_lookup[key].id
        if key in technology_lookup:
            return "technology", technology_lookup[key].id
        return "external_concept", None

    def _normalize(self, value: str) -> str:
        return " ".join(value.lower().strip().split())
