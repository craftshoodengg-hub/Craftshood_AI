"""Layout grid for grid-based room placement.

Immutable dataclass representing a 2D grid of layout cells.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterator

from .layout_cell import LayoutCell


@dataclass(frozen=True, slots=True)
class LayoutGrid:
    """Immutable 2D grid of layout cells.

    Represents a rectangular grid for room placement with
    occupancy tracking and neighborhood queries.

    Attributes:
        width: Number of columns (must be > 0).
        height: Number of rows (must be > 0).
        cells: Tuple of cell data, stored row-major (index = y * width + x).
    """

    width: int
    height: int
    cells: tuple[LayoutCell, ...]

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        if self.width <= 0:
            raise ValueError("width must be positive")
        if self.height <= 0:
            raise ValueError("height must be positive")
        expected_count = self.width * self.height
        if len(self.cells) != expected_count:
            raise ValueError(
                f"cells length {len(self.cells)} does not match "
                f"width * height = {expected_count}"
            )

    def _index(self, x: int, y: int) -> int:
        """Compute the index in the cells tuple for (x, y).

        Args:
            x: X coordinate (column).
            y: Y coordinate (row).

        Returns:
            Index in the cells tuple.
        """
        return y * self.width + x

    def cell(self, x: int, y: int) -> LayoutCell:
        """Get the cell at (x, y).

        Args:
            x: X coordinate (column).
            y: Y coordinate (row).

        Returns:
            The LayoutCell at the specified position.

        Raises:
            IndexError: If the coordinates are out of bounds.
        """
        self._check_bounds(x, y)
        return self.cells[self._index(x, y)]

    def _check_bounds(self, x: int, y: int) -> None:
        """Check if (x, y) is within grid bounds.

        Args:
            x: X coordinate (column).
            y: Y coordinate (row).

        Raises:
            IndexError: If the coordinates are out of bounds.
        """
        if not self.in_bounds(x, y):
            raise IndexError(f"Cell ({x}, {y}) is out of bounds")

    def in_bounds(self, x: int, y: int) -> bool:
        """Check if (x, y) is within grid bounds.

        Args:
            x: X coordinate (column).
            y: Y coordinate (row).

        Returns:
            True if (x, y) is within bounds, False otherwise.
        """
        if x < 0 or y < 0:
            return False
        if x >= self.width or y >= self.height:
            return False
        return True

    def area(self) -> int:
        """Total number of cells in the grid.

        Returns:
            Total cell count.
        """
        return self.width * self.height

    def neighbors(self, x: int, y: int) -> tuple[LayoutCell, ...]:
        """Get the four orthogonal neighbors of (x, y).

        Returns neighbors in deterministic order: North, East, South, West.
        Out-of-bounds neighbors are omitted.

        Args:
            x: X coordinate (column).
            y: Y coordinate (row).

        Returns:
            Tuple of neighbor cells in N, E, S, W order.
        """
        # N, E, S, W
        deltas = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        result: list[LayoutCell] = []
        for dx, dy in deltas:
            nx = x + dx
            ny = y + dy
            if self.in_bounds(nx, ny):
                result.append(self.cell(nx, ny))
        return tuple(result)

    def occupied_cells(self) -> tuple[LayoutCell, ...]:
        """Get all occupied cells.

        Returns:
            Tuple of occupied cells in row-major order.
        """
        return tuple(cell for cell in self.cells if cell.occupied)

    def empty_cells(self) -> tuple[LayoutCell, ...]:
        """Get all empty cells.

        Returns:
            Tuple of empty cells in row-major order.
        """
        return tuple(cell for cell in self.cells if not cell.occupied)

    def occupancy_ratio(self) -> float:
        """Compute the occupancy ratio.

        Returns:
            Fraction of occupied cells (0.0 to 1.0).
            Returns 0.0 if the grid has no cells.
        """
        if len(self.cells) == 0:
            return 0.0
        occupied = len(self.occupied_cells())
        return occupied / len(self.cells)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "width": self.width,
            "height": self.height,
            "cells": tuple(cell.to_dict() for cell in self.cells),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LayoutGrid:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing grid data.

        Returns:
            New LayoutGrid instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        cells = tuple(LayoutCell.from_dict(cell_data) for cell_data in data["cells"])
        return cls(
            width=data["width"],
            height=data["height"],
            cells=cells,
        )