"""ValidationError representation for Building Model v2.

Defines the structure for validation errors with all associated metadata.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from .validation_severity import ValidationSeverity


@dataclass(frozen=True, slots=True)
class ValidationError:
    """Represents a single validation error.
    
    Attributes:
        code: Unique error code identifier.
        message: Human-readable error message.
        severity: Severity level of the error.
        entity_id: Optional ID of the entity that caused the error.
        entity_type: Optional type of the entity.
        location: Optional location information (e.g., coordinates).
        metadata: Additional metadata about the error.
    """
    
    code: str
    message: str
    severity: ValidationSeverity
    entity_id: Optional[str] = None
    entity_type: Optional[str] = None
    location: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate the error after initialization.
        
        Raises:
            ValueError: If code or message is empty.
        """
        if not self.code:
            raise ValueError("ValidationError code cannot be empty")
        if not self.message:
            raise ValueError("ValidationError message cannot be empty")
    
    def __str__(self) -> str:
        """Return a string representation of the error.
        
        Returns:
            A formatted string with severity, code, and message.
        """
        return f"[{self.severity.value.upper()}] {self.code}: {self.message}"
    
    def __repr__(self) -> str:
        """Return a detailed representation of the error.
        
        Returns:
            A string representation useful for debugging.
        """
        return (
            f"ValidationError(code={self.code!r}, message={self.message!r}, "
            f"severity={self.severity!r}, entity_id={self.entity_id!r})"
        )
    
    def __eq__(self, other: object) -> bool:
        """Check equality between ValidationError instances.
        
        Args:
            other: Another object to compare with.
            
        Returns:
            True if all fields are equal.
        """
        if not isinstance(other, ValidationError):
            return NotImplemented
        return (
            self.code == other.code
            and self.message == other.message
            and self.severity == other.severity
            and self.entity_id == other.entity_id
            and self.entity_type == other.entity_type
            and self.location == other.location
            and self.metadata == other.metadata
        )
    
    def __hash__(self) -> int:
        """Return a hash for the error.
        
        Returns:
            A hash based on the error's fields.
        """
        return hash((
            self.code,
            self.message,
            self.severity,
            self.entity_id,
            self.entity_type,
            self.location,
        ))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary.
        
        Returns:
            A dictionary representation of the error.
        """
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity.value,
            "entity_id": self.entity_id,
            "entity_type": self.entity_type,
            "location": self.location,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ValidationError:
        """Create a ValidationError from a dictionary.
        
        Args:
            data: Dictionary containing error data.
            
        Returns:
            A new ValidationError instance.
            
        Raises:
            KeyError: If required fields are missing.
            ValueError: If severity value is invalid.
        """
        return cls(
            code=data["code"],
            message=data["message"],
            severity=ValidationSeverity(data["severity"]),
            entity_id=data.get("entity_id"),
            entity_type=data.get("entity_type"),
            location=data.get("location"),
            metadata=data.get("metadata", {}),
        )
    
    def with_entity(self, entity_id: str, entity_type: Optional[str] = None) -> ValidationError:
        """Create a copy of this error with entity information.
        
        Args:
            entity_id: The entity ID.
            entity_type: The entity type.
            
        Returns:
            A new ValidationError with the entity information.
        """
        return ValidationError(
            code=self.code,
            message=self.message,
            severity=self.severity,
            entity_id=entity_id,
            entity_type=entity_type,
            location=self.location,
            metadata=self.metadata,
        )
    
    def with_location(self, location: str) -> ValidationError:
        """Create a copy of this error with location information.
        
        Args:
            location: The location string.
            
        Returns:
            A new ValidationError with the location information.
        """
        return ValidationError(
            code=self.code,
            message=self.message,
            severity=self.severity,
            entity_id=self.entity_id,
            entity_type=self.entity_type,
            location=location,
            metadata=self.metadata,
        )
    
    def with_metadata(self, key: str, value: Any) -> ValidationError:
        """Create a copy of this error with additional metadata.
        
        Args:
            key: The metadata key.
            value: The metadata value.
            
        Returns:
            A new ValidationError with the additional metadata.
        """
        new_metadata = dict(self.metadata)
        new_metadata[key] = value
        return ValidationError(
            code=self.code,
            message=self.message,
            severity=self.severity,
            entity_id=self.entity_id,
            entity_type=self.entity_type,
            location=self.location,
            metadata=new_metadata,
        )