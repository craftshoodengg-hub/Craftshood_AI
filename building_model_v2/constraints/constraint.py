"""Constraint base class for Building Model v2.

Defines the abstract base class for architectural constraints.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from ..validation.cross_entity_validator import BuildingModel
from .constraint_result import ConstraintResult


class Constraint(ABC):
    """Abstract base class for architectural constraints.
    
    All constraints must implement the evaluate method.
    
    Attributes:
        name: Human-readable name of the constraint.
        description: Description of what the constraint checks.
    """
    
    def __init__(self, name: str, description: str = "") -> None:
        """Initialize the constraint.
        
        Args:
            name: Human-readable name of the constraint.
            description: Description of what the constraint checks.
        """
        self._name = name
        self._description = description
    
    @property
    def name(self) -> str:
        """Get the constraint name.
        
        Returns:
            The constraint name.
        """
        return self._name
    
    @property
    def description(self) -> str:
        """Get the constraint description.
        
        Returns:
            The constraint description.
        """
        return self._description
    
    @abstractmethod
    def evaluate(self, building_model: BuildingModel) -> ConstraintResult:
        """Evaluate the constraint against a building model.
        
        Args:
            building_model: The building model to evaluate.
            
        Returns:
            ConstraintResult containing any issues found.
        """
        ...
    
    def __repr__(self) -> str:
        """Return a detailed representation of the constraint.
        
        Returns:
            A string representation useful for debugging.
        """
        return f"{self.__class__.__name__}(name='{self._name}')"
    
    def __str__(self) -> str:
        """Return a string representation of the constraint.
        
        Returns:
            The constraint name.
        """
        return self._name