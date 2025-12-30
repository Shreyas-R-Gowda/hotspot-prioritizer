import httpx
import os
import sys

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def verify_admin():
    log("=== Verification: Admin Dashboard Capabilities ===")
    
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Login as Admin
        log("1. Authenticating as Admin...")
        resp = client.post("/auth/login", data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        if resp.status_code != 200:
             log(f"Admin login failed: {resp.text}", "FAILURE")
             return
        
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        log("Authenticated successfully.", "SUCCESS")

        # 2. Track Reports (List View)
        log("\n2. Fetching Reports (Dashboard View)...")
        resp = client.get("/reports/", headers=headers, params={"limit": 5})
        if resp.status_code == 200:
            reports = resp.json()
            log(f"Fetched {len(reports)} reports.", "SUCCESS")
            if len(reports) > 0:
                report_id = reports[0]['report_id']
                log(f"Targeting Report ID: {report_id} for updates.", "INFO")
            else:
                log("No reports found to update. Creating one...", "WARNING")
                # Create one quickly
                client.post("/reports/", data={"title":"Admin Test","category":"Pothole","lat":12,"lon":77,"road_importance":1}, headers=headers)
                resp = client.get("/reports/", headers=headers)
                report_id = resp.json()[0]['report_id']
        else:
            log(f"Fetch failed: {resp.text}", "FAILURE")
            return

        # 3. Update Status
        log("\n3. Updating Status (Open -> In Progress)...")
        resp = client.patch(f"/reports/{report_id}/status", json={"status": "in_progress", "note": "Admin verifying"}, headers=headers)
        if resp.status_code == 200:
            new_status = resp.json()['status']
            if new_status == "in_progress":
                log("Status updated successfully.", "SUCCESS")
            else:
                log(f"Status update mismatch: {new_status}", "FAILURE")
        else:
             log(f"Status update failed: {resp.text}", "FAILURE")

        # 4. Assign Task
        log("\n4. Assigning Repair Task...")
        resp = client.post(f"/reports/{report_id}/assign", json={
            "staff_name": "Bob The Builder",
            "staff_phone": "555-0199",
            "expected_resolution_date": "2025-01-01T00:00:00"
        }, headers=headers)
        
        if resp.status_code == 200:
            log("Task assigned successfully.", "SUCCESS")
        else:
            log(f"Assignment failed: {resp.text}", "FAILURE")

        # 5. Export Data
        log("\n5. Exporting Hotspots CSV...")
        resp = client.get("/hotspots/export", headers=headers)
        if resp.status_code == 200:
            content = resp.text
            if "HOTSPOT_ID,LATITUDE" in content:
                log("CSV Export validated (headers found).", "SUCCESS")
                log(f"CSV Size: {len(content)} bytes", "INFO")
            else:
                log("CSV Export content invalid.", "FAILURE")
        else:
             log(f"Export failed: {resp.text}", "FAILURE")

    log("\n=== Admin Verification Complete ===")

if __name__ == "__main__":
    verify_admin()
