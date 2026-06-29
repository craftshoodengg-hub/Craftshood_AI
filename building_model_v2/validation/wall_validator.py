"""Wall validator for Building Model v2.

Validates wall entities for geometric and property correctness.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from shapely.geometry import LineString

from ..entities_wall import Wall
from ..types import WallType
from .validation_error import ValidationError
from .validation_result import ValidationResult
from .validation_severity import ValidationSeverity
from .validator import Validator


# Validation error codes
WALL_INVALID_GEOMETRY: Final[str] = "WALL_INVALID_GEOMETRY"
WALL_ZERO_LENGTH: Final[str] = "WALL_ZERO_LENGTH"
WALL_INVALID_THICKNESS: Final[str] = "WALL_INVALID_THICKNESS"
WALL_INVALID_HEIGHT: Final[str] = "WALL_INVALID_HEIGHT"
WALL_INVALID_TYPE: Final[str] = "WALL_INVALID_TYPE"
WALL_MISSING_FLOOR_ID: Final[str] = "WALL_MISSING_FLOOR_ID"
WALL_TOO_SHORT: Final[str] = "WALL_TOO_SHORT"
WALL_TOO_LONG: Final[str] = "WALL_TOO_LONG"


@dataclass(slots=True)
class WallValidationConfig:
    """Configuration for wall validation thresholds.
    
    Attributes:
        min_wall_length: Minimum acceptable wall length in feet.
        max_wall_length: Maximum acceptable wall length in feet.
        min_wall_thickness: Minimum acceptable wall thickness in feet.
        max_wall_thickness: Maximum acceptable wall thickness in feet.
        min_wall_height: Minimum acceptable wall height in feet.
        allow_zero_openings: Whether walls can have no openings.
    """
    
    min_wall_length: float = 1.0
    max_wall_length: float = 100.0
    min_wall_thickness: float = 0.1
    max_wall_thickness: float = 5.0
    min_wall_height: float = 1.0
    allow_zero_openings: bool = True


class WallValidator(Validator):
    """Validates Wall entities.
    
    Checks geometry validity, dimensions, properties, and openings.
    
    Attributes:
        config: Validation thresholds configuration.
    """
    
    def __init__(self, config: WallValidationConfig | None = None) -> None:
        """Initialize the wall validator.
        
        Args:
            config: Optional validation configuration. Uses defaults if not provided.
        """
        self._config = config or WallValidationConfig()
    
    @property
    def config(self) -> WallValidationConfig:
        """Get the validation configuration.
        
        Returns:
            The current validation configuration.
        """
        return self._config
    
    def validate(self, entity: Any) -> ValidationResult:
        """Validate a Wall entity.
        
        Args:
            entity: The entity to validate. Must be a Wall instance.
            
        Returns:
            ValidationResult containing any issues found.
        """
        if not isinstance(entity, Wall):
            result = ValidationResult.create()
            result.add_error(ValidationError(
                code="WALL_INVALID_ENTITY",
                message=f"Expected Wall entity, got {type(entity).__name__}",
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
        
        # Validate openings
        self._validate_openings(entity, warnings)
        
        return ValidationResult(
            errors=errors,
            warnings=warnings,
            infos=infos,
        )
    
    def _validate_geometry(self, wall: Wall, errors: list[ValidationError]) -> None:
        """Validate wall geometry.
        
        Args:
            wall: The wall to validate.
            errors: List to append errors to.
        """
        geometry = wall.geometry
        
        # Check if geometry exists (is not empty)
        if geometry.is_empty:
            errors.append(ValidationError(
                code=WALL_INVALID_GEOMETRY,
                message="Wall geometry is empty",
                severity=ValidationSeverity.ERROR,
                entity_id=wall.id,
                entity_type="Wall",
            ))
            return
        
        # Check minimum points (at least 2 for a line)
        coords = list(geometry.coords)
        if len(coords) < 2:
            errors.append(ValidationError(
                code=WALL_INVALID_GEOMETRY,
                message=f"Wall geometry has insufficient points: {len(coords)} (minimum 2)",
                severity=ValidationSeverity.ERROR,
                entity_id=wall.id,
                entity_type="Wall",
            ))
            return
        
        # Check for distinct points (non-zero length)
        if geometry.length <= 0:
            errors.append(ValidationError(
                code=WALL_ZERO_LENGTH,
                message="Wall has zero length",
                severity=ValidationSeverity.ERROR,
                entity_id=wall.id,
                entity_type="Wall",
            ))
            return
        
        # Check if line is valid
        if not geometry.is_valid:
            errors.append(ValidationError(
                code=WALL_INVALID_GEOMETRY,
                message="Wall geometry is invalid",
                severity=ValidationSeverity.ERROR,
                entity_id=wall.id,
                entity_type="Wall",
            ))
    
    def _validate_dimensions(
        self,
        wall: Wall,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate wall dimensions.
        
        Args:
            wall: The wall to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Skip dimension checks if geometry is invalid
        if wall.geometry.is_empty or wall.geometry.length <= 0:
            return
        
        # Validate thickness (width)
        if wall.width <= 0:
            errors.append(ValidationError(
                code=WALL_INVALID_THICKNESS,
                message=f"Wall thickness must be positive, got {wall.width}",
                severity=ValidationSeverity.ERROR,
                entity_id=wall.id,
                entity_type="Wall",
                metadata={"width": wall.width},
            ))
        elif wall.width < self._config.min_wall_thickness:
            errors.append(ValidationError(
                code=WALL_INVALID_THICKNESS,
                message=f"Wall thickness {wall.width} is below minimum {self._config.min_wall_thickness}",
                severity=ValidationSeverity.ERROR,
                entity_id=wall.id,
                entity_type="Wall",
                metadata={"width": wall.width},
            ))
        elif wall.width > self._config.max_wall_thickness:
            warnings.append(ValidationError(
                code=WALL_INVALID_THICKNESS,
                message=f"Wall thickness {wall.width} exceeds recommended maximum {self._config.max_wall_thickness}",
                severity=ValidationSeverity.WARNING,
                entity_id=wall.id,
                entity_type="Wall",
                metadata={"width": wall.width},
            ))
        
        # Validate height
        if wall.height is not None:
            if wall.height <= 0:
                errors.append(ValidationError(
                    code=WALL_INVALID_HEIGHT,
                    message=f"Wall height must be positive, got {wall.height}",
                    severity=ValidationSeverity.ERROR,
                    entity_id=wall.id,
                    entity_type="Wall",
                    metadata={"height": wall.height},
                ))
            elif wall.height < self._config.min_wall_height:
                errors.append(ValidationError(
                    code=WALL_INVALID_HEIGHT,
                    message=f"Wall height {wall.height} is below minimum {self._config.min_wall_height}",
                    severity=ValidationSeverity.ERROR,
                    entity_id=wall.id,
                    entity_type="Wall",
                    metadata={"height": wall.height},
                ))
        
        # Validate length
        length = wall.length
        if length < self._config.min_wall_length:
            errors.append(ValidationError(
                code=WALL_TOO_SHORT,
                message=f"Wall length {length:.2f} is below minimum {self._config.min_wall_length}",
                severity=ValidationSeverity.ERROR,
                entity_id=wall.id,
                entity_type="Wall",
                metadata={"length": round(length, 2)},
            ))
        elif length > self._config.max_wall_length:
            errors.append(ValidationError(
                code=WALL_TOO_LONG,
                message=f"Wall length {length:.2f} exceeds maximum {self._config.max_wall_length}",
                severity=ValidationSeverity.ERROR,
                entity_id=wall.id,
                entity_type="Wall",
                metadata={"length": round(length, 2)},
            ))
    
    def _validate_properties(
        self,
        wall: Wall,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate wall properties.
        
        Args:
            wall: The wall to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        # Validate wall type
        if wall.wall_type == WallType.UNKNOWN:
            warnings.append(ValidationError(
                code=WALL_INVALID_TYPE,
                message="Wall has UNKNOWN type",
                severity=ValidationSeverity.WARNING,
                entity_id=wall.id,
                entity_type="Wall",
            ))
        
        # Validate floor ID
        if not wall.floor_id:
            errors.append(ValidationError(
                code=WALL_MISSING_FLOOR_ID,
                message="Wall must belong to a floor",
                severity=ValidationSeverity.ERROR,
                entity_id=wall.id,
                entity_type="Wall",
            ))
    
    def _validate_openings(self, wall: Wall, warnings: list[ValidationError]) -> None:
        """Validate wall openings (door and window IDs presence).
        
        Args:
            wall: The wall to validate.
            warnings: List to append warnings to.
        """
        if not self._config.allow_zero_openings:
            if not wall.door_ids and not wall.window_ids:
                warnings.append(ValidationError(
                    code="WALL_NO_OPENINGS",
                    message="Wall has no doors or windows",
                    severity=ValidationSeverity.WARNING,
                    entity_id=wall.id,
                    entity_type="Wall",
                ))