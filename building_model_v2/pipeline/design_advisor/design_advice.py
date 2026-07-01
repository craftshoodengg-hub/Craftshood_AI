"""Design advice domain model."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

_ALLOWED_SEVERITIES = {"info", "recommendation", "warning"}


@dataclass(frozen=True, slots=True)
class DesignAdvice:
    """A single advisory observation for a design."""

    category: str
    title: str
    description: str
    severity: str
    recommendation: str

    def __post_init__(self) -> None:
        if self.severity not in _ALLOWED_SEVERITIES:
            raise ValueError(
                f"severity must be one of {sorted(_ALLOWED_SEVERITIES)!r}, got {self.severity!r}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "category": self.category,
            "title": self.title,
            "description": self.description,
            "severity": self.severity,
            "recommendation": self.recommendation,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DesignAdvice":
        return cls(
            category=str(data["category"]),
            title=str(data["title"]),
            description=str(data["description"]),
            severity=str(data["severity"]),
            recommendation=str(data["recommendation"]),
        )
