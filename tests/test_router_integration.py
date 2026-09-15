"""Integration coverage for authenticated FastAPI routers."""

from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

os.environ["DATABASE_URL"] = f"sqlite:///{Path(__file__).with_name('router_integration.sqlite3')}"
os.environ["SECRET_KEY"] = "integration-test-secret"
os.environ["ENV"] = "test"

from backend.auth import create_access_token, hash_password  # noqa: E402
from backend.database import Base  # noqa: E402
from backend.dependencies import get_db as dependency_get_db  # noqa: E402
from backend.models import User, UserProfile  # noqa: E402
from backend.database import get_db as database_get_db  # noqa: E402
from backend.main import app  # noqa: E402


TEST_DATABASE = create_engine(os.environ["DATABASE_URL"])
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_DATABASE)
Base.metadata.create_all(bind=TEST_DATABASE)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[dependency_get_db] = override_get_db
app.dependency_overrides[database_get_db] = override_get_db


@pytest.fixture()
def client_and_token():
    db = TestingSessionLocal()
    user = User(
        username=f"integration_{datetime.utcnow().timestamp()}",
        email=f"integration_{datetime.utcnow().timestamp()}@example.com",
        hashed_password=hash_password("Password123!"),
        age=30,
        fitness_level="beginner",
        goal="general_fitness",
        onboarding_complete=True,
    )
    db.add(user)
    db.flush()
    db.add(
        UserProfile(
            user_id=user.id,
            age=30,
            gender="other",
            height_cm=175,
            weight_kg=70,
            bmi=22.9,
            fitness_level="beginner",
            goal="general_fitness",
            has_equipment=False,
            equipment_list=[],
            days_per_week=3,
            workout_duration_minutes=30,
            preferred_time="Morning (8-11am)",
            onboarding_complete=True,
        )
    )
    db.commit()
    token = create_access_token({"sub": user.id})
    db.close()

    with TestClient(app) as client:
        yield client, token

    cleanup = TestingSessionLocal()
    cleanup.query(User).filter(User.id == user.id).delete(synchronize_session=False)
    cleanup.commit()
    cleanup.close()


def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_sessions_router_happy_path(client_and_token) -> None:
    client, token = client_and_token
    response = client.post(
        "/sessions/",
        headers=auth_headers(token),
        json={
            "exercise_type": "Squat",
            "total_reps": 10,
            "correct_reps": 8,
            "incorrect_reps": 2,
            "posture_accuracy": None,
            "duration_seconds": 120,
        },
    )
    assert response.status_code == 200
    assert response.json()["posture_accuracy"] == 80.0


def test_sessions_router_requires_auth(client_and_token) -> None:
    client, _ = client_and_token
    assert client.get("/sessions/").status_code == 401


def test_recommendations_router_happy_path(client_and_token) -> None:
    client, token = client_and_token
    response = client.get("/recommendations/plan", headers=auth_headers(token))
    assert response.status_code == 200
    assert isinstance(response.json(), dict)


def test_recommendations_router_requires_auth(client_and_token) -> None:
    client, _ = client_and_token
    assert client.get("/recommendations/plan").status_code == 401


def test_analytics_router_happy_path(client_and_token) -> None:
    client, token = client_and_token
    response = client.get("/analytics/summary", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["total_sessions"] == 0


def test_analytics_router_requires_auth(client_and_token) -> None:
    client, _ = client_and_token
    assert client.get("/analytics/summary").status_code == 401


def test_onboarding_router_happy_path(client_and_token) -> None:
    client, token = client_and_token
    response = client.get("/onboarding/profile", headers=auth_headers(token))
    assert response.status_code == 200
    assert response.json()["bmi"] == 22.9


def test_onboarding_router_requires_auth(client_and_token) -> None:
    client, _ = client_and_token
    assert client.get("/onboarding/profile").status_code == 401


def test_pose_router_happy_path(client_and_token) -> None:
    client, token = client_and_token
    response = client.post(
        "/pose/analyse-frame",
        headers=auth_headers(token),
        data={"exercise": "Squat", "session_id": "integration-session"},
        files={"file": ("frame.jpg", b"not-a-real-image", "image/jpeg")},
    )
    assert response.status_code == 200
    assert response.json()["feedback"] == "Invalid image"


def test_pose_router_requires_auth(client_and_token) -> None:
    client, _ = client_and_token
    response = client.post(
        "/pose/analyse-frame",
        data={"exercise": "Squat", "session_id": "integration-session"},
        files={"file": ("frame.jpg", b"not-a-real-image", "image/jpeg")},
    )
    assert response.status_code == 401
