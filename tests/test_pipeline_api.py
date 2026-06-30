"""Tests for the Craftshood AI pipeline API integration."""
from __future__ import annotations

from fastapi.testclient import TestClient

from api.app import app


client = TestClient(app)


class TestPipelineAPI:
    def test_health_endpoint(self) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "version": "1.0"}

    def test_pipeline_generate_one_bhk(self) -> None:
        response = client.post("/pipeline/generate", json={"sample_project": "one_bhk"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] in (True, False)
        assert data["room_count"] == 4
        assert data["floor_count"] >= 0
        assert "building" in data
        assert data["pipeline_summary"]["overall_success"] == data["success"]

    def test_pipeline_generate_two_bhk(self) -> None:
        response = client.post("/pipeline/generate", json={"sample_project": "two_bhk"})
        assert response.status_code == 200
        data = response.json()
        assert data["room_count"] == 6
        assert data["floor_count"] >= 0
        assert "building" in data
        assert isinstance(data["warnings"], list)

    def test_pipeline_generate_invalid_sample_project(self) -> None:
        response = client.post("/pipeline/generate", json={"sample_project": "invalid_project"})
        assert response.status_code == 400
        assert "Unsupported sample_project" in response.json()["detail"]

    def test_pipeline_generate_empty_request(self) -> None:
        response = client.post("/pipeline/generate", json={})
        assert response.status_code == 400
        assert "Either prompt or sample_project must be provided" in response.json()["detail"]

    def test_pipeline_generate_alias_route(self) -> None:
        response = client.post("/api/v1/pipeline/generate", json={"sample_project": "one_bhk"})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] in (True, False)
        assert data["room_count"] == 4
        assert data["floor_count"] >= 0
        assert "building" in data

    def test_pipeline_generate_deterministic_response_shape(self) -> None:
        response1 = client.post("/pipeline/generate", json={"sample_project": "one_bhk"})
        response2 = client.post("/pipeline/generate", json={"sample_project": "one_bhk"})
        assert response1.status_code == 200
        assert response2.status_code == 200
        data1 = response1.json()
        data2 = response2.json()
        assert data1["room_count"] == data2["room_count"]
        assert data1["floor_count"] == data2["floor_count"]
        assert data1["success"] == data2["success"]
        assert data1["pipeline_summary"] == data2["pipeline_summary"]
