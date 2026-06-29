"""Unit tests for StairValidator."""

from __future__ import annotations

import pytest
from shapely.geometry import LineString

from building_model_v2.entities_stair import Stair
from building_model_v2.types import StairType
from building_model_v2.validation import (
    StairValidationConfig,
    StairValidator,
)
from building_model_v2.validation.stair_validator import (
    STAIR_INVALID_DIRECTION,
    STAIR_INVALID_GEOMETRY,
    STAIR_INVALID_STEP_COUNT,
    STAIR_INVALID_TYPE,
    STAIR_INVALID_WIDTH,
    STAIR_MISSING_CONNECTIONS,
    STAIR_MISSING_FLOOR,
    STAIR_ZERO_LENGTH,
)


# Helper config for tests not focused on connectivity
NO_CONNECTIVITY_CONFIG = StairValidationConfig(require_floor_connections=False)


class TestStairValidationConfig:
    """Tests for StairValidationConfig."""
    
    def test_default_values(self) -> None:
        config = StairValidationConfig()
        assert config.min_width == 2.5
        assert config.max_width == 6.0
        assert config.min_step_count == 3
        assert config.max_step_count == 50
        assert config.min_riser_height == 0.5
        assert config.max_riser_height == 0.85
        assert config.min_tread_depth == 0.75
        assert config.max_tread_depth == 1.25
        assert config.allow_unknown_type is True
        assert config.require_floor_connections is True
    
    def test_custom_values(self) -> None:
        config = StairValidationConfig(
            min_width=3.0,
            max_width=5.0,
            min_step_count=5,
            max_step_count=30,
            min_riser_height=0.6,
            max_riser_height=0.8,
            min_tread_depth=0.8,
            max_tread_depth=1.0,
            allow_unknown_type=False,
            require_floor_connections=False,
        )
        assert config.min_width == 3.0
        assert config.max_width == 5.0
        assert config.min_step_count == 5
        assert config.max_step_count == 30
        assert config.min_riser_height == 0.6
        assert config.max_riser_height == 0.8
        assert config.min_tread_depth == 0.8
        assert config.max_tread_depth == 1.0
        assert config.allow_unknown_type is False
        assert config.require_floor_connections is False


class TestStairValidatorValid:
    """Tests for valid stair validation."""
    
    def test_valid_stair(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            direction="both",
            connects_floors=("floor-1", "floor-2"),
            num_steps=15,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.is_valid is True
        assert result.error_count == 0
    
    def test_valid_stair_without_steps(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            direction="up",
            connects_floors=("floor-1", "floor-2"),
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.is_valid is True
    
    def test_valid_stair_without_floor_id(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            direction="both",
            connects_floors=("floor-1", "floor-2"),
            stair_type=StairType.STRAIGHT,
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.error_count == 1  # missing floor_id


class TestStairValidatorGeometry:
    """Tests for geometry validation."""
    
    def test_empty_geometry(self) -> None:
        stair = Stair(
            geometry=LineString(),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_INVALID_GEOMETRY
    
    def test_zero_length(self) -> None:
        stair = Stair.create(
            start=(5, 5),
            end=(5, 5),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_ZERO_LENGTH
    
    def test_valid_geometry(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.is_valid is True


class TestStairValidatorWidth:
    """Tests for width validation."""
    
    def test_zero_width(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=0.0,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_INVALID_WIDTH
    
    def test_negative_width(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=-1.0,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_INVALID_WIDTH
    
    def test_width_below_minimum(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=2.0,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_INVALID_WIDTH
    
    def test_width_above_maximum(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=8.0,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        validator = StairValidator(NO_CONNECTIVITY_CONFIG)
        result = validator.validate(stair)
        assert result.warning_count == 1
        assert result.warnings[0].code == STAIR_INVALID_WIDTH
    
    def test_valid_width(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        validator = StairValidator(NO_CONNECTIVITY_CONFIG)
        result = validator.validate(stair)
        assert result.is_valid is True


class TestStairValidatorStepCount:
    """Tests for step count validation."""
    
    def test_zero_step_count(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            num_steps=0,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_INVALID_STEP_COUNT
    
    def test_negative_step_count(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            num_steps=-5,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_INVALID_STEP_COUNT
    
    def test_step_count_below_minimum(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            num_steps=2,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_INVALID_STEP_COUNT
    
    def test_step_count_above_maximum(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            num_steps=60,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        validator = StairValidator(NO_CONNECTIVITY_CONFIG)
        result = validator.validate(stair)
        assert result.warning_count == 1
        assert result.warnings[0].code == STAIR_INVALID_STEP_COUNT
    
    def test_valid_step_count(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            num_steps=15,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.is_valid is True
    
    def test_no_step_count_set(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        validator = StairValidator(NO_CONNECTIVITY_CONFIG)
        result = validator.validate(stair)
        assert result.is_valid is True


class TestStairValidatorType:
    """Tests for stair type validation."""
    
    def test_unknown_type_allowed(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.UNKNOWN,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        config = StairValidationConfig(allow_unknown_type=True)
        validator = StairValidator(config)
        result = validator.validate(stair)
        assert result.warning_count == 1
        assert result.warnings[0].code == STAIR_INVALID_TYPE
    
    def test_unknown_type_disallowed(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.UNKNOWN,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        config = StairValidationConfig(allow_unknown_type=False)
        validator = StairValidator(config)
        result = validator.validate(stair)
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_INVALID_TYPE
    
    def test_valid_type(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.is_valid is True


class TestStairValidatorDirection:
    """Tests for direction validation."""
    
    def test_invalid_direction(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            direction="sideways",
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_INVALID_DIRECTION
    
    def test_valid_directions(self) -> None:
        for direction in ["up", "down", "both"]:
            stair = Stair.create(
                start=(0, 0),
                end=(10, 0),
                width=3.5,
                direction=direction,
                stair_type=StairType.STRAIGHT,
                floor_id="floor-1",
                connects_floors=("floor-1", "floor-2"),
            )
            validator = StairValidator()
            result = validator.validate(stair)
            assert result.is_valid is True, f"Direction '{direction}' should be valid"


class TestStairValidatorFloor:
    """Tests for floor ID validation."""
    
    def test_missing_floor_id(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_MISSING_FLOOR
    
    def test_empty_floor_id(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            connects_floors=("floor-1", "floor-2"),
            floor_id="",
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_MISSING_FLOOR
    
    def test_valid_floor_id(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.is_valid is True


class TestStairValidatorConnectivity:
    """Tests for connectivity validation."""
    
    def test_missing_connections_required(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        config = StairValidationConfig(require_floor_connections=True)
        validator = StairValidator(config)
        result = validator.validate(stair)
        assert result.error_count == 1
        assert result.errors[0].code == STAIR_MISSING_CONNECTIONS
    
    def test_missing_connections_not_required(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        config = StairValidationConfig(require_floor_connections=False)
        validator = StairValidator(config)
        result = validator.validate(stair)
        assert result.is_valid is True
    
    def test_partial_connections(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            connects_floors=("floor-1", None),
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.warning_count == 1
        assert result.warnings[0].code == STAIR_MISSING_CONNECTIONS
    
    def test_valid_connections(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            connects_floors=("floor-1", "floor-2"),
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.is_valid is True


class TestStairValidatorMultipleErrors:
    """Tests for multiple simultaneous errors."""
    
    def test_multiple_errors(self) -> None:
        stair = Stair(
            geometry=LineString(),
            width=0.0,
            stair_type=StairType.UNKNOWN,
        )
        config = StairValidationConfig(allow_unknown_type=False)
        validator = StairValidator(config)
        result = validator.validate(stair)
        assert result.error_count >= 3  # geometry, width, type, floor, connections
    
    def test_error_and_warning(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=8.0,
            stair_type=StairType.UNKNOWN,
            floor_id="floor-1",
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.error_count == 0
        assert result.warning_count == 2  # unknown type, wide stair


class TestStairValidatorEdgeCases:
    """Tests for edge cases."""
    
    def test_non_stair_entity(self) -> None:
        validator = StairValidator()
        result = validator.validate("not a stair")
        assert result.error_count == 1
    
    def test_none_entity(self) -> None:
        validator = StairValidator()
        result = validator.validate(None)
        assert result.error_count == 1
    
    def test_validate_many(self) -> None:
        valid_stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            connects_floors=("floor-1", "floor-2"),
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        invalid_stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            floor_id="floor-1",
        )
        validator = StairValidator()
        result = validator.validate_many([valid_stair, invalid_stair])
        assert result.error_count == 1  # missing connections only
    
    def test_validate_many_empty_list(self) -> None:
        validator = StairValidator()
        result = validator.validate_many([])
        assert result.is_valid is True
    
    def test_l_shaped_stair(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(5, 5),
            width=3.5,
            stair_type=StairType.L_SHAPED,
            connects_floors=("floor-1", "floor-2"),
            floor_id="floor-1",
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.is_valid is True
    
    def test_spiral_stair(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(3, 3),
            width=4.0,
            stair_type=StairType.SPIRAL,
            connects_floors=("floor-1", "floor-2"),
            floor_id="floor-1",
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.is_valid is True


class TestStairValidatorSerialization:
    """Tests for serialization compatibility."""
    
    def test_error_includes_entity_id(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        assert result.errors[0].entity_id == stair.id
        assert result.errors[0].entity_type == "Stair"
    
    def test_result_can_serialize(self) -> None:
        stair = Stair.create(
            start=(0, 0),
            end=(10, 0),
            width=3.5,
            stair_type=StairType.STRAIGHT,
            connects_floors=("floor-1", "floor-2"),
        )
        validator = StairValidator()
        result = validator.validate(stair)
        d = result.to_dict()
        assert "errors" in d
        assert "warnings" in d
        assert "is_valid" in d


class TestStairValidatorConfigAccess:
    """Tests for validator config access."""
    
    def test_config_property(self) -> None:
        config = StairValidationConfig(max_width=5.0)
        validator = StairValidator(config)
        assert validator.config.max_width == 5.0
    
    def test_default_config(self) -> None:
        validator = StairValidator()
        assert validator.config.max_width == 6.0