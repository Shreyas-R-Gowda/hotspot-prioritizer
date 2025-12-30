# ImageNet Class Indices relevant to Garbage/Waste and Potholes
# Based on standard ImageNet 1000 classes

GARBAGE_CLASSES = {
    # Containers / Receptacles
    412: "ashcan, trash can, garbage can",
    463: "bucket, pail",
    516: "carton",
    529: "cest, hamper",
    
    # Packaging / Debris
    673: "mousetrap", 
    696: "packet",
    723: "plastic bag",
    738: "pot, flowerpot",
    898: "water bottle",
    906: "wine bottle",
    
    # Larger items
    539: "crate",
    702: "paper towel",
}

POTHOLE_CLASSES = {
    # Road / Street defects or related infrastructure
    637: "manhole, inspection chamber", # Closest proxy for hole in ground
    # Geological features mimicking holes/cracks
    977: "sandbar, sand bar",
    979: "valley, vale",
    980: "volcano",
}

def get_predicted_category(class_idx: int) -> str | None:
    if class_idx in GARBAGE_CLASSES:
        return "Garbage"
    if class_idx in POTHOLE_CLASSES:
        return "Pothole"
    return None

def get_label(class_idx: int) -> str:
    if class_idx in GARBAGE_CLASSES:
        return GARBAGE_CLASSES[class_idx]
    if class_idx in POTHOLE_CLASSES:
        return POTHOLE_CLASSES[class_idx]
    return "Unknown"
