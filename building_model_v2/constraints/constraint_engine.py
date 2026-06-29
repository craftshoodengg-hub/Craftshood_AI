"""Constraint Engine for Building Model v2.

Orchestrates constraint evaluation and produces a single ConstraintResult.
"""

from __future__ import annotations

from typing import List, Sequence

from ..validation.cross_entity_validator import BuildingModel
from .constraint import Constraint
from .constraint_result import ConstraintResult


class ConstraintEngine:
    """Orchestrates evaluation of architectural constraints.
    
    Coordinates multiple constraints and merges their results into a single
    ConstraintResult.
    
    Attributes:
        constraints: List of registered constraints.
    """
    
    def __init__(self, constraints: Sequence[Constraint] | None = None) -> None:
        """Initialize the constraint engine.
        
        Args:
            constraints: Optional initial list of constraints.
        """
        self._constraints: List[Constraint] = list(constraints) if constraints else []
    
    @property
    def constraints(self) -> List[Constraint]:
        """Get the list of registered constraints.
        
        Returns:
            The list of registered constraints.
        """
        return self._constraints.copy()
    
    @property
    def constraint_count(self) -> int:
        """Get the number of registered constraints.
        
        Returns:
            The number of constraints.
        """
        return len(self._constraints)
    
    def register(self, constraint: Constraint) -> None:
        """Register a constraint with the engine.
        
        Args:
            constraint: The constraint to register.
        """
        self._constraints.append(constraint)
    
    def unregister(self, constraint: Constraint) -> bool:
        """Unregister a constraint from the engine.
        
        Args:
            constraint: The constraint to unregister.
            
        Returns:
            True if the constraint was found and removed.
        """
        try:
            self._constraints.remove(constraint)
            return True
        except ValueError:
            return False
    
    def clear(self) -> None:
        """Remove all registered constraints."""
        self._constraints.clear()
    
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate all registered constraints against a building model.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult containing all issues found.
        """
        result = ConstraintResult.create()
        
        for constraint in self._constraints:
            constraint_result = constraint.evaluate(building_model)
            result = result.merge(constraint_result)
        
        return result
    
    def __repr__(self) -> str:
        """Return a detailed representation of the engine.
        
        Returns:
            A string representation useful for debugging.
        """
        return f"ConstraintEngine(constraints={len(self._constraints)})"
    
    def __str__(self) -> str:
        """Return a string representation of the engine.
        
        Returns:
            A formatted string with constraint count.
        """
        return f"ConstraintEngine({len(self._constraints)} constraints)"