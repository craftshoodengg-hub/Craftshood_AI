"""Unit tests for FloorValidator."""

from __future__ import annotations

import math

import pytest

from building_model_v2.entities_floor import Floor
from building_model_v2.types import FloorType
from building_model_v2.validation import (
    FloorValidationConfig,
    FloorValidator,
)
from building_model_v2.validation.floor_validator import (
    FLOOR_EMPTY_COLLECTION,
    FLOOR_EMPTY_NAME,
    FLOOR_INVALID_HEIGHT,
    FLOOR_INVALID_LEVEL,
    FLOOR_INVALID_SLAB,
    FLOOR_INVALID_TYPE,
)


class TestFloorValidationConfig:
    """Tests for FloorValidationConfig."""
    
    def test_default_values(self) -> None:
        config = FloorValidationConfig()
        assert config.min_floor_height == 6.0
        assert config.max_floor_height == 30.0
        assert config.min_slab_thickness == 0.25
        assert config.max_slab_thickness == 3.0
        assert config.allow_negative_levels is True
        assert config.allow_empty_floor is True
    
    def test_custom_values(self) -> None:
        config = FloorValidationConfig(
            min_floor_height=8.0,
            max_floor_height=20.0,
            min_slab_thickness=0.5,
            max_slab_thickness=2.0,
            allow_negative_levels=False,
            allow_empty_floor=False,
        )
        assert config.min_floor_height == 8.0
        assert config.max_floor_height == 20.0
        assert config.min_slab_thickness == 0.5
        assert config.max_slab_thickness == 2.0
        assert config.allow_negative_levels is False
        assert config.allow_empty_floor is False


class TestFloorValidatorValid:
    """Tests for valid floor validation."""
    
    def test_valid_floor(self) -> None:
        floor = Floor.create(
            name="Ground Floor",
            level=0,
            elevation=0.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.GROUND,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.is_valid is True
        assert result.error_count == 0
    
    def test_valid_floor_with_collections(self) -> None:
        floor = Floor.create(
            name="First Floor",
            level=1,
            elevation=10.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.UPPER,
            room_ids=frozenset(["room-1", "room-2"]),
            wall_ids=frozenset(["wall-1", "wall-2"]),
            column_ids=frozenset(["col-1"]),
            stair_ids=frozenset(["stair-1"]),
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.is_valid is True


class TestFloorValidatorName:
    """Tests for name validation."""
    
    def test_empty_name(self) -> None:
        floor = Floor.create(
            name="",
            level=0,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.error_count == 1
        assert result.errors[0].code == FLOOR_EMPTY_NAME
    
    def test_whitespace_name(self) -> None:
        floor = Floor.create(
            name="   ",
            level=0,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.error_count == 1
        assert result.errors[0].code == FLOOR_EMPTY_NAME
    
    def test_valid_name(self) -> None:
        floor = Floor.create(
            name="Ground Floor",
            level=0,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.is_valid is True


class TestFloorValidatorLevel:
    """Tests for level validation."""
    
    def test_negative_level_allowed(self) -> None:
        floor = Floor.create(
            name="Basement",
            level=-1,
            elevation=-10.0,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        config = FloorValidationConfig(allow_negative_levels=True)
        validator = FloorValidator(config)
        result = validator.validate(floor)
        assert result.is_valid is True
    
    def test_negative_level_disallowed(self) -> None:
        floor = Floor.create(
            name="Basement",
            level=-1,
            elevation=-10.0,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        config = FloorValidationConfig(allow_negative_levels=False)
        validator = FloorValidator(config)
        result = validator.validate(floor)
        assert result.error_count == 1
        assert result.errors[0].code == FLOOR_INVALID_LEVEL
    
    def test_nan_elevation(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            elevation=math.nan,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.error_count == 1
        assert result.errors[0].code == FLOOR_INVALID_LEVEL
    
    def test_infinite_elevation(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            elevation=math.inf,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.error_count == 1
        assert result.errors[0].code == FLOOR_INVALID_LEVEL


class TestFloorValidatorHeight:
    """Tests for floor height validation."""
    
    def test_zero_height(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            floor_height=0.0,
            slab_thickness=0.5,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.error_count == 1
        assert result.errors[0].code == FLOOR_INVALID_HEIGHT
    
    def test_negative_height(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            floor_height=-5.0,
            slab_thickness=0.5,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.error_count == 1
        assert result.errors[0].code == FLOOR_INVALID_HEIGHT
    
    def test_height_below_minimum(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            floor_height=4.0,
            slab_thickness=0.5,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.error_count == 1
        assert result.errors[0].code == FLOOR_INVALID_HEIGHT
    
    def test_height_above_maximum(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            floor_height=35.0,
            slab_thickness=0.5,
            floor_type=FloorType.UPPER,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.warning_count == 1
        assert result.warnings[0].code == FLOOR_INVALID_HEIGHT
    
    def test_valid_height(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.is_valid is True


class TestFloorValidatorSlab:
    """Tests for slab thickness validation."""
    
    def test_zero_slab(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            floor_height=10.0,
            slab_thickness=0.0,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.error_count == 1
        assert result.errors[0].code == FLOOR_INVALID_SLAB
    
    def test_negative_slab(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            floor_height=10.0,
            slab_thickness=-0.5,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.error_count == 1
        assert result.errors[0].code == FLOOR_INVALID_SLAB
    
    def test_slab_below_minimum(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            floor_height=10.0,
            slab_thickness=0.1,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.error_count == 1
        assert result.errors[0].code == FLOOR_INVALID_SLAB
    
    def test_slab_above_maximum(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            floor_height=10.0,
            slab_thickness=4.0,
            floor_type=FloorType.UPPER,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.warning_count == 1
        assert result.warnings[0].code == FLOOR_INVALID_SLAB
    
    def test_valid_slab(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.is_valid is True


class TestFloorValidatorType:
    """Tests for floor type validation."""
    
    def test_unknown_type(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.UNKNOWN,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.warning_count == 1
        assert result.warnings[0].code == FLOOR_INVALID_TYPE
    
    def test_valid_types(self) -> None:
        for floor_type in [FloorType.GROUND, FloorType.UPPER, FloorType.ROOF, FloorType.BASEMENT, FloorType.MEZZANINE]:
            floor = Floor.create(
                name="Test Floor",
                level=0,
                floor_height=10.0,
                slab_thickness=0.5,
                floor_type=floor_type,
            )
            validator = FloorValidator()
            result = validator.validate(floor)
            assert result.is_valid is True, f"Type '{floor_type}' should be valid"


class TestFloorValidatorCollections:
    """Tests for collection validation."""
    
    def test_empty_floor_allowed(self) -> None:
        floor = Floor.create(
            name="Empty Floor",
            level=0,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        config = FloorValidationConfig(allow_empty_floor=True)
        validator = FloorValidator(config)
        result = validator.validate(floor)
        assert result.is_valid is True
    
    def test_empty_floor_disallowed(self) -> None:
        floor = Floor.create(
            name="Empty Floor",
            level=0,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        config = FloorValidationConfig(allow_empty_floor=False)
        validator = FloorValidator(config)
        result = validator.validate(floor)
        assert result.error_count == 1
        assert result.errors[0].code == FLOOR_EMPTY_COLLECTION
    
    def test_floor_with_rooms(self) -> None:
        floor = Floor.create(
            name="Standard Floor",
            level=0,
            floor_height=10.0,
            slab_thickness=0.5,
            room_ids=frozenset(["room-1", "room-2"]),
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.is_valid is True


class TestFloorValidatorMultipleErrors:
    """Tests for multiple simultaneous errors."""
    
    def test_multiple_errors(self) -> None:
        floor = Floor.create(
            name="",
            level=0,
            elevation=math.nan,
            floor_height=0.0,
            slab_thickness=0.0,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.error_count >= 3  # name, elevation, height, slab
    
    def test_error_and_warning(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            floor_height=35.0,
            slab_thickness=4.0,
            floor_type=FloorType.UNKNOWN,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.error_count == 0
        assert result.warning_count == 3  # unknown type, height, slab


class TestFloorValidatorEdgeCases:
    """Tests for edge cases."""
    
    def test_non_floor_entity(self) -> None:
        validator = FloorValidator()
        result = validator.validate("not a floor")
        assert result.error_count == 1
    
    def test_none_entity(self) -> None:
        validator = FloorValidator()
        result = validator.validate(None)
        assert result.error_count == 1
    
    def test_validate_many(self) -> None:
        valid_floor = Floor.create(
            name="Floor 1",
            level=0,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        invalid_floor = Floor.create(
            name="",
            level=0,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        validator = FloorValidator()
        result = validator.validate_many([valid_floor, invalid_floor])
        assert result.error_count == 1  # empty name only
    
    def test_validate_many_empty_list(self) -> None:
        validator = FloorValidator()
        result = validator.validate_many([])
        assert result.is_valid is True
    
    def test_ground_floor(self) -> None:
        floor = Floor.create(
            name="Ground Floor",
            level=0,
            elevation=0.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.GROUND,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.is_valid is True
    
    def test_basement_floor(self) -> None:
        floor = Floor.create(
            name="Basement",
            level=-1,
            elevation=-10.0,
            floor_height=10.0,
            slab_thickness=0.5,
            floor_type=FloorType.BASEMENT,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.is_valid is True
    
    def test_roof_floor(self) -> None:
        floor = Floor.create(
            name="Roof",
            level=5,
            elevation=50.0,
            floor_height=8.0,
            slab_thickness=0.5,
            floor_type=FloorType.ROOF,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.is_valid is True


class TestFloorValidatorSerialization:
    """Tests for serialization compatibility."""
    
    def test_error_includes_entity_id(self) -> None:
        floor = Floor.create(
            name="",
            level=0,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        assert result.errors[0].entity_id == floor.id
        assert result.errors[0].entity_type == "Floor"
    
    def test_result_can_serialize(self) -> None:
        floor = Floor.create(
            name="Test Floor",
            level=0,
            floor_height=10.0,
            slab_thickness=0.5,
        )
        validator = FloorValidator()
        result = validator.validate(floor)
        d = result.to_dict()
        assert "errors" in d
        assert "warnings" in d
        assert "is_valid" in d


class TestFloorValidatorConfigAccess:
    """Tests for validator config access."""
    
    def test_config_property(self) -> None:
        config = FloorValidationConfig(max_floor_height=20.0)
        validator = FloorValidator(config)
        assert validator.config.max_floor_height == 20.0
    
    def test_default_config(self) -> None:
        validator = FloorValidator()
        assert validator.config.max_floor_height == 30.0