"""Placement issue model.

Immutable dataclass representing a single validation issue in room placement.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True, slots=True)
class PlacementIssue:
    """Immutable representation of a placement validation issue.

    Attributes:
        issue_type: Category of the issue (e.g., 'overlap', 'out_of_bounds').
        severity: Severity level ('error' or 'warning').
        room_id: ID of the room involved, or None if not room-specific.
        message: Human-readable description of the issue.
    """

    issue_type: str
    severity: str
    room_id: str | None
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "issue_type": self.issue_type,
            "severity": self.severity,
            "room_id": self.room_id,
            "message": self.message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PlacementIssue:
        """Deserialize from dictionary."""
        return cls(
            issue_type=data["issue_type"],
            severity=data["severity"],
            room_id=data["room_id"],
            message=data["message"],
        )