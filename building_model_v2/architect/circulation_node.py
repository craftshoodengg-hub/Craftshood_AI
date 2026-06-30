"""Circulation node for architectural circulation graphs.

Represents a single point or space in a circulation network,
such as a corridor junction, entrance point, or key intersection.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class CirculationNode:
    """Immutable representation of a circulation node.

    Represents a point in the circulation network, such as a
    corridor segment, entrance, staircase landing, or junction.

    Attributes:
        id: Unique identifier for this circulation node.
        name: Human-readable name (e.g., "Main Corridor", "Entry Point").
        space_id: Optional reference to a source space id (e.g., BubbleNode or Room id).
        width: Width of the circulation path at this node in meters. Must be > 0.
        is_entry_exit: Whether this node is an entry or exit point.
        metadata: Additional key-value metadata.
    """

    id: str
    name: str
    space_id: str | None = None
    width: float = 1.2
    is_entry_exit: bool = False
    metadata: dict[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        if not self.id:
            raise ValueError("id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        if self.width <= 0:
            raise ValueError("width must be positive")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "id": self.id,
            "name": self.name,
            "space_id": self.space_id,
            "width": self.width,
            "is_entry_exit": self.is_entry_exit,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CirculationNode:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing circulation node data.

        Returns:
            New CirculationNode instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        return cls(
            id=data["id"],
            name=data["name"],
            space_id=data.get("space_id"),
            width=data.get("width", 1.2),
            is_entry_exit=data.get("is_entry_exit", False),
            metadata=dict(data.get("metadata", {})),
        )