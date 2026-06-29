"""Parser Result for Craftshood AI.

Immutable dataclass representing the result of parsing user requirements.
No AI. Pure deterministic output.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from .design_requirements import DesignRequirements


@dataclass(frozen=True, slots=True)
class ParserResult:
    requirements: DesignRequirements
    confidence: float = 0.0
    extracted_fields: tuple[str, ...] = ()
    missing_fields: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()

    @property
    def is_complete(self) -> bool:
        return len(self.missing_fields) == 0 and self.confidence >= 0.5

    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirements": self.requirements.to_dict(),
            "confidence": self.confidence,
            "extracted_fields": list(self.extracted_fields),
            "missing_fields": list(self.missing_fields),
            "warnings": list(self.warnings),
            "is_complete": self.is_complete,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ParserResult:
        return cls(
            requirements=DesignRequirements.from_dict(data.get("requirements", {})),
            confidence=data.get("confidence", 0.0),
            extracted_fields=tuple(data.get("extracted_fields", [])),
            missing_fields=tuple(data.get("missing_fields", [])),
            warnings=tuple(data.get("warnings", [])),
        )
