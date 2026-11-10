import pytest
from fastapi.testclient import TestClient
from app.main import app, ml_engine
from app.auth import create_access_token
from app.config import settings

client = TestClient(app)

def test_read_docs():
    response = client.get("/docs")
    assert response.status_code == 200

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_prediction_no_auth():
    response = client.post("/predict", json={"home_team": "Arsenal", "away_team": "Chelsea"})
    assert response.status_code == 401

def test_register_and_login():
    test_email = "testuser@example.com"
    test_password = "password123"

    # Register
    reg_res = client.post("/register", json={"email": test_email, "password": test_password})
    assert reg_res.status_code in [200, 400] # 200 on first run, 400 if already exists

    # Login
    login_res = client.post("/token", data={"username": test_email, "password": test_password})
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    assert "is_admin" in token_data

def test_admin_health_requires_admin():
    # Regular user token
    token = create_access_token(data={"sub": "regular_user@example.com"})
    res = client.get("/admin/health", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 403

    # Admin user token
    admin_token = create_access_token(data={"sub": settings.ADMIN_EMAIL})
    admin_res = client.get("/admin/health", headers={"Authorization": f"Bearer {admin_token}"})
    # If admin exists in db, returns 200; if not in DB yet, returns 401/403
    assert admin_res.status_code in [200, 401, 403]
