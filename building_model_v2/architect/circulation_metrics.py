"""Circulation metrics for architectural circulation evaluation.

Immutable dataclass containing computed metrics about a circulation graph.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class CirculationMetrics:
    """Immutable computed metrics for a circulation graph.

    Attributes:
        total_path_length: Sum of all edge lengths in meters.
        average_path_length: Average edge length in meters.
        primary_path_count: Number of edges with width >= 1.5m (primary paths).
        secondary_path_count: Number of edges with width < 1.5m (secondary paths).
        dead_end_count: Number of nodes with degree 1 (dead ends).
        isolated_room_count: Number of nodes with degree 0 (isolated).
        connected_room_count: Number of nodes with degree >= 1.
        connectivity_ratio: Fraction of connected rooms (0.0 to 1.0).
    """

    total_path_length: float
    average_path_length: float
    primary_path_count: int
    secondary_path_count: int
    dead_end_count: int
    isolated_room_count: int
    connected_room_count: int
    connectivity_ratio: float

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        if self.total_path_length < 0:
            raise ValueError("total_path_length must be non-negative")
        if self.average_path_length < 0:
            raise ValueError("average_path_length must be non-negative")
        if self.primary_path_count < 0:
            raise ValueError("primary_path_count must be non-negative")
        if self.secondary_path_count < 0:
            raise ValueError("secondary_path_count must be non-negative")
        if self.dead_end_count < 0:
            raise ValueError("dead_end_count must be non-negative")
        if self.isolated_room_count < 0:
            raise ValueError("isolated_room_count must be non-negative")
        if self.connected_room_count < 0:
            raise ValueError("connected_room_count must be non-negative")
        if not 0.0 <= self.connectivity_ratio <= 1.0:
            raise ValueError("connectivity_ratio must be between 0.0 and 1.0")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "total_path_length": self.total_path_length,
            "average_path_length": self.average_path_length,
            "primary_path_count": self.primary_path_count,
            "secondary_path_count": self.secondary_path_count,
            "dead_end_count": self.dead_end_count,
            "isolated_room_count": self.isolated_room_count,
            "connected_room_count": self.connected_room_count,
            "connectivity_ratio": self.connectivity_ratio,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CirculationMetrics:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing metrics data.

        Returns:
            New CirculationMetrics instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        return cls(
            total_path_length=data["total_path_length"],
            average_path_length=data["average_path_length"],
            primary_path_count=data["primary_path_count"],
            secondary_path_count=data["secondary_path_count"],
            dead_end_count=data["dead_end_count"],
            isolated_room_count=data["isolated_room_count"],
            connected_room_count=data["connected_room_count"],
            connectivity_ratio=data["connectivity_ratio"],
        )