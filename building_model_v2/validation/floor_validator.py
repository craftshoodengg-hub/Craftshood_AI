"""Floor validator for Building Model v2.

Validates floor entities for metadata, dimensions, and collection correctness.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Final

from ..entities_floor import Floor
from ..types import FloorType
from .validation_error import ValidationError
from .validation_result import ValidationResult
from .validation_severity import ValidationSeverity
from .validator import Validator


# Validation error codes
FLOOR_EMPTY_NAME: Final[str] = "FLOOR_EMPTY_NAME"
FLOOR_INVALID_LEVEL: Final[str] = "FLOOR_INVALID_LEVEL"
FLOOR_INVALID_HEIGHT: Final[str] = "FLOOR_INVALID_HEIGHT"
FLOOR_INVALID_SLAB: Final[str] = "FLOOR_INVALID_SLAB"
FLOOR_INVALID_TYPE: Final[str] = "FLOOR_INVALID_TYPE"
FLOOR_EMPTY_COLLECTION: Final[str] = "FLOOR_EMPTY_COLLECTION"


@dataclass(slots=True)
class FloorValidationConfig:
    """Configuration for floor validation thresholds.
    
    Attributes:
        min_floor_height: Minimum acceptable floor height in feet.
        max_floor_height: Maximum acceptable floor height in feet.
        min_slab_thickness: Minimum acceptable slab thickness in feet.
        max_slab_thickness: Maximum acceptable slab thickness in feet.
        allow_negative_levels: Whether negative levels (basements) are allowed.
        allow_empty_floor: Whether floors with no rooms are allowed.
    """
    
    min_floor_height: float = 6.0
    max_floor_height: float = 30.0
    min_slab_thickness: float = 0.25
    max_slab_thickness: float = 3.0
    allow_negative_levels: bool = True
    allow_empty_floor: bool = True


class FloorValidator(Validator):
    """Validates Floor entities.
    
    Checks metadata, dimensions, and collection integrity.
    
    Attributes:
        config: Validation thresholds configuration.
    """
    
    def __init__(self, config: FloorValidationConfig | None = None) -> None:
        """Initialize the floor validator.
        
        Args:
            config: Optional validation configuration. Uses defaults if not provided.
        """
        self._config = config or FloorValidationConfig()
    
    @property
    def config(self) -> FloorValidationConfig:
        """Get the validation configuration.
        
        Returns:
            The current validation configuration.
        """
        return self._config
    
    def validate(self, entity: Any) -> ValidationResult:
        """Validate a Floor entity.
        
        Args:
            entity: The entity to validate. Must be a Floor instance.
            
        Returns:
            ValidationResult containing any issues found.
        """
        if not isinstance(entity, Floor):
            result = ValidationResult.create()
            result.add_error(ValidationError(
                code="FLOOR_INVALID_ENTITY",
                message=f"Expected Floor entity, got {type(entity).__name__}",
                severity=ValidationSeverity.ERROR,
            ))
            return result
        
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []
        infos: list[ValidationError] = []
        
        # Validate floor properties
        self._validate_properties(entity, errors, warnings)
        
        # Validate dimensions
        self._validate_dimensions(entity, errors, warnings)
        
        # Validate collections
        self._validate_collections(entity, errors, warnings)
        
        return ValidationResult(
            errors=errors,
            warnings=warnings,
            infos=infos,
        )
    
    def _validate_properties(self, floor: Floor, errors: list[ValidationError], warnings: list[ValidationError]) -> None:
        """Validate floor properties.
        
        Args:
            floor: The floor to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate name
        if not floor.name or not floor.name.strip():
            errors.append(ValidationError(
                code=FLOOR_EMPTY_NAME,
                message="Floor name is empty",
                severity=ValidationSeverity.ERROR,
                entity_id=floor.id,
                entity_type="Floor",
            ))
        
        # Validate level
        if not self._config.allow_negative_levels and floor.level < 0:
            errors.append(ValidationError(
                code=FLOOR_INVALID_LEVEL,
                message=f"Floor level {floor.level} is negative and negative levels are not allowed",
                severity=ValidationSeverity.ERROR,
                entity_id=floor.id,
                entity_type="Floor",
                metadata={"level": floor.level},
            ))
        
        # Validate elevation is finite
        if math.isnan(floor.elevation) or math.isinf(floor.elevation):
            errors.append(ValidationError(
                code=FLOOR_INVALID_LEVEL,
                message=f"Floor elevation is invalid: {floor.elevation}",
                severity=ValidationSeverity.ERROR,
                entity_id=floor.id,
                entity_type="Floor",
                metadata={"elevation": floor.elevation},
            ))
        
        # Validate floor type
        if floor.floor_type == FloorType.UNKNOWN:
            warnings.append(ValidationError(
                code=FLOOR_INVALID_TYPE,
                message="Floor has UNKNOWN type",
                severity=ValidationSeverity.WARNING,
                entity_id=floor.id,
                entity_type="Floor",
            ))
    
    def _validate_dimensions(self, floor: Floor, errors: list[ValidationError], warnings: list[ValidationError]) -> None:
        """Validate floor dimensions.
        
        Args:
            floor: The floor to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate floor height
        if floor.floor_height <= 0:
            errors.append(ValidationError(
                code=FLOOR_INVALID_HEIGHT,
                message=f"Floor height must be positive, got {floor.floor_height}",
                severity=ValidationSeverity.ERROR,
                entity_id=floor.id,
                entity_type="Floor",
                metadata={"floor_height": floor.floor_height},
            ))
        elif floor.floor_height < self._config.min_floor_height:
            errors.append(ValidationError(
                code=FLOOR_INVALID_HEIGHT,
                message=f"Floor height {floor.floor_height} is below minimum {self._config.min_floor_height}",
                severity=ValidationSeverity.ERROR,
                entity_id=floor.id,
                entity_type="Floor",
                metadata={"floor_height": floor.floor_height},
            ))
        elif floor.floor_height > self._config.max_floor_height:
            warnings.append(ValidationError(
                code=FLOOR_INVALID_HEIGHT,
                message=f"Floor height {floor.floor_height} exceeds recommended maximum {self._config.max_floor_height}",
                severity=ValidationSeverity.WARNING,
                entity_id=floor.id,
                entity_type="Floor",
                metadata={"floor_height": floor.floor_height},
            ))
        
        # Validate slab thickness
        if floor.slab_thickness <= 0:
            errors.append(ValidationError(
                code=FLOOR_INVALID_SLAB,
                message=f"Slab thickness must be positive, got {floor.slab_thickness}",
                severity=ValidationSeverity.ERROR,
                entity_id=floor.id,
                entity_type="Floor",
                metadata={"slab_thickness": floor.slab_thickness},
            ))
        elif floor.slab_thickness < self._config.min_slab_thickness:
            errors.append(ValidationError(
                code=FLOOR_INVALID_SLAB,
                message=f"Slab thickness {floor.slab_thickness} is below minimum {self._config.min_slab_thickness}",
                severity=ValidationSeverity.ERROR,
                entity_id=floor.id,
                entity_type="Floor",
                metadata={"slab_thickness": floor.slab_thickness},
            ))
        elif floor.slab_thickness > self._config.max_slab_thickness:
            warnings.append(ValidationError(
                code=FLOOR_INVALID_SLAB,
                message=f"Slab thickness {floor.slab_thickness} exceeds recommended maximum {self._config.max_slab_thickness}",
                severity=ValidationSeverity.WARNING,
                entity_id=floor.id,
                entity_type="Floor",
                metadata={"slab_thickness": floor.slab_thickness},
            ))
    
    def _validate_collections(self, floor: Floor, errors: list[ValidationError], warnings: list[ValidationError]) -> None:
        """Validate floor collections.
        
        Args:
            floor: The floor to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Check for empty floor (no rooms)
        if not self._config.allow_empty_floor and not floor.room_ids:
            errors.append(ValidationError(
                code=FLOOR_EMPTY_COLLECTION,
                message="Floor has no rooms and empty floors are not allowed",
                severity=ValidationSeverity.ERROR,
                entity_id=floor.id,
                entity_type="Floor",
                metadata={"collection": "room_ids"},
            ))
        
        # Check for duplicate IDs within collections (shouldn't happen with frozenset, but check anyway)
        # This is more of a sanity check for data integrity
        if len(floor.room_ids) != len(set(floor.room_ids)):
            warnings.append(ValidationError(
                code=FLOOR_EMPTY_COLLECTION,
                message="Floor contains duplicate room IDs",
                severity=ValidationSeverity.WARNING,
                entity_id=floor.id,
                entity_type="Floor",
            ))
        
        if len(floor.wall_ids) != len(set(floor.wall_ids)):
            warnings.append(ValidationError(
                code=FLOOR_EMPTY_COLLECTION,
                message="Floor contains duplicate wall IDs",
                severity=ValidationSeverity.WARNING,
                entity_id=floor.id,
                entity_type="Floor",
            ))
        
        if len(floor.column_ids) != len(set(floor.column_ids)):
            warnings.append(ValidationError(
                code=FLOOR_EMPTY_COLLECTION,
                message="Floor contains duplicate column IDs",
                severity=ValidationSeverity.WARNING,
                entity_id=floor.id,
                entity_type="Floor",
            ))
        
        if len(floor.stair_ids) != len(set(floor.stair_ids)):
            warnings.append(ValidationError(
                code=FLOOR_EMPTY_COLLECTION,
                message="Floor contains duplicate stair IDs",
                severity=ValidationSeverity.WARNING,
                entity_id=floor.id,
                entity_type="Floor",
            ))