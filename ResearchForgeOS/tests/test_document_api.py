from collections.abc import Generator

import pytest
from backend.core.database import Base
from backend.dependencies.database import get_db
from backend.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

SAMPLE_NOTES = """
Knowledge Graph Systems are used to connect entities, concepts, and evidence.
FastAPI exposes document APIs, PostgreSQL stores metadata, and SQLAlchemy maps database records.
JWT authentication protects document upload and document reading endpoints.
Embedding metadata is generated for every chunk in the document.
ResearchForge creates executive summaries, beginner summaries, technical summaries, and learning objectives.
References
- Doe, A. (2025). "Knowledge Graphs for Research". https://example.com/research-graphs
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


def test_document_upload_and_read_api(client: TestClient) -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "owner@example.com",
            "full_name": "Research Owner",
            "password": "very-secure-password",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"email": "owner@example.com", "password": "very-secure-password"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    upload_response = client.post(
        "/api/v1/documents",
        data={
            "source_text": SAMPLE_NOTES,
            "source_type": "plain_notes",
            "title": "Knowledge Graph Systems",
            "category": "Research",
        },
        headers=headers,
    )
    assert upload_response.status_code == 201
    uploaded = upload_response.json()
    document_id = uploaded["id"]
    assert uploaded["title"] == "Knowledge Graph Systems"
    assert uploaded["summaries"]
    assert uploaded["concepts"]
    assert uploaded["keywords"]
    assert uploaded["embeddings"]

    list_response = client.get("/api/v1/documents", headers=headers)
    assert list_response.status_code == 200
    assert len(list_response.json()) == 1

    summary_response = client.get(f"/api/v1/documents/{document_id}/summary", headers=headers)
    assert summary_response.status_code == 200
    assert len(summary_response.json()) == 6

    metadata_response = client.get(f"/api/v1/documents/{document_id}/metadata", headers=headers)
    assert metadata_response.status_code == 200
    metadata = metadata_response.json()
    assert metadata["concepts_count"] >= 1
    assert metadata["references_count"] >= 1

    delete_response = client.delete(f"/api/v1/documents/{document_id}", headers=headers)
    assert delete_response.status_code == 204
