"""Column validator for Building Model v2.

Validates column entities for geometric and property correctness.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Final

from ..base import Point2D
from ..entities_column import Column
from ..types import ColumnType
from .validation_error import ValidationError
from .validation_result import ValidationResult
from .validation_severity import ValidationSeverity
from .validator import Validator


# Validation error codes
COLUMN_INVALID_GEOMETRY: Final[str] = "COLUMN_INVALID_GEOMETRY"
COLUMN_INVALID_WIDTH: Final[str] = "COLUMN_INVALID_WIDTH"
COLUMN_INVALID_DEPTH: Final[str] = "COLUMN_INVALID_DEPTH"
COLUMN_INVALID_HEIGHT: Final[str] = "COLUMN_INVALID_HEIGHT"
COLUMN_INVALID_TYPE: Final[str] = "COLUMN_INVALID_TYPE"
COLUMN_MISSING_FLOOR: Final[str] = "COLUMN_MISSING_FLOOR"


@dataclass(slots=True)
class ColumnValidationConfig:
    """Configuration for column validation thresholds.
    
    Attributes:
        min_width: Minimum acceptable column width/diameter in feet.
        max_width: Maximum acceptable column width/diameter in feet.
        min_depth: Minimum acceptable column depth in feet.
        max_depth: Maximum acceptable column depth in feet.
        min_height: Minimum acceptable column height in feet.
        max_height: Maximum acceptable column height in feet.
        allow_unknown_type: Whether ColumnType.UNKNOWN is allowed.
        require_floor_id: Whether floor_id must be present.
    """
    
    min_width: float = 0.5
    max_width: float = 4.0
    min_depth: float = 0.5
    max_depth: float = 4.0
    min_height: float = 6.0
    max_height: float = 20.0
    allow_unknown_type: bool = True
    require_floor_id: bool = True


class ColumnValidator(Validator):
    """Validates Column entities.
    
    Checks geometry validity, dimensions, properties, and placement.
    
    Attributes:
        config: Validation thresholds configuration.
    """
    
    def __init__(self, config: ColumnValidationConfig | None = None) -> None:
        """Initialize the column validator.
        
        Args:
            config: Optional validation configuration. Uses defaults if not provided.
        """
        self._config = config or ColumnValidationConfig()
    
    @property
    def config(self) -> ColumnValidationConfig:
        """Get the validation configuration.
        
        Returns:
            The current validation configuration.
        """
        return self._config
    
    def validate(self, entity: Any) -> ValidationResult:
        """Validate a Column entity.
        
        Args:
            entity: The entity to validate. Must be a Column instance.
            
        Returns:
            ValidationResult containing any issues found.
        """
        if not isinstance(entity, Column):
            result = ValidationResult.create()
            result.add_error(ValidationError(
                code="COLUMN_INVALID_ENTITY",
                message=f"Expected Column entity, got {type(entity).__name__}",
                severity=ValidationSeverity.ERROR,
            ))
            return result
        
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []
        infos: list[ValidationError] = []
        
        # Validate geometry (location point)
        self._validate_geometry(entity, errors)
        
        # Validate dimensions
        self._validate_dimensions(entity, errors, warnings)
        
        # Validate properties
        self._validate_properties(entity, errors, warnings)
        
        return ValidationResult(
            errors=errors,
            warnings=warnings,
            infos=infos,
        )
    
    def _validate_geometry(self, column: Column, errors: list[ValidationError]) -> None:
        """Validate column geometry (location point).
        
        Args:
            column: The column to validate.
            errors: List to append errors to.
        """
        location = column.geometry
        
        # Check if location is valid
        if location is None:
            errors.append(ValidationError(
                code=COLUMN_INVALID_GEOMETRY,
                message="Column location is missing",
                severity=ValidationSeverity.ERROR,
                entity_id=column.id,
                entity_type="Column",
            ))
            return
        
        # Check for valid type
        if not isinstance(location, Point2D):
            errors.append(ValidationError(
                code=COLUMN_INVALID_GEOMETRY,
                message="Column location has invalid type",
                severity=ValidationSeverity.ERROR,
                entity_id=column.id,
                entity_type="Column",
            ))
            return
        
        # Check for NaN or infinite coordinates
        if math.isnan(location.x) or math.isnan(location.y):
            errors.append(ValidationError(
                code=COLUMN_INVALID_GEOMETRY,
                message="Column location contains NaN coordinates",
                severity=ValidationSeverity.ERROR,
                entity_id=column.id,
                entity_type="Column",
            ))
            return
        
        if math.isinf(location.x) or math.isinf(location.y):
            errors.append(ValidationError(
                code=COLUMN_INVALID_GEOMETRY,
                message="Column location contains infinite coordinates",
                severity=ValidationSeverity.ERROR,
                entity_id=column.id,
                entity_type="Column",
            ))
    
    def _validate_dimensions(
        self,
        column: Column,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate column dimensions.
        
        Args:
            column: The column to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate size (width/diameter)
        if column.size <= 0:
            errors.append(ValidationError(
                code=COLUMN_INVALID_WIDTH,
                message=f"Column size must be positive, got {column.size}",
                severity=ValidationSeverity.ERROR,
                entity_id=column.id,
                entity_type="Column",
                metadata={"size": column.size},
            ))
        elif column.size < self._config.min_width:
            errors.append(ValidationError(
                code=COLUMN_INVALID_WIDTH,
                message=f"Column size {column.size} is below minimum {self._config.min_width}",
                severity=ValidationSeverity.ERROR,
                entity_id=column.id,
                entity_type="Column",
                metadata={"size": column.size},
            ))
        elif column.size > self._config.max_width:
            warnings.append(ValidationError(
                code=COLUMN_INVALID_WIDTH,
                message=f"Column size {column.size} exceeds recommended maximum {self._config.max_width}",
                severity=ValidationSeverity.WARNING,
                entity_id=column.id,
                entity_type="Column",
                metadata={"size": column.size},
            ))
        
        # Validate height
        if column.height is not None:
            if column.height <= 0:
                errors.append(ValidationError(
                    code=COLUMN_INVALID_HEIGHT,
                    message=f"Column height must be positive, got {column.height}",
                    severity=ValidationSeverity.ERROR,
                    entity_id=column.id,
                    entity_type="Column",
                    metadata={"height": column.height},
                ))
            elif column.height < self._config.min_height:
                errors.append(ValidationError(
                    code=COLUMN_INVALID_HEIGHT,
                    message=f"Column height {column.height} is below minimum {self._config.min_height}",
                    severity=ValidationSeverity.ERROR,
                    entity_id=column.id,
                    entity_type="Column",
                    metadata={"height": column.height},
                ))
            elif column.height > self._config.max_height:
                warnings.append(ValidationError(
                    code=COLUMN_INVALID_HEIGHT,
                    message=f"Column height {column.height} exceeds recommended maximum {self._config.max_height}",
                    severity=ValidationSeverity.WARNING,
                    entity_id=column.id,
                    entity_type="Column",
                    metadata={"height": column.height},
                ))
    
    def _validate_properties(
        self,
        column: Column,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate column properties.
        
        Args:
            column: The column to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate column type
        if column.column_type == ColumnType.UNKNOWN:
            if self._config.allow_unknown_type:
                warnings.append(ValidationError(
                    code=COLUMN_INVALID_TYPE,
                    message="Column has UNKNOWN type",
                    severity=ValidationSeverity.WARNING,
                    entity_id=column.id,
                    entity_type="Column",
                ))
            else:
                errors.append(ValidationError(
                    code=COLUMN_INVALID_TYPE,
                    message="Column has UNKNOWN type",
                    severity=ValidationSeverity.ERROR,
                    entity_id=column.id,
                    entity_type="Column",
                ))
        
        # Validate floor ID (configurable)
        if self._config.require_floor_id and not column.floor_id:
            errors.append(ValidationError(
                code=COLUMN_MISSING_FLOOR,
                message="Column must belong to a floor",
                severity=ValidationSeverity.ERROR,
                entity_id=column.id,
                entity_type="Column",
            ))