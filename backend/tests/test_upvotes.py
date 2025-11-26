import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_upvote_flow():
    # 1. Register User
    email = f"upvoter_{uuid.uuid4()}@example.com"
    password = "password123"
    client.post("/auth/register", json={"email": email, "password": password, "name": "Upvoter"})
    
    # 2. Login
    login_res = client.post("/auth/login", data={"username": email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 3. Create Report
    report_res = client.post("/reports/", data={
        "title": "Upvote Test",
        "category": "Test",
        "lat": 51.505,
        "lon": -0.09
    }, headers=headers)
    report_id = report_res.json()["report_id"]
    
    # 4. Upvote Report
    upvote_res = client.post(f"/reports/{report_id}/upvote", headers=headers)
    assert upvote_res.status_code == 200
    assert upvote_res.json()["upvote_count"] == 1
    
    # 5. Verify is_upvoted in nearby
    nearby_res = client.get("/reports/nearby?lat=51.505&lon=-0.09", headers=headers)
    assert nearby_res.status_code == 200
    reports = nearby_res.json()
    target_report = next(r for r in reports if r["report_id"] == report_id)
    assert target_report["is_upvoted"] == True
    assert target_report["upvote_count"] == 1
    
    # 6. Unvote Report
    unvote_res = client.delete(f"/reports/{report_id}/unvote", headers=headers)
    assert unvote_res.status_code == 200
    assert unvote_res.json()["upvote_count"] == 0
    
    # 7. Verify is_upvoted is False
    nearby_res_2 = client.get("/reports/nearby?lat=51.505&lon=-0.09", headers=headers)
    target_report_2 = next(r for r in nearby_res_2.json() if r["report_id"] == report_id)
    assert target_report_2["is_upvoted"] == False
    assert target_report_2["upvote_count"] == 0
