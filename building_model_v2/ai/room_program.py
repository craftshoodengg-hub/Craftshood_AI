"""Room Program for Craftshood AI.

Immutable dataclass representing a single room in the space program.
No geometry. Pure architectural programming.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, FrozenSet, Optional


class PrivacyLevel(Enum):
    """Room privacy classification."""
    PUBLIC = "public"
    SEMI_PRIVATE = "semi_private"
    PRIVATE = "private"
    SERVICE = "service"


class FloorPreference(Enum):
    """Preferred floor location."""
    GROUND = "ground"
    UPPER = "upper"
    ANY = "any"


@dataclass(frozen=True, slots=True)
class RoomProgram:
    """Immutable specification for a single room in the building program."""

    id: str
    room_type: str
    name: str = ""
    target_area: float | None = None
    minimum_area: float | None = None
    maximum_area: float | None = None
    privacy_level: PrivacyLevel = PrivacyLevel.PRIVATE
    required: bool = True
    floor_preference: FloorPreference = FloorPreference.ANY
    adjacency_preferences: FrozenSet[str] = field(default_factory=frozenset)
    adjacency_requirements: FrozenSet[str] = field(default_factory=frozenset)
    circulation_importance: float = 0.5
    natural_light_required: bool = False
    ventilation_required: bool = False
    vastu_preference: str | None = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "room_type": self.room_type,
            "name": self.name,
            "target_area": self.target_area,
            "minimum_area": self.minimum_area,
            "maximum_area": self.maximum_area,
            "privacy_level": self.privacy_level.value,
            "required": self.required,
            "floor_preference": self.floor_preference.value,
            "adjacency_preferences": sorted(self.adjacency_preferences),
            "adjacency_requirements": sorted(self.adjacency_requirements),
            "circulation_importance": self.circulation_importance,
            "natural_light_required": self.natural_light_required,
            "ventilation_required": self.ventilation_required,
            "vastu_preference": self.vastu_preference,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> RoomProgram:
        return cls(
            id=data["id"],
            room_type=data["room_type"],
            name=data.get("name", ""),
            target_area=data.get("target_area"),
            minimum_area=data.get("minimum_area"),
            maximum_area=data.get("maximum_area"),
            privacy_level=PrivacyLevel(data.get("privacy_level", "private")),
            required=data.get("required", True),
            floor_preference=FloorPreference(data.get("floor_preference", "any")),
            adjacency_preferences=frozenset(data.get("adjacency_preferences", [])),
            adjacency_requirements=frozenset(data.get("adjacency_requirements", [])),
            circulation_importance=data.get("circulation_importance", 0.5),
            natural_light_required=data.get("natural_light_required", False),
            ventilation_required=data.get("ventilation_required", False),
            vastu_preference=data.get("vastu_preference"),
            metadata=dict(data.get("metadata", {})),
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RoomProgram):
            return NotImplemented
        return self.id == other.id and self.room_type == other.room_type

    def __hash__(self) -> int:
        return hash((self.id, self.room_type))
