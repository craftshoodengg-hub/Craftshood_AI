"""Design Iteration for Building Model v2.

Immutable dataclass representing a single iteration in the optimization loop.
Tracks the model state, evaluation, recommendations, and results.

Future extension points:
    - parallel optimization
    - genetic optimization
    - simulated annealing
    - reinforcement learning
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict

from .improvement_plan import ImprovementPlan
from .optimization_result import OptimizationResult


@dataclass(frozen=True, slots=True)
class DesignIteration:
    """Immutable dataclass representing a single optimization iteration.

    Attributes:
        iteration: Zero-based iteration number.
        building_model: The building model at this iteration.
        evaluation_report: The evaluation report for this iteration.
        improvement_plan: The improvement plan generated for this iteration.
        optimization_result: The optimization result after applying actions.
        score: The quality score at this iteration.
        elapsed_time: Wall-clock time for this iteration in seconds.
        metadata: Additional metadata about this iteration.
    """

    iteration: int = 0
    building_model: Any = None
    evaluation_report: Any = None
    improvement_plan: ImprovementPlan | None = None
    optimization_result: OptimizationResult | None = None
    score: float = 0.0
    elapsed_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def improved(self) -> bool:
        """Check if this iteration improved the model.

        Returns:
            True if optimization result shows improvement.
        """
        if self.optimization_result is None:
            return False
        return self.optimization_result.improved

    @property
    def action_count(self) -> int:
        """Get the number of actions applied in this iteration.

        Returns:
            Count of applied actions.
        """
        if self.optimization_result is None:
            return 0
        return self.optimization_result.action_count

    @property
    def score_delta(self) -> float:
        """Get the score change from optimization in this iteration.

        Returns:
            Score delta (after - before).
        """
        if self.optimization_result is None:
            return 0.0
        return self.optimization_result.score_delta

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "iteration": self.iteration,
            "score": self.score,
            "elapsed_time": self.elapsed_time,
            "improved": self.improved,
            "action_count": self.action_count,
            "score_delta": self.score_delta,
            "metadata": dict(self.metadata),
        }

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, DesignIteration):
            return NotImplemented
        return (
            self.iteration == other.iteration
            and self.score == other.score
            and self.elapsed_time == other.elapsed_time
        )

    def __hash__(self) -> int:
        """Return hash."""
        return hash((self.iteration, self.score, self.elapsed_time))