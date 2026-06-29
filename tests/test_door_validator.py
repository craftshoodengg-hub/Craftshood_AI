"""Unit tests for DoorValidator."""

from __future__ import annotations

import math

import pytest

from building_model_v2.base import Point2D
from building_model_v2.entities_opening import Door
from building_model_v2.types import DoorType
from building_model_v2.validation import (
    DoorValidationConfig,
    DoorValidator,
)
from building_model_v2.validation.door_validator import (
    DOOR_INVALID_GEOMETRY,
    DOOR_INVALID_HEIGHT,
    DOOR_INVALID_TYPE,
    DOOR_INVALID_WIDTH,
    DOOR_MISSING_FLOOR,
    DOOR_MISSING_ROOM_CONNECTION,
    DOOR_MISSING_WALL,
)


class TestDoorValidationConfig:
    """Tests for DoorValidationConfig."""
    
    def test_default_values(self) -> None:
        config = DoorValidationConfig()
        assert config.min_width == 2.0
        assert config.max_width == 6.0
        assert config.min_height == 6.0
        assert config.max_height == 9.0
        assert config.allow_unknown_type is True
        assert config.require_wall_id is True
        assert config.require_room_connection is False
    
    def test_custom_values(self) -> None:
        config = DoorValidationConfig(
            min_width=3.0,
            max_width=4.0,
            min_height=7.0,
            max_height=8.0,
            allow_unknown_type=False,
            require_wall_id=False,
            require_room_connection=True,
        )
        assert config.min_width == 3.0
        assert config.max_width == 4.0
        assert config.min_height == 7.0
        assert config.max_height == 8.0
        assert config.allow_unknown_type is False
        assert config.require_wall_id is False
        assert config.require_room_connection is True


class TestDoorValidatorValid:
    """Tests for valid door validation."""
    
    def test_valid_door(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            height=7.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.is_valid is True
        assert result.error_count == 0
    
    def test_valid_door_without_height(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.is_valid is True
    
    def test_valid_door_with_room_ids(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            height=7.0,
            door_type=DoorType.DOUBLE_LEAF,
            wall_id="wall-1",
            room_ids=frozenset(["room-1", "room-2"]),
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.is_valid is True


class TestDoorValidatorGeometry:
    """Tests for geometry validation."""
    
    def test_nan_coordinates(self) -> None:
        door = Door(
            location=Point2D(x=math.nan, y=0.0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.error_count == 1
        assert result.errors[0].code == DOOR_INVALID_GEOMETRY
    
    def test_infinite_coordinates(self) -> None:
        door = Door(
            location=Point2D(x=math.inf, y=0.0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.error_count == 1
        assert result.errors[0].code == DOOR_INVALID_GEOMETRY
    
    def test_valid_location(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.is_valid is True


class TestDoorValidatorWidth:
    """Tests for width validation."""
    
    def test_zero_width(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=0.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.error_count == 1
        assert result.errors[0].code == DOOR_INVALID_WIDTH
    
    def test_negative_width(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=-1.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.error_count == 1
        assert result.errors[0].code == DOOR_INVALID_WIDTH
    
    def test_width_below_minimum(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=1.5,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.error_count == 1
        assert result.errors[0].code == DOOR_INVALID_WIDTH
    
    def test_width_above_maximum(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=8.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.warning_count == 1
        assert result.warnings[0].code == DOOR_INVALID_WIDTH
    
    def test_valid_width(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.is_valid is True


class TestDoorValidatorHeight:
    """Tests for height validation."""
    
    def test_zero_height(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            height=0.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.error_count == 1
        assert result.errors[0].code == DOOR_INVALID_HEIGHT
    
    def test_negative_height(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            height=-2.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.error_count == 1
        assert result.errors[0].code == DOOR_INVALID_HEIGHT
    
    def test_height_below_minimum(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            height=5.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.error_count == 1
        assert result.errors[0].code == DOOR_INVALID_HEIGHT
    
    def test_height_above_maximum(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            height=10.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.warning_count == 1
        assert result.warnings[0].code == DOOR_INVALID_HEIGHT
    
    def test_valid_height(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            height=7.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.is_valid is True
    
    def test_no_height_set(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.is_valid is True


class TestDoorValidatorType:
    """Tests for door type validation."""
    
    def test_unknown_type_allowed(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.UNKNOWN,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        config = DoorValidationConfig(allow_unknown_type=True)
        validator = DoorValidator(config)
        result = validator.validate(door)
        assert result.warning_count == 1
        assert result.warnings[0].code == DOOR_INVALID_TYPE
    
    def test_unknown_type_disallowed(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.UNKNOWN,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        config = DoorValidationConfig(allow_unknown_type=False)
        validator = DoorValidator(config)
        result = validator.validate(door)
        assert result.error_count == 1
        assert result.errors[0].code == DOOR_INVALID_TYPE
    
    def test_valid_type(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.is_valid is True


class TestDoorValidatorFloor:
    """Tests for floor ID validation."""
    
    def test_missing_floor_id(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.error_count == 1
        assert result.errors[0].code == DOOR_MISSING_FLOOR
    
    def test_empty_floor_id(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.error_count == 1
        assert result.errors[0].code == DOOR_MISSING_FLOOR
    
    def test_valid_floor_id(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.is_valid is True


class TestDoorValidatorPlacement:
    """Tests for placement validation."""
    
    def test_missing_wall_id_required(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            floor_id="floor-1",
        )
        config = DoorValidationConfig(require_wall_id=True)
        validator = DoorValidator(config)
        result = validator.validate(door)
        assert result.error_count == 1
        assert result.errors[0].code == DOOR_MISSING_WALL
    
    def test_missing_wall_id_not_required(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            floor_id="floor-1",
        )
        config = DoorValidationConfig(require_wall_id=False)
        validator = DoorValidator(config)
        result = validator.validate(door)
        assert result.is_valid is True
    
    def test_valid_wall_id(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.is_valid is True
    
    def test_missing_room_connection_required(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        config = DoorValidationConfig(require_room_connection=True)
        validator = DoorValidator(config)
        result = validator.validate(door)
        assert result.error_count == 1
        assert result.errors[0].code == DOOR_MISSING_ROOM_CONNECTION
    
    def test_missing_room_connection_not_required(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        config = DoorValidationConfig(require_room_connection=False)
        validator = DoorValidator(config)
        result = validator.validate(door)
        assert result.is_valid is True
    
    def test_valid_room_connection(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            room_ids=frozenset(["room-1"]),
            floor_id="floor-1",
        )
        config = DoorValidationConfig(require_room_connection=True)
        validator = DoorValidator(config)
        result = validator.validate(door)
        assert result.is_valid is True


class TestDoorValidatorMultipleErrors:
    """Tests for multiple simultaneous errors."""
    
    def test_multiple_errors(self) -> None:
        door = Door(
            location=Point2D(x=math.nan, y=0.0),
            width=0.0,
            height=-1.0,
            door_type=DoorType.UNKNOWN,
        )
        config = DoorValidationConfig(allow_unknown_type=False)
        validator = DoorValidator(config)
        result = validator.validate(door)
        assert result.error_count >= 4  # geometry, width, height, type, floor
    
    def test_error_and_warning(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=8.0,
            door_type=DoorType.UNKNOWN,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.error_count == 0
        assert result.warning_count == 2  # unknown type, wide door


class TestDoorValidatorEdgeCases:
    """Tests for edge cases."""
    
    def test_non_door_entity(self) -> None:
        validator = DoorValidator()
        result = validator.validate("not a door")
        assert result.error_count == 1
    
    def test_none_entity(self) -> None:
        validator = DoorValidator()
        result = validator.validate(None)
        assert result.error_count == 1
    
    def test_validate_many(self) -> None:
        valid_door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        invalid_door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-2",
        )
        validator = DoorValidator()
        result = validator.validate_many([valid_door, invalid_door])
        assert result.error_count == 1  # missing floor_id only
    
    def test_validate_many_empty_list(self) -> None:
        validator = DoorValidator()
        result = validator.validate_many([])
        assert result.is_valid is True
    
    def test_exterior_door(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            height=7.0,
            door_type=DoorType.SINGLE_LEAF,
            wall_id="wall-1",
            floor_id="floor-1",
            is_exterior=True,
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.is_valid is True
    
    def test_door_with_swing_direction(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            height=7.0,
            door_type=DoorType.SINGLE_LEAF,
            swing_direction="left",
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.is_valid is True


class TestDoorValidatorSerialization:
    """Tests for serialization compatibility."""
    
    def test_error_includes_entity_id(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
        )
        validator = DoorValidator()
        result = validator.validate(door)
        assert result.errors[0].entity_id == door.id
        assert result.errors[0].entity_type == "Door"
    
    def test_result_can_serialize(self) -> None:
        door = Door.create(
            location=(5, 0),
            width=3.0,
            door_type=DoorType.SINGLE_LEAF,
        )
        validator = DoorValidator()
        result = validator.validate(door)
        d = result.to_dict()
        assert "errors" in d
        assert "warnings" in d
        assert "is_valid" in d


class TestDoorValidatorConfigAccess:
    """Tests for validator config access."""
    
    def test_config_property(self) -> None:
        config = DoorValidationConfig(max_width=4.0)
        validator = DoorValidator(config)
        assert validator.config.max_width == 4.0
    
    def test_default_config(self) -> None:
        validator = DoorValidator()
        assert validator.config.max_width == 6.0