"""Vastu Direction Enum for Building Model v2.

Defines the eight cardinal and intercardinal directions used in Vastu Shastra.
Each direction has a display name and angle for deterministic orientation calculations.
"""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict


class VastuDirection(Enum):
    """Eight cardinal and intercardinal directions in Vastu Shastra.

    Attributes:
        angle: Clockwise angle in degrees from North (0-360).
        display_name: Human-readable name for UI display.
    """

    NORTH = ("North", 0.0)
    NORTH_EAST = ("North-East", 45.0)
    EAST = ("East", 90.0)
    SOUTH_EAST = ("South-East", 135.0)
    SOUTH = ("South", 180.0)
    SOUTH_WEST = ("South-West", 225.0)
    WEST = ("West", 270.0)
    NORTH_WEST = ("North-West", 315.0)
    CENTER = ("Center", 0.0)

    def __init__(self, display_name: str, angle: float) -> None:
        self._display_name = display_name
        self._angle = angle

    @property
    def display_name(self) -> str:
        """Get the human-readable display name."""
        return self._display_name

    @property
    def angle(self) -> float:
        """Get the clockwise angle in degrees from North."""
        return self._angle

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "angle": self.angle,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> VastuDirection:
        """Create from dictionary."""
        return cls[data["name"]]

    @classmethod
    def from_angle(cls, angle: float) -> VastuDirection:
        """Get the closest VastuDirection from an angle.

        Args:
            angle: Clockwise angle in degrees from North (0-360).

        Returns:
            The closest VastuDirection enum member.
        """
        normalized = angle % 360.0
        # Each direction covers 45 degrees, centered on the direction angle
        # Add 22.5 to shift boundaries, then divide by 45 to get index
        index = int((normalized + 22.5) % 360.0 // 45.0)
        members = [
            cls.NORTH,
            cls.NORTH_EAST,
            cls.EAST,
            cls.SOUTH_EAST,
            cls.SOUTH,
            cls.SOUTH_WEST,
            cls.WEST,
            cls.NORTH_WEST,
        ]
        return members[index]

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"VastuDirection.{self.name}"