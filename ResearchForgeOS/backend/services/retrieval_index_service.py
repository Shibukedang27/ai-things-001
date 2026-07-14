from __future__ import annotations

import logging

from retrieval.embedding import RetrievalEmbeddingService
from retrieval.utils import stable_hash
from retrieval.vector_store import VectorRecord, VectorStore, create_vector_store
from sqlalchemy.orm import Session

from backend.config.settings import get_settings
from backend.models.document import Document
from backend.models.retrieval import RetrievalEmbedding
from backend.repositories.document_repository import DocumentRepository
from backend.repositories.retrieval_repository import RetrievalEmbeddingRepository

logger = logging.getLogger(__name__)


class RetrievalIndexService:
    def __init__(
        self,
        session: Session,
        embedding_service: RetrievalEmbeddingService | None = None,
        vector_store: VectorStore | None = None,
    ) -> None:
        settings = get_settings()
        self.session = session
        self.embedding_service = embedding_service or RetrievalEmbeddingService()
        self.vector_store_backend = settings.retrieval_vector_backend
        self.vector_store = vector_store or create_vector_store(
            backend=settings.retrieval_vector_backend,
            persist_directory=settings.retrieval_chroma_persist_directory,
        )
        self.embeddings = RetrievalEmbeddingRepository(session)
        self.documents = DocumentRepository(session)
        self.default_namespace = settings.retrieval_namespace
        self.default_collection_name = settings.retrieval_collection_name

    def index_document(
        self,
        document: Document,
        *,
        namespace: str | None = None,
        collection_name: str | None = None,
    ) -> int:
        resolved_namespace = namespace or self.default_namespace
        resolved_collection = collection_name or self.default_collection_name
        self.embeddings.delete_by_document(document.id)
        self.session.flush()

        records: list[VectorRecord] = []
        existing_vectors = {
            embedding.chunk_id: embedding.vector
            for embedding in document.embeddings
            if embedding.chunk_id
        }
        for chunk in sorted(document.chunks, key=lambda item: item.chunk_index):
            vector = existing_vectors.get(chunk.id) or self.embedding_service.embed_text(chunk.content)
            cache_key = stable_hash(
                resolved_namespace,
                resolved_collection,
                document.id,
                chunk.id,
                chunk.content_hash,
                self.embedding_service.model_name,
            )
            metadata = self._metadata(document, chunk_id=chunk.id, chunk_index=chunk.chunk_index)
            self.session.add(
                RetrievalEmbedding(
                    document_id=document.id,
                    chunk_id=chunk.id,
                    namespace=resolved_namespace,
                    collection_name=resolved_collection,
                    vector_store_backend=self.vector_store_backend,
                    embedding_model=self.embedding_service.model_name,
                    embedding_dimensions=len(vector),
                    vector=vector,
                    content_hash=chunk.content_hash,
                    cache_key=cache_key,
                    metadata_json=metadata,
                )
            )
            records.append(
                VectorRecord(
                    id=cache_key,
                    collection_name=resolved_collection,
                    namespace=resolved_namespace,
                    embedding=vector,
                    document=chunk.content,
                    metadata=metadata,
                )
            )

        if not records and document.cleaned_text:
            vector = self.embedding_service.embed_text(document.cleaned_text)
            cache_key = stable_hash(
                resolved_namespace,
                resolved_collection,
                document.id,
                document.content_hash,
                self.embedding_service.model_name,
            )
            metadata = self._metadata(document, chunk_id=None, chunk_index=0)
            self.session.add(
                RetrievalEmbedding(
                    document_id=document.id,
                    chunk_id=None,
                    namespace=resolved_namespace,
                    collection_name=resolved_collection,
                    vector_store_backend=self.vector_store_backend,
                    embedding_model=self.embedding_service.model_name,
                    embedding_dimensions=len(vector),
                    vector=vector,
                    content_hash=document.content_hash,
                    cache_key=cache_key,
                    metadata_json=metadata,
                )
            )
            records.append(
                VectorRecord(
                    id=cache_key,
                    collection_name=resolved_collection,
                    namespace=resolved_namespace,
                    embedding=vector,
                    document=document.cleaned_text,
                    metadata=metadata,
                )
            )

        self.vector_store.upsert(records)
        self.vector_store.optimize(collection_name=resolved_collection, namespace=resolved_namespace)
        logger.info("Retrieval index updated", extra={"document_id": document.id, "records": len(records)})
        return len(records)

    def delete_document_index(
        self,
        document_id: str,
        *,
        namespace: str | None = None,
        collection_name: str | None = None,
    ) -> None:
        resolved_namespace = namespace or self.default_namespace
        resolved_collection = collection_name or self.default_collection_name
        self.vector_store.delete_document(
            collection_name=resolved_collection,
            namespace=resolved_namespace,
            document_id=document_id,
        )
        self.embeddings.delete_by_document(document_id)
        logger.info("Retrieval index deleted", extra={"document_id": document_id})

    def rebuild_indexes(
        self,
        *,
        namespace: str | None = None,
        collection_name: str | None = None,
    ) -> int:
        total_records = 0
        for document in self.documents.list_documents(offset=0, limit=10_000):
            full_document = self.documents.get_full(document.id)
            if full_document is not None:
                total_records += self.index_document(
                    full_document,
                    namespace=namespace,
                    collection_name=collection_name,
                )
        return total_records

    def _metadata(self, document: Document, *, chunk_id: str | None, chunk_index: int) -> dict[str, object]:
        return {
            "document_id": document.id,
            "chunk_id": chunk_id,
            "chunk_index": chunk_index,
            "title": document.title,
            "category": document.category,
            "source_type": document.source_type,
            "difficulty": document.difficulty,
            "source_url": document.source_url,
            "topics": document.topics,
            "keywords": [keyword.value for keyword in document.keywords],
            "technologies": [technology.name for technology in document.technologies],
        }
