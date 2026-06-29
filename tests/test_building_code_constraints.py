"""Unit tests for Building Code Constraints."""

from __future__ import annotations

import pytest

from building_model_v2.constraints import (
    BuildingCodeConstraint,
    CeilingHeightConstraint,
    ConstraintCategory,
    ConstraintEngine,
    ConstraintResult,
    ConstraintSeverity,
    MaximumTravelDistanceConstraint,
    MinimumDoorWidthConstraint,
    MinimumRoomAreaConstraint,
    MinimumWindowAreaConstraint,
    StairWidthConstraint,
)
from building_model_v2.constraints.building_code_constraints import (
    MaximumTravelDistanceConfig,
    MinimumCeilingHeightConfig,
    MinimumDoorWidthConfig,
    MinimumRoomAreaConfig,
    MinimumStairWidthConfig,
    MinimumWindowAreaConfig,
)
from building_model_v2.entities_opening import Door, Window
from building_model_v2.entities_room import Room
from building_model_v2.entities_stair import Stair
from building_model_v2.types import DoorType, FloorType, RoomType, StairType, WindowType
from building_model_v2.validation.cross_entity_validator import BuildingModel


# ============================================================================
# Helper functions
# ============================================================================


def create_room_with_area(area: float, ceiling_height: float | None = 8.0) -> Room:
    """Create a room with a specific area.
    
    Args:
        area: Room area in square feet.
        ceiling_height: Ceiling height in feet.
    
    Returns:
        Room with the specified area.
    """
    # Calculate side length for a square room
    import math
    side = math.sqrt(area)
    return Room.create(
        vertices=[(0, 0), (side, 0), (side, side), (0, side)],
        room_type=RoomType.LIVING,
        ceiling_height=ceiling_height,
        metadata={"name": f"Room_{area}sqft"},
    )


def create_door_with_width(width: float) -> Door:
    """Create a door with a specific width.
    
    Args:
        width: Door width in feet.
    
    Returns:
        Door with the specified width.
    """
    return Door.create(
        location=(0, 0),
        width=width,
        height=6.5,
        door_type=DoorType.SINGLE_LEAF,
    )


def create_window_with_area(width: float, height: float) -> Window:
    """Create a window with a specific area.
    
    Args:
        width: Window width in feet.
        height: Window height in feet.
    
    Returns:
        Window with the specified dimensions.
    """
    return Window.create(
        location=(0, 0),
        width=width,
        height=height,
        window_type=WindowType.FIXED,
    )


def create_stair_with_width(width: float) -> Stair:
    """Create a stair with a specific width.
    
    Args:
        width: Stair width in feet.
    
    Returns:
        Stair with the specified width.
    """
    from shapely.geometry import LineString
    return Stair.create(
        stair_type=StairType.STRAIGHT,
        width=width,
        start=(0, 0),
        end=(10, 0),
    )


# ============================================================================
# BuildingCodeConstraint base class tests
# ============================================================================


class TestBuildingCodeConstraint:
    """Tests for BuildingCodeConstraint base class."""
    
    def test_category(self) -> None:
        constraint = MinimumRoomAreaConstraint()
        assert constraint.category == ConstraintCategory.BUILDING_CODE
    
    def test_default_severity(self) -> None:
        constraint = MinimumRoomAreaConstraint()
        assert constraint.default_severity == ConstraintSeverity.WARNING
    
    def test_name_and_description(self) -> None:
        constraint = MinimumRoomAreaConstraint()
        assert constraint.name == "Minimum Room Area"
        assert "minimum" in constraint.description.lower()


# ============================================================================
# MinimumRoomAreaConstraint tests
# ============================================================================


class TestMinimumRoomAreaConstraint:
    """Tests for MinimumRoomAreaConstraint."""
    
    def test_default_config(self) -> None:
        constraint = MinimumRoomAreaConstraint()
        assert constraint.config.minimum_area == 70.0
    
    def test_custom_config(self) -> None:
        config = MinimumRoomAreaConfig(minimum_area=100.0)
        constraint = MinimumRoomAreaConstraint(config=config)
        assert constraint.config.minimum_area == 100.0
    
    def test_valid_room(self) -> None:
        room = create_room_with_area(100.0)
        model = BuildingModel(rooms={"room-1": room})
        constraint = MinimumRoomAreaConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_invalid_room(self) -> None:
        room = create_room_with_area(50.0)
        model = BuildingModel(rooms={"room-1": room})
        constraint = MinimumRoomAreaConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "ROOM_AREA_BELOW_MINIMUM"
    
    def test_exact_threshold(self) -> None:
        room = create_room_with_area(70.0)
        model = BuildingModel(rooms={"room-1": room})
        constraint = MinimumRoomAreaConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_multiple_rooms_mixed(self) -> None:
        room1 = create_room_with_area(100.0)
        room2 = create_room_with_area(50.0)
        room3 = create_room_with_area(80.0)
        model = BuildingModel(rooms={"r1": room1, "r2": room2, "r3": room3})
        constraint = MinimumRoomAreaConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].entity_id == "r2"
    
    def test_custom_threshold(self) -> None:
        room = create_room_with_area(80.0)
        model = BuildingModel(rooms={"room-1": room})
        config = MinimumRoomAreaConfig(minimum_area=100.0)
        constraint = MinimumRoomAreaConstraint(config=config)
        result = constraint.evaluate(model)
        assert result.issue_count == 1


# ============================================================================
# MinimumDoorWidthConstraint tests
# ============================================================================


class TestMinimumDoorWidthConstraint:
    """Tests for MinimumDoorWidthConstraint."""
    
    def test_default_config(self) -> None:
        constraint = MinimumDoorWidthConstraint()
        assert constraint.config.minimum_width == 2.5
    
    def test_custom_config(self) -> None:
        config = MinimumDoorWidthConfig(minimum_width=3.0)
        constraint = MinimumDoorWidthConstraint(config=config)
        assert constraint.config.minimum_width == 3.0
    
    def test_valid_door(self) -> None:
        door = create_door_with_width(3.0)
        model = BuildingModel(doors={"door-1": door})
        constraint = MinimumDoorWidthConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_invalid_door(self) -> None:
        door = create_door_with_width(2.0)
        model = BuildingModel(doors={"door-1": door})
        constraint = MinimumDoorWidthConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "DOOR_WIDTH_BELOW_MINIMUM"
    
    def test_exact_threshold(self) -> None:
        door = create_door_with_width(2.5)
        model = BuildingModel(doors={"door-1": door})
        constraint = MinimumDoorWidthConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_multiple_doors_mixed(self) -> None:
        door1 = create_door_with_width(3.0)
        door2 = create_door_with_width(2.0)
        door3 = create_door_with_width(2.5)
        model = BuildingModel(doors={"d1": door1, "d2": door2, "d3": door3})
        constraint = MinimumDoorWidthConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].entity_id == "d2"


# ============================================================================
# MinimumWindowAreaConstraint tests
# ============================================================================


class TestMinimumWindowAreaConstraint:
    """Tests for MinimumWindowAreaConstraint."""
    
    def test_default_config(self) -> None:
        constraint = MinimumWindowAreaConstraint()
        assert constraint.config.minimum_area == 3.0
    
    def test_custom_config(self) -> None:
        config = MinimumWindowAreaConfig(minimum_area=5.0)
        constraint = MinimumWindowAreaConstraint(config=config)
        assert constraint.config.minimum_area == 5.0
    
    def test_valid_window(self) -> None:
        window = create_window_with_area(2.0, 2.0)  # 4 sq ft
        model = BuildingModel(windows={"window-1": window})
        constraint = MinimumWindowAreaConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_invalid_window(self) -> None:
        window = create_window_with_area(1.0, 2.0)  # 2 sq ft
        model = BuildingModel(windows={"window-1": window})
        constraint = MinimumWindowAreaConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "WINDOW_AREA_BELOW_MINIMUM"
    
    def test_window_without_height(self) -> None:
        window = Window.create(
            location=(0, 0),
            width=2.0,
            height=None,
            window_type=WindowType.FIXED,
        )
        model = BuildingModel(windows={"window-1": window})
        constraint = MinimumWindowAreaConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True  # Skipped due to missing height

    def test_multiple_windows_mixed(self) -> None:
        window1 = create_window_with_area(2.0, 2.0)  # 4 sq ft
        window2 = create_window_with_area(1.0, 2.0)  # 2 sq ft
        window3 = create_window_with_area(1.5, 2.0)  # 3 sq ft
        model = BuildingModel(windows={"w1": window1, "w2": window2, "w3": window3})
        constraint = MinimumWindowAreaConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].entity_id == "w2"


# ============================================================================
# StairWidthConstraint tests
# ============================================================================


class TestStairWidthConstraint:
    """Tests for StairWidthConstraint."""
    
    def test_default_config(self) -> None:
        constraint = StairWidthConstraint()
        assert constraint.config.minimum_width == 3.0
    
    def test_custom_config(self) -> None:
        config = MinimumStairWidthConfig(minimum_width=4.0)
        constraint = StairWidthConstraint(config=config)
        assert constraint.config.minimum_width == 4.0
    
    def test_valid_stair(self) -> None:
        stair = create_stair_with_width(3.5)
        model = BuildingModel(stairs={"stair-1": stair})
        constraint = StairWidthConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_invalid_stair(self) -> None:
        stair = create_stair_with_width(2.5)
        model = BuildingModel(stairs={"stair-1": stair})
        constraint = StairWidthConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "STAIR_WIDTH_BELOW_MINIMUM"
    
    def test_exact_threshold(self) -> None:
        stair = create_stair_with_width(3.0)
        model = BuildingModel(stairs={"stair-1": stair})
        constraint = StairWidthConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_multiple_stairs_mixed(self) -> None:
        stair1 = create_stair_with_width(3.5)
        stair2 = create_stair_with_width(2.5)
        stair3 = create_stair_with_width(3.0)
        model = BuildingModel(stairs={"s1": stair1, "s2": stair2, "s3": stair3})
        constraint = StairWidthConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].entity_id == "s2"


# ============================================================================
# CeilingHeightConstraint tests
# ============================================================================


class TestCeilingHeightConstraint:
    """Tests for CeilingHeightConstraint."""
    
    def test_default_config(self) -> None:
        constraint = CeilingHeightConstraint()
        assert constraint.config.minimum_height == 7.0
    
    def test_custom_config(self) -> None:
        config = MinimumCeilingHeightConfig(minimum_height=8.0)
        constraint = CeilingHeightConstraint(config=config)
        assert constraint.config.minimum_height == 8.0
    
    def test_valid_ceiling(self) -> None:
        room = create_room_with_area(100.0, ceiling_height=8.0)
        model = BuildingModel(rooms={"room-1": room})
        constraint = CeilingHeightConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_invalid_ceiling(self) -> None:
        room = create_room_with_area(100.0, ceiling_height=6.0)
        model = BuildingModel(rooms={"room-1": room})
        constraint = CeilingHeightConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "CEILING_HEIGHT_BELOW_MINIMUM"
    
    def test_exact_threshold(self) -> None:
        room = create_room_with_area(100.0, ceiling_height=7.0)
        model = BuildingModel(rooms={"room-1": room})
        constraint = CeilingHeightConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_room_without_ceiling_height(self) -> None:
        room = Room.create(
            vertices=[(0, 0), (10, 0), (10, 10), (0, 10)],
            room_type=RoomType.LIVING,
            ceiling_height=None,
        )
        model = BuildingModel(rooms={"room-1": room})
        constraint = CeilingHeightConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True  # Skipped due to missing height
    
    def test_multiple_rooms_mixed(self) -> None:
        room1 = create_room_with_area(100.0, ceiling_height=8.0)
        room2 = create_room_with_area(100.0, ceiling_height=6.0)
        room3 = create_room_with_area(100.0, ceiling_height=7.0)
        model = BuildingModel(rooms={"r1": room1, "r2": room2, "r3": room3})
        constraint = CeilingHeightConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].entity_id == "r2"


# ============================================================================
# MaximumTravelDistanceConstraint tests
# ============================================================================


class TestMaximumTravelDistanceConstraint:
    """Tests for MaximumTravelDistanceConstraint (placeholder)."""
    
    def test_default_config(self) -> None:
        constraint = MaximumTravelDistanceConstraint()
        assert constraint.config.maximum_distance == 75.0
    
    def test_custom_config(self) -> None:
        config = MaximumTravelDistanceConfig(maximum_distance=100.0)
        constraint = MaximumTravelDistanceConstraint(config=config)
        assert constraint.config.maximum_distance == 100.0
    
    def test_placeholder_returns_optimal(self) -> None:
        model = BuildingModel()
        constraint = MaximumTravelDistanceConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_placeholder_with_rooms(self) -> None:
        room = create_room_with_area(100.0)
        model = BuildingModel(rooms={"room-1": room})
        constraint = MaximumTravelDistanceConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True


# ============================================================================
# Constraint Engine Integration tests
# ============================================================================


class TestConstraintEngineIntegration:
    """Tests for constraint engine with building code constraints."""
    
    def test_engine_with_multiple_constraints(self) -> None:
        room = create_room_with_area(50.0, ceiling_height=6.0)
        door = create_door_with_width(2.0)
        stair = create_stair_with_width(2.5)
        model = BuildingModel(
            rooms={"room-1": room},
            doors={"door-1": door},
            stairs={"stair-1": stair},
        )
        engine = ConstraintEngine()
        engine.register(MinimumRoomAreaConstraint())
        engine.register(MinimumDoorWidthConstraint())
        engine.register(StairWidthConstraint())
        engine.register(CeilingHeightConstraint())
        result = engine.evaluate(model)
        assert result.issue_count == 4
    
    def test_engine_all_valid(self) -> None:
        room = create_room_with_area(100.0, ceiling_height=8.0)
        door = create_door_with_width(3.0)
        stair = create_stair_with_width(3.5)
        window = create_window_with_area(2.0, 2.0)
        model = BuildingModel(
            rooms={"room-1": room},
            doors={"door-1": door},
            stairs={"stair-1": stair},
            windows={"window-1": window},
        )
        engine = ConstraintEngine()
        engine.register(MinimumRoomAreaConstraint())
        engine.register(MinimumDoorWidthConstraint())
        engine.register(StairWidthConstraint())
        engine.register(CeilingHeightConstraint())
        engine.register(MinimumWindowAreaConstraint())
        result = engine.evaluate(model)
        assert result.is_optimal is True


# ============================================================================
# Serialization tests
# ============================================================================


class TestSerialization:
    """Tests for serialization compatibility."""
    
    def test_room_area_issue_serialization(self) -> None:
        room = create_room_with_area(50.0)
        model = BuildingModel(rooms={"room-1": room})
        constraint = MinimumRoomAreaConstraint()
        result = constraint.evaluate(model)
        d = result.to_dict()
        assert d["issue_count"] == 1
        assert d["issues"][0]["code"] == "ROOM_AREA_BELOW_MINIMUM"
    
    def test_door_width_issue_serialization(self) -> None:
        door = create_door_with_width(2.0)
        model = BuildingModel(doors={"door-1": door})
        constraint = MinimumDoorWidthConstraint()
        result = constraint.evaluate(model)
        d = result.to_dict()
        assert d["issue_count"] == 1
        assert d["issues"][0]["code"] == "DOOR_WIDTH_BELOW_MINIMUM"
    
    def test_result_round_trip(self) -> None:
        room = create_room_with_area(50.0)
        model = BuildingModel(rooms={"room-1": room})
        constraint = MinimumRoomAreaConstraint()
        result = constraint.evaluate(model)
        d = result.to_dict()
        restored = ConstraintResult.from_dict(d)
        assert restored == result


# ============================================================================
# Score calculation tests
# ============================================================================


class TestScoreCalculation:
    """Tests for quality score calculation."""
    
    def test_room_area_score(self) -> None:
        room = create_room_with_area(35.0)  # Half of minimum
        model = BuildingModel(rooms={"room-1": room})
        constraint = MinimumRoomAreaConstraint()
        result = constraint.evaluate(model)
        assert result.total_score > 0.0
    
    def test_door_width_score(self) -> None:
        door = create_door_with_width(1.25)  # Half of minimum
        model = BuildingModel(doors={"door-1": door})
        constraint = MinimumDoorWidthConstraint()
        result = constraint.evaluate(model)
        assert result.total_score > 0.0
    
    def test_no_score_for_valid(self) -> None:
        room = create_room_with_area(100.0)
        model = BuildingModel(rooms={"room-1": room})
        constraint = MinimumRoomAreaConstraint()
        result = constraint.evaluate(model)
        assert result.total_score == 0.0