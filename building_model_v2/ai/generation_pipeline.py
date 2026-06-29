"""Generation Pipeline for Craftshood AI."""
from __future__ import annotations
from typing import Any, Dict
from ..evaluation.evaluation_pipeline import EvaluationPipeline
from ..layout.layout_evaluation import LayoutEvaluationEngine
from ..optimization.iteration_engine import IterationEngine, IterationEngineConfig
from ..optimization.recommendation_engine import RecommendationEngine
from .generation_result import GenerationResult
from .layout_generator import LayoutGenerator
from .requirement_parser import RequirementParser
from .space_generator import SpaceProgramGenerator


class GenerationPipeline:
    def __init__(self) -> None:
        self._requirement_parser = RequirementParser()
        self._space_generator = SpaceProgramGenerator()
        self._layout_generator = LayoutGenerator()
        self._evaluation_pipeline = EvaluationPipeline()
        self._layout_evaluation = LayoutEvaluationEngine()
        self._recommendation_engine = RecommendationEngine()
        self._iteration_engine = IterationEngine(
            config=IterationEngineConfig(max_iterations=3),
        )

    def generate(self, prompt: str) -> GenerationResult:
        warnings: list[str] = []
        parser_result = self._requirement_parser.parse(prompt)
        if not parser_result.is_complete:
            warnings.append(f"Parser confidence: {parser_result.confidence}")
            for w in parser_result.warnings:
                warnings.append(w)
        design_requirements = parser_result.requirements
        space_program = self._space_generator.generate(design_requirements)
        initial_layout = self._layout_generator.generate(space_program)
        if not initial_layout.success:
            warnings.append("Initial layout generation failed")
            return self._build_result(prompt, parser_result, design_requirements, space_program, initial_layout, None, None, None, None, None, 0.0, warnings)
        building_model = initial_layout.building_model
        try:
            evaluation_report = self._evaluation_pipeline.evaluate(building_model)
        except Exception as e:
            warnings.append(f"Evaluation failed: {e}")
            evaluation_report = None
        try:
            layout_eval = self._layout_evaluation.evaluate(building_model)
        except Exception as e:
            warnings.append(f"Layout evaluation failed: {e}")
            layout_eval = None
        improvement_plan = None
        if evaluation_report is not None:
            try:
                improvement_plan = self._recommendation_engine.generate(evaluation_report)
            except Exception as e:
                warnings.append(f"Recommendation generation failed: {e}")
        try:
            iteration_history = self._iteration_engine.run(building_model)
        except Exception as e:
            warnings.append(f"Iteration failed: {e}")
            iteration_history = None
        final_score = self._calculate_final_score(evaluation_report, layout_eval)
        return self._build_result(prompt, parser_result, design_requirements, space_program, initial_layout, None, evaluation_report, layout_eval, improvement_plan, iteration_history, final_score, warnings)

    def _calculate_final_score(self, evaluation_report: Any, layout_eval: Any) -> float:
        eval_score = 0.0
        layout_score = 0.0
        if evaluation_report is not None:
            try:
                eval_score = evaluation_report.summary.overall_score
            except (AttributeError, TypeError):
                pass
        if layout_eval is not None:
            try:
                layout_score = layout_eval.overall_layout_score
            except (AttributeError, TypeError):
                pass
        overall = (eval_score * 0.7) + (layout_score * 0.3)
        return max(0.0, min(100.0, overall))

    def _build_result(self, prompt, parser_result, design_requirements, space_program, initial_layout, optimized_layout, evaluation_report, layout_eval, improvement_plan, iteration_history, final_score, warnings) -> GenerationResult:
        return GenerationResult(
            prompt=prompt, parser_result=parser_result, design_requirements=design_requirements,
            space_program=space_program, initial_layout=initial_layout, optimized_layout=optimized_layout,
            evaluation_report=evaluation_report, layout_evaluation=layout_eval,
            improvement_plan=improvement_plan, iteration_history=iteration_history,
            final_score=final_score, metadata={"warnings": warnings, "pipeline_version": "1.0.0"},
        )
