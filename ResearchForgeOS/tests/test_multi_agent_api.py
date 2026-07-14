from collections.abc import Generator

import pytest
from backend.core.database import Base
from backend.dependencies.database import get_db
from backend.main import app
from backend.models.agent import AgentTask
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

AGENT_NOTES = """
Attention Is All You Need describes Transformer architecture for neural networks.
Attention is a mechanism for weighting token relationships in sequence modeling.
Backpropagation and embeddings are prerequisites for understanding transformer systems.
PyTorch implementations often use Gradient Descent Algorithm and loss = y - prediction / batch_size.
References
- Vaswani, A. (2017). "Attention Is All You Need". https://example.com/attention
"""


@pytest.fixture
def client_and_session() -> Generator[tuple[TestClient, sessionmaker[Session]], None, None]:
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
            yield test_client, testing_session
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)


def auth_headers(client: TestClient) -> dict[str, str]:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "agent-owner@example.com",
            "full_name": "Agent Owner",
            "password": "very-secure-password",
        },
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"email": "agent-owner@example.com", "password": "very-secure-password"},
    )
    assert login_response.status_code == 200
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}


def upload_document(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/documents",
        data={
            "source_text": AGENT_NOTES,
            "source_type": "plain_notes",
            "title": "Attention Is All You Need",
            "category": "Research",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def generate_dna(client: TestClient, headers: dict[str, str], document_id: str) -> str:
    response = client.post(f"/api/v1/knowledge-dna/documents/{document_id}/generate", headers=headers)
    assert response.status_code == 201
    return str(response.json()["id"])


def test_multi_agent_api_lifecycle(client_and_session: tuple[TestClient, sessionmaker[Session]]) -> None:
    client, session_factory = client_and_session
    headers = auth_headers(client)
    document_id = upload_document(client, headers)
    generate_dna(client, headers, document_id)

    status_response = client.get("/api/v1/agents/status", headers=headers)
    assert status_response.status_code == 200
    assert len(status_response.json()) == 10

    analysis_response = client.post(
        "/api/v1/agents/analyze",
        json={"document_id": document_id, "request_options": {"depth": "standard"}},
        headers=headers,
    )
    assert analysis_response.status_code == 201
    pipeline = analysis_response.json()
    pipeline_id = pipeline["id"]
    assert pipeline["status"] == "completed"
    assert len(pipeline["tasks"]) == 10
    assert pipeline["final_response"]["quality_review"]["validation_status"] == "passed"

    pipeline_status_response = client.get(f"/api/v1/agents/pipelines/{pipeline_id}/status", headers=headers)
    assert pipeline_status_response.status_code == 200
    assert pipeline_status_response.json()["completed_tasks"] == 10

    history_response = client.get("/api/v1/agents/history", headers=headers)
    assert history_response.status_code == 200
    assert len(history_response.json()) == 1

    task_id = str(pipeline["tasks"][0]["id"])
    retry_response = client.post(f"/api/v1/agents/tasks/{task_id}/retry", headers=headers)
    assert retry_response.status_code == 200

    pending_task_id = "pending-cancel-task"
    with session_factory() as session:
        session.add(
            AgentTask(
                id=pending_task_id,
                pipeline_id=pipeline_id,
                agent_role="research_agent",
                status="pending",
                priority=10,
                attempts=0,
                max_retries=1,
                timeout_seconds=5,
                duration_ms=0,
                task_payload={"test": True},
            )
        )
        session.commit()

    cancel_response = client.post(f"/api/v1/agents/tasks/{pending_task_id}/cancel", headers=headers)
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "canceled"
