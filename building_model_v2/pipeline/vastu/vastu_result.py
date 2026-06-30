"""Result model for Vastu analysis."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True, slots=True)
class VastuResult:
    """Outcome of a Vastu analysis rule."""

    passed: bool
    score: float
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    rule_name: str = ""

    def has_warnings(self) -> bool:
        return bool(self.warnings)

    def has_suggestions(self) -> bool:
        return bool(self.suggestions)
