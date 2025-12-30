import sys
import os

# Add backend to path so we can import app.ml.classifier
sys.path.append(os.path.abspath("backend"))

from app.ml.classifier import predict_severity

def test_classifier():
    print("Testing Classifier Logic...")
    
    # 1. Test Keywords
    assert predict_severity("path/to/huge_pothole.jpg") == "High", "Failed 'huge' keyword"
    assert predict_severity("path/to/tiny_crack.jpg") == "Low", "Failed 'tiny' keyword"
    print("✅ Keywords passed")
    
    # 2. Test Deterministic Hash
    # Same string should always return same result
    res1 = predict_severity("image1.jpg")
    res2 = predict_severity("image1.jpg")
    assert res1 == res2, "Non-deterministic result!"
    
    res3 = predict_severity("image2.jpg")
    print(f"Random filename 'image1.jpg' -> {res1}")
    print("✅ Deterministic hash passed")

if __name__ == "__main__":
    test_classifier()
