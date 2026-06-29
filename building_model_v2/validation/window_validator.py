"""Window validator for Building Model v2.

Validates window entities for geometric and property correctness.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Any, Final

from ..base import Point2D
from ..entities_opening import Window
from ..types import WindowType
from .validation_error import ValidationError
from .validation_result import ValidationResult
from .validation_severity import ValidationSeverity
from .validator import Validator


# Validation error codes
WINDOW_INVALID_GEOMETRY: Final[str] = "WINDOW_INVALID_GEOMETRY"
WINDOW_INVALID_WIDTH: Final[str] = "WINDOW_INVALID_WIDTH"
WINDOW_INVALID_HEIGHT: Final[str] = "WINDOW_INVALID_HEIGHT"
WINDOW_INVALID_TYPE: Final[str] = "WINDOW_INVALID_TYPE"
WINDOW_INVALID_SILL_HEIGHT: Final[str] = "WINDOW_INVALID_SILL_HEIGHT"
WINDOW_MISSING_WALL: Final[str] = "WINDOW_MISSING_WALL"
WINDOW_MISSING_FLOOR: Final[str] = "WINDOW_MISSING_FLOOR"


@dataclass(slots=True)
class WindowValidationConfig:
    """Configuration for window validation thresholds.
    
    Attributes:
        min_width: Minimum acceptable window width in feet.
        max_width: Maximum acceptable window width in feet.
        min_height: Minimum acceptable window height in feet.
        max_height: Maximum acceptable window height in feet.
        min_sill_height: Minimum acceptable sill height in feet.
        max_sill_height: Maximum acceptable sill height in feet.
        allow_unknown_type: Whether WindowType.UNKNOWN is allowed.
        require_wall_id: Whether wall_id must be present.
    """
    
    min_width: float = 1.0
    max_width: float = 8.0
    min_height: float = 1.0
    max_height: float = 6.0
    min_sill_height: float = 0.0
    max_sill_height: float = 10.0
    allow_unknown_type: bool = True
    require_wall_id: bool = True


class WindowValidator(Validator):
    """Validates Window entities.
    
    Checks geometry validity, dimensions, properties, and placement.
    
    Attributes:
        config: Validation thresholds configuration.
    """
    
    def __init__(self, config: WindowValidationConfig | None = None) -> None:
        """Initialize the window validator.
        
        Args:
            config: Optional validation configuration. Uses defaults if not provided.
        """
        self._config = config or WindowValidationConfig()
    
    @property
    def config(self) -> WindowValidationConfig:
        """Get the validation configuration.
        
        Returns:
            The current validation configuration.
        """
        return self._config
    
    def validate(self, entity: Any) -> ValidationResult:
        """Validate a Window entity.
        
        Args:
            entity: The entity to validate. Must be a Window instance.
            
        Returns:
            ValidationResult containing any issues found.
        """
        if not isinstance(entity, Window):
            result = ValidationResult.create()
            result.add_error(ValidationError(
                code="WINDOW_INVALID_ENTITY",
                message=f"Expected Window entity, got {type(entity).__name__}",
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
        
        # Validate placement
        self._validate_placement(entity, errors, warnings)
        
        return ValidationResult(
            errors=errors,
            warnings=warnings,
            infos=infos,
        )
    
    def _validate_geometry(self, window: Window, errors: list[ValidationError]) -> None:
        """Validate window geometry (location point).
        
        Args:
            window: The window to validate.
            errors: List to append errors to.
        """
        location = window.location
        
        # Check if location is valid (not None and has valid coordinates)
        if location is None:
            errors.append(ValidationError(
                code=WINDOW_INVALID_GEOMETRY,
                message="Window location is missing",
                severity=ValidationSeverity.ERROR,
                entity_id=window.id,
                entity_type="Window",
            ))
            return
        
        # Check for valid coordinates
        if not isinstance(location, Point2D):
            errors.append(ValidationError(
                code=WINDOW_INVALID_GEOMETRY,
                message="Window location has invalid type",
                severity=ValidationSeverity.ERROR,
                entity_id=window.id,
                entity_type="Window",
            ))
            return
        
        # Check for NaN or infinite coordinates
        if math.isnan(location.x) or math.isnan(location.y):
            errors.append(ValidationError(
                code=WINDOW_INVALID_GEOMETRY,
                message="Window location contains NaN coordinates",
                severity=ValidationSeverity.ERROR,
                entity_id=window.id,
                entity_type="Window",
            ))
            return
        
        if math.isinf(location.x) or math.isinf(location.y):
            errors.append(ValidationError(
                code=WINDOW_INVALID_GEOMETRY,
                message="Window location contains infinite coordinates",
                severity=ValidationSeverity.ERROR,
                entity_id=window.id,
                entity_type="Window",
            ))
    
    def _validate_dimensions(
        self,
        window: Window,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate window dimensions.
        
        Args:
            window: The window to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate width
        if window.width <= 0:
            errors.append(ValidationError(
                code=WINDOW_INVALID_WIDTH,
                message=f"Window width must be positive, got {window.width}",
                severity=ValidationSeverity.ERROR,
                entity_id=window.id,
                entity_type="Window",
                metadata={"width": window.width},
            ))
        elif window.width < self._config.min_width:
            errors.append(ValidationError(
                code=WINDOW_INVALID_WIDTH,
                message=f"Window width {window.width} is below minimum {self._config.min_width}",
                severity=ValidationSeverity.ERROR,
                entity_id=window.id,
                entity_type="Window",
                metadata={"width": window.width},
            ))
        elif window.width > self._config.max_width:
            warnings.append(ValidationError(
                code=WINDOW_INVALID_WIDTH,
                message=f"Window width {window.width} exceeds recommended maximum {self._config.max_width}",
                severity=ValidationSeverity.WARNING,
                entity_id=window.id,
                entity_type="Window",
                metadata={"width": window.width},
            ))
        
        # Validate height
        if window.height is not None:
            if window.height <= 0:
                errors.append(ValidationError(
                    code=WINDOW_INVALID_HEIGHT,
                    message=f"Window height must be positive, got {window.height}",
                    severity=ValidationSeverity.ERROR,
                    entity_id=window.id,
                    entity_type="Window",
                    metadata={"height": window.height},
                ))
            elif window.height < self._config.min_height:
                errors.append(ValidationError(
                    code=WINDOW_INVALID_HEIGHT,
                    message=f"Window height {window.height} is below minimum {self._config.min_height}",
                    severity=ValidationSeverity.ERROR,
                    entity_id=window.id,
                    entity_type="Window",
                    metadata={"height": window.height},
                ))
            elif window.height > self._config.max_height:
                warnings.append(ValidationError(
                    code=WINDOW_INVALID_HEIGHT,
                    message=f"Window height {window.height} exceeds recommended maximum {self._config.max_height}",
                    severity=ValidationSeverity.WARNING,
                    entity_id=window.id,
                    entity_type="Window",
                    metadata={"height": window.height},
                ))
        
        # Validate sill height
        if window.sill_height is not None:
            if window.sill_height < 0:
                errors.append(ValidationError(
                    code=WINDOW_INVALID_SILL_HEIGHT,
                    message=f"Window sill height must be non-negative, got {window.sill_height}",
                    severity=ValidationSeverity.ERROR,
                    entity_id=window.id,
                    entity_type="Window",
                    metadata={"sill_height": window.sill_height},
                ))
            elif window.sill_height < self._config.min_sill_height:
                errors.append(ValidationError(
                    code=WINDOW_INVALID_SILL_HEIGHT,
                    message=f"Window sill height {window.sill_height} is below minimum {self._config.min_sill_height}",
                    severity=ValidationSeverity.ERROR,
                    entity_id=window.id,
                    entity_type="Window",
                    metadata={"sill_height": window.sill_height},
                ))
            elif window.sill_height > self._config.max_sill_height:
                warnings.append(ValidationError(
                    code=WINDOW_INVALID_SILL_HEIGHT,
                    message=f"Window sill height {window.sill_height} exceeds recommended maximum {self._config.max_sill_height}",
                    severity=ValidationSeverity.WARNING,
                    entity_id=window.id,
                    entity_type="Window",
                    metadata={"sill_height": window.sill_height},
                ))
    
    def _validate_properties(
        self,
        window: Window,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate window properties.
        
        Args:
            window: The window to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate window type
        if window.window_type == WindowType.UNKNOWN:
            if self._config.allow_unknown_type:
                warnings.append(ValidationError(
                    code=WINDOW_INVALID_TYPE,
                    message="Window has UNKNOWN type",
                    severity=ValidationSeverity.WARNING,
                    entity_id=window.id,
                    entity_type="Window",
                ))
            else:
                errors.append(ValidationError(
                    code=WINDOW_INVALID_TYPE,
                    message="Window has UNKNOWN type",
                    severity=ValidationSeverity.ERROR,
                    entity_id=window.id,
                    entity_type="Window",
                ))
        
        # Validate floor ID
        if not window.floor_id:
            errors.append(ValidationError(
                code=WINDOW_MISSING_FLOOR,
                message="Window must belong to a floor",
                severity=ValidationSeverity.ERROR,
                entity_id=window.id,
                entity_type="Window",
            ))
    
    def _validate_placement(
        self,
        window: Window,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate window placement references.
        
        Args:
            window: The window to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate wall ID (configurable)
        if self._config.require_wall_id and not window.wall_id:
            errors.append(ValidationError(
                code=WINDOW_MISSING_WALL,
                message="Window must be associated with a wall",
                severity=ValidationSeverity.ERROR,
                entity_id=window.id,
                entity_type="Window",
            ))