import hashlib
import math

from knowledge_engine.types import EmbeddingRecord, TextChunk


class EmbeddingService:
    MODEL_NAME = "researchforge-hash-embedding-v1"

    def __init__(self, dimensions: int = 384) -> None:
        self.dimensions = dimensions

    def embed_chunks(self, chunks: list[TextChunk]) -> list[EmbeddingRecord]:
        return [
            EmbeddingRecord(
                chunk_index=chunk.index,
                embedding_model=self.MODEL_NAME,
                embedding_dimensions=self.dimensions,
                vector=self._embed_text(chunk.content),
                content_hash=chunk.content_hash,
                metadata={"token_count": chunk.token_count, "start_char": chunk.start_char, "end_char": chunk.end_char},
            )
            for chunk in chunks
        ]

    def _embed_text(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in text.lower().split():
            digest = hashlib.sha256(token.encode("utf-8", errors="ignore")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [round(value / norm, 6) for value in vector]
