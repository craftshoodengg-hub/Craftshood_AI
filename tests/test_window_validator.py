"""Unit tests for WindowValidator."""

from __future__ import annotations

import math

import pytest

from building_model_v2.base import Point2D
from building_model_v2.entities_opening import Window
from building_model_v2.types import WindowType
from building_model_v2.validation import (
    WindowValidationConfig,
    WindowValidator,
)
from building_model_v2.validation.window_validator import (
    WINDOW_INVALID_GEOMETRY,
    WINDOW_INVALID_HEIGHT,
    WINDOW_INVALID_SILL_HEIGHT,
    WINDOW_INVALID_TYPE,
    WINDOW_INVALID_WIDTH,
    WINDOW_MISSING_FLOOR,
    WINDOW_MISSING_WALL,
)


class TestWindowValidationConfig:
    """Tests for WindowValidationConfig."""
    
    def test_default_values(self) -> None:
        config = WindowValidationConfig()
        assert config.min_width == 1.0
        assert config.max_width == 8.0
        assert config.min_height == 1.0
        assert config.max_height == 6.0
        assert config.min_sill_height == 0.0
        assert config.max_sill_height == 10.0
        assert config.allow_unknown_type is True
        assert config.require_wall_id is True
    
    def test_custom_values(self) -> None:
        config = WindowValidationConfig(
            min_width=2.0,
            max_width=6.0,
            min_height=2.0,
            max_height=5.0,
            min_sill_height=1.0,
            max_sill_height=8.0,
            allow_unknown_type=False,
            require_wall_id=False,
        )
        assert config.min_width == 2.0
        assert config.max_width == 6.0
        assert config.min_height == 2.0
        assert config.max_height == 5.0
        assert config.min_sill_height == 1.0
        assert config.max_sill_height == 8.0
        assert config.allow_unknown_type is False
        assert config.require_wall_id is False


class TestWindowValidatorValid:
    """Tests for valid window validation."""
    
    def test_valid_window(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            height=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True
        assert result.error_count == 0
    
    def test_valid_window_without_height(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True
    
    def test_valid_window_with_sill_height(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            height=4.0,
            sill_height=3.0,
            window_type=WindowType.CASEMENT,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True


class TestWindowValidatorGeometry:
    """Tests for geometry validation."""
    
    def test_nan_coordinates(self) -> None:
        window = Window(
            location=Point2D(x=math.nan, y=3.0),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_INVALID_GEOMETRY
    
    def test_infinite_coordinates(self) -> None:
        window = Window(
            location=Point2D(x=math.inf, y=3.0),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_INVALID_GEOMETRY
    
    def test_valid_location(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True


class TestWindowValidatorWidth:
    """Tests for width validation."""
    
    def test_zero_width(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=0.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_INVALID_WIDTH
    
    def test_negative_width(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=-1.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_INVALID_WIDTH
    
    def test_width_below_minimum(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=0.5,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_INVALID_WIDTH
    
    def test_width_above_maximum(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=10.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.warning_count == 1
        assert result.warnings[0].code == WINDOW_INVALID_WIDTH
    
    def test_valid_width(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True


class TestWindowValidatorHeight:
    """Tests for height validation."""
    
    def test_zero_height(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            height=0.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_INVALID_HEIGHT
    
    def test_negative_height(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            height=-2.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_INVALID_HEIGHT
    
    def test_height_below_minimum(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            height=0.5,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_INVALID_HEIGHT
    
    def test_height_above_maximum(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            height=8.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.warning_count == 1
        assert result.warnings[0].code == WINDOW_INVALID_HEIGHT
    
    def test_valid_height(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            height=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True
    
    def test_no_height_set(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True


class TestWindowValidatorSillHeight:
    """Tests for sill height validation."""
    
    def test_negative_sill_height(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            sill_height=-1.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_INVALID_SILL_HEIGHT
    
    def test_sill_height_below_minimum(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            sill_height=0.5,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        config = WindowValidationConfig(min_sill_height=1.0)
        validator = WindowValidator(config)
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_INVALID_SILL_HEIGHT
    
    def test_sill_height_above_maximum(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            sill_height=12.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.warning_count == 1
        assert result.warnings[0].code == WINDOW_INVALID_SILL_HEIGHT
    
    def test_valid_sill_height(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            sill_height=3.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True
    
    def test_no_sill_height_set(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True


class TestWindowValidatorType:
    """Tests for window type validation."""
    
    def test_unknown_type_allowed(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.UNKNOWN,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        config = WindowValidationConfig(allow_unknown_type=True)
        validator = WindowValidator(config)
        result = validator.validate(window)
        assert result.warning_count == 1
        assert result.warnings[0].code == WINDOW_INVALID_TYPE
    
    def test_unknown_type_disallowed(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.UNKNOWN,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        config = WindowValidationConfig(allow_unknown_type=False)
        validator = WindowValidator(config)
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_INVALID_TYPE
    
    def test_valid_type(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True


class TestWindowValidatorFloor:
    """Tests for floor ID validation."""
    
    def test_missing_floor_id(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_MISSING_FLOOR
    
    def test_empty_floor_id(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_MISSING_FLOOR
    
    def test_valid_floor_id(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True


class TestWindowValidatorPlacement:
    """Tests for placement validation."""
    
    def test_missing_wall_id_required(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            floor_id="floor-1",
        )
        config = WindowValidationConfig(require_wall_id=True)
        validator = WindowValidator(config)
        result = validator.validate(window)
        assert result.error_count == 1
        assert result.errors[0].code == WINDOW_MISSING_WALL
    
    def test_missing_wall_id_not_required(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            floor_id="floor-1",
        )
        config = WindowValidationConfig(require_wall_id=False)
        validator = WindowValidator(config)
        result = validator.validate(window)
        assert result.is_valid is True
    
    def test_valid_wall_id(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True


class TestWindowValidatorMultipleErrors:
    """Tests for multiple simultaneous errors."""
    
    def test_multiple_errors(self) -> None:
        window = Window(
            location=Point2D(x=math.nan, y=3.0),
            width=0.0,
            height=-1.0,
            window_type=WindowType.UNKNOWN,
        )
        config = WindowValidationConfig(allow_unknown_type=False)
        validator = WindowValidator(config)
        result = validator.validate(window)
        assert result.error_count >= 4  # geometry, width, height, type, floor
    
    def test_error_and_warning(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=10.0,
            window_type=WindowType.UNKNOWN,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.error_count == 0
        assert result.warning_count == 2  # unknown type, wide window


class TestWindowValidatorEdgeCases:
    """Tests for edge cases."""
    
    def test_non_window_entity(self) -> None:
        validator = WindowValidator()
        result = validator.validate("not a window")
        assert result.error_count == 1
    
    def test_none_entity(self) -> None:
        validator = WindowValidator()
        result = validator.validate(None)
        assert result.error_count == 1
    
    def test_validate_many(self) -> None:
        valid_window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        invalid_window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-2",
        )
        validator = WindowValidator()
        result = validator.validate_many([valid_window, invalid_window])
        assert result.error_count == 1  # missing floor_id only
    
    def test_validate_many_empty_list(self) -> None:
        validator = WindowValidator()
        result = validator.validate_many([])
        assert result.is_valid is True
    
    def test_exterior_window(self) -> None:
        window = Window.create(
            location=(3, 0),
            width=4.0,
            height=4.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
            is_exterior=True,
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True
    
    def test_window_at_ground_level(self) -> None:
        window = Window.create(
            location=(3, 0),
            width=4.0,
            height=4.0,
            sill_height=0.0,
            window_type=WindowType.FIXED,
            wall_id="wall-1",
            floor_id="floor-1",
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.is_valid is True


class TestWindowValidatorSerialization:
    """Tests for serialization compatibility."""
    
    def test_error_includes_entity_id(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
        )
        validator = WindowValidator()
        result = validator.validate(window)
        assert result.errors[0].entity_id == window.id
        assert result.errors[0].entity_type == "Window"
    
    def test_result_can_serialize(self) -> None:
        window = Window.create(
            location=(3, 3),
            width=4.0,
            window_type=WindowType.FIXED,
        )
        validator = WindowValidator()
        result = validator.validate(window)
        d = result.to_dict()
        assert "errors" in d
        assert "warnings" in d
        assert "is_valid" in d


class TestWindowValidatorConfigAccess:
    """Tests for validator config access."""
    
    def test_config_property(self) -> None:
        config = WindowValidationConfig(max_width=6.0)
        validator = WindowValidator(config)
        assert validator.config.max_width == 6.0
    
    def test_default_config(self) -> None:
        validator = WindowValidator()
        assert validator.config.max_width == 8.0