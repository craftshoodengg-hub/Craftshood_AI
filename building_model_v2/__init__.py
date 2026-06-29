"""Building Model v2 — Core types and base classes.

This package provides strongly-typed, immutable data models for representing
building structures. It is designed for:

- Future BIM/IFC export
- AI reasoning and analysis
- Flutter mobile visualization
- Vastu compliance analysis

The models are organized in a hierarchy:
    Building → Floor → (Room, Wall, Door, Window, Column, Stair)

All entities inherit from BaseEntity which provides UUID identification,
timestamps, and extensible metadata.

Relationships describe how entities connect and form the building graph.

Geometry provides distance calculations, intersection predicates,
polygon utilities, transformations, and snapping.
"""

from .base import (
    BaseEntity,
    BoundingBox,
    GeometryMixin,
    Point2D,
    ValidationIssue,
    ValidationReport,
)
from .entities_building import (
    Building,
)
from .entities_column import (
    Column,
)
from .entities_floor import (
    Floor,
)
from .entities_opening import (
    Door,
    Opening,
    Window,
)
from .entities_room import (
    Room,
)
from .entities_stair import (
    Stair,
)
from .entities_wall import (
    Wall,
)
from .evaluation import (
    EvaluationPipeline,
    EvaluationPipelineConfig,
    EvaluationReport,
    EvaluationSummary,
)
from .geometry import (
    area,
    aspect_ratio,
    bounding_box,
    bounds,
    compactness,
    contains,
    crosses,
    distance,
    distance_bbox_to_point,
    distance_line_to_point,
    distance_point_to_bbox,
    distance_point_to_line,
    distance_point_to_point,
    distance_point_to_polygon,
    distance_polygon_to_point,
    intersects,
    is_clockwise,
    is_counter_clockwise,
    is_convex,
    is_rectangular,
    is_square,
    is_triangle,
    merge_vertices,
    mirror,
    offset,
    orientation,
    perimeter,
    remove_duplicate_vertices,
    rotate,
    scale,
    simplify_geometry,
    snap_line,
    snap_point,
    snap_polygon,
    touches,
    translate,
    vertex_count,
)
from .relationships import (
    Relationship,
    RelationshipType,
)
from .types import (
    ColumnType,
    DoorType,
    FloorType,
    OpeningType,
    Orientation,
    RoomType,
    StairType,
    WallType,
    WindowType,
)
from .vastu import (
    VastuDirection,
    VastuMetadata,
    VastuRule,
    VastuZone,
    VastuCell,
    VastuGrid,
    VastuAnalyzer,
    calculate_building_center,
    calculate_plot_rotation,
    calculate_room_centroid,
    calculate_room_direction,
    determine_zone,
    rotate_point,
    zone_to_vastu_zone,
)
from .ai import (
    BuildingRequirements,
    DesignRequirements,
    PlotRequirements,
    ParserResult,
    RequirementParser,
)
from .layout import (
    AdjacencyEngine,
    AdjacencyRule,
    AdjacencyRuleSet,
    RoomConnection,
    RoomGraph,
    create_default_rules,
    CirculationEngine,
    CirculationMetrics,
    CirculationPath,
    PrivacyEngine,
    PrivacyConflict,
    PrivacyMetrics,
    EgressEngine,
    EgressMetrics,
    ExitPath,
    LayoutEvaluationEngine,
    LayoutEvaluationResult,
)
from .constraints import (
    Constraint,
    ConstraintEngine,
    ConstraintIssue,
    ConstraintResult,
    ConstraintSeverity,
)
from .validation import (
    ValidationError,
    ValidationPipeline,
    ValidationPipelineConfig,
    ValidationResult,
    ValidationSeverity,
    Validator,
)
from .rules import (
    RulePack,
    RulePackAccessibility,
    RulePackBuildingCode,
    RulePackEnvironmental,
    RulePackStructural,
    RulePackVastu,
    create_residential_rule_pack,
    create_commercial_rule_pack,
    create_custom_rule_pack,
    rule_pack_from_dict,
)
from .optimization import (
    ActionRegistry,
    DesignIteration,
    ImprovementPlan,
    IterationEngine,
    IterationEngineConfig,
    IterationHistory,
    MultiObjectiveOptimizer,
    ObjectiveScore,
    OptimizationAction,
    OptimizationProfile,
    OptimizationObjective,
    OptimizationResult,
    Optimizer,
    RecommendationEngine,
    StoppingReason,
)

__all__ = [
    # Base
    "BaseEntity",
    "BoundingBox",
    "GeometryMixin",
    "Point2D",
    "ValidationIssue",
    "ValidationReport",
    # Entities
    "Building",
    "Wall",
    "Opening",
    "Door",
    "Window",
    "Room",
    "Column",
    "Stair",
    "Floor",
    # Relationships
    "Relationship",
    "RelationshipType",
    # Geometry - Distance
    "distance",
    "distance_point_to_point",
    "distance_point_to_line",
    "distance_line_to_point",
    "distance_point_to_polygon",
    "distance_polygon_to_point",
    "distance_point_to_bbox",
    "distance_bbox_to_point",
    # Geometry - Intersection
    "intersects",
    "contains",
    "touches",
    "crosses",
    # Geometry - Polygon
    "area",
    "perimeter",
    "bounding_box",
    "bounds",
    "orientation",
    "aspect_ratio",
    "compactness",
    "is_clockwise",
    "is_counter_clockwise",
    "is_convex",
    "is_rectangular",
    "is_square",
    "is_triangle",
    "vertex_count",
    # Geometry - Transform
    "translate",
    "rotate",
    "scale",
    "mirror",
    "offset",
    # Geometry - Snap
    "snap_point",
    "snap_line",
    "snap_polygon",
    "merge_vertices",
    "remove_duplicate_vertices",
    "simplify_geometry",
    # Enums
    "ColumnType",
    "DoorType",
    "FloorType",
    "OpeningType",
    "Orientation",
    "RoomType",
    "StairType",
    "WallType",
    "WindowType",
    # Validation
    "ValidationError",
    "ValidationPipeline",
    "ValidationPipelineConfig",
    "ValidationResult",
    "ValidationSeverity",
    "Validator",
    # Constraints
    "Constraint",
    "ConstraintEngine",
    "ConstraintIssue",
    "ConstraintResult",
    "ConstraintSeverity",
    # Evaluation
    "EvaluationPipeline",
    "EvaluationPipelineConfig",
    "EvaluationReport",
    "EvaluationSummary",
    # Rules
    "RulePack",
    "RulePackAccessibility",
    "RulePackBuildingCode",
    "RulePackEnvironmental",
    "RulePackStructural",
    "RulePackVastu",
    "create_residential_rule_pack",
    "create_commercial_rule_pack",
    "create_custom_rule_pack",
    "rule_pack_from_dict",
    # Optimization
    "ActionRegistry",
    "DesignIteration",
    "ImprovementPlan",
    "IterationEngine",
    "IterationEngineConfig",
    "IterationHistory",
    "MultiObjectiveOptimizer",
    "ObjectiveScore",
    "OptimizationAction",
    "OptimizationProfile",
    "OptimizationObjective",
    "OptimizationResult",
    "Optimizer",
    "RecommendationEngine",
    "StoppingReason",
    # AI
    "BuildingRequirements",
    "DesignRequirements",
    "PlotRequirements",
    "ParserResult",
    "RequirementParser",
    # Vastu
    "VastuDirection",
    "VastuMetadata",
    "VastuRule",
    "VastuZone",
    "VastuCell",
    "VastuGrid",
    "VastuAnalyzer",
    "calculate_building_center",
    "calculate_plot_rotation",
    "calculate_room_centroid",
    "calculate_room_direction",
    "determine_zone",
    "rotate_point",
    "zone_to_vastu_zone",
    # Layout
    "AdjacencyEngine",
    "AdjacencyRule",
    "AdjacencyRuleSet",
    "RoomConnection",
    "RoomGraph",
    "create_default_rules",
    "CirculationEngine",
    "CirculationMetrics",
    "CirculationPath",
    "PrivacyEngine",
    "PrivacyConflict",
    "PrivacyMetrics",
    "EgressEngine",
    "EgressMetrics",
    "ExitPath",
    "LayoutEvaluationEngine",
    "LayoutEvaluationResult",
]

__version__ = "2.0.0"
