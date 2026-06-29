"""Door validator for Building Model v2.

Validates door entities for geometric and property correctness.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from ..base import Point2D
from ..entities_opening import Door
from ..types import DoorType
from .validation_error import ValidationError
from .validation_result import ValidationResult
from .validation_severity import ValidationSeverity
from .validator import Validator


# Validation error codes
DOOR_INVALID_GEOMETRY: Final[str] = "DOOR_INVALID_GEOMETRY"
DOOR_INVALID_WIDTH: Final[str] = "DOOR_INVALID_WIDTH"
DOOR_INVALID_HEIGHT: Final[str] = "DOOR_INVALID_HEIGHT"
DOOR_INVALID_TYPE: Final[str] = "DOOR_INVALID_TYPE"
DOOR_MISSING_WALL: Final[str] = "DOOR_MISSING_WALL"
DOOR_MISSING_FLOOR: Final[str] = "DOOR_MISSING_FLOOR"
DOOR_MISSING_ROOM_CONNECTION: Final[str] = "DOOR_MISSING_ROOM_CONNECTION"


@dataclass(slots=True)
class DoorValidationConfig:
    """Configuration for door validation thresholds.
    
    Attributes:
        min_width: Minimum acceptable door width in feet.
        max_width: Maximum acceptable door width in feet.
        min_height: Minimum acceptable door height in feet.
        max_height: Maximum acceptable door height in feet.
        allow_unknown_type: Whether DoorType.UNKNOWN is allowed.
        require_wall_id: Whether wall_id must be present.
        require_room_connection: Whether at least one room_id must be present.
    """
    
    min_width: float = 2.0
    max_width: float = 6.0
    min_height: float = 6.0
    max_height: float = 9.0
    allow_unknown_type: bool = True
    require_wall_id: bool = True
    require_room_connection: bool = False


class DoorValidator(Validator):
    """Validates Door entities.
    
    Checks geometry validity, dimensions, properties, and placement.
    
    Attributes:
        config: Validation thresholds configuration.
    """
    
    def __init__(self, config: DoorValidationConfig | None = None) -> None:
        """Initialize the door validator.
        
        Args:
            config: Optional validation configuration. Uses defaults if not provided.
        """
        self._config = config or DoorValidationConfig()
    
    @property
    def config(self) -> DoorValidationConfig:
        """Get the validation configuration.
        
        Returns:
            The current validation configuration.
        """
        return self._config
    
    def validate(self, entity: Any) -> ValidationResult:
        """Validate a Door entity.
        
        Args:
            entity: The entity to validate. Must be a Door instance.
            
        Returns:
            ValidationResult containing any issues found.
        """
        if not isinstance(entity, Door):
            result = ValidationResult.create()
            result.add_error(ValidationError(
                code="DOOR_INVALID_ENTITY",
                message=f"Expected Door entity, got {type(entity).__name__}",
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
    
    def _validate_geometry(self, door: Door, errors: list[ValidationError]) -> None:
        """Validate door geometry (location point).
        
        Args:
            door: The door to validate.
            errors: List to append errors to.
        """
        location = door.location
        
        # Check if location is valid (not None and has valid coordinates)
        if location is None:
            errors.append(ValidationError(
                code=DOOR_INVALID_GEOMETRY,
                message="Door location is missing",
                severity=ValidationSeverity.ERROR,
                entity_id=door.id,
                entity_type="Door",
            ))
            return
        
        # Check for valid coordinates
        if not isinstance(location, Point2D):
            errors.append(ValidationError(
                code=DOOR_INVALID_GEOMETRY,
                message="Door location has invalid type",
                severity=ValidationSeverity.ERROR,
                entity_id=door.id,
                entity_type="Door",
            ))
            return
        
        # Check for NaN or infinite coordinates
        import math
        if math.isnan(location.x) or math.isnan(location.y):
            errors.append(ValidationError(
                code=DOOR_INVALID_GEOMETRY,
                message="Door location contains NaN coordinates",
                severity=ValidationSeverity.ERROR,
                entity_id=door.id,
                entity_type="Door",
            ))
            return
        
        if math.isinf(location.x) or math.isinf(location.y):
            errors.append(ValidationError(
                code=DOOR_INVALID_GEOMETRY,
                message="Door location contains infinite coordinates",
                severity=ValidationSeverity.ERROR,
                entity_id=door.id,
                entity_type="Door",
            ))
    
    def _validate_dimensions(
        self,
        door: Door,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate door dimensions.
        
        Args:
            door: The door to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate width
        if door.width <= 0:
            errors.append(ValidationError(
                code=DOOR_INVALID_WIDTH,
                message=f"Door width must be positive, got {door.width}",
                severity=ValidationSeverity.ERROR,
                entity_id=door.id,
                entity_type="Door",
                metadata={"width": door.width},
            ))
        elif door.width < self._config.min_width:
            errors.append(ValidationError(
                code=DOOR_INVALID_WIDTH,
                message=f"Door width {door.width} is below minimum {self._config.min_width}",
                severity=ValidationSeverity.ERROR,
                entity_id=door.id,
                entity_type="Door",
                metadata={"width": door.width},
            ))
        elif door.width > self._config.max_width:
            warnings.append(ValidationError(
                code=DOOR_INVALID_WIDTH,
                message=f"Door width {door.width} exceeds recommended maximum {self._config.max_width}",
                severity=ValidationSeverity.WARNING,
                entity_id=door.id,
                entity_type="Door",
                metadata={"width": door.width},
            ))
        
        # Validate height
        if door.height is not None:
            if door.height <= 0:
                errors.append(ValidationError(
                    code=DOOR_INVALID_HEIGHT,
                    message=f"Door height must be positive, got {door.height}",
                    severity=ValidationSeverity.ERROR,
                    entity_id=door.id,
                    entity_type="Door",
                    metadata={"height": door.height},
                ))
            elif door.height < self._config.min_height:
                errors.append(ValidationError(
                    code=DOOR_INVALID_HEIGHT,
                    message=f"Door height {door.height} is below minimum {self._config.min_height}",
                    severity=ValidationSeverity.ERROR,
                    entity_id=door.id,
                    entity_type="Door",
                    metadata={"height": door.height},
                ))
            elif door.height > self._config.max_height:
                warnings.append(ValidationError(
                    code=DOOR_INVALID_HEIGHT,
                    message=f"Door height {door.height} exceeds recommended maximum {self._config.max_height}",
                    severity=ValidationSeverity.WARNING,
                    entity_id=door.id,
                    entity_type="Door",
                    metadata={"height": door.height},
                ))
    
    def _validate_properties(
        self,
        door: Door,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate door properties.
        
        Args:
            door: The door to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate door type
        if door.door_type == DoorType.UNKNOWN:
            if self._config.allow_unknown_type:
                warnings.append(ValidationError(
                    code=DOOR_INVALID_TYPE,
                    message="Door has UNKNOWN type",
                    severity=ValidationSeverity.WARNING,
                    entity_id=door.id,
                    entity_type="Door",
                ))
            else:
                errors.append(ValidationError(
                    code=DOOR_INVALID_TYPE,
                    message="Door has UNKNOWN type",
                    severity=ValidationSeverity.ERROR,
                    entity_id=door.id,
                    entity_type="Door",
                ))
        
        # Validate floor ID
        if not door.floor_id:
            errors.append(ValidationError(
                code=DOOR_MISSING_FLOOR,
                message="Door must belong to a floor",
                severity=ValidationSeverity.ERROR,
                entity_id=door.id,
                entity_type="Door",
            ))
    
    def _validate_placement(
        self,
        door: Door,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate door placement references.
        
        Args:
            door: The door to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate wall ID (configurable)
        if self._config.require_wall_id and not door.wall_id:
            errors.append(ValidationError(
                code=DOOR_MISSING_WALL,
                message="Door must be associated with a wall",
                severity=ValidationSeverity.ERROR,
                entity_id=door.id,
                entity_type="Door",
            ))
        
        # Validate room connection (configurable)
        if self._config.require_room_connection and not door.room_ids:
            errors.append(ValidationError(
                code=DOOR_MISSING_ROOM_CONNECTION,
                message="Door must connect at least one room",
                severity=ValidationSeverity.ERROR,
                entity_id=door.id,
                entity_type="Door",
            ))