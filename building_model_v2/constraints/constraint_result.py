"""Constraint Result for Building Model v2.

Defines the structure for collecting and managing constraint evaluation results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence

from .constraint_issue import ConstraintIssue
from .constraint_severity import ConstraintSeverity


@dataclass(slots=True)
class ConstraintResult:
    """Collects constraint evaluation issues.
    
    Provides methods for adding issues and computing aggregate statistics.
    
    Attributes:
        issues: List of constraint issues found during evaluation.
    """
    
    issues: List[ConstraintIssue] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Ensure lists are initialized."""
        if self.issues is None:
            object.__setattr__(self, "issues", [])
    
    @property
    def is_optimal(self) -> bool:
        """Check if the result has no issues.
        
        Returns:
            True if there are no issues.
        """
        return len(self.issues) == 0
    
    @property
    def issue_count(self) -> int:
        """Get the total number of issues.
        
        Returns:
            The count of all issues.
        """
        return len(self.issues)
    
    @property
    def recommendation_count(self) -> int:
        """Get the number of recommendation issues.
        
        Returns:
            The count of RECOMMENDATION severity issues.
        """
        return sum(
            1 for issue in self.issues
            if issue.severity == ConstraintSeverity.RECOMMENDATION
        )
    
    @property
    def warning_count(self) -> int:
        """Get the number of warning issues.
        
        Returns:
            The count of WARNING severity issues.
        """
        return sum(
            1 for issue in self.issues
            if issue.severity == ConstraintSeverity.WARNING
        )
    
    @property
    def suggestion_count(self) -> int:
        """Get the number of suggestion issues.
        
        Returns:
            The count of SUGGESTION severity issues.
        """
        return sum(
            1 for issue in self.issues
            if issue.severity == ConstraintSeverity.SUGGESTION
        )
    
    @property
    def info_count(self) -> int:
        """Get the number of info issues.
        
        Returns:
            The count of INFO severity issues.
        """
        return sum(
            1 for issue in self.issues
            if issue.severity == ConstraintSeverity.INFO
        )
    
    @property
    def total_score(self) -> float:
        """Get the total quality score impact.
        
        Returns:
            Sum of all issue scores (0.0 to 1.0 per issue).
        """
        return sum(issue.score for issue in self.issues)
    
    def add_issue(self, issue: ConstraintIssue) -> None:
        """Add a constraint issue.
        
        Args:
            issue: The issue to add.
        """
        self.issues.append(issue)
    
    def merge(self, other: ConstraintResult) -> ConstraintResult:
        """Merge another ConstraintResult into this one.
        
        Args:
            other: The other result to merge.
            
        Returns:
            A new ConstraintResult containing all issues from both.
        """
        return ConstraintResult(
            issues=self.issues + other.issues,
        )
    
    def get_issues_by_severity(self, severity: ConstraintSeverity) -> List[ConstraintIssue]:
        """Get all issues with a specific severity.
        
        Args:
            severity: The severity level to filter by.
            
        Returns:
            List of issues with the specified severity.
        """
        return [issue for issue in self.issues if issue.severity == severity]
    
    def get_issues_by_code(self, code: str) -> List[ConstraintIssue]:
        """Get all issues with a specific code.
        
        Args:
            code: The constraint code to filter by.
            
        Returns:
            List of issues with the specified code.
        """
        return [issue for issue in self.issues if issue.code == code]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary.
        
        Returns:
            A dictionary representation of the result.
        """
        return {
            "is_optimal": self.is_optimal,
            "issue_count": self.issue_count,
            "recommendation_count": self.recommendation_count,
            "warning_count": self.warning_count,
            "suggestion_count": self.suggestion_count,
            "info_count": self.info_count,
            "total_score": self.total_score,
            "issues": [issue.to_dict() for issue in self.issues],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ConstraintResult:
        """Create a ConstraintResult from a dictionary.
        
        Args:
            data: Dictionary containing result data.
            
        Returns:
            A new ConstraintResult instance.
        """
        return cls(
            issues=[
                ConstraintIssue.from_dict(issue)
                for issue in data.get("issues", [])
            ],
        )
    
    @classmethod
    def create(cls) -> ConstraintResult:
        """Create an empty optimal result.
        
        Returns:
            A new empty ConstraintResult instance.
        """
        return cls()
    
    @classmethod
    def from_issues(cls, issues: Sequence[ConstraintIssue]) -> ConstraintResult:
        """Create a result containing multiple issues.
        
        Args:
            issues: The issues to include.
            
        Returns:
            A new ConstraintResult with the issues.
        """
        return cls(issues=list(issues))
    
    def __str__(self) -> str:
        """Return a string representation of the result.
        
        Returns:
            A formatted string with counts.
        """
        return (
            f"ConstraintResult("
            f"optimal={self.is_optimal}, "
            f"issues={self.issue_count}, "
            f"recommendations={self.recommendation_count}, "
            f"warnings={self.warning_count})"
        )
    
    def __repr__(self) -> str:
        """Return a detailed representation of the result.
        
        Returns:
            A string representation useful for debugging.
        """
        return (
            f"ConstraintResult("
            f"issues={len(self.issues)}, "
            f"recommendations={self.recommendation_count}, "
            f"warnings={self.warning_count}, "
            f"suggestions={self.suggestion_count})"
        )
    
    def __eq__(self, other: object) -> bool:
        """Check equality between ConstraintResult instances.
        
        Args:
            other: Another object to compare with.
            
        Returns:
            True if all fields are equal.
        """
        if not isinstance(other, ConstraintResult):
            return NotImplemented
        return self.issues == other.issues
    
    def __bool__(self) -> bool:
        """Return True if the result is optimal.
        
        Returns:
            True if there are no issues.
        """
        return self.is_optimal