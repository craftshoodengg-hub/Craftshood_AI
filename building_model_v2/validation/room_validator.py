"""Room validator for Building Model v2.

Validates room entities for geometric and property correctness.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Final

from shapely.geometry import Polygon
from shapely.validation import explain_validity

from ..entities_room import Room
from ..types import RoomType
from .validation_error import ValidationError
from .validation_result import ValidationResult
from .validation_severity import ValidationSeverity
from .validator import Validator


# Validation error codes
ROOM_EMPTY_NAME: Final[str] = "ROOM_EMPTY_NAME"
ROOM_INVALID_POLYGON: Final[str] = "ROOM_INVALID_POLYGON"
ROOM_ZERO_AREA: Final[str] = "ROOM_ZERO_AREA"
ROOM_SELF_INTERSECTING: Final[str] = "ROOM_SELF_INTERSECTING"
ROOM_INVALID_HEIGHT: Final[str] = "ROOM_INVALID_HEIGHT"
ROOM_INVALID_TYPE: Final[str] = "ROOM_INVALID_TYPE"
ROOM_MISSING_FLOOR_ID: Final[str] = "ROOM_MISSING_FLOOR_ID"
ROOM_BAD_ASPECT_RATIO: Final[str] = "ROOM_BAD_ASPECT_RATIO"
ROOM_LOW_COMPACTNESS: Final[str] = "ROOM_LOW_COMPACTNESS"
ROOM_DUPLICATE_WALL_IDS: Final[str] = "ROOM_DUPLICATE_WALL_IDS"
ROOM_DUPLICATE_DOOR_IDS: Final[str] = "ROOM_DUPLICATE_DOOR_IDS"
ROOM_DUPLICATE_WINDOW_IDS: Final[str] = "ROOM_DUPLICATE_WINDOW_IDS"


@dataclass(slots=True)
class RoomValidationConfig:
    """Configuration for room validation thresholds.
    
    Attributes:
        min_ceiling_height: Minimum acceptable ceiling height in feet.
        max_aspect_ratio: Maximum acceptable aspect ratio before warning.
        min_compactness: Minimum compactness before warning.
        allow_unknown_type: Whether to allow RoomType.UNKNOWN.
    """
    
    min_ceiling_height: float = 6.0
    max_aspect_ratio: float = 5.0
    min_compactness: float = 0.3
    allow_unknown_type: bool = True


class RoomValidator(Validator):
    """Validates Room entities.
    
    Checks geometry validity, property correctness, and collection integrity.
    
    Attributes:
        config: Validation thresholds configuration.
    """
    
    def __init__(self, config: RoomValidationConfig | None = None) -> None:
        """Initialize the room validator.
        
        Args:
            config: Optional validation configuration. Uses defaults if not provided.
        """
        self._config = config or RoomValidationConfig()
    
    @property
    def config(self) -> RoomValidationConfig:
        """Get the validation configuration.
        
        Returns:
            The current validation configuration.
        """
        return self._config
    
    def validate(self, entity: Any) -> ValidationResult:
        """Validate a Room entity.
        
        Args:
            entity: The entity to validate. Must be a Room instance.
            
        Returns:
            ValidationResult containing any issues found.
        """
        if not isinstance(entity, Room):
            result = ValidationResult.create()
            result.add_error(ValidationError(
                code="ROOM_INVALID_ENTITY",
                message=f"Expected Room entity, got {type(entity).__name__}",
                severity=ValidationSeverity.ERROR,
            ))
            return result
        
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []
        infos: list[ValidationError] = []
        
        # Validate name
        self._validate_name(entity, errors)
        
        # Validate room type
        self._validate_room_type(entity, errors, warnings)
        
        # Validate polygon geometry
        self._validate_polygon(entity, errors)
        
        # Validate ceiling height
        self._validate_ceiling_height(entity, errors)
        
        # Validate floor ID
        self._validate_floor_id(entity, errors)
        
        # Validate aspect ratio
        self._validate_aspect_ratio(entity, warnings)
        
        # Validate compactness
        self._validate_compactness(entity, warnings)
        
        # Validate collections
        self._validate_collections(entity, errors)
        
        return ValidationResult(
            errors=errors,
            warnings=warnings,
            infos=infos,
        )
    
    def _validate_name(self, room: Room, errors: list[ValidationError]) -> None:
        """Validate room name is not empty.
        
        Room name is stored in metadata under the 'name' key.
        
        Args:
            room: The room to validate.
            errors: List to append errors to.
        """
        name = room.metadata.get("name", "")
        if not name or not str(name).strip():
            errors.append(ValidationError(
                code=ROOM_EMPTY_NAME,
                message="Room name cannot be empty",
                severity=ValidationSeverity.ERROR,
                entity_id=room.id,
                entity_type="Room",
            ))
    
    def _validate_room_type(
        self,
        room: Room,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate room type.
        
        Args:
            room: The room to validate.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        if room.room_type == RoomType.UNKNOWN:
            if not self._config.allow_unknown_type:
                errors.append(ValidationError(
                    code=ROOM_INVALID_TYPE,
                    message="Room type cannot be UNKNOWN",
                    severity=ValidationSeverity.ERROR,
                    entity_id=room.id,
                    entity_type="Room",
                ))
            else:
                warnings.append(ValidationError(
                    code=ROOM_INVALID_TYPE,
                    message="Room has UNKNOWN type",
                    severity=ValidationSeverity.WARNING,
                    entity_id=room.id,
                    entity_type="Room",
                ))
    
    def _validate_polygon(self, room: Room, errors: list[ValidationError]) -> None:
        """Validate room polygon geometry.
        
        Args:
            room: The room to validate.
            errors: List to append errors to.
        """
        polygon = room.polygon
        
        # Check if polygon exists (is not empty)
        if polygon.is_empty:
            errors.append(ValidationError(
                code=ROOM_INVALID_POLYGON,
                message="Room polygon is empty",
                severity=ValidationSeverity.ERROR,
                entity_id=room.id,
                entity_type="Room",
            ))
            return
        
        # Check minimum vertices (3 for a valid polygon + closure = 4)
        exterior_coords = list(polygon.exterior.coords)
        if len(exterior_coords) < 4:
            errors.append(ValidationError(
                code=ROOM_INVALID_POLYGON,
                message=f"Room polygon has insufficient vertices: {len(exterior_coords)} (minimum 4)",
                severity=ValidationSeverity.ERROR,
                entity_id=room.id,
                entity_type="Room",
            ))
            return
        
        # Check if polygon is valid (not self-intersecting)
        if not polygon.is_valid:
            reason = explain_validity(polygon)
            errors.append(ValidationError(
                code=ROOM_SELF_INTERSECTING,
                message=f"Room polygon is invalid: {reason}",
                severity=ValidationSeverity.ERROR,
                entity_id=room.id,
                entity_type="Room",
            ))
            return
        
        # Check area > 0
        if polygon.area <= 0:
            errors.append(ValidationError(
                code=ROOM_ZERO_AREA,
                message="Room polygon has zero area",
                severity=ValidationSeverity.ERROR,
                entity_id=room.id,
                entity_type="Room",
            ))
    
    def _validate_ceiling_height(self, room: Room, errors: list[ValidationError]) -> None:
        """Validate ceiling height is positive.
        
        Args:
            room: The room to validate.
            errors: List to append errors to.
        """
        if room.ceiling_height is not None and room.ceiling_height <= 0:
            errors.append(ValidationError(
                code=ROOM_INVALID_HEIGHT,
                message=f"Ceiling height must be positive, got {room.ceiling_height}",
                severity=ValidationSeverity.ERROR,
                entity_id=room.id,
                entity_type="Room",
                metadata={"ceiling_height": room.ceiling_height},
            ))
    
    def _validate_floor_id(self, room: Room, errors: list[ValidationError]) -> None:
        """Validate floor ID exists.
        
        Args:
            room: The room to validate.
            errors: List to append errors to.
        """
        if not room.floor_id:
            errors.append(ValidationError(
                code=ROOM_MISSING_FLOOR_ID,
                message="Room must belong to a floor",
                severity=ValidationSeverity.ERROR,
                entity_id=room.id,
                entity_type="Room",
            ))
    
    def _validate_aspect_ratio(self, room: Room, warnings: list[ValidationError]) -> None:
        """Validate aspect ratio is within reasonable range.
        
        Args:
            room: The room to validate.
            warnings: List to append warnings to.
        """
        if room.polygon.is_empty:
            return
        
        aspect_ratio = room.aspect_ratio()
        if aspect_ratio > self._config.max_aspect_ratio:
            warnings.append(ValidationError(
                code=ROOM_BAD_ASPECT_RATIO,
                message=f"Room aspect ratio {aspect_ratio:.2f} exceeds recommended maximum {self._config.max_aspect_ratio}",
                severity=ValidationSeverity.WARNING,
                entity_id=room.id,
                entity_type="Room",
                metadata={"aspect_ratio": round(aspect_ratio, 2)},
            ))
    
    def _validate_compactness(self, room: Room, warnings: list[ValidationError]) -> None:
        """Validate compactness is above threshold.
        
        Args:
            room: The room to validate.
            warnings: List to append warnings to.
        """
        if room.polygon.is_empty:
            return
        
        compactness = room.compactness()
        if compactness < self._config.min_compactness:
            warnings.append(ValidationError(
                code=ROOM_LOW_COMPACTNESS,
                message=f"Room compactness {compactness:.2f} is below recommended minimum {self._config.min_compactness}",
                severity=ValidationSeverity.WARNING,
                entity_id=room.id,
                entity_type="Room",
                metadata={"compactness": round(compactness, 2)},
            ))
    
    def _validate_collections(self, room: Room, errors: list[ValidationError]) -> None:
        """Validate ID collections for duplicates.
        
        Args:
            room: The room to validate.
            errors: List to append errors to.
        """
        # Check wall_ids for duplicates
        wall_ids_list = list(room.wall_ids)
        if len(wall_ids_list) != len(set(wall_ids_list)):
            errors.append(ValidationError(
                code=ROOM_DUPLICATE_WALL_IDS,
                message="Room contains duplicate wall IDs",
                severity=ValidationSeverity.ERROR,
                entity_id=room.id,
                entity_type="Room",
            ))
        
        # Check door_ids for duplicates
        door_ids_list = list(room.door_ids)
        if len(door_ids_list) != len(set(door_ids_list)):
            errors.append(ValidationError(
                code=ROOM_DUPLICATE_DOOR_IDS,
                message="Room contains duplicate door IDs",
                severity=ValidationSeverity.ERROR,
                entity_id=room.id,
                entity_type="Room",
            ))
        
        # Check window_ids for duplicates
        window_ids_list = list(room.window_ids)
        if len(window_ids_list) != len(set(window_ids_list)):
            errors.append(ValidationError(
                code=ROOM_DUPLICATE_WINDOW_IDS,
                message="Room contains duplicate window IDs",
                severity=ValidationSeverity.ERROR,
                entity_id=room.id,
                entity_type="Room",
            ))