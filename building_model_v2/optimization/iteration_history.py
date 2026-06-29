"""Iteration History for Building Model v2.

Immutable dataclass tracking the history of optimization iterations.
Provides methods for analyzing convergence and improvement patterns.

Future extension points:
    - parallel optimization
    - genetic optimization
    - simulated annealing
    - reinforcement learning
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from .design_iteration import DesignIteration


@dataclass(frozen=True, slots=True)
class IterationHistory:
    """Immutable dataclass tracking optimization iteration history.

    Attributes:
        iterations: List of all iterations performed, in order.
        best_iteration: The iteration with the best score.
        stopping_reason: Why the iteration loop stopped.
        converged: Whether the engine converged.
    """

    iterations: List[DesignIteration] = field(default_factory=list)
    best_iteration: DesignIteration | None = None
    stopping_reason: str = ""
    converged: bool = False

    @property
    def iteration_count(self) -> int:
        """Get the number of iterations performed.

        Returns:
            Count of iterations.
        """
        return len(self.iterations)

    @property
    def score_progression(self) -> List[float]:
        """Get the score at each iteration.

        Returns:
            List of scores in iteration order.
        """
        return [iteration.score for iteration in self.iterations]

    @property
    def best_score(self) -> float:
        """Get the best score achieved across all iterations.

        Returns:
            The highest score, or 0.0 if no iterations.
        """
        if not self.iterations:
            return 0.0
        return max(iteration.score for iteration in self.iterations)

    @property
    def average_improvement(self) -> float:
        """Get the average score improvement per iteration.

        Returns:
            Average improvement, or 0.0 if fewer than 2 iterations.
        """
        if len(self.iterations) < 2:
            return 0.0
        improvements = [
            self.iterations[i].score - self.iterations[i - 1].score
            for i in range(1, len(self.iterations))
        ]
        return sum(improvements) / len(improvements)

    @property
    def total_actions(self) -> int:
        """Get the total number of actions applied across all iterations.

        Returns:
            Count of applied actions.
        """
        return sum(iteration.action_count for iteration in self.iterations)

    @property
    def total_elapsed_time(self) -> float:
        """Get the total elapsed time across all iterations.

        Returns:
            Sum of iteration elapsed times in seconds.
        """
        return sum(iteration.elapsed_time for iteration in self.iterations)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary.

        Returns:
            Dictionary representation.
        """
        return {
            "iterations": [iteration.to_dict() for iteration in self.iterations],
            "best_iteration": self.best_iteration.to_dict() if self.best_iteration else None,
            "stopping_reason": self.stopping_reason,
            "converged": self.converged,
            "iteration_count": self.iteration_count,
            "score_progression": self.score_progression,
            "best_score": self.best_score,
            "average_improvement": self.average_improvement,
            "total_actions": self.total_actions,
            "total_elapsed_time": self.total_elapsed_time,
        }

    def get_iteration(self, index: int) -> DesignIteration | None:
        """Get a specific iteration by index.

        Args:
            index: Zero-based iteration index.

        Returns:
            The iteration if index is valid, None otherwise.
        """
        if 0 <= index < len(self.iterations):
            return self.iterations[index]
        return None

    def get_score_at(self, index: int) -> float:
        """Get the score at a specific iteration.

        Args:
            index: Zero-based iteration index.

        Returns:
            The score at that iteration, or 0.0 if index is invalid.
        """
        iteration = self.get_iteration(index)
        return iteration.score if iteration else 0.0

    def get_improvement_between(self, from_index: int, to_index: int) -> float:
        """Get the score improvement between two iterations.

        Args:
            from_index: Source iteration index.
            to_index: Target iteration index.

        Returns:
            Score difference (to - from), or 0.0 if indices are invalid.
        """
        from_score = self.get_score_at(from_index)
        to_score = self.get_score_at(to_index)
        return to_score - from_score

    def __eq__(self, other: object) -> bool:
        """Check equality."""
        if not isinstance(other, IterationHistory):
            return NotImplemented
        return (
            self.iterations == other.iterations
            and self.stopping_reason == other.stopping_reason
            and self.converged == other.converged
        )

    def __hash__(self) -> int:
        """Return hash."""
        return hash((
            tuple(self.iterations),
            self.stopping_reason,
            self.converged,
        ))