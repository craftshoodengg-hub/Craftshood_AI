"""Optimization package for Building Model v2.

Provides deterministic improvement recommendations based on evaluation reports.
Includes Iteration Engine for repeated optimization until convergence.
Includes Multi-Objective Optimization framework for weighted scoring.
"""


from .action_registry import ActionRegistry

from .design_iteration import DesignIteration

from .improvement_plan import ImprovementPlan

from .iteration_engine import IterationEngine, IterationEngineConfig, StoppingReason

from .iteration_history import IterationHistory

from .multi_objective_optimizer import MultiObjectiveOptimizer

from .objective_score import ObjectiveScore

from .optimization_action import OptimizationAction

from .optimization_profile import OptimizationProfile

from .optimization_result import OptimizationResult

from .optimization_objective import OptimizationObjective

from .optimizer import Optimizer

from .recommendation_engine import RecommendationEngine


__all__ = [

    "ActionRegistry",

    "DesignIteration",

    "ImprovementPlan",

    "IterationEngine",

    "IterationEngineConfig",

    "IterationHistory",

    "MultiObjectiveOptimizer",

    "ObjectiveScore",

    "OptimizationAction",

    "OptimizationProfile",

    "OptimizationObjective",

    "OptimizationResult",

    "Optimizer",

    "RecommendationEngine",

    "StoppingReason",

]

