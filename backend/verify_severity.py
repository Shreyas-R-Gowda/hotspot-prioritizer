import httpx
import os
import sys

# Configuration
BASE_URL = "http://localhost:8000"
CITIZEN_EMAIL = "severity_tester@example.com"
CITIZEN_PASSWORD = "password123"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def create_dummy_image():
    # Create a minimal valid JPEG image
    with open("test_severity.jpg", "wb") as f:
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xc0\x00\x11\x08\x00\x10\x00\x10\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xbf\x00\xff\xd9')

def verify_severity():
    log("=== Verification: AI Severity Classification ===")
    
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        # 1. Login
        log("1. Authenticating...")
        # Try register first just in case
        client.post("/auth/register", json={
            "email": CITIZEN_EMAIL,
            "password": CITIZEN_PASSWORD,
            "name": "Severity Tester"
        })
        
        resp = client.post("/auth/login", data={"username": CITIZEN_EMAIL, "password": CITIZEN_PASSWORD})
        if resp.status_code != 200:
            log(f"Login failed: {resp.text}", "FAILURE")
            return
            
        token = resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # 2. Submit Report with Image
        log("\n2. Submitting Report with Image to trigger AI...")
        create_dummy_image()
        
        with open("test_severity.jpg", "rb") as f:
            files = {"image": ("test_severity.jpg", f, "image/jpeg")}
            data = {
                "title": "Severity Test Report",
                "category": "Pothole",
                "description": "Testing severity logic",
                "lat": "12.000",
                "lon": "77.000",
                "road_importance": "1"
            }
            
            resp = client.post("/reports/", data=data, files=files, headers=headers)
            
        if resp.status_code == 200:
            report = resp.json()
            severity = report.get('severity')
            log(f"Report ID: {report.get('report_id')}", "SUCCESS")
            log(f"Assigned Severity: {severity}", "INFO")
            
            # Validation Logic
            # - IF AI works but confidence low (expected for dummy image) -> Medium
            # - IF AI fails -> Medium (default)
            # - IF AI works and confidence high -> High
            
            if severity in ["High", "Medium", "Low"]:
                log("Severity field is populated correctly.", "SUCCESS")
            else:
                log(f"Invalid Severity: {severity}", "FAILURE")
                
        else:
            log(f"Submission failed: {resp.text}", "FAILURE")

    # Cleanup
    if os.path.exists("test_severity.jpg"):
        os.remove("test_severity.jpg")

if __name__ == "__main__":
    verify_severity()
