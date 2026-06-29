"""Objective Score for Building Model v2.

Immutable dataclass representing the result of multi-objective scoring.
Contains overall score, category breakdown, and weighted totals.

Future extension points:
    - Energy optimization
    - Construction cost
    - Carbon footprint
    - User preference learning
    - Regional optimization
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass(frozen=True, slots=True)
class ObjectiveScore:
    """Immutable dataclass for multi-objective scoring results.

    Attributes:
        overall: Overall weighted score (0-100).
        category_scores: Scores broken down by category.
        weighted_score: Final weighted composite score.
        objective_breakdown: Score contribution per objective.
    """

    overall: float = 0.0
    category_scores: Dict[str, float] = field(default_factory=dict)
    weighted_score: float = 0.0
    objective_breakdown: Dict[str, float] = field(default_factory=dict)

    @property
    def percentage(self) -> float:
        """Get the score as a percentage.

        Returns:
            Score clamped between 0.0 and 100.0.
        """
        return max(0.0, min(100.0, self.overall))

    @property
    def best_category(self) -> str | None:
        """Get the category with the highest score.

        Returns:
            Category name with highest score, or None if no categories.
        """
        if not self.category_scores:
            return None
        return max(self.category_scores, key=self.category_scores.get)

    @property
    def worst_category(self) -> str | None:
        """Get the category with the lowest score.

        Returns:
            Category name with lowest score, or None if no categories.
        """
        if not self.category_scores:
            return None
        return min(self.category_scores, key=self.category_scores.get)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "overall": self.overall,
            "category_scores": dict(self.category_scores),
            "weighted_score": self.weighted_score,
            "objective_breakdown": dict(self.objective_breakdown),
            "percentage": self.percentage,
            "best_category": self.best_category,
            "worst_category": self.worst_category,
        }

    def get_category_score(self, category: str) -> float:
        """Get the score for a specific category.

        Args:
            category: The category name.

        Returns:
            The category score, or 0.0 if not found.
        """
        return self.category_scores.get(category, 0.0)

    def get_objective_weight(self, objective_name: str) -> float:
        """Get the contribution weight for a specific objective.

        Args:
            objective_name: The objective name.

        Returns:
            The objective weight, or 0.0 if not found.
        """
        return self.objective_breakdown.get(objective_name, 0.0)

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, ObjectiveScore):
            return NotImplemented
        return (
            self.overall == other.overall
            and self.weighted_score == other.weighted_score
            and self.category_scores == other.category_scores
        )

    def __hash__(self) -> int:
        """Return hash."""
        return hash((self.overall, self.weighted_score))