"""Unit tests for WallValidator."""

from __future__ import annotations

import pytest
from shapely.geometry import LineString

from building_model_v2.entities_wall import Wall
from building_model_v2.types import WallType
from building_model_v2.validation import (
    WallValidationConfig,
    WallValidator,
)
from building_model_v2.validation.wall_validator import (
    WALL_INVALID_GEOMETRY,
    WALL_INVALID_HEIGHT,
    WALL_INVALID_THICKNESS,
    WALL_INVALID_TYPE,
    WALL_MISSING_FLOOR_ID,
    WALL_TOO_LONG,
    WALL_TOO_SHORT,
    WALL_ZERO_LENGTH,
)


class TestWallValidationConfig:
    """Tests for WallValidationConfig."""
    
    def test_default_values(self) -> None:
        config = WallValidationConfig()
        assert config.min_wall_length == 1.0
        assert config.max_wall_length == 100.0
        assert config.min_wall_thickness == 0.1
        assert config.max_wall_thickness == 5.0
        assert config.min_wall_height == 1.0
        assert config.allow_zero_openings is True
    
    def test_custom_values(self) -> None:
        config = WallValidationConfig(
            min_wall_length=2.0,
            max_wall_length=50.0,
            min_wall_thickness=0.2,
            max_wall_thickness=3.0,
            min_wall_height=8.0,
            allow_zero_openings=False,
        )
        assert config.min_wall_length == 2.0
        assert config.max_wall_length == 50.0
        assert config.min_wall_thickness == 0.2
        assert config.max_wall_thickness == 3.0
        assert config.min_wall_height == 8.0
        assert config.allow_zero_openings is False


class TestWallValidatorValid:
    """Tests for valid wall validation."""
    
    def test_valid_wall(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            height=9.0,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.is_valid is True
        assert result.error_count == 0
    
    def test_valid_wall_without_height(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.INTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.is_valid is True
    
    def test_valid_wall_with_openings(self) -> None:
        wall = Wall(
            geometry=LineString([(0, 0), (10, 0)]),
            width=0.5,
            height=9.0,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
            door_ids=frozenset(["door-1"]),
            window_ids=frozenset(["window-1"]),
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.is_valid is True


class TestWallValidatorGeometry:
    """Tests for geometry validation."""
    
    def test_empty_geometry(self) -> None:
        wall = Wall(
            geometry=LineString(),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count == 1
        assert result.errors[0].code == WALL_INVALID_GEOMETRY
    
    def test_zero_length(self) -> None:
        # Wall with same start and end point
        wall = Wall.create(
            start=(5, 5),
            end=(5, 5),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count == 1
        assert result.errors[0].code == WALL_ZERO_LENGTH
    
    def test_valid_geometry(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.is_valid is True


class TestWallValidatorThickness:
    """Tests for thickness validation."""
    
    def test_zero_thickness(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.0,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count == 1
        assert result.errors[0].code == WALL_INVALID_THICKNESS
    
    def test_negative_thickness(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=-0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count == 1
        assert result.errors[0].code == WALL_INVALID_THICKNESS
    
    def test_thickness_below_minimum(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.05,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count == 1
        assert result.errors[0].code == WALL_INVALID_THICKNESS
    
    def test_thickness_above_maximum(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=10.0,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.warning_count == 1
        assert result.warnings[0].code == WALL_INVALID_THICKNESS
    
    def test_valid_thickness(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.is_valid is True


class TestWallValidatorHeight:
    """Tests for height validation."""
    
    def test_zero_height(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            height=0.0,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count == 1
        assert result.errors[0].code == WALL_INVALID_HEIGHT
    
    def test_negative_height(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            height=-5.0,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count == 1
        assert result.errors[0].code == WALL_INVALID_HEIGHT
    
    def test_height_below_minimum(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            height=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count == 1
        assert result.errors[0].code == WALL_INVALID_HEIGHT
    
    def test_valid_height(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            height=9.0,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.is_valid is True
    
    def test_no_height_set(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.is_valid is True


class TestWallValidatorLength:
    """Tests for length validation."""
    
    def test_too_short(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(0.5, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count == 1
        assert result.errors[0].code == WALL_TOO_SHORT
    
    def test_too_long(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(150, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count == 1
        assert result.errors[0].code == WALL_TOO_LONG
    
    def test_custom_length_threshold(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(15, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        config = WallValidationConfig(max_wall_length=10.0)
        validator = WallValidator(config)
        result = validator.validate(wall)
        assert result.error_count == 1
        assert result.errors[0].code == WALL_TOO_LONG
    
    def test_valid_length(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.is_valid is True


class TestWallValidatorType:
    """Tests for wall type validation."""
    
    def test_unknown_type(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.UNKNOWN,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.warning_count == 1
        assert result.warnings[0].code == WALL_INVALID_TYPE
    
    def test_valid_type(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.is_valid is True


class TestWallValidatorFloorId:
    """Tests for floor ID validation."""
    
    def test_missing_floor_id(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count == 1
        assert result.errors[0].code == WALL_MISSING_FLOOR_ID
    
    def test_empty_floor_id(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count == 1
        assert result.errors[0].code == WALL_MISSING_FLOOR_ID
    
    def test_valid_floor_id(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.is_valid is True


class TestWallValidatorOpenings:
    """Tests for openings validation."""
    
    def test_no_openings_allowed(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        config = WallValidationConfig(allow_zero_openings=True)
        validator = WallValidator(config)
        result = validator.validate(wall)
        assert result.is_valid is True
    
    def test_no_openings_disallowed(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        config = WallValidationConfig(allow_zero_openings=False)
        validator = WallValidator(config)
        result = validator.validate(wall)
        assert result.warning_count == 1
    
    def test_with_doors(self) -> None:
        wall = Wall(
            geometry=LineString([(0, 0), (10, 0)]),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
            door_ids=frozenset(["door-1"]),
        )
        config = WallValidationConfig(allow_zero_openings=False)
        validator = WallValidator(config)
        result = validator.validate(wall)
        assert result.is_valid is True
    
    def test_with_windows(self) -> None:
        wall = Wall(
            geometry=LineString([(0, 0), (10, 0)]),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
            window_ids=frozenset(["window-1"]),
        )
        config = WallValidationConfig(allow_zero_openings=False)
        validator = WallValidator(config)
        result = validator.validate(wall)
        assert result.is_valid is True


class TestWallValidatorMultipleErrors:
    """Tests for multiple simultaneous errors."""
    
    def test_multiple_errors(self) -> None:
        wall = Wall(
            geometry=LineString(),
            width=0.0,
            height=-1.0,
            wall_type=WallType.UNKNOWN,
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count >= 2  # invalid geometry, missing floor ID
    
    def test_error_and_warning(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=10.0,
            wall_type=WallType.UNKNOWN,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.error_count == 0
        assert result.warning_count == 2  # unknown type, thick warning


class TestWallValidatorEdgeCases:
    """Tests for edge cases."""
    
    def test_non_wall_entity(self) -> None:
        validator = WallValidator()
        result = validator.validate("not a wall")
        assert result.error_count == 1
    
    def test_none_entity(self) -> None:
        validator = WallValidator()
        result = validator.validate(None)
        assert result.error_count == 1
    
    def test_validate_many(self) -> None:
        valid_wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        invalid_wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
        )
        validator = WallValidator()
        result = validator.validate_many([valid_wall, invalid_wall])
        assert result.error_count == 1
    
    def test_validate_many_empty_list(self) -> None:
        validator = WallValidator()
        result = validator.validate_many([])
        assert result.is_valid is True
    
    def test_diagonal_wall(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 10),
            width=0.5,
            wall_type=WallType.EXTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.is_valid is True
    
    def test_vertical_wall(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(0, 10),
            width=0.5,
            wall_type=WallType.INTERIOR,
            floor_id="floor-1",
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.is_valid is True


class TestWallValidatorSerialization:
    """Tests for serialization compatibility."""
    
    def test_error_includes_entity_id(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
        )
        validator = WallValidator()
        result = validator.validate(wall)
        assert result.errors[0].entity_id == wall.id
        assert result.errors[0].entity_type == "Wall"
    
    def test_result_can_serialize(self) -> None:
        wall = Wall.create(
            start=(0, 0),
            end=(10, 0),
            width=0.5,
            wall_type=WallType.EXTERIOR,
        )
        validator = WallValidator()
        result = validator.validate(wall)
        d = result.to_dict()
        assert "errors" in d
        assert "warnings" in d
        assert "is_valid" in d


class TestWallValidatorConfigAccess:
    """Tests for validator config access."""
    
    def test_config_property(self) -> None:
        config = WallValidationConfig(max_wall_length=50.0)
        validator = WallValidator(config)
        assert validator.config.max_wall_length == 50.0
    
    def test_default_config(self) -> None:
        validator = WallValidator()
        assert validator.config.max_wall_length == 100.0