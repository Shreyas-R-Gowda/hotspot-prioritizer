import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db
from app.models import User, Report
from app.deps.roles import get_current_user
import os

# Use a separate test database or the same one if careful
# For simplicity in this environment, we'll use the main one but be careful
# Actually, let's mock the DB or use a temporary SQLite for speed if possible, 
# but we need PostGIS. So we must use the Postgres DB.
# We will assume the DB is running (docker-compose up).

SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/hotspot_db")

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def test_user_token():
    # Register a user
    email = "test_report_user@example.com"
    password = "password123"
    
    # Try login first
    response = client.post("/auth/login", data={"username": email, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
        
    # Register if not exists
    client.post("/auth/register", json={"email": email, "password": password, "name": "Test User"})
    response = client.post("/auth/login", data={"username": email, "password": password})
    return response.json()["access_token"]

def test_create_report_with_image(test_user_token):
    # Create a dummy image file
    with open("test_image.jpg", "wb") as f:
        f.write(b"dummy image content")
        
    with open("test_image.jpg", "rb") as f:
        response = client.post(
            "/reports/",
            data={
                "title": "Test Report with Image",
                "category": "Trash",
                "description": "Testing image upload",
                "lat": 51.505,
                "lon": -0.09
            },
            files={"image": ("test_image.jpg", f, "image/jpeg")},
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
    
    # Cleanup
    os.remove("test_image.jpg")
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Report with Image"
    assert len(data["images"]) == 1
    assert data["images"][0].startswith("/media/")

def test_get_nearby_reports(test_user_token):
    # Ensure we have at least one report (created above)
    response = client.get(
        "/reports/nearby",
        params={"lat": 51.505, "lon": -0.09, "radius_m": 1000},
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    # Check if images field exists
    assert "images" in data[0]
    assert isinstance(data[0]["images"], list)
