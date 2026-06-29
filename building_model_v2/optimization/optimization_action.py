"""Optimization Action for Building Model v2.

Immutable dataclass representing a single improvement recommendation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass(frozen=True, slots=True)
class OptimizationAction:
    """Immutable dataclass representing a single improvement action.
    
    Attributes:
        id: Unique identifier for this action.
        title: Short title describing the action.
        description: Detailed description of what to do.
        target_entity_id: ID of the entity to modify (e.g., room_id).
        target_entity_type: Type of entity (e.g., 'room', 'door', 'window').
        constraint_codes: List of constraint codes this action addresses.
        current_score: Current quality score for this area (0.0 to 1.0).
        estimated_score_gain: Estimated improvement in score (0.0 to 1.0).
        priority: Priority level (1 = highest priority).
        confidence: Confidence in the recommendation (0.0 to 1.0).
        metadata: Additional metadata for the action.
    """
    
    id: str
    title: str
    description: str
    target_entity_id: str
    target_entity_type: str
    constraint_codes: List[str] = field(default_factory=list)
    current_score: float = 0.0
    estimated_score_gain: float = 0.0
    priority: int = 0
    confidence: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "target_entity_id": self.target_entity_id,
            "target_entity_type": self.target_entity_type,
            "constraint_codes": list(self.constraint_codes),
            "current_score": self.current_score,
            "estimated_score_gain": self.estimated_score_gain,
            "priority": self.priority,
            "confidence": self.confidence,
            "metadata": dict(self.metadata),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> OptimizationAction:
        """Create from dictionary."""
        return cls(
            id=data["id"],
            title=data["title"],
            description=data["description"],
            target_entity_id=data["target_entity_id"],
            target_entity_type=data["target_entity_type"],
            constraint_codes=data.get("constraint_codes", []),
            current_score=data.get("current_score", 0.0),
            estimated_score_gain=data.get("estimated_score_gain", 0.0),
            priority=data.get("priority", 0),
            confidence=data.get("confidence", 0.0),
            metadata=data.get("metadata", {}),
        )
    
    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, OptimizationAction):
            return NotImplemented
        return (
            self.id == other.id
            and self.title == other.title
            and self.description == other.description
            and self.target_entity_id == other.target_entity_id
            and self.target_entity_type == other.target_entity_type
            and self.constraint_codes == other.constraint_codes
            and self.current_score == other.current_score
            and self.estimated_score_gain == other.estimated_score_gain
            and self.priority == other.priority
            and self.confidence == other.confidence
        )
    
    def __hash__(self) -> int:
        """Return hash."""
        return hash((
            self.id,
            self.title,
            self.description,
            self.target_entity_id,
            self.target_entity_type,
            tuple(self.constraint_codes),
            self.current_score,
            self.estimated_score_gain,
            self.priority,
            self.confidence,
        ))
    
    def __lt__(self, other: OptimizationAction) -> bool:
        """Compare for sorting (by priority, then by estimated gain)."""
        if not isinstance(other, OptimizationAction):
            return NotImplemented
        if self.priority != other.priority:
            return self.priority < other.priority
        if self.estimated_score_gain != other.estimated_score_gain:
            return self.estimated_score_gain > other.estimated_score_gain
        return self.id < other.id