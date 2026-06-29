"""Validator base class for Building Model v2.

Defines the abstract interface for validators.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Sequence

from .validation_result import ValidationResult


class Validator(ABC):
    """Abstract base class for validators.
    
    Subclasses must implement the validate method to perform
    validation on entities.
    """
    
    @abstractmethod
    def validate(self, entity: Any) -> ValidationResult:
        """Validate a single entity.
        
        Args:
            entity: The entity to validate.
            
        Returns:
            A ValidationResult containing any issues found.
        """
        ...
    
    def validate_many(self, entities: Sequence[Any]) -> ValidationResult:
        """Validate multiple entities.
        
        Args:
            entities: A sequence of entities to validate.
            
        Returns:
            A combined ValidationResult containing all issues found.
        """
        result = ValidationResult.create()
        for entity in entities:
            entity_result = self.validate(entity)
            result = result.merge(entity_result)
        return result