"""Constraint Framework for Building Model v2.

Provides a foundation for architectural constraint evaluation.
This module establishes the reusable infrastructure for all future
architectural rules including building codes, Vastu, accessibility,
and structural constraints.

Modules:
    constraint_severity: Severity levels for constraint issues.
    constraint_issue: Constraint issue representation.
    constraint_result: Collection of constraint issues.
    constraint: Abstract base class for constraints.
    constraint_engine: Engine for orchestrating constraint evaluation.
    constraint_category: Categories for organizing constraints.
    functional_constraints: Design quality constraints.
"""

from .constraint import Constraint
from .constraint_category import ConstraintCategory
from .constraint_engine import ConstraintEngine
from .constraint_issue import ConstraintIssue
from .constraint_result import ConstraintResult
from .constraint_severity import ConstraintSeverity
from .building_code_constraints import (
    BuildingCodeConstraint,
    CeilingHeightConstraint,
    MaximumTravelDistanceConstraint,
    MinimumDoorWidthConstraint,
    MinimumRoomAreaConstraint,
    MinimumStairWidthConfig,
    MinimumWindowAreaConfig,
    MinimumWindowAreaConstraint,
    StairWidthConstraint,
)
from .accessibility_constraints import (
    AccessibilityConstraint,
    AccessibleBathroomConstraint,
    MinimumAccessibleDoorWidthConstraint,
    MinimumHallwayWidthConstraint,
    RampSlopeConstraint,
    StairHandrailConstraint,
    WheelchairTurningRadiusConstraint,
)
from .functional_constraints import (
    EmptyBuildingConstraint,
    EmptyFloorConstraint,
    FunctionalConstraint,
    IsolatedRoomConstraint,
    RoomWithoutDoorConstraint,
    RoomWithoutWindowConstraint,
    UnconnectedFloorConstraint,
)
from .environmental_constraints import (
    CrossVentilationConfig,
    CrossVentilationConstraint,
    EnvironmentalConstraint,
    EnvironmentalConstraintConfig,
    MinimumWindowToFloorAreaConfig,
    MinimumWindowToFloorAreaConstraint,
    NaturalLightConfig,
    NaturalLightConstraint,
    OutdoorConnectionConfig,
    OutdoorConnectionConstraint,
    SolarOrientationConfig,
    SolarOrientationConstraint,
    WestFacingHeatGainConfig,
    WestFacingHeatGainConstraint,
)
from .structural_constraints import (
    ColumnAlignmentConfig,
    ColumnAlignmentConstraint,
    ColumnSpacingConfig,
    ColumnSpacingConstraint,
    LargeUnsupportedRoomConfig,
    LargeUnsupportedRoomConstraint,
    MaximumWallSpanConfig,
    MaximumWallSpanConstraint,
    StairSupportConfig,
    StairSupportConstraint,
    StructuralConstraint,
    StructuralConstraintConfig,
    StructuralSymmetryConfig,
    StructuralSymmetryConstraint,
    WallContinuityConfig,
    WallContinuityConstraint,
)

from .vastu_constraints import (
    BrahmasthanConstraint,
    EntranceDirectionConstraint,
    KitchenPlacementConstraint,
    MasterBedroomConstraint,
    PoojaRoomConstraint,
    StaircaseConstraint,
    ToiletPlacementConstraint,
    VastuConstraint,
    VASTU_BRAHMASTHAN,
    VASTU_ENTRANCE_DIRECTION,
    VASTU_KITCHEN_PLACEMENT,
    VASTU_MASTER_BEDROOM,
    VASTU_POOJA_ROOM,
    VASTU_STAIRCASE,
    VASTU_TOILET,
)
from .scoring import (
    ConstraintScore,
    ConstraintScoreEngine,
    ConstraintWeightProfile,
)

__all__ = [
    "Constraint",
    "ConstraintCategory",
    "ConstraintEngine",
    "ConstraintIssue",
    "ConstraintResult",
    "ConstraintSeverity",
    "EmptyBuildingConstraint",
    "EmptyFloorConstraint",
    "FunctionalConstraint",
    "IsolatedRoomConstraint",
    "RoomWithoutDoorConstraint",
    "RoomWithoutWindowConstraint",
    "UnconnectedFloorConstraint",
    "BuildingCodeConstraint",
    "CeilingHeightConstraint",
    "MaximumTravelDistanceConstraint",
    "MinimumDoorWidthConstraint",
    "MinimumRoomAreaConstraint",
    "MinimumWindowAreaConstraint",
    "StairWidthConstraint",
    "AccessibilityConstraint",
    "AccessibleBathroomConstraint",
    "MinimumAccessibleDoorWidthConstraint",
    "MinimumHallwayWidthConstraint",
    "RampSlopeConstraint",
    "StairHandrailConstraint",
    "WheelchairTurningRadiusConstraint",
    "CrossVentilationConfig",
    "CrossVentilationConstraint",
    "EnvironmentalConstraint",
    "EnvironmentalConstraintConfig",
    "MinimumWindowToFloorAreaConfig",
    "MinimumWindowToFloorAreaConstraint",
    "NaturalLightConfig",
    "NaturalLightConstraint",
    "OutdoorConnectionConfig",
    "OutdoorConnectionConstraint",
    "SolarOrientationConfig",
    "SolarOrientationConstraint",
    "WestFacingHeatGainConfig",
    "WestFacingHeatGainConstraint",
    "ColumnSpacingConfig",
    "ColumnSpacingConstraint",
    "MaximumWallSpanConfig",
    "MaximumWallSpanConstraint",
    "StairSupportConfig",
    "StairSupportConstraint",
    "StructuralConstraint",
    "StructuralConstraintConfig",
    "StructuralSymmetryConfig",
    "StructuralSymmetryConstraint",
    "ConstraintScore",
    "ConstraintScoreEngine",
    "ConstraintWeightProfile",
    "BrahmasthanConstraint",
    "EntranceDirectionConstraint",
    "KitchenPlacementConstraint",
    "MasterBedroomConstraint",
    "PoojaRoomConstraint",
    "StaircaseConstraint",
    "ToiletPlacementConstraint",
    "VastuConstraint",
    "VASTU_BRAHMASTHAN",
    "VASTU_ENTRANCE_DIRECTION",
    "VASTU_KITCHEN_PLACEMENT",
    "VASTU_MASTER_BEDROOM",
    "VASTU_POOJA_ROOM",
    "VASTU_STAIRCASE",
    "VASTU_TOILET",
    "LargeUnsupportedRoomConfig",
    "LargeUnsupportedRoomConstraint",
    "MaximumWallSpanConfig",
    "MaximumWallSpanConstraint",
    "WallContinuityConfig",
    "WallContinuityConstraint",
    "ColumnAlignmentConfig",
    "ColumnAlignmentConstraint",
]
