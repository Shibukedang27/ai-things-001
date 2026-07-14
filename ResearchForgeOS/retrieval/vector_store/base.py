from dataclasses import dataclass, field
from typing import Protocol


@dataclass(frozen=True)
class VectorRecord:
    id: str
    collection_name: str
    namespace: str
    embedding: list[float]
    document: str
    metadata: dict[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class VectorSearchResult:
    id: str
    score: float
    document: str
    metadata: dict[str, object]


class VectorStore(Protocol):
    def upsert(self, records: list[VectorRecord]) -> None:
        ...

    def query(
        self,
        *,
        collection_name: str,
        namespace: str,
        embedding: list[float],
        top_k: int,
        filters: dict[str, object] | None = None,
    ) -> list[VectorSearchResult]:
        ...

    def delete_document(self, *, collection_name: str, namespace: str, document_id: str) -> None:
        ...

    def optimize(self, *, collection_name: str, namespace: str) -> None:
        ...
