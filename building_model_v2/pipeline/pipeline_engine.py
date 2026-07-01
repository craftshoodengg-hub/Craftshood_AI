"""Pipeline engine.

Deterministic orchestrator that executes the complete Craftshood AI workflow.
"""
from __future__ import annotations

from dataclasses import replace
from ..ai.space_program import SpaceProgram
from ..architect.architect_engine import ArchitectEngine
from ..architect.circulation_evaluator import CirculationEvaluator
from ..architect.circulation_optimizer import CirculationOptimizer
from ..architect.circulation_planner import CirculationPlanner
from ..layout.building_model_converter import BuildingModelConverter
from ..layout.layout_cell import LayoutCell
from ..layout.layout_grid import LayoutGrid
from ..layout.layout_refiner import LayoutRefiner
from ..layout.room_placement_engine import RoomPlacementEngine
from ..layout.placement_result import PlacementResult
from ..layout.placement_validator import PlacementValidator
from .design_advisor.design_advisor_engine import DesignAdvisorEngine
from .design_advisor.advice_result import AdviceResult
from .design_advisor.design_advice import DesignAdvice
from .pipeline_result import PipelineResult
from .design_request import DesignRequest
from .vastu.vastu_engine import VastuEngine


class PipelineEngine:
    """Deterministic pipeline orchestrator.

    Executes the complete workflow from SpaceProgram to BuildingModel
    by coordinating existing engines in a fixed order.
    """

    def __init__(
        self,
        vastu_engine: VastuEngine | None = None,
        design_advisor_engine: DesignAdvisorEngine | None = None,
    ) -> None:
        """Initialize the pipeline engine with all sub-engines."""
        self._architect_engine = ArchitectEngine()
        self._circulation_planner = CirculationPlanner()
        self._circulation_evaluator = CirculationEvaluator()
        self._circulation_optimizer = CirculationOptimizer()
        self._placement_engine = RoomPlacementEngine()
        self._placement_validator = PlacementValidator()
        self._layout_refiner = LayoutRefiner()
        self._building_converter = BuildingModelConverter()
        self._vastu_engine = vastu_engine if vastu_engine is not None else VastuEngine()
        self._design_advisor_engine = (
            design_advisor_engine if design_advisor_engine is not None else DesignAdvisorEngine()
        )

    def run(self, space_program: SpaceProgram, design_request: DesignRequest | None = None) -> PipelineResult:
        """Execute the complete pipeline.

        Args:
            space_program: The space program to process.
            design_request: Optional design request for advisory analysis.

        Returns:
            PipelineResult containing all stage results.

        Raises:
            RuntimeError: If any pipeline stage fails.
        """
        try:
            # Stage 1-3: Architect engine (BubbleGenerator + ZoningEngine + ArchitectResult)
            architect_result = self._architect_engine.analyze(space_program)

            circulation_result = self._circulation_planner.plan(architect_result)
            circulation_metrics, circulation_score = self._circulation_evaluator.evaluate(
                circulation_result
            )
            optimization_result = self._circulation_optimizer.optimize(architect_result)
            grid = self._create_grid(space_program)
            placement_result = self._placement_engine.place(architect_result, grid)
            validation_result = self._placement_validator.validate(placement_result)
            refinement_result = self._layout_refiner.refine(placement_result)
            building = self._building_converter.convert(refinement_result)

            vastu_results = []
            vastu_score = 0.0
            vastu_warnings: list[str] = []
            vastu_suggestions: list[str] = []
            advisor_results: list[AdviceResult] = []
            advisor_score = 0.0
            advisor_strengths: list[str] = []
            advisor_weaknesses: list[str] = []
            advisor_advice: list[DesignAdvice] = []

            if self._vastu_engine is not None and design_request is not None:
                vastu_results = self._vastu_engine.analyze(design_request)
                vastu_score = self._vastu_engine.overall_score(vastu_results)
                vastu_warnings = self._vastu_engine.warnings(vastu_results)
                vastu_suggestions = self._vastu_engine.suggestions(vastu_results)

            result = PipelineResult(
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
                vastu_score=vastu_score,
                vastu_warnings=vastu_warnings,
                vastu_suggestions=vastu_suggestions,
                advisor_results=advisor_results,
                advisor_score=advisor_score,
                advisor_strengths=advisor_strengths,
                advisor_weaknesses=advisor_weaknesses,
                advisor_advice=advisor_advice,
            )

            if self._design_advisor_engine is not None and design_request is not None:
                advisor_results = self._design_advisor_engine.analyze(
                    design_request,
                    building,
                    result,
                )
                advisor_score = self._design_advisor_engine.overall_score(advisor_results)
                advisor_strengths = self._design_advisor_engine.strengths(advisor_results)
                advisor_weaknesses = self._design_advisor_engine.weaknesses(advisor_results)
                advisor_advice = self._design_advisor_engine.advice(advisor_results)
                result = replace(
                    result,
                    advisor_results=advisor_results,
                    advisor_score=advisor_score,
                    advisor_strengths=advisor_strengths,
                    advisor_weaknesses=advisor_weaknesses,
                    advisor_advice=advisor_advice,
                )

            return result

        except Exception as exc:
            raise RuntimeError(f"Pipeline stage failed: {exc}") from exc

    def _create_grid(self, program: SpaceProgram) -> LayoutGrid:
        """Create a deterministic layout grid from the space program.

        Args:
            program: The space program.

        Returns:
            A LayoutGrid sized to accommodate all rooms.
        """
        if not program.rooms:
            cells = tuple(LayoutCell(x=x, y=y) for y in range(10) for x in range(10))
            return LayoutGrid(width=10, height=10, cells=cells)

        max_x = 0
        max_y = 0
        for room in program.rooms:
            width = max(1, int(room.target_area ** 0.5))
            height = max(1, int(room.target_area / width))
            # Estimate position from metadata or default to 0
            x = program.metadata.get("start_x", 0)
            y = program.metadata.get("start_y", 0)
            max_x = max(max_x, x + width)
            max_y = max(max_y, y + height)

        width = max(10, max_x + 2)
        height = max(10, max_y + 2)
        cells = tuple(
            LayoutCell(x=x, y=y)
            for y in range(height)
            for x in range(width)
        )
        return LayoutGrid(width=width, height=height, cells=cells)