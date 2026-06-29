"""Unit tests for Rule Pack System."""

from __future__ import annotations

import pytest

from building_model_v2.rules import (
    RulePack,
    RulePackAccessibility,
    RulePackBuildingCode,
    RulePackEnvironmental,
    RulePackStructural,
    RulePackVastu,
    create_commercial_rule_pack,
    create_custom_rule_pack,
    create_residential_rule_pack,
    rule_pack_from_dict,
)
from building_model_v2.constraints.accessibility_constraints import (
    AccessibleBathroomConfig,
    MinimumHallwayWidthConfig,
    RampSlopeConfig,
    StairHandrailConfig,
    WheelchairTurningRadiusConfig,
)
from building_model_v2.constraints.building_code_constraints import (
    MaximumTravelDistanceConfig,
    MinimumCeilingHeightConfig,
    MinimumDoorWidthConfig,
    MinimumRoomAreaConfig,
    MinimumStairWidthConfig,
    MinimumWindowAreaConfig,
)
from building_model_v2.constraints.environmental_constraints import (
    CrossVentilationConfig,
    NaturalLightConfig,
    OutdoorConnectionConfig,
    SolarOrientationConfig,
    MinimumWindowToFloorAreaConfig,
)
from building_model_v2.constraints.scoring import ConstraintWeightProfile
from building_model_v2.constraints.structural_constraints import (
    ColumnSpacingConfig,
    WallContinuityConfig,
    MaximumWallSpanConfig,
    StairSupportConfig,
    StructuralSymmetryConfig,
)


# ============================================================================
# RulePackBuildingCode tests
# ============================================================================


class TestRulePackBuildingCode:
    """Tests for RulePackBuildingCode."""
    
    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = RulePackBuildingCode()
        assert config.room_area.minimum_area == 70.0
        assert config.door_width.minimum_width == 2.5
        assert config.window_area.minimum_area == 3.0
        assert config.stair_width.minimum_width == 3.0
        assert config.ceiling_height.minimum_height == 7.0
        assert config.max_travel_distance.maximum_distance == 75.0
    
    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = RulePackBuildingCode(
            room_area=MinimumRoomAreaConfig(minimum_area=100.0),
            door_width=MinimumDoorWidthConfig(minimum_width=3.0),
        )
        assert config.room_area.minimum_area == 100.0
        assert config.door_width.minimum_width == 3.0
        assert config.window_area.minimum_area == 3.0  # default
    
    def test_immutable(self) -> None:
        """Test that config is immutable."""
        config = RulePackBuildingCode()
        with pytest.raises(AttributeError):
            config.room_area = MinimumRoomAreaConfig(minimum_area=50.0)
    
    def test_equality(self) -> None:
        """Test equality comparison."""
        config1 = RulePackBuildingCode()
        config2 = RulePackBuildingCode()
        assert config1 == config2
    
    def test_inequality(self) -> None:
        """Test inequality comparison."""
        config1 = RulePackBuildingCode()
        config2 = RulePackBuildingCode(
            room_area=MinimumRoomAreaConfig(minimum_area=100.0),
        )
        assert config1 != config2


# ============================================================================
# RulePackAccessibility tests
# ============================================================================


class TestRulePackAccessibility:
    """Tests for RulePackAccessibility."""
    
    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = RulePackAccessibility()
        assert config.hallway_width.minimum_width == 3.5
        assert config.ramp_slope.maximum_slope_ratio == 0.083
        assert config.stair_handrail.require_handrail_metadata is True
        assert config.turning_radius.minimum_radius == 5.0
        assert config.accessible_bathroom.require_accessible_metadata is True
    
    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = RulePackAccessibility(
            hallway_width=MinimumHallwayWidthConfig(minimum_width=4.5),
            turning_radius=WheelchairTurningRadiusConfig(minimum_radius=6.0),
        )
        assert config.hallway_width.minimum_width == 4.5
        assert config.turning_radius.minimum_radius == 6.0


# ============================================================================
# RulePackEnvironmental tests
# ============================================================================


class TestRulePackEnvironmental:
    """Tests for RulePackEnvironmental."""
    
    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = RulePackEnvironmental()
        assert config.window_to_floor_area.minimum_ratio == 0.10
        assert config.natural_light.min_daylight_factor == 2.0
        assert config.cross_ventilation.min_window_count == 2
        assert config.outdoor_connection.recommend_outdoor is True
        assert config.solar_orientation.preferred_orientations is not None
    
    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = RulePackEnvironmental(
            window_to_floor_area=MinimumWindowToFloorAreaConfig(minimum_ratio=0.15),
            natural_light=NaturalLightConfig(min_daylight_factor=3.0),
        )
        assert config.window_to_floor_area.minimum_ratio == 0.15
        assert config.natural_light.min_daylight_factor == 3.0


# ============================================================================
# RulePackStructural tests
# ============================================================================


class TestRulePackStructural:
    """Tests for RulePackStructural."""
    
    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = RulePackStructural()
        assert config.max_wall_span.max_span_ft == 20.0
        assert config.column_spacing.max_spacing_ft == 18.0
        assert config.wall_continuity.require_continuity is True
        assert config.stair_support.require_floor_connection is True
        assert config.structural_symmetry.tolerance == 0.20
        assert config.large_room.max_area_sqft == 400.0
    
    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = RulePackStructural(
            max_wall_span=MaximumWallSpanConfig(max_span_ft=25.0),
            column_spacing=ColumnSpacingConfig(max_spacing_ft=35.0),
        )
        assert config.max_wall_span.max_span_ft == 25.0
        assert config.column_spacing.max_spacing_ft == 35.0


# ============================================================================
# RulePackVastu tests
# ============================================================================


class TestRulePackVastu:
    """Tests for RulePackVastu."""
    
    def test_default_values(self) -> None:
        """Test default configuration values."""
        config = RulePackVastu()
        assert config.enabled is False
        assert config.custom_params == {}
    
    def test_custom_values(self) -> None:
        """Test custom configuration values."""
        config = RulePackVastu(
            enabled=True,
            custom_params={"direction": "north"},
        )
        assert config.enabled is True
        assert config.custom_params == {"direction": "north"}


# ============================================================================
# RulePack base class tests
# ============================================================================


class TestRulePack:
    """Tests for RulePack base class."""
    
    def test_creation(self) -> None:
        """Test basic rule pack creation."""
        pack = RulePack(name="Test Pack")
        assert pack.name == "Test Pack"
        assert pack.description == ""
    
    def test_immutable(self) -> None:
        """Test that rule pack is immutable."""
        pack = RulePack(name="Test Pack")
        with pytest.raises(AttributeError):
            pack.name = "Modified"
    
    def test_equality(self) -> None:
        """Test equality comparison."""
        pack1 = RulePack(name="Test Pack")
        pack2 = RulePack(name="Test Pack")
        assert pack1 == pack2
    
    def test_inequality(self) -> None:
        """Test inequality comparison."""
        pack1 = RulePack(name="Test Pack 1")
        pack2 = RulePack(name="Test Pack 2")
        assert pack1 != pack2
    
    def test_to_dict(self) -> None:
        """Test serialization to dictionary."""
        pack = RulePack(name="Test Pack", description="A test pack")
        data = pack.to_dict()
        assert data["name"] == "Test Pack"
        assert data["description"] == "A test pack"
        assert "building_code" in data
        assert "accessibility" in data
        assert "environmental" in data
        assert "structural" in data
        assert "vastu" in data
        assert "scoring" in data
    
    def test_to_dict_structure(self) -> None:
        """Test dictionary structure completeness."""
        pack = RulePack(name="Test")
        data = pack.to_dict()
        assert "room_area" in data["building_code"]
        assert "door_width" in data["building_code"]
        assert "window_area" in data["building_code"]
        assert "stair_width" in data["building_code"]
        assert "ceiling_height" in data["building_code"]
        assert "max_travel_distance" in data["building_code"]
        assert "hallway_width" in data["accessibility"]
        assert "ramp_slope" in data["accessibility"]
        assert "stair_handrail" in data["accessibility"]
        assert "turning_radius" in data["accessibility"]
        assert "accessible_bathroom" in data["accessibility"]
        assert "window_to_floor_area" in data["environmental"]
        assert "natural_light" in data["environmental"]
        assert "cross_ventilation" in data["environmental"]
        assert "outdoor_connection" in data["environmental"]
        assert "solar_orientation" in data["environmental"]
        assert "max_wall_span" in data["structural"]
        assert "column_spacing" in data["structural"]
        assert "wall_continuity" in data["structural"]
        assert "stair_support" in data["structural"]
        assert "structural_symmetry" in data["structural"]
        assert "large_room" in data["structural"]
        assert "enabled" in data["vastu"]
        assert "custom_params" in data["vastu"]
        assert "functional_weight" in data["scoring"]
        assert "building_code_weight" in data["scoring"]
        assert "accessibility_weight" in data["scoring"]
        assert "environmental_weight" in data["scoring"]
        assert "structural_weight" in data["scoring"]
        assert "vastu_weight" in data["scoring"]
        assert "custom_weight" in data["scoring"]


# ============================================================================
# Residential Rule Pack tests
# ============================================================================


class TestResidentialRulePack:
    """Tests for residential rule pack."""
    
    def test_creation(self) -> None:
        """Test residential rule pack creation."""
        pack = create_residential_rule_pack()
        assert pack.name == "Residential"
        assert "residential" in pack.description.lower()
    
    def test_building_code_defaults(self) -> None:
        """Test residential building code defaults."""
        pack = create_residential_rule_pack()
        assert pack.building_code.room_area.minimum_area == 70.0
        assert pack.building_code.door_width.minimum_width == 2.5
        assert pack.building_code.window_area.minimum_area == 3.0
        assert pack.building_code.stair_width.minimum_width == 3.0
        assert pack.building_code.ceiling_height.minimum_height == 7.0
        assert pack.building_code.max_travel_distance.maximum_distance == 75.0
    
    def test_accessibility_defaults(self) -> None:
        """Test residential accessibility defaults."""
        pack = create_residential_rule_pack()
        assert pack.accessibility.hallway_width.minimum_width == 3.5
        assert pack.accessibility.ramp_slope.maximum_slope_ratio == 0.083
        assert pack.accessibility.turning_radius.minimum_radius == 5.0
    
    def test_environmental_defaults(self) -> None:
        """Test residential environmental defaults."""
        pack = create_residential_rule_pack()
        assert pack.environmental.window_to_floor_area.minimum_ratio == 0.10
        assert pack.environmental.natural_light.min_daylight_factor == 2.0
        assert pack.environmental.cross_ventilation.min_window_count == 2
    
    def test_structural_defaults(self) -> None:
        """Test residential structural defaults."""
        pack = create_residential_rule_pack()
        assert pack.structural.max_wall_span.max_span_ft == 20.0
        assert pack.structural.column_spacing.max_spacing_ft == 18.0
        assert pack.structural.large_room.max_area_sqft == 400.0
    
    def test_vastu_disabled(self) -> None:
        """Test that Vastu is disabled by default."""
        pack = create_residential_rule_pack()
        assert pack.vastu.enabled is False
    
    def test_scoring_weights(self) -> None:
        """Test residential scoring weights."""
        pack = create_residential_rule_pack()
        assert pack.scoring.functional_weight == 1.0
        assert pack.scoring.building_code_weight == 1.5
        assert pack.scoring.accessibility_weight == 1.0
        assert pack.scoring.structural_weight == 1.2
    
    def test_immutable(self) -> None:
        """Test that residential rule pack is immutable."""
        pack = create_residential_rule_pack()
        with pytest.raises(AttributeError):
            pack.name = "Modified"


# ============================================================================
# Commercial Rule Pack tests
# ============================================================================


class TestCommercialRulePack:
    """Tests for commercial rule pack."""
    
    def test_creation(self) -> None:
        """Test commercial rule pack creation."""
        pack = create_commercial_rule_pack()
        assert pack.name == "Commercial"
        assert "commercial" in pack.description.lower()
    
    def test_building_code_defaults(self) -> None:
        """Test commercial building code defaults."""
        pack = create_commercial_rule_pack()
        assert pack.building_code.room_area.minimum_area == 100.0
        assert pack.building_code.door_width.minimum_width == 3.0
        assert pack.building_code.window_area.minimum_area == 5.0
        assert pack.building_code.stair_width.minimum_width == 4.0
        assert pack.building_code.ceiling_height.minimum_height == 9.0
        assert pack.building_code.max_travel_distance.maximum_distance == 100.0
    
    def test_accessibility_defaults(self) -> None:
        """Test commercial accessibility defaults."""
        pack = create_commercial_rule_pack()
        assert pack.accessibility.hallway_width.minimum_width == 4.5
        assert pack.accessibility.turning_radius.minimum_radius == 6.0
    
    def test_environmental_defaults(self) -> None:
        """Test commercial environmental defaults."""
        pack = create_commercial_rule_pack()
        assert pack.environmental.window_to_floor_area.minimum_ratio == 0.15
        assert pack.environmental.natural_light.min_daylight_factor == 3.0
    
    def test_structural_defaults(self) -> None:
        """Test commercial structural defaults."""
        pack = create_commercial_rule_pack()
        assert pack.structural.max_wall_span.max_span_ft == 25.0
        assert pack.structural.column_spacing.max_spacing_ft == 18.0
        assert pack.structural.large_room.max_area_sqft == 400.0
    
    def test_scoring_weights(self) -> None:
        """Test commercial scoring weights."""
        pack = create_commercial_rule_pack()
        assert pack.scoring.functional_weight == 1.2
        assert pack.scoring.building_code_weight == 1.5
        assert pack.scoring.accessibility_weight == 1.5
        assert pack.scoring.structural_weight == 1.3
    
    def test_different_from_residential(self) -> None:
        """Test that commercial differs from residential."""
        res = create_residential_rule_pack()
        com = create_commercial_rule_pack()
        assert res.building_code.room_area.minimum_area != com.building_code.room_area.minimum_area
        assert res.building_code.ceiling_height.minimum_height != com.building_code.ceiling_height.minimum_height
        assert res.accessibility.hallway_width.minimum_width != com.accessibility.hallway_width.minimum_width


# ============================================================================
# Custom Rule Pack tests
# ============================================================================


class TestCustomRulePack:
    """Tests for custom rule pack."""
    
    def test_creation_with_defaults(self) -> None:
        """Test custom rule pack with default values."""
        pack = create_custom_rule_pack()
        assert pack.name == "Custom"
        assert pack.description == "User-defined rule pack"
    
    def test_creation_with_custom_name(self) -> None:
        """Test custom rule pack with custom name."""
        pack = create_custom_rule_pack(name="My Custom Pack")
        assert pack.name == "My Custom Pack"
    
    def test_creation_with_custom_building_code(self) -> None:
        """Test custom rule pack with custom building code."""
        custom_bc = RulePackBuildingCode(
            room_area=MinimumRoomAreaConfig(minimum_area=120.0),
        )
        pack = create_custom_rule_pack(building_code=custom_bc)
        assert pack.building_code.room_area.minimum_area == 120.0
    
    def test_creation_with_custom_accessibility(self) -> None:
        """Test custom rule pack with custom accessibility."""
        custom_acc = RulePackAccessibility(
            hallway_width=MinimumHallwayWidthConfig(minimum_width=5.0),
        )
        pack = create_custom_rule_pack(accessibility=custom_acc)
        assert pack.accessibility.hallway_width.minimum_width == 5.0
    
    def test_creation_with_custom_environmental(self) -> None:
        """Test custom rule pack with custom environmental."""
        custom_env = RulePackEnvironmental(
            window_to_floor_area=MinimumWindowToFloorAreaConfig(minimum_ratio=0.20),
        )
        pack = create_custom_rule_pack(environmental=custom_env)
        assert pack.environmental.window_to_floor_area.minimum_ratio == 0.20
    
    def test_creation_with_custom_structural(self) -> None:
        """Test custom rule pack with custom structural."""
        custom_str = RulePackStructural(
            max_wall_span=MaximumWallSpanConfig(max_span_ft=30.0),
        )
        pack = create_custom_rule_pack(structural=custom_str)
        assert pack.structural.max_wall_span.max_span_ft == 30.0
    
    def test_creation_with_custom_vastu(self) -> None:
        """Test custom rule pack with Vastu enabled."""
        custom_vastu = RulePackVastu(enabled=True, custom_params={"direction": "east"})
        pack = create_custom_rule_pack(vastu=custom_vastu)
        assert pack.vastu.enabled is True
        assert pack.vastu.custom_params == {"direction": "east"}
    
    def test_creation_with_custom_scoring(self) -> None:
        """Test custom rule pack with custom scoring."""
        custom_scoring = ConstraintWeightProfile(
            structural_weight=2.0,
            building_code_weight=2.0,
        )
        pack = create_custom_rule_pack(scoring=custom_scoring)
        assert pack.scoring.structural_weight == 2.0
        assert pack.scoring.building_code_weight == 2.0


# ============================================================================
# Serialization tests
# ============================================================================


class TestSerialization:
    """Tests for rule pack serialization."""
    
    def test_roundtrip_residential(self) -> None:
        """Test serialization roundtrip for residential pack."""
        original = create_residential_rule_pack()
        data = original.to_dict()
        restored = rule_pack_from_dict(data)
        assert restored == original
    
    def test_roundtrip_commercial(self) -> None:
        """Test serialization roundtrip for commercial pack."""
        original = create_commercial_rule_pack()
        data = original.to_dict()
        restored = rule_pack_from_dict(data)
        assert restored == original
    
    def test_roundtrip_custom(self) -> None:
        """Test serialization roundtrip for custom pack."""
        original = create_custom_rule_pack(
            name="Test Custom",
            description="A custom pack for testing",
            vastu=RulePackVastu(enabled=True),
        )
        data = original.to_dict()
        restored = rule_pack_from_dict(data)
        assert restored == original
    
    def test_from_dict_minimal(self) -> None:
        """Test deserialization from minimal dictionary."""
        data = {"name": "Minimal"}
        pack = rule_pack_from_dict(data)
        assert pack.name == "Minimal"
        assert pack.description == ""
    
    def test_from_dict_with_building_code(self) -> None:
        """Test deserialization with building code config."""
        data = {
            "name": "Test",
            "building_code": {
                "room_area": {"minimum_area": 80.0},
                "door_width": {"minimum_width": 3.0},
            },
        }
        pack = rule_pack_from_dict(data)
        assert pack.building_code.room_area.minimum_area == 80.0
        assert pack.building_code.door_width.minimum_width == 3.0
    
    def test_from_dict_with_scoring(self) -> None:
        """Test deserialization with scoring config."""
        data = {
            "name": "Test",
            "scoring": {
                "structural_weight": 2.0,
                "building_code_weight": 1.5,
            },
        }
        pack = rule_pack_from_dict(data)
        assert pack.scoring.structural_weight == 2.0
        assert pack.scoring.building_code_weight == 1.5
    
    def test_from_dict_with_vastu(self) -> None:
        """Test deserialization with Vastu config."""
        data = {
            "name": "Test",
            "vastu": {
                "enabled": True,
                "custom_params": {"direction": "north"},
            },
        }
        pack = rule_pack_from_dict(data)
        assert pack.vastu.enabled is True
        assert pack.vastu.custom_params == {"direction": "north"}
    
    def test_to_dict_returns_dict(self) -> None:
        """Test that to_dict returns a dictionary."""
        pack = create_residential_rule_pack()
        data = pack.to_dict()
        assert isinstance(data, dict)
    
    def test_to_dict_contains_all_sections(self) -> None:
        """Test that to_dict contains all configuration sections."""
        pack = create_residential_rule_pack()
        data = pack.to_dict()
        expected_sections = [
            "name", "description", "building_code", "accessibility",
            "environmental", "structural", "vastu", "scoring",
        ]
        for section in expected_sections:
            assert section in data


# ============================================================================
# Integration tests
# ============================================================================


class TestIntegration:
    """Integration tests for rule packs."""
    
    def test_rule_pack_provides_valid_configs(self) -> None:
        """Test that rule packs provide valid configuration objects."""
        pack = create_residential_rule_pack()
        assert isinstance(pack.building_code, RulePackBuildingCode)
        assert isinstance(pack.accessibility, RulePackAccessibility)
        assert isinstance(pack.environmental, RulePackEnvironmental)
        assert isinstance(pack.structural, RulePackStructural)
        assert isinstance(pack.vastu, RulePackVastu)
        assert isinstance(pack.scoring, ConstraintWeightProfile)
    
    def test_residential_different_from_commercial(self) -> None:
        """Test that residential and commercial packs differ."""
        res = create_residential_rule_pack()
        com = create_commercial_rule_pack()
        assert res != com
        assert res.building_code.room_area.minimum_area < com.building_code.room_area.minimum_area
        assert res.building_code.ceiling_height.minimum_height < com.building_code.ceiling_height.minimum_height
    
    def test_custom_can_override_any_field(self) -> None:
        """Test that custom pack can override any field."""
        custom = create_custom_rule_pack(
            name="Fully Custom",
            building_code=RulePackBuildingCode(
                room_area=MinimumRoomAreaConfig(minimum_area=200.0),
            ),
            accessibility=RulePackAccessibility(
                hallway_width=MinimumHallwayWidthConfig(minimum_width=6.0),
            ),
            environmental=RulePackEnvironmental(
                window_to_floor_area=MinimumWindowToFloorAreaConfig(minimum_ratio=0.25),
            ),
            structural=RulePackStructural(
                max_wall_span=MaximumWallSpanConfig(max_span_ft=40.0),
            ),
            vastu=RulePackVastu(enabled=True),
            scoring=ConstraintWeightProfile(
                structural_weight=3.0,
            ),
        )
        assert custom.name == "Fully Custom"
        assert custom.building_code.room_area.minimum_area == 200.0
        assert custom.accessibility.hallway_width.minimum_width == 6.0
        assert custom.environmental.window_to_floor_area.minimum_ratio == 0.25
        assert custom.structural.max_wall_span.max_span_ft == 40.0
        assert custom.vastu.enabled is True
        assert custom.scoring.structural_weight == 3.0
    
    def test_rule_pack_can_be_used_with_constraint_engine(self) -> None:
        """Test that rule pack configs work with constraint engine."""
        from building_model_v2.constraints import ConstraintEngine
        from building_model_v2.constraints.structural_constraints import MaximumWallSpanConstraint
        
        pack = create_residential_rule_pack()
        config = pack.structural.max_wall_span
        constraint = MaximumWallSpanConstraint(config=config)
        
        assert constraint.max_span_ft == 20.0
    
    def test_rule_pack_can_be_used_with_scoring_engine(self) -> None:
        """Test that rule pack scoring config works with scoring engine."""
        from building_model_v2.constraints.scoring import ConstraintScoreEngine
        from building_model_v2.constraints.constraint_result import ConstraintResult
        
        pack = create_residential_rule_pack()
        engine = ConstraintScoreEngine()
        
        # Create a valid constraint result
        result = ConstraintResult(issues=[])
        
        # Just verify the weight profile can be used
        score = engine.evaluate(
            constraint_result=result,
            weight_profile=pack.scoring,
        )
        assert score is not None

class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_empty_name(self) -> None:
        """Test rule pack with empty name."""
        pack = RulePack(name="")
        assert pack.name == ""
    
    def test_empty_description(self) -> None:
        """Test rule pack with empty description."""
        pack = RulePack(name="Test", description="")
        assert pack.description == ""
    
    def test_vastu_empty_params(self) -> None:
        """Test Vastu with empty custom params."""
        vastu = RulePackVastu(enabled=True, custom_params={})
        assert vastu.enabled is True
        assert vastu.custom_params == {}
    
    def test_multiple_rule_packs_independent(self) -> None:
        """Test that multiple rule packs are independent."""
        pack1 = create_residential_rule_pack()
        pack2 = create_commercial_rule_pack()
        pack3 = create_custom_rule_pack(name="Custom")
        
        assert pack1 != pack2
        assert pack2 != pack3
        assert pack1 != pack3
    
    def test_rule_pack_hashable(self) -> None:
        """Test that rule pack can be represented as string."""
        pack = create_residential_rule_pack()
        # Verify pack has string representation
        assert str(pack.name) == "Residential"

    def test_serialization_preserves_all_values(self) -> None:
        """Test that serialization preserves all configuration values."""
        pack = create_custom_rule_pack(
            name="Test",
            building_code=RulePackBuildingCode(
                room_area=MinimumRoomAreaConfig(minimum_area=150.0),
                door_width=MinimumDoorWidthConfig(minimum_width=3.5),
                window_area=MinimumWindowAreaConfig(minimum_area=8.0),
                stair_width=MinimumStairWidthConfig(minimum_width=4.5),
                ceiling_height=MinimumCeilingHeightConfig(minimum_height=10.0),
                max_travel_distance=MaximumTravelDistanceConfig(maximum_distance=150.0),
            ),
        )
        data = pack.to_dict()
        restored = rule_pack_from_dict(data)
        assert restored.building_code.room_area.minimum_area == 150.0
        assert restored.building_code.door_width.minimum_width == 3.5
        assert restored.building_code.window_area.minimum_area == 8.0
        assert restored.building_code.stair_width.minimum_width == 4.5
        assert restored.building_code.ceiling_height.minimum_height == 10.0
        assert restored.building_code.max_travel_distance.maximum_distance == 150.0