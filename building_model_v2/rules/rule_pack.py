"""Rule Pack System for Building Model v2.

Provides configurable rule packs that define configuration values
used by validation, constraints, scoring, and evaluation.

Rule Packs contain no logic. They only provide configuration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..constraints.accessibility_constraints import (
    AccessibleBathroomConfig,
    MinimumHallwayWidthConfig as HallwayWidthConfig,
    RampSlopeConfig,
    StairHandrailConfig,
    WheelchairTurningRadiusConfig as TurningRadiusConfig,
)
from ..constraints.building_code_constraints import (
    MinimumCeilingHeightConfig as CeilingHeightConfig,
    MinimumDoorWidthConfig as DoorWidthConfig,
    MaximumTravelDistanceConfig as MaxTravelDistanceConfig,
    MinimumRoomAreaConfig as RoomAreaConfig,
    MinimumStairWidthConfig as StairWidthConfig,
    MinimumWindowAreaConfig as WindowAreaConfig,
)
from ..constraints.environmental_constraints import (
    CrossVentilationConfig,
    NaturalLightConfig,
    OutdoorConnectionConfig,
    SolarOrientationConfig,
    MinimumWindowToFloorAreaConfig as WindowToFloorAreaConfig,
)
from ..constraints.scoring import ConstraintWeightProfile
from ..constraints.structural_constraints import (
    LargeUnsupportedRoomConfig,
    WallContinuityConfig,
    ColumnSpacingConfig,
    MaximumWallSpanConfig,
    StairSupportConfig,
    StructuralSymmetryConfig,
)
from ..validation.room_validator import RoomValidationConfig
from ..validation.door_validator import DoorValidationConfig
from ..validation.wall_validator import WallValidationConfig
from ..validation.window_validator import WindowValidationConfig
from ..validation.stair_validator import StairValidationConfig


# ============================================================================
# Configuration Dataclasses for Rule Pack
# ============================================================================


@dataclass(frozen=True, slots=True)
class RulePackBuildingCode:
    """Building code configuration values.
    
    Attributes:
        room_area: Room area thresholds.
        door_width: Door width thresholds.
        window_area: Window area thresholds.
        stair_width: Stair width thresholds.
        ceiling_height: Ceiling height thresholds.
        max_travel_distance: Maximum travel distance thresholds.
    """
    
    room_area: RoomAreaConfig = field(default_factory=RoomAreaConfig)
    door_width: DoorWidthConfig = field(default_factory=DoorWidthConfig)
    window_area: WindowAreaConfig = field(default_factory=WindowAreaConfig)
    stair_width: StairWidthConfig = field(default_factory=StairWidthConfig)
    ceiling_height: CeilingHeightConfig = field(default_factory=CeilingHeightConfig)
    max_travel_distance: MaxTravelDistanceConfig = field(default_factory=MaxTravelDistanceConfig)


@dataclass(frozen=True, slots=True)
class RulePackAccessibility:
    """Accessibility configuration values.
    
    Attributes:
        hallway_width: Hallway width thresholds.
        ramp_slope: Ramp slope thresholds.
        stair_handrail: Stair handrail thresholds.
        turning_radius: Wheelchair turning radius thresholds.
        accessible_bathroom: Accessible bathroom thresholds.
    """
    
    hallway_width: HallwayWidthConfig = field(default_factory=HallwayWidthConfig)
    ramp_slope: RampSlopeConfig = field(default_factory=RampSlopeConfig)
    stair_handrail: StairHandrailConfig = field(default_factory=StairHandrailConfig)
    turning_radius: TurningRadiusConfig = field(default_factory=TurningRadiusConfig)
    accessible_bathroom: AccessibleBathroomConfig = field(default_factory=AccessibleBathroomConfig)


@dataclass(frozen=True, slots=True)
class RulePackEnvironmental:
    """Environmental configuration values.
    
    Attributes:
        window_to_floor_area: Window to floor area thresholds.
        natural_light: Natural light thresholds.
        cross_ventilation: Cross ventilation thresholds.
        outdoor_connection: Outdoor connection thresholds.
        solar_orientation: Solar orientation thresholds.
    """
    
    window_to_floor_area: WindowToFloorAreaConfig = field(default_factory=WindowToFloorAreaConfig)
    natural_light: NaturalLightConfig = field(default_factory=NaturalLightConfig)
    cross_ventilation: CrossVentilationConfig = field(default_factory=CrossVentilationConfig)
    outdoor_connection: OutdoorConnectionConfig = field(default_factory=OutdoorConnectionConfig)
    solar_orientation: SolarOrientationConfig = field(default_factory=SolarOrientationConfig)


@dataclass(frozen=True, slots=True)
class RulePackStructural:
    """Structural configuration values.
    
    Attributes:
        max_wall_span: Maximum wall span thresholds.
        column_spacing: Column spacing thresholds.
        load_bearing_continuity: Load-bearing wall continuity config.
        stair_support: Stair support config.
        structural_symmetry: Structural symmetry config.
        large_opening: Large opening config.
    """
    
    max_wall_span: MaximumWallSpanConfig = field(default_factory=MaximumWallSpanConfig)
    column_spacing: ColumnSpacingConfig = field(default_factory=ColumnSpacingConfig)
    wall_continuity: WallContinuityConfig = field(
        default_factory=WallContinuityConfig
    )
    stair_support: StairSupportConfig = field(default_factory=StairSupportConfig)
    structural_symmetry: StructuralSymmetryConfig = field(default_factory=StructuralSymmetryConfig)
    large_room: LargeUnsupportedRoomConfig = field(default_factory=LargeUnsupportedRoomConfig)


@dataclass(frozen=True, slots=True)
class RulePackVastu:
    """Vastu configuration values.
    
    Currently a placeholder for future Vastu constraint configuration.
    
    Attributes:
        enabled: Whether Vastu constraints are enabled.
        custom_params: Custom Vastu parameters.
    """
    
    enabled: bool = False
    custom_params: dict[str, Any] = field(default_factory=dict)


# ============================================================================
# RulePack Base Class
# ============================================================================


@dataclass(frozen=True, slots=True)
class RulePack:
    """Immutable rule pack that provides configuration values.
    
    Rule Packs define the configuration values used by validation,
    constraints, scoring, and evaluation. They contain no logic.
    
    Attributes:
        name: Human-readable name of the rule pack.
        description: Description of the rule pack.
        building_code: Building code configuration.
        accessibility: Accessibility configuration.
        environmental: Environmental configuration.
        structural: Structural configuration.
        vastu: Vastu configuration.
        scoring: Scoring weight profile.
    """
    
    name: str
    description: str = ""
    building_code: RulePackBuildingCode = field(default_factory=RulePackBuildingCode)
    accessibility: RulePackAccessibility = field(default_factory=RulePackAccessibility)
    environmental: RulePackEnvironmental = field(default_factory=RulePackEnvironmental)
    structural: RulePackStructural = field(default_factory=RulePackStructural)
    vastu: RulePackVastu = field(default_factory=RulePackVastu)
    scoring: ConstraintWeightProfile = field(default_factory=ConstraintWeightProfile)
    
    def to_dict(self) -> dict[str, Any]:
        """Serialize the rule pack to a dictionary.
        
        Returns:
            A dictionary representation of the rule pack.
        """
        return {
            "name": self.name,
            "description": self.description,
            "building_code": {
                "room_area": _config_to_dict(self.building_code.room_area),
                "door_width": _config_to_dict(self.building_code.door_width),
                "window_area": _config_to_dict(self.building_code.window_area),
                "stair_width": _config_to_dict(self.building_code.stair_width),
                "ceiling_height": _config_to_dict(self.building_code.ceiling_height),
                "max_travel_distance": _config_to_dict(self.building_code.max_travel_distance),
            },
            "accessibility": {
                "hallway_width": _config_to_dict(self.accessibility.hallway_width),
                "ramp_slope": _config_to_dict(self.accessibility.ramp_slope),
                "stair_handrail": _config_to_dict(self.accessibility.stair_handrail),
                "turning_radius": _config_to_dict(self.accessibility.turning_radius),
                "accessible_bathroom": _config_to_dict(self.accessibility.accessible_bathroom),
            },
            "environmental": {
                "window_to_floor_area": _config_to_dict(self.environmental.window_to_floor_area),
                "natural_light": _config_to_dict(self.environmental.natural_light),
                "cross_ventilation": _config_to_dict(self.environmental.cross_ventilation),
                "outdoor_connection": _config_to_dict(self.environmental.outdoor_connection),
                "solar_orientation": _config_to_dict(self.environmental.solar_orientation),
            },
            "structural": {
                "max_wall_span": _config_to_dict(self.structural.max_wall_span),
                "column_spacing": _config_to_dict(self.structural.column_spacing),
                "wall_continuity": _config_to_dict(self.structural.wall_continuity),
                "stair_support": _config_to_dict(self.structural.stair_support),
                "structural_symmetry": _config_to_dict(self.structural.structural_symmetry),
                "large_room": _config_to_dict(self.structural.large_room),
            },
            "vastu": {
                "enabled": self.vastu.enabled,
                "custom_params": self.vastu.custom_params,
            },
            "scoring": {
                "functional_weight": self.scoring.functional_weight,
                "building_code_weight": self.scoring.building_code_weight,
                "accessibility_weight": self.scoring.accessibility_weight,
                "environmental_weight": self.scoring.environmental_weight,
                "structural_weight": self.scoring.structural_weight,
                "vastu_weight": self.scoring.vastu_weight,
                "custom_weight": self.scoring.custom_weight,
            },
        }


def _config_to_dict(config: Any) -> dict[str, Any]:
    """Convert a frozen dataclass config to a dictionary.
    
    Args:
        config: A frozen dataclass instance.
        
    Returns:
        A dictionary of field names to values.
    """
    return {f.name: getattr(config, f.name) for f in config.__dataclass_fields__.values()}