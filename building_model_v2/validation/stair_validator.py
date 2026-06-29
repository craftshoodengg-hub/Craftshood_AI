"""Stair validator for Building Model v2.

Validates stair entities for geometric and property correctness.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from ..entities_stair import Stair
from ..types import StairType
from .validation_error import ValidationError
from .validation_result import ValidationResult
from .validation_severity import ValidationSeverity
from .validator import Validator


# Validation error codes
STAIR_INVALID_GEOMETRY: Final[str] = "STAIR_INVALID_GEOMETRY"
STAIR_ZERO_LENGTH: Final[str] = "STAIR_ZERO_LENGTH"
STAIR_INVALID_WIDTH: Final[str] = "STAIR_INVALID_WIDTH"
STAIR_INVALID_STEP_COUNT: Final[str] = "STAIR_INVALID_STEP_COUNT"
STAIR_INVALID_RISER_HEIGHT: Final[str] = "STAIR_INVALID_RISER_HEIGHT"
STAIR_INVALID_TREAD_DEPTH: Final[str] = "STAIR_INVALID_TREAD_DEPTH"
STAIR_INVALID_TYPE: Final[str] = "STAIR_INVALID_TYPE"
STAIR_INVALID_DIRECTION: Final[str] = "STAIR_INVALID_DIRECTION"
STAIR_MISSING_FLOOR: Final[str] = "STAIR_MISSING_FLOOR"
STAIR_MISSING_CONNECTIONS: Final[str] = "STAIR_MISSING_CONNECTIONS"


# Valid direction values
VALID_DIRECTIONS: Final[frozenset[str]] = frozenset({"up", "down", "both"})


@dataclass(slots=True)
class StairValidationConfig:
    """Configuration for stair validation thresholds.
    
    Attributes:
        min_width: Minimum acceptable stair width in feet.
        max_width: Maximum acceptable stair width in feet.
        min_step_count: Minimum acceptable number of steps.
        max_step_count: Maximum acceptable number of steps.
        min_riser_height: Minimum acceptable riser height in feet.
        max_riser_height: Maximum acceptable riser height in feet.
        min_tread_depth: Minimum acceptable tread depth in feet.
        max_tread_depth: Maximum acceptable tread depth in feet.
        allow_unknown_type: Whether StairType.UNKNOWN is allowed.
        require_floor_connections: Whether connects_floors must be set.
    """
    
    min_width: float = 2.5
    max_width: float = 6.0
    min_step_count: int = 3
    max_step_count: int = 50
    min_riser_height: float = 0.5
    max_riser_height: float = 0.85
    min_tread_depth: float = 0.75
    max_tread_depth: float = 1.25
    allow_unknown_type: bool = True
    require_floor_connections: bool = True


class StairValidator(Validator):
    """Validates Stair entities.
    
    Checks geometry validity, dimensions, properties, and connectivity.
    
    Attributes:
        config: Validation thresholds configuration.
    """
    
    def __init__(self, config: StairValidationConfig | None = None) -> None:
        """Initialize the stair validator.
        
        Args:
            config: Optional validation configuration. Uses defaults if not provided.
        """
        self._config = config or StairValidationConfig()
    
    @property
    def config(self) -> StairValidationConfig:
        """Get the validation configuration.
        
        Returns:
            The current validation configuration.
        """
        return self._config
    
    def validate(self, entity: Any) -> ValidationResult:
        """Validate a Stair entity.
        
        Args:
            entity: The entity to validate. Must be a Stair instance.
            
        Returns:
            ValidationResult containing any issues found.
        """
        if not isinstance(entity, Stair):
            result = ValidationResult.create()
            result.add_error(ValidationError(
                code="STAIR_INVALID_ENTITY",
                message=f"Expected Stair entity, got {type(entity).__name__}",
                severity=ValidationSeverity.ERROR,
            ))
            return result
        
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []
        infos: list[ValidationError] = []
        
        # Validate geometry
        self._validate_geometry(entity, errors)
        
        # Validate dimensions
        self._validate_dimensions(entity, errors, warnings)
        
        # Validate properties
        self._validate_properties(entity, errors, warnings)
        
        # Validate connectivity
        self._validate_connectivity(entity, errors, warnings)
        
        return ValidationResult(
            errors=errors,
            warnings=warnings,
            infos=infos,
        )
    
    def _validate_geometry(self, stair: Stair, errors: list[ValidationError]) -> None:
        """Validate stair geometry.
        
        Args:
            stair: The stair to validate.
            errors: List to append errors to.
        """
        geometry = stair.geometry
        
        # Check if geometry exists (is not empty)
        if geometry.is_empty:
            errors.append(ValidationError(
                code=STAIR_INVALID_GEOMETRY,
                message="Stair geometry is empty",
                severity=ValidationSeverity.ERROR,
                entity_id=stair.id,
                entity_type="Stair",
            ))
            return
        
        # Check minimum points (at least 2 for a line)
        coords = list(geometry.coords)
        if len(coords) < 2:
            errors.append(ValidationError(
                code=STAIR_INVALID_GEOMETRY,
                message=f"Stair geometry has insufficient points: {len(coords)} (minimum 2)",
                severity=ValidationSeverity.ERROR,
                entity_id=stair.id,
                entity_type="Stair",
            ))
            return
        
        # Check for distinct points (non-zero length)
        if geometry.length <= 0:
            errors.append(ValidationError(
                code=STAIR_ZERO_LENGTH,
                message="Stair has zero length",
                severity=ValidationSeverity.ERROR,
                entity_id=stair.id,
                entity_type="Stair",
            ))
            return
        
        # Check if line is valid
        if not geometry.is_valid:
            errors.append(ValidationError(
                code=STAIR_INVALID_GEOMETRY,
                message="Stair geometry is invalid",
                severity=ValidationSeverity.ERROR,
                entity_id=stair.id,
                entity_type="Stair",
            ))
    
    def _validate_dimensions(
        self,
        stair: Stair,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate stair dimensions.
        
        Args:
            stair: The stair to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Skip dimension checks if geometry is invalid
        if stair.geometry.is_empty or stair.geometry.length <= 0:
            return
        
        # Validate width
        if stair.width <= 0:
            errors.append(ValidationError(
                code=STAIR_INVALID_WIDTH,
                message=f"Stair width must be positive, got {stair.width}",
                severity=ValidationSeverity.ERROR,
                entity_id=stair.id,
                entity_type="Stair",
                metadata={"width": stair.width},
            ))
        elif stair.width < self._config.min_width:
            errors.append(ValidationError(
                code=STAIR_INVALID_WIDTH,
                message=f"Stair width {stair.width} is below minimum {self._config.min_width}",
                severity=ValidationSeverity.ERROR,
                entity_id=stair.id,
                entity_type="Stair",
                metadata={"width": stair.width},
            ))
        elif stair.width > self._config.max_width:
            warnings.append(ValidationError(
                code=STAIR_INVALID_WIDTH,
                message=f"Stair width {stair.width} exceeds recommended maximum {self._config.max_width}",
                severity=ValidationSeverity.WARNING,
                entity_id=stair.id,
                entity_type="Stair",
                metadata={"width": stair.width},
            ))
        
        # Validate step count
        if stair.num_steps is not None:
            if stair.num_steps <= 0:
                errors.append(ValidationError(
                    code=STAIR_INVALID_STEP_COUNT,
                    message=f"Stair step count must be positive, got {stair.num_steps}",
                    severity=ValidationSeverity.ERROR,
                    entity_id=stair.id,
                    entity_type="Stair",
                    metadata={"num_steps": stair.num_steps},
                ))
            elif stair.num_steps < self._config.min_step_count:
                errors.append(ValidationError(
                    code=STAIR_INVALID_STEP_COUNT,
                    message=f"Stair step count {stair.num_steps} is below minimum {self._config.min_step_count}",
                    severity=ValidationSeverity.ERROR,
                    entity_id=stair.id,
                    entity_type="Stair",
                    metadata={"num_steps": stair.num_steps},
                ))
            elif stair.num_steps > self._config.max_step_count:
                warnings.append(ValidationError(
                    code=STAIR_INVALID_STEP_COUNT,
                    message=f"Stair step count {stair.num_steps} exceeds recommended maximum {self._config.max_step_count}",
                    severity=ValidationSeverity.WARNING,
                    entity_id=stair.id,
                    entity_type="Stair",
                    metadata={"num_steps": stair.num_steps},
                ))
    
    def _validate_properties(
        self,
        stair: Stair,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate stair properties.
        
        Args:
            stair: The stair to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate stair type
        if stair.stair_type == StairType.UNKNOWN:
            if self._config.allow_unknown_type:
                warnings.append(ValidationError(
                    code=STAIR_INVALID_TYPE,
                    message="Stair has UNKNOWN type",
                    severity=ValidationSeverity.WARNING,
                    entity_id=stair.id,
                    entity_type="Stair",
                ))
            else:
                errors.append(ValidationError(
                    code=STAIR_INVALID_TYPE,
                    message="Stair has UNKNOWN type",
                    severity=ValidationSeverity.ERROR,
                    entity_id=stair.id,
                    entity_type="Stair",
                ))
        
        # Validate direction
        if stair.direction not in VALID_DIRECTIONS:
            errors.append(ValidationError(
                code=STAIR_INVALID_DIRECTION,
                message=f"Stair direction '{stair.direction}' is invalid. Must be one of: up, down, both",
                severity=ValidationSeverity.ERROR,
                entity_id=stair.id,
                entity_type="Stair",
                metadata={"direction": stair.direction},
            ))
        
        # Validate floor ID
        if not stair.floor_id:
            errors.append(ValidationError(
                code=STAIR_MISSING_FLOOR,
                message="Stair must belong to a floor",
                severity=ValidationSeverity.ERROR,
                entity_id=stair.id,
                entity_type="Stair",
            ))
    
    def _validate_connectivity(
        self,
        stair: Stair,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate stair connectivity metadata.
        
        Args:
            stair: The stair to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate floor connections (configurable)
        if self._config.require_floor_connections:
            if not stair.connects_floors or (stair.connects_floors[0] is None and stair.connects_floors[1] is None):
                errors.append(ValidationError(
                    code=STAIR_MISSING_CONNECTIONS,
                    message="Stair must connect at least one floor",
                    severity=ValidationSeverity.ERROR,
                    entity_id=stair.id,
                    entity_type="Stair",
                ))
            elif stair.connects_floors[0] is None or stair.connects_floors[1] is None:
                warnings.append(ValidationError(
                    code=STAIR_MISSING_CONNECTIONS,
                    message="Stair should connect two floors for proper vertical circulation",
                    severity=ValidationSeverity.WARNING,
                    entity_id=stair.id,
                    entity_type="Stair",
                ))