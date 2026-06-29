"""Unit tests for Room, Column, and Stair entities."""

from __future__ import annotations

import pytest
from shapely.geometry import LineString, Point

from building_model_v2 import (
    Column,
    ColumnType,
    Room,
    RoomType,
    Stair,
    StairType,
)
from building_model_v2.base import BoundingBox, Point2D


# ==================== Room Tests ====================

class TestRoom:
    """Tests for Room entity."""
    
    def _create_rectangular_room(self) -> Room:
        """Helper to create a 10x10 rectangular room."""
        return Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
        )
    
    def test_create_with_defaults(self) -> None:
        room = Room()
        assert room.room_type == RoomType.UNKNOWN
        assert room.area == 0.0
        assert room.perimeter == 0.0
        assert room.wall_ids == frozenset()
        assert room.door_ids == frozenset()
        assert room.window_ids == frozenset()
        assert room.ceiling_height is None
    
    def test_create_with_vertices(self) -> None:
        room = self._create_rectangular_room()
        assert room.area == pytest.approx(100.0)
        assert room.perimeter == pytest.approx(40.0)
        assert room.room_type == RoomType.LIVING
    
    def test_centroid(self) -> None:
        room = self._create_rectangular_room()
        centroid = room.centroid
        assert centroid.x == pytest.approx(5.0)
        assert centroid.y == pytest.approx(5.0)
    
    def test_bounding_box(self) -> None:
        room = self._create_rectangular_room()
        bbox = room.bounding_box
        assert isinstance(bbox, BoundingBox)
        assert bbox.min_x == pytest.approx(0.0)
        assert bbox.min_y == pytest.approx(0.0)
        assert bbox.max_x == pytest.approx(10.0)
        assert bbox.max_y == pytest.approx(10.0)
    
    def test_orientation(self) -> None:
        room = self._create_rectangular_room()
        orientation = room.orientation_degrees
        assert orientation == pytest.approx(0.0) or orientation == pytest.approx(90.0)
    
    def test_contains_point_inside(self) -> None:
        room = self._create_rectangular_room()
        assert room.contains(Point2D(x=5.0, y=5.0)) is True
    
    def test_contains_point_outside(self) -> None:
        room = self._create_rectangular_room()
        assert room.contains(Point2D(x=15.0, y=15.0)) is False
    
    def test_has_window_true(self) -> None:
        room = Room(window_ids=frozenset(["window-1"]))
        assert room.has_window() is True
    
    def test_has_window_false(self) -> None:
        room = Room()
        assert room.has_window() is False
    
    def test_has_door_true(self) -> None:
        room = Room(door_ids=frozenset(["door-1"]))
        assert room.has_door() is True
    
    def test_has_door_false(self) -> None:
        room = Room()
        assert room.has_door() is False
    
    def test_is_exterior_with_window(self) -> None:
        room = Room(window_ids=frozenset(["window-1"]))
        assert room.is_exterior() is True
    
    def test_is_exterior_without_window(self) -> None:
        room = Room()
        assert room.is_exterior() is False
    
    def test_aspect_ratio_square(self) -> None:
        room = self._create_rectangular_room()
        assert room.aspect_ratio() == pytest.approx(1.0)
    
    def test_aspect_ratio_rectangle(self) -> None:
        room = Room.create(vertices=[(0, 0), (20, 0), (20, 10), (0, 10)])
        assert room.aspect_ratio() == pytest.approx(2.0)
    
    def test_compactness_square(self) -> None:
        room = self._create_rectangular_room()
        assert room.compactness() == pytest.approx(1.0)
    
    def test_compactness_l_shape(self) -> None:
        # L-shaped room
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 5), (5, 5), (5, 10), (0, 10)]
        )
        assert room.compactness() < 1.0
    
    def test_to_dict(self) -> None:
        room = self._create_rectangular_room()
        result = room.to_dict()
        assert result["room_type"] == "Living"
        assert result["geometry"]["area"] == pytest.approx(100.0)
        assert result["geometry"]["perimeter"] == pytest.approx(40.0)
    
    def test_from_dict(self) -> None:
        payload = {
            "id": "room-1",
            "room_type": "Bedroom",
            "geometry": {"polygon": [[0, 0], [12, 0], [12, 10], [0, 10]]},
            "floor_id": "floor-1",
            "wall_ids": ["wall-1", "wall-2"],
            "door_ids": ["door-1"],
            "window_ids": ["window-1"],
            "ceiling_height": 9.0,
        }
        room = Room.from_dict(payload)
        assert room.id == "room-1"
        assert room.room_type == RoomType.BEDROOM
        assert room.floor_id == "floor-1"
        assert room.wall_ids == frozenset(["wall-1", "wall-2"])
        assert room.ceiling_height == 9.0
    
    def test_from_dict_defaults(self) -> None:
        room = Room.from_dict({})
        assert room.room_type == RoomType.UNKNOWN
    
    def test_immutability(self) -> None:
        room = Room()
        with pytest.raises(AttributeError):
            room.room_type = RoomType.LIVING  # type: ignore
    
    def test_inherits_base_entity(self) -> None:
        room = Room()
        assert hasattr(room, "id")
        assert hasattr(room, "created_at")
        assert hasattr(room, "updated_at")
        assert hasattr(room, "metadata")
    
    def test_round_trip_serialization(self) -> None:
        original = Room.create(
            vertices=[(0, 0), (15, 0), (15, 10), (0, 10)],
            room_type=RoomType.KITCHEN,
            floor_id="floor-1",
            wall_ids=frozenset(["wall-1"]),
            door_ids=frozenset(["door-1"]),
            window_ids=frozenset(["window-1"]),
            ceiling_height=8.0,
        )
        data = original.to_dict()
        restored = Room.from_dict(data)
        assert restored.room_type == original.room_type
        assert restored.area == original.area
        assert restored.floor_id == original.floor_id
        assert restored.wall_ids == original.wall_ids
        assert restored.ceiling_height == original.ceiling_height


# ==================== Column Tests ====================

class TestColumn:
    """Tests for Column entity."""
    
    def test_create_with_defaults(self) -> None:
        column = Column()
        assert column.column_type == ColumnType.UNKNOWN
        assert column.size == 0.0
        assert column.height is None
        assert column.floor_id is None
        assert column.is_load_bearing is True
    
    def test_create_factory(self) -> None:
        column = Column.create(
            location=(5.0, 5.0),
            size=2.0,
            height=10.0,
            column_type=ColumnType.RECTANGULAR,
        )
        assert column.geometry == Point2D(x=5.0, y=5.0)
        assert column.size == pytest.approx(2.0)
        assert column.height == 10.0
        assert column.column_type == ColumnType.RECTANGULAR
    
    def test_bounding_box(self) -> None:
        column = Column.create(location=(5.0, 5.0), size=2.0)
        bbox = column.bounding_box
        assert bbox.min_x == pytest.approx(4.0)
        assert bbox.min_y == pytest.approx(4.0)
        assert bbox.max_x == pytest.approx(6.0)
        assert bbox.max_y == pytest.approx(6.0)
    
    def test_cross_section_area_rectangular(self) -> None:
        column = Column.create(location=(0, 0), size=2.0, column_type=ColumnType.RECTANGULAR)
        assert column.cross_section_area == pytest.approx(4.0)
    
    def test_cross_section_area_circular(self) -> None:
        column = Column.create(location=(0, 0), size=2.0, column_type=ColumnType.CIRCULAR)
        import math
        expected = math.pi * 1.0 * 1.0  # pi * r^2
        assert column.cross_section_area == pytest.approx(expected)
    
    def test_is_circular_true(self) -> None:
        column = Column(column_type=ColumnType.CIRCULAR)
        assert column.is_circular is True
    
    def test_is_circular_false(self) -> None:
        column = Column(column_type=ColumnType.RECTANGULAR)
        assert column.is_circular is False
    
    def test_is_rectangular_true(self) -> None:
        column = Column(column_type=ColumnType.SQUARE)
        assert column.is_rectangular is True
    
    def test_to_dict(self) -> None:
        column = Column.create(
            location=(5.0, 5.0),
            size=2.0,
            height=10.0,
            column_type=ColumnType.CIRCULAR,
        )
        result = column.to_dict()
        assert result["column_type"] == "Circular"
        assert result["size"] == pytest.approx(2.0)
        assert result["height"] == 10.0
        assert result["is_load_bearing"] is True
    
    def test_from_dict(self) -> None:
        payload = {
            "id": "column-1",
            "column_type": "Rectangular",
            "geometry": {"x": 5.0, "y": 5.0},
            "size": 2.0,
            "height": 10.0,
            "floor_id": "floor-1",
            "is_load_bearing": True,
        }
        column = Column.from_dict(payload)
        assert column.id == "column-1"
        assert column.column_type == ColumnType.RECTANGULAR
        assert column.geometry == Point2D(x=5.0, y=5.0)
        assert column.size == pytest.approx(2.0)
    
    def test_from_dict_defaults(self) -> None:
        column = Column.from_dict({})
        assert column.column_type == ColumnType.UNKNOWN
    
    def test_immutability(self) -> None:
        column = Column()
        with pytest.raises(AttributeError):
            column.size = 1.0  # type: ignore
    
    def test_inherits_base_entity(self) -> None:
        column = Column()
        assert hasattr(column, "id")
        assert hasattr(column, "created_at")
        assert hasattr(column, "updated_at")
        assert hasattr(column, "metadata")
    
    def test_round_trip_serialization(self) -> None:
        original = Column.create(
            location=(5.0, 5.0),
            size=3.0,
            height=12.0,
            column_type=ColumnType.CIRCULAR,
            floor_id="floor-1",
            is_load_bearing=True,
        )
        data = original.to_dict()
        restored = Column.from_dict(data)
        assert restored.column_type == original.column_type
        assert restored.size == original.size
        assert restored.height == original.height
        assert restored.floor_id == original.floor_id
        assert restored.is_load_bearing == original.is_load_bearing


# ==================== Stair Tests ====================

class TestStair:
    """Tests for Stair entity."""
    
    def test_create_with_defaults(self) -> None:
        stair = Stair()
        assert stair.stair_type == StairType.UNKNOWN
        assert stair.width == 0.0
        assert stair.direction == "both"
        assert stair.connects_floors == (None, None)
        assert stair.num_steps is None
    
    def test_create_factory(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 5),
            width=3.0,
            direction="up",
            connects_floors=("floor-1", "floor-2"),
            num_steps=20,
            stair_type=StairType.STRAIGHT,
        )
        assert stair.width == pytest.approx(3.0)
        assert stair.direction == "up"
        assert stair.connects_floors == ("floor-1", "floor-2")
        assert stair.num_steps == 20
        assert stair.stair_type == StairType.STRAIGHT
    
    def test_length(self) -> None:
        stair = Stair.create(start=(0, 0), end=(10, 0))
        assert stair.length == pytest.approx(10.0)
    
    def test_bounding_box(self) -> None:
        stair = Stair.create(start=(0, 0), end=(10, 5))
        bbox = stair.bounding_box
        assert isinstance(bbox, BoundingBox)
        assert bbox.min_x == pytest.approx(0.0)
        assert bbox.min_y == pytest.approx(0.0)
        assert bbox.max_x == pytest.approx(10.0)
        assert bbox.max_y == pytest.approx(5.0)
    
    def test_from_floor_id(self) -> None:
        stair = Stair(connects_floors=("floor-1", "floor-2"))
        assert stair.from_floor_id == "floor-1"
    
    def test_to_floor_id(self) -> None:
        stair = Stair(connects_floors=("floor-1", "floor-2"))
        assert stair.to_floor_id == "floor-2"
    
    def test_is_connected_true(self) -> None:
        stair = Stair(connects_floors=("floor-1", "floor-2"))
        assert stair.is_connected is True
    
    def test_is_connected_false(self) -> None:
        stair = Stair()
        assert stair.is_connected is False
    
    def test_is_exterior_l_shaped(self) -> None:
        stair = Stair(stair_type=StairType.L_SHAPED)
        assert stair.is_exterior is True
    
    def test_is_exterior_straight(self) -> None:
        stair = Stair(stair_type=StairType.STRAIGHT)
        assert stair.is_exterior is False
    
    def test_to_dict(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 5),
            width=3.0,
            connects_floors=("floor-1", "floor-2"),
            stair_type=StairType.U_SHAPED,
        )
        result = stair.to_dict()
        assert result["stair_type"] == "U-Shaped"
        assert result["width"] == pytest.approx(3.0)
        assert result["connects_floors"]["from_floor"] == "floor-1"
        assert result["connects_floors"]["to_floor"] == "floor-2"
    
    def test_from_dict(self) -> None:
        payload = {
            "id": "stair-1",
            "stair_type": "Spiral",
            "geometry": {"centerline": [[0, 0], [5, 5]]},
            "width": 4.0,
            "direction": "up",
            "connects_floors": {"from_floor": "floor-1", "to_floor": "floor-2"},
            "num_steps": 25,
            "floor_id": "floor-1",
        }
        stair = Stair.from_dict(payload)
        assert stair.id == "stair-1"
        assert stair.stair_type == StairType.SPIRAL
        assert stair.width == pytest.approx(4.0)
        assert stair.num_steps == 25
    
    def test_from_dict_defaults(self) -> None:
        stair = Stair.from_dict({})
        assert stair.stair_type == StairType.UNKNOWN
    
    def test_immutability(self) -> None:
        stair = Stair()
        with pytest.raises(AttributeError):
            stair.width = 1.0  # type: ignore
    
    def test_inherits_base_entity(self) -> None:
        stair = Stair()
        assert hasattr(stair, "id")
        assert hasattr(stair, "created_at")
        assert hasattr(stair, "updated_at")
        assert hasattr(stair, "metadata")
    
    def test_round_trip_serialization(self) -> None:
        original = Stair.create(
            start=(0, 0),
            end=(10, 5),
            width=3.0,
            direction="both",
            connects_floors=("floor-1", "floor-2"),
            num_steps=20,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        data = original.to_dict()
        restored = Stair.from_dict(data)
        assert restored.stair_type == original.stair_type
        assert restored.width == original.width
        assert restored.direction == original.direction
        assert restored.connects_floors == original.connects_floors
        assert restored.num_steps == original.num_steps


# ==================== Integration Tests ====================

class TestEntityIntegration:
    """Integration tests for Room, Column, and Stair entities."""
    
    def test_room_with_all_properties(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (15, 0), (15, 10), (0, 10)],
            room_type=RoomType.BEDROOM,
            floor_id="floor-1",
            wall_ids=frozenset(["wall-1", "wall-2", "wall-3", "wall-4"]),
            door_ids=frozenset(["door-1"]),
            window_ids=frozenset(["window-1", "window-2"]),
            ceiling_height=9.0,
        )
        assert room.area == pytest.approx(150.0)
        assert room.has_door() is True
        assert room.has_window() is True
        assert room.is_exterior() is True
    
    def test_column_with_all_properties(self) -> None:
        column = Column.create(
            location=(5.0, 5.0),
            size=2.0,
            height=10.0,
            column_type=ColumnType.CIRCULAR,
            floor_id="floor-1",
            is_load_bearing=True,
        )
        assert column.is_circular is True
        assert column.is_load_bearing is True
    
    def test_stair_with_all_properties(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 5),
            width=3.0,
            direction="up",
            connects_floors=("floor-1", "floor-2"),
            num_steps=20,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        assert stair.is_connected is True
        assert stair.from_floor_id == "floor-1"
        assert stair.to_floor_id == "floor-2"
    
    def test_entities_have_unique_ids(self) -> None:
        room = Room.create(vertices=[(0, 0), (10, 0), (10, 10), (0, 10)])
        column = Column.create(location=(5.0, 5.0))
        stair = Stair.create(start=(0, 0), end=(10, 0))
        assert room.id != column.id
        assert room.id != stair.id
        assert column.id != stair.id
    
    def test_entities_have_timestamps(self) -> None:
        room = Room.create(vertices=[(0, 0), (10, 0), (10, 10), (0, 10)])
        column = Column.create(location=(5.0, 5.0))
        stair = Stair.create(start=(0, 0), end=(10, 0))
        assert room.created_at is not None
        assert column.created_at is not None
        assert stair.created_at is not None
    
    def test_entities_have_metadata(self) -> None:
        room = Room.create(vertices=[(0, 0), (10, 0), (10, 10), (0, 10)], metadata={"flooring": "hardwood"})
        column = Column.create(location=(5.0, 5.0), metadata={"material": "concrete"})
        stair = Stair.create(start=(0, 0), end=(10, 0), metadata={"material": "steel"})
        assert room.metadata["flooring"] == "hardwood"
        assert column.metadata["material"] == "concrete"
        assert stair.metadata["material"] == "steel"