"""Validation severity levels for Building Model v2.

Defines the severity levels that can be assigned to validation issues.
"""

from __future__ import annotations

from enum import Enum


class ValidationSeverity(Enum):
    """Severity levels for validation issues.
    
    Attributes:
        INFO: Informational message, no action required.
        WARNING: Potential issue, should be reviewed.
        ERROR: Definite issue, should be fixed.
        CRITICAL: Severe issue, must be fixed.
    """
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    
    def __str__(self) -> str:
        """Return the string representation of the severity.
        
        Returns:
            The severity value as a string.
        """
        return self.value
    
    def __repr__(self) -> str:
        """Return a detailed representation of the severity.
        
        Returns:
            A string in the format 'ValidationSeverity.LEVEL'.
        """
        return f"ValidationSeverity.{self.name}"
    
    def __lt__(self, other: ValidationSeverity) -> bool:
        """Compare severity levels for ordering.
        
        Args:
            other: Another ValidationSeverity to compare with.
            
        Returns:
            True if this severity is less than the other.
        """
        order = {
            ValidationSeverity.INFO: 0,
            ValidationSeverity.WARNING: 1,
            ValidationSeverity.ERROR: 2,
            ValidationSeverity.CRITICAL: 3,
        }
        return order[self] < order[other]
    
    def __le__(self, other: ValidationSeverity) -> bool:
        """Compare severity levels for ordering.
        
        Args:
            other: Another ValidationSeverity to compare with.
            
        Returns:
            True if this severity is less than or equal to the other.
        """
        return self == other or self.__lt__(other)
    
    def __gt__(self, other: ValidationSeverity) -> bool:
        """Compare severity levels for ordering.
        
        Args:
            other: Another ValidationSeverity to compare with.
            
        Returns:
            True if this severity is greater than the other.
        """
        return not self.__le__(other)
    
    def __ge__(self, other: ValidationSeverity) -> bool:
        """Compare severity levels for ordering.
        
        Args:
            other: Another ValidationSeverity to compare with.
            
        Returns:
            True if this severity is greater than or equal to the other.
        """
        return not self.__lt__(other)
    
    @property
    def is_error(self) -> bool:
        """Check if this severity represents an error condition.
        
        Returns:
            True if ERROR or CRITICAL.
        """
        return self in (ValidationSeverity.ERROR, ValidationSeverity.CRITICAL)
    
    @property
    def is_warning(self) -> bool:
        """Check if this severity represents a warning condition.
        
        Returns:
            True if WARNING.
        """
        return self == ValidationSeverity.WARNING
    
    @property
    def is_info(self) -> bool:
        """Check if this severity represents an info condition.
        
        Returns:
            True if INFO.
        """
        return self == ValidationSeverity.INFO