"""Placement result model.

Immutable dataclass representing the result of room placement.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Tuple

from .layout_grid import LayoutGrid
from .placed_room import PlacedRoom


@dataclass(frozen=True, slots=True)
class PlacementResult:
    """Immutable result of room placement.

    Attributes:
        grid: The layout grid used for placement.
        placed_rooms: Tuple of successfully placed rooms.
        unplaced_rooms: Tuple of rooms that could not be placed.
        success: Whether all rooms were placed successfully.
        metadata: Additional metadata.
    """

    grid: LayoutGrid
    placed_rooms: Tuple[PlacedRoom, ...] = ()
    unplaced_rooms: Tuple[PlacedRoom, ...] = ()
    success: bool = True
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    def placed_count(self) -> int:
        """Number of successfully placed rooms."""
        return len(self.placed_rooms)

    @property
    def unplaced_count(self) -> int:
        """Number of rooms that could not be placed."""
        return len(self.unplaced_rooms)

    @property
    def occupancy_ratio(self) -> float:
        """Ratio of occupied cells to total grid cells.

        Returns:
            Float between 0.0 and 1.0.
        """
        if self.grid.area() == 0:
            return 0.0
        occupied = sum(room.area() for room in self.placed_rooms)
        return occupied / self.grid.area()

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "grid": self.grid.to_dict(),
            "placed_rooms": [r.to_dict() for r in self.placed_rooms],
            "unplaced_rooms": [r.to_dict() for r in self.unplaced_rooms],
            "success": self.success,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PlacementResult:
        """Deserialize from dictionary."""
        grid = LayoutGrid.from_dict(data["grid"])
        placed_rooms = tuple(PlacedRoom.from_dict(r) for r in data["placed_rooms"])
        unplaced_rooms = tuple(PlacedRoom.from_dict(r) for r in data["unplaced_rooms"])
        success = data["success"]
        metadata = dict(data.get("metadata", {}))
        return cls(
            grid=grid,
            placed_rooms=placed_rooms,
            unplaced_rooms=unplaced_rooms,
            success=success,
            metadata=metadata,
        )