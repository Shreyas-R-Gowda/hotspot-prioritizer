import httpx
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import time
import os

# Use internal URL when running inside Docker
BASE_URL = "http://localhost:8000"
# Use localized DB URL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5433/hotspot_db")

def get_db_connection():
    return create_engine(DATABASE_URL).connect()

def verify():
    print("=== Starting Verification ===")
    
    # 1. Setup Data (Direct DB manipulation for precise control over created_at)
    print("\n[1] Setting up test data...")
    try:
        with get_db_connection() as conn:
            # Clear existing data for clean test
            conn.execute(text("TRUNCATE TABLE reports, users, upvotes CASCADE"))
            conn.commit()
            
            # Create User
            conn.execute(text("INSERT INTO users (name, email, password_hash, role) VALUES ('Test User', 'test@example.com', 'hashed_pw', 'citizen')"))
            conn.commit()
            user_id = conn.execute(text("SELECT user_id FROM users WHERE email='test@example.com'")).scalar()
            
            # Create Reports
            # Report A: High Severity, Recent, 10 Upvotes -> Should be #1
            # Report B: Low Severity, Old, 0 Upvotes -> Should be #2 or lower
            
            # Insert Report A
            conn.execute(text(f"""
                INSERT INTO reports (user_id, category, title, description, location, severity, upvote_count, road_importance, created_at)
                VALUES ({user_id}, 'Pothole', 'High Priority Pothole', 'Dangerous', ST_SetSRID(ST_MakePoint(77.5946, 12.9716), 4326), 'High', 10, 10, NOW())
            """))
            # Added road_importance=10 (Highway) to test new scoring
            
            # Insert Report B
            conn.execute(text(f"""
                INSERT INTO reports (user_id, category, title, description, location, severity, upvote_count, road_importance, created_at)
                VALUES ({user_id}, 'Pothole', 'Low Priority Pothole', 'Small crack', ST_SetSRID(ST_MakePoint(77.5950, 12.9720), 4326), 'Low', 0, 1, NOW() - INTERVAL '30 DAYS')
            """))
            
            conn.commit()
            print("Test data inserted.")
    except Exception as e:
        print(f"DB Setup failed: {e}")
        return

    # 2. Test Hotspots Endpoint
    print("\n[2] Testing /hotspots endpoint (Priority Scoring)...")
    try:
        # Use httpx context
        with httpx.Client(follow_redirects=True) as client:
            response = client.get(f"{BASE_URL}/hotspots/", params={"method": "kmeans", "k": 5})
            if response.status_code == 200:
                hotspots = response.json()
                print(f"Found {len(hotspots)} hotspots.")
                if len(hotspots) > 0:
                    top_hotspot = hotspots[0]
                    score = top_hotspot.get('score', 0)
                    title = top_hotspot.get('title')
                    description = top_hotspot.get('description')
                    
                    print(f"Top Hotspot Score: {score}")
                    print(f"Top Hotspot Title: {title}")
                    print(f"Top Hotspot Desc: {description}")
                    
                    # We expect the High Severity one to be top.
                    if score > 5:
                        print("SUCCESS: Priority scoring working. High score detected.")
                    else:
                        print("FAILURE: Score seems too low.")
                        
                    if title == 'High Priority Pothole':
                        print("SUCCESS: Hotspot metadata (Title) is correctly populated.")
                    else:
                        print(f"FAILURE: Unexpected title: {title}")
            else:
                print(f"FAILURE: API Error {response.status_code} - {response.text}")
                
            # 3. Test Duplicate Detection
            print("\n[3] Testing /reports/check-duplicates endpoint...")
            # Check for "Dangerous" which matches Report A
            response = client.post(f"{BASE_URL}/reports/check-duplicates", data={"description": "Dangerous"})
            if response.status_code == 200:
                duplicates = response.json()
                print(f"Found {len(duplicates)} duplicates.")
                found = False
                for d in duplicates:
                     if d.get('title') == 'High Priority Pothole':
                         found = True
                         break
                
                if found:
                    print("SUCCESS: Duplicate detection working.")
                else:
                    print(f"FAILURE: Did not find expected duplicate. Got {duplicates}")
            else:
                print(f"FAILURE: API Error {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"FAILURE: Connection error: {e}")

    print("\n=== Verification Complete ===")

if __name__ == "__main__":
    # Wait for server to start if running in parallel
    time.sleep(2) 
    verify()
