"""Optimization Profile for Building Model v2.

Immutable dataclass representing a collection of weighted objectives.
Profiles determine the priority of different design goals.

Future extension points:
    - Energy optimization
    - Construction cost
    - Carbon footprint
    - User preference learning
    - Regional optimization
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from ..constraints.constraint_category import ConstraintCategory
from .optimization_objective import OptimizationObjective


@dataclass(frozen=True, slots=True)
class OptimizationProfile:
    """Immutable dataclass representing an optimization profile.

    A profile defines which objectives are prioritized and their relative weights.
    Profiles are deterministic and contain no AI logic.

    Attributes:
        name: Human-readable name of the profile.
        description: Detailed description of the profile's focus.
        objectives: Tuple of optimization objectives with weights.
    """

    name: str
    description: str = ""
    objectives: tuple[OptimizationObjective, ...] = ()

    @property
    def active_objectives(self) -> List[OptimizationObjective]:
        """Get only the active objectives."""
        return [obj for obj in self.objectives if obj.is_active]

    @property
    def enabled_objectives(self) -> List[OptimizationObjective]:
        """Get only the enabled objectives."""
        return [obj for obj in self.objectives if obj.enabled]

    @property
    def disabled_objectives(self) -> List[OptimizationObjective]:
        """Get only the disabled objectives."""
        return [obj for obj in self.objectives if not obj.enabled]

    @property
    def total_weight(self) -> float:
        """Get the sum of all active objective weights."""
        return sum(obj.normalized_weight for obj in self.active_objectives)

    def get_objective(self, category: str) -> OptimizationObjective | None:
        """Get an objective by category."""
        for obj in self.objectives:
            if obj.category == category:
                return obj
        return None

    def get_objectives_for_category(self, category: str) -> List[OptimizationObjective]:
        """Get all objectives for a specific category."""
        return [obj for obj in self.objectives if obj.category == category]

    def normalized(self) -> OptimizationProfile:
        """Return a new profile with normalized weights (sum to 1.0)."""
        total = self.total_weight
        if total <= 0:
            return self

        normalized_objectives = tuple(
            OptimizationObjective(
                name=obj.name,
                category=obj.category,
                weight=obj.normalized_weight / total,
                enabled=obj.enabled,
                description=obj.description,
            )
            for obj in self.objectives
        )

        return OptimizationProfile(
            name=self.name,
            description=self.description,
            objectives=normalized_objectives,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "objectives": [obj.to_dict() for obj in self.objectives],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OptimizationProfile:
        """Create from dictionary."""
        objectives = tuple(
            OptimizationObjective.from_dict(obj_data)
            for obj_data in data.get("objectives", [])
        )
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            objectives=objectives,
        )

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, OptimizationProfile):
            return NotImplemented
        return (
            self.name == other.name
            and self.description == other.description
            and self.objectives == other.objectives
        )

    def __hash__(self) -> int:
        """Return hash."""
        return hash((self.name, self.description, self.objectives))

    @classmethod
    def balanced(cls) -> OptimizationProfile:
        """Create a balanced profile with equal weights for all categories."""
        return cls(
            name="Balanced",
            description="Equal priority for all design objectives",
            objectives=(
                OptimizationObjective(name="Functional", category=ConstraintCategory.FUNCTIONAL.value, weight=1.0, description="Design quality and functional requirements"),
                OptimizationObjective(name="Building Code", category=ConstraintCategory.BUILDING_CODE.value, weight=1.0, description="Building code compliance"),
                OptimizationObjective(name="Accessibility", category=ConstraintCategory.ACCESSIBILITY.value, weight=1.0, description="Accessibility compliance"),
                OptimizationObjective(name="Environmental", category=ConstraintCategory.ENVIRONMENTAL.value, weight=1.0, description="Environmental impact and sustainability"),
                OptimizationObjective(name="Structural", category=ConstraintCategory.STRUCTURAL.value, weight=1.0, description="Structural integrity"),
                OptimizationObjective(name="Vastu", category=ConstraintCategory.VASTU.value, weight=1.0, description="Vastu Shastra compliance"),
                OptimizationObjective(name="Custom", category=ConstraintCategory.CUSTOM.value, weight=1.0, description="Custom objectives"),
            ),
        )

    @classmethod
    def building_code_first(cls) -> OptimizationProfile:
        """Create a profile prioritizing building code compliance."""
        return cls(
            name="Building Code First",
            description="Prioritize building code compliance above other objectives",
            objectives=(
                OptimizationObjective(name="Functional", category=ConstraintCategory.FUNCTIONAL.value, weight=0.5, description="Design quality and functional requirements"),
                OptimizationObjective(name="Building Code", category=ConstraintCategory.BUILDING_CODE.value, weight=3.0, description="Building code compliance"),
                OptimizationObjective(name="Accessibility", category=ConstraintCategory.ACCESSIBILITY.value, weight=0.8, description="Accessibility compliance"),
                OptimizationObjective(name="Environmental", category=ConstraintCategory.ENVIRONMENTAL.value, weight=0.5, description="Environmental impact and sustainability"),
                OptimizationObjective(name="Structural", category=ConstraintCategory.STRUCTURAL.value, weight=1.0, description="Structural integrity"),
                OptimizationObjective(name="Vastu", category=ConstraintCategory.VASTU.value, weight=0.3, description="Vastu Shastra compliance"),
                OptimizationObjective(name="Custom", category=ConstraintCategory.CUSTOM.value, weight=0.5, description="Custom objectives"),
            ),
        )

    @classmethod
    def accessibility_first(cls) -> OptimizationProfile:
        """Create a profile prioritizing accessibility compliance."""
        return cls(
            name="Accessibility First",
            description="Prioritize accessibility compliance for universal design",
            objectives=(
                OptimizationObjective(name="Functional", category=ConstraintCategory.FUNCTIONAL.value, weight=0.8, description="Design quality and functional requirements"),
                OptimizationObjective(name="Building Code", category=ConstraintCategory.BUILDING_CODE.value, weight=1.0, description="Building code compliance"),
                OptimizationObjective(name="Accessibility", category=ConstraintCategory.ACCESSIBILITY.value, weight=3.0, description="Accessibility compliance"),
                OptimizationObjective(name="Environmental", category=ConstraintCategory.ENVIRONMENTAL.value, weight=0.5, description="Environmental impact and sustainability"),
                OptimizationObjective(name="Structural", category=ConstraintCategory.STRUCTURAL.value, weight=0.7, description="Structural integrity"),
                OptimizationObjective(name="Vastu", category=ConstraintCategory.VASTU.value, weight=0.3, description="Vastu Shastra compliance"),
                OptimizationObjective(name="Custom", category=ConstraintCategory.CUSTOM.value, weight=0.5, description="Custom objectives"),
            ),
        )

    @classmethod
    def environmental_first(cls) -> OptimizationProfile:
        """Create a profile prioritizing environmental sustainability."""
        return cls(
            name="Environmental First",
            description="Prioritize environmental sustainability and energy efficiency",
            objectives=(
                OptimizationObjective(name="Functional", category=ConstraintCategory.FUNCTIONAL.value, weight=0.5, description="Design quality and functional requirements"),
                OptimizationObjective(name="Building Code", category=ConstraintCategory.BUILDING_CODE.value, weight=0.7, description="Building code compliance"),
                OptimizationObjective(name="Accessibility", category=ConstraintCategory.ACCESSIBILITY.value, weight=0.5, description="Accessibility compliance"),
                OptimizationObjective(name="Environmental", category=ConstraintCategory.ENVIRONMENTAL.value, weight=3.0, description="Environmental impact and sustainability"),
                OptimizationObjective(name="Structural", category=ConstraintCategory.STRUCTURAL.value, weight=0.5, description="Structural integrity"),
                OptimizationObjective(name="Vastu", category=ConstraintCategory.VASTU.value, weight=0.8, description="Vastu Shastra compliance"),
                OptimizationObjective(name="Custom", category=ConstraintCategory.CUSTOM.value, weight=0.5, description="Custom objectives"),
            ),
        )

    @classmethod
    def structural_first(cls) -> OptimizationProfile:
        """Create a profile prioritizing structural integrity."""
        return cls(
            name="Structural First",
            description="Prioritize structural integrity and safety",
            objectives=(
                OptimizationObjective(name="Functional", category=ConstraintCategory.FUNCTIONAL.value, weight=0.5, description="Design quality and functional requirements"),
                OptimizationObjective(name="Building Code", category=ConstraintCategory.BUILDING_CODE.value, weight=1.0, description="Building code compliance"),
                OptimizationObjective(name="Accessibility", category=ConstraintCategory.ACCESSIBILITY.value, weight=0.5, description="Accessibility compliance"),
                OptimizationObjective(name="Environmental", category=ConstraintCategory.ENVIRONMENTAL.value, weight=0.5, description="Environmental impact and sustainability"),
                OptimizationObjective(name="Structural", category=ConstraintCategory.STRUCTURAL.value, weight=3.0, description="Structural integrity"),
                OptimizationObjective(name="Vastu", category=ConstraintCategory.VASTU.value, weight=0.3, description="Vastu Shastra compliance"),
                OptimizationObjective(name="Custom", category=ConstraintCategory.CUSTOM.value, weight=0.5, description="Custom objectives"),
            ),
        )

    @classmethod
    def vastu_first(cls) -> OptimizationProfile:
        """Create a profile prioritizing Vastu Shastra compliance."""
        return cls(
            name="Vastu First",
            description="Prioritize Vastu Shastra compliance and energy flow",
            objectives=(
                OptimizationObjective(name="Functional", category=ConstraintCategory.FUNCTIONAL.value, weight=0.5, description="Design quality and functional requirements"),
                OptimizationObjective(name="Building Code", category=ConstraintCategory.BUILDING_CODE.value, weight=0.5, description="Building code compliance"),
                OptimizationObjective(name="Accessibility", category=ConstraintCategory.ACCESSIBILITY.value, weight=0.3, description="Accessibility compliance"),
                OptimizationObjective(name="Environmental", category=ConstraintCategory.ENVIRONMENTAL.value, weight=1.0, description="Environmental impact and sustainability"),
                OptimizationObjective(name="Structural", category=ConstraintCategory.STRUCTURAL.value, weight=0.3, description="Structural integrity"),
                OptimizationObjective(name="Vastu", category=ConstraintCategory.VASTU.value, weight=3.0, description="Vastu Shastra compliance"),
                OptimizationObjective(name="Custom", category=ConstraintCategory.CUSTOM.value, weight=0.3, description="Custom objectives"),
            ),
        )

    @classmethod
    def high_performance_home(cls) -> OptimizationProfile:
        """Create a profile for high-performance home design."""
        return cls(
            name="High Performance Home",
            description="Optimize for energy efficiency, comfort, and sustainability",
            objectives=(
                OptimizationObjective(name="Functional", category=ConstraintCategory.FUNCTIONAL.value, weight=1.0, description="Design quality and functional requirements"),
                OptimizationObjective(name="Building Code", category=ConstraintCategory.BUILDING_CODE.value, weight=1.5, description="Building code compliance"),
                OptimizationObjective(name="Accessibility", category=ConstraintCategory.ACCESSIBILITY.value, weight=0.8, description="Accessibility compliance"),
                OptimizationObjective(name="Environmental", category=ConstraintCategory.ENVIRONMENTAL.value, weight=2.5, description="Environmental impact and sustainability"),
                OptimizationObjective(name="Structural", category=ConstraintCategory.STRUCTURAL.value, weight=1.0, description="Structural integrity"),
                OptimizationObjective(name="Vastu", category=ConstraintCategory.VASTU.value, weight=0.5, description="Vastu Shastra compliance"),
                OptimizationObjective(name="Custom", category=ConstraintCategory.CUSTOM.value, weight=0.5, description="Custom objectives"),
            ),
        )

    @classmethod
    def luxury_villa(cls) -> OptimizationProfile:
        """Create a profile for luxury villa design."""
        return cls(
            name="Luxury Villa",
            description="Optimize for luxury, aesthetics, and premium living experience",
            objectives=(
                OptimizationObjective(name="Functional", category=ConstraintCategory.FUNCTIONAL.value, weight=2.0, description="Design quality and functional requirements"),
                OptimizationObjective(name="Building Code", category=ConstraintCategory.BUILDING_CODE.value, weight=1.0, description="Building code compliance"),
                OptimizationObjective(name="Accessibility", category=ConstraintCategory.ACCESSIBILITY.value, weight=1.0, description="Accessibility compliance"),
                OptimizationObjective(name="Environmental", category=ConstraintCategory.ENVIRONMENTAL.value, weight=1.5, description="Environmental impact and sustainability"),
                OptimizationObjective(name="Structural", category=ConstraintCategory.STRUCTURAL.value, weight=1.0, description="Structural integrity"),
                OptimizationObjective(name="Vastu", category=ConstraintCategory.VASTU.value, weight=1.5, description="Vastu Shastra compliance"),
                OptimizationObjective(name="Custom", category=ConstraintCategory.CUSTOM.value, weight=1.0, description="Custom objectives"),
            ),
        )

    @classmethod
    def compact_house(cls) -> OptimizationProfile:
        """Create a profile for compact house design."""
        return cls(
            name="Compact House",
            description="Optimize for space efficiency, affordability, and functionality",
            objectives=(
                OptimizationObjective(name="Functional", category=ConstraintCategory.FUNCTIONAL.value, weight=2.0, description="Design quality and functional requirements"),
                OptimizationObjective(name="Building Code", category=ConstraintCategory.BUILDING_CODE.value, weight=1.5, description="Building code compliance"),
                OptimizationObjective(name="Accessibility", category=ConstraintCategory.ACCESSIBILITY.value, weight=0.5, description="Accessibility compliance"),
                OptimizationObjective(name="Environmental", category=ConstraintCategory.ENVIRONMENTAL.value, weight=1.0, description="Environmental impact and sustainability"),
                OptimizationObjective(name="Structural", category=ConstraintCategory.STRUCTURAL.value, weight=1.5, description="Structural integrity"),
                OptimizationObjective(name="Vastu", category=ConstraintCategory.VASTU.value, weight=0.3, description="Vastu Shastra compliance"),
                OptimizationObjective(name="Custom", category=ConstraintCategory.CUSTOM.value, weight=0.5, description="Custom objectives"),
            ),
        )

    @classmethod
    def custom(
        cls,
        name: str,
        description: str = "",
        objectives: List[OptimizationObjective] | None = None,
    ) -> OptimizationProfile:
        """Create a custom profile."""
        if objectives is None:
            balanced = cls.balanced()
            objectives = list(balanced.objectives)

        return cls(
            name=name,
            description=description,
            objectives=tuple(objectives),
        )
