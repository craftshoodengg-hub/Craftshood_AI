"""Circulation score for architectural circulation evaluation.

Immutable dataclass containing quality scores for a circulation graph.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, slots=True)
class CirculationScore:
    """Immutable quality score for a circulation graph.

    Attributes:
        overall_score: Overall circulation quality from 0 to 100.
        connectivity_score: How well rooms are connected (0 to 100).
        accessibility_score: How accessible the circulation is (0 to 100).
        efficiency_score: How efficient paths are (0 to 100).
        penalties: List of penalty descriptions.
        recommendations: List of improvement recommendations.
    """

    overall_score: float
    connectivity_score: float
    accessibility_score: float
    efficiency_score: float
    penalties: tuple[str, ...] = ()
    recommendations: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        if not 0.0 <= self.overall_score <= 100.0:
            raise ValueError("overall_score must be between 0 and 100")
        if not 0.0 <= self.connectivity_score <= 100.0:
            raise ValueError("connectivity_score must be between 0 and 100")
        if not 0.0 <= self.accessibility_score <= 100.0:
            raise ValueError("accessibility_score must be between 0 and 100")
        if not 0.0 <= self.efficiency_score <= 100.0:
            raise ValueError("efficiency_score must be between 0 and 100")

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "overall_score": self.overall_score,
            "connectivity_score": self.connectivity_score,
            "accessibility_score": self.accessibility_score,
            "efficiency_score": self.efficiency_score,
            "penalties": list(self.penalties),
            "recommendations": list(self.recommendations),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CirculationScore:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing score data.

        Returns:
            New CirculationScore instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        return cls(
            overall_score=data["overall_score"],
            connectivity_score=data["connectivity_score"],
            accessibility_score=data["accessibility_score"],
            efficiency_score=data["efficiency_score"],
            penalties=tuple(data.get("penalties", [])),
            recommendations=tuple(data.get("recommendations", [])),
        )