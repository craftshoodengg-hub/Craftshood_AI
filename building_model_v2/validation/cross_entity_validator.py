"""Cross-entity validator for Building Model v2.

Validates references and consistency between entities in a building model.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Final

from ..entities_building import Building
from ..entities_column import Column
from ..entities_floor import Floor
from ..entities_room import Room
from ..entities_stair import Stair
from ..entities_wall import Wall
from ..relationships import Relationship
from ..types import DoorType, WindowType
from .validation_error import ValidationError
from .validation_result import ValidationResult
from .validation_severity import ValidationSeverity
from .validator import Validator


# Validation error codes
ENTITY_REFERENCE_MISSING: Final[str] = "ENTITY_REFERENCE_MISSING"
ROOM_UNKNOWN_WALL: Final[str] = "ROOM_UNKNOWN_WALL"
ROOM_UNKNOWN_DOOR: Final[str] = "ROOM_UNKNOWN_DOOR"
ROOM_UNKNOWN_WINDOW: Final[str] = "ROOM_UNKNOWN_WINDOW"
DOOR_UNKNOWN_WALL: Final[str] = "DOOR_UNKNOWN_WALL"
WINDOW_UNKNOWN_WALL: Final[str] = "WINDOW_UNKNOWN_WALL"
STAIR_UNKNOWN_FLOOR: Final[str] = "STAIR_UNKNOWN_FLOOR"
COLUMN_UNKNOWN_FLOOR: Final[str] = "COLUMN_UNKNOWN_FLOOR"
FLOOR_UNKNOWN_ROOM: Final[str] = "FLOOR_UNKNOWN_ROOM"
FLOOR_UNKNOWN_WALL: Final[str] = "FLOOR_UNKNOWN_WALL"
FLOOR_UNKNOWN_COLUMN: Final[str] = "FLOOR_UNKNOWN_COLUMN"
FLOOR_UNKNOWN_STAIR: Final[str] = "FLOOR_UNKNOWN_STAIR"
BUILDING_UNKNOWN_FLOOR: Final[str] = "BUILDING_UNKNOWN_FLOOR"
RELATIONSHIP_UNKNOWN_SOURCE: Final[str] = "RELATIONSHIP_UNKNOWN_SOURCE"
RELATIONSHIP_UNKNOWN_TARGET: Final[str] = "RELATIONSHIP_UNKNOWN_TARGET"


@dataclass(slots=True)
class CrossEntityValidationConfig:
    """Configuration for cross-entity validation.
    
    Attributes:
        require_room_walls: Whether rooms must reference existing walls.
        require_door_wall: Whether doors must reference an existing wall.
        require_window_wall: Whether windows must reference an existing wall.
        require_stair_floors: Whether stairs must reference existing floors.
        require_building_floors: Whether buildings must reference existing floors.
        allow_orphan_entities: Whether entities without relationships are allowed.
    """
    
    require_room_walls: bool = False
    require_door_wall: bool = False
    require_window_wall: bool = False
    require_stair_floors: bool = False
    require_building_floors: bool = False
    allow_orphan_entities: bool = True


@dataclass(slots=True)
class BuildingModel:
    """Container for all entities in a building model.
    
    Attributes:
        building: The building entity.
        floors: Mapping of floor ID to Floor entities.
        rooms: Mapping of room ID to Room entities.
        walls: Mapping of wall ID to Wall entities.
        columns: Mapping of column ID to Column entities.
        stairs: Mapping of stair ID to Stair entities.
        doors: Mapping of door ID to door entities (Opening with DoorType).
        windows: Mapping of window ID to window entities (Opening with WindowType).
        relationships: List of Relationship entities.
    """
    
    building: Building | None = None
    floors: dict[str, Floor] = field(default_factory=dict)
    rooms: dict[str, Room] = field(default_factory=dict)
    walls: dict[str, Wall] = field(default_factory=dict)
    columns: dict[str, Column] = field(default_factory=dict)
    stairs: dict[str, Stair] = field(default_factory=dict)
    doors: dict[str, Any] = field(default_factory=dict)
    windows: dict[str, Any] = field(default_factory=dict)
    relationships: list[Relationship] = field(default_factory=list)


class CrossEntityValidator(Validator):
    """Validates cross-entity references and consistency.
    
    Checks that all entity references point to existing entities.
    
    Attributes:
        config: Validation configuration.
    """
    
    def __init__(self, config: CrossEntityValidationConfig | None = None) -> None:
        """Initialize the cross-entity validator.
        
        Args:
            config: Optional validation configuration. Uses defaults if not provided.
        """
        self._config = config or CrossEntityValidationConfig()
    
    @property
    def config(self) -> CrossEntityValidationConfig:
        """Get the validation configuration.
        
        Returns:
            The current validation configuration.
        """
        return self._config
    
    def validate(self, entity: Any) -> ValidationResult:
        """Validate a BuildingModel.
        
        Args:
            entity: The BuildingModel to validate.
            
        Returns:
            ValidationResult containing any issues found.
        """
        if not isinstance(entity, BuildingModel):
            result = ValidationResult.create()
            result.add_error(ValidationError(
                code="CROSS_ENTITY_INVALID_INPUT",
                message=f"Expected BuildingModel, got {type(entity).__name__}",
                severity=ValidationSeverity.ERROR,
            ))
            return result
        
        errors: list[ValidationError] = []
        warnings: list[ValidationError] = []
        infos: list[ValidationError] = []
        
        # Validate building references
        self._validate_building_references(entity, errors, warnings)
        
        # Validate floor references
        self._validate_floor_references(entity, errors, warnings)
        
        # Validate room references
        self._validate_room_references(entity, errors, warnings)
        
        # Validate wall references
        self._validate_wall_references(entity, errors, warnings)
        
        # Validate column references
        self._validate_column_references(entity, errors, warnings)
        
        # Validate stair references
        self._validate_stair_references(entity, errors, warnings)
        
        # Validate relationship references
        self._validate_relationship_references(entity, errors, warnings)
        
        return ValidationResult(
            errors=errors,
            warnings=warnings,
            infos=infos,
        )
    
    def _validate_building_references(
        self,
        model: BuildingModel,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate building references to floors.
        
        Args:
            model: The building model.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        if model.building is None:
            return
        
        if not self._config.require_building_floors and not model.building.floor_ids:
            return
        
        for floor_id in model.building.floor_ids:
            if floor_id not in model.floors:
                severity = (ValidationSeverity.ERROR if self._config.require_building_floors
                           else ValidationSeverity.WARNING)
                (errors if severity == ValidationSeverity.ERROR else warnings).append(ValidationError(
                    code=BUILDING_UNKNOWN_FLOOR,
                    message=f"Building references unknown floor: {floor_id}",
                    severity=severity,
                    entity_id=model.building.id,
                    entity_type="Building",
                    metadata={"floor_id": floor_id},
                ))
    
    def _validate_floor_references(
        self,
        model: BuildingModel,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate floor references to rooms, walls, columns, and stairs.
        
        Args:
            model: The building model.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        for floor_id, floor in model.floors.items():
            # Validate room references
            for room_id in floor.room_ids:
                if room_id not in model.rooms:
                    warnings.append(ValidationError(
                        code=FLOOR_UNKNOWN_ROOM,
                        message=f"Floor {floor_id} references unknown room: {room_id}",
                        severity=ValidationSeverity.WARNING,
                        entity_id=floor_id,
                        entity_type="Floor",
                        metadata={"room_id": room_id},
                    ))
            
            # Validate wall references (if we had wall_ids on Floor)
            # Note: Floor entity doesn't have wall_ids in current model
            # This is for future expansion
            
            # Validate column references
            for column_id in floor.column_ids:
                if column_id not in model.columns:
                    warnings.append(ValidationError(
                        code=FLOOR_UNKNOWN_COLUMN,
                        message=f"Floor {floor_id} references unknown column: {column_id}",
                        severity=ValidationSeverity.WARNING,
                        entity_id=floor_id,
                        entity_type="Floor",
                        metadata={"column_id": column_id},
                    ))
            
            # Validate stair references
            for stair_id in floor.stair_ids:
                if stair_id not in model.stairs:
                    warnings.append(ValidationError(
                        code=FLOOR_UNKNOWN_STAIR,
                        message=f"Floor {floor_id} references unknown stair: {stair_id}",
                        severity=ValidationSeverity.WARNING,
                        entity_id=floor_id,
                        entity_type="Floor",
                        metadata={"stair_id": stair_id},
                    ))
    
    def _validate_room_references(
        self,
        model: BuildingModel,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate room references to walls, doors, and windows.
        
        Args:
            model: The building model.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        for room_id, room in model.rooms.items():
            # Validate wall references
            for wall_id in room.wall_ids:
                if wall_id not in model.walls:
                    severity = (ValidationSeverity.ERROR if self._config.require_room_walls
                               else ValidationSeverity.WARNING)
                    (errors if severity == ValidationSeverity.ERROR else warnings).append(ValidationError(
                        code=ROOM_UNKNOWN_WALL,
                        message=f"Room {room_id} references unknown wall: {wall_id}",
                        severity=severity,
                        entity_id=room_id,
                        entity_type="Room",
                        metadata={"wall_id": wall_id},
                    ))
            
            # Validate door references
            for door_id in room.door_ids:
                if door_id not in model.doors:
                    severity = (ValidationSeverity.ERROR if self._config.require_door_wall
                               else ValidationSeverity.WARNING)
                    (errors if severity == ValidationSeverity.ERROR else warnings).append(ValidationError(
                        code=ROOM_UNKNOWN_DOOR,
                        message=f"Room {room_id} references unknown door: {door_id}",
                        severity=severity,
                        entity_id=room_id,
                        entity_type="Room",
                        metadata={"door_id": door_id},
                    ))
            
            # Validate window references
            for window_id in room.window_ids:
                if window_id not in model.windows:
                    severity = (ValidationSeverity.ERROR if self._config.require_window_wall
                               else ValidationSeverity.WARNING)
                    (errors if severity == ValidationSeverity.ERROR else warnings).append(ValidationError(
                        code=ROOM_UNKNOWN_WINDOW,
                        message=f"Room {room_id} references unknown window: {window_id}",
                        severity=severity,
                        entity_id=room_id,
                        entity_type="Room",
                        metadata={"window_id": window_id},
                    ))
    
    def _validate_wall_references(
        self,
        model: BuildingModel,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate wall references to floor.
        
        Args:
            model: The building model.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        for wall_id, wall in model.walls.items():
            if wall.floor_id and wall.floor_id not in model.floors:
                warnings.append(ValidationError(
                    code=ENTITY_REFERENCE_MISSING,
                    message=f"Wall {wall_id} references unknown floor: {wall.floor_id}",
                    severity=ValidationSeverity.WARNING,
                    entity_id=wall_id,
                    entity_type="Wall",
                    metadata={"floor_id": wall.floor_id},
                ))
    
    def _validate_column_references(
        self,
        model: BuildingModel,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate column references to floor.
        
        Args:
            model: The building model.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        for column_id, column in model.columns.items():
            if column.floor_id and column.floor_id not in model.floors:
                severity = (ValidationSeverity.ERROR if self._config.require_stair_floors
                           else ValidationSeverity.WARNING)
                (errors if severity == ValidationSeverity.ERROR else warnings).append(ValidationError(
                    code=COLUMN_UNKNOWN_FLOOR,
                    message=f"Column {column_id} references unknown floor: {column.floor_id}",
                    severity=severity,
                    entity_id=column_id,
                    entity_type="Column",
                    metadata={"floor_id": column.floor_id},
                ))
    
    def _validate_stair_references(
        self,
        model: BuildingModel,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate stair references to floors.
        
        Args:
            model: The building model.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        for stair_id, stair in model.stairs.items():
            if stair.floor_id and stair.floor_id not in model.floors:
                severity = (ValidationSeverity.ERROR if self._config.require_stair_floors
                           else ValidationSeverity.WARNING)
                (errors if severity == ValidationSeverity.ERROR else warnings).append(ValidationError(
                    code=STAIR_UNKNOWN_FLOOR,
                    message=f"Stair {stair_id} references unknown floor: {stair.floor_id}",
                    severity=severity,
                    entity_id=stair_id,
                    entity_type="Stair",
                    metadata={"floor_id": stair.floor_id},
                ))
    
    def _validate_relationship_references(
        self,
        model: BuildingModel,
        errors: list[ValidationError],
        warnings: list[ValidationError],
    ) -> None:
        """Validate relationship references to source and target entities.
        
        Args:
            model: The building model.
            errors: List to append errors to.
            warnings: List to append warnings to.
        """
        all_entity_ids: set[str] = set()
        
        # Collect all entity IDs
        if model.building:
            all_entity_ids.add(model.building.id)
        all_entity_ids.update(model.floors.keys())
        all_entity_ids.update(model.rooms.keys())
        all_entity_ids.update(model.walls.keys())
        all_entity_ids.update(model.columns.keys())
        all_entity_ids.update(model.stairs.keys())
        all_entity_ids.update(model.doors.keys())
        all_entity_ids.update(model.windows.keys())
        
        for relationship in model.relationships:
            # Check source
            if relationship.source_id and relationship.source_id not in all_entity_ids:
                warnings.append(ValidationError(
                    code=RELATIONSHIP_UNKNOWN_SOURCE,
                    message=f"Relationship {relationship.id} references unknown source: {relationship.source_id}",
                    severity=ValidationSeverity.WARNING,
                    entity_id=relationship.id,
                    entity_type="Relationship",
                    metadata={"source_id": relationship.source_id},
                ))
            
            # Check target
            if relationship.target_id and relationship.target_id not in all_entity_ids:
                warnings.append(ValidationError(
                    code=RELATIONSHIP_UNKNOWN_TARGET,
                    message=f"Relationship {relationship.id} references unknown target: {relationship.target_id}",
                    severity=ValidationSeverity.WARNING,
                    entity_id=relationship.id,
                    entity_type="Relationship",
                    metadata={"target_id": relationship.target_id},
                ))