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

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "score": self.score,
            "warnings": list(self.warnings),
            "suggestions": list(self.suggestions),
            "rule_name": self.rule_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "VastuResult":
        return cls(
            passed=bool(data["passed"]),
            score=float(data["score"]),
            warnings=list(data.get("warnings", [])),
            suggestions=list(data.get("suggestions", [])),
            rule_name=str(data.get("rule_name", "")),
        )
