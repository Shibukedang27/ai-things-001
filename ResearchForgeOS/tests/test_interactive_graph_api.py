from collections.abc import Generator

import pytest
from backend.core.database import Base
from backend.dependencies.database import get_db
from backend.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

GRAPH_NOTES = """
Attention Is All You Need introduced Transformer architecture and self-attention.
Attention depends on embeddings and backpropagation.
PyTorch and Python are used to implement scaled dot product attention.
Google, OpenAI, and Stanford are connected to modern Transformer research.
Retrieval Augmented Generation extends transformer systems with source evidence.
References
- Vaswani, A. (2017). Attention Is All You Need. https://example.com/attention
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
            "email": "graph-owner@example.com",
            "full_name": "Graph Owner",
            "password": "very-secure-password",
        },
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"email": "graph-owner@example.com", "password": "very-secure-password"},
    )
    assert login_response.status_code == 200
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}


def upload_document(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/documents",
        data={
            "source_text": GRAPH_NOTES,
            "source_type": "research_paper",
            "title": "Attention Is All You Need",
            "author": "Ashish Vaswani",
            "category": "Research",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def test_interactive_graph_api_lifecycle(client: TestClient) -> None:
    headers = auth_headers(client)
    document_id = upload_document(client, headers)

    graph_response = client.get("/api/v1/graph", headers=headers)
    assert graph_response.status_code == 200
    graph = graph_response.json()
    assert graph["total_nodes"] > 0
    assert graph["total_edges"] > 0
    assert graph["layout"]
    assert graph["interaction"]["supports"]["mini_map"] is True

    generate_response = client.post(f"/api/v1/graph/documents/{document_id}/generate", headers=headers)
    assert generate_response.status_code == 201

    search_response = client.get("/api/v1/graph/nodes/search", params={"query": "Attention"}, headers=headers)
    assert search_response.status_code == 200
    search_results = search_response.json()["results"]
    assert search_results
    node_id = search_results[0]["id"]

    get_node_response = client.get(f"/api/v1/graph/nodes/{node_id}", headers=headers)
    assert get_node_response.status_code == 200

    update_response = client.patch(
        f"/api/v1/graph/nodes/{node_id}",
        json={"label": "Attention Mechanism", "position_x": 120.0, "position_y": 80.0},
        headers=headers,
    )
    assert update_response.status_code == 200
    assert update_response.json()["label"] == "Attention Mechanism"

    expand_response = client.get(f"/api/v1/graph/nodes/{node_id}/expand", headers=headers)
    assert expand_response.status_code == 200
    assert expand_response.json()["nodes"]

    collapse_response = client.post(f"/api/v1/graph/nodes/{node_id}/collapse", headers=headers)
    assert collapse_response.status_code == 200
    assert collapse_response.json()["collapsed"] is True

    json_export = client.get("/api/v1/graph/export", params={"format": "json"}, headers=headers)
    assert json_export.status_code == 200
    assert json_export.json()["nodes"]

    svg_export = client.get("/api/v1/graph/export", params={"format": "svg"}, headers=headers)
    assert svg_export.status_code == 200
    assert "<svg" in svg_export.text

    png_export = client.get("/api/v1/graph/export", params={"format": "png"}, headers=headers)
    assert png_export.status_code == 200
    assert png_export.content.startswith(b"\x89PNG")

    snapshot_response = client.post(
        "/api/v1/graph/snapshots",
        json={"name": "Graph API Snapshot", "snapshot_type": "integration"},
        headers=headers,
    )
    assert snapshot_response.status_code == 201
    assert snapshot_response.json()["node_count"] > 0

    snapshots_response = client.get("/api/v1/graph/snapshots", headers=headers)
    assert snapshots_response.status_code == 200
    assert snapshots_response.json()

    delete_response = client.delete(f"/api/v1/graph/nodes/{node_id}", headers=headers)
    assert delete_response.status_code == 200
