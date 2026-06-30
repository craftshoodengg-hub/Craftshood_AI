"""Circulation edge for architectural circulation graphs.

Represents a connection or path between two circulation nodes
in a circulation network.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class CirculationEdge:
    """Immutable connection between two circulation nodes.

    Represents a path segment in the circulation network, such as
    a corridor run, hallway link, or stair flight.

    Attributes:
        source_id: ID of the source circulation node.
        target_id: ID of the target circulation node.
        length: Length of the path segment in meters. Must be > 0.
        width: Width of the path segment in meters. Must be > 0.
        bidirectional: Whether traversal is allowed in both directions.
        is_accessible: Whether this path is wheelchair accessible.
        metadata: Additional key-value metadata.
    """

    source_id: str
    target_id: str
    length: float
    width: float = 1.2
    bidirectional: bool = True
    is_accessible: bool = True
    metadata: dict[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        if not self.source_id:
            raise ValueError("source_id cannot be empty")
        if not self.target_id:
            raise ValueError("target_id cannot be empty")
        if self.source_id == self.target_id:
            raise ValueError("source_id and target_id must be different")
        if self.length <= 0:
            raise ValueError("length must be positive")
        if self.width <= 0:
            raise ValueError("width must be positive")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "source_id": self.source_id,
            "target_id": self.target_id,
            "length": self.length,
            "width": self.width,
            "bidirectional": self.bidirectional,
            "is_accessible": self.is_accessible,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CirculationEdge:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing circulation edge data.

        Returns:
            New CirculationEdge instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        return cls(
            source_id=data["source_id"],
            target_id=data["target_id"],
            length=data["length"],
            width=data.get("width", 1.2),
            bidirectional=data.get("bidirectional", True),
            is_accessible=data.get("is_accessible", True),
            metadata=dict(data.get("metadata", {})),
        )