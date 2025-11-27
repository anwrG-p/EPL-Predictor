from fastapi.testclient import TestClient
from app.main import app
from app.auth import create_access_token

client = TestClient(app)

def test_read_main():
    response = client.get("/docs")
    assert response.status_code == 200

def test_prediction_no_auth():
    response = client.post("/predict", json={"home_team": "Arsenal", "away_team": "Chelsea"})
    assert response.status_code == 401
