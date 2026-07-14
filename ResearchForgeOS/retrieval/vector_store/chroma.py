from pathlib import Path
from typing import Any

from retrieval.utils import clamp, flatten_metadata
from retrieval.vector_store.base import VectorRecord, VectorSearchResult


class ChromaVectorStore:
    def __init__(self, persist_directory: str = ".chroma") -> None:
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("ChromaDB is not installed. Install chromadb to enable this vector backend.") from exc

        Path(persist_directory).mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=persist_directory)

    def upsert(self, records: list[VectorRecord]) -> None:
        grouped: dict[tuple[str, str], list[VectorRecord]] = {}
        for record in records:
            grouped.setdefault((record.collection_name, record.namespace), []).append(record)

        for (collection_name, namespace), items in grouped.items():
            collection = self._collection(collection_name, namespace)
            collection.upsert(
                ids=[item.id for item in items],
                embeddings=[item.embedding for item in items],
                metadatas=[
                    flatten_metadata({"namespace": item.namespace, **item.metadata})
                    for item in items
                ],
                documents=[item.document for item in items],
            )

    def query(
        self,
        *,
        collection_name: str,
        namespace: str,
        embedding: list[float],
        top_k: int,
        filters: dict[str, object] | None = None,
    ) -> list[VectorSearchResult]:
        collection = self._collection(collection_name, namespace)
        where = flatten_metadata({"namespace": namespace, **(filters or {})})
        result = collection.query(
            query_embeddings=[embedding],
            n_results=top_k,
            where=where or None,
            include=["documents", "metadatas", "distances"],
        )
        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        return [
            VectorSearchResult(
                id=str(item_id),
                score=clamp(1.0 - float(distance)),
                document=str(document),
                metadata=dict(metadata or {}),
            )
            for item_id, document, metadata, distance in zip(ids, documents, metadatas, distances, strict=False)
        ]

    def delete_document(self, *, collection_name: str, namespace: str, document_id: str) -> None:
        collection = self._collection(collection_name, namespace)
        collection.delete(where={"namespace": namespace, "document_id": document_id})

    def optimize(self, *, collection_name: str, namespace: str) -> None:
        self._collection(collection_name, namespace)

    def _collection(self, collection_name: str, namespace: str) -> Any:
        safe_name = f"{namespace}_{collection_name}".replace("-", "_").lower()
        return self._client.get_or_create_collection(name=safe_name)
