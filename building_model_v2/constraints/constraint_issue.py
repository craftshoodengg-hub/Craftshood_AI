"""Constraint Issue for Building Model v2.

Defines the structure for constraint evaluation issues.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .constraint_severity import ConstraintSeverity


@dataclass(slots=True, frozen=True)
class ConstraintIssue:
    """Represents a single constraint evaluation issue.
    
    Attributes:
        code: Unique identifier for the constraint rule.
        message: Human-readable description of the issue.
        severity: Severity level of the issue.
        entity_id: Optional ID of the entity that triggered the issue.
        entity_type: Optional type of the entity.
        location: Optional location information (e.g., floor, room).
        score: Optional quality score impact (0.0 to 1.0).
        metadata: Additional metadata about the issue.
    """
    
    code: str
    message: str
    severity: ConstraintSeverity
    entity_id: str | None = None
    entity_type: str | None = None
    location: str | None = None
    score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the issue to a dictionary.
        
        Returns:
            A dictionary representation of the issue.
        """
        return {
            "code": self.code,
            "message": self.message,
            "severity": str(self.severity),
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "location": self.location,
            "score": self.score,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConstraintIssue:
        """Create a ConstraintIssue from a dictionary.
        
        Args:
            data: Dictionary containing issue data.
            
        Returns:
            A new ConstraintIssue instance.
        """
        return cls(
            code=data["code"],
            message=data["message"],
            severity=ConstraintSeverity(data["severity"]),
            entity_id=data.get("entity_id"),
            entity_type=data.get("entity_type"),
            location=data.get("location"),
            score=data.get("score", 0.0),
            metadata=data.get("metadata", {}),
        )
    
    def __eq__(self, other: object) -> bool:
        """Check equality between ConstraintIssue instances.
        
        Args:
            other: Another object to compare with.
            
        Returns:
            True if all fields are equal.
        """
        if not isinstance(other, ConstraintIssue):
            return NotImplemented
        return (
            self.code == other.code
            and self.message == other.message
            and self.severity == other.severity
            and self.entity_id == other.entity_id
            and self.entity_type == other.entity_type
            and self.location == other.location
            and self.score == other.score
        )
    
    def __hash__(self) -> int:
        """Return hash for the issue.
        
        Returns:
            Hash based on immutable fields.
        """
        return hash((
            self.code,
            self.message,
            self.severity,
            self.entity_id,
            self.entity_type,
            self.location,
            self.score,
        ))