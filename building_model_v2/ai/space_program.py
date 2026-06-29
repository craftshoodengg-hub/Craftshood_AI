"""Space Program for Craftshood AI.

Immutable dataclass representing the complete architectural space program.
No geometry. Pure architectural programming specification.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from .room_program import RoomProgram


@dataclass(frozen=True, slots=True)
class SpaceProgram:
    """Complete architectural space program."""

    rooms: Tuple[RoomProgram, ...] = ()
    total_target_area: float = 0.0
    circulation_area: float = 0.0
    usable_area: float = 0.0
    floor_count: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def room_count(self) -> int:
        return len(self.rooms)

    @property
    def bedroom_count(self) -> int:
        return sum(1 for r in self.rooms if r.room_type in ("bedroom", "master_bedroom"))

    @property
    def bathroom_count(self) -> int:
        return sum(1 for r in self.rooms if "bathroom" in r.room_type)

    @property
    def required_rooms(self) -> Tuple[RoomProgram, ...]:
        return tuple(r for r in self.rooms if r.required)

    @property
    def optional_rooms(self) -> Tuple[RoomProgram, ...]:
        return tuple(r for r in self.rooms if not r.required)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "rooms": [r.to_dict() for r in self.rooms],
            "total_target_area": self.total_target_area,
            "circulation_area": self.circulation_area,
            "usable_area": self.usable_area,
            "floor_count": self.floor_count,
            "metadata": dict(self.metadata),
            "room_count": self.room_count,
            "bedroom_count": self.bedroom_count,
            "bathroom_count": self.bathroom_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> SpaceProgram:
        rooms = tuple(RoomProgram.from_dict(r) for r in data.get("rooms", []))
        return cls(
            rooms=rooms,
            total_target_area=data.get("total_target_area", 0.0),
            circulation_area=data.get("circulation_area", 0.0),
            usable_area=data.get("usable_area", 0.0),
            floor_count=data.get("floor_count", 1),
            metadata=dict(data.get("metadata", {})),
        )
