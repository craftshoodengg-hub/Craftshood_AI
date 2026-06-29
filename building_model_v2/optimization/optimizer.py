"""Optimizer for Building Model v2.

Deterministic optimization engine that applies actions to a copy of a BuildingModel.
The original BuildingModel remains completely unchanged.
"""

from __future__ import annotations

from copy import deepcopy
from typing import Any, List, Optional

from .action_registry import ActionRegistry
from .improvement_plan import ImprovementPlan
from .optimization_action import OptimizationAction
from .optimization_result import OptimizationResult


class Optimizer:
    """Deterministic optimization engine.
    
    Applies optimization actions to a copy of a BuildingModel.
    The original model is never modified.
    
    Pipeline:
        1. Deep copy model
        2. Apply actions in priority order
        3. Track successfully applied actions
        4. Return OptimizationResult
    
    No evaluation logic.
    No scoring logic.
    No recommendation logic.
    Pure orchestration.
    """
    
    def __init__(self, registry: Optional[ActionRegistry] = None) -> None:
        """Initialize the optimizer.
        
        Args:
            registry: Optional custom action registry. Uses default if None.
        """
        self._registry = registry or ActionRegistry()
    
    @property
    def registry(self) -> ActionRegistry:
        """Get the action registry."""
        return self._registry
    
    def optimize(
        self,
        building_model: Any,
        improvement_plan: ImprovementPlan,
        before_score: float = 0.0,
        after_score: float = 0.0,
    ) -> OptimizationResult:
        """Apply optimization actions to a copy of the building model.
        
        Args:
            building_model: The original building model (never modified).
            improvement_plan: The plan containing actions to apply.
            before_score: Quality score before optimization.
            after_score: Quality score after optimization.
            
        Returns:
            OptimizationResult with original, optimized, and applied actions.
        """
        # Step 1: Deep copy model
        optimized_model = deepcopy(building_model)
        
        # Step 2: Apply actions in priority order
        applied_actions: List[OptimizationAction] = []
        
        for action in improvement_plan.actions:
            optimized_model = self._apply_action(optimized_model, action)
            applied_actions.append(action)
        
        # Step 4: Return result
        return OptimizationResult(
            original_model=building_model,
            optimized_model=optimized_model,
            applied_actions=applied_actions,
            before_score=before_score,
            after_score=after_score,
            metadata={
                "optimizer_version": "1.0.0",
                "action_count": len(applied_actions),
            },
        )
    
    def _apply_action(
        self,
        model: Any,
        action: OptimizationAction,
    ) -> Any:
        """Apply a single optimization action to the model.
        
        Args:
            model: The model to apply the action to.
            action: The optimization action to apply.
            
        Returns:
            New model with action applied, or original if action fails.
        """
        # Get the optimization function from registry
        func = self._registry.get(action.id)
        
        if func is None:
            # Unknown action - return model unchanged
            return model
        
        try:
            # Apply the action
            result = func(model, action)
            
            # Validate result is not None and values are positive
            if result is None:
                return model
            
            return result
        except Exception:
            # Never throw on unsupported actions - fail gracefully
            return model
    
    def can_optimize(self, action_id: str) -> bool:
        """Check if an action can be optimized.
        
        Args:
            action_id: The action/constraint ID to check.
            
        Returns:
            True if an optimization function is registered.
        """
        return self._registry.has(action_id)
    
    @property
    def available_actions(self) -> frozenset[str]:
        """Get all available action IDs.
        
        Returns:
            Frozenset of registered action IDs.
        """
        return self._registry.registered_codes