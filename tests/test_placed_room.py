"""Tests for PlacedRoom data model."""
from __future__ import annotations

import pytest

from building_model_v2.layout.placed_room import PlacedRoom


class TestPlacedRoomConstruction:
    """Tests for PlacedRoom construction."""

    def test_create_valid_room(self) -> None:
        """Test creating a valid room."""
        room = PlacedRoom(
            room_id="room1", room_type="bedroom", x=0, y=0, width=3, height=2
        )
        assert room.room_id == "room1"
        assert room.room_type == "bedroom"
        assert room.x == 0
        assert room.y == 0
        assert room.width == 3
        assert room.height == 2
        assert room.zone is None

    def test_create_room_with_zone(self) -> None:
        """Test creating a room with a zone."""
        room = PlacedRoom(
            room_id="room1", room_type="bedroom", x=1, y=1, width=2, height=2, zone="zoneA"
        )
        assert room.zone == "zoneA"

    def test_zero_coordinates_allowed(self) -> None:
        """Test that zero coordinates are valid."""
        room = PlacedRoom(room_id="r1", room_type="living", x=0, y=0, width=1, height=1)
        assert room.x == 0
        assert room.y == 0

    def test_empty_room_id_raises(self) -> None:
        """Test that empty room_id raises error."""
        with pytest.raises(ValueError, match="room_id must not be empty"):
            PlacedRoom(room_id="", room_type="bedroom", x=0, y=0, width=1, height=1)

    def test_empty_room_type_raises(self) -> None:
        """Test that empty room_type raises error."""
        with pytest.raises(ValueError, match="room_type must not be empty"):
            PlacedRoom(room_id="r1", room_type="", x=0, y=0, width=1, height=1)

    def test_negative_x_raises(self) -> None:
        """Test that negative x raises error."""
        with pytest.raises(ValueError, match="x must be non-negative"):
            PlacedRoom(room_id="r1", room_type="bedroom", x=-1, y=0, width=1, height=1)

    def test_negative_y_raises(self) -> None:
        """Test that negative y raises error."""
        with pytest.raises(ValueError, match="y must be non-negative"):
            PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=-1, width=1, height=1)

    def test_zero_width_raises(self) -> None:
        """Test that zero width raises error."""
        with pytest.raises(ValueError, match="width must be positive"):
            PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=0, height=1)

    def test_negative_width_raises(self) -> None:
        """Test that negative width raises error."""
        with pytest.raises(ValueError, match="width must be positive"):
            PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=-1, height=1)

    def test_zero_height_raises(self) -> None:
        """Test that zero height raises error."""
        with pytest.raises(ValueError, match="height must be positive"):
            PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=1, height=0)

    def test_negative_height_raises(self) -> None:
        """Test that negative height raises error."""
        with pytest.raises(ValueError, match="height must be positive"):
            PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=1, height=-1)


class TestPlacedRoomCells:
    """Tests for cells() method."""

    def test_cells_1x1(self) -> None:
        """Test cells for a 1x1 room."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=2, y=1, width=1, height=1)
        cells = room.cells()
        assert cells == ((2, 1),)

    def test_cells_2x3(self) -> None:
        """Test cells for a 2x3 room."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=2, y=1, width=2, height=3)
        cells = room.cells()
        expected = (
            (2, 1), (3, 1),
            (2, 2), (3, 2),
            (2, 3), (3, 3),
        )
        assert cells == expected

    def test_cells_larger_room(self) -> None:
        """Test cells for a larger room."""
        room = PlacedRoom(room_id="r1", room_type="living", x=1, y=2, width=3, height=2)
        cells = room.cells()
        assert len(cells) == 6
        assert (1, 2) in cells
        assert (3, 2) in cells
        assert (1, 3) in cells
        assert (3, 3) in cells

    def test_cells_row_by_row(self) -> None:
        """Test that cells are generated row-by-row from top-left."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        cells = room.cells()
        # Top row first, then bottom row
        assert cells[0] == (0, 0)
        assert cells[1] == (1, 0)
        assert cells[2] == (0, 1)
        assert cells[3] == (1, 1)

    def test_cells_single_row(self) -> None:
        """Test cells for a single-row room."""
        room = PlacedRoom(room_id="r1", room_type="hallway", x=0, y=0, width=4, height=1)
        cells = room.cells()
        assert len(cells) == 4
        assert cells == ((0, 0), (1, 0), (2, 0), (3, 0))

    def test_cells_single_column(self) -> None:
        """Test cells for a single-column room."""
        room = PlacedRoom(room_id="r1", room_type="stair", x=0, y=0, width=1, height=3)
        cells = room.cells()
        assert len(cells) == 3
        assert cells == ((0, 0), (0, 1), (0, 2))


class TestPlacedRoomArea:
    """Tests for area() method."""

    def test_area_basic(self) -> None:
        """Test basic area calculation."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=3, height=2)
        assert room.area() == 6

    def test_area_1x1(self) -> None:
        """Test area of 1x1 room."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=1, height=1)
        assert room.area() == 1

    def test_area_large(self) -> None:
        """Test area of large room."""
        room = PlacedRoom(room_id="r1", room_type="hall", x=0, y=0, width=10, height=5)
        assert room.area() == 50

    def test_area_square(self) -> None:
        """Test area of square room."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=4, height=4)
        assert room.area() == 16


class TestPlacedRoomContains:
    """Tests for contains() method."""

    def test_contains_inside(self) -> None:
        """Test contains() returns True for interior coordinates."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=2, y=1, width=3, height=2)
        assert room.contains(2, 1) is True
        assert room.contains(3, 1) is True
        assert room.contains(2, 2) is True
        assert room.contains(4, 2) is True

    def test_contains_outside(self) -> None:
        """Test contains() returns False for exterior coordinates."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=2, y=1, width=3, height=2)
        assert room.contains(1, 1) is False
        assert room.contains(5, 1) is False
        assert room.contains(2, 0) is False
        assert room.contains(2, 3) is False

    def test_contains_boundary_left_top(self) -> None:
        """Test contains() includes left and top boundaries."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=2, y=1, width=3, height=2)
        assert room.contains(2, 1) is True  # top-left corner included
        assert room.contains(2, 2) is True  # left edge included
        assert room.contains(3, 1) is True  # top edge included

    def test_contains_boundary_right_bottom(self) -> None:
        """Test contains() excludes right and bottom boundaries."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=2, y=1, width=3, height=2)
        # right = x + width = 5, bottom = y + height = 3
        assert room.contains(5, 1) is False  # right boundary excluded
        assert room.contains(2, 3) is False  # bottom boundary excluded
        assert room.contains(5, 3) is False  # bottom-right corner excluded

    def test_contains_single_cell(self) -> None:
        """Test contains() for a single-cell room."""
        room = PlacedRoom(room_id="r1", room_type="closet", x=5, y=5, width=1, height=1)
        assert room.contains(5, 5) is True
        assert room.contains(4, 5) is False
        assert room.contains(6, 5) is False
        assert room.contains(5, 4) is False
        assert room.contains(5, 6) is False


class TestPlacedRoomBounds:
    """Tests for bounds() method."""

    def test_bounds_basic(self) -> None:
        """Test basic bounds calculation."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=2, y=1, width=3, height=2)
        assert room.bounds() == (2, 1, 5, 3)

    def test_bounds_1x1(self) -> None:
        """Test bounds for 1x1 room."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=1, height=1)
        assert room.bounds() == (0, 0, 1, 1)

    def test_bounds_origin(self) -> None:
        """Test bounds for room at origin."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=3)
        assert room.bounds() == (0, 0, 2, 3)

    def test_bounds_large_offset(self) -> None:
        """Test bounds with large offset."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=10, y=20, width=5, height=4)
        assert room.bounds() == (10, 20, 15, 24)


class TestPlacedRoomOverlaps:
    """Tests for overlaps() method."""

    def test_overlaps_identical_rooms(self) -> None:
        """Test that identical rooms overlap."""
        room1 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        room2 = PlacedRoom(room_id="r2", room_type="bedroom", x=0, y=0, width=2, height=2)
        assert room1.overlaps(room2) is True

    def test_overlaps_partial(self) -> None:
        """Test partial overlap."""
        room1 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=3, height=2)
        room2 = PlacedRoom(room_id="r2", room_type="living", x=2, y=0, width=2, height=2)
        assert room1.overlaps(room2) is True

    def test_overlaps_contained(self) -> None:
        """Test that contained rooms overlap."""
        room1 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=4, height=4)
        room2 = PlacedRoom(room_id="r2", room_type="bath", x=1, y=1, width=2, height=2)
        assert room1.overlaps(room2) is True

    def test_overlaps_separated(self) -> None:
        """Test that separated rooms do not overlap."""
        room1 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        room2 = PlacedRoom(room_id="r2", room_type="living", x=3, y=3, width=2, height=2)
        assert room1.overlaps(room2) is False

    def test_overlaps_touching_edges_only(self) -> None:
        """Test that rooms touching only on edges do not overlap."""
        # Room1: (0,0) to (2,2)
        # Room2: (2,0) to (4,2) - touches on right edge of room1
        room1 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        room2 = PlacedRoom(room_id="r2", room_type="living", x=2, y=0, width=2, height=2)
        assert room1.overlaps(room2) is False

    def test_overlaps_touching_corners_only(self) -> None:
        """Test that rooms touching only at corners do not overlap."""
        # Room1: (0,0) to (2,2)
        # Room2: (2,2) to (4,4) - touches at corner (2,2)
        room1 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        room2 = PlacedRoom(room_id="r2", room_type="living", x=2, y=2, width=2, height=2)
        assert room1.overlaps(room2) is False

    def test_overlaps_vertical_touching(self) -> None:
        """Test rooms stacked vertically touching on edge."""
        # Room1: (0,0) to (2,2)
        # Room2: (0,2) to (2,4) - touches on bottom edge of room1
        room1 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        room2 = PlacedRoom(room_id="r2", room_type="bath", x=0, y=2, width=2, height=2)
        assert room1.overlaps(room2) is False

    def test_overlaps_same_y_different_x(self) -> None:
        """Test rooms side by side with gap."""
        room1 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        room2 = PlacedRoom(room_id="r2", room_type="living", x=5, y=0, width=2, height=2)
        assert room1.overlaps(room2) is False


class TestPlacedRoomSerialization:
    """Tests for PlacedRoom serialization."""

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        room = PlacedRoom(
            room_id="room1", room_type="bedroom", x=2, y=1, width=3, height=2, zone="zoneA"
        )
        data = room.to_dict()
        assert data["room_id"] == "room1"
        assert data["room_type"] == "bedroom"
        assert data["x"] == 2
        assert data["y"] == 1
        assert data["width"] == 3
        assert data["height"] == 2
        assert data["zone"] == "zoneA"

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "room_id": "room1",
            "room_type": "bedroom",
            "x": 2,
            "y": 1,
            "width": 3,
            "height": 2,
            "zone": "zoneA",
        }
        room = PlacedRoom.from_dict(data)
        assert room.room_id == "room1"
        assert room.room_type == "bedroom"
        assert room.x == 2
        assert room.y == 1
        assert room.width == 3
        assert room.height == 2
        assert room.zone == "zoneA"

    def test_round_trip(self) -> None:
        """Test serialization round-trip."""
        original = PlacedRoom(
            room_id="room1", room_type="bedroom", x=2, y=1, width=3, height=2, zone="zoneA"
        )
        data = original.to_dict()
        restored = PlacedRoom.from_dict(data)
        assert restored == original

    def test_from_dict_without_zone(self) -> None:
        """Test deserialization without optional zone field."""
        data = {
            "room_id": "room1",
            "room_type": "bedroom",
            "x": 0,
            "y": 0,
            "width": 1,
            "height": 1,
        }
        room = PlacedRoom.from_dict(data)
        assert room.zone is None


class TestPlacedRoomDataclassBehavior:
    """Tests for dataclass behavior."""

    def test_equality(self) -> None:
        """Test room equality."""
        room1 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        room2 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        assert room1 == room2

    def test_inequality_different_id(self) -> None:
        """Test rooms with different IDs are not equal."""
        room1 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        room2 = PlacedRoom(room_id="r2", room_type="bedroom", x=0, y=0, width=2, height=2)
        assert room1 != room2

    def test_inequality_different_position(self) -> None:
        """Test rooms at different positions are not equal."""
        room1 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        room2 = PlacedRoom(room_id="r1", room_type="bedroom", x=1, y=0, width=2, height=2)
        assert room1 != room2

    def test_frozen_immutable(self) -> None:
        """Test that room is frozen."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        with pytest.raises(AttributeError):
            room.x = 1  # type: ignore[misc]
        with pytest.raises(AttributeError):
            room.width = 3  # type: ignore[misc]

    def test_hashable(self) -> None:
        """Test that room is hashable."""
        room1 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        room2 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        # Should be able to add to a set
        room_set = {room1, room2}
        assert len(room_set) == 1  # Equal rooms hash the same


class TestPlacedRoomEdgeCases:
    """Tests for edge cases."""

    def test_width_one(self) -> None:
        """Test room with width=1."""
        room = PlacedRoom(room_id="r1", room_type="closet", x=5, y=5, width=1, height=3)
        assert room.width == 1
        assert len(room.cells()) == 3
        assert room.area() == 3

    def test_height_one(self) -> None:
        """Test room with height=1."""
        room = PlacedRoom(room_id="r1", room_type="hallway", x=5, y=5, width=4, height=1)
        assert room.height == 1
        assert len(room.cells()) == 4
        assert room.area() == 4

    def test_large_coordinates(self) -> None:
        """Test room at large coordinates."""
        room = PlacedRoom(
            room_id="r1", room_type="bedroom", x=1000, y=2000, width=10, height=5
        )
        assert room.x == 1000
        assert room.y == 2000
        assert room.contains(1009, 2004) is True
        assert room.contains(1010, 2004) is False

    def test_contains_at_all_corners(self) -> None:
        """Test contains() at all four corners."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=1, y=1, width=3, height=2)
        # top-left (inclusive)
        assert room.contains(1, 1) is True
        # top-right (exclusive)
        assert room.contains(4, 1) is False
        # bottom-left (exclusive)
        assert room.contains(1, 3) is False
        # bottom-right (exclusive)
        assert room.contains(4, 3) is False

    def test_area_equals_cells_count(self) -> None:
        """Test that area() equals the number of cells."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=5, y=3, width=4, height=3)
        assert room.area() == len(room.cells())

    def test_bounds_match_cells_extremes(self) -> None:
        """Test that bounds match cell extremes."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=2, y=3, width=3, height=2)
        left, top, right, bottom = room.bounds()
        cells = room.cells()
        min_x = min(x for x, _ in cells)
        max_x = max(x for x, _ in cells)
        min_y = min(y for _, y in cells)
        max_y = max(y for _, y in cells)
        assert left == min_x
        assert top == min_y
        assert right == max_x + 1  # right is exclusive
        assert bottom == max_y + 1  # bottom is exclusive

    def test_no_overlap_with_disjoint_rooms(self) -> None:
        """Test multiple disjoint rooms."""
        room1 = PlacedRoom(room_id="r1", room_type="bedroom", x=0, y=0, width=2, height=2)
        room2 = PlacedRoom(room_id="r2", room_type="bath", x=5, y=5, width=2, height=2)
        room3 = PlacedRoom(room_id="r3", room_type="living", x=10, y=0, width=3, height=3)
        assert room1.overlaps(room2) is False
        assert room1.overlaps(room3) is False
        assert room2.overlaps(room3) is False

    def test_self_overlap(self) -> None:
        """Test that a room overlaps with itself."""
        room = PlacedRoom(room_id="r1", room_type="bedroom", x=1, y=1, width=3, height=2)
        assert room.overlaps(room) is True