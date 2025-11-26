from fastapi.testclient import TestClient
from app.main import app
from app import models
import pytest

client = TestClient(app)

# Mock DB or use a test DB?
# For simplicity in MVP, we might test against the running DB or a separate one.
# Ideally we use a separate test DB.
# But setting that up requires more config.
# Let's just write the tests assuming a clean state or handling it.

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Neighborhood Hotspot Prioritizer API"}

def test_register_user():
    # Use a random email to avoid conflict
    import random
    email = f"test{random.randint(1, 100000)}@example.com"
    response = client.post(
        "/auth/register",
        json={"email": email, "password": "password", "name": "Test User"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == email
    assert "user_id" in data
    return email, "password"

def test_login_user():
    email, password = test_register_user()
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    return data["access_token"]

def test_create_report():
    token = test_login_user()
    response = client.post(
        "/reports/",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "title": "Test Report",
            "category": "Infrastructure",
            "description": "Test Description",
            "lat": 51.505,
            "lon": -0.09
        }
    )
    # Note: We are sending data as form fields, but TestClient handles it if we pass data=...
    # But we defined it as Form(...) parameters.
    # TestClient needs to send multipart/form-data if we want to match exactly or x-www-form-urlencoded.
    # If we pass data=dict, requests sends form-urlencoded.
    # If we pass files=..., it sends multipart.
    # Our endpoint expects Form(...) which works with both usually, but we added UploadFile.
    # So we should probably send as multipart.
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Report"
    assert "report_id" in data

def test_get_nearby_reports():
    # Create a report first
    test_create_report()
    
    response = client.get(
        "/reports/nearby",
        params={"lat": 51.505, "lon": -0.09, "radius_m": 1000}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert data[0]["title"] == "Test Report"
