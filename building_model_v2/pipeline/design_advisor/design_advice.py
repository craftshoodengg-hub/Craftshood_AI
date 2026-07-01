"""Design advice domain model."""
from __future__ import annotations

from dataclasses import dataclass

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
