import random
import hashlib

def predict_severity(image_path: str) -> str:
    """
    Heuristic-based severity classifier.
    1. Checks filename/path for keywords (useful for demo/testing).
    2. Falls back to deterministic hash of the path to ensure consistency.
    """
    # 1. Keyword Heuristics (for forcing behavior in demos)
    path_lower = image_path.lower()
    if any(k in path_lower for k in ["large", "huge", "danger", "deep", "accident"]):
        return "High"
    if any(k in path_lower for k in ["small", "tiny", "minor"]):
        return "Low"

    # 2. Deterministic Fallback based on file path hash
    # This ensures that the same image always gets the same severity, unlike random.choice
    hash_object = hashlib.md5(image_path.encode())
    hash_int = int(hash_object.hexdigest(), 16)
    
    # heavily weight towards Medium/High for better hotspot demo
    # 20% Low, 40% Medium, 40% High
    modulo = hash_int % 10
    if modulo < 2:
        return "Low"
    elif modulo < 6:
        return "Medium"
    else:
        return "High"
