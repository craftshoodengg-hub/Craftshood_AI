"""Improvement Plan for Building Model v2.

Immutable dataclass containing ranked optimization recommendations.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .optimization_action import OptimizationAction


@dataclass(frozen=True, slots=True)
class ImprovementPlan:
    """Immutable dataclass containing ranked optimization recommendations.
    
    Attributes:
        actions: List of optimization actions, sorted by priority.
        current_score: Current overall quality score.
        estimated_final_score: Estimated score after applying all actions.
    """
    
    actions: List[OptimizationAction] = field(default_factory=list)
    current_score: float = 0.0
    estimated_final_score: float = 0.0
    
    @property
    def action_count(self) -> int:
        """Get the number of actions in the plan."""
        return len(self.actions)
    
    @property
    def highest_priority(self) -> OptimizationAction | None:
        """Get the highest priority action.
        
        Returns:
            The action with the lowest priority number, or None if empty.
        """
        if not self.actions:
            return None
        return min(self.actions)
    
    @property
    def total_estimated_gain(self) -> float:
        """Get the total estimated score gain.
        
        Returns:
            Sum of all estimated score gains.
        """
        return sum(action.estimated_score_gain for action in self.actions)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.
        
        Returns:
            Dictionary representation.
        """
        return {
            "actions": [action.to_dict() for action in self.actions],
            "current_score": self.current_score,
            "estimated_final_score": self.estimated_final_score,
            "action_count": self.action_count,
            "total_estimated_gain": self.total_estimated_gain,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ImprovementPlan:
        """Create from dictionary.
        
        Args:
            data: Dictionary containing plan data.
            
        Returns:
            A new ImprovementPlan.
        """
        actions = [
            OptimizationAction.from_dict(action_data)
            for action_data in data.get("actions", [])
        ]
        return cls(
            actions=actions,
            current_score=data.get("current_score", 0.0),
            estimated_final_score=data.get("estimated_final_score", 0.0),
        )
    
    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, ImprovementPlan):
            return NotImplemented
        return (
            self.actions == other.actions
            and self.current_score == other.current_score
            and self.estimated_final_score == other.estimated_final_score
        )
    
    def __hash__(self) -> int:
        """Return hash."""
        return hash((
            tuple(self.actions),
            self.current_score,
            self.estimated_final_score,
        ))