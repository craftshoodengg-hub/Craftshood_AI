"""Unit tests for Opening, Door, and Window entities."""

from __future__ import annotations

import pytest
from shapely.geometry import LineString

from building_model_v2 import (
    Door,
    DoorType,
    Opening,
    OpeningType,
    Wall,
    WallType,
    Window,
    WindowType,
)
from building_model_v2.base import Point2D


# ==================== Opening Tests ====================

class TestOpening:
    """Tests for Opening abstract entity."""
    
    def test_create_with_defaults(self) -> None:
        opening = Opening()
        assert opening.opening_type == OpeningType.UNKNOWN
        assert opening.width == 0.0
        assert opening.height is None
        assert opening.location == Point2D(x=0.0, y=0.0)
        assert opening.wall_id is None
        assert opening.room_ids == frozenset()
        assert opening.floor_id is None
        assert opening.is_exterior is False
    
    def test_create_with_values(self) -> None:
        opening = Opening(
            opening_type=OpeningType.DOOR,
            width=3.0,
            height=7.0,
            location=Point2D(x=5.0, y=0.0),
            wall_id="wall-1",
            room_ids=frozenset(["room-1", "room-2"]),
            floor_id="floor-1",
            is_exterior=False,
        )
        assert opening.opening_type == OpeningType.DOOR
        assert opening.width == pytest.approx(3.0)
        assert opening.height == 7.0
        assert opening.wall_id == "wall-1"
        assert opening.is_exterior is False
    
    def test_to_dict(self) -> None:
        opening = Opening(
            opening_type=OpeningType.WINDOW,
            width=4.0,
            height=5.0,
            location=Point2D(x=1.0, y=2.0),
        )
        result = opening.to_dict()
        assert result["opening_type"] == "Window"
        assert result["width"] == pytest.approx(4.0)
        assert result["height"] == 5.0
        assert result["location"] == {"x": 1.0, "y": 2.0}
    
    def test_from_dict(self) -> None:
        payload = {
            "id": "opening-1",
            "opening_type": "Door",
            "width": 3.0,
            "height": 7.0,
            "location": {"x": 5.0, "y": 0.0},
            "wall_id": "wall-1",
            "room_ids": ["room-1"],
            "floor_id": "floor-1",
            "is_exterior": True,
        }
        opening = Opening.from_dict(payload)
        assert opening.id == "opening-1"
        assert opening.opening_type == OpeningType.DOOR
        assert opening.width == pytest.approx(3.0)
        assert opening.is_exterior is True
    
    def test_from_dict_defaults(self) -> None:
        opening = Opening.from_dict({})
        assert opening.opening_type == OpeningType.UNKNOWN
        assert opening.width == 0.0
    
    def test_immutability(self) -> None:
        opening = Opening()
        with pytest.raises(AttributeError):
            opening.width = 1.0  # type: ignore
    
    def test_inherits_base_entity(self) -> None:
        opening = Opening()
        assert hasattr(opening, "id")
        assert hasattr(opening, "created_at")
        assert hasattr(opening, "updated_at")
        assert hasattr(opening, "metadata")


# ==================== Door Tests ====================

class TestDoor:
    """Tests for Door entity."""
    
    def test_create_with_defaults(self) -> None:
        door = Door()
        assert door.opening_type == OpeningType.DOOR
        assert door.door_type == DoorType.UNKNOWN
        assert door.width == 0.0
        assert door.height is None
        assert door.swing_direction is None
        assert door.is_exterior is False
    
    def test_create_factory_with_tuple_location(self) -> None:
        door = Door.create(
            location=(5.0, 0.0),
            width=3.0,
            height=7.0,
            door_type=DoorType.SINGLE_LEAF,
        )
        assert door.location == Point2D(x=5.0, y=0.0)
        assert door.width == pytest.approx(3.0)
        assert door.height == 7.0
        assert door.door_type == DoorType.SINGLE_LEAF
    
    def test_create_factory_with_point_location(self) -> None:
        door = Door.create(
            location=Point2D(x=5.0, y=0.0),
            width=3.0,
        )
        assert door.location == Point2D(x=5.0, y=0.0)
    
    def test_opening_type_is_door(self) -> None:
        door = Door()
        assert door.opening_type == OpeningType.DOOR
    
    def test_to_dict(self) -> None:
        door = Door.create(
            location=(5.0, 0.0),
            width=3.0,
            height=7.0,
            door_type=DoorType.DOUBLE_LEAF,
            swing_direction="left",
            wall_id="wall-1",
            room_ids=frozenset(["room-1", "room-2"]),
            is_exterior=True,
        )
        result = door.to_dict()
        assert result["opening_type"] == "Door"
        assert result["door_type"] == "Double Leaf"
        assert result["swing_direction"] == "left"
        assert result["width"] == pytest.approx(3.0)
        assert result["height"] == 7.0
        assert result["wall_id"] == "wall-1"
        assert result["is_exterior"] is True
    
    def test_from_dict(self) -> None:
        payload = {
            "id": "door-1",
            "door_type": "Sliding",
            "width": 6.0,
            "height": 7.0,
            "location": {"x": 5.0, "y": 0.0},
            "swing_direction": "sliding",
            "wall_id": "wall-1",
            "room_ids": ["room-1"],
            "floor_id": "floor-1",
            "is_exterior": True,
        }
        door = Door.from_dict(payload)
        assert door.id == "door-1"
        assert door.door_type == DoorType.SLIDING
        assert door.width == pytest.approx(6.0)
        assert door.swing_direction == "sliding"
        assert door.is_exterior is True
    
    def test_from_dict_defaults(self) -> None:
        door = Door.from_dict({})
        assert door.door_type == DoorType.UNKNOWN
        assert door.opening_type == OpeningType.DOOR
    
    def test_immutability(self) -> None:
        door = Door()
        with pytest.raises(AttributeError):
            door.width = 1.0  # type: ignore
    
    def test_inherits_opening(self) -> None:
        door = Door()
        assert isinstance(door, Opening)
    
    def test_round_trip_serialization(self) -> None:
        original = Door.create(
            location=(5.0, 0.0),
            width=3.0,
            height=7.0,
            door_type=DoorType.SINGLE_LEAF,
            swing_direction="right",
            wall_id="wall-1",
            room_ids=frozenset(["room-1"]),
            floor_id="floor-1",
            is_exterior=True,
        )
        data = original.to_dict()
        restored = Door.from_dict(data)
        assert restored.door_type == original.door_type
        assert restored.width == original.width
        assert restored.height == original.height
        assert restored.swing_direction == original.swing_direction
        assert restored.wall_id == original.wall_id
        assert restored.is_exterior == original.is_exterior


# ==================== Window Tests ====================

class TestWindow:
    """Tests for Window entity."""
    
    def test_create_with_defaults(self) -> None:
        window = Window()
        assert window.opening_type == OpeningType.WINDOW
        assert window.window_type == WindowType.UNKNOWN
        assert window.width == 0.0
        assert window.height is None
        assert window.sill_height is None
        assert window.is_exterior is False
    
    def test_create_factory_with_tuple_location(self) -> None:
        window = Window.create(
            location=(5.0, 3.0),
            width=4.0,
            height=4.0,
            sill_height=3.0,
            window_type=WindowType.CASEMENT,
        )
        assert window.location == Point2D(x=5.0, y=3.0)
        assert window.width == pytest.approx(4.0)
        assert window.height == 4.0
        assert window.sill_height == 3.0
        assert window.window_type == WindowType.CASEMENT
    
    def test_create_factory_with_point_location(self) -> None:
        window = Window.create(
            location=Point2D(x=5.0, y=3.0),
            width=4.0,
        )
        assert window.location == Point2D(x=5.0, y=3.0)
    
    def test_opening_type_is_window(self) -> None:
        window = Window()
        assert window.opening_type == OpeningType.WINDOW
    
    def test_to_dict(self) -> None:
        window = Window.create(
            location=(5.0, 3.0),
            width=4.0,
            height=5.0,
            sill_height=3.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            room_ids=frozenset(["room-1"]),
            is_exterior=True,
        )
        result = window.to_dict()
        assert result["opening_type"] == "Window"
        assert result["window_type"] == "Fixed"
        assert result["sill_height"] == pytest.approx(3.0)
        assert result["width"] == pytest.approx(4.0)
        assert result["height"] == 5.0
        assert result["wall_id"] == "wall-1"
        assert result["is_exterior"] is True
    
    def test_from_dict(self) -> None:
        payload = {
            "id": "window-1",
            "window_type": "Casement",
            "width": 4.0,
            "height": 5.0,
            "location": {"x": 5.0, "y": 3.0},
            "sill_height": 3.0,
            "wall_id": "wall-1",
            "room_ids": ["room-1"],
            "floor_id": "floor-1",
            "is_exterior": True,
        }
        window = Window.from_dict(payload)
        assert window.id == "window-1"
        assert window.window_type == WindowType.CASEMENT
        assert window.width == pytest.approx(4.0)
        assert window.sill_height == pytest.approx(3.0)
        assert window.is_exterior is True
    
    def test_from_dict_defaults(self) -> None:
        window = Window.from_dict({})
        assert window.window_type == WindowType.UNKNOWN
        assert window.opening_type == OpeningType.WINDOW
    
    def test_immutability(self) -> None:
        window = Window()
        with pytest.raises(AttributeError):
            window.width = 1.0  # type: ignore
    
    def test_inherits_opening(self) -> None:
        window = Window()
        assert isinstance(window, Opening)
    
    def test_round_trip_serialization(self) -> None:
        original = Window.create(
            location=(5.0, 3.0),
            width=4.0,
            height=5.0,
            sill_height=3.0,
            window_type=WindowType.SLIDING,
            wall_id="wall-1",
            room_ids=frozenset(["room-1"]),
            floor_id="floor-1",
            is_exterior=True,
        )
        data = original.to_dict()
        restored = Window.from_dict(data)
        assert restored.window_type == original.window_type
        assert restored.width == original.width
        assert restored.height == original.height
        assert restored.sill_height == original.sill_height
        assert restored.wall_id == original.wall_id
        assert restored.is_exterior == original.is_exterior


# ==================== Integration Tests ====================

class TestEntityIntegration:
    """Integration tests for Wall, Door, and Window entities."""
    
    def test_wall_with_doors(self) -> None:
        door1 = Door.create(location=(2.0, 0.0), width=3.0)
        door2 = Door.create(location=(8.0, 0.0), width=3.0)
        wall = Wall(
            geometry=LineString([(0, 0), (10, 0)]),
            door_ids=frozenset([door1.id, door2.id]),
        )
        assert wall.has_openings is True
        assert len(wall.door_ids) == 2
    
    def test_wall_with_windows(self) -> None:
        window1 = Window.create(location=(3.0, 0.0), width=4.0)
        window2 = Window.create(location=(7.0, 0.0), width=4.0)
        wall = Wall(
            geometry=LineString([(0, 0), (10, 0)]),
            window_ids=frozenset([window1.id, window2.id]),
        )
        assert wall.has_openings is True
        assert len(wall.window_ids) == 2
    
    def test_wall_with_room_ids(self) -> None:
        wall = Wall(
            geometry=LineString([(0, 0), (10, 0)]),
            room_ids=frozenset(["living", "bedroom"]),
        )
        assert "living" in wall.room_ids
        assert "bedroom" in wall.room_ids
    
    def test_door_with_wall_id(self) -> None:
        door = Door.create(
            location=(5.0, 0.0),
            wall_id="wall-1",
        )
        assert door.wall_id == "wall-1"
    
    def test_window_with_wall_id(self) -> None:
        window = Window.create(
            location=(5.0, 0.0),
            wall_id="wall-1",
        )
        assert window.wall_id == "wall-1"
    
    def test_entities_have_unique_ids(self) -> None:
        wall = Wall(geometry=LineString([(0, 0), (10, 0)]))
        door = Door.create(location=(5.0, 0.0))
        window = Window.create(location=(7.0, 0.0))
        assert wall.id != door.id
        assert wall.id != window.id
        assert door.id != window.id
    
    def test_entities_have_timestamps(self) -> None:
        wall = Wall(geometry=LineString([(0, 0), (10, 0)]))
        door = Door.create(location=(5.0, 0.0))
        window = Window.create(location=(7.0, 0.0))
        assert wall.created_at is not None
        assert door.created_at is not None
        assert window.created_at is not None
    
    def test_entities_have_metadata(self) -> None:
        wall = Wall(geometry=LineString([(0, 0), (10, 0)]), metadata={"material": "brick"})
        door = Door.create(location=(5.0, 0.0), metadata={"material": "wood"})
        window = Window.create(location=(7.0, 0.0), metadata={"glass": "double"})
        assert wall.metadata["material"] == "brick"
        assert door.metadata["material"] == "wood"
        assert window.metadata["glass"] == "double"