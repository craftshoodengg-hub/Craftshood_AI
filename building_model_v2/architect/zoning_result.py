"""Zoning result model.

Immutable dataclass containing the result of zoning analysis.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from .zone import Zone


@dataclass(frozen=True, slots=True)
class ZoningResult:
    """Immutable result of zoning analysis.

    Attributes:
        zones: Tuple of Zone objects.
        unassigned_rooms: Tuple of room IDs that were not assigned to any zone.
        metadata: Additional metadata about the zoning analysis.
    """

    zones: Tuple[Zone, ...] = ()
    unassigned_rooms: Tuple[str, ...] = ()
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_zone_count(self) -> int:
        """Total number of zones."""
        return len(self.zones)

    @property
    def assigned_room_count(self) -> int:
        """Total number of rooms assigned to zones."""
        return sum(zone.room_count for zone in self.zones)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "zones": [zone.to_dict() for zone in self.zones],
            "unassigned_rooms": list(self.unassigned_rooms),
            "metadata": dict(self.metadata),
            "total_zone_count": self.total_zone_count,
            "assigned_room_count": self.assigned_room_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ZoningResult:
        """Deserialize from dictionary."""
        zones = tuple(Zone.from_dict(z) for z in data.get("zones", []))
        unassigned_rooms = tuple(data.get("unassigned_rooms", []))
        metadata = dict(data.get("metadata", {}))
        return cls(
            zones=zones,
            unassigned_rooms=unassigned_rooms,
            metadata=metadata,
        )