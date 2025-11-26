import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import get_db
from app import models
import os

client = TestClient(app)

def test_get_hotspots_grid():
    # Ensure we have some reports (relies on previous tests or DB state)
    # Ideally we should seed data here, but for now we assume the DB has data from previous steps
    
    response = client.get("/hotspots/?method=grid&grid_size_deg=0.005")
    assert response.status_code == 200
    data = response.json()
    
    # Check GeoJSON structure
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    assert isinstance(data["features"], list)
    
    if len(data["features"]) > 0:
        feature = data["features"][0]
        assert feature["type"] == "Feature"
        assert "geometry" in feature
        assert feature["geometry"]["type"] == "Polygon"
        assert "properties" in feature
        assert "count" in feature["properties"]
        assert "center" in feature["properties"]

def test_get_hotspots_kmeans():
    response = client.get("/hotspots/?method=kmeans&k=3")
    assert response.status_code == 200
    data = response.json()
    
    # Check list structure
    assert isinstance(data, list)
    if len(data) > 0:
        item = data[0]
        assert "hotspot_id" in item
        assert "center" in item
        assert "report_count" in item
