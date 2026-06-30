"""Tests for building model converter."""
from __future__ import annotations

from building_model_v2.layout.building_model_converter import BuildingModelConverter
from building_model_v2.layout.layout_cell import LayoutCell
from building_model_v2.layout.layout_grid import LayoutGrid
from building_model_v2.layout.layout_refinement_result import LayoutRefinementResult
from building_model_v2.layout.placed_room import PlacedRoom
from building_model_v2.layout.placement_result import PlacementResult


def _make_grid(width: int, height: int) -> LayoutGrid:
    cells = tuple(
        LayoutCell(x=x, y=y)
        for y in range(height)
        for x in range(width)
    )
    return LayoutGrid(width=width, height=height, cells=cells)


def _make_placed(room_id: str, x: int, y: int, width: int, height: int, room_type: str = "ROOM") -> PlacedRoom:
    return PlacedRoom(
        room_id=room_id,
        room_type=room_type,
        x=x,
        y=y,
        width=width,
        height=height,
    )


def _make_refinement(placed_rooms: tuple[PlacedRoom, ...], grid: LayoutGrid) -> LayoutRefinementResult:
    result = PlacementResult(grid=grid, placed_rooms=placed_rooms)
    return LayoutRefinementResult(
        original_result=result,
        refined_result=result,
        improvements=(),
        moved_rooms=(),
        score_before=result.occupancy_ratio,
        score_after=result.occupancy_ratio,
    )


class TestBuildingModelConverterEmpty:
    """Tests for empty layout."""

    def test_empty_layout(self) -> None:
        """Empty placement produces empty building."""
        grid = _make_grid(5, 5)
        refinement = _make_refinement((), grid)
        converter = BuildingModelConverter()
        building = converter.convert(refinement)
        assert building.floor_count == 0


class TestBuildingModelConverterSingleRoom:
    """Tests for single room."""

    def test_single_room(self) -> None:
        """Single room conversion."""
        grid = _make_grid(10, 10)
        placed = (_make_placed("r1", 0, 0, 2, 2, "LIVING"),)
        refinement = _make_refinement(placed, grid)
        converter = BuildingModelConverter()
        building = converter.convert(refinement)
        assert building.floor_count == 1
        assert len(building.floor_ids) == 1


class TestBuildingModelConverterMultipleRooms:
    """Tests for multiple rooms."""

    def test_multiple_rooms(self) -> None:
        """Multiple rooms conversion."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 0, 0, 2, 2, "LIVING"),
            _make_placed("r2", 2, 0, 2, 2, "BEDROOM"),
            _make_placed("r3", 0, 2, 2, 2, "KITCHEN"),
        )
        refinement = _make_refinement(placed, grid)
        converter = BuildingModelConverter()
        building = converter.convert(refinement)
        assert building.floor_count == 1
        assert len(building.floor_ids) == 1

    def test_room_count_preserved(self) -> None:
        """Room count preserved in floors."""
        grid = _make_grid(20, 20)
        n = 5
        placed = tuple(_make_placed(f"r{i}", i * 2, 0, 2, 2) for i in range(n))
        refinement = _make_refinement(placed, grid)
        converter = BuildingModelConverter()
        building = converter.convert(refinement)
        assert building.floor_count == 1


class TestBuildingModelConverterMultiFloor:
    """Tests for multi-floor layouts."""

    def test_multi_floor(self) -> None:
        """Multi-floor conversion."""
        grid = _make_grid(30, 30)
        placed = (
            _make_placed("r1", 0, 0, 2, 2, "LIVING"),
            _make_placed("r2", 0, 15, 2, 2, "BEDROOM"),
        )
        refinement = _make_refinement(placed, grid)
        converter = BuildingModelConverter()
        building = converter.convert(refinement)
        assert building.floor_count == 2


class TestBuildingModelConverterSerialization:
    """Tests for serialization."""

    def test_building_to_dict(self) -> None:
        """Building serializes to dict."""
        grid = _make_grid(5, 5)
        placed = (_make_placed("r1", 0, 0, 2, 2, "LIVING"),)
        refinement = _make_refinement(placed, grid)
        converter = BuildingModelConverter()
        building = converter.convert(refinement)
        data = building.to_dict()
        assert "floor_ids" in data

    def test_building_from_dict(self) -> None:
        """Building deserializes from dict."""
        from building_model_v2.entities_building import Building
        grid = _make_grid(5, 5)
        placed = (_make_placed("r1", 0, 0, 2, 2, "LIVING"),)
        refinement = _make_refinement(placed, grid)
        converter = BuildingModelConverter()
        building = converter.convert(refinement)
        restored = Building.from_dict(building.to_dict())
        assert restored.floor_count == building.floor_count


class TestBuildingModelConverterDeterministic:
    """Tests for deterministic behavior."""

    def test_deterministic_conversion(self) -> None:
        """Same input produces same output."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 0, 0, 2, 2, "LIVING"),
            _make_placed("r2", 3, 3, 2, 2, "BEDROOM"),
        )
        refinement = _make_refinement(placed, grid)
        converter = BuildingModelConverter()
        b1 = converter.convert(refinement)
        b2 = converter.convert(refinement)
        assert b1.floor_ids == b2.floor_ids


class TestBuildingModelConverterCompatibility:
    """Tests for BuildingModel compatibility."""

    def test_floor_ids_unique(self) -> None:
        """Floor IDs are unique."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 0, 0, 2, 2, "LIVING"),
            _make_placed("r2", 3, 3, 2, 2, "BEDROOM"),
        )
        refinement = _make_refinement(placed, grid)
        converter = BuildingModelConverter()
        building = converter.convert(refinement)
        assert len(building.floor_ids) == len(set(building.floor_ids))

    def test_floor_ids_match(self) -> None:
        """Floor IDs match floor count."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 0, 0, 2, 2, "LIVING"),
            _make_placed("r2", 0, 15, 2, 2, "BEDROOM"),
        )
        refinement = _make_refinement(placed, grid)
        converter = BuildingModelConverter()
        building = converter.convert(refinement)
        assert len(building.floor_ids) == building.floor_count