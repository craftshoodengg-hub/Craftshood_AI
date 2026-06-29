"""Residential Rule Pack for Building Model v2.

Provides sensible default configuration values for residential buildings.
"""

from __future__ import annotations

from .rule_pack import (
    RulePack,
    RulePackAccessibility,
    RulePackBuildingCode,
    RulePackEnvironmental,
    RulePackStructural,
    RulePackVastu,
)
from ..constraints.accessibility_constraints import (
    AccessibleBathroomConfig,
    MinimumHallwayWidthConfig,
    RampSlopeConfig,
    StairHandrailConfig,
    WheelchairTurningRadiusConfig,
)
from ..constraints.building_code_constraints import (
    MaximumTravelDistanceConfig,
    MinimumCeilingHeightConfig,
    MinimumDoorWidthConfig,
    MinimumRoomAreaConfig,
    MinimumStairWidthConfig,
    MinimumWindowAreaConfig,
)
from ..constraints.environmental_constraints import (
    CrossVentilationConfig,
    NaturalLightConfig,
    OutdoorConnectionConfig,
    SolarOrientationConfig,
    MinimumWindowToFloorAreaConfig,
)
from ..constraints.scoring import ConstraintWeightProfile
from ..constraints.structural_constraints import (
    WallContinuityConfig,
    ColumnSpacingConfig,
    MaximumWallSpanConfig,
    StairSupportConfig,
    StructuralSymmetryConfig,
)


def create_residential_rule_pack() -> RulePack:
    """Create a residential rule pack with sensible defaults.
    
    Returns:
        A RulePack configured for residential buildings.
    """
    return RulePack(
        name="Residential",
        description="Default rule pack for residential buildings",
        building_code=RulePackBuildingCode(
            room_area=MinimumRoomAreaConfig(minimum_area=70.0),
            door_width=MinimumDoorWidthConfig(minimum_width=2.5),
            window_area=MinimumWindowAreaConfig(minimum_area=3.0),
            stair_width=MinimumStairWidthConfig(minimum_width=3.0),
            ceiling_height=MinimumCeilingHeightConfig(minimum_height=7.0),
            max_travel_distance=MaximumTravelDistanceConfig(maximum_distance=75.0),
        ),
        accessibility=RulePackAccessibility(
            hallway_width=MinimumHallwayWidthConfig(minimum_width=3.5),
            ramp_slope=RampSlopeConfig(maximum_slope_ratio=0.083),
            stair_handrail=StairHandrailConfig(require_handrail_metadata=True),
            turning_radius=WheelchairTurningRadiusConfig(minimum_radius=5.0),
            accessible_bathroom=AccessibleBathroomConfig(require_accessible_metadata=True),
        ),
        environmental=RulePackEnvironmental(
            window_to_floor_area=MinimumWindowToFloorAreaConfig(minimum_ratio=0.10),
            natural_light=NaturalLightConfig(min_daylight_factor=2.0),
            cross_ventilation=CrossVentilationConfig(min_window_count=2),
            outdoor_connection=OutdoorConnectionConfig(),
            solar_orientation=SolarOrientationConfig(),
        ),
        structural=RulePackStructural(
            max_wall_span=MaximumWallSpanConfig(max_span_ft=20.0),
            column_spacing=ColumnSpacingConfig(max_spacing_ft=18.0),
            wall_continuity=WallContinuityConfig(require_continuity=True),
            stair_support=StairSupportConfig(require_floor_connection=True),
            structural_symmetry=StructuralSymmetryConfig(tolerance=0.20),
        ),
        vastu=RulePackVastu(enabled=False),
        scoring=ConstraintWeightProfile(
            functional_weight=1.0,
            building_code_weight=1.5,
            accessibility_weight=1.0,
            environmental_weight=0.8,
            structural_weight=1.2,
            vastu_weight=0.0,
            custom_weight=1.0,
        ),
    )