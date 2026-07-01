import pytest
from fastapi.testclient import TestClient
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.app import app, db
from data.repositories import UserRepository

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    # We use the actual app's db but clear it and add test data
    db.create_tables()
    db.clear_database()
    u_repo = UserRepository(db)
    u_repo.create("API Test User", ["Python"], user_id=1)
    yield
    db.clear_database()

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_get_users():
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == "API Test User"

def test_get_recommendations_success():
    response = client.get("/api/recommend/1?limit=3&strategy=hybrid")
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == 1
    assert "recommendations" in data

def test_get_recommendations_invalid_user():
    response = client.get("/api/recommend/999")
    assert response.status_code == 404

def test_get_recommendations_invalid_strategy():
    response = client.get("/api/recommend/1?strategy=magic")
    assert response.status_code == 400

def test_post_feedback():
    payload = {
        "user_id": 1,
        "content_id": "C1",
        "interaction_type": "rate",
        "rating": 5
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

def test_post_feedback_invalid_rating():
    payload = {
        "user_id": 1,
        "content_id": "C1",
        "interaction_type": "rate",
        "rating": 10
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 400

def test_get_metrics():
    # Make a request first
    client.get("/api/recommend/1")
    
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert data["total_requests"] > 0
