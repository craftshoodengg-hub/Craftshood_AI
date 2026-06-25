from __future__ import annotations

import json
from pathlib import Path

import pytest

from building_model import (
    BuildingModelBuilder,
    BuildingModelSerializer,
    BuildingModelValidator,
    ModuleOutputs,
)


def test_builder_constructs_model_and_computes_statistics() -> None:
    model = _sample_model()

    assert model.metadata == {"project": "demo"}
    assert model.statistics.room_count == 2
    assert model.statistics.wall_count == 2
    assert model.statistics.door_count == 1
    assert model.statistics.window_count == 1
    assert model.statistics.total_room_area == 180.0
    assert model.statistics.average_room_area == 90.0
    assert model.statistics.adjacency_edge_count == 1
    assert model.statistics.connectivity_edge_count == 1
    assert model.statistics.front_room_count == 1
    assert model.statistics.average_confidence == 0.9
    assert model.statistics.zones == {"Public": 1, "Service": 1}


def test_validator_accepts_consistent_model() -> None:
    report = BuildingModelValidator().validate(_sample_model())

    assert report.valid is True
    assert [issue.severity for issue in report.issues] == []


def test_validator_reports_unknown_room_references() -> None:
    model = BuildingModelBuilder().build(
        ModuleOutputs(
            metadata={"project": "bad"},
            rooms=[{"room_id": "living", "room_name": "Living"}],
            adjacency_graph=[
                {"room_id": "living", "adjacent_rooms": ["missing"]},
            ],
            connectivity_graph=[
                {
                    "room_id": "living",
                    "connected_rooms": [{"room_id": "missing", "door_id": "door-1"}],
                }
            ],
            facing_information={"road_side": "North", "front_wall_id": "w1", "front_rooms": ["missing"]},
            zoning=[{"room_id": "missing", "zone": "Public"}],
            confidence=[{"room_id": "missing", "confidence": 0.8}],
        )
    )

    report = BuildingModelValidator().validate(model)

    assert report.valid is False
    codes = {issue.code for issue in report.issues}
    assert "adjacency_unknown_neighbor" in codes
    assert "connectivity_unknown_neighbor" in codes
    assert "facing_unknown_front_room" in codes
    assert "zoning_unknown_room" in codes
    assert "confidence_unknown_room" in codes


def test_serializer_round_trips_json(tmp_path: Path) -> None:
    model = _sample_model()
    serializer = BuildingModelSerializer()
    output_path = tmp_path / "building.json"

    json_text = serializer.write_json(model, output_path)
    loaded = serializer.read_json(output_path)

    assert json.loads(output_path.read_text(encoding="utf-8")) == json.loads(json_text)
    assert loaded.to_dict() == model.to_dict()


def test_builder_accepts_to_dict_objects() -> None:
    class Payload:
        def __init__(self, room_id: str) -> None:
            self.room_id = room_id

        def to_dict(self) -> dict[str, str]:
            return {"room_id": self.room_id, "room_name": "Living"}

    model = BuildingModelBuilder().build(
        ModuleOutputs(
            metadata={"project": "objects"},
            rooms=[Payload("living")],
        )
    )

    assert model.rooms == ({"room_id": "living", "room_name": "Living"},)
    assert model.statistics.room_count == 1


def test_serializer_handles_shapely_geometry_in_payload() -> None:
    pytest.importorskip("shapely")
    from shapely.geometry import Polygon

    model = BuildingModelBuilder().build(
        ModuleOutputs(
            metadata={"project": "geometry"},
            rooms=[
                {
                    "room_id": "living",
                    "room_name": "Living",
                    "polygon": Polygon([(0, 0), (1, 0), (1, 1), (0, 1), (0, 0)]),
                    "area": 1,
                }
            ],
        )
    )

    payload = BuildingModelSerializer().to_dict(model)

    assert payload["rooms"][0]["polygon"]["type"] == "Polygon"


def test_raise_for_invalid_raises() -> None:
    model = BuildingModelBuilder().build(
        ModuleOutputs(
            rooms=[],
        )
    )

    with pytest.raises(ValueError, match="at least one room is required"):
        BuildingModelValidator().raise_for_invalid(model)


def _sample_model():
    return BuildingModelBuilder().build(
        ModuleOutputs(
            metadata={"project": "demo"},
            plot={"plot_id": "plot-1", "area": 1200},
            walls=[
                {"wall_id": "w1", "length": 10},
                {"wall_id": "w2", "length": 10},
            ],
            doors=[{"door_id": "door-1"}],
            windows=[{"window_id": "window-1"}],
            rooms=[
                {"room_id": "living", "room_name": "Living", "area": 120, "perimeter": 44},
                {"room_id": "kitchen", "room_name": "Kitchen", "area": 60, "perimeter": 32},
            ],
            adjacency_graph=[
                {
                    "room_id": "living",
                    "adjacent_rooms": ["kitchen"],
                    "shared_boundary_length": {"kitchen": 10},
                },
                {
                    "room_id": "kitchen",
                    "adjacent_rooms": ["living"],
                    "shared_boundary_length": {"living": 10},
                },
            ],
            connectivity_graph=[
                {
                    "room_id": "living",
                    "connected_rooms": [{"room_id": "kitchen", "door_id": "door-1"}],
                },
                {
                    "room_id": "kitchen",
                    "connected_rooms": [{"room_id": "living", "door_id": "door-1"}],
                },
            ],
            facing_information={
                "road_side": "North",
                "front_wall_id": "w1",
                "front_rooms": ["living"],
            },
            zoning=[
                {"room_id": "living", "zone": "Public"},
                {"room_id": "kitchen", "zone": "Service"},
            ],
            confidence=[
                {"room_id": "living", "confidence": 0.95},
                {"room_id": "kitchen", "confidence": 0.85},
            ],
        )
    )
