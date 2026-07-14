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
Attention Is All You Need explains Transformer architecture for neural networks.
Attention is a mechanism for weighting token relationships in sequence modeling.
Backpropagation and embeddings are prerequisites for understanding transformers.
PyTorch implementations often use Gradient Descent Algorithm and loss = y - prediction / batch_size.
OpenAI and Google use transformer models in industry systems.
References
- Vaswani, A. (2017). "Attention Is All You Need". https://example.com/attention
"""

RAG_NOTES = """
Retrieval Augmented Generation extends Transformer systems with vector search and embeddings.
Attention remains important because retrieved chunks are combined with language models.
PyTorch, PostgreSQL, and vector databases are often used in production implementations.
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
            "email": "dna-owner@example.com",
            "full_name": "DNA Owner",
            "password": "very-secure-password",
        },
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"email": "dna-owner@example.com", "password": "very-secure-password"},
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


def test_knowledge_dna_api_lifecycle(client: TestClient) -> None:
    headers = auth_headers(client)
    primary_document_id = upload_document(client, headers, "Attention Is All You Need", ATTENTION_NOTES)
    upload_document(client, headers, "Retrieval Augmented Generation", RAG_NOTES)

    generate_response = client.post(
        f"/api/v1/knowledge-dna/documents/{primary_document_id}/generate",
        headers=headers,
    )
    assert generate_response.status_code == 201
    dna = generate_response.json()
    dna_id = dna["id"]
    assert dna["document_title"] == "Attention Is All You Need"
    assert dna["knowledge_score"] > 0
    assert dna["nodes"]
    assert dna["edges"]
    assert dna["learning_path_steps"]
    assert dna["prerequisite_items"]

    get_response = client.get(f"/api/v1/knowledge-dna/documents/{primary_document_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["id"] == dna_id

    learning_path_response = client.get(
        f"/api/v1/knowledge-dna/documents/{primary_document_id}/learning-path",
        headers=headers,
    )
    assert learning_path_response.status_code == 200
    assert learning_path_response.json()

    related_topics_response = client.get(
        f"/api/v1/knowledge-dna/documents/{primary_document_id}/related-topics",
        headers=headers,
    )
    assert related_topics_response.status_code == 200
    assert related_topics_response.json()

    prerequisites_response = client.get(
        f"/api/v1/knowledge-dna/documents/{primary_document_id}/prerequisites",
        headers=headers,
    )
    assert prerequisites_response.status_code == 200
    assert prerequisites_response.json()

    update_response = client.patch(
        f"/api/v1/knowledge-dna/{dna_id}",
        json={"research_category": "Artificial Intelligence", "interview_importance": 0.95},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["research_category"] == "Artificial Intelligence"
    assert update_response.json()["interview_importance"] == 0.95

    delete_response = client.delete(f"/api/v1/knowledge-dna/{dna_id}", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["message"] == "Knowledge DNA deleted."
