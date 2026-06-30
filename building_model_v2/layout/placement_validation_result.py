"""Placement validation result model.

Immutable dataclass representing the result of placement validation.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Tuple

from .placement_issue import PlacementIssue


@dataclass(frozen=True, slots=True)
class PlacementValidationResult:
    """Immutable result of placement validation.

    Attributes:
        valid: Whether the placement is valid (no errors).
        issues: Tuple of validation issues found.
    """

    valid: bool
    issues: Tuple[PlacementIssue, ...] = ()

    @property
    def error_count(self) -> int:
        """Number of issues with severity 'error'."""
        return sum(1 for issue in self.issues if issue.severity == "error")

    @property
    def warning_count(self) -> int:
        """Number of issues with severity 'warning'."""
        return sum(1 for issue in self.issues if issue.severity == "warning")

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "valid": self.valid,
            "issues": [issue.to_dict() for issue in self.issues],
            "error_count": self.error_count,
            "warning_count": self.warning_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PlacementValidationResult:
        """Deserialize from dictionary."""
        issues = tuple(PlacementIssue.from_dict(issue) for issue in data["issues"])
        valid = data["valid"]
        return cls(valid=valid, issues=issues)