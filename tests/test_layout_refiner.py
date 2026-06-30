"""Tests for layout refiner."""
from __future__ import annotations

from building_model_v2.layout.layout_cell import LayoutCell
from building_model_v2.layout.layout_grid import LayoutGrid
from building_model_v2.layout.layout_refinement_result import LayoutRefinementResult
from building_model_v2.layout.layout_refiner import LayoutRefiner
from building_model_v2.layout.placed_room import PlacedRoom
from building_model_v2.layout.placement_result import PlacementResult


def _make_grid(width: int, height: int) -> LayoutGrid:
    cells = tuple(
        LayoutCell(x=x, y=y)
        for y in range(height)
        for x in range(width)
    )
    return LayoutGrid(width=width, height=height, cells=cells)


def _make_placed(room_id: str, x: int, y: int, width: int, height: int) -> PlacedRoom:
    return PlacedRoom(
        room_id=room_id,
        room_type="ROOM",
        x=x,
        y=y,
        width=width,
        height=height,
    )


class TestLayoutRefinerEmpty:
    """Tests for empty placement."""

    def test_empty_placement(self) -> None:
        """Empty placement returns unchanged."""
        grid = _make_grid(5, 5)
        result = PlacementResult(grid=grid)
        refiner = LayoutRefiner()
        refined = refiner.refine(result)
        assert refined.improvement_count == 0


class TestLayoutRefinerSingleRoom:
    """Tests for single room."""

    def test_single_room_moves_up_left(self) -> None:
        """Single room moves to origin."""
        grid = _make_grid(10, 10)
        placed = (_make_placed("r1", 3, 3, 2, 2),)
        result = PlacementResult(grid=grid, placed_rooms=placed)
        refiner = LayoutRefiner()
        refined = refiner.refine(result)
        assert refined.improvement_count == 1
        assert refined.refined_result.placed_rooms[0].x == 0
        assert refined.refined_result.placed_rooms[0].y == 0


class TestLayoutRefinerMultiRoom:
    """Tests for multi-room refinement."""

    def test_multiple_rooms_compact(self) -> None:
        """Multiple rooms compact toward top-left."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 2, 2, 2, 2),
            _make_placed("r2", 5, 5, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        refiner = LayoutRefiner()
        refined = refiner.refine(result)
        assert refined.improvement_count > 0
        r1 = refined.refined_result.placed_rooms[0]
        assert r1.x == 0
        assert r1.y == 0

    def test_no_overlap_after_refinement(self) -> None:
        """Refined rooms do not overlap."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 1, 1, 2, 2),
            _make_placed("r2", 4, 4, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        refiner = LayoutRefiner()
        refined = refiner.refine(result)
        rooms = refined.refined_result.placed_rooms
        for i in range(len(rooms)):
            for j in range(i + 1, len(rooms)):
                assert not rooms[i].overlaps(rooms[j])


class TestLayoutRefinerNoImprovement:
    """Tests when no improvement is possible."""

    def test_no_improvement_possible(self) -> None:
        """Already compact layout."""
        grid = _make_grid(5, 5)
        placed = (
            _make_placed("r1", 0, 0, 2, 2),
            _make_placed("r2", 2, 0, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        refiner = LayoutRefiner()
        refined = refiner.refine(result)
        assert refined.improvement_count == 0


class TestLayoutRefinerImprovementCount:
    """Tests for improvement counting."""

    def test_improvement_count_matches_moved_rooms(self) -> None:
        """Improvement count equals number of moved rooms."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 3, 3, 2, 2),
            _make_placed("r2", 6, 6, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        refiner = LayoutRefiner()
        refined = refiner.refine(result)
        assert refined.improvement_count == len(refined.moved_rooms)


class TestLayoutRefinerValidation:
    """Tests for validation preservation."""

    def test_refined_layout_valid(self) -> None:
        """Refined layout passes validation."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 2, 2, 2, 2),
            _make_placed("r2", 5, 5, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        refiner = LayoutRefiner()
        refined = refiner.refine(result)
        assert refined.refined_result.occupancy_ratio >= refined.score_before


class TestLayoutRefinerSerialization:
    """Tests for serialization."""

    def test_result_to_dict(self) -> None:
        """LayoutRefinementResult serializes to dict."""
        grid = _make_grid(5, 5)
        placed = (_make_placed("r1", 2, 2, 2, 2),)
        result = PlacementResult(grid=grid, placed_rooms=placed)
        refiner = LayoutRefiner()
        refined = refiner.refine(result)
        data = refined.to_dict()
        assert "original_result" in data
        assert "refined_result" in data

    def test_result_from_dict(self) -> None:
        """LayoutRefinementResult deserializes from dict."""
        grid = _make_grid(5, 5)
        placed = (_make_placed("r1", 2, 2, 2, 2),)
        result = PlacementResult(grid=grid, placed_rooms=placed)
        refiner = LayoutRefiner()
        refined = refiner.refine(result)
        restored = LayoutRefinementResult.from_dict(refined.to_dict())
        assert restored.improvement_count == refined.improvement_count


class TestLayoutRefinerDeterministic:
    """Tests for deterministic behavior."""

    def test_deterministic_output(self) -> None:
        """Same input produces same output."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 3, 3, 2, 2),
            _make_placed("r2", 6, 6, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        refiner = LayoutRefiner()
        refined1 = refiner.refine(result)
        refined2 = refiner.refine(result)
        assert refined1.improvement_count == refined2.improvement_count
        assert len(refined1.moved_rooms) == len(refined2.moved_rooms)


class TestLayoutRefinerOccupancyImprovement:
    """Tests for occupancy improvement."""

    def test_occupancy_improves_or_stable(self) -> None:
        """Occupancy ratio does not decrease."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 3, 3, 2, 2),
            _make_placed("r2", 7, 7, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        refiner = LayoutRefiner()
        refined = refiner.refine(result)
        assert refined.score_after >= refined.score_before


class TestLayoutRefinerRoomPreservation:
    """Tests for room preservation."""

    def test_room_ids_preserved(self) -> None:
        """Room IDs are preserved after refinement."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 3, 3, 2, 2),
            _make_placed("r2", 6, 6, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        refiner = LayoutRefiner()
        refined = refiner.refine(result)
        refined_ids = {r.room_id for r in refined.refined_result.placed_rooms}
        assert refined_ids == {"r1", "r2"}

    def test_room_sizes_preserved(self) -> None:
        """Room sizes are preserved after refinement."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 3, 3, 2, 2),
            _make_placed("r2", 6, 6, 3, 3),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        refiner = LayoutRefiner()
        refined = refiner.refine(result)
        sizes = {(r.width, r.height) for r in refined.refined_result.placed_rooms}
        assert (2, 2) in sizes
        assert (3, 3) in sizes


class TestLayoutRefinerLarge:
    """Tests for large layouts."""

    def test_large_layout(self) -> None:
        """Large layout refinement."""
        grid = _make_grid(50, 50)
        placed = tuple(
            _make_placed(f"r{i}", i * 5 + 2, 2, 4, 4)
            for i in range(8)
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        refiner = LayoutRefiner()
        refined = refiner.refine(result)
        assert refined.improvement_count >= 0
