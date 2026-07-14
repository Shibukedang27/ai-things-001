from retrieval.vector_store.base import VectorStore
from retrieval.vector_store.chroma import ChromaVectorStore
from retrieval.vector_store.memory import InMemoryVectorStore


def create_vector_store(*, backend: str, persist_directory: str = ".chroma") -> VectorStore:
    normalized_backend = backend.strip().lower()
    if normalized_backend == "chroma":
        return ChromaVectorStore(persist_directory=persist_directory)
    return InMemoryVectorStore()
