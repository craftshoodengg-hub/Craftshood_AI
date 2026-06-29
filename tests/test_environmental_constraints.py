"""Unit tests for Environmental Constraints."""

from __future__ import annotations

import pytest
from shapely.geometry import Polygon

from building_model_v2.base import Point2D
from building_model_v2.constraints import (
    ConstraintCategory,
    ConstraintEngine,
    ConstraintScoreEngine,
    ConstraintSeverity,
    CrossVentilationConstraint,
    EnvironmentalConstraint,
    MinimumWindowToFloorAreaConstraint,
    MinimumWindowToFloorAreaConfig,
    NaturalLightConstraint,
    NaturalLightConfig,
    OutdoorConnectionConstraint,
    OutdoorConnectionConfig,
    SolarOrientationConstraint,
    SolarOrientationConfig,
    WestFacingHeatGainConstraint,
    WestFacingHeatGainConfig,
)
from building_model_v2.constraints.scoring import ConstraintWeightProfile
from building_model_v2.entities_opening import Window
from building_model_v2.entities_room import Room
from building_model_v2.types import RoomType, WindowType
from building_model_v2.validation.cross_entity_validator import BuildingModel


# ============================================================================
# Helper functions
# ============================================================================


def create_room(
    room_type: RoomType = RoomType.LIVING,
    vertices: list[tuple[float, float]] | None = None,
    window_ids: set[str] | None = None,
    metadata: dict | None = None,
) -> Room:
    """Create a test room."""
    if vertices is None:
        vertices = [(0, 0), (10, 0), (10, 10), (0, 10)]
    polygon = Polygon(vertices)
    return Room(
        room_type=room_type,
        polygon=polygon,
        window_ids=frozenset(window_ids or []),
        metadata=metadata or {},
    )


def create_window(
    width: float = 2.0,
    height: float | None = None,
    metadata: dict | None = None,
    location: tuple[float, float] = (0, 0),
) -> Window:
    """Create a test window."""
    if height is None:
        height = width
    return Window(
        window_type=WindowType.FIXED,
        width=width,
        height=height,
        location=Point2D(x=location[0], y=location[1]),
        metadata=metadata or {},
    )


def create_building_with_rooms(
    rooms: dict[str, Room] | None = None,
    windows: dict[str, Window] | None = None,
) -> BuildingModel:
    """Create a building model with rooms and windows."""
    return BuildingModel(
        rooms=rooms or {},
        windows=windows or {},
    )


# ============================================================================
# EnvironmentalConstraint base class tests
# ============================================================================


class TestEnvironmentalConstraint:
    """Tests for EnvironmentalConstraint base class."""
    
    def test_category(self) -> None:
        """Test that environmental constraints have correct category."""
        constraint = MinimumWindowToFloorAreaConstraint()
        assert constraint.category == ConstraintCategory.ENVIRONMENTAL
    
    def test_default_severity(self) -> None:
        """Test default severity is SUGGESTION."""
        constraint = MinimumWindowToFloorAreaConstraint()
        assert constraint.default_severity == ConstraintSeverity.SUGGESTION
    
    def test_custom_severity(self) -> None:
        """Test custom severity configuration."""
        from building_model_v2.constraints.environmental_constraints import (
            EnvironmentalConstraintConfig,
        )
        config = EnvironmentalConstraintConfig(severity=ConstraintSeverity.WARNING)
        constraint = MinimumWindowToFloorAreaConstraint(config=config)
        assert constraint.default_severity == ConstraintSeverity.WARNING
    
    def test_name_and_description(self) -> None:
        """Test name and description."""
        constraint = MinimumWindowToFloorAreaConstraint()
        assert constraint.name == "Minimum Window to Floor Area Ratio"
        assert "window area" in constraint.description.lower()
    
    def test_repr(self) -> None:
        """Test string representation."""
        constraint = MinimumWindowToFloorAreaConstraint()
        assert "MinimumWindowToFloorAreaConstraint" in repr(constraint)


# ============================================================================
# MinimumWindowToFloorAreaConstraint tests
# ============================================================================


class TestMinimumWindowToFloorAreaConstraint:
    """Tests for MinimumWindowToFloorAreaConstraint."""
    
    def test_below_minimum(self) -> None:
        """Test room with inadequate window-to-floor ratio."""
        room = create_room(window_ids={"win1"})
        window = create_window(width=4, height=1)  # Area = 4
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        constraint = MinimumWindowToFloorAreaConstraint()
        result = constraint.evaluate(building)
        
        # Room area = 100, window area = 4, ratio = 4% < 10%
        assert result.issue_count == 1
    
    def test_exceeds_minimum(self) -> None:
        """Test room exceeding minimum ratio."""
        room = create_room(window_ids={"win1"})
        # Window area = 20 (5x4), room area = 100, ratio = 20% > 10%
        window = create_window(width=5, height=4)
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        constraint = MinimumWindowToFloorAreaConstraint()
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_custom_ratio(self) -> None:
        """Test custom minimum ratio."""
        room = create_room(window_ids={"win1"})
        window = create_window(width=3, height=1)  # Area = 3
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        config = MinimumWindowToFloorAreaConfig(minimum_ratio=0.05)
        constraint = MinimumWindowToFloorAreaConstraint(config=config)
        result = constraint.evaluate(building)
        
        # Room area = 100, window area = 3, ratio = 3% < 5%
        assert result.issue_count == 1
    
    def test_no_windows(self) -> None:
        """Test room with no windows - should not trigger this constraint."""
        room = create_room(window_ids=set())
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = MinimumWindowToFloorAreaConstraint()
        result = constraint.evaluate(building)
        
        # No windows - constraint should skip (NaturalLightConstraint handles this)
        assert result.is_optimal
    
    def test_empty_room(self) -> None:
        """Test empty room polygon."""
        room = Room(room_type=RoomType.LIVING, polygon=Polygon())
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = MinimumWindowToFloorAreaConstraint()
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_multiple_rooms(self) -> None:
        """Test multiple rooms with different ratios."""
        room1 = create_room(window_ids={"win1"})
        room2 = create_room(window_ids={"win2"})
        
        # room1: window area = 4, ratio = 4% (fails)
        window1 = create_window(width=2, height=2)
        # room2: window area = 20, ratio = 20% (passes)
        window2 = create_window(width=5, height=4)
        
        building = create_building_with_rooms(
            rooms={"room1": room1, "room2": room2},
            windows={"win1": window1, "win2": window2},
        )
        
        constraint = MinimumWindowToFloorAreaConstraint()
        result = constraint.evaluate(building)
        
        assert result.issue_count == 1
    
    def test_issue_details(self) -> None:
        """Test issue details are correct."""
        room = create_room(window_ids={"win1"})
        window = create_window(width=2, height=1)  # Area = 2
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        constraint = MinimumWindowToFloorAreaConstraint()
        result = constraint.evaluate(building)
        
        assert result.issue_count == 1
        issue = result.issues[0]
        assert issue.code == "WINDOW_TO_FLOOR_RATIO_LOW"
        assert issue.entity_id == "room1"
        assert issue.severity == ConstraintSeverity.SUGGESTION


# ============================================================================
# CrossVentilationConstraint tests
# ============================================================================


class TestCrossVentilationConstraint:
    """Tests for CrossVentilationConstraint."""
    
    def test_sufficient_windows(self) -> None:
        """Test room with sufficient windows."""
        room = create_room(window_ids={"win1", "win2"})
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = CrossVentilationConstraint()
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_insufficient_windows(self) -> None:
        """Test room with insufficient windows."""
        room = create_room(window_ids={"win1"})
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = CrossVentilationConstraint()
        result = constraint.evaluate(building)
        
        assert result.issue_count == 1
    
    def test_no_windows(self) -> None:
        """Test room with no windows."""
        room = create_room(window_ids=set())
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = CrossVentilationConstraint()
        result = constraint.evaluate(building)
        
        assert result.issue_count == 1
    
    def test_custom_min_count(self) -> None:
        """Test custom minimum window count."""
        room = create_room(window_ids={"win1", "win2"})
        building = create_building_with_rooms(rooms={"room1": room})
        
        from building_model_v2.constraints.environmental_constraints import (
            CrossVentilationConfig,
        )
        config = CrossVentilationConfig(min_window_count=3)
        constraint = CrossVentilationConstraint(config=config)
        result = constraint.evaluate(building)
        
        assert result.issue_count == 1
    
    def test_issue_details(self) -> None:
        """Test issue details are correct."""
        room = create_room(window_ids=set())
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = CrossVentilationConstraint()
        result = constraint.evaluate(building)
        
        issue = result.issues[0]
        assert issue.code == "CROSS_VENTILATION_POSSIBLE"
        assert issue.entity_id == "room1"


# ============================================================================
# SolarOrientationConstraint tests
# ============================================================================


class TestSolarOrientationConstraint:
    """Tests for SolarOrientationConstraint."""
    
    def test_optimal_orientation(self) -> None:
        """Test room with optimal orientation."""
        room = create_room(
            room_type=RoomType.BEDROOM,
            metadata={"orientation": "east"},
        )
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = SolarOrientationConstraint()
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_suboptimal_orientation(self) -> None:
        """Test room with suboptimal orientation."""
        room = create_room(
            room_type=RoomType.BEDROOM,
            metadata={"orientation": "west"},
        )
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = SolarOrientationConstraint()
        result = constraint.evaluate(building)
        
        assert result.issue_count == 1
    
    def test_no_metadata(self) -> None:
        """Test room without orientation metadata - should skip."""
        room = create_room(room_type=RoomType.BEDROOM)
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = SolarOrientationConstraint()
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_custom_preferences(self) -> None:
        """Test custom orientation preferences."""
        room = create_room(
            room_type=RoomType.BEDROOM,
            metadata={"orientation": "south"},
        )
        building = create_building_with_rooms(rooms={"room1": room})
        
        config = SolarOrientationConfig(preferred_orientations={
            "bedroom": ["south", "west"],
        })
        constraint = SolarOrientationConstraint(config=config)
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_unknown_room_type(self) -> None:
        """Test room type without preferences."""
        room = create_room(
            room_type=RoomType.STORAGE,
            metadata={"orientation": "west"},
        )
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = SolarOrientationConstraint()
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_issue_details(self) -> None:
        """Test issue details are correct."""
        room = create_room(
            room_type=RoomType.KITCHEN,
            metadata={"orientation": "west"},
        )
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = SolarOrientationConstraint()
        result = constraint.evaluate(building)
        
        issue = result.issues[0]
        assert issue.code == "SOLAR_ORIENTATION_SUBOPTIMAL"
        assert issue.entity_id == "room1"


# ============================================================================
# WestFacingHeatGainConstraint tests
# ============================================================================


class TestWestFacingHeatGainConstraint:
    """Tests for WestFacingHeatGainConstraint."""
    
    def test_west_facing_small_glazing(self) -> None:
        """Test west-facing room with small glazing."""
        room = create_room(
            window_ids={"win1"},
            metadata={"orientation": "west"},
        )
        window = create_window(
            width=1, height=1,  # Area = 1
            metadata={"orientation": "west"},
        )
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        constraint = WestFacingHeatGainConstraint()
        result = constraint.evaluate(building)
        
        # Small window ratio - should pass
        assert result.is_optimal
    
    def test_west_facing_large_glazing(self) -> None:
        """Test west-facing room with large glazing."""
        room = create_room(
            window_ids={"win1"},
            metadata={"orientation": "west"},
        )
        # Window area = 50, room area = 100, ratio = 50% > 30%
        window = create_window(
            width=10, height=5,
            metadata={"orientation": "west"},
        )
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        constraint = WestFacingHeatGainConstraint()
        result = constraint.evaluate(building)
        
        assert result.issue_count == 1
    
    def test_non_west_facing(self) -> None:
        """Test non-west-facing room - should skip."""
        room = create_room(
            window_ids={"win1"},
            metadata={"orientation": "south"},
        )
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = WestFacingHeatGainConstraint()
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_no_metadata(self) -> None:
        """Test room without orientation metadata - should skip."""
        room = create_room(window_ids={"win1"})
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = WestFacingHeatGainConstraint()
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_custom_max_ratio(self) -> None:
        """Test custom maximum west-facing ratio."""
        room = create_room(
            window_ids={"win1"},
            metadata={"orientation": "west"},
        )
        # Window area = 20, room area = 100, ratio = 20%
        window = create_window(
            width=5, height=4,
            metadata={"orientation": "west"},
        )
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        config = WestFacingHeatGainConfig(max_west_window_ratio=0.15)
        constraint = WestFacingHeatGainConstraint(config=config)
        result = constraint.evaluate(building)
        
        assert result.issue_count == 1
    
    def test_issue_details(self) -> None:
        """Test issue details are correct."""
        room = create_room(
            window_ids={"win1"},
            metadata={"orientation": "west"},
        )
        window = create_window(
            width=10, height=5,
            metadata={"orientation": "west"},
        )
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        constraint = WestFacingHeatGainConstraint()
        result = constraint.evaluate(building)
        
        issue = result.issues[0]
        assert issue.code == "WEST_FACING_LARGE_GLAZING"
        assert issue.entity_id == "room1"


# ============================================================================
# NaturalLightConstraint tests
# ============================================================================


class TestNaturalLightConstraint:
    """Tests for NaturalLightConstraint."""
    
    def test_no_windows(self) -> None:
        """Test room with no windows."""
        room = create_room(window_ids=set())
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = NaturalLightConstraint()
        result = constraint.evaluate(building)
        
        assert result.issue_count == 1
    
    def test_small_window(self) -> None:
        """Test room with small window-to-wall ratio."""
        room = create_room(window_ids={"win1"})
        # Window area = 3, perimeter ~40, wall area = 120, ratio = 2.5% < 15%
        window = create_window(width=1, height=3)
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        constraint = NaturalLightConstraint()
        result = constraint.evaluate(building)
        
        assert result.issue_count == 1
    
    def test_large_window(self) -> None:
        """Test room with large window."""
        room = create_room(window_ids={"win1"})
        # Window area = 30, perimeter ~40, wall area = 120, ratio = 25% > 15%
        window = create_window(width=6, height=5)
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        constraint = NaturalLightConstraint()
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_custom_ratio(self) -> None:
        """Test custom minimum window-to-wall ratio."""
        room = create_room(window_ids={"win1"})
        # Window area = 3, perimeter ~40, wall area = 120, ratio = 2.5%
        window = create_window(width=1, height=3)
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        config = NaturalLightConfig(min_window_wall_ratio=0.02)
        constraint = NaturalLightConstraint(config=config)
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_issue_details(self) -> None:
        """Test issue details are correct."""
        room = create_room(window_ids=set())
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = NaturalLightConstraint()
        result = constraint.evaluate(building)
        
        issue = result.issues[0]
        assert issue.code == "NATURAL_LIGHT_INSUFFICIENT"
        assert issue.entity_id == "room1"


# ============================================================================
# OutdoorConnectionConstraint tests
# ============================================================================


class TestOutdoorConnectionConstraint:
    """Tests for OutdoorConnectionConstraint."""
    
    def test_outdoor_potential_no_connection(self) -> None:
        """Test room with outdoor potential but no connection."""
        room = create_room(metadata={"outdoor_potential": True})
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = OutdoorConnectionConstraint()
        result = constraint.evaluate(building)
        
        assert result.issue_count == 1
    
    def test_outdoor_potential_with_balcony(self) -> None:
        """Test room with outdoor potential and balcony."""
        room = create_room(metadata={
            "outdoor_potential": True,
            "has_balcony": True,
        })
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = OutdoorConnectionConstraint()
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_no_outdoor_potential(self) -> None:
        """Test room without outdoor potential metadata."""
        room = create_room()
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = OutdoorConnectionConstraint()
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_disabled_recommendation(self) -> None:
        """Test with recommendation disabled."""
        room = create_room(metadata={"outdoor_potential": True})
        building = create_building_with_rooms(rooms={"room1": room})
        
        config = OutdoorConnectionConfig(recommend_outdoor=False)
        constraint = OutdoorConnectionConstraint(config=config)
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_issue_details(self) -> None:
        """Test issue details are correct."""
        room = create_room(metadata={
            "outdoor_potential": True,
            "outdoor_type": "balcony",
        })
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = OutdoorConnectionConstraint()
        result = constraint.evaluate(building)
        
        issue = result.issues[0]
        assert issue.code == "OUTDOOR_CONNECTION_MISSING"
        assert issue.entity_id == "room1"


# ============================================================================
# Integration tests
# ============================================================================


class TestIntegration:
    """Integration tests for environmental constraints."""
    
    def test_with_constraint_engine(self) -> None:
        """Test constraints work with ConstraintEngine."""
        engine = ConstraintEngine()
        engine.register(MinimumWindowToFloorAreaConstraint())
        engine.register(CrossVentilationConstraint())
        
        room = create_room(window_ids={"win1"})
        window = create_window(width=2, height=1)  # Area = 2
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        result = engine.evaluate(building)
        
        assert result.issue_count >= 1
    
    def test_with_score_engine(self) -> None:
        """Test constraints work with ConstraintScoreEngine."""
        engine = ConstraintEngine()
        engine.register(MinimumWindowToFloorAreaConstraint())
        
        room = create_room(window_ids={"win1"})
        window = create_window(width=2, height=1)  # Area = 2
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        constraint_result = engine.evaluate(building)
        score_engine = ConstraintScoreEngine()
        score = score_engine.evaluate(constraint_result)
        
        assert score.overall_score < 100
    
    def test_with_weight_profile(self) -> None:
        """Test constraints work with custom weight profile."""
        engine = ConstraintEngine()
        engine.register(MinimumWindowToFloorAreaConstraint())
        
        room = create_room(window_ids={"win1"})
        window = create_window(width=2, height=1)  # Area = 2
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        constraint_result = engine.evaluate(building)
        score_engine = ConstraintScoreEngine()
        weight_profile = ConstraintWeightProfile.prioritize_category(
            ConstraintCategory.ENVIRONMENTAL,
            weight=2.0,
        )
        score = score_engine.evaluate(constraint_result, weight_profile=weight_profile)
        
        assert score.overall_score < 100
    
    def test_empty_building(self) -> None:
        """Test all constraints with empty building."""
        engine = ConstraintEngine()
        engine.register(MinimumWindowToFloorAreaConstraint())
        engine.register(CrossVentilationConstraint())
        engine.register(SolarOrientationConstraint())
        engine.register(WestFacingHeatGainConstraint())
        engine.register(NaturalLightConstraint())
        engine.register(OutdoorConnectionConstraint())
        
        building = BuildingModel()
        result = engine.evaluate(building)
        
        assert result.is_optimal
    
    def test_all_constraints_registered(self) -> None:
        """Test all environmental constraints can be registered."""
        engine = ConstraintEngine()
        engine.register(MinimumWindowToFloorAreaConstraint())
        engine.register(CrossVentilationConstraint())
        engine.register(SolarOrientationConstraint())
        engine.register(WestFacingHeatGainConstraint())
        engine.register(NaturalLightConstraint())
        engine.register(OutdoorConnectionConstraint())
        
        assert engine.constraint_count == 6


# ============================================================================
# Edge case tests
# ============================================================================


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_zero_area_room(self) -> None:
        """Test room with zero area."""
        room = Room(room_type=RoomType.LIVING, polygon=Polygon())
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = MinimumWindowToFloorAreaConstraint()
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_missing_window_reference(self) -> None:
        """Test room referencing non-existent window."""
        room = create_room(window_ids={"nonexistent"})
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = MinimumWindowToFloorAreaConstraint()
        result = constraint.evaluate(building)
        
        # Should handle gracefully
        assert result.is_optimal
    
    def test_case_insensitive_orientation(self) -> None:
        """Test orientation comparison is case-insensitive."""
        room = create_room(
            room_type=RoomType.BEDROOM,
            metadata={"orientation": "EAST"},
        )
        building = create_building_with_rooms(rooms={"room1": room})
        
        constraint = SolarOrientationConstraint()
        result = constraint.evaluate(building)
        
        assert result.is_optimal
    
    def test_multiple_issues_same_room(self) -> None:
        """Test multiple constraints finding issues in same room."""
        engine = ConstraintEngine()
        engine.register(CrossVentilationConstraint())
        engine.register(NaturalLightConstraint())
        
        # Room with no windows - fails both constraints
        room = create_room(window_ids=set())
        building = create_building_with_rooms(rooms={"room1": room})
        
        result = engine.evaluate(building)
        
        assert result.issue_count == 2
    
    def test_deterministic_results(self) -> None:
        """Test that results are deterministic."""
        constraint = MinimumWindowToFloorAreaConstraint()
        
        room = create_room(window_ids={"win1"})
        window = create_window(width=2, height=1)  # Area = 2
        building = create_building_with_rooms(
            rooms={"room1": room},
            windows={"win1": window},
        )
        
        result1 = constraint.evaluate(building)
        result2 = constraint.evaluate(building)
        
        assert result1.issue_count == result2.issue_count
        assert result1.is_optimal == result2.is_optimal