"""Relationship validator for Building Model v2.

Validates relationship entities for internal correctness.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from ..relationships import Relationship, RelationshipType
from .validation_error import ValidationError
from .validation_result import ValidationResult
from .validation_severity import ValidationSeverity
from .validator import Validator


# Validation error codes
RELATIONSHIP_INVALID_TYPE: Final[str] = "RELATIONSHIP_INVALID_TYPE"
RELATIONSHIP_MISSING_SOURCE: Final[str] = "RELATIONSHIP_MISSING_SOURCE"
RELATIONSHIP_MISSING_TARGET: Final[str] = "RELATIONSHIP_MISSING_TARGET"
RELATIONSHIP_SELF_REFERENCE: Final[str] = "RELATIONSHIP_SELF_REFERENCE"
RELATIONSHIP_INVALID_METADATA: Final[str] = "RELATIONSHIP_INVALID_METADATA"


@dataclass(slots=True)
class RelationshipValidationConfig:
    """Configuration for relationship validation thresholds.
    
    Attributes:
        allow_self_relationship: Whether source_id == target_id is allowed.
        allow_empty_metadata: Whether empty metadata dict is allowed.
        allow_unknown_relationship: Whether unknown relationship types are allowed.
    """
    
    allow_self_relationship: bool = False
    allow_empty_metadata: bool = True
    allow_unknown_relationship: bool = True


class RelationshipValidator(Validator):
    """Validates Relationship entities.
    
    Checks relationship fields, metadata, and type validity.
    
    Attributes:
        config: Validation thresholds configuration.
    """
    
    def __init__(self, config: RelationshipValidationConfig | None = None) -> None:
        """Initialize the relationship validator.
        
        Args:
            config: Optional validation configuration. Uses defaults if not provided.
        """
        self._config = config or RelationshipValidationConfig()
    
    @property
    def config(self) -> RelationshipValidationConfig:
        """Get the validation configuration.
        
        Returns:
            The current validation configuration.
        """
        return self._config
    
    def validate(self, entity: Any) -> ValidationResult:
        """Validate a Relationship entity.
        
        Args:
            entity: The entity to validate. Must be a Relationship instance.
            
        Returns:
            ValidationResult containing any issues found.
        """
        if not isinstance(entity, Relationship):
            result = ValidationResult.create()
            result.add_error(ValidationError(
                code="RELATIONSHIP_INVALID_ENTITY",
                message=f"Expected Relationship entity, got {type(entity).__name__}",
                severity=ValidationSeverity.ERROR,
            ))
            return result
        
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []
        infos: list[ValidationError] = []
        
        # Validate relationship fields
        self._validate_fields(entity, errors, warnings)
        
        # Validate metadata
        self._validate_metadata(entity, errors, warnings)
        
        return ValidationResult(
            errors=errors,
            warnings=warnings,
            infos=infos,
        )
    
    def _validate_fields(self, relationship: Relationship, errors: list[ValidationError], warnings: list[ValidationError]) -> None:
        """Validate relationship fields.
        
        Args:
            relationship: The relationship to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate source_id
        if not relationship.source_id or not relationship.source_id.strip():
            errors.append(ValidationError(
                code=RELATIONSHIP_MISSING_SOURCE,
                message="Relationship source_id is missing",
                severity=ValidationSeverity.ERROR,
                entity_id=relationship.id,
                entity_type="Relationship",
            ))
        
        # Validate target_id
        if not relationship.target_id or not relationship.target_id.strip():
            errors.append(ValidationError(
                code=RELATIONSHIP_MISSING_TARGET,
                message="Relationship target_id is missing",
                severity=ValidationSeverity.ERROR,
                entity_id=relationship.id,
                entity_type="Relationship",
            ))
        
        # Validate self-reference
        if not self._config.allow_self_relationship:
            if relationship.source_id and relationship.target_id and relationship.source_id == relationship.target_id:
                errors.append(ValidationError(
                    code=RELATIONSHIP_SELF_REFERENCE,
                    message=f"Relationship references itself: {relationship.source_id}",
                    severity=ValidationSeverity.ERROR,
                    entity_id=relationship.id,
                    entity_type="Relationship",
                    metadata={"source_id": relationship.source_id, "target_id": relationship.target_id},
                ))
        
        # Validate relationship type
        if relationship.relationship_type not in RelationshipType:
            errors.append(ValidationError(
                code=RELATIONSHIP_INVALID_TYPE,
                message=f"Invalid relationship type: {relationship.relationship_type}",
                severity=ValidationSeverity.ERROR,
                entity_id=relationship.id,
                entity_type="Relationship",
            ))
    
    def _validate_metadata(self, relationship: Relationship, errors: list[ValidationError], warnings: list[ValidationError]) -> None:
        """Validate relationship metadata.
        
        Args:
            relationship: The relationship to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate metadata type
        if not isinstance(relationship.metadata, dict):
            errors.append(ValidationError(
                code=RELATIONSHIP_INVALID_METADATA,
                message="Relationship metadata must be a dictionary",
                severity=ValidationSeverity.ERROR,
                entity_id=relationship.id,
                entity_type="Relationship",
            ))
            return
        
        # Check for empty metadata
        if not self._config.allow_empty_metadata and not relationship.metadata:
            warnings.append(ValidationError(
                code=RELATIONSHIP_INVALID_METADATA,
                message="Relationship metadata is empty",
                severity=ValidationSeverity.WARNING,
                entity_id=relationship.id,
                entity_type="Relationship",
            ))