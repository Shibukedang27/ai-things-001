from collections.abc import Generator

import pytest
from backend.core.database import Base
from backend.dependencies.database import get_db
from backend.main import app
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

SAMPLE_LEARNING_NOTES = """
Transformer attention systems compare token relationships with query, key, and value projections.
Self Attention is a mechanism where each token attends to other tokens in the same sequence.
Scaled Dot Product Attention computes scores with softmax(QK^T / sqrt(d_k))V.
Multi Head Attention runs several attention projections in parallel to capture different relationships.
Python and PyTorch are common technologies for implementing attention models.
FastAPI can expose backend services for adaptive learning and knowledge review workflows.
Algorithm: Scaled Dot Product Attention
Steps: project queries keys values, compute similarity scores, normalize scores, weight values.
Code:
scores = q @ k.T
weights = softmax(scores)
output = weights @ v
References
- Vaswani, A. (2017). Attention Is All You Need.
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
            "email": "adaptive-owner@example.com",
            "full_name": "Adaptive Owner",
            "password": "very-secure-password",
        },
    )
    assert register_response.status_code == 201
    login_response = client.post(
        "/api/v1/auth/login/json",
        json={"email": "adaptive-owner@example.com", "password": "very-secure-password"},
    )
    assert login_response.status_code == 200
    return {"Authorization": f"Bearer {login_response.json()['access_token']}"}


def upload_document(client: TestClient, headers: dict[str, str]) -> str:
    response = client.post(
        "/api/v1/documents",
        data={
            "source_text": SAMPLE_LEARNING_NOTES,
            "source_type": "plain_notes",
            "title": "Transformer Attention Systems",
            "category": "Machine Learning",
        },
        headers=headers,
    )
    assert response.status_code == 201
    return str(response.json()["id"])


def test_adaptive_learning_api_lifecycle(client: TestClient) -> None:
    headers = auth_headers(client)
    document_id = upload_document(client, headers)

    flashcards_response = client.get(f"/api/v1/learning/documents/{document_id}/flashcards", headers=headers)
    assert flashcards_response.status_code == 200
    flashcards = flashcards_response.json()
    assert flashcards
    assert {"concept", "interview", "true_false"}.intersection({card["card_type"] for card in flashcards})

    bundle_response = client.post(
        f"/api/v1/learning/documents/{document_id}/generate",
        json={"force": False},
        headers=headers,
    )
    assert bundle_response.status_code == 201
    bundle = bundle_response.json()
    assert bundle["flashcards"]
    assert bundle["quiz"]["questions"]
    assert bundle["interview_questions"]
    assert bundle["coding_challenges"]
    assert bundle["revision_plans"]
    assert bundle["progress"]["total_items"] > 0

    quiz_response = client.post(
        f"/api/v1/learning/documents/{document_id}/quizzes/generate",
        json={"difficulty": "medium", "question_limit": 8},
        headers=headers,
    )
    assert quiz_response.status_code == 201
    quiz = quiz_response.json()
    quiz_id = quiz["id"]
    assert quiz["adaptive"] is True
    assert quiz["questions"]

    start_response = client.post(f"/api/v1/learning/quizzes/{quiz_id}/start", headers=headers)
    assert start_response.status_code == 201
    attempt_id = start_response.json()["attempt"]["id"]
    answers = {question["id"]: question["correct_answers"] for question in quiz["questions"]}

    submit_response = client.post(
        f"/api/v1/learning/quiz-attempts/{attempt_id}/submit",
        json={"answers": answers, "time_spent_seconds": 180},
        headers=headers,
    )
    assert submit_response.status_code == 200
    submitted = submit_response.json()
    assert submitted["attempt"]["passed"] is True
    assert submitted["progress"]["quiz_accuracy"] == 1.0
    assert submitted["certificate"] is not None

    review_response = client.post(
        "/api/v1/learning/flashcards/review",
        json={
            "reviews": [
                {
                    "flashcard_id": flashcards[0]["id"],
                    "rating": "easy",
                    "confidence": 0.92,
                    "response_quality": 0.9,
                    "duration_ms": 1200,
                }
            ]
        },
        headers=headers,
    )
    assert review_response.status_code == 200
    assert review_response.json()["memory"][0]["review_count"] == 1

    progress_response = client.get(
        "/api/v1/learning/progress",
        params={"document_id": document_id},
        headers=headers,
    )
    assert progress_response.status_code == 200
    assert progress_response.json()["progress"][0]["knowledge_score"] >= 0

    revision_response = client.post(
        f"/api/v1/learning/documents/{document_id}/revision-plan",
        json={"plan_type": "interview"},
        headers=headers,
    )
    assert revision_response.status_code == 201
    assert revision_response.json()["plan_type"] == "interview"

    coding_response = client.get(f"/api/v1/learning/documents/{document_id}/coding-challenges", headers=headers)
    assert coding_response.status_code == 200
    assert coding_response.json()

    interview_response = client.get(f"/api/v1/learning/documents/{document_id}/interview-questions", headers=headers)
    assert interview_response.status_code == 200
    assert interview_response.json()

    achievements_response = client.get("/api/v1/learning/achievements", headers=headers)
    assert achievements_response.status_code == 200
    assert achievements_response.json()

    certificates_response = client.get("/api/v1/learning/certificates", headers=headers)
    assert certificates_response.status_code == 200
    assert certificates_response.json()
