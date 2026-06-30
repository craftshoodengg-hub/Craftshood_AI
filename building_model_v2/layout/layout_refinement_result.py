"""Layout refinement result model.

Immutable dataclass representing the result of layout refinement.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from .placement_result import PlacementResult


@dataclass(frozen=True, slots=True)
class LayoutRefinementResult:
    """Immutable result of layout refinement.

    Attributes:
        original_result: The original placement result before refinement.
        refined_result: The refined placement result.
        improvements: Tuple of description strings for each improvement made.
        moved_rooms: Tuple of room IDs that were moved during refinement.
        score_before: Quality score before refinement (0.0 to 1.0).
        score_after: Quality score after refinement (0.0 to 1.0).
    """

    original_result: PlacementResult
    refined_result: PlacementResult
    improvements: Tuple[str, ...] = ()
    moved_rooms: Tuple[str, ...] = ()
    score_before: float = 0.0
    score_after: float = 0.0

    @property
    def improvement_count(self) -> int:
        """Number of improvements made."""
        return len(self.improvements)

    @property
    def score_delta(self) -> float:
        """Change in score (after - before)."""
        return self.score_after - self.score_before

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "original_result": self.original_result.to_dict(),
            "refined_result": self.refined_result.to_dict(),
            "improvements": list(self.improvements),
            "moved_rooms": list(self.moved_rooms),
            "score_before": self.score_before,
            "score_after": self.score_after,
            "improvement_count": self.improvement_count,
            "score_delta": self.score_delta,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> LayoutRefinementResult:
        """Deserialize from dictionary."""
        original_result = PlacementResult.from_dict(data["original_result"])
        refined_result = PlacementResult.from_dict(data["refined_result"])
        improvements = tuple(data["improvements"])
        moved_rooms = tuple(data["moved_rooms"])
        score_before = data["score_before"]
        score_after = data["score_after"]
        return cls(
            original_result=original_result,
            refined_result=refined_result,
            improvements=improvements,
            moved_rooms=moved_rooms,
            score_before=score_before,
            score_after=score_after,
        )