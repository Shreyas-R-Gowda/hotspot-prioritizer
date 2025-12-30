import httpx
import os
import sys

# Configuration
BASE_URL = "http://localhost:8000"
CITIZEN_EMAIL = "scorer@example.com"
CITIZEN_PASSWORD = "password123"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def verify_scoring():
    log("=== Verification: Priority Scoring Mechanism ===")
    
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Authenticate
        log("1. Authenticating...")
        client.post("/auth/register", json={
            "email": CITIZEN_EMAIL,
            "password": CITIZEN_PASSWORD,
            "name": "Scoring Tester"
        })
        resp = client.post("/auth/login", data={"username": CITIZEN_EMAIL, "password": CITIZEN_PASSWORD})
        token = resp.json().get("access_token")
        if not token:
             log("Authentication failed.", "FAILURE")
             return
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Create High Priority Report
        # High Sev (10), Road Imp (10 - Highway), Recent (10), Upvotes (will add 5)
        # Score approx: (10*0.35) + (5*0.25) + (10*0.2) + (10*0.2) = 3.5 + 1.25 + 2 + 2 = 8.75
        log("\n2. Creating HIGH Priority Report...")
        resp = client.post("/reports/", data={
            "title": "High Priority Danger",
            "category": "Pothole",
            "description": "Massive hole on highway",
            "lat": 13.0000,
            "lon": 77.0000,
            "road_importance": 10 
        }, headers=headers)
        
        if resp.status_code == 200:
            high_id = resp.json()['report_id']
            # Force Severity to High manually (since we didn't use image AI here)
            # We can use admin endpoint or just trust the DB default if we could set it.
            # Reports endpoint doesn't allow setting severity on create directly unless via AI.
            # BUT we can assume 'Medium' (5) by default if no image.
            # Let's use the update endpoint with admin to force it, or just accept Medium.
            # Let's try to simulate Upvotes.
            for i in range(5):
                client.post(f"/reports/{high_id}/upvote", headers=headers) # Self upvote repeated? 
                # Logic prevents duplicate upvotes from same user. 
                # So upvote count will be 1 max with single user.
                # Use SQL or assume count=1.
                pass
            
            # Let's manually upvote via SQL injection in `verify_features` style? No, keep it pure API.
            # We will rely on Road Importance (10 vs 1) to drive the diff.
        else:
             log(f"Failed to create report: {resp.text}", "FAILURE")
             return

        # 3. Create Low Priority Report
        # Medium Sev (5), Road Imp (1 - Street), Recent (10), Upvotes (0)
        # Score approx: (5*0.35) + (0*0.25) + (10*0.2) + (1*0.2) = 1.75 + 0 + 2 + 0.2 = 3.95
        log("\n3. Creating LOW Priority Report...")
        resp = client.post("/reports/", data={
            "title": "Low Priority Scratch",
            "category": "Pothole",
            "description": "Small scratch",
            "lat": 13.0005, # Close enough to cluster if K is small, but let's keep separate
            "lon": 77.0005,
            "road_importance": 1
        }, headers=headers)
        low_id = resp.json()['report_id']

        # 4. Check Scores via Hotspots
        # We need them to NOT cluster together to see individual scores, OR check the cluster score if they do.
        # 13.0000/77.0000 and 13.0005/77.0005 are ~50m apart.
        # K-Means=2 should separate them if they are the only ones there.
        # Or we can check if the High one is top of its cluster.
        
        log("\n4. Verifying Scores...")
        resp = client.get("/hotspots/?method=kmeans&k=5") # ample K
        if resp.status_code == 200:
            clusters = resp.json()
            high_found = False
            low_found = False
            
            for c in clusters:
                # Identify via title
                if c['title'] == "High Priority Danger":
                    high_score = c['score']
                    log(f"High Priority Score: {high_score}", "INFO")
                    high_found = True
                    
                if c['title'] == "Low Priority Scratch":
                    low_score = c['score']
                    log(f"Low Priority Score: {low_score}", "INFO")
                    low_found = True
            
            if high_found and low_found:
                if high_score > low_score:
                    log("SUCCESS: High priority report scored higher than low priority.", "SUCCESS")
                else:
                    log("FAILURE: Scoring logic weird. High <= Low.", "FAILURE")
            else:
                log(f"Could not find both reports in hotspots. (High: {high_found}, Low: {low_found})", "WARNING")
        else:
             log(f"Hotspot API failed: {resp.text}", "FAILURE")

    log("\n=== Scoring Verification Complete ===")

if __name__ == "__main__":
    verify_scoring()
