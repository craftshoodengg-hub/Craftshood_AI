"""Iteration Engine for Building Model v2.

Deterministic engine that repeatedly evaluates and improves a BuildingModel
until convergence. Orchestrates Evaluation, Recommendation, and Optimization
without performing any AI reasoning.

Future extension points:
    - parallel optimization
    - genetic optimization
    - simulated annealing
    - reinforcement learning
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any

from ..evaluation.evaluation_pipeline import EvaluationPipeline, EvaluationPipelineConfig
from .design_iteration import DesignIteration
from .iteration_history import IterationHistory
from .optimizer import Optimizer
from .recommendation_engine import RecommendationEngine


class StoppingReason:
    """Deterministic stopping reasons for iteration loop."""
    MAX_ITERATIONS = "max_iterations"
    NO_IMPROVEMENT = "no_improvement"
    NO_ACTIONS = "no_actions"
    CONVERGED = "converged"


@dataclass(slots=True)
class IterationEngineConfig:
    """Configuration for the IterationEngine."""
    max_iterations: int = 10
    minimum_score_gain: float = 0.25
    stop_when_no_actions: bool = True
    stop_when_no_improvement: bool = True
    evaluation_config: EvaluationPipelineConfig | None = None


class IterationEngine:
    """Deterministic iteration engine."""

    def __init__(
        self,
        config: IterationEngineConfig | None = None,
        evaluation_pipeline: EvaluationPipeline | None = None,
        recommendation_engine: RecommendationEngine | None = None,
        optimizer: Optimizer | None = None,
    ) -> None:
        """Initialize the iteration engine."""
        self._config = config or IterationEngineConfig()
        self._evaluation_pipeline = evaluation_pipeline or EvaluationPipeline(
            config=self._config.evaluation_config,
        )
        self._recommendation_engine = recommendation_engine or RecommendationEngine()
        self._optimizer = optimizer or Optimizer()

    @property
    def config(self) -> IterationEngineConfig:
        return self._config

    @property
    def evaluation_pipeline(self) -> EvaluationPipeline:
        return self._evaluation_pipeline

    @property
    def recommendation_engine(self) -> RecommendationEngine:
        return self._recommendation_engine

    @property
    def optimizer(self) -> Optimizer:
        return self._optimizer

    def run(self, building_model: Any) -> IterationHistory:
        """Run the iteration loop on a building model."""
        iterations: list[DesignIteration] = []
        current_model = building_model
        previous_score = 0.0
        best_iteration: DesignIteration | None = None
        stopping_reason = ""

        for iteration_num in range(self._config.max_iterations):
            iteration_start = time.time()

            # Step 1: Evaluate
            evaluation_report = self._evaluation_pipeline.evaluate(current_model)
            current_score = self._extract_score(evaluation_report)

            # Step 2: Recommend
            improvement_plan = self._recommendation_engine.generate(evaluation_report)

            # Step 3: Optimize
            optimization_result = self._optimizer.optimize(
                building_model=current_model,
                improvement_plan=improvement_plan,
                before_score=previous_score,
                after_score=current_score,
            )

            iteration_elapsed = time.time() - iteration_start

            # Create iteration record
            iteration = DesignIteration(
                iteration=iteration_num,
                building_model=current_model,
                evaluation_report=evaluation_report,
                improvement_plan=improvement_plan,
                optimization_result=optimization_result,
                score=current_score,
                elapsed_time=iteration_elapsed,
                metadata={
                    "action_count": optimization_result.action_count,
                    "score_delta": optimization_result.score_delta,
                },
            )
            iterations.append(iteration)

            # Track best
            if best_iteration is None or iteration.score > best_iteration.score:
                best_iteration = iteration

            # Check stopping conditions
            score_gain = current_score - previous_score

            if self._config.stop_when_no_actions and optimization_result.action_count == 0:
                stopping_reason = StoppingReason.NO_ACTIONS
                break

            if self._config.stop_when_no_improvement and score_gain <= 0 and iteration_num > 0:
                stopping_reason = StoppingReason.NO_IMPROVEMENT
                break

            if iteration_num > 0 and 0 < score_gain < self._config.minimum_score_gain:
                stopping_reason = StoppingReason.CONVERGED
                break

            current_model = optimization_result.optimized_model
            previous_score = current_score
        else:
            stopping_reason = StoppingReason.MAX_ITERATIONS

        converged = stopping_reason == StoppingReason.CONVERGED

        return IterationHistory(
            iterations=iterations,
            best_iteration=best_iteration,
            stopping_reason=stopping_reason,
            converged=converged,
        )

    def _extract_score(self, evaluation_report: Any) -> float:
        """Extract the overall score from an evaluation report."""
        try:
            summary = evaluation_report.summary
            return float(summary.overall_score)
        except (AttributeError, TypeError):
            return 0.0

