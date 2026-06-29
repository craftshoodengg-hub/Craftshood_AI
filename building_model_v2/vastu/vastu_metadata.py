"""Vastu Metadata for Building Model v2.

Immutable dataclass storing Vastu-specific orientation and direction data
for a building or plot.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .vastu_direction import VastuDirection


@dataclass(frozen=True, slots=True)
class VastuMetadata:
    """Immutable dataclass for Vastu-specific building metadata.

    Attributes:
        entrance_direction: Direction of the main entrance.
        kitchen_direction: Direction of the kitchen.
        master_bedroom_direction: Direction of the master bedroom.
        pooja_direction: Direction of the pooja/prayer room.
        staircase_direction: Direction of the staircase.
        toilet_direction: Direction of the main toilet.
        water_tank_direction: Direction of the underground water tank.
        septic_direction: Direction of the septic tank.
        plot_facing: Direction the plot faces.
        north_rotation: Rotation angle in degrees from true north.
        custom_directions: Additional custom direction mappings.
    """

    entrance_direction: VastuDirection | None = None
    kitchen_direction: VastuDirection | None = None
    master_bedroom_direction: VastuDirection | None = None
    pooja_direction: VastuDirection | None = None
    staircase_direction: VastuDirection | None = None
    toilet_direction: VastuDirection | None = None
    water_tank_direction: VastuDirection | None = None
    septic_direction: VastuDirection | None = None
    plot_facing: VastuDirection | None = None
    north_rotation: float = 0.0
    custom_directions: Dict[str, VastuDirection] = field(default_factory=dict)

    def get_direction(self, key: str) -> VastuDirection | None:
        """Get a direction by key, checking both standard and custom directions.

        Args:
            key: The direction key (e.g., 'entrance', 'kitchen', or custom key).

        Returns:
            The VastuDirection if found, None otherwise.
        """
        standard_map = {
            "entrance": self.entrance_direction,
            "kitchen": self.kitchen_direction,
            "master_bedroom": self.master_bedroom_direction,
            "pooja": self.pooja_direction,
            "staircase": self.staircase_direction,
            "toilet": self.toilet_direction,
            "water_tank": self.water_tank_direction,
            "septic": self.septic_direction,
            "plot_facing": self.plot_facing,
        }
        if key in standard_map:
            return standard_map[key]
        return self.custom_directions.get(key)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entrance_direction": self.entrance_direction.name if self.entrance_direction else None,
            "kitchen_direction": self.kitchen_direction.name if self.kitchen_direction else None,
            "master_bedroom_direction": self.master_bedroom_direction.name if self.master_bedroom_direction else None,
            "pooja_direction": self.pooja_direction.name if self.pooja_direction else None,
            "staircase_direction": self.staircase_direction.name if self.staircase_direction else None,
            "toilet_direction": self.toilet_direction.name if self.toilet_direction else None,
            "water_tank_direction": self.water_tank_direction.name if self.water_tank_direction else None,
            "septic_direction": self.septic_direction.name if self.septic_direction else None,
            "plot_facing": self.plot_facing.name if self.plot_facing else None,
            "north_rotation": self.north_rotation,
            "custom_directions": {k: v.name for k, v in self.custom_directions.items()},
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> VastuMetadata:
        """Create from dictionary."""
        def parse_direction(key: str) -> VastuDirection | None:
            val = data.get(key)
            return VastuDirection[val] if val else None

        custom = {
            k: VastuDirection[v]
            for k, v in data.get("custom_directions", {}).items()
        }

        return cls(
            entrance_direction=parse_direction("entrance_direction"),
            kitchen_direction=parse_direction("kitchen_direction"),
            master_bedroom_direction=parse_direction("master_bedroom_direction"),
            pooja_direction=parse_direction("pooja_direction"),
            staircase_direction=parse_direction("staircase_direction"),
            toilet_direction=parse_direction("toilet_direction"),
            water_tank_direction=parse_direction("water_tank_direction"),
            septic_direction=parse_direction("septic_direction"),
            plot_facing=parse_direction("plot_facing"),
            north_rotation=data.get("north_rotation", 0.0),
            custom_directions=custom,
        )

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, VastuMetadata):
            return NotImplemented
        return (
            self.entrance_direction == other.entrance_direction
            and self.kitchen_direction == other.kitchen_direction
            and self.master_bedroom_direction == other.master_bedroom_direction
            and self.north_rotation == other.north_rotation
        )

    def __hash__(self) -> int:
        """Return hash."""
        return hash((
            self.entrance_direction,
            self.kitchen_direction,
            self.master_bedroom_direction,
            self.north_rotation,
        ))