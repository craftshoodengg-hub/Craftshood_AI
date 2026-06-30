"""Tests for placement validator."""
from __future__ import annotations

import pytest

from building_model_v2.layout.layout_cell import LayoutCell
from building_model_v2.layout.layout_grid import LayoutGrid
from building_model_v2.layout.placed_room import PlacedRoom
from building_model_v2.layout.placement_issue import PlacementIssue
from building_model_v2.layout.placement_result import PlacementResult
from building_model_v2.layout.placement_validator import PlacementValidator
from building_model_v2.layout.placement_validation_result import PlacementValidationResult


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


class TestPlacementValidatorValid:
    """Tests for valid placement."""

    def test_valid_single_room(self) -> None:
        """Valid single room placement."""
        grid = _make_grid(5, 5)
        placed = (_make_placed("r1", 0, 0, 2, 2),)
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert vr.valid is True
        assert vr.error_count == 0

    def test_valid_multiple_non_overlapping(self) -> None:
        """Valid multiple rooms without overlap."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 0, 0, 2, 2),
            _make_placed("r2", 2, 0, 2, 2),
            _make_placed("r3", 0, 2, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert vr.valid is True

    def test_valid_with_unplaced(self) -> None:
        """Valid even with unplaced rooms."""
        grid = _make_grid(5, 5)
        placed = (_make_placed("r1", 0, 0, 2, 2),)
        unplaced = (_make_placed("r2", 0, 0, 10, 10),)
        result = PlacementResult(grid=grid, placed_rooms=placed, unplaced_rooms=unplaced)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert vr.error_count == 0
        assert vr.warning_count == 1


class TestPlacementValidatorOverlap:
    """Tests for overlap detection."""

    def test_overlap_identical_rooms(self) -> None:
        """Identical rooms overlap."""
        grid = _make_grid(5, 5)
        placed = (
            _make_placed("r1", 0, 0, 2, 2),
            _make_placed("r2", 0, 0, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert vr.valid is False
        assert any(issue.issue_type == "overlap" for issue in vr.issues)

    def test_overlap_partial(self) -> None:
        """Partial overlap detected."""
        grid = _make_grid(5, 5)
        placed = (
            _make_placed("r1", 0, 0, 3, 3),
            _make_placed("r2", 2, 2, 3, 3),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert vr.valid is False
        assert vr.error_count == 1

    def test_overlap_contained(self) -> None:
        """One room inside another detected."""
        grid = _make_grid(5, 5)
        placed = (
            _make_placed("r1", 0, 0, 5, 5),
            _make_placed("r2", 1, 1, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert vr.valid is False

    def test_no_overlap_separated(self) -> None:
        """Separated rooms do not trigger overlap."""
        grid = _make_grid(10, 10)
        placed = (
            _make_placed("r1", 0, 0, 2, 2),
            _make_placed("r2", 5, 5, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert vr.error_count == 0

    def test_no_overlap_touching_edges(self) -> None:
        """Rooms touching edges only do not overlap."""
        grid = _make_grid(5, 5)
        placed = (
            _make_placed("r1", 0, 0, 2, 2),
            _make_placed("r2", 2, 0, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert vr.error_count == 0


class TestPlacementValidatorBounds:
    """Tests for boundary detection."""

    def test_out_of_bounds_positive(self) -> None:
        """Room exceeding right/bottom bounds."""
        grid = _make_grid(3, 3)
        placed = (_make_placed("r1", 2, 2, 2, 2),)
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert vr.valid is False
        assert any(issue.issue_type == "out_of_bounds" for issue in vr.issues)

    def test_room_within_bounds(self) -> None:
        """Room within bounds passes bounds check."""
        grid = _make_grid(5, 5)
        placed = (_make_placed("r1", 0, 0, 2, 2),)
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert not any(issue.issue_type == "out_of_bounds" for issue in vr.issues)


class TestPlacementValidatorDuplicate:
    """Tests for duplicate ID detection."""

    def test_duplicate_ids(self) -> None:
        """Duplicate room IDs detected."""
        grid = _make_grid(5, 5)
        placed = (
            _make_placed("r1", 0, 0, 2, 2),
            _make_placed("r1", 3, 3, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert vr.valid is False
        assert any(issue.issue_type == "duplicate_id" for issue in vr.issues)

    def test_unique_ids(self) -> None:
        """Unique room IDs pass."""
        grid = _make_grid(5, 5)
        placed = (
            _make_placed("r1", 0, 0, 2, 2),
            _make_placed("r2", 3, 3, 2, 2),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert not any(issue.issue_type == "duplicate_id" for issue in vr.issues)


class TestPlacementValidatorZeroArea:
    """Tests for zero-area detection."""

    def test_unit_area_room(self) -> None:
        """1x1 room has positive area."""
        grid = _make_grid(5, 5)
        placed = (_make_placed("r1", 0, 0, 1, 1),)
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert not any(issue.issue_type == "zero_area" for issue in vr.issues)


class TestPlacementValidatorSerialization:
    """Tests for serialization."""

    def test_result_to_dict(self) -> None:
        """ValidationResult serializes to dict."""
        grid = _make_grid(5, 5)
        placed = (_make_placed("r1", 0, 0, 2, 2),)
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        data = vr.to_dict()
        assert "valid" in data
        assert "issues" in data

    def test_result_from_dict(self) -> None:
        """ValidationResult deserializes from dict."""
        grid = _make_grid(5, 5)
        placed = (_make_placed("r1", 0, 0, 2, 2),)
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        restored = PlacementValidationResult.from_dict(vr.to_dict())
        assert restored.valid == vr.valid
        assert restored.error_count == vr.error_count


class TestPlacementValidatorResult:
    """Tests for validation result properties."""

    def test_valid_result(self) -> None:
        """Valid result properties."""
        grid = _make_grid(5, 5)
        placed = (_make_placed("r1", 0, 0, 2, 2),)
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert vr.valid is True
        assert vr.error_count == 0
        assert vr.warning_count == 0

    def test_error_result(self) -> None:
        """Error result properties."""
        grid = _make_grid(5, 5)
        placed = (
            _make_placed("r1", 0, 0, 3, 3),
            _make_placed("r2", 2, 2, 3, 3),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert vr.valid is False
        assert vr.error_count > 0


class TestPlacementValidatorDeterministic:
    """Tests for deterministic behavior."""

    def test_deterministic(self) -> None:
        """Same input produces same output."""
        grid = _make_grid(5, 5)
        placed = (
            _make_placed("r1", 0, 0, 3, 3),
            _make_placed("r2", 2, 2, 3, 3),
        )
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr1 = validator.validate(result)
        vr2 = validator.validate(result)
        assert vr1.valid == vr2.valid
        assert len(vr1.issues) == len(vr2.issues)


class TestPlacementValidatorEmpty:
    """Tests for empty placement."""

    def test_empty_placement(self) -> None:
        """Empty placement produces warning."""
        grid = _make_grid(5, 5)
        result = PlacementResult(grid=grid)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert any(issue.issue_type == "empty_placement" for issue in vr.issues)

    def test_empty_grid(self) -> None:
        """Empty grid produces warning."""
        grid = _make_grid(1, 1)
        result = PlacementResult(grid=grid)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert any(issue.issue_type == "empty_placement" for issue in vr.issues)


class TestPlacementValidatorLarge:
    """Tests for large layouts."""

    def test_large_layout_no_issues(self) -> None:
        """Large layout with no issues."""
        grid = _make_grid(20, 20)
        placed = tuple(_make_placed(f"r{i}", i * 2, 0, 2, 2) for i in range(10))
        result = PlacementResult(grid=grid, placed_rooms=placed)
        validator = PlacementValidator()
        vr = validator.validate(result)
        assert vr.valid is True