from fastapi.testclient import TestClient
from app.main import app
from app import models
from app.database import SessionLocal, engine
import pytest

# Create tables
models.Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_auth_flow():
    # 1. Register Citizen
    import uuid
    citizen_email = f"citizen_{uuid.uuid4()}@example.com"
    response = client.post("/auth/register", json={
        "email": citizen_email,
        "password": "password123",
        "name": "Citizen Test"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == citizen_email
    assert data["role"] == "citizen"

    # 2. Login Citizen
    response = client.post("/auth/login", data={
        "username": citizen_email,
        "password": "password123"
    })
    assert response.status_code == 200
    citizen_token = response.json()["access_token"]
    role = response.json()["role"]
    assert role == "citizen"

    # 3. Login Admin (Seeded)
    response = client.post("/auth/login", data={
        "username": "admin@example.com",
        "password": "admin123"
    })
    assert response.status_code == 200
    admin_token = response.json()["access_token"]
    role = response.json()["role"]
    assert role == "admin"

    # 4. Access Admin Endpoint as Citizen
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {citizen_token}"})
    assert response.status_code == 403

    # 5. Access Admin Endpoint as Admin
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert response.status_code == 200
    users = response.json()
    assert len(users) >= 2 # Admin + Citizen
