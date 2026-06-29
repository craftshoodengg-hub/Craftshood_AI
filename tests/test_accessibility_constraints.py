"""Unit tests for Accessibility Constraints."""

from __future__ import annotations

import pytest

from building_model_v2.constraints import (
    AccessibilityConstraint,
    AccessibleBathroomConstraint,
    ConstraintCategory,
    ConstraintEngine,
    ConstraintResult,
    ConstraintSeverity,
    MinimumAccessibleDoorWidthConstraint,
    MinimumHallwayWidthConstraint,
    RampSlopeConstraint,
    StairHandrailConstraint,
    WheelchairTurningRadiusConstraint,
)
from building_model_v2.constraints.accessibility_constraints import (
    AccessibleBathroomConfig,
    MinimumAccessibleDoorWidthConfig,
    MinimumHallwayWidthConfig,
    RampSlopeConfig,
    StairHandrailConfig,
    WheelchairTurningRadiusConfig,
)
from building_model_v2.entities_opening import Door
from building_model_v2.entities_room import Room
from building_model_v2.entities_stair import Stair
from building_model_v2.types import DoorType, RoomType, StairType, WindowType
from building_model_v2.validation.cross_entity_validator import BuildingModel


# ============================================================================
# Helper functions
# ============================================================================


def create_room_with_area(
    area: float,
    ceiling_height: float | None = 8.0,
    room_type: RoomType = RoomType.LIVING,
    metadata: dict | None = None,
) -> Room:
    """Create a room with a specific area.
    
    Args:
        area: Room area in square feet.
        ceiling_height: Ceiling height in feet.
        room_type: Type of room.
        metadata: Optional metadata.
    
    Returns:
        Room with the specified area.
    """
    import math
    side = math.sqrt(area)
    return Room.create(
        vertices=[(0, 0), (side, 0), (side, side), (0, side)],
        room_type=room_type,
        ceiling_height=ceiling_height,
        metadata=metadata or {"name": f"Room_{area}sqft"},
    )


def create_corridor_with_width(width: float, length: float = 10.0) -> Room:
    """Create a corridor room with a specific width.
    
    Args:
        width: Corridor width in feet.
        length: Corridor length in feet.
    
    Returns:
        Room classified as corridor.
    """
    return Room.create(
        vertices=[(0, 0), (length, 0), (length, width), (0, width)],
        room_type=RoomType.CORRIDOR,
        metadata={"name": f"Corridor_{width}ft"},
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


def create_stair_with_width(width: float, handrail: bool = False) -> Stair:
    """Create a stair with a specific width.
    
    Args:
        width: Stair width in feet.
        handrail: Whether the stair has handrail metadata.
    
    Returns:
        Stair with the specified width.
    """
    metadata = {"handrail": handrail}
    return Stair.create(
        stair_type=StairType.STRAIGHT,
        width=width,
        start=(0, 0),
        end=(10, 0),
        metadata=metadata,
    )


# ============================================================================
# AccessibilityConstraint base class tests
# ============================================================================


class TestAccessibilityConstraint:
    """Tests for AccessibilityConstraint base class."""
    
    def test_category(self) -> None:
        constraint = MinimumAccessibleDoorWidthConstraint()
        assert constraint.category == ConstraintCategory.ACCESSIBILITY
    
    def test_default_severity(self) -> None:
        constraint = MinimumAccessibleDoorWidthConstraint()
        assert constraint.default_severity == ConstraintSeverity.WARNING
    
    def test_name_and_description(self) -> None:
        constraint = MinimumAccessibleDoorWidthConstraint()
        assert constraint.name == "Minimum Accessible Door Width"
        assert "accessible" in constraint.description.lower()


# ============================================================================
# MinimumAccessibleDoorWidthConstraint tests
# ============================================================================


class TestMinimumAccessibleDoorWidthConstraint:
    """Tests for MinimumAccessibleDoorWidthConstraint."""
    
    def test_default_config(self) -> None:
        constraint = MinimumAccessibleDoorWidthConstraint()
        assert constraint.config.minimum_width == 3.0
    
    def test_custom_config(self) -> None:
        config = MinimumAccessibleDoorWidthConfig(minimum_width=3.5)
        constraint = MinimumAccessibleDoorWidthConstraint(config=config)
        assert constraint.config.minimum_width == 3.5
    
    def test_valid_door(self) -> None:
        door = create_door_with_width(3.5)
        model = BuildingModel(doors={"door-1": door})
        constraint = MinimumAccessibleDoorWidthConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_invalid_door(self) -> None:
        door = create_door_with_width(2.5)
        model = BuildingModel(doors={"door-1": door})
        constraint = MinimumAccessibleDoorWidthConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "DOOR_WIDTH_BELOW_ACCESSIBLE_MINIMUM"
    
    def test_exact_threshold(self) -> None:
        door = create_door_with_width(3.0)
        model = BuildingModel(doors={"door-1": door})
        constraint = MinimumAccessibleDoorWidthConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_multiple_doors_mixed(self) -> None:
        door1 = create_door_with_width(3.5)
        door2 = create_door_with_width(2.5)
        door3 = create_door_with_width(3.0)
        model = BuildingModel(doors={"d1": door1, "d2": door2, "d3": door3})
        constraint = MinimumAccessibleDoorWidthConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].entity_id == "d2"
    
    def test_custom_threshold(self) -> None:
        door = create_door_with_width(3.0)
        model = BuildingModel(doors={"door-1": door})
        config = MinimumAccessibleDoorWidthConfig(minimum_width=3.5)
        constraint = MinimumAccessibleDoorWidthConstraint(config=config)
        result = constraint.evaluate(model)
        assert result.issue_count == 1
    
    def test_score_calculation(self) -> None:
        door = create_door_with_width(1.5)  # Half of minimum
        model = BuildingModel(doors={"door-1": door})
        constraint = MinimumAccessibleDoorWidthConstraint()
        result = constraint.evaluate(model)
        assert result.total_score > 0.0
    
    def test_no_score_for_valid(self) -> None:
        door = create_door_with_width(4.0)
        model = BuildingModel(doors={"door-1": door})
        constraint = MinimumAccessibleDoorWidthConstraint()
        result = constraint.evaluate(model)
        assert result.total_score == 0.0


# ============================================================================
# MinimumHallwayWidthConstraint tests
# ============================================================================


class TestMinimumHallwayWidthConstraint:
    """Tests for MinimumHallwayWidthConstraint."""
    
    def test_default_config(self) -> None:
        constraint = MinimumHallwayWidthConstraint()
        assert constraint.config.minimum_width == 3.5
    
    def test_custom_config(self) -> None:
        config = MinimumHallwayWidthConfig(minimum_width=4.0)
        constraint = MinimumHallwayWidthConstraint(config=config)
        assert constraint.config.minimum_width == 4.0
    
    def test_valid_hallway(self) -> None:
        corridor = create_corridor_with_width(4.0)
        model = BuildingModel(rooms={"corridor-1": corridor})
        constraint = MinimumHallwayWidthConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_invalid_hallway(self) -> None:
        corridor = create_corridor_with_width(3.0)
        model = BuildingModel(rooms={"corridor-1": corridor})
        constraint = MinimumHallwayWidthConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "HALLWAY_WIDTH_BELOW_MINIMUM"
    
    def test_exact_threshold(self) -> None:
        corridor = create_corridor_with_width(3.5)
        model = BuildingModel(rooms={"corridor-1": corridor})
        constraint = MinimumHallwayWidthConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_non_corridor_rooms_skipped(self) -> None:
        """Non-corridor rooms should be skipped, not flagged."""
        living = create_room_with_area(100.0, room_type=RoomType.LIVING)
        bedroom = create_room_with_area(100.0, room_type=RoomType.BEDROOM)
        model = BuildingModel(rooms={"living": living, "bedroom": bedroom})
        constraint = MinimumHallwayWidthConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_multiple_corridors_mixed(self) -> None:
        corridor1 = create_corridor_with_width(4.0)
        corridor2 = create_corridor_with_width(3.0)
        corridor3 = create_corridor_with_width(3.5)
        model = BuildingModel(rooms={"c1": corridor1, "c2": corridor2, "c3": corridor3})
        constraint = MinimumHallwayWidthConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].entity_id == "c2"
    
    def test_custom_threshold(self) -> None:
        corridor = create_corridor_with_width(3.5)
        model = BuildingModel(rooms={"corridor-1": corridor})
        config = MinimumHallwayWidthConfig(minimum_width=4.0)
        constraint = MinimumHallwayWidthConstraint(config=config)
        result = constraint.evaluate(model)
        assert result.issue_count == 1
    
    def test_score_calculation(self) -> None:
        corridor = create_corridor_with_width(1.75)  # Half of minimum
        model = BuildingModel(rooms={"corridor-1": corridor})
        constraint = MinimumHallwayWidthConstraint()
        result = constraint.evaluate(model)
        assert result.total_score > 0.0
    
    def test_no_score_for_valid(self) -> None:
        corridor = create_corridor_with_width(4.0)
        model = BuildingModel(rooms={"corridor-1": corridor})
        constraint = MinimumHallwayWidthConstraint()
        result = constraint.evaluate(model)
        assert result.total_score == 0.0


# ============================================================================
# WheelchairTurningRadiusConstraint tests (placeholder)
# ============================================================================


class TestWheelchairTurningRadiusConstraint:
    """Tests for WheelchairTurningRadiusConstraint (placeholder)."""
    
    def test_default_config(self) -> None:
        constraint = WheelchairTurningRadiusConstraint()
        assert constraint.config.minimum_radius == 5.0
    
    def test_custom_config(self) -> None:
        config = WheelchairTurningRadiusConfig(minimum_radius=6.0)
        constraint = WheelchairTurningRadiusConstraint(config=config)
        assert constraint.config.minimum_radius == 6.0
    
    def test_placeholder_returns_optimal(self) -> None:
        model = BuildingModel()
        constraint = WheelchairTurningRadiusConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_placeholder_with_rooms(self) -> None:
        room = create_room_with_area(100.0)
        model = BuildingModel(rooms={"room-1": room})
        constraint = WheelchairTurningRadiusConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True


# ============================================================================
# RampSlopeConstraint tests (placeholder)
# ============================================================================


class TestRampSlopeConstraint:
    """Tests for RampSlopeConstraint (placeholder)."""
    
    def test_default_config(self) -> None:
        constraint = RampSlopeConstraint()
        assert constraint.config.maximum_slope_ratio == 0.083
    
    def test_custom_config(self) -> None:
        config = RampSlopeConfig(maximum_slope_ratio=0.1)
        constraint = RampSlopeConstraint(config=config)
        assert constraint.config.maximum_slope_ratio == 0.1
    
    def test_placeholder_returns_optimal(self) -> None:
        model = BuildingModel()
        constraint = RampSlopeConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_placeholder_with_rooms(self) -> None:
        room = create_room_with_area(100.0)
        model = BuildingModel(rooms={"room-1": room})
        constraint = RampSlopeConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True


# ============================================================================
# AccessibleBathroomConstraint tests
# ============================================================================


class TestAccessibleBathroomConstraint:
    """Tests for AccessibleBathroomConstraint."""
    
    def test_default_config(self) -> None:
        constraint = AccessibleBathroomConstraint()
        assert constraint.config.require_accessible_metadata is True
    
    def test_custom_config(self) -> None:
        config = AccessibleBathroomConfig(require_accessible_metadata=False)
        constraint = AccessibleBathroomConstraint(config=config)
        assert constraint.config.require_accessible_metadata is False
    
    def test_default_severity_is_recommendation(self) -> None:
        constraint = AccessibleBathroomConstraint()
        assert constraint.default_severity == ConstraintSeverity.RECOMMENDATION
    
    def test_bathroom_with_accessible_metadata(self) -> None:
        bathroom = create_room_with_area(
            50.0,
            room_type=RoomType.BATHROOM,
            metadata={"accessible": True, "name": "Master Bath"},
        )
        model = BuildingModel(rooms={"bathroom-1": bathroom})
        constraint = AccessibleBathroomConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_bathroom_without_accessible_metadata(self) -> None:
        bathroom = create_room_with_area(
            50.0,
            room_type=RoomType.BATHROOM,
            metadata={"name": "Master Bath"},
        )
        model = BuildingModel(rooms={"bathroom-1": bathroom})
        constraint = AccessibleBathroomConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "BATHROOM_ACCESSIBILITY_MISSING"
    
    def test_non_bathroom_rooms_skipped(self) -> None:
        living = create_room_with_area(100.0, room_type=RoomType.LIVING)
        kitchen = create_room_with_area(100.0, room_type=RoomType.KITCHEN)
        model = BuildingModel(rooms={"living": living, "kitchen": kitchen})
        constraint = AccessibleBathroomConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_metadata_not_required_returns_optimal(self) -> None:
        bathroom = create_room_with_area(
            50.0,
            room_type=RoomType.BATHROOM,
            metadata={"name": "Master Bath"},
        )
        model = BuildingModel(rooms={"bathroom-1": bathroom})
        config = AccessibleBathroomConfig(require_accessible_metadata=False)
        constraint = AccessibleBathroomConstraint(config=config)
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_multiple_bathrooms_mixed(self) -> None:
        bathroom1 = create_room_with_area(
            50.0,
            room_type=RoomType.BATHROOM,
            metadata={"accessible": True, "name": "Bath 1"},
        )
        bathroom2 = create_room_with_area(
            40.0,
            room_type=RoomType.BATHROOM,
            metadata={"name": "Bath 2"},
        )
        model = BuildingModel(rooms={"b1": bathroom1, "b2": bathroom2})
        constraint = AccessibleBathroomConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].entity_id == "b2"


# ============================================================================
# StairHandrailConstraint tests
# ============================================================================


class TestStairHandrailConstraint:
    """Tests for StairHandrailConstraint."""
    
    def test_default_config(self) -> None:
        constraint = StairHandrailConstraint()
        assert constraint.config.require_handrail_metadata is True
    
    def test_custom_config(self) -> None:
        config = StairHandrailConfig(require_handrail_metadata=False)
        constraint = StairHandrailConstraint(config=config)
        assert constraint.config.require_handrail_metadata is False
    
    def test_stair_with_handrail_metadata(self) -> None:
        stair = create_stair_with_width(3.5, handrail=True)
        model = BuildingModel(stairs={"stair-1": stair})
        constraint = StairHandrailConstraint()
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_stair_without_handrail_metadata(self) -> None:
        stair = create_stair_with_width(3.5, handrail=False)
        model = BuildingModel(stairs={"stair-1": stair})
        constraint = StairHandrailConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 1
        assert result.issues[0].code == "STAIR_HANDRAIL_MISSING"
    
    def test_metadata_not_required_returns_optimal(self) -> None:
        stair = create_stair_with_width(3.5, handrail=False)
        model = BuildingModel(stairs={"stair-1": stair})
        config = StairHandrailConfig(require_handrail_metadata=False)
        constraint = StairHandrailConstraint(config=config)
        result = constraint.evaluate(model)
        assert result.is_optimal is True
    
    def test_multiple_stairs_mixed(self) -> None:
        stair1 = create_stair_with_width(3.5, handrail=True)
        stair2 = create_stair_with_width(3.0, handrail=False)
        stair3 = create_stair_with_width(4.0, handrail=False)
        model = BuildingModel(stairs={"s1": stair1, "s2": stair2, "s3": stair3})
        constraint = StairHandrailConstraint()
        result = constraint.evaluate(model)
        assert result.issue_count == 2
        issue_ids = {issue.entity_id for issue in result.issues}
        assert "s2" in issue_ids
        assert "s3" in issue_ids


# ============================================================================
# Constraint Engine Integration tests
# ============================================================================


class TestConstraintEngineIntegration:
    """Tests for constraint engine with accessibility constraints."""
    
    def test_engine_with_multiple_constraints(self) -> None:
        door = create_door_with_width(2.5)
        corridor = create_corridor_with_width(3.0)
        stair = create_stair_with_width(3.5, handrail=False)
        model = BuildingModel(
            doors={"door-1": door},
            rooms={"corridor-1": corridor},
            stairs={"stair-1": stair},
        )
        engine = ConstraintEngine()
        engine.register(MinimumAccessibleDoorWidthConstraint())
        engine.register(MinimumHallwayWidthConstraint())
        engine.register(StairHandrailConstraint())
        result = engine.evaluate(model)
        assert result.issue_count == 3
    
    def test_engine_all_valid(self) -> None:
        door = create_door_with_width(3.5)
        corridor = create_corridor_with_width(4.0)
        stair = create_stair_with_width(3.5, handrail=True)
        bathroom = create_room_with_area(
            50.0,
            room_type=RoomType.BATHROOM,
            metadata={"accessible": True},
        )
        model = BuildingModel(
            doors={"door-1": door},
            rooms={"corridor-1": corridor, "bathroom-1": bathroom},
            stairs={"stair-1": stair},
        )
        engine = ConstraintEngine()
        engine.register(MinimumAccessibleDoorWidthConstraint())
        engine.register(MinimumHallwayWidthConstraint())
        engine.register(StairHandrailConstraint())
        engine.register(AccessibleBathroomConstraint())
        result = engine.evaluate(model)
        assert result.is_optimal is True
    
    def test_engine_with_placeholders(self) -> None:
        """Placeholder constraints should always return optimal."""
        room = create_room_with_area(100.0)
        model = BuildingModel(rooms={"room-1": room})
        engine = ConstraintEngine()
        engine.register(WheelchairTurningRadiusConstraint())
        engine.register(RampSlopeConstraint())
        result = engine.evaluate(model)
        assert result.is_optimal is True


# ============================================================================
# Serialization tests
# ============================================================================


class TestSerialization:
    """Tests for serialization compatibility."""
    
    def test_door_width_issue_serialization(self) -> None:
        door = create_door_with_width(2.5)
        model = BuildingModel(doors={"door-1": door})
        constraint = MinimumAccessibleDoorWidthConstraint()
        result = constraint.evaluate(model)
        d = result.to_dict()
        assert d["issue_count"] == 1
        assert d["issues"][0]["code"] == "DOOR_WIDTH_BELOW_ACCESSIBLE_MINIMUM"
    
    def test_hallway_width_issue_serialization(self) -> None:
        corridor = create_corridor_with_width(3.0)
        model = BuildingModel(rooms={"corridor-1": corridor})
        constraint = MinimumHallwayWidthConstraint()
        result = constraint.evaluate(model)
        d = result.to_dict()
        assert d["issue_count"] == 1
        assert d["issues"][0]["code"] == "HALLWAY_WIDTH_BELOW_MINIMUM"
    
    def test_bathroom_issue_serialization(self) -> None:
        bathroom = create_room_with_area(
            50.0,
            room_type=RoomType.BATHROOM,
        )
        model = BuildingModel(rooms={"bathroom-1": bathroom})
        constraint = AccessibleBathroomConstraint()
        result = constraint.evaluate(model)
        d = result.to_dict()
        assert d["issue_count"] == 1
        assert d["issues"][0]["code"] == "BATHROOM_ACCESSIBILITY_MISSING"
    
    def test_stair_handrail_issue_serialization(self) -> None:
        stair = create_stair_with_width(3.5, handrail=False)
        model = BuildingModel(stairs={"stair-1": stair})
        constraint = StairHandrailConstraint()
        result = constraint.evaluate(model)
        d = result.to_dict()
        assert d["issue_count"] == 1
        assert d["issues"][0]["code"] == "STAIR_HANDRAIL_MISSING"
    
    def test_result_round_trip(self) -> None:
        door = create_door_with_width(2.5)
        model = BuildingModel(doors={"door-1": door})
        constraint = MinimumAccessibleDoorWidthConstraint()
        result = constraint.evaluate(model)
        d = result.to_dict()
        restored = ConstraintResult.from_dict(d)
        assert restored == result


# ============================================================================
# Metadata tests
# ============================================================================


class TestMetadata:
    """Tests for constraint metadata."""
    
    def test_door_width_constraint_metadata(self) -> None:
        constraint = MinimumAccessibleDoorWidthConstraint()
        assert constraint.name == "Minimum Accessible Door Width"
        assert "accessible" in constraint.description.lower()
        assert constraint.category == ConstraintCategory.ACCESSIBILITY
    
    def test_hallway_width_constraint_metadata(self) -> None:
        constraint = MinimumHallwayWidthConstraint()
        assert constraint.name == "Minimum Hallway Width"
        assert "hallway" in constraint.description.lower()
        assert constraint.category == ConstraintCategory.ACCESSIBILITY
    
    def test_turning_radius_constraint_metadata(self) -> None:
        constraint = WheelchairTurningRadiusConstraint()
        assert constraint.name == "Wheelchair Turning Radius"
        assert "placeholder" in constraint.description.lower()
        assert constraint.category == ConstraintCategory.ACCESSIBILITY
    
    def test_ramp_slope_constraint_metadata(self) -> None:
        constraint = RampSlopeConstraint()
        assert constraint.name == "Ramp Slope"
        assert "placeholder" in constraint.description.lower()
        assert constraint.category == ConstraintCategory.ACCESSIBILITY
    
    def test_bathroom_constraint_metadata(self) -> None:
        constraint = AccessibleBathroomConstraint()
        assert constraint.name == "Accessible Bathroom"
        assert "placeholder" in constraint.description.lower()
        assert constraint.category == ConstraintCategory.ACCESSIBILITY
    
    def test_stair_handrail_constraint_metadata(self) -> None:
        constraint = StairHandrailConstraint()
        assert constraint.name == "Stair Handrail"
        assert "placeholder" in constraint.description.lower()
        assert constraint.category == ConstraintCategory.ACCESSIBILITY