from collections.abc import Generator

import pytest
from backend.core.database import Base
from backend.dependencies.database import get_db
from backend.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

ATTENTION_NOTES = """
Attention Is All You Need introduced the Transformer architecture.
Self-attention compares token relationships and improves sequence modeling.
Backpropagation and embeddings are prerequisites for training neural networks.
PyTorch implementations use attention masks, gradient descent, and batched matrix multiplication.
References
- Vaswani, A. (2017). Attention Is All You Need. https://example.com/attention
"""

RAG_NOTES = """
Retrieval Augmented Generation combines vector search with generated answers.
The retrieval stage finds source evidence, validates citations, and helps reduce hallucination.
ChromaDB collections store embeddings and PostgreSQL stores metadata for production systems.
References
- Lewis, P. (2020). Retrieval-Augmented Generation. https://example.com/rag
"""


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite+pysqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    testing_session = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

    def _get_db() -> Generator[Session, None, None]:
        session = testing_session()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _get_db
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


def auth_headers(client: TestClient) -> dict[str, str]:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "retrieval-owner@example.com",
            "full_name": "Retrieval Owner",
            "password": "very-secure-password",
        },
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"email": "retrieval-owner@example.com", "password": "very-secure-password"},
    )
    assert login_response.status_code == 200
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}


def upload_document(client: TestClient, headers: dict[str, str], title: str, source_text: str) -> str:
    response = client.post(
        "/api/v1/documents",
        data={
            "source_text": source_text,
            "source_type": "plain_notes",
            "title": title,
            "category": "Research",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def test_retrieval_api_lifecycle(client: TestClient) -> None:
    headers = auth_headers(client)
    upload_document(client, headers, "Attention Is All You Need", ATTENTION_NOTES)
    upload_document(client, headers, "Retrieval Augmented Generation", RAG_NOTES)

    payload = {
        "query": "Compare transformer attention and retrieval augmented generation for research systems",
        "top_k": 5,
        "max_context_characters": 800,
    }
    ask_response = client.post("/api/v1/retrieval/ask", json=payload, headers=headers)
    assert ask_response.status_code == 201
    answer = ask_response.json()
    history_id = answer["history_id"]
    assert answer["intent"] == "comparison"
    assert answer["confidence_score"] > 0
    assert answer["citations"]
    assert answer["retrieved_sections"]
    assert answer["reasoning_path"]

    cached_response = client.post("/api/v1/retrieval/ask", json=payload, headers=headers)
    assert cached_response.status_code == 201
    assert cached_response.json()["cache_hit"] is True

    for endpoint in ("hybrid", "semantic", "keyword"):
        response = client.post(f"/api/v1/retrieval/search/{endpoint}", json=payload, headers=headers)
        assert response.status_code == 200
        assert response.json()["results"]

    related_response = client.post("/api/v1/retrieval/related-concepts", json=payload, headers=headers)
    assert related_response.status_code == 200
    assert related_response.json()["concepts"]

    history_response = client.get("/api/v1/retrieval/history", headers=headers)
    assert history_response.status_code == 200
    assert history_response.json()

    citations_response = client.get(f"/api/v1/retrieval/citations/{history_id}", headers=headers)
    assert citations_response.status_code == 200
    assert citations_response.json()["citations"]

    stream_response = client.post("/api/v1/retrieval/ask/stream", json=payload, headers=headers)
    assert stream_response.status_code == 200
    assert "answer" in stream_response.text
