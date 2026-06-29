"""Unit tests for Floor entity."""

from __future__ import annotations

import pytest

from building_model_v2 import Floor, FloorType
from building_model_v2.base import Point2D


class TestFloor:
    """Tests for Floor entity."""
    
    def test_create_with_defaults(self) -> None:
        floor = Floor()
        assert floor.name == ""
        assert floor.level == 0
        assert floor.elevation == pytest.approx(0.0)
        assert floor.floor_height == pytest.approx(0.0)
        assert floor.slab_thickness == pytest.approx(0.0)
        assert floor.floor_type == FloorType.UNKNOWN
        assert floor.room_ids == frozenset()
        assert floor.wall_ids == frozenset()
        assert floor.column_ids == frozenset()
        assert floor.stair_ids == frozenset()
    
    def test_create_with_values(self) -> None:
        floor = Floor(
            name="Ground Floor",
            level=0,
            elevation=0.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.GROUND,
        )
        assert floor.name == "Ground Floor"
        assert floor.level == 0
        assert floor.elevation == pytest.approx(0.0)
        assert floor.floor_height == pytest.approx(10.0)
        assert floor.slab_thickness == pytest.approx(0.5)
        assert floor.floor_type == FloorType.GROUND
    
    def test_create_factory(self) -> None:
        floor = Floor.create(
            name="First Floor",
            level=1,
            elevation=10.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.UPPER,
        )
        assert floor.name == "First Floor"
        assert floor.level == 1
        assert floor.elevation == pytest.approx(10.0)
        assert floor.floor_type == FloorType.UPPER
    
    def test_create_factory_with_collections(self) -> None:
        floor = Floor.create(
            name="Ground Floor",
            room_ids=frozenset(["room-1", "room-2"]),
            wall_ids=frozenset(["wall-1", "wall-2", "wall-3"]),
            column_ids=frozenset(["col-1"]),
            stair_ids=frozenset(["stair-1"]),
        )
        assert floor.room_ids == frozenset(["room-1", "room-2"])
        assert floor.wall_ids == frozenset(["wall-1", "wall-2", "wall-3"])
        assert floor.column_ids == frozenset(["col-1"])
        assert floor.stair_ids == frozenset(["stair-1"])
    
    def test_room_count(self) -> None:
        floor = Floor(room_ids=frozenset(["r1", "r2", "r3"]))
        assert floor.room_count == 3
    
    def test_room_count_empty(self) -> None:
        floor = Floor()
        assert floor.room_count == 0
    
    def test_wall_count(self) -> None:
        floor = Floor(wall_ids=frozenset(["w1", "w2"]))
        assert floor.wall_count == 2
    
    def test_wall_count_empty(self) -> None:
        floor = Floor()
        assert floor.wall_count == 0
    
    def test_column_count(self) -> None:
        floor = Floor(column_ids=frozenset(["c1", "c2", "c3", "c4"]))
        assert floor.column_count == 4
    
    def test_column_count_empty(self) -> None:
        floor = Floor()
        assert floor.column_count == 0
    
    def test_stair_count(self) -> None:
        floor = Floor(stair_ids=frozenset(["s1"]))
        assert floor.stair_count == 1
    
    def test_stair_count_empty(self) -> None:
        floor = Floor()
        assert floor.stair_count == 0
    
    def test_has_rooms_true(self) -> None:
        floor = Floor(room_ids=frozenset(["room-1"]))
        assert floor.has_rooms is True
    
    def test_has_rooms_false(self) -> None:
        floor = Floor()
        assert floor.has_rooms is False
    
    def test_has_columns_true(self) -> None:
        floor = Floor(column_ids=frozenset(["col-1"]))
        assert floor.has_columns is True
    
    def test_has_columns_false(self) -> None:
        floor = Floor()
        assert floor.has_columns is False
    
    def test_has_stairs_true(self) -> None:
        floor = Floor(stair_ids=frozenset(["stair-1"]))
        assert floor.has_stairs is True
    
    def test_has_stairs_false(self) -> None:
        floor = Floor()
        assert floor.has_stairs is False
    
    def test_is_ground_floor_true(self) -> None:
        floor = Floor(level=0)
        assert floor.is_ground_floor is True
    
    def test_is_ground_floor_false(self) -> None:
        floor = Floor(level=1)
        assert floor.is_ground_floor is False
    
    def test_is_basement_true(self) -> None:
        floor = Floor(level=-1)
        assert floor.is_basement is True
    
    def test_is_basement_false(self) -> None:
        floor = Floor(level=0)
        assert floor.is_basement is False
    
    def test_is_roof_true(self) -> None:
        floor = Floor(floor_type=FloorType.ROOF)
        assert floor.is_roof is True
    
    def test_is_roof_false(self) -> None:
        floor = Floor(floor_type=FloorType.GROUND)
        assert floor.is_roof is False
    
    def test_bounding_box_placeholder(self) -> None:
        floor = Floor(name="Test Floor")
        assert floor.bounding_box() is None
    
    def test_to_dict(self) -> None:
        floor = Floor.create(
            name="Ground Floor",
            level=0,
            elevation=0.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.GROUND,
            room_ids=frozenset(["room-1", "room-2"]),
            wall_ids=frozenset(["wall-1"]),
            column_ids=frozenset(["col-1", "col-2"]),
            stair_ids=frozenset(["stair-1"]),
        )
        result = floor.to_dict()
        assert result["name"] == "Ground Floor"
        assert result["level"] == 0
        assert result["elevation"] == pytest.approx(0.0)
        assert result["floor_height"] == pytest.approx(10.0)
        assert result["slab_thickness"] == pytest.approx(0.5)
        assert result["floor_type"] == "Ground"
        assert result["room_ids"] == ["room-1", "room-2"]
        assert result["wall_ids"] == ["wall-1"]
        assert result["column_ids"] == ["col-1", "col-2"]
        assert result["stair_ids"] == ["stair-1"]
        assert result["counts"]["rooms"] == 2
        assert result["counts"]["walls"] == 1
        assert result["counts"]["columns"] == 2
        assert result["counts"]["stairs"] == 1
    
    def test_from_dict(self) -> None:
        payload = {
            "id": "floor-1",
            "name": "First Floor",
            "level": 1,
            "elevation": 10.0,
            "floor_height": 10.0,
            "slab_thickness": 0.5,
            "floor_type": "Upper",
            "room_ids": ["room-1", "room-2"],
            "wall_ids": ["wall-1", "wall-2"],
            "column_ids": ["col-1"],
            "stair_ids": ["stair-1"],
        }
        floor = Floor.from_dict(payload)
        assert floor.id == "floor-1"
        assert floor.name == "First Floor"
        assert floor.level == 1
        assert floor.elevation == pytest.approx(10.0)
        assert floor.floor_height == pytest.approx(10.0)
        assert floor.slab_thickness == pytest.approx(0.5)
        assert floor.floor_type == FloorType.UPPER
        assert floor.room_ids == frozenset(["room-1", "room-2"])
        assert floor.wall_ids == frozenset(["wall-1", "wall-2"])
        assert floor.column_ids == frozenset(["col-1"])
        assert floor.stair_ids == frozenset(["stair-1"])
    
    def test_from_dict_defaults(self) -> None:
        floor = Floor.from_dict({})
        assert floor.name == ""
        assert floor.level == 0
        assert floor.floor_type == FloorType.UNKNOWN
    
    def test_from_dict_partial(self) -> None:
        payload = {
            "id": "floor-2",
            "name": "Basement",
            "level": -1,
        }
        floor = Floor.from_dict(payload)
        assert floor.id == "floor-2"
        assert floor.name == "Basement"
        assert floor.level == -1
        assert floor.elevation == pytest.approx(0.0)
        assert floor.room_ids == frozenset()
    
    def test_immutability(self) -> None:
        floor = Floor()
        with pytest.raises(AttributeError):
            floor.name = "New Name"  # type: ignore
    
    def test_immutability_level(self) -> None:
        floor = Floor()
        with pytest.raises(AttributeError):
            floor.level = 5  # type: ignore
    
    def test_inherits_base_entity(self) -> None:
        floor = Floor()
        assert hasattr(floor, "id")
        assert hasattr(floor, "created_at")
        assert hasattr(floor, "updated_at")
        assert hasattr(floor, "metadata")
    
    def test_round_trip_serialization(self) -> None:
        original = Floor.create(
            name="Test Floor",
            level=2,
            elevation=20.0,
            floor_height=12.0,
            slab_thickness=0.75,
            floor_type=FloorType.UPPER,
            room_ids=frozenset(["room-1", "room-2", "room-3"]),
            wall_ids=frozenset(["wall-1", "wall-2"]),
            column_ids=frozenset(["col-1", "col-2", "col-3", "col-4"]),
            stair_ids=frozenset(["stair-1", "stair-2"]),
            metadata={"material": "concrete"},
        )
        data = original.to_dict()
        restored = Floor.from_dict(data)
        assert restored.name == original.name
        assert restored.level == original.level
        assert restored.elevation == original.elevation
        assert restored.floor_height == original.floor_height
        assert restored.slab_thickness == original.slab_thickness
        assert restored.floor_type == original.floor_type
        assert restored.room_ids == original.room_ids
        assert restored.wall_ids == original.wall_ids
        assert restored.column_ids == original.column_ids
        assert restored.stair_ids == original.stair_ids
        assert restored.metadata == original.metadata
    
    def test_equality(self) -> None:
        floor1 = Floor(name="Floor 1", level=0)
        floor2 = Floor(name="Floor 1", level=0)
        # Different IDs by default
        assert floor1 != floor2
    
    def test_equality_same_id(self) -> None:
        floor1 = Floor(
            id="same-id",
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
            name="Floor 1",
            level=0,
        )
        floor2 = Floor(
            id="same-id",
            created_at="2024-01-01T00:00:00+00:00",
            updated_at="2024-01-01T00:00:00+00:00",
            name="Floor 1",
            level=0,
        )
        assert floor1 == floor2
    
    def test_negative_level(self) -> None:
        floor = Floor.create(name="Basement 1", level=-1, elevation=-10.0)
        assert floor.level == -1
        assert floor.elevation == pytest.approx(-10.0)
        assert floor.is_basement is True
    
    def test_high_level(self) -> None:
        floor = Floor.create(name="Penthouse", level=50, elevation=500.0)
        assert floor.level == 50
        assert floor.elevation == pytest.approx(500.0)
    
    def test_empty_name(self) -> None:
        floor = Floor(name="")
        assert floor.name == ""
    
    def test_metadata_preserved(self) -> None:
        floor = Floor(
            name="Test",
            metadata={"area": 1000, "type": "office"}
        )
        assert floor.metadata["area"] == 1000
        assert floor.metadata["type"] == "office"
    
    def test_floor_type_enum_values(self) -> None:
        for floor_type in FloorType:
            floor = Floor(floor_type=floor_type)
            assert floor.floor_type == floor_type
    
    def test_all_counts_zero_on_empty_floor(self) -> None:
        floor = Floor()
        assert floor.room_count == 0
        assert floor.wall_count == 0
        assert floor.column_count == 0
        assert floor.stair_count == 0
    
    def test_to_dict_includes_base_fields(self) -> None:
        floor = Floor(name="Test")
        result = floor.to_dict()
        assert "id" in result
        assert "created_at" in result
        assert "updated_at" in result
        assert "metadata" in result
    
    def test_from_dict_preserves_timestamps(self) -> None:
        payload = {
            "id": "floor-1",
            "created_at": "2024-01-01T00:00:00+00:00",
            "updated_at": "2024-01-02T00:00:00+00:00",
        }
        floor = Floor.from_dict(payload)
        assert floor.id == "floor-1"
        assert floor.created_at == "2024-01-01T00:00:00+00:00"
        assert floor.updated_at == "2024-01-02T00:00:00+00:00"
    
    def test_from_dict_generates_timestamps_if_missing(self) -> None:
        floor = Floor.from_dict({"id": "floor-1"})
        assert floor.created_at is not None
        assert floor.updated_at is not None
    
    def test_large_collection_ids(self) -> None:
        room_ids = frozenset([f"room-{i}" for i in range(100)])
        wall_ids = frozenset([f"wall-{i}" for i in range(150)])
        floor = Floor(room_ids=room_ids, wall_ids=wall_ids)
        assert floor.room_count == 100
        assert floor.wall_count == 150
    
    def test_floor_with_all_properties(self) -> None:
        floor = Floor(
            name="Typical Floor",
            level=3,
            elevation=30.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.UPPER,
            room_ids=frozenset(["r1", "r2", "r3", "r4"]),
            wall_ids=frozenset(["w1", "w2", "w3", "w4", "w5"]),
            column_ids=frozenset(["c1", "c2", "c3", "c4", "c5", "c6"]),
            stair_ids=frozenset(["s1", "s2"]),
            metadata={"construction": "steel_frame"},
        )
        assert floor.name == "Typical Floor"
        assert floor.level == 3
        assert floor.room_count == 4
        assert floor.wall_count == 5
        assert floor.column_count == 6
        assert floor.stair_count == 2
        assert floor.has_rooms is True
        assert floor.has_columns is True
        assert floor.has_stairs is True
        assert floor.is_ground_floor is False
        assert floor.is_basement is False
        assert floor.is_roof is False