import httpx
import os

# Configuration
BASE_URL = "http://localhost:8000"
CITIZEN_EMAIL = "reporter@example.com"
CITIZEN_PASSWORD = "password123"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def create_dummy_image():
    # Create a minimal valid JPEG image
    # Header: FF D8 FF E0 ...
    with open("test_report.jpg", "wb") as f:
        f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xc0\x00\x11\x08\x00\x10\x00\x10\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xbf\x00\xff\xd9')

def verify_reporting():
    log("=== Verification: Structured Reporting System ===")
    
    with httpx.Client(base_url=BASE_URL, timeout=10.0) as client:
        # 1. Register/Login Citizen
        log("1. Authenticating Citizen...")
        client.post("/auth/register", json={
            "email": CITIZEN_EMAIL,
            "password": CITIZEN_PASSWORD,
            "name": "Reporter Citizen"
        })
        
        login_resp = client.post("/auth/login", data={
            "username": CITIZEN_EMAIL,
            "password": CITIZEN_PASSWORD
        })
        
        if login_resp.status_code != 200:
            log(f"Login failed: {login_resp.text}", "FAILURE")
            return
            
        token = login_resp.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        log("Authenticated successfully.", "SUCCESS")

        # 2. Submit Report with All Fields
        log("\n2. Submitting Full Report (Title, Desc, Lat, Lon, Image)...")
        create_dummy_image()
        
        with open("test_report.jpg", "rb") as f:
            files = {"image": ("test_report.jpg", f, "image/jpeg")}
            data = {
                "title": "Verified Pothole",
                "category": "Pothole",
                "description": "Deep hole near verification script",
                "lat": "12.9716",
                "lon": "77.5946",
                "road_importance": "5"
            }
            
            resp = client.post("/reports/", data=data, files=files, headers=headers)
            
        if resp.status_code == 200:
            report_data = resp.json()
            log(f"Report Created ID: {report_data['report_id']}", "SUCCESS")
        else:
            log(f"Submission failed: {resp.text}", "FAILURE")
            return

        # 3. Verify Stored Data
        log("\n3. Verifying Stored Data...")
        report_id = report_data['report_id']
        
        # Verify basic fields match
        if report_data['title'] == "Verified Pothole" and report_data['description'] == "Deep hole near verification script":
             log("Text fields match.", "SUCCESS")
        else:
             log(f"Text mismatch: {report_data}", "FAILURE")

        # Verify GPS
        if abs(report_data['lat'] - 12.9716) < 0.0001 and abs(report_data['lon'] - 77.5946) < 0.0001:
             log("GPS location matches.", "SUCCESS")
        else:
             log(f"GPS mismatch: {report_data['lat']}, {report_data['lon']}", "FAILURE")

        # Verify Image
        if len(report_data['images']) > 0:
             log("Image path stored.", "SUCCESS")
             # Optionally check if file exists on disk?
             # But the response proves backend acknowledged it.
        else:
             log("Image missing from response.", "FAILURE")

    log("\n=== Reporting Verification Complete ===")
    
    # Cleanup
    if os.path.exists("test_report.jpg"):
        os.remove("test_report.jpg")

if __name__ == "__main__":
    verify_reporting()
