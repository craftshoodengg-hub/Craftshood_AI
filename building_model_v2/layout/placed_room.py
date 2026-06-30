"""Placed room model for grid-based room placement.

Immutable dataclass representing a room placed on a layout grid.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class PlacedRoom:
    """Immutable placed room on a layout grid.

    Represents a room with its position and dimensions on the grid.

    Attributes:
        room_id: Unique identifier for the room (must not be empty).
        room_type: Type of the room (must not be empty).
        x: X coordinate of the top-left corner (column), must be >= 0.
        y: Y coordinate of the top-left corner (row), must be >= 0.
        width: Width of the room in cells, must be > 0.
        height: Height of the room in cells, must be > 0.
        zone: Optional zone identifier for the room.
    """

    room_id: str
    room_type: str
    x: int
    y: int
    width: int
    height: int
    zone: str | None = None

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        if not self.room_id:
            raise ValueError("room_id must not be empty")
        if not self.room_type:
            raise ValueError("room_type must not be empty")
        if self.x < 0:
            raise ValueError("x must be non-negative")
        if self.y < 0:
            raise ValueError("y must be non-negative")
        if self.width <= 0:
            raise ValueError("width must be positive")
        if self.height <= 0:
            raise ValueError("height must be positive")

    def cells(self) -> tuple[tuple[int, int], ...]:
        """Get all grid coordinates occupied by this room.

        Returns coordinates row-by-row from top-left.

        Returns:
            Tuple of (x, y) coordinates for each cell in the room.
        """
        result: list[tuple[int, int]] = []
        for dy in range(self.height):
            for dx in range(self.width):
                result.append((self.x + dx, self.y + dy))
        return tuple(result)

    def area(self) -> int:
        """Compute the area of the room in cells.

        Returns:
            Number of cells occupied by the room.
        """
        return self.width * self.height

    def contains(self, x: int, y: int) -> bool:
        """Check if a coordinate lies inside the room.

        Left/top inclusive, right/bottom exclusive.

        Args:
            x: X coordinate to check.
            y: Y coordinate to check.

        Returns:
            True if the coordinate is inside the room, False otherwise.
        """
        return self.x <= x < self.x + self.width and self.y <= y < self.y + self.height

    def overlaps(self, other: PlacedRoom) -> bool:
        """Check if this room overlaps with another room.

        Rooms touching only along an edge or corner are NOT overlapping.

        Args:
            other: Another PlacedRoom to check against.

        Returns:
            True if the rectangles overlap, False otherwise.
        """
        # Two rectangles overlap if and only if they overlap on both axes
        # For axis-aligned rectangles with exclusive right/bottom bounds:
        # They overlap if: self.x < other.x + other.width AND other.x < self.x + self.width
        #                  AND self.y < other.y + other.height AND other.y < self.y + self.height
        return (
            self.x < other.x + other.width
            and other.x < self.x + self.width
            and self.y < other.y + other.height
            and other.y < self.y + self.height
        )

    def bounds(self) -> tuple[int, int, int, int]:
        """Get the bounding box of the room.

        Returns:
            Tuple of (left, top, right, bottom).
        """
        return (self.x, self.y, self.x + self.width, self.y + self.height)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "room_id": self.room_id,
            "room_type": self.room_type,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "zone": self.zone,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PlacedRoom:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing room data.

        Returns:
            New PlacedRoom instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        return cls(
            room_id=data["room_id"],
            room_type=data["room_type"],
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            zone=data.get("zone"),
        )