import torch
from torchvision import models, transforms
from PIL import Image
import io

# Singleton model instance
_model = None

def get_model():
    global _model
    if _model is None:
        print("Loading MobileNetV2 (CPU)...")
        # Load with default weights (pretrained on ImageNet)
        weights = models.MobileNet_V2_Weights.DEFAULT
        _model = models.mobilenet_v2(weights=weights)
        _model.eval()
    return _model

def get_transforms():
    # Standard ImageNet transforms
    return transforms.Compose([
        transforms.Resize(256),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

def predict_image(image_bytes: bytes):
    model = get_model()
    transform = get_transforms()
    
    image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    input_tensor = transform(image).unsqueeze(0) # Add batch dimension
    
    with torch.no_grad():
        output = model(input_tensor)
        probabilities = torch.nn.functional.softmax(output[0], dim=0)
        
    # Get top 3 predictions
    top3_prob, top3_idx = torch.topk(probabilities, 3)
    
    return top3_prob.tolist(), top3_idx.tolist()
