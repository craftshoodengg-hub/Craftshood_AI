"""Result model for individual constraint validation checks."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass(frozen=True, slots=True)
class ConstraintResult:
    """Result of a single constraint validation."""

    passed: bool
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
    constraint_name: str = ""

    def has_errors(self) -> bool:
        return bool(self.errors)

    def has_warnings(self) -> bool:
        return bool(self.warnings)

    def to_dict(self) -> dict[str, object]:
        return {
            "passed": self.passed,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "constraint_name": self.constraint_name,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "ConstraintResult":
        return cls(
            passed=bool(data["passed"]),
            warnings=tuple(data.get("warnings", [])),
            errors=tuple(data.get("errors", [])),
            constraint_name=str(data.get("constraint_name", "")),
        )
