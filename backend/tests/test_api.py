import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_read_docs():
    response = client.get("/docs")
    assert response.status_code == 200

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_admin_health_open():
    response = client.get("/admin/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_admin_stats_open():
    response = client.get("/admin/stats")
    assert response.status_code == 200
    assert "total_predictions" in response.json()

def test_simulate_match():
    response = client.post("/simulate-match", json={"home_team": "Arsenal", "away_team": "Chelsea"})
    assert response.status_code == 200
    data = response.json()
    assert "sim_probs" in data
    assert data["home_team"] == "Arsenal"
    assert "Home" in data["sim_probs"]
