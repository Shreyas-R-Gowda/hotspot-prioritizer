import httpx
import os
import sys

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"
CITIZEN_EMAIL = "verifier@example.com"
CITIZEN_PASSWORD = "password123"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def verify_auth():
    log("=== Starting JWT Authentication Verification ===")
    
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Test Citizen Registration
        log("1. Testing Citizen Registration...")
        # Try to register (ignore error if exists)
        resp = client.post("/auth/register", json={
            "email": CITIZEN_EMAIL,
            "password": CITIZEN_PASSWORD,
            "name": "Verifier Citizen"
        })
        
        if resp.status_code == 200:
            log("Citizen registered successfully.", "SUCCESS")
        elif resp.status_code == 400 and "already registered" in resp.text:
            log("Citizen already exists, proceeding...", "INFO")
        else:
            log(f"Registration failed: {resp.text}", "FAILURE")
            return

        # 2. Test Citizen Login
        log("\n2. Testing Citizen Login...")
        resp = client.post("/auth/login", data={
            "username": CITIZEN_EMAIL,
            "password": CITIZEN_PASSWORD
        })
        
        if resp.status_code == 200:
            citizen_token = resp.json()["access_token"]
            log("Citizen login successful. Token acquired.", "SUCCESS")
        else:
            log(f"Citizen login failed: {resp.text}", "FAILURE")
            return

        # 3. Test Protected Route Access (with token)
        log("\n3. Testing Protected Route (/auth/me) with Token...")
        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {citizen_token}"})
        if resp.status_code == 200:
            user_data = resp.json()
            if user_data["email"] == CITIZEN_EMAIL and user_data["role"] == "citizen":
                log("Protected route accessed successfully. User identity confirmed.", "SUCCESS")
            else:
                log(f"Identity mismatch: {user_data}", "FAILURE")
        else:
            log(f"Protected route access failed: {resp.text}", "FAILURE")

        # 4. Test Protected Route Access (without token)
        log("\n4. Testing Protected Route (/auth/me) WITHOUT Token...")
        resp = client.get("/auth/me")
        if resp.status_code == 401:
            log("Access denied as expected.", "SUCCESS")
        else:
            log(f"Security Breach! Access allowed without token: {resp.status_code}", "FAILURE")

        # 5. Test Admin Login
        log("\n5. Testing Admin Login...")
        resp = client.post("/auth/login", data={
            "username": ADMIN_EMAIL,
            "password": ADMIN_PASSWORD
        })
        
        if resp.status_code == 200:
            admin_token = resp.json()["access_token"]
            role = resp.json()["role"]
            if role == "admin":
                log("Admin login successful. Role confirmed.", "SUCCESS")
            else:
                log(f"Admin login returned wrong role: {role}", "FAILURE")
        else:
            log(f"Admin login failed: {resp.text}", "FAILURE")
            return

        # 6. Verify RBAC (Admin Only Route)
        # We need an admin route. Let's check /reports/{id}/status which requires admin
        # We'll try to hit it with citizen token first
        log("\n6. Testing RBAC (Admin-Only Route)...")
        
        # 6a. Citizen attempting admin action
        # Using a dummy ID 99999, we just want to see 403 Forbidden, not 404 Not Found
        # Actually reports.py: update_report_status checks DB first? 
        # deps/roles.py: require_role raises 403 BEFORE the function logic if properly depended.
        # Let's check router: update_report_status uses Depends(require_role("admin"))
        # So client should get 403 immediately.
        
        resp = client.patch("/reports/99999/status", json={"status": "resolved", "note": "test"}, headers={"Authorization": f"Bearer {citizen_token}"})
        if resp.status_code == 403:
             log("Citizen blocked from admin action (403 Forbidden).", "SUCCESS")
        else:
             log(f"RBAC failed? Citizen got: {resp.status_code} {resp.text}", "FAILURE")

        log("\n=== Verification Complete ===")

if __name__ == "__main__":
    verify_auth()
