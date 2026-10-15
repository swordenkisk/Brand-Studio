# tests/test_api.py
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_image_request_rejects_invalid_aspect_ratio():
    response = client.post(
        "/api/images",
        json={
            "prompt": "A packaging concept for coffee",
            "model": "example/image-model",
            "aspect_ratio": "invalid",
            "resolution": "1K",
        },
    )

    assert response.status_code == 422


def test_image_request_requires_prompt():
    response = client.post(
        "/api/images",
        json={
            "model": "example/image-model",
            "aspect_ratio": "1:1",
            "resolution": "1K",
        },
    )

    assert response.status_code == 422
