"""Constraint severity levels for Building Model v2.

Defines the severity levels that can be assigned to constraint issues.
Unlike validation, constraints represent design quality rather than correctness.
"""

from __future__ import annotations

from enum import Enum


class ConstraintSeverity(Enum):
    """Severity levels for constraint issues.
    
    Represents design quality levels rather than correctness.
    
    Attributes:
        INFO: Informational message, no action required.
        SUGGESTION: Design improvement suggestion.
        WARNING: Potential design issue, should be reviewed.
        RECOMMENDATION: Strong design recommendation.
    """
    
    INFO = "info"
    SUGGESTION = "suggestion"
    WARNING = "warning"
    RECOMMENDATION = "recommendation"
    
    def __str__(self) -> str:
        """Return the string representation of the severity.
        
        Returns:
            The severity value as a string.
        """
        return self.value
    
    def __repr__(self) -> str:
        """Return a detailed representation of the severity.
        
        Returns:
            A string in the format 'ConstraintSeverity.LEVEL'.
        """
        return f"ConstraintSeverity.{self.name}"
    
    def __lt__(self, other: ConstraintSeverity) -> bool:
        """Compare severity levels for ordering.
        
        Args:
            other: Another ConstraintSeverity to compare with.
            
        Returns:
            True if this severity is less than the other.
        """
        order = {
            ConstraintSeverity.INFO: 0,
            ConstraintSeverity.SUGGESTION: 1,
            ConstraintSeverity.WARNING: 2,
            ConstraintSeverity.RECOMMENDATION: 3,
        }
        return order[self] < order[other]
    
    def __le__(self, other: ConstraintSeverity) -> bool:
        """Compare severity levels for ordering.
        
        Args:
            other: Another ConstraintSeverity to compare with.
            
        Returns:
            True if this severity is less than or equal to the other.
        """
        return self == other or self.__lt__(other)
    
    def __gt__(self, other: ConstraintSeverity) -> bool:
        """Compare severity levels for ordering.
        
        Args:
            other: Another ConstraintSeverity to compare with.
            
        Returns:
            True if this severity is greater than the other.
        """
        return not self.__le__(other)
    
    def __ge__(self, other: ConstraintSeverity) -> bool:
        """Compare severity levels for ordering.
        
        Args:
            other: Another ConstraintSeverity to compare with.
            
        Returns:
            True if this severity is greater than or equal to the other.
        """
        return not self.__lt__(other)
    
    @property
    def is_recommendation(self) -> bool:
        """Check if this severity represents a recommendation.
        
        Returns:
            True if RECOMMENDATION.
        """
        return self == ConstraintSeverity.RECOMMENDATION
    
    @property
    def is_warning(self) -> bool:
        """Check if this severity represents a warning.
        
        Returns:
            True if WARNING.
        """
        return self == ConstraintSeverity.WARNING
    
    @property
    def is_suggestion(self) -> bool:
        """Check if this severity represents a suggestion.
        
        Returns:
            True if SUGGESTION.
        """
        return self == ConstraintSeverity.SUGGESTION
    
    @property
    def is_info(self) -> bool:
        """Check if this severity represents an info.
        
        Returns:
            True if INFO.
        """
        return self == ConstraintSeverity.INFO