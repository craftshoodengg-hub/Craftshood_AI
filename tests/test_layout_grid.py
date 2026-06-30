"""Tests for layout grid foundation."""
from __future__ import annotations

import pytest

from building_model_v2.layout.layout_cell import LayoutCell
from building_model_v2.layout.layout_grid import LayoutGrid


def _make_grid(width: int, height: int) -> LayoutGrid:
    """Create an empty layout grid."""
    cells = tuple(
        LayoutCell(x=x % width, y=y)
        for y in range(height)
        for x in range(width)
    )
    return LayoutGrid(width=width, height=height, cells=cells)


class TestLayoutCellConstruction:
    """Tests for LayoutCell construction."""

    def test_create_cell(self) -> None:
        """Test creating a valid cell."""
        cell = LayoutCell(x=1, y=2)
        assert cell.x == 1
        assert cell.y == 2
        assert cell.occupied is False
        assert cell.room_id is None
        assert cell.zone is None

    def test_create_occupied_cell(self) -> None:
        """Test creating an occupied cell."""
        cell = LayoutCell(x=0, y=0, occupied=True, room_id="room1")
        assert cell.occupied is True
        assert cell.room_id == "room1"

    def test_create_cell_with_zone(self) -> None:
        """Test creating a cell with zone."""
        cell = LayoutCell(x=1, y=1, zone="zoneA")
        assert cell.zone == "zoneA"

    def test_zero_coordinates_allowed(self) -> None:
        """Test that zero coordinates are valid."""
        cell = LayoutCell(x=0, y=0)
        assert cell.x == 0
        assert cell.y == 0

    def test_negative_x_raises(self) -> None:
        """Test that negative x raises error."""
        with pytest.raises(ValueError, match="x must be non-negative"):
            LayoutCell(x=-1, y=0)

    def test_negative_y_raises(self) -> None:
        """Test that negative y raises error."""
        with pytest.raises(ValueError, match="y must be non-negative"):
            LayoutCell(x=0, y=-1)


class TestLayoutCellSerialization:
    """Tests for LayoutCell serialization."""

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        cell = LayoutCell(x=1, y=2, occupied=True, room_id="r1", zone="z1")
        data = cell.to_dict()
        assert data["x"] == 1
        assert data["y"] == 2
        assert data["occupied"] is True
        assert data["room_id"] == "r1"
        assert data["zone"] == "z1"

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {"x": 1, "y": 2, "occupied": True, "room_id": "r1", "zone": "z1"}
        cell = LayoutCell.from_dict(data)
        assert cell.x == 1
        assert cell.y == 2
        assert cell.room_id == "r1"

    def test_round_trip(self) -> None:
        """Test serialization round-trip."""
        original = LayoutCell(x=3, y=4, occupied=True, room_id="r2", zone="z2")
        data = original.to_dict()
        restored = LayoutCell.from_dict(data)
        assert restored == original

    def test_defaults_in_from_dict(self) -> None:
        """Test that defaults are applied when fields are missing."""
        data = {"x": 1, "y": 2}
        cell = LayoutCell.from_dict(data)
        assert cell.occupied is False
        assert cell.room_id is None
        assert cell.zone is None

    def test_immutable(self) -> None:
        """Test that cell is frozen."""
        cell = LayoutCell(x=0, y=0)
        with pytest.raises(AttributeError):
            cell.x = 1  # type: ignore[misc]


class TestLayoutGridConstruction:
    """Tests for LayoutGrid construction."""

    def test_create_grid(self) -> None:
        """Test creating a valid grid."""
        grid = _make_grid(3, 2)
        assert grid.width == 3
        assert grid.height == 2
        assert grid.cells is not None

    def test_width_must_be_positive(self) -> None:
        """Test that zero or negative width raises error."""
        with pytest.raises(ValueError, match="width must be positive"):
            _make_grid(0, 2)
        with pytest.raises(ValueError, match="width must be positive"):
            _make_grid(-1, 2)

    def test_height_must_be_positive(self) -> None:
        """Test that zero or negative height raises error."""
        with pytest.raises(ValueError, match="height must be positive"):
            _make_grid(2, 0)
        with pytest.raises(ValueError, match="height must be positive"):
            _make_grid(2, -1)

    def test_cells_length_mismatch_raises(self) -> None:
        """Test that incorrect cells length raises error."""
        with pytest.raises(ValueError, match="cells length"):
            LayoutGrid(width=2, height=2, cells=tuple())
        with pytest.raises(ValueError, match="cells length"):
            LayoutGrid(width=2, height=2, cells=tuple([LayoutCell(x=0, y=0) for _ in range(3)]))


class TestLayoutGridCellAccess:
    """Tests for cell access methods."""

    def test_cell_access(self) -> None:
        """Test accessing cells by coordinates."""
        grid = _make_grid(3, 2)
        cell = grid.cell(1, 1)
        assert cell.x == 1
        assert cell.y == 1

    def test_cell_out_of_bounds_raises(self) -> None:
        """Test that out-of-bounds access raises error."""
        grid = _make_grid(3, 2)
        with pytest.raises(IndexError, match="out of bounds"):
            grid.cell(-1, 0)
        with pytest.raises(IndexError, match="out of bounds"):
            grid.cell(0, -1)
        with pytest.raises(IndexError, match="out of bounds"):
            grid.cell(3, 0)
        with pytest.raises(IndexError, match="out of bounds"):
            grid.cell(0, 2)

    def test_in_bounds_true(self) -> None:
        """Test in_bounds returns True for valid coordinates."""
        grid = _make_grid(3, 2)
        assert grid.in_bounds(0, 0) is True
        assert grid.in_bounds(2, 1) is True
        assert grid.in_bounds(1, 0) is True

    def test_in_bounds_false(self) -> None:
        """Test in_bounds returns False for invalid coordinates."""
        grid = _make_grid(3, 2)
        assert grid.in_bounds(-1, 0) is False
        assert grid.in_bounds(0, -1) is False
        assert grid.in_bounds(3, 0) is False
        assert grid.in_bounds(0, 2) is False


class TestLayoutGridNeighbors:
    """Tests for neighbor queries."""

    def test_neighbors_corner(self) -> None:
        """Test neighbors at a corner cell (0, 0)."""
        grid = _make_grid(3, 2)
        neighbors = grid.neighbors(0, 0)
        # Should have East (1,0) and South (0,1) in N,E,S,W order
        assert len(neighbors) == 2
        assert neighbors[0].x == 1 and neighbors[0].y == 0  # East
        assert neighbors[1].x == 0 and neighbors[1].y == 1  # South

    def test_neighbors_interior(self) -> None:
        """Test neighbors at an interior cell."""
        grid = _make_grid(3, 2)
        # Interior cell (1, 0) has 3 neighbors
        neighbors = grid.neighbors(1, 0)
        assert len(neighbors) == 3
        # North (out of bounds, omitted), East (2,0), South (1,1), West (0,0)
        assert neighbors[0].x == 2 and neighbors[0].y == 0  # East
        assert neighbors[1].x == 1 and neighbors[1].y == 1  # South
        assert neighbors[2].x == 0 and neighbors[2].y == 0  # West

    def test_neighbors_deterministic_order(self) -> None:
        """Test that neighbors are returned in N, E, S, W order."""
        grid = _make_grid(5, 5)
        neighbors = grid.neighbors(2, 2)
        # Center cell (2,2) has 4 neighbors in N,E,S,W order
        assert len(neighbors) == 4
        assert (neighbors[0].x, neighbors[0].y) == (2, 1)  # North
        assert (neighbors[1].x, neighbors[1].y) == (3, 2)  # East
        assert (neighbors[2].x, neighbors[2].y) == (2, 3)  # South
        assert (neighbors[3].x, neighbors[3].y) == (1, 2)  # West

    def test_neighbors_edge(self) -> None:
        """Test neighbors at an edge cell."""
        grid = _make_grid(3, 3)
        # Top edge cell (1, 0)
        neighbors = grid.neighbors(1, 0)
        assert len(neighbors) == 3
        # East, South, West
        assert (neighbors[0].x, neighbors[0].y) == (2, 0)
        assert (neighbors[1].x, neighbors[1].y) == (1, 1)
        assert (neighbors[2].x, neighbors[2].y) == (0, 0)

    def test_neighbors_1x1_grid(self) -> None:
        """Test neighbors in a 1x1 grid (no neighbors)."""
        grid = _make_grid(1, 1)
        neighbors = grid.neighbors(0, 0)
        assert len(neighbors) == 0


class TestLayoutGridOccupancy:
    """Tests for occupancy methods."""

    def test_initial_occupancy(self) -> None:
        """Test initial occupancy ratio."""
        grid = _make_grid(3, 2)
        assert grid.occupancy_ratio() == 0.0
        assert len(grid.occupied_cells()) == 0
        assert len(grid.empty_cells()) == 6

    def test_occupied_cells(self) -> None:
        """Test getting occupied cells."""
        grid = _make_grid(3, 2)
        cells = list(grid.cells)
        cells[0] = LayoutCell(x=0, y=0, occupied=True)
        cells[3] = LayoutCell(x=0, y=1, occupied=True, room_id="r1")
        grid = LayoutGrid(width=3, height=2, cells=tuple(cells))
        occupied = grid.occupied_cells()
        assert len(occupied) == 2
        assert occupied[0].occupied is True
        assert occupied[1].room_id == "r1"

    def test_empty_cells(self) -> None:
        """Test getting empty cells."""
        grid = _make_grid(3, 2)
        cells = list(grid.cells)
        cells[0] = LayoutCell(x=0, y=0, occupied=True)
        grid = LayoutGrid(width=3, height=2, cells=tuple(cells))
        empty = grid.empty_cells()
        assert len(empty) == 5

    def test_occupancy_ratio_partial(self) -> None:
        """Test occupancy ratio with partial occupancy."""
        grid = _make_grid(3, 2)
        cells = list(grid.cells)
        cells[0] = LayoutCell(x=0, y=0, occupied=True)
        cells[1] = LayoutCell(x=1, y=0, occupied=True)
        grid = LayoutGrid(width=3, height=2, cells=tuple(cells))
        ratio = grid.occupancy_ratio()
        assert ratio == 2.0 / 6.0

    def test_occupancy_ratio_full(self) -> None:
        """Test occupancy ratio with full occupancy."""
        cells = tuple(LayoutCell(x=x % 3, y=y, occupied=True) for y in range(2) for x in range(3))
        grid = LayoutGrid(width=3, height=2, cells=cells)
        assert grid.occupancy_ratio() == 1.0


class TestLayoutGridSerialization:
    """Tests for LayoutGrid serialization."""

    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        grid = _make_grid(2, 2)
        data = grid.to_dict()
        assert data["width"] == 2
        assert data["height"] == 2
        assert len(data["cells"]) == 4

    def test_from_dict(self) -> None:
        """Test deserialization from dictionary."""
        data = {
            "width": 2,
            "height": 2,
            "cells": [
                {"x": 0, "y": 0, "occupied": False, "room_id": None, "zone": None},
                {"x": 1, "y": 0, "occupied": False, "room_id": None, "zone": None},
                {"x": 0, "y": 1, "occupied": False, "room_id": None, "zone": None},
                {"x": 1, "y": 1, "occupied": False, "room_id": None, "zone": None},
            ],
        }
        grid = LayoutGrid.from_dict(data)
        assert grid.width == 2
        assert grid.height == 2
        assert len(grid.cells) == 4

    def test_round_trip(self) -> None:
        """Test serialization round-trip."""
        original = _make_grid(3, 2)
        data = original.to_dict()
        restored = LayoutGrid.from_dict(data)
        assert restored.width == original.width
        assert restored.height == original.height
        assert len(restored.cells) == len(original.cells)


class TestLayoutGridEquality:
    """Tests for LayoutGrid equality and immutability."""

    def test_equality(self) -> None:
        """Test grid equality."""
        grid1 = _make_grid(2, 2)
        grid2 = _make_grid(2, 2)
        assert grid1 == grid2

    def test_inequality_different_size(self) -> None:
        """Test grids with different sizes are not equal."""
        grid1 = _make_grid(2, 2)
        grid2 = _make_grid(3, 2)
        assert grid1 != grid2

    def test_immutable(self) -> None:
        """Test that grid is frozen."""
        grid = _make_grid(2, 2)
        with pytest.raises(AttributeError):
            grid.width = 3  # type: ignore[misc]

    def test_cells_immutable(self) -> None:
        """Test that cells tuple is immutable."""
        grid = _make_grid(2, 2)
        with pytest.raises(AttributeError):
            grid.cells = ()  # type: ignore[misc]


class TestLayoutGridEdgeCases:
    """Tests for edge cases."""

    def test_1x1_grid(self) -> None:
        """Test a 1x1 grid."""
        grid = _make_grid(1, 1)
        assert grid.width == 1
        assert grid.height == 1
        assert len(grid.cells) == 1
        assert grid.occupancy_ratio() == 0.0

    def test_large_grid(self) -> None:
        """Test a larger grid."""
        grid = _make_grid(10, 10)
        assert grid.width == 10
        assert grid.height == 10
        assert len(grid.cells) == 100
        assert grid.occupancy_ratio() == 0.0

    def test_neighbors_boundary(self) -> None:
        """Test neighbors at various boundaries."""
        grid = _make_grid(3, 3)
        # Top-right corner (2, 0)
        n = grid.neighbors(2, 0)
        assert len(n) == 2
        # Bottom-left corner (0, 2)
        n = grid.neighbors(0, 2)
        assert len(n) == 2
        # Bottom-center (1, 2)
        n = grid.neighbors(1, 2)
        assert len(n) == 3

    def test_empty_grid_occupancy(self) -> None:
        """Test occupancy on empty grid."""
        grid = _make_grid(2, 2)
        assert len(grid.empty_cells()) == 4
        assert len(grid.occupied_cells()) == 0
        assert grid.occupancy_ratio() == 0.0

    def test_occupancy_ratio_empty_cells(self) -> None:
        """Test occupancy ratio returns 0 for empty grid."""
        grid = _make_grid(1, 1)
        assert grid.occupancy_ratio() == 0.0

    def test_row_major_ordering(self) -> None:
        """Test that cells are stored in row-major order."""
        grid = _make_grid(3, 2)
        # Row 0: (0,0), (1,0), (2,0)
        # Row 1: (0,1), (1,1), (2,1)
        assert grid.cells[0].x == 0 and grid.cells[0].y == 0
        assert grid.cells[1].x == 1 and grid.cells[1].y == 0
        assert grid.cells[2].x == 2 and grid.cells[2].y == 0
        assert grid.cells[3].x == 0 and grid.cells[3].y == 1
        assert grid.cells[4].x == 1 and grid.cells[4].y == 1
        assert grid.cells[5].x == 2 and grid.cells[5].y == 1

    def test_deterministic_cell_retrieval(self) -> None:
        """Test that cell retrieval is deterministic."""
        grid = _make_grid(5, 5)
        for y in range(5):
            for x in range(5):
                cell1 = grid.cell(x, y)
                cell2 = grid.cell(x, y)
                assert cell1 == cell2