"""Optimization Result for Building Model v2.

Immutable dataclass representing the result of an optimization operation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .optimization_action import OptimizationAction


@dataclass(frozen=True, slots=True)
class OptimizationResult:
    """Immutable dataclass representing the result of an optimization.
    
    Attributes:
        original_model: The original building model before optimization.
        optimized_model: The new building model after optimization.
        applied_actions: List of actions that were successfully applied.
        before_score: Quality score before optimization.
        after_score: Quality score after optimization.
        metadata: Additional metadata about the optimization.
    """
    
    original_model: Any
    optimized_model: Any
    applied_actions: List[OptimizationAction] = field(default_factory=list)
    before_score: float = 0.0
    after_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def improved(self) -> bool:
        """Check if the optimization improved the model."""
        return self.after_score > self.before_score
    
    @property
    def action_count(self) -> int:
        """Get the number of applied actions."""
        return len(self.applied_actions)
    
    @property
    def score_delta(self) -> float:
        """Get the score change."""
        return self.after_score - self.before_score
    
    @property
    def improvement_percentage(self) -> float:
        """Get the percentage improvement."""
        if self.before_score <= 0:
            return 0.0
        return (self.score_delta / self.before_score) * 100.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "applied_actions": [action.to_dict() for action in self.applied_actions],
            "before_score": self.before_score,
            "after_score": self.after_score,
            "score_delta": self.score_delta,
            "improvement_percentage": self.improvement_percentage,
            "action_count": self.action_count,
            "improved": self.improved,
            "metadata": dict(self.metadata),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OptimizationResult:
        """Create from dictionary."""
        actions = [
            OptimizationAction.from_dict(action_data)
            for action_data in data.get("applied_actions", [])
        ]
        return cls(
            original_model=None,
            optimized_model=None,
            applied_actions=actions,
            before_score=data.get("before_score", 0.0),
            after_score=data.get("after_score", 0.0),
            metadata=data.get("metadata", {}),
        )
    
    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, OptimizationResult):
            return NotImplemented
        return (
            self.applied_actions == other.applied_actions
            and self.before_score == other.before_score
            and self.after_score == other.after_score
        )
    
    def __hash__(self) -> int:
        """Return hash."""
        return hash((
            tuple(self.applied_actions),
            self.before_score,
            self.after_score,
        ))