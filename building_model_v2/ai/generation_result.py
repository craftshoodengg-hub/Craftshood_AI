"""Generation Result for Craftshood AI.

Immutable dataclass representing the complete result of the generation pipeline.
No AI. Pure deterministic orchestration output.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .design_requirements import DesignRequirements
from .layout_generation_result import LayoutGenerationResult
from .parser_result import ParserResult
from .space_program import SpaceProgram


@dataclass(frozen=True, slots=True)
class GenerationResult:
    """Complete result of the generation pipeline."""

    prompt: str = ""
    parser_result: Optional[ParserResult] = None
    design_requirements: Optional[DesignRequirements] = None
    space_program: Optional[SpaceProgram] = None
    initial_layout: Optional[LayoutGenerationResult] = None
    optimized_layout: Optional[LayoutGenerationResult] = None
    evaluation_report: Any = None
    layout_evaluation: Any = None
    improvement_plan: Any = None
    iteration_history: Any = None
    final_score: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def success(self) -> bool:
        return (
            self.parser_result is not None
            and self.design_requirements is not None
            and self.space_program is not None
            and self.initial_layout is not None
            and self.initial_layout.success
        )

    @property
    def quality(self) -> str:
        score = self.final_score
        if score >= 95:
            return "Excellent"
        elif score >= 85:
            return "Good"
        elif score >= 70:
            return "Fair"
        else:
            return "Poor"

    @property
    def iteration_count(self) -> int:
        if self.iteration_history is not None:
            return self.iteration_history.iteration_count
        return 0

    @property
    def layout_score(self) -> float:
        if self.layout_evaluation is not None:
            return self.layout_evaluation.overall_layout_score
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "success": self.success,
            "quality": self.quality,
            "final_score": self.final_score,
            "iteration_count": self.iteration_count,
            "layout_score": self.layout_score,
            "metadata": dict(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GenerationResult":
        return cls(
            prompt=data.get("prompt", ""),
            final_score=data.get("final_score", 0.0),
            metadata=dict(data.get("metadata", {})),
        )
