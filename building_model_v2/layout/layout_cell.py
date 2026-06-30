"""Layout cell for grid-based room placement.

Immutable dataclass representing a single cell in a layout grid.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class LayoutCell:
    """Immutable cell in a layout grid.

    Represents a single grid cell with position and occupancy state.

    Attributes:
        x: X coordinate (column), must be >= 0.
        y: Y coordinate (row), must be >= 0.
        occupied: Whether the cell is occupied by a room.
        room_id: ID of the room occupying this cell, if any.
        zone: Zone identifier for this cell, if any.
    """

    x: int
    y: int
    occupied: bool = False
    room_id: str | None = None
    zone: str | None = None

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        if self.x < 0:
            raise ValueError("x must be non-negative")
        if self.y < 0:
            raise ValueError("y must be non-negative")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "x": self.x,
            "y": self.y,
            "occupied": self.occupied,
            "room_id": self.room_id,
            "zone": self.zone,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> LayoutCell:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing cell data.

        Returns:
            New LayoutCell instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        return cls(
            x=data["x"],
            y=data["y"],
            occupied=data.get("occupied", False),
            room_id=data.get("room_id"),
            zone=data.get("zone"),
        )