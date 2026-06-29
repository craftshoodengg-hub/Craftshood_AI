"""Optimization Objective for Building Model v2.

Immutable dataclass representing a single optimization objective with weight.
Objectives are used by profiles to prioritize different design goals.

Future extension points:
    - Energy optimization
    - Construction cost
    - Carbon footprint
    - User preference learning
    - Regional optimization
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True, slots=True)
class OptimizationObjective:
    """Immutable dataclass representing a single optimization objective.

    Attributes:
        name: Human-readable name of the objective.
        category: Constraint category this objective targets.
        weight: Relative weight for this objective (0.0 to 1.0+).
        enabled: Whether this objective is active.
        description: Detailed description of the objective.
    """

    name: str
    category: str
    weight: float = 1.0
    enabled: bool = True
    description: str = ""

    @property
    def is_active(self) -> bool:
        """Check if this objective is active.

        Returns:
            True if enabled and weight > 0.
        """
        return self.enabled and self.weight > 0

    @property
    def normalized_weight(self) -> float:
        """Get the normalized weight (clamped to non-negative).

        Returns:
            Non-negative weight value.
        """
        return max(0.0, self.weight)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "name": self.name,
            "category": self.category,
            "weight": self.weight,
            "enabled": self.enabled,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OptimizationObjective:
        """Create from dictionary.

        Args:
            data: Dictionary with objective data.

        Returns:
            A new OptimizationObjective.
        """
        return cls(
            name=data.get("name", ""),
            category=data.get("category", ""),
            weight=data.get("weight", 1.0),
            enabled=data.get("enabled", True),
            description=data.get("description", ""),
        )

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, OptimizationObjective):
            return NotImplemented
        return (
            self.name == other.name
            and self.category == other.category
            and self.weight == other.weight
            and self.enabled == other.enabled
        )

    def __hash__(self) -> int:
        """Return hash."""
        return hash((self.name, self.category, self.weight, self.enabled))