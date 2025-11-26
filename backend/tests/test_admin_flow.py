import pytest
from fastapi.testclient import TestClient
from app.main import app
import uuid

client = TestClient(app)

def test_admin_flow():
    # 1. Register Admin
    email = f"admin_{uuid.uuid4()}@example.com"
    password = "password123"
    # Create admin via direct DB or special endpoint?
    # For now, register as citizen then update role manually? 
    # Or use the dev endpoint if we had one.
    # Actually, we can use the /auth/register and then maybe we need a way to make them admin.
    # In our init.sql we have a default admin. Let's use that or create a new one if we can.
    # Wait, we don't have an endpoint to promote users. 
    # Let's use the default admin credentials if possible, or assume we can create one.
    # The init.sql inserts 'admin@example.com' / 'admin123'.
    
    # Login as default admin
    login_res = client.post("/auth/login", data={"username": "admin@example.com", "password": "admin123"})
    if login_res.status_code != 200:
        # Maybe init.sql didn't run or password changed?
        # Let's try to register a new user and force role if we could, but we can't.
        # We'll assume the test DB has the seed data.
        assert login_res.status_code == 200, "Default admin login failed"
        
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # 2. Create a Report (as citizen)
    citizen_email = f"citizen_{uuid.uuid4()}@example.com"
    client.post("/auth/register", json={"email": citizen_email, "password": "password", "name": "Cit"})
    cit_login = client.post("/auth/login", data={"username": citizen_email, "password": "password"})
    cit_token = cit_login.json()["access_token"]
    cit_headers = {"Authorization": f"Bearer {cit_token}"}
    
    report_res = client.post("/reports/", data={
        "title": "Admin Flow Test",
        "category": "Test",
        "lat": 12.0,
        "lon": 77.0
    }, headers=cit_headers)
    report_id = report_res.json()["report_id"]
    
    # 3. Admin: List Reports
    list_res = client.get("/reports/?status=open", headers=headers)
    assert list_res.status_code == 200
    reports = list_res.json()
    assert any(r["report_id"] == report_id for r in reports)
    
    # 4. Admin: Assign Report
    assign_res = client.post(f"/reports/{report_id}/assign", json={
        "staff_name": "Fixer Joe",
        "staff_phone": "555-0199"
    }, headers=headers)
    assert assign_res.status_code == 200
    
    # Verify status changed to in_progress
    get_res = client.get("/reports/", headers=headers)
    target = next(r for r in get_res.json() if r["report_id"] == report_id)
    assert target["status"] == "in_progress"
    
    # 5. Admin: Update Status to Resolved
    status_res = client.patch(f"/reports/{report_id}/status", json={
        "status": "resolved",
        "note": "Fixed it"
    }, headers=headers)
    assert status_res.status_code == 200
    assert status_res.json()["status"] == "resolved"
    
    # 6. Citizen: Verify My Reports
    my_res = client.get("/reports/?scope=mine", headers=cit_headers)
    assert my_res.status_code == 200
    my_reports = my_res.json()
    assert len(my_reports) >= 1
    assert my_reports[0]["status"] == "resolved"

