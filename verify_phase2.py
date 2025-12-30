import httpx
import sys

BASE_URL = "http://localhost:8000"

def verify_integration():
    print("=== Phase 2 Verification: Backend <-> AI Integration ===")
    
    # 1. Login
    print("[1] Logging in...")
    try:
        login_resp = httpx.post(f"{BASE_URL}/auth/login", data={"username": "test@example.com", "password": "password"})
        # If test user doesn't exist, we might need to create one, but verify_features.py likely handled it or we can rely on persistence.
        # If 401, we'll try to create one or use admin
        if login_resp.status_code != 200:
             # Try admin
             login_resp = httpx.post(f"{BASE_URL}/auth/login", data={"username": "admin@example.com", "password": "password123"})
             
        if login_resp.status_code != 200:
            print(f"❌ Login failed: {login_resp.text}")
            return

        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        print("✅ Logged in.")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return

    # 2. Upload Report with Garbage Image
    print("\n[2] Uploading Garbage Report...")
    try:
        # We need a valid image file. We can use the one already in the container or upload locally.
        # Since this script runs on HOST, we need a local file.
        # Using the same sample.png (assuming it resembles garbage or not)
        # If sample.png is generic, AI might say "Not Garbage".
        # We'll see the output.
        
        with open("backend/test_images/sample.jpg", "rb") as f:
            files = {"image": ("test_garbage.jpg", f, "image/jpeg")}
            data = {
                "title": "Test Garbage Report",
                "category": "General", # Intentionally wrong to see auto-correct
                "description": "This is a test.",
                "lat": "12.97",
                "lon": "77.59"
            }
            
            resp = httpx.post(f"{BASE_URL}/reports/", data=data, files=files, headers=headers)
            
            if resp.status_code == 200:
                report = resp.json()
                print(f"Report Created: ID {report['report_id']}")
                print(f"Category: {report['category']}")
                print(f"Severity: {report['severity']}")
                
                # Check results
                if report['category'] == "Garbage / Sanitation":
                    print("✅ AI Auto-Categorization WORKED.")
                else:
                    print("⚠️ AI Auto-Categorization did NOT trigger (Sample image might not be garbage).")
                    
                if report['severity'] in ["High", "Medium"]:
                    print("✅ Severity set.")
            else:
                print(f"❌ Upload failed: {resp.status_code} - {resp.text}")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    verify_integration()
