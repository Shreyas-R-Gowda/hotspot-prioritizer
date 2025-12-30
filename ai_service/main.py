from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from typing import List
import model
import logic

app = FastAPI(title="Garbage Detection AI Service")

class DetectionResult(BaseModel):
    is_garbage: bool
    detected_category: str | None
    confidence: float
    garbage_type: str | None
    all_predictions: List[dict]

@app.on_event("startup")
async def startup_event():
    # Preload model
    model.get_model()

@app.post("/detect", response_model=DetectionResult)
async def detect_object(file: UploadFile = File(...)):
    contents = await file.read()
    
    probs, indices = model.predict_image(contents)
    
    # Check Top-1
    top_class_idx = indices[0]
    top_prob = probs[0]
    
    predicted_category = logic.get_predicted_category(top_class_idx)
    predicted_label = logic.get_label(top_class_idx) if predicted_category else None
    
    # If no category detected, result is False/None
    is_detected = predicted_category is not None

    predictions = []
    for i in range(len(indices)):
        idx = indices[i]
        cat = logic.get_predicted_category(idx)
        predictions.append({
            "class_id": idx,
            "label": logic.get_label(idx) if cat else "Other",
            "confidence": probs[i],
            "category": cat
        })

    return {
        "is_garbage": is_detected, # Legacy field, true if either detected
        "detected_category": predicted_category, # New field: "Garbage" or "Pothole"
        "garbage_type": predicted_label, # Legacy field
        "confidence": top_prob if is_detected else 0.0,
        "all_predictions": predictions
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "model": "mobilenet_v3_small"}
