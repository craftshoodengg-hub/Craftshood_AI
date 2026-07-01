"""Domain model for design advisor results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .design_advice import DesignAdvice


@dataclass(frozen=True, slots=True)
class AdviceResult:
    """Aggregated advice output from a design advisor rule."""

    advice: List[DesignAdvice] = field(default_factory=list)
    score: float = 0.0
    strengths: List[str] = field(default_factory=list)
    weaknesses: List[str] = field(default_factory=list)

    def has_strengths(self) -> bool:
        return bool(self.strengths)

    def has_weaknesses(self) -> bool:
        return bool(self.weaknesses)

    def advice_count(self) -> int:
        return len(self.advice)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "advice": [item.to_dict() for item in self.advice],
            "score": self.score,
            "strengths": list(self.strengths),
            "weaknesses": list(self.weaknesses),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AdviceResult":
        return cls(
            advice=[DesignAdvice.from_dict(item) for item in data.get("advice", [])],
            score=float(data.get("score", 0.0)),
            strengths=list(data.get("strengths", [])),
            weaknesses=list(data.get("weaknesses", [])),
        )
