"""Bubble node for architectural bubble diagrams.

Represents one logical room inside the Architect Brain's Bubble Diagram.
Contains planning information before geometry exists.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from ..ai.room_program import FloorPreference, PrivacyLevel
from ..types import RoomType


@dataclass(frozen=True, slots=True)
class BubbleNode:
    """Immutable representation of a room in the bubble diagram.

    This is NOT a BuildingModel Room. It contains planning information
    before geometry exists.

    Attributes:
        id: Unique identifier for this bubble node.
        room_type: Type of room (Living, Bedroom, Kitchen, etc.).
        name: Human-readable name for the room.
        target_area: Target area in square feet. Must be positive.
        privacy_level: Privacy classification (Public, Private, etc.).
        preferred_floor: Preferred floor location (Ground, Upper, Any).
        preferred_zone: Optional zone identifier (e.g., "north", "private_wing").
        metadata: Additional key-value metadata.
    """

    id: str
    room_type: RoomType
    name: str
    target_area: float
    privacy_level: PrivacyLevel
    preferred_floor: FloorPreference
    preferred_zone: str | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        if not self.id:
            raise ValueError("id cannot be empty")
        if not self.name:
            raise ValueError("name cannot be empty")
        if self.target_area <= 0:
            raise ValueError("target_area must be positive")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "id": self.id,
            "room_type": self.room_type.value,
            "name": self.name,
            "target_area": self.target_area,
            "privacy_level": self.privacy_level.value,
            "preferred_floor": self.preferred_floor.value,
            "preferred_zone": self.preferred_zone,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> BubbleNode:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing bubble node data.

        Returns:
            New BubbleNode instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        return cls(
            id=data["id"],
            room_type=RoomType(data["room_type"]),
            name=data["name"],
            target_area=data["target_area"],
            privacy_level=PrivacyLevel(data["privacy_level"]),
            preferred_floor=FloorPreference(data["preferred_floor"]),
            preferred_zone=data.get("preferred_zone"),
            metadata=dict(data.get("metadata", {})),
        )