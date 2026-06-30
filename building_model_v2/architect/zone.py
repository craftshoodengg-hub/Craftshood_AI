"""Zone model for architectural zoning.

Immutable dataclass representing a logical architectural zone
containing grouped rooms.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from ..types import RoomType
from .bubble_node import BubbleNode


@dataclass(frozen=True, slots=True)
class Zone:
    """Immutable architectural zone containing grouped rooms.

    Attributes:
        name: Zone name (e.g., "Living Zone", "Bedroom Zone").
        zone_type: Type of zone (PUBLIC, SEMI_PRIVATE, PRIVATE, SERVICE, VERTICAL, OUTDOOR).
        rooms: Tuple of BubbleNode objects in this zone.
    """

    name: str
    zone_type: str
    rooms: Tuple[BubbleNode, ...] = ()

    @property
    def room_count(self) -> int:
        """Number of rooms in this zone."""
        return len(self.rooms)

    @property
    def total_area(self) -> float:
        """Total target area of all rooms in this zone."""
        return sum(room.target_area for room in self.rooms)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "zone_type": self.zone_type,
            "rooms": [room.to_dict() for room in self.rooms],
            "room_count": self.room_count,
            "total_area": self.total_area,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> Zone:
        """Deserialize from dictionary."""
        rooms = tuple(BubbleNode.from_dict(r) for r in data.get("rooms", []))
        return cls(
            name=data["name"],
            zone_type=data["zone_type"],
            rooms=rooms,
        )