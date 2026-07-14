from retrieval.utils import cosine_similarity
from retrieval.vector_store.base import VectorRecord, VectorSearchResult


class InMemoryVectorStore:
    _records: dict[tuple[str, str], dict[str, VectorRecord]] = {}

    def upsert(self, records: list[VectorRecord]) -> None:
        for record in records:
            key = (record.collection_name, record.namespace)
            self._records.setdefault(key, {})[record.id] = record

    def query(
        self,
        *,
        collection_name: str,
        namespace: str,
        embedding: list[float],
        top_k: int,
        filters: dict[str, object] | None = None,
    ) -> list[VectorSearchResult]:
        key = (collection_name, namespace)
        candidates = self._records.get(key, {}).values()
        filtered = [record for record in candidates if self._matches(record.metadata, filters or {})]
        ranked = sorted(
            (
                VectorSearchResult(
                    id=record.id,
                    score=cosine_similarity(embedding, record.embedding),
                    document=record.document,
                    metadata=record.metadata,
                )
                for record in filtered
            ),
            key=lambda result: result.score,
            reverse=True,
        )
        return ranked[:top_k]

    def delete_document(self, *, collection_name: str, namespace: str, document_id: str) -> None:
        key = (collection_name, namespace)
        records = self._records.get(key, {})
        record_ids = [
            item_id
            for item_id, record in records.items()
            if record.metadata.get("document_id") == document_id
        ]
        for record_id in record_ids:
            records.pop(record_id, None)

    def optimize(self, *, collection_name: str, namespace: str) -> None:
        self._records.setdefault((collection_name, namespace), {})

    def _matches(self, metadata: dict[str, object], filters: dict[str, object]) -> bool:
        for key, expected in filters.items():
            current = metadata.get(key)
            if isinstance(expected, list | tuple | set):
                if current not in expected:
                    return False
            elif current != expected:
                return False
        return True
