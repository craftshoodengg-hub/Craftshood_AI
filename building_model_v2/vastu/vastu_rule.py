"""Vastu Rule for Building Model v2.

Immutable dataclass representing a single Vastu Shastra rule.
Rules define preferred, allowed, and avoided zones for specific room functions.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from ..constraints.constraint_severity import ConstraintSeverity
from .vastu_zone import VastuZone


@dataclass(frozen=True, slots=True)
class VastuRule:
    """Immutable dataclass representing a single Vastu rule.

    Attributes:
        id: Unique identifier for the rule.
        name: Human-readable name of the rule.
        description: Detailed description of the rule.
        preferred_zone: The most auspicious zone for this function.
        allowed_zones: List of acceptable zones (excluding preferred).
        severity: Severity level when this rule is violated.
        enabled: Whether this rule is active.
        metadata: Additional metadata about the rule.
    """

    id: str
    name: str
    description: str = ""
    preferred_zone: VastuZone | None = None
    allowed_zones: tuple[VastuZone, ...] = ()
    severity: ConstraintSeverity = ConstraintSeverity.RECOMMENDATION
    enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

    def is_zone_allowed(self, zone: VastuZone) -> bool:
        """Check if a zone is allowed (preferred or in allowed list).

        Args:
            zone: The zone to check.

        Returns:
            True if the zone is preferred or in the allowed list.
        """
        if self.preferred_zone and zone == self.preferred_zone:
            return True
        return zone in self.allowed_zones

    def is_zone_preferred(self, zone: VastuZone) -> bool:
        """Check if a zone is the preferred zone.

        Args:
            zone: The zone to check.

        Returns:
            True if the zone is the preferred zone.
        """
        return self.preferred_zone is not None and zone == self.preferred_zone

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "preferred_zone": self.preferred_zone.name if self.preferred_zone else None,
            "allowed_zones": [z.name for z in self.allowed_zones],
            "severity": str(self.severity),
            "enabled": self.enabled,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> VastuRule:
        """Create from dictionary."""
        preferred_zone = None
        if data.get("preferred_zone"):
            preferred_zone = VastuZone[data["preferred_zone"]]

        allowed_zones = tuple(
            VastuZone[z] for z in data.get("allowed_zones", [])
        )

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description", ""),
            preferred_zone=preferred_zone,
            allowed_zones=allowed_zones,
            severity=ConstraintSeverity(data.get("severity", "recommendation")),
            enabled=data.get("enabled", True),
            metadata=data.get("metadata", {}),
        )

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, VastuRule):
            return NotImplemented
        return (
            self.id == other.id
            and self.name == other.name
            and self.preferred_zone == other.preferred_zone
            and self.allowed_zones == other.allowed_zones
        )

    def __hash__(self) -> int:
        """Return hash."""
        return hash((self.id, self.name, self.preferred_zone, self.allowed_zones))