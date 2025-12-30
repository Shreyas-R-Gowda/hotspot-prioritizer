import httpx
import sys

# AI Service exposed internally on 8000
URL = "http://ai_service:8000/detect"
FILE_PATH = "backend/test_images/sample.jpg" # Need to ensure this exists or use a generated one

def test_ai():
    print(f"Testing AI Service at {URL}...")
    
    # Read sample image
    try:
        with open("sample.png", "rb") as f:
            img_byte_arr = f.read()
            
        files = {'file': ('sample.png', img_byte_arr, 'image/png')}
    except FileNotFoundError:
        print("❌ sample.png not found")
        sys.exit(1)
    
    try:
        response = httpx.post(URL, files=files, timeout=10.0)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ AI Service is reachable and predicting.")
        else:
            print("❌ AI Service failed.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_ai()
