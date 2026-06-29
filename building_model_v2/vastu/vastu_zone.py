"""Vastu Zone Enum for Building Model v2."""
from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List

from .vastu_direction import VastuDirection


class VastuZone(Enum):
    """Nine zones of the Vastu Purusha mandala."""

    BRAHMASTHAN = "brahmasthan"
    ISHANYA = "ishanya"
    AGNEYA = "agneya"
    NAIRUTYA = "nairutya"
    VAYAVYA = "vayavya"
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"

    @property
    def display_name(self) -> str:
        names = {
            VastuZone.BRAHMASTHAN: "Brahmasthan (Center)",
            VastuZone.ISHANYA: "Ishanya (North-East)",
            VastuZone.AGNEYA: "Agneya (South-East)",
            VastuZone.NAIRUTYA: "Nairutya (South-West)",
            VastuZone.VAYAVYA: "Vayavya (North-West)",
            VastuZone.NORTH: "North (Kuber)",
            VastuZone.SOUTH: "South (Yamya)",
            VastuZone.EAST: "East (Indra)",
            VastuZone.WEST: "West (Varun)",
        }
        return names[self]

    @property
    def element(self) -> str:
        elements = {
            VastuZone.BRAHMASTHAN: "Space (Akasha)",
            VastuZone.ISHANYA: "Water (Jal)",
            VastuZone.AGNEYA: "Fire (Agni)",
            VastuZone.NAIRUTYA: "Earth (Prithvi)",
            VastuZone.VAYAVYA: "Air (Vayu)",
            VastuZone.NORTH: "Water (Jal)",
            VastuZone.SOUTH: "Earth (Prithvi)",
            VastuZone.EAST: "Fire (Agni)",
            VastuZone.WEST: "Air (Vayu)",
        }
        return elements[self]

    @property
    def primary_direction(self) -> VastuDirection | None:
        direction_map = {
            VastuZone.BRAHMASTHAN: None,
            VastuZone.ISHANYA: VastuDirection.NORTH_EAST,
            VastuZone.AGNEYA: VastuDirection.SOUTH_EAST,
            VastuZone.NAIRUTYA: VastuDirection.SOUTH_WEST,
            VastuZone.VAYAVYA: VastuDirection.NORTH_WEST,
            VastuZone.NORTH: VastuDirection.NORTH,
            VastuZone.SOUTH: VastuDirection.SOUTH,
            VastuZone.EAST: VastuDirection.EAST,
            VastuZone.WEST: VastuDirection.WEST,
        }
        return direction_map[self]

    @property
    def is_corner(self) -> bool:
        return self in {
            VastuZone.ISHANYA, VastuZone.AGNEYA,
            VastuZone.NAIRUTYA, VastuZone.VAYAVYA,
        }

    @property
    def is_cardinal(self) -> bool:
        return self in {
            VastuZone.NORTH, VastuZone.SOUTH,
            VastuZone.EAST, VastuZone.WEST,
        }

    @property
    def is_center(self) -> bool:
        return self == VastuZone.BRAHMASTHAN

    def get_adjacent_zones(self) -> List[VastuZone]:
        adjacency = {
            VastuZone.BRAHMASTHAN: list(VastuZone),
            VastuZone.ISHANYA: [VastuZone.BRAHMASTHAN, VastuZone.NORTH, VastuZone.EAST],
            VastuZone.AGNEYA: [VastuZone.BRAHMASTHAN, VastuZone.EAST, VastuZone.SOUTH],
            VastuZone.NAIRUTYA: [VastuZone.BRAHMASTHAN, VastuZone.SOUTH, VastuZone.WEST],
            VastuZone.VAYAVYA: [VastuZone.BRAHMASTHAN, VastuZone.WEST, VastuZone.NORTH],
            VastuZone.NORTH: [VastuZone.BRAHMASTHAN, VastuZone.ISHANYA, VastuZone.VAYAVYA],
            VastuZone.SOUTH: [VastuZone.BRAHMASTHAN, VastuZone.AGNEYA, VastuZone.NAIRUTYA],
            VastuZone.EAST: [VastuZone.BRAHMASTHAN, VastuZone.ISHANYA, VastuZone.AGNEYA],
            VastuZone.WEST: [VastuZone.BRAHMASTHAN, VastuZone.VAYAVYA, VastuZone.NAIRUTYA],
        }
        # Remove self from Brahmasthan's adjacency list
        adjacency[VastuZone.BRAHMASTHAN] = [z for z in adjacency[VastuZone.BRAHMASTHAN] if z != VastuZone.BRAHMASTHAN]
        return adjacency[self]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "display_name": self.display_name,
            "element": self.element,
            "direction": self.primary_direction.name if self.primary_direction else None,
            "is_corner": self.is_corner,
            "is_cardinal": self.is_cardinal,
            "is_center": self.is_center,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> VastuZone:
        return cls[data["name"]]

    @classmethod
    def get_corners(cls) -> List[VastuZone]:
        return [z for z in cls if z.is_corner]

    @classmethod
    def get_cardinals(cls) -> List[VastuZone]:
        return [z for z in cls if z.is_cardinal]

    def __str__(self) -> str:
        return self.display_name

    def __repr__(self) -> str:
        return f"VastuZone.{self.name}"