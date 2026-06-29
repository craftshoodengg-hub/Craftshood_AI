"""Custom Rule Pack for Building Model v2.

Provides a customizable rule pack that allows user-supplied configuration.
Supports serialization and deserialization.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .rule_pack import (
    RulePack,
    RulePackAccessibility,
    RulePackBuildingCode,
    RulePackEnvironmental,
    RulePackStructural,
    RulePackVastu,
    _config_to_dict,
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
    ColumnSpacingConfig,
    LargeUnsupportedRoomConfig,
    MaximumWallSpanConfig,
    StairSupportConfig,
    StructuralSymmetryConfig,
    WallContinuityConfig,
)


def create_custom_rule_pack(
    name: str = "Custom",
    description: str = "User-defined rule pack",
    building_code: RulePackBuildingCode | None = None,
    accessibility: RulePackAccessibility | None = None,
    environmental: RulePackEnvironmental | None = None,
    structural: RulePackStructural | None = None,
    vastu: RulePackVastu | None = None,
    scoring: ConstraintWeightProfile | None = None,
) -> RulePack:
    """Create a custom rule pack with user-supplied configuration.
    
    Any configuration section not provided will use default values.
    
    Args:
        name: Human-readable name of the rule pack.
        description: Description of the rule pack.
        building_code: Building code configuration. Uses defaults if None.
        accessibility: Accessibility configuration. Uses defaults if None.
        environmental: Environmental configuration. Uses defaults if None.
        structural: Structural configuration. Uses defaults if None.
        vastu: Vastu configuration. Uses defaults if None.
        scoring: Scoring weight profile. Uses defaults if None.
    
    Returns:
        A RulePack with the specified configuration.
    """
    return RulePack(
        name=name,
        description=description,
        building_code=building_code or RulePackBuildingCode(),
        accessibility=accessibility or RulePackAccessibility(),
        environmental=environmental or RulePackEnvironmental(),
        structural=structural or RulePackStructural(),
        vastu=vastu or RulePackVastu(),
        scoring=scoring or ConstraintWeightProfile(),
    )


def rule_pack_from_dict(data: dict[str, Any]) -> RulePack:
    """Deserialize a rule pack from a dictionary.
    
    Args:
        data: Dictionary containing rule pack configuration.
        
    Returns:
        A RulePack instance created from the dictionary.
        
    Raises:
        KeyError: If required fields are missing.
        ValueError: If field values are invalid.
    """
    building_code_data = data.get("building_code", {})
    accessibility_data = data.get("accessibility", {})
    environmental_data = data.get("environmental", {})
    structural_data = data.get("structural", {})
    vastu_data = data.get("vastu", {})
    scoring_data = data.get("scoring", {})
    
    return RulePack(
        name=data["name"],
        description=data.get("description", ""),
        building_code=RulePackBuildingCode(
            room_area=_parse_config(
                building_code_data.get("room_area"),
                MinimumRoomAreaConfig,
            ),
            door_width=_parse_config(
                building_code_data.get("door_width"),
                MinimumDoorWidthConfig,
            ),
            window_area=_parse_config(
                building_code_data.get("window_area"),
                MinimumWindowAreaConfig,
            ),
            stair_width=_parse_config(
                building_code_data.get("stair_width"),
                MinimumStairWidthConfig,
            ),
            ceiling_height=_parse_config(
                building_code_data.get("ceiling_height"),
                MinimumCeilingHeightConfig,
            ),
            max_travel_distance=_parse_config(
                building_code_data.get("max_travel_distance"),
                MaximumTravelDistanceConfig,
            ),
        ),
        accessibility=RulePackAccessibility(
            hallway_width=_parse_config(
                accessibility_data.get("hallway_width"),
                MinimumHallwayWidthConfig,
            ),
            ramp_slope=_parse_config(
                accessibility_data.get("ramp_slope"),
                RampSlopeConfig,
            ),
            stair_handrail=_parse_config(
                accessibility_data.get("stair_handrail"),
                StairHandrailConfig,
            ),
            turning_radius=_parse_config(
                accessibility_data.get("turning_radius"),
                WheelchairTurningRadiusConfig,
            ),
            accessible_bathroom=_parse_config(
                accessibility_data.get("accessible_bathroom"),
                AccessibleBathroomConfig,
            ),
        ),
        environmental=RulePackEnvironmental(
            window_to_floor_area=_parse_config(
                environmental_data.get("window_to_floor_area"),
                MinimumWindowToFloorAreaConfig,
            ),
            natural_light=_parse_config(
                environmental_data.get("natural_light"),
                NaturalLightConfig,
            ),
            cross_ventilation=_parse_config(
                environmental_data.get("cross_ventilation"),
                CrossVentilationConfig,
            ),
            outdoor_connection=_parse_config(
                environmental_data.get("outdoor_connection"),
                OutdoorConnectionConfig,
            ),
            solar_orientation=_parse_config(
                environmental_data.get("solar_orientation"),
                SolarOrientationConfig,
            ),
        ),
        structural=RulePackStructural(
            max_wall_span=_parse_config(
                structural_data.get("max_wall_span"),
                MaximumWallSpanConfig,
            ),
            column_spacing=_parse_config(
                structural_data.get("column_spacing"),
                ColumnSpacingConfig,
            ),
            wall_continuity=_parse_config(
                structural_data.get("wall_continuity"),
                WallContinuityConfig,
            ),
            stair_support=_parse_config(
                structural_data.get("stair_support"),
                StairSupportConfig,
            ),
            structural_symmetry=_parse_config(
                structural_data.get("structural_symmetry"),
                StructuralSymmetryConfig,
            ),
            large_room=_parse_config(
                structural_data.get("large_room"),
                LargeUnsupportedRoomConfig,
            ),
        ),
        vastu=RulePackVastu(
            enabled=vastu_data.get("enabled", False),
            custom_params=vastu_data.get("custom_params", {}),
        ),
        scoring=ConstraintWeightProfile(
            functional_weight=scoring_data.get("functional_weight", 1.0),
            building_code_weight=scoring_data.get("building_code_weight", 1.0),
            accessibility_weight=scoring_data.get("accessibility_weight", 1.0),
            environmental_weight=scoring_data.get("environmental_weight", 1.0),
            structural_weight=scoring_data.get("structural_weight", 1.0),
            vastu_weight=scoring_data.get("vastu_weight", 1.0),
            custom_weight=scoring_data.get("custom_weight", 1.0),
        ),
    )


def _parse_config(data: dict[str, Any] | None, config_cls: type) -> Any:
    """Parse a configuration dictionary into a config dataclass.
    
    Args:
        data: Dictionary of field values, or None for defaults.
        config_cls: The dataclass type to instantiate.
        
    Returns:
        An instance of config_cls.
    """
    if data is None:
        return config_cls()
    return config_cls(**data)