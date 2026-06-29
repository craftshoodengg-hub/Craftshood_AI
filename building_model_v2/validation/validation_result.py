"""ValidationResult for Building Model v2.

Defines the structure for collecting and managing validation results.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Sequence

from .validation_error import ValidationError
from .validation_severity import ValidationSeverity


@dataclass(slots=True)
class ValidationResult:
    """Collects validation errors, warnings, and info messages.
    
    Provides methods for adding issues and computing aggregate statistics.
    
    Attributes:
        errors: List of validation errors (ERROR and CRITICAL).
        warnings: List of validation warnings.
        infos: List of validation info messages.
    """
    
    errors: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    infos: List[ValidationError] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        """Ensure lists are initialized."""
        if self.errors is None:
            object.__setattr__(self, "errors", [])
        if self.warnings is None:
            object.__setattr__(self, "warnings", [])
        if self.infos is None:
            object.__setattr__(self, "infos", [])
    
    @property
    def is_valid(self) -> bool:
        """Check if the result has no errors.
        
        Returns:
            True if there are no ERROR or CRITICAL issues.
        """
        return len(self.errors) == 0
    
    @property
    def error_count(self) -> int:
        """Get the number of errors.
        
        Returns:
            The count of ERROR and CRITICAL issues.
        """
        return len(self.errors)
    
    @property
    def warning_count(self) -> int:
        """Get the number of warnings.
        
        Returns:
            The count of WARNING issues.
        """
        return len(self.warnings)
    
    @property
    def info_count(self) -> int:
        """Get the number of info messages.
        
        Returns:
            The count of INFO issues.
        """
        return len(self.infos)
    
    @property
    def critical_count(self) -> int:
        """Get the number of critical errors.
        
        Returns:
            The count of CRITICAL issues.
        """
        return sum(1 for e in self.errors if e.severity == ValidationSeverity.CRITICAL)
    
    @property
    def has_errors(self) -> bool:
        """Check if there are any errors.
        
        Returns:
            True if there are ERROR or CRITICAL issues.
        """
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if there are any warnings.
        
        Returns:
            True if there are WARNING issues.
        """
        return len(self.warnings) > 0
    
    @property
    def has_infos(self) -> bool:
        """Check if there are any info messages.
        
        Returns:
            True if there are INFO issues.
        """
        return len(self.infos) > 0
    
    @property
    def total_count(self) -> int:
        """Get the total number of issues.
        
        Returns:
            Sum of errors, warnings, and infos.
        """
        return len(self.errors) + len(self.warnings) + len(self.infos)
    
    @property
    def all_issues(self) -> List[ValidationError]:
        """Get all issues in a single list.
        
        Returns:
            Combined list of errors, warnings, and infos.
        """
        return self.errors + self.warnings + self.infos
    
    def add_error(self, error: ValidationError) -> None:
        """Add a validation error.
        
        Args:
            error: The error to add.
        """
        self.errors.append(error)
    
    def add_warning(self, warning: ValidationError) -> None:
        """Add a validation warning.
        
        Args:
            warning: The warning to add.
        """
        self.warnings.append(warning)
    
    def add_info(self, info: ValidationError) -> None:
        """Add a validation info message.
        
        Args:
            info: The info to add.
        """
        self.infos.append(info)
    
    def add(self, error: ValidationError) -> None:
        """Add a validation issue based on its severity.
        
        Args:
            error: The validation error to add.
        """
        if error.severity == ValidationSeverity.ERROR or error.severity == ValidationSeverity.CRITICAL:
            self.add_error(error)
        elif error.severity == ValidationSeverity.WARNING:
            self.add_warning(error)
        else:
            self.add_info(error)
    
    def merge(self, other: ValidationResult) -> ValidationResult:
        """Merge another ValidationResult into this one.
        
        Args:
            other: The other result to merge.
            
        Returns:
            A new ValidationResult containing all issues from both.
        """
        return ValidationResult(
            errors=self.errors + other.errors,
            warnings=self.warnings + other.warnings,
            infos=self.infos + other.infos,
        )
    
    def get_errors_by_code(self, code: str) -> List[ValidationError]:
        """Get all errors with a specific code.
        
        Args:
            code: The error code to filter by.
            
        Returns:
            List of errors with the specified code.
        """
        return [e for e in self.errors if e.code == code]
    
    def get_warnings_by_code(self, code: str) -> List[ValidationError]:
        """Get all warnings with a specific code.
        
        Args:
            code: The warning code to filter by.
            
        Returns:
            List of warnings with the specified code.
        """
        return [w for w in self.warnings if w.code == code]
    
    def get_by_severity(self, severity: ValidationSeverity) -> List[ValidationError]:
        """Get all issues with a specific severity.
        
        Args:
            severity: The severity level to filter by.
            
        Returns:
            List of issues with the specified severity.
        """
        if severity == ValidationSeverity.ERROR:
            return [e for e in self.errors if e.severity == ValidationSeverity.ERROR]
        elif severity == ValidationSeverity.CRITICAL:
            return [e for e in self.errors if e.severity == ValidationSeverity.CRITICAL]
        elif severity == ValidationSeverity.WARNING:
            return list(self.warnings)
        else:
            return list(self.infos)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the result to a dictionary.
        
        Returns:
            A dictionary representation of the result.
        """
        return {
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "critical_count": self.critical_count,
            "errors": [e.to_dict() for e in self.errors],
            "warnings": [w.to_dict() for w in self.warnings],
            "infos": [i.to_dict() for i in self.infos],
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ValidationResult:
        """Create a ValidationResult from a dictionary.
        
        Args:
            data: Dictionary containing result data.
            
        Returns:
            A new ValidationResult instance.
        """
        return cls(
            errors=[ValidationError.from_dict(e) for e in data.get("errors", [])],
            warnings=[ValidationError.from_dict(w) for w in data.get("warnings", [])],
            infos=[ValidationError.from_dict(i) for i in data.get("infos", [])],
        )
    
    @classmethod
    def create(cls) -> ValidationResult:
        """Create an empty valid result.
        
        Returns:
            A new empty ValidationResult.
        """
        return cls()
    
    @classmethod
    def from_error(cls, error: ValidationError) -> ValidationResult:
        """Create a result containing a single error.
        
        Args:
            error: The error to include.
            
        Returns:
            A new ValidationResult with the error.
        """
        result = cls()
        result.add(error)
        return result
    
    @classmethod
    def from_errors(cls, errors: Sequence[ValidationError]) -> ValidationResult:
        """Create a result containing multiple errors.
        
        Args:
            errors: The errors to include.
            
        Returns:
            A new ValidationResult with the errors.
        """
        result = cls()
        for error in errors:
            result.add(error)
        return result
    
    def __str__(self) -> str:
        """Return a string representation of the result.
        
        Returns:
            A formatted string with counts.
        """
        return (
            f"ValidationResult("
            f"valid={self.is_valid}, "
            f"errors={self.error_count}, "
            f"warnings={self.warning_count}, "
            f"infos={self.info_count})"
        )
    
    def __repr__(self) -> str:
        """Return a detailed representation of the result.
        
        Returns:
            A string representation useful for debugging.
        """
        return (
            f"ValidationResult("
            f"errors={len(self.errors)}, "
            f"warnings={len(self.warnings)}, "
            f"infos={len(self.infos)})"
        )
    
    def __eq__(self, other: object) -> bool:
        """Check equality between ValidationResult instances.
        
        Args:
            other: Another object to compare with.
            
        Returns:
            True if all fields are equal.
        """
        if not isinstance(other, ValidationResult):
            return NotImplemented
        return (
            self.errors == other.errors
            and self.warnings == other.warnings
            and self.infos == other.infos
        )
    
    def __bool__(self) -> bool:
        """Return True if the result is valid.
        
        Returns:
            True if there are no errors.
        """
        return self.is_valid