import httpx
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import time
import sys
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Internal Docker URLs
BASE_URL = "http://localhost:8000"
# Connect to 'db' service on internal port 5432
DATABASE_URL = "postgresql://postgres:password@db:5432/hotspot_db"

def get_db_connection():
    return create_engine(DATABASE_URL).connect()

def verify():
    print("=== Starting Verification (Internal) ===")
    
    # 1. Setup Data
    print("\n[1] Setting up test data...")
    try:
        with get_db_connection() as conn:
            conn.execute(text("TRUNCATE TABLE reports, users, upvotes CASCADE"))
            conn.commit()
            
            # Create User
            conn.execute(text("INSERT INTO users (name, email, password_hash, role) VALUES ('Test User', 'test@example.com', 'hashed_pw', 'citizen')"))
            conn.commit()
            user_id = conn.execute(text("SELECT user_id FROM users WHERE email='test@example.com'")).scalar()
            
            # Create Reports
            # Report A: High Severity (10), Recent, 10 Upvotes
            conn.execute(text(f"""
                INSERT INTO reports (user_id, category, title, description, location, severity, upvote_count, created_at, status, updated_at)
                VALUES ({user_id}, 'Pothole', 'High Priority Pothole', 'Dangerous', ST_SetSRID(ST_MakePoint(77.5946, 12.9716), 4326), 'High', 10, NOW(), 'open', NOW())
            """))
            
            # Report B: Low Severity (2), Old, 0 Upvotes
            conn.execute(text(f"""
                INSERT INTO reports (user_id, category, title, description, location, severity, upvote_count, created_at, status, updated_at)
                VALUES ({user_id}, 'Pothole', 'Low Priority Pothole', 'Small crack', ST_SetSRID(ST_MakePoint(77.5950, 12.9720), 4326), 'Low', 0, NOW() - INTERVAL '30 DAYS', 'open', NOW())
            """))
            
            # Report C: Resolved Report for Analytics
            # Created 25 hours ago, Resolved 30 mins ago (~24.5 hours resolution)
            conn.execute(text(f"""
                INSERT INTO reports (user_id, category, title, description, location, severity, upvote_count, created_at, status, updated_at)
                VALUES ({user_id}, 'Cleanup', 'Resolved Item', 'Done', ST_SetSRID(ST_MakePoint(77.5960, 12.9730), 4326), 'Medium', 5, NOW() - INTERVAL '25 HOURS', 'resolved', NOW() - INTERVAL '30 MINUTES')
            """))
            
            # Create Admin User
            admin_hash = pwd_context.hash("password123")
            conn.execute(text(f"INSERT INTO users (name, email, password_hash, role) VALUES ('Admin', 'admin@example.com', '{admin_hash}', 'admin')"))
            
            conn.commit()
            print("Test data inserted.")
    except Exception as e:
        print(f"DB Connection Failed: {e}")
        return

    # 2. Test Hotspots (Priority Scoring)
    print("\n[2] Testing /hotspots endpoint...")
    try:
        # Trailing slash is important for FastAPI router with Prefix
        response = httpx.get(f"{BASE_URL}/hotspots/?method=kmeans&k=5")
        if response.status_code == 200:
            hotspots = response.json()
            if len(hotspots) > 0:
                top = hotspots[0]
                score = float(top.get('score', 0))
                print(f"Top Hotspot Score: {score}")
                if score > 5:
                    print("SUCCESS: Priority scoring working.")
                else:
                    print("FAILURE: Score too low.")
            else:
                print("FAILURE: No hotspots found.")
        else:
            print(f"FAILURE: API {response.status_code}")
    except Exception as e:
        print(f"FAILURE: {e}")

    # 3. Test Duplicates
    print("\n[3] Testing Duplicates (Fuzzy Match)...")
    try:
        # "Dangerous" matches "High Priority Pothole" description "Dangerous" -> exact hit or high similarity
        response = httpx.post(f"{BASE_URL}/reports/check-duplicates", data={"description": "Dangerous"})
        duplicates = response.json()
        if len(duplicates) > 0:
            print(f"Found {len(duplicates)} duplicates. Top match: {duplicates[0]['title']} ({duplicates[0]['similarity']})")
            if duplicates[0]['similarity'] >= 0.6:
                print("SUCCESS: Duplicate detected.")
            else:
                 print("FAILURE: Low similarity.")
        else:
            print("FAILURE: No duplicates found.")
    except Exception as e:
        print(f"FAILURE: {e}")

    # 4. Test Analytics
    print("\n[4] Testing Analytics (Resolution Time)...")
    try:
        # Login
        login_resp = httpx.post(f"{BASE_URL}/auth/login", data={"username": "admin@example.com", "password": "password123"})
        if login_resp.status_code != 200:
             print(f"Login Failed: {login_resp.text}")
        else:
            token = login_resp.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            
            response = httpx.get(f"{BASE_URL}/analytics/overview", headers=headers)
            if response.status_code == 200:
                data = response.json()
                print(f"Avg Resolution Hours: {data.get('avg_resolution_hours')}")
                # Expecting ~24.5
                val = float(data.get('avg_resolution_hours', 0))
                if 24.0 <= val <= 25.0:
                    print("SUCCESS: Analytics calculation correct.")
                else:
                     print(f"FAILURE: Analytics value {val} off.")
            else:
                print(f"FAILURE: Analytics API {response.status_code} - {response.text}")
    except Exception as e:
        print(f"FAILURE: {e}")

    print("\n=== Params Verified ===")

if __name__ == "__main__":
    verify()
