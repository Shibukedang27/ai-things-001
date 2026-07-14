from collections.abc import Generator

import pytest
from backend.core.database import Base
from backend.dependencies.database import get_db
from backend.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool


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
            "email": "workspace-owner@example.com",
            "full_name": "Workspace Owner",
            "password": "very-secure-password",
        },
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"email": "workspace-owner@example.com", "password": "very-secure-password"},
    )
    assert login_response.status_code == 200
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}


def test_workspace_api_lifecycle(client: TestClient) -> None:
    headers = auth_headers(client)

    settings_response = client.get("/api/v1/workspace/settings", headers=headers)
    assert settings_response.status_code == 200
    assert settings_response.json()["preferences"]["auto_link_notes"] is True

    project_response = client.post(
        "/api/v1/workspace/projects",
        json={
            "title": "Transformer Research",
            "description": "Investigate attention, embeddings, and citation-grounded reasoning.",
            "research_domain": "Machine Learning",
            "goals": ["Compare RAG with long context systems"],
        },
        headers=headers,
    )
    assert project_response.status_code == 201
    project_id = project_response.json()["id"]

    collection_response = client.post(
        "/api/v1/workspace/collections",
        json={
            "name": "Attention Papers",
            "description": "Notes and resources about transformer attention.",
            "project_id": project_id,
            "tags": ["attention", "papers"],
        },
        headers=headers,
    )
    assert collection_response.status_code == 201
    collection_id = collection_response.json()["id"]

    note_response = client.post(
        "/api/v1/workspace/notes",
        json={
            "title": "Attention Reading Notes",
            "content": (
                "Attention mechanisms connect tokens through learned relevance weights. "
                "Action: compare Retrieval Augmented Generation with long-context models. "
                "FastAPI, PostgreSQL, and knowledge graphs support the workspace memory."
            ),
            "project_id": project_id,
            "collection_id": collection_id,
            "tags": ["attention", "rag"],
            "is_pinned": True,
        },
        headers=headers,
    )
    assert note_response.status_code == 201
    note = note_response.json()
    note_id = note["id"]
    assert note["summary"]
    assert note["keywords"]
    assert note["concepts"]
    assert note["action_items"]
    assert note["is_pinned"] is True

    search_response = client.post(
        "/api/v1/workspace/notes/search",
        json={"query": "attention rag", "mode": "hybrid", "tags": ["rag"], "project_id": project_id},
        headers=headers,
    )
    assert search_response.status_code == 200
    assert search_response.json()["results"][0]["note_id"] == note_id

    improve_response = client.post(
        f"/api/v1/workspace/notes/{note_id}/improve",
        json={"mode": "structure"},
        headers=headers,
    )
    assert improve_response.status_code == 200
    assert "## Summary" in improve_response.json()["improved_content"]

    writing_response = client.post(
        "/api/v1/workspace/writing/assist",
        json={"text": "attention helps models connect tokens", "mode": "technical_explanation"},
        headers=headers,
    )
    assert writing_response.status_code == 200
    assert "Technical Explanation" in writing_response.json()["output_text"]

    bookmark_response = client.post(
        "/api/v1/workspace/bookmarks",
        json={
            "target_type": "note",
            "target_id": note_id,
            "title": "Pinned attention note",
            "description": "Important note for transformer research.",
            "project_id": project_id,
            "collection_id": collection_id,
            "tags": ["attention"],
        },
        headers=headers,
    )
    assert bookmark_response.status_code == 201
    bookmark_id = bookmark_response.json()["id"]

    task_plan_response = client.post(
        "/api/v1/workspace/tasks/assistant",
        json={
            "prompt": "Create an implementation checklist for attention notes and graph-linked citations.",
            "plan_type": "implementation_checklist",
            "concepts": ["Attention"],
            "create_tasks": True,
            "project_id": project_id,
        },
        headers=headers,
    )
    assert task_plan_response.status_code == 200
    created_task_ids = task_plan_response.json()["created_task_ids"]
    assert created_task_ids

    task_update_response = client.patch(
        f"/api/v1/workspace/tasks/{created_task_ids[0]}",
        json={"status": "completed"},
        headers=headers,
    )
    assert task_update_response.status_code == 200
    assert task_update_response.json()["completed_at"] is not None

    session_response = client.post(
        "/api/v1/workspace/sessions",
        json={
            "title": "Morning Research",
            "objective": "Connect attention notes with the graph.",
            "project_id": project_id,
            "active_concepts": ["Attention"],
            "recent_note_ids": [note_id],
        },
        headers=headers,
    )
    assert session_response.status_code == 201
    session_id = session_response.json()["id"]

    canvas_a = client.post(
        "/api/v1/workspace/canvas/objects",
        json={
            "canvas_id": "research-map",
            "object_type": "note",
            "title": "Attention Note",
            "target_type": "note",
            "target_id": note_id,
            "project_id": project_id,
            "session_id": session_id,
        },
        headers=headers,
    )
    canvas_b = client.post(
        "/api/v1/workspace/canvas/objects",
        json={
            "canvas_id": "research-map",
            "object_type": "concept",
            "title": "Attention",
            "target_type": "concept",
            "project_id": project_id,
            "session_id": session_id,
            "position_x": 400,
        },
        headers=headers,
    )
    assert canvas_a.status_code == 201
    assert canvas_b.status_code == 201

    connect_response = client.post(
        f"/api/v1/workspace/canvas/objects/{canvas_a.json()['id']}/connect",
        json={"target_object_id": canvas_b.json()["id"], "relationship_type": "explains", "label": "Explains"},
        headers=headers,
    )
    assert connect_response.status_code == 200
    assert connect_response.json()["connections"]

    timeline_response = client.get("/api/v1/workspace/timeline", headers=headers)
    assert timeline_response.status_code == 200
    assert timeline_response.json()["items"]

    graph_search_response = client.get(
        "/api/v1/graph/nodes/search",
        params={"query": "Attention Reading Notes"},
        headers=headers,
    )
    assert graph_search_response.status_code == 200
    assert any(item["node_type"] == "note" for item in graph_search_response.json()["results"])

    overview_response = client.get("/api/v1/workspace", headers=headers)
    assert overview_response.status_code == 200
    assert overview_response.json()["pinned_notes"]

    delete_bookmark_response = client.delete(f"/api/v1/workspace/bookmarks/{bookmark_id}", headers=headers)
    assert delete_bookmark_response.status_code == 200
