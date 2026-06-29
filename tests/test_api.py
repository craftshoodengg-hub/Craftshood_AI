"""Unit tests for REST API."""
from __future__ import annotations
import pytest
from fastapi.testclient import TestClient

from api.app import create_app


@pytest.fixture
def client():
    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["version"] == "1.0"


class TestVersionEndpoint:
    def test_version_returns_version(self, client):
        response = client.get("/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "pipeline_version" in data


class TestGenerateEndpoint:
    def test_generate_valid_prompt(self, client):
        response = client.post("/generate", json={"prompt": "3BHK modern duplex"})
        assert response.status_code == 200
        data = response.json()
        assert data["prompt"] == "3BHK modern duplex"
        assert "success" in data
        assert "quality" in data
        assert "final_score" in data
        assert "iteration_count" in data
        assert "layout_score" in data

    def test_generate_empty_prompt(self, client):
        response = client.post("/generate", json={"prompt": "x"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_generate_complex_prompt(self, client):
        response = client.post("/generate", json={
            "prompt": "Modern east-facing 3BHK villa with parking and pooja room."
        })
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["quality"] in ("Excellent", "Good", "Fair", "Poor")

    def test_generate_deterministic(self, client):
        r1 = client.post("/generate", json={"prompt": "3BHK house"})
        r2 = client.post("/generate", json={"prompt": "3BHK house"})
        assert r1.json()["final_score"] == r2.json()["final_score"]
        assert r1.json()["quality"] == r2.json()["quality"]

    def test_generate_response_schema(self, client):
        response = client.post("/generate", json={"prompt": "2BHK apartment"})
        data = response.json()
        assert isinstance(data["prompt"], str)
        assert isinstance(data["success"], bool)
        assert isinstance(data["quality"], str)
        assert isinstance(data["final_score"], (int, float))
        assert isinstance(data["iteration_count"], int)
        assert isinstance(data["layout_score"], (int, float))
        assert isinstance(data["metadata"], dict)

    def test_generate_missing_prompt_field(self, client):
        response = client.post("/generate", json={})
        assert response.status_code == 422

    def test_generate_empty_string_prompt(self, client):
        response = client.post("/generate", json={"prompt": ""})
        assert response.status_code == 422
