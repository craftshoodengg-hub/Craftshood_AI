"""Tests for room placement engine."""
from __future__ import annotations

import pytest

from building_model_v2.architect.architect_result import ArchitectResult
from building_model_v2.architect.bubble_connection import BubbleConnection
from building_model_v2.architect.bubble_diagram import BubbleDiagram
from building_model_v2.architect.bubble_node import BubbleNode
from building_model_v2.architect.zone import Zone
from building_model_v2.architect.zoning_result import ZoningResult
from building_model_v2.ai.room_program import FloorPreference, PrivacyLevel
from building_model_v2.layout.layout_cell import LayoutCell
from building_model_v2.layout.layout_grid import LayoutGrid
from building_model_v2.layout.placed_room import PlacedRoom
from building_model_v2.layout.placement_result import PlacementResult
from building_model_v2.layout.room_placement_engine import RoomPlacementEngine
from building_model_v2.types import RoomType


# --- Helpers ---

def _make_node(room_id: str, width: int, height: int) -> BubbleNode:
    return BubbleNode(
        id=room_id,
        room_type=RoomType.LIVING,
        name=room_id,
        target_area=float(width * height),
        privacy_level=PrivacyLevel.PUBLIC,
        preferred_floor=FloorPreference.ANY,
    )


def _make_grid(width: int, height: int) -> LayoutGrid:
    cells = tuple(
        LayoutCell(x=x, y=y)
        for y in range(height)
        for x in range(width)
    )
    return LayoutGrid(
        width=width,
        height=height,
        cells=cells,
    )


def _make_architect_result(rooms: list[BubbleNode]) -> ArchitectResult:
    diagram = BubbleDiagram(
        nodes=tuple(rooms),
        connections=(),
    )
    zones = (Zone(name="default", zone_type="PUBLIC", rooms=tuple(rooms)),)
    zoning = ZoningResult(zones=zones)
    return ArchitectResult(
        bubble_diagram=diagram,
        zoning_result=zoning,
    )


# --- Tests ---

class TestRoomPlacementEngineEmpty:
    """Tests for empty grid and empty result."""

    def test_empty_grid_no_rooms(self) -> None:
        """Empty grid with no rooms produces empty placement."""
        grid = _make_grid(10, 10)
        architect = _make_architect_result([])
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        assert result.placed_count == 0
        assert result.unplaced_count == 0
        assert result.success is True
        assert result.occupancy_ratio == 0.0

    def test_empty_grid_with_rooms(self) -> None:
        """Empty grid with no rooms produces empty placement."""
        grid = _make_grid(10, 10)
        architect = _make_architect_result([_make_node("r1", 2, 2)])
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        assert result.placed_count == 1
        assert result.unplaced_count == 0


class TestRoomPlacementEngineSingleRoom:
    """Tests for single room placement."""

    def test_single_room_placed_at_origin(self) -> None:
        """Single room placed at origin."""
        grid = _make_grid(10, 10)
        architect = _make_architect_result([_make_node("r1", 2, 2)])
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        assert result.placed_count == 1
        placed = result.placed_rooms[0]
        assert placed.x == 0
        assert placed.y == 0
        assert placed.width == 2
        assert placed.height == 2


class TestRoomPlacementEngineMultipleRooms:
    """Tests for multiple room placement."""

    def test_multiple_rooms_no_overlap(self) -> None:
        """Multiple rooms placed without overlap."""
        grid = _make_grid(10, 10)
        rooms = [
            _make_node("r1", 3, 3),
            _make_node("r2", 2, 2),
            _make_node("r3", 1, 1),
        ]
        architect = _make_architect_result(rooms)
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        assert result.placed_count == 3
        assert result.unplaced_count == 0

    def test_rooms_do_not_overlap(self) -> None:
        """Placed rooms do not overlap."""
        grid = _make_grid(10, 10)
        rooms = [
            _make_node("r1", 3, 3),
            _make_node("r2", 3, 3),
        ]
        architect = _make_architect_result(rooms)
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        assert result.placed_count == 2
        r1, r2 = result.placed_rooms
        assert not r1.overlaps(r2)


class TestRoomPlacementEngineLargeRoom:
    """Tests for large room placement."""

    def test_large_room_fits(self) -> None:
        """Large room placed correctly."""
        grid = _make_grid(20, 20)
        rooms = [_make_node("r1", 10, 10)]
        architect = _make_architect_result(rooms)
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        assert result.placed_count == 1
        placed = result.placed_rooms[0]
        assert placed.x == 0
        assert placed.y == 0
        assert placed.width == 10
        assert placed.height == 10


class TestRoomPlacementEngineGridOverflow:
    """Tests for grid overflow."""

    def test_room_too_large_for_grid(self) -> None:
        """Room that is too large is not placed."""
        grid = _make_grid(5, 5)
        rooms = [_make_node("r1", 10, 10)]
        architect = _make_architect_result(rooms)
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        assert result.placed_count == 0
        assert result.unplaced_count == 1
        assert result.success is False

    def test_multiple_rooms_partial_placement(self) -> None:
        """Some rooms placed, some not."""
        grid = _make_grid(5, 5)
        rooms = [
            _make_node("r1", 3, 3),
            _make_node("r2", 3, 3),
        ]
        architect = _make_architect_result(rooms)
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        assert result.placed_count == 1
        assert result.unplaced_count == 1


class TestRoomPlacementEngineOccupancyRatio:
    """Tests for occupancy ratio."""

    def test_occupancy_ratio_empty(self) -> None:
        """Occupancy ratio is 0 for empty placement."""
        grid = _make_grid(10, 10)
        architect = _make_architect_result([])
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        assert result.occupancy_ratio == 0.0

    def test_occupancy_ratio_full(self) -> None:
        """Occupancy ratio is 1.0 when grid is fully covered."""
        grid = _make_grid(2, 2)
        rooms = [_make_node("r1", 2, 2)]
        architect = _make_architect_result(rooms)
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        assert result.occupancy_ratio == 1.0

    def test_occupancy_ratio_partial(self) -> None:
        """Occupancy ratio is calculated correctly."""
        grid = _make_grid(10, 10)
        rooms = [_make_node("r1", 2, 2)]
        architect = _make_architect_result(rooms)
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        expected = 4 / 100
        assert abs(result.occupancy_ratio - expected) < 1e-6


class TestRoomPlacementEngineSerialization:
    """Tests for serialization."""

    def test_result_to_dict(self) -> None:
        """PlacementResult can be serialized to dict."""
        grid = _make_grid(10, 10)
        rooms = [_make_node("r1", 2, 2)]
        architect = _make_architect_result(rooms)
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        data = result.to_dict()
        assert "grid" in data
        assert "placed_rooms" in data
        assert "unplaced_rooms" in data
        assert "success" in data

    def test_result_from_dict(self) -> None:
        """PlacementResult can be deserialized from dict."""
        grid = _make_grid(10, 10)
        rooms = [_make_node("r1", 2, 2)]
        architect = _make_architect_result(rooms)
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        restored = PlacementResult.from_dict(result.to_dict())
        assert restored.placed_count == result.placed_count
        assert restored.unplaced_count == result.unplaced_count
        assert restored.success == result.success


class TestRoomPlacementEngineDeterministic:
    """Tests for deterministic ordering."""

    def test_deterministic_output(self) -> None:
        """Same input produces same output."""
        grid = _make_grid(10, 10)
        rooms = [
            _make_node("r1", 2, 2),
            _make_node("r2", 3, 3),
            _make_node("r3", 1, 1),
        ]
        architect = _make_architect_result(rooms)
        engine = RoomPlacementEngine()
        result1 = engine.place(architect, grid)
        result2 = engine.place(architect, grid)
        assert result1.placed_count == result2.placed_count
        for r1, r2 in zip(result1.placed_rooms, result2.placed_rooms):
            assert r1 == r2


class TestRoomPlacementEngineValidation:
    """Tests for validation."""

    def test_no_out_of_bounds(self) -> None:
        """No room placed outside grid bounds."""
        grid = _make_grid(5, 5)
        rooms = [_make_node("r1", 3, 3)]
        architect = _make_architect_result(rooms)
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        for room in result.placed_rooms:
            assert room.x >= 0
            assert room.y >= 0
            assert room.x + room.width <= grid.width
            assert room.y + room.height <= grid.height

    def test_no_overlaps(self) -> None:
        """No overlapping rooms."""
        grid = _make_grid(10, 10)
        rooms = [
            _make_node("r1", 3, 3),
            _make_node("r2", 3, 3),
            _make_node("r3", 3, 3),
        ]
        architect = _make_architect_result(rooms)
        engine = RoomPlacementEngine()
        result = engine.place(architect, grid)
        placed = list(result.placed_rooms)
        for i in range(len(placed)):
            for j in range(i + 1, len(placed)):
                assert not placed[i].overlaps(placed[j])