"""Circulation optimization result model.

Immutable dataclass containing the result of circulation optimization.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .circulation_result import CirculationResult
from .circulation_score import CirculationScore


@dataclass(frozen=True, slots=True)
class CirculationOptimizationResult:
    """Immutable result of circulation optimization.

    Attributes:
        original_score: The circulation score before optimization.
        optimized_score: The circulation score after optimization.
        improvements: List of improvement descriptions.
        modified_connections: List of connection modifications made.
        iteration_count: Number of optimization iterations performed.
        circulation_result: The optimized circulation result.
    """

    original_score: CirculationScore
    optimized_score: CirculationScore
    improvements: tuple[str, ...] = ()
    modified_connections: tuple[str, ...] = ()
    iteration_count: int = 0
    circulation_result: CirculationResult | None = None

    def __post_init__(self) -> None:
        """Validate field values after initialization."""
        if self.iteration_count < 0:
            raise ValueError("iteration_count must be non-negative")
        if self.optimized_score.overall_score < self.original_score.overall_score:
            raise ValueError(
                "optimized_score must be >= original_score"
            )

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "original_score": self.original_score.to_dict(),
            "optimized_score": self.optimized_score.to_dict(),
            "improvements": list(self.improvements),
            "modified_connections": list(self.modified_connections),
            "iteration_count": self.iteration_count,
            "circulation_result": (
                self.circulation_result.to_dict()
                if self.circulation_result is not None
                else None
            ),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> CirculationOptimizationResult:
        """Deserialize from dictionary.

        Args:
            data: Dictionary containing optimization result data.

        Returns:
            New CirculationOptimizationResult instance.

        Raises:
            KeyError: If required fields are missing.
            ValueError: If field values are invalid.
        """
        original_score = CirculationScore.from_dict(data["original_score"])
        optimized_score = CirculationScore.from_dict(data["optimized_score"])
        circulation_result = (
            CirculationResult.from_dict(data["circulation_result"])
            if data.get("circulation_result") is not None
            else None
        )
        return cls(
            original_score=original_score,
            optimized_score=optimized_score,
            improvements=tuple(data.get("improvements", [])),
            modified_connections=tuple(data.get("modified_connections", [])),
            iteration_count=data.get("iteration_count", 0),
            circulation_result=circulation_result,
        )