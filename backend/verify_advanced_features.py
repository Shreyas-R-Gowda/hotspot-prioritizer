import httpx
import os
import sys
import time

# Configuration
BASE_URL = "http://localhost:8000"
CITIZEN_EMAIL = "advanced_tester@example.com"
CITIZEN_PASSWORD = "password123"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def verify_advanced():
    log("=== Verification: NLP Duplicates & Hotspots ===")
    
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Authenticate
        log("1. Authenticating...")
        client.post("/auth/register", json={
            "email": CITIZEN_EMAIL,
            "password": CITIZEN_PASSWORD,
            "name": "Advanced Tester"
        })
        resp = client.post("/auth/login", data={"username": CITIZEN_EMAIL, "password": CITIZEN_PASSWORD})
        token = resp.json().get("access_token")
        if not token:
             log("Authentication failed.", "FAILURE")
             return
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. NLP Duplicate Detection
        log("\n2. Testing Duplicate Detection...")
        
        # 2a. Create Base Report
        description_orig = "There is a massive pothole in the middle of the junction that is causing traffic jams."
        resp = client.post("/reports/", data={
            "title": "Original Pothole",
            "category": "Pothole",
            "description": description_orig,
            "lat": 12.9800,
            "lon": 77.6000,
            "road_importance": 3
        }, headers=headers)
        
        if resp.status_code == 200:
            log("Base report created.", "SUCCESS")
        else:
            log(f"Failed to create base report: {resp.text}", "FAILURE")

        # 2b. Check Duplicate (Similar text)
        # Using more overlapping words for TF-IDF sensitivity
        description_similar = "Massive pothole in the junction causing bad traffic jams."
        
        resp = client.post("/reports/check-duplicates", data={"description": description_similar}, headers=headers)
        if resp.status_code == 200:
            duplicates = resp.json()
            if len(duplicates) > 0 and duplicates[0]['title'] == "Original Pothole":
                log(f"Duplicate detected! Similarity: {duplicates[0]['similarity']}", "SUCCESS")
            else:
                log(f"Duplicate NOT detected (Count: {len(duplicates)}). NLP might need tuning.", "WARNING")
        else:
            log(f"Duplicate check failed: {resp.text}", "FAILURE")

        # 3. Geospatial Hotspot Analysis
        log("\n3. Testing Hotspot Clustering...")
        
        # Create a cluster: 2 more reports very close to the first one (0.0001 deg ~ 11m)
        client.post("/reports/", data={
            "title": "Another Pothole Here",
            "category": "Pothole",
            "description": "Same spot issues",
            "lat": 12.9801,
            "lon": 77.6001,
            "road_importance": 3
        }, headers=headers)
        
        client.post("/reports/", data={
            "title": "Traffic Nightmare",
            "category": "Pothole",
            "description": "Road broken",
            "lat": 12.9802,
            "lon": 77.5999,
            "road_importance": 3
        }, headers=headers)
        
        # Check Hotspots Endpoint
        # Reduce K to 2 to ensure clustering happens (since total reports in DB is small)
        resp = client.get("/hotspots/?method=kmeans&k=2")
        if resp.status_code == 200:
            clusters = resp.json()
            # We expect at least one cluster with count >= 3
            found_cluster = False
            for c in clusters:
                if c['report_count'] >= 3:
                     found_cluster = True
                     log(f"Cluster found! Count: {c['report_count']}, Score: {c['score']}", "SUCCESS")
                     break
            
            if not found_cluster:
                log(f"No significant cluster found in test area. Response: {len(clusters)} clusters", "FAILURE")
        else:
            log(f"Hotspot API failed: {resp.text}", "FAILURE")

    log("\n=== Advanced Verification Complete ===")

if __name__ == "__main__":
    verify_advanced()
