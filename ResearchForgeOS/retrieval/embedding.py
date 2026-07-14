import hashlib
import math

from retrieval.utils import stable_hash, tokenize


class EmbeddingCache:
    def __init__(self) -> None:
        self._vectors: dict[str, list[float]] = {}

    def get(self, key: str) -> list[float] | None:
        vector = self._vectors.get(key)
        return list(vector) if vector is not None else None

    def set(self, key: str, vector: list[float]) -> None:
        self._vectors[key] = list(vector)

    def clear(self) -> None:
        self._vectors.clear()


class RetrievalEmbeddingService:
    model_name = "researchforge-hybrid-embedding-v1"

    def __init__(self, dimensions: int = 384, cache: EmbeddingCache | None = None) -> None:
        self.dimensions = dimensions
        self.cache = cache or EmbeddingCache()

    def embed_text(self, text: str) -> list[float]:
        cache_key = stable_hash(self.model_name, self.dimensions, text)
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        vector = [0.0] * self.dimensions
        for token in tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8", errors="ignore")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        normalized = vector if norm == 0 else [round(value / norm, 6) for value in vector]
        self.cache.set(cache_key, normalized)
        return normalized

    def embed_many(self, texts: list[str]) -> list[list[float]]:
        return [self.embed_text(text) for text in texts]
