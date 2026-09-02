# Unit Tests for FastAPI Web Endpoints

import pytest
from fastapi.testclient import TestClient
from web.server import app

client = TestClient(app)

def test_api_hardware():
    response = client.get("/api/hardware")
    assert response.status_code == 200
    data = response.json()
    assert "hardware_badge" in data
    assert "device_type" in data

def test_api_presets():
    response = client.get("/api/presets")
    assert response.status_code == 200
    data = response.json()
    assert "presets" in data
    assert "models" in data
    assert "stem_labels" in data
    assert "drumsep" in data["presets"]
    assert "karaoke" in data["presets"]

def test_api_status():
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert "job" in data
    assert "hardware" in data
    assert data["job"]["status"] in ["idle", "processing", "completed", "error"]

def test_index_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "Stem Separator Studio" in response.text
