"""Unit tests for RoomValidator."""

from __future__ import annotations

import pytest
from shapely.geometry import Polygon

from building_model_v2.entities_room import Room
from building_model_v2.types import RoomType
from building_model_v2.validation import (
    RoomValidationConfig,
    RoomValidator,
)
from building_model_v2.validation.room_validator import (
    ROOM_BAD_ASPECT_RATIO,
    ROOM_DUPLICATE_DOOR_IDS,
    ROOM_DUPLICATE_WALL_IDS,
    ROOM_DUPLICATE_WINDOW_IDS,
    ROOM_EMPTY_NAME,
    ROOM_INVALID_HEIGHT,
    ROOM_INVALID_POLYGON,
    ROOM_INVALID_TYPE,
    ROOM_LOW_COMPACTNESS,
    ROOM_MISSING_FLOOR_ID,
    ROOM_SELF_INTERSECTING,
    ROOM_ZERO_AREA,
)


class TestRoomValidationConfig:
    """Tests for RoomValidationConfig."""
    
    def test_default_values(self) -> None:
        config = RoomValidationConfig()
        assert config.min_ceiling_height == 6.0
        assert config.max_aspect_ratio == 5.0
        assert config.min_compactness == 0.3
        assert config.allow_unknown_type is True
    
    def test_custom_values(self) -> None:
        config = RoomValidationConfig(
            min_ceiling_height=8.0,
            max_aspect_ratio=3.0,
            min_compactness=0.5,
            allow_unknown_type=False,
        )
        assert config.min_ceiling_height == 8.0
        assert config.max_aspect_ratio == 3.0
        assert config.min_compactness == 0.5
        assert config.allow_unknown_type is False


class TestRoomValidatorValid:
    """Tests for valid room validation."""
    
    def test_valid_room(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            ceiling_height=9.0,
            metadata={"name": "Living Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.is_valid is True
        assert result.error_count == 0
    
    def test_valid_room_with_no_ceiling_height(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "Living Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.is_valid is True
    
    def test_valid_room_with_collections(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.BEDROOM,
            floor_id="floor-1",
            wall_ids=frozenset(["wall-1", "wall-2"]),
            door_ids=frozenset(["door-1"]),
            window_ids=frozenset(["window-1"]),
            metadata={"name": "Bedroom"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.is_valid is True


class TestRoomValidatorName:
    """Tests for room name validation."""
    
    def test_empty_name(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": ""},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.error_count == 1
        assert result.errors[0].code == ROOM_EMPTY_NAME
    
    def test_whitespace_only_name(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "   "},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.error_count == 1
        assert result.errors[0].code == ROOM_EMPTY_NAME
    
    def test_no_name_in_metadata(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.error_count == 1
        assert result.errors[0].code == ROOM_EMPTY_NAME


class TestRoomValidatorType:
    """Tests for room type validation."""
    
    def test_unknown_type_allowed_by_default(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.UNKNOWN,
            floor_id="floor-1",
            metadata={"name": "Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.error_count == 0
        assert result.warning_count == 1
        assert result.warnings[0].code == ROOM_INVALID_TYPE
    
    def test_unknown_type_disallowed(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.UNKNOWN,
            floor_id="floor-1",
            metadata={"name": "Room"},
        )
        config = RoomValidationConfig(allow_unknown_type=False)
        validator = RoomValidator(config)
        result = validator.validate(room)
        assert result.error_count == 1
        assert result.errors[0].code == ROOM_INVALID_TYPE
    
    def test_valid_type(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.KITCHEN,
            floor_id="floor-1",
            metadata={"name": "Kitchen"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.error_count == 0
        assert result.warning_count == 0


class TestRoomValidatorPolygon:
    """Tests for polygon geometry validation."""
    
    def test_empty_polygon(self) -> None:
        room = Room(
            room_type=RoomType.LIVING,
            polygon=Polygon(),
            floor_id="floor-1",
            metadata={"name": "Empty Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.error_count == 1
        assert result.errors[0].code == ROOM_INVALID_POLYGON
    
    def test_insufficient_vertices(self) -> None:
        # A polygon with only 3 vertices (triangle) is valid in Shapely
        # but our validator requires at least 4 coords (3 vertices + closure)
        # This test verifies that a triangle passes validation
        room = Room(
            room_type=RoomType.LIVING,
            polygon=Polygon([(0, 0), (1, 0), (0.5, 1)]),  # Triangle
            floor_id="floor-1",
            metadata={"name": "Triangle Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        # Triangle has 4 coords (3 vertices + closure), should pass
        assert result.is_valid is True
    
    def test_self_intersecting_polygon(self) -> None:
        # Bowtie shape - self-intersecting
        room = Room(
            room_type=RoomType.LIVING,
            polygon=Polygon([(0, 0), (10, 10), (10, 0), (0, 10)]),
            floor_id="floor-1",
            metadata={"name": "Bowtie Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.error_count >= 1
        assert any(e.code == ROOM_SELF_INTERSECTING for e in result.errors)
    
    def test_zero_area_polygon(self) -> None:
        # Collinear points - zero area
        # Shapely creates a valid polygon but with zero area
        room = Room(
            room_type=RoomType.LIVING,
            polygon=Polygon([(0, 0), (5, 0), (10, 0)]),
            floor_id="floor-1",
            metadata={"name": "Zero Area Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        # Should detect zero area
        assert result.error_count >= 1
    
    def test_valid_polygon(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "Good Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.is_valid is True


class TestRoomValidatorHeight:
    """Tests for ceiling height validation."""
    
    def test_negative_height(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            ceiling_height=-5.0,
            metadata={"name": "Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.error_count == 1
        assert result.errors[0].code == ROOM_INVALID_HEIGHT
    
    def test_zero_height(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            ceiling_height=0.0,
            metadata={"name": "Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.error_count == 1
        assert result.errors[0].code == ROOM_INVALID_HEIGHT
    
    def test_positive_height(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            ceiling_height=8.0,
            metadata={"name": "Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.is_valid is True
    
    def test_no_height_set(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.is_valid is True


class TestRoomValidatorFloorId:
    """Tests for floor ID validation."""
    
    def test_missing_floor_id(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            metadata={"name": "Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.error_count == 1
        assert result.errors[0].code == ROOM_MISSING_FLOOR_ID
    
    def test_empty_floor_id(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="",
            metadata={"name": "Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.error_count == 1
        assert result.errors[0].code == ROOM_MISSING_FLOOR_ID
    
    def test_valid_floor_id(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.is_valid is True


class TestRoomValidatorAspectRatio:
    """Tests for aspect ratio validation."""
    
    def test_bad_aspect_ratio(self) -> None:
        # Very long narrow room: 100x1 = aspect ratio 100
        room = Room.create(
            vertices=[(0, 0), (100, 0), (100, 1), (0, 1)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "Narrow Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.warning_count == 1
        assert result.warnings[0].code == ROOM_BAD_ASPECT_RATIO
    
    def test_acceptable_aspect_ratio(self) -> None:
        # Square room
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "Square Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.warning_count == 0
    
    def test_custom_aspect_ratio_threshold(self) -> None:
        # 3:1 ratio
        room = Room.create(
            vertices=[(0, 0), (30, 0), (30, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "Room"},
        )
        config = RoomValidationConfig(max_aspect_ratio=2.0)
        validator = RoomValidator(config)
        result = validator.validate(room)
        assert result.warning_count == 1
        assert result.warnings[0].code == ROOM_BAD_ASPECT_RATIO


class TestRoomValidatorCompactness:
    """Tests for compactness validation."""
    
    def test_low_compactness(self) -> None:
        # Use a very thin U-shape that will have low compactness
        # Compactness = area / bbox_area
        # Outer 100x10, inner cutout 98x8
        # Area = 232, bbox_area = 1000, compactness = 0.232
        room = Room.create(
            vertices=[
                (0, 0), (100, 0), (100, 10), (98, 10), (98, 2), (2, 2),
                (2, 10), (0, 10),
            ],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "Thin U-Shaped Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        # Thin U-shape should have compactness < 0.3
        assert result.warning_count >= 1
        assert any(w.code == ROOM_LOW_COMPACTNESS for w in result.warnings)
    
    def test_high_compactness(self) -> None:
        # Square room has high compactness
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "Square Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.warning_count == 0
    
    def test_custom_compactness_threshold(self) -> None:
        # U-shaped room
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (8, 10), (8, 2), (2, 2), (2, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "U-Shaped Room"},
        )
        config = RoomValidationConfig(min_compactness=0.9)
        validator = RoomValidator(config)
        result = validator.validate(room)
        assert result.warning_count == 1
        assert any(w.code == ROOM_LOW_COMPACTNESS for w in result.warnings)


class TestRoomValidatorCollections:
    """Tests for collection validation."""
    
    def test_no_duplicate_wall_ids(self) -> None:
        # Since wall_ids is a frozenset, duplicates are automatically prevented
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            wall_ids=frozenset(["wall-1", "wall-2"]),
            metadata={"name": "Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        # frozenset automatically removes duplicates, so this should be valid
        assert result.is_valid is True
    
    def test_no_duplicate_door_ids(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            door_ids=frozenset(["door-1", "door-2"]),
            metadata={"name": "Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.is_valid is True
    
    def test_no_duplicate_window_ids(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            window_ids=frozenset(["window-1", "window-2"]),
            metadata={"name": "Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.is_valid is True


class TestRoomValidatorMultipleErrors:
    """Tests for multiple simultaneous errors."""
    
    def test_multiple_errors(self) -> None:
        room = Room(
            room_type=RoomType.UNKNOWN,
            polygon=Polygon(),
            ceiling_height=-1.0,
            metadata={"name": ""},
        )
        config = RoomValidationConfig(allow_unknown_type=False)
        validator = RoomValidator(config)
        result = validator.validate(room)
        assert result.error_count >= 3  # empty name, invalid type, invalid polygon
    
    def test_error_and_warning(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (100, 0), (100, 1), (0, 1)],
            room_type=RoomType.UNKNOWN,
            floor_id="floor-1",
            metadata={"name": "Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.error_count == 0
        assert result.warning_count == 2  # unknown type, bad aspect ratio


class TestRoomValidatorEdgeCases:
    """Tests for edge cases."""
    
    def test_non_room_entity(self) -> None:
        validator = RoomValidator()
        result = validator.validate("not a room")
        assert result.error_count == 1
    
    def test_none_entity(self) -> None:
        validator = RoomValidator()
        result = validator.validate(None)
        assert result.error_count == 1
    
    def test_validate_many(self) -> None:
        valid_room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "Valid"},
        )
        invalid_room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": ""},
        )
        validator = RoomValidator()
        result = validator.validate_many([valid_room, invalid_room])
        assert result.error_count == 1
    
    def test_validate_many_empty_list(self) -> None:
        validator = RoomValidator()
        result = validator.validate_many([])
        assert result.is_valid is True
    
    def test_triangle_room(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (5, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "Triangle Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        # Triangle has 3 vertices + closure = 4 coords
        assert result.is_valid is True
    
    def test_complex_polygon(self) -> None:
        # Room with many vertices
        room = Room.create(
            vertices=[
                (0, 0), (5, 0), (10, 0), (10, 5), (10, 10),
                (5, 10), (0, 10), (0, 5),
            ],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": "Octagon Room"},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.is_valid is True


class TestRoomValidatorSerialization:
    """Tests for serialization compatibility."""
    
    def test_error_includes_entity_id(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": ""},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        assert result.errors[0].entity_id == room.id
        assert result.errors[0].entity_type == "Room"
    
    def test_result_can_serialize(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            floor_id="floor-1",
            metadata={"name": ""},
        )
        validator = RoomValidator()
        result = validator.validate(room)
        d = result.to_dict()
        assert "errors" in d
        assert "warnings" in d
        assert "is_valid" in d


class TestRoomValidatorConfigAccess:
    """Tests for validator config access."""
    
    def test_config_property(self) -> None:
        config = RoomValidationConfig(max_aspect_ratio=10.0)
        validator = RoomValidator(config)
        assert validator.config.max_aspect_ratio == 10.0
    
    def test_default_config(self) -> None:
        validator = RoomValidator()
        assert validator.config.max_aspect_ratio == 5.0