"""Domain model for design advisor results."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

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
