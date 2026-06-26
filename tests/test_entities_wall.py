"""Unit tests for Wall entity."""

from __future__ import annotations

import pytest
from shapely.geometry import LineString

from building_model_v2 import Wall, WallType
from building_model_v2.base import BoundingBox, Point2D


class TestWall:
    """Tests for Wall entity."""
    
    def test_create_with_defaults(self) -> None:
        wall = Wall()
        assert wall.wall_type == WallType.UNKNOWN
        assert wall.width == 0.0
        assert wall.height is None
        assert wall.length == 0.0
        assert wall.room_ids == frozenset()
        assert wall.floor_id is None
        assert wall.door_ids == frozenset()
        assert wall.window_ids == frozenset()
        assert wall.is_load_bearing is False
    
    def test_create_with_geometry(self) -> None:
        wall = Wall(geometry=LineString([(0, 0), (10, 0)]), width=0.5)
        assert wall.length == pytest.approx(10.0)
        assert wall.width == pytest.approx(0.5)
    
    def test_create_factory(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            height=8.0,
            wall_type=WallType.EXTERIOR,
        )
        assert wall.length == pytest.approx(10.0)
        assert wall.width == pytest.approx(0.5)
        assert wall.height == 8.0
        assert wall.wall_type == WallType.EXTERIOR
    
    def test_bounding_box(self) -> None:
        wall = Wall(geometry=LineString([(0, 0), (10, 5)]))
        bbox = wall.bounding_box
        assert isinstance(bbox, BoundingBox)
        assert bbox.min_x == pytest.approx(0.0)
        assert bbox.min_y == pytest.approx(0.0)
        assert bbox.max_x == pytest.approx(10.0)
        assert bbox.max_y == pytest.approx(5.0)
    
    def test_orientation_horizontal(self) -> None:
        wall = Wall(geometry=LineString([(0, 0), (10, 0)]))
        assert wall.orientation_degrees == pytest.approx(0.0)
    
    def test_orientation_vertical(self) -> None:
        wall = Wall(geometry=LineString([(0, 0), (0, 10)]))
        assert wall.orientation_degrees == pytest.approx(90.0)
    
    def test_orientation_45_degrees(self) -> None:
        wall = Wall(geometry=LineString([(0, 0), (10, 10)]))
        assert wall.orientation_degrees == pytest.approx(45.0)
    
    def test_start_point(self) -> None:
        wall = Wall(geometry=LineString([(1, 2), (10, 20)]))
        start = wall.start_point
        assert start.x == pytest.approx(1.0)
        assert start.y == pytest.approx(2.0)
    
    def test_end_point(self) -> None:
        wall = Wall(geometry=LineString([(1, 2), (10, 20)]))
        end = wall.end_point
        assert end.x == pytest.approx(10.0)
        assert end.y == pytest.approx(20.0)
    
    def test_is_exterior_true(self) -> None:
        wall = Wall(wall_type=WallType.EXTERIOR)
        assert wall.is_exterior is True
    
    def test_is_exterior_false(self) -> None:
        wall = Wall(wall_type=WallType.INTERIOR)
        assert wall.is_exterior is False
    
    def test_has_openings_true(self) -> None:
        wall = Wall(door_ids=frozenset(["door-1"]))
        assert wall.has_openings is True
    
    def test_has_openings_false(self) -> None:
        wall = Wall()
        assert wall.has_openings is False
    
    def test_to_dict(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
        )
        result = wall.to_dict()
        assert result["wall_type"] == "Exterior"
        assert result["width"] == pytest.approx(0.5)
        assert result["geometry"]["length"] == pytest.approx(10.0)
        # is_exterior is a property, not a serialized field
        assert wall.is_exterior is True
    
    def test_from_dict(self) -> None:
        payload = {
            "id": "wall-1",
            "wall_type": "Exterior",
            "geometry": {"centerline": [[0, 0], [10, 0]]},
            "width": 0.5,
            "height": 8.0,
            "room_ids": ["room-1", "room-2"],
            "floor_id": "floor-1",
            "is_load_bearing": True,
        }
        wall = Wall.from_dict(payload)
        assert wall.id == "wall-1"
        assert wall.wall_type == WallType.EXTERIOR
        assert wall.width == pytest.approx(0.5)
        assert wall.height == 8.0
        assert wall.room_ids == frozenset(["room-1", "room-2"])
        assert wall.floor_id == "floor-1"
        assert wall.is_load_bearing is True
    
    def test_from_dict_defaults(self) -> None:
        wall = Wall.from_dict({})
        assert wall.wall_type == WallType.UNKNOWN
        assert wall.width == 0.0
    
    def test_immutability(self) -> None:
        wall = Wall()
        with pytest.raises(AttributeError):
            wall.width = 1.0  # type: ignore
    
    def test_inherits_base_entity(self) -> None:
        wall = Wall()
        assert hasattr(wall, "id")
        assert hasattr(wall, "created_at")
        assert hasattr(wall, "updated_at")
        assert hasattr(wall, "metadata")
    
    def test_round_trip_serialization(self) -> None:
        original = Wall.create(
            start=(0, 0),
            end=(10, 5),
            width=0.5,
            height=8.0,
            wall_type=WallType.INTERIOR,
            room_ids=frozenset(["room-1"]),
            floor_id="floor-1",
            is_load_bearing=True,
        )
        data = original.to_dict()
        restored = Wall.from_dict(data)
        assert restored.wall_type == original.wall_type
        assert restored.width == original.width
        assert restored.height == original.height
        assert restored.room_ids == original.room_ids
        assert restored.floor_id == original.floor_id
        assert restored.is_load_bearing == original.is_load_bearing