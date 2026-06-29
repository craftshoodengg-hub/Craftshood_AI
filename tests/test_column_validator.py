"""Unit tests for ColumnValidator."""

from __future__ import annotations

import math

import pytest

from building_model_v2.base import Point2D
from building_model_v2.entities_column import Column
from building_model_v2.types import ColumnType
from building_model_v2.validation import (
    ColumnValidationConfig,
    ColumnValidator,
)
from building_model_v2.validation.column_validator import (
    COLUMN_INVALID_GEOMETRY,
    COLUMN_INVALID_HEIGHT,
    COLUMN_INVALID_TYPE,
    COLUMN_INVALID_WIDTH,
    COLUMN_MISSING_FLOOR,
)


class TestColumnValidationConfig:
    """Tests for ColumnValidationConfig."""
    
    def test_default_values(self) -> None:
        config = ColumnValidationConfig()
        assert config.min_width == 0.5
        assert config.max_width == 4.0
        assert config.min_depth == 0.5
        assert config.max_depth == 4.0
        assert config.min_height == 6.0
        assert config.max_height == 20.0
        assert config.allow_unknown_type is True
        assert config.require_floor_id is True
    
    def test_custom_values(self) -> None:
        config = ColumnValidationConfig(
            min_width=1.0,
            max_width=3.0,
            min_depth=1.0,
            max_depth=3.0,
            min_height=8.0,
            max_height=15.0,
            allow_unknown_type=False,
            require_floor_id=False,
        )
        assert config.min_width == 1.0
        assert config.max_width == 3.0
        assert config.min_depth == 1.0
        assert config.max_depth == 3.0
        assert config.min_height == 8.0
        assert config.max_height == 15.0
        assert config.allow_unknown_type is False
        assert config.require_floor_id is False


class TestColumnValidatorValid:
    """Tests for valid column validation."""
    
    def test_valid_column(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            height=10.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.is_valid is True
        assert result.error_count == 0
    
    def test_valid_column_without_height(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.CIRCULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.is_valid is True
    
    def test_valid_column_non_load_bearing(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            height=10.0,
            column_type=ColumnType.SQUARE,
            floor_id="floor-1",
            is_load_bearing=False,
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.is_valid is True


class TestColumnValidatorGeometry:
    """Tests for geometry validation."""
    
    def test_nan_coordinates(self) -> None:
        column = Column(
            geometry=Point2D(x=math.nan, y=5.0),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.error_count == 1
        assert result.errors[0].code == COLUMN_INVALID_GEOMETRY
    
    def test_infinite_coordinates(self) -> None:
        column = Column(
            geometry=Point2D(x=math.inf, y=5.0),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.error_count == 1
        assert result.errors[0].code == COLUMN_INVALID_GEOMETRY
    
    def test_valid_location(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.is_valid is True


class TestColumnValidatorWidth:
    """Tests for width/size validation."""
    
    def test_zero_size(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=0.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.error_count == 1
        assert result.errors[0].code == COLUMN_INVALID_WIDTH
    
    def test_negative_size(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=-1.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.error_count == 1
        assert result.errors[0].code == COLUMN_INVALID_WIDTH
    
    def test_size_below_minimum(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=0.25,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.error_count == 1
        assert result.errors[0].code == COLUMN_INVALID_WIDTH
    
    def test_size_above_maximum(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=5.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.warning_count == 1
        assert result.warnings[0].code == COLUMN_INVALID_WIDTH
    
    def test_valid_size(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.is_valid is True


class TestColumnValidatorHeight:
    """Tests for height validation."""
    
    def test_zero_height(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            height=0.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.error_count == 1
        assert result.errors[0].code == COLUMN_INVALID_HEIGHT
    
    def test_negative_height(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            height=-5.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.error_count == 1
        assert result.errors[0].code == COLUMN_INVALID_HEIGHT
    
    def test_height_below_minimum(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            height=4.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.error_count == 1
        assert result.errors[0].code == COLUMN_INVALID_HEIGHT
    
    def test_height_above_maximum(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            height=25.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.warning_count == 1
        assert result.warnings[0].code == COLUMN_INVALID_HEIGHT
    
    def test_valid_height(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            height=10.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.is_valid is True
    
    def test_no_height_set(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.is_valid is True


class TestColumnValidatorType:
    """Tests for column type validation."""
    
    def test_unknown_type_allowed(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.UNKNOWN,
            floor_id="floor-1",
        )
        config = ColumnValidationConfig(allow_unknown_type=True)
        validator = ColumnValidator(config)
        result = validator.validate(column)
        assert result.warning_count == 1
        assert result.warnings[0].code == COLUMN_INVALID_TYPE
    
    def test_unknown_type_disallowed(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.UNKNOWN,
            floor_id="floor-1",
        )
        config = ColumnValidationConfig(allow_unknown_type=False)
        validator = ColumnValidator(config)
        result = validator.validate(column)
        assert result.error_count == 1
        assert result.errors[0].code == COLUMN_INVALID_TYPE
    
    def test_valid_types(self) -> None:
        for col_type in [ColumnType.RECTANGULAR, ColumnType.CIRCULAR, ColumnType.SQUARE]:
            column = Column.create(
                location=(5, 5),
                size=1.0,
                column_type=col_type,
                floor_id="floor-1",
            )
            validator = ColumnValidator()
            result = validator.validate(column)
            assert result.is_valid is True, f"Type '{col_type}' should be valid"


class TestColumnValidatorFloor:
    """Tests for floor ID validation."""
    
    def test_missing_floor_id(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.error_count == 1
        assert result.errors[0].code == COLUMN_MISSING_FLOOR
    
    def test_empty_floor_id(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.error_count == 1
        assert result.errors[0].code == COLUMN_MISSING_FLOOR
    
    def test_valid_floor_id(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.is_valid is True


class TestColumnValidatorMultipleErrors:
    """Tests for multiple simultaneous errors."""
    
    def test_multiple_errors(self) -> None:
        column = Column(
            geometry=Point2D(x=math.nan, y=5.0),
            size=0.0,
            column_type=ColumnType.UNKNOWN,
        )
        config = ColumnValidationConfig(allow_unknown_type=False)
        validator = ColumnValidator(config)
        result = validator.validate(column)
        assert result.error_count >= 3  # geometry, size, type, floor
    
    def test_error_and_warning(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=5.0,
            column_type=ColumnType.UNKNOWN,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.error_count == 0
        assert result.warning_count == 2  # unknown type, large size


class TestColumnValidatorEdgeCases:
    """Tests for edge cases."""
    
    def test_non_column_entity(self) -> None:
        validator = ColumnValidator()
        result = validator.validate("not a column")
        assert result.error_count == 1
    
    def test_none_entity(self) -> None:
        validator = ColumnValidator()
        result = validator.validate(None)
        assert result.error_count == 1
    
    def test_validate_many(self) -> None:
        valid_column = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
            floor_id="floor-1",
        )
        invalid_column = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
        )
        validator = ColumnValidator()
        result = validator.validate_many([valid_column, invalid_column])
        assert result.error_count == 1  # missing floor_id only
    
    def test_validate_many_empty_list(self) -> None:
        validator = ColumnValidator()
        result = validator.validate_many([])
        assert result.is_valid is True
    
    def test_circular_column(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=2.0,
            height=12.0,
            column_type=ColumnType.CIRCULAR,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.is_valid is True
    
    def test_square_column(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.5,
            height=10.0,
            column_type=ColumnType.SQUARE,
            floor_id="floor-1",
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.is_valid is True


class TestColumnValidatorSerialization:
    """Tests for serialization compatibility."""
    
    def test_error_includes_entity_id(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        assert result.errors[0].entity_id == column.id
        assert result.errors[0].entity_type == "Column"
    
    def test_result_can_serialize(self) -> None:
        column = Column.create(
            location=(5, 5),
            size=1.0,
            column_type=ColumnType.RECTANGULAR,
        )
        validator = ColumnValidator()
        result = validator.validate(column)
        d = result.to_dict()
        assert "errors" in d
        assert "warnings" in d
        assert "is_valid" in d


class TestColumnValidatorConfigAccess:
    """Tests for validator config access."""
    
    def test_config_property(self) -> None:
        config = ColumnValidationConfig(max_width=3.0)
        validator = ColumnValidator(config)
        assert validator.config.max_width == 3.0
    
    def test_default_config(self) -> None:
        validator = ColumnValidator()
        assert validator.config.max_width == 4.0