"""Pipeline result model.

Immutable dataclass representing the result of the end-to-end pipeline.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from ..architect.architect_result import ArchitectResult
from .design_advisor.advice_result import AdviceResult
from .design_advisor.design_advice import DesignAdvice
from .dwg_knowledge import DwgReference
from .vastu.vastu_result import VastuResult
from ..architect.circulation_metrics import CirculationMetrics
from ..architect.circulation_optimization_result import CirculationOptimizationResult
from ..architect.circulation_result import CirculationResult
from ..architect.circulation_score import CirculationScore
from ..entities_building import Building
from ..layout.layout_refinement_result import LayoutRefinementResult
from ..layout.placement_result import PlacementResult
from ..layout.placement_validation_result import PlacementValidationResult


@dataclass(frozen=True, slots=True)
class PipelineResult:
    """Immutable result of the complete pipeline execution.

    Attributes:
        architect_result: Result from architect engine.
        circulation_result: Result from circulation planner.
        circulation_metrics: Metrics from circulation evaluator.
        circulation_score: Score from circulation evaluation.
        optimization_result: Result from circulation optimizer.
        placement_result: Result from room placement engine.
        validation_result: Result from placement validator.
        refinement_result: Result from layout refiner.
        building: Final BuildingModel.
    """

    architect_result: ArchitectResult
    circulation_result: CirculationResult
    circulation_metrics: Any
    circulation_score: CirculationScore
    optimization_result: CirculationOptimizationResult
    placement_result: PlacementResult
    validation_result: PlacementValidationResult
    refinement_result: LayoutRefinementResult
    building: Building
    vastu_results: List[VastuResult] = field(default_factory=list)
    vastu_score: float = 0.0
    vastu_warnings: List[str] = field(default_factory=list)
    vastu_suggestions: List[str] = field(default_factory=list)
    advisor_results: List[AdviceResult] = field(default_factory=list)
    advisor_score: float = 0.0
    advisor_strengths: List[str] = field(default_factory=list)
    advisor_weaknesses: List[str] = field(default_factory=list)
    advisor_advice: List[DesignAdvice] = field(default_factory=list)
    reference_designs: List[DwgReference] = field(default_factory=list)
    retrieval_score: float = 0.0
    retrieval_count: int = 0

    @property
    def success(self) -> bool:
        """Whether the pipeline completed successfully."""
        return (
            self.validation_result.valid
            and self.refinement_result.refined_result.success
            and self.building is not None
        )

    @property
    def room_count(self) -> int:
        """Total number of rooms in the building."""
        return len(self.building.room_ids) if self.building else 0

    @property
    def floor_count(self) -> int:
        """Total number of floors in the building."""
        return len(self.building.floor_ids) if self.building else 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "architect_result": self.architect_result.to_dict(),
            "circulation_result": self.circulation_result.to_dict(),
            "circulation_metrics": self.circulation_metrics.to_dict(),
            "circulation_score": self.circulation_score.to_dict(),
            "optimization_result": self.optimization_result.to_dict(),
            "placement_result": self.placement_result.to_dict(),
            "validation_result": self.validation_result.to_dict(),
            "refinement_result": self.refinement_result.to_dict(),
            "building": self.building.to_dict(),
            "vastu_results": [result.to_dict() for result in self.vastu_results],
            "vastu_score": self.vastu_score,
            "vastu_warnings": list(self.vastu_warnings),
            "vastu_suggestions": list(self.vastu_suggestions),
            "advisor_results": [result.to_dict() for result in self.advisor_results],
            "advisor_score": self.advisor_score,
            "advisor_strengths": list(self.advisor_strengths),
            "advisor_weaknesses": list(self.advisor_weaknesses),
            "advisor_advice": [advice.to_dict() for advice in self.advisor_advice],
            "reference_designs": [reference.to_dict() for reference in self.reference_designs],
            "retrieval_score": self.retrieval_score,
            "retrieval_count": self.retrieval_count,
            "success": self.success,
            "room_count": self.room_count,
            "floor_count": self.floor_count,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> PipelineResult:
        """Deserialize from dictionary."""
        architect_result = ArchitectResult.from_dict(data["architect_result"])
        circulation_result = CirculationResult.from_dict(data["circulation_result"])
        circulation_metrics = CirculationMetrics.from_dict(data["circulation_metrics"])
        circulation_score = CirculationScore.from_dict(data["circulation_score"])
        optimization_result = CirculationOptimizationResult.from_dict(data["optimization_result"])
        placement_result = PlacementResult.from_dict(data["placement_result"])
        validation_result = PlacementValidationResult.from_dict(data["validation_result"])
        refinement_result = LayoutRefinementResult.from_dict(data["refinement_result"])
        building = Building.from_dict(data["building"])
        vastu_results = [VastuResult.from_dict(item) for item in data.get("vastu_results", [])]
        advisor_results = [AdviceResult.from_dict(item) for item in data.get("advisor_results", [])]
        advisor_score = float(data.get("advisor_score", 0.0))
        advisor_strengths = list(data.get("advisor_strengths", []))
        advisor_weaknesses = list(data.get("advisor_weaknesses", []))
        advisor_advice = [DesignAdvice.from_dict(item) for item in data.get("advisor_advice", [])]
        reference_designs = [DwgReference.from_dict(item) for item in data.get("reference_designs", [])]
        retrieval_score = float(data.get("retrieval_score", 0.0))
        retrieval_count = int(data.get("retrieval_count", 0))
        return cls(
            architect_result=architect_result,
            circulation_result=circulation_result,
            circulation_metrics=circulation_metrics,
            circulation_score=circulation_score,
            optimization_result=optimization_result,
            placement_result=placement_result,
            validation_result=validation_result,
            refinement_result=refinement_result,
            building=building,
            vastu_results=vastu_results,
            advisor_results=advisor_results,
            advisor_score=advisor_score,
            advisor_strengths=advisor_strengths,
            advisor_weaknesses=advisor_weaknesses,
            advisor_advice=advisor_advice,
            reference_designs=reference_designs,
            retrieval_score=retrieval_score,
            retrieval_count=retrieval_count,
        )